from dataclasses import dataclass

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


@dataclass(frozen=True)
class Mesure:
    temps_ms: float
    lignes: int
    parcours: str


TABLES_SPATIALES = {
    "Bornes": "assets_borne",
    "Batiments": "assets_batiment",
    "Segments de rue": "assets_segmentrue",
}


def extraire_types_parcours(plan):
    """Retourne les opérations du plan dans leur ordre d'exécution."""
    types = [plan["Node Type"]]
    for enfant in plan.get("Plans", []):
        types.extend(extraire_types_parcours(enfant))
    return types


def mesurer_requete(curseur, requete, parametres, parcours_sequentiel=False):
    with transaction.atomic():
        if parcours_sequentiel:
            # SET LOCAL limite la désactivation des index à cette seule mesure.
            # La configuration de PostgreSQL reste donc intacte après la commande.
            curseur.execute("SET LOCAL enable_indexscan = off")
            curseur.execute("SET LOCAL enable_bitmapscan = off")

        curseur.execute(
            f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {requete}",
            parametres,
        )
        resultat = curseur.fetchone()[0]

    rapport = resultat[0] if isinstance(resultat, list) else resultat
    plan = rapport["Plan"]
    return Mesure(
        temps_ms=rapport["Execution Time"],
        lignes=plan["Actual Rows"],
        parcours=" -> ".join(extraire_types_parcours(plan)),
    )


class Command(BaseCommand):
    help = (
        "Verifie les index GiST des geometries et compare EXPLAIN ANALYZE "
        "avec un parcours sequentiel force."
    )

    def add_arguments(self, parser):
        parser.add_argument("--latitude", type=float, default=45.75)
        parser.add_argument("--longitude", type=float, default=-73.46)
        parser.add_argument("--rayon", type=float, default=1000.0)

    def handle(self, *args, **options):
        latitude = options["latitude"]
        longitude = options["longitude"]
        rayon = options["rayon"]
        if not -90 <= latitude <= 90:
            raise CommandError("La latitude doit etre comprise entre -90 et 90.")
        if not -180 <= longitude <= 180:
            raise CommandError("La longitude doit etre comprise entre -180 et 180.")
        if rayon <= 0:
            raise CommandError("Le rayon doit etre strictement positif.")

        with connection.cursor() as curseur:
            index_par_table = self._lire_index_gist(curseur)
            manquants = [
                table for table in TABLES_SPATIALES.values() if table not in index_par_table
            ]
            if manquants:
                raise CommandError(
                    "Index GiST manquant sur geometrie : " + ", ".join(manquants)
                )

            self.stdout.write(self.style.SUCCESS("Index GiST verifies"))
            for libelle, table in TABLES_SPATIALES.items():
                self.stdout.write(f"  {libelle:<18} {index_par_table[table]}")

            self.stdout.write(
                f"\nEXPLAIN ANALYZE autour de ({latitude}, {longitude}), rayon {rayon:g} m"
            )
            for libelle, table in TABLES_SPATIALES.items():
                requete = self._requete_proximite(table)
                parametres = [longitude, latitude, rayon]
                sans_index = mesurer_requete(
                    curseur,
                    requete,
                    parametres,
                    parcours_sequentiel=True,
                )
                avec_index = mesurer_requete(curseur, requete, parametres)
                gain = (
                    sans_index.temps_ms / avec_index.temps_ms
                    if avec_index.temps_ms
                    else float("inf")
                )

                self.stdout.write(f"\n{libelle} ({avec_index.lignes} resultat(s))")
                self.stdout.write(
                    f"  Sans index : {sans_index.temps_ms:.3f} ms | {sans_index.parcours}"
                )
                self.stdout.write(
                    f"  Avec index : {avec_index.temps_ms:.3f} ms | {avec_index.parcours}"
                )
                self.stdout.write(f"  Facteur    : x{gain:.2f}")

    @staticmethod
    def _lire_index_gist(curseur):
        """Récupère uniquement les index GiST appliqués à la géométrie."""
        curseur.execute(
            """
            SELECT tablename, indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND tablename = ANY(%s)
              AND indexdef ILIKE '%% USING gist (geometrie%%'
            ORDER BY tablename
            """,
            [list(TABLES_SPATIALES.values())],
        )
        return dict(curseur.fetchall())

    @staticmethod
    def _requete_proximite(table):
        # Le nom de table vient de notre constante, et non d'une saisie utilisateur.
        return f"""
            SELECT id
            FROM {table}
            WHERE ST_DWithin(
                geometrie,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
            )
        """
