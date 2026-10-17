import logging
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from assets.import_pipeline.chargement import (
    charger_batiments,
    charger_bornes,
    charger_segments_rue,
)


logger = logging.getLogger("municipal.import")


class Command(BaseCommand):
    help = "Importe les donnees municipales (bornes, batiments, segments de rue) depuis les fichiers GeoJSON bruts."

    def handle(self, *args, **options):
        dossier_donnees = Path(settings.BASE_DIR).parent / "data"
        logger.info("Import des données municipales démarré.")

        try:
            rapport_bornes = charger_bornes(
                dossier_donnees / "raw" / "borne_incendie.geojson",
                dossier_donnees / "rejected" / "bornes_invalides.geojson",
            )
            self.afficher_rapport("Bornes", rapport_bornes)

            rapport_batiments = charger_batiments(
                dossier_donnees / "raw" / "batiments.geojson",
                dossier_donnees / "rejected" / "batiments_invalides.geojson",
            )
            self.afficher_rapport("Batiments", rapport_batiments)

            rapport_segments_rue = charger_segments_rue(
                dossier_donnees / "raw" / "segmentrue.geojson",
                dossier_donnees / "rejected" / "segments_rue_invalides.geojson",
            )
            self.afficher_rapport("Segments de rue", rapport_segments_rue)
        except Exception:
            logger.exception("Échec de l'import des données municipales.")
            raise

        logger.info("Import des données municipales terminé avec succès.")

    def afficher_rapport(self, titre, rapport):
        self.stdout.write(self.style.SUCCESS(f"Rapport d'import - {titre}"))
        for cle, valeur in rapport.items():
            self.stdout.write(f"  {cle:<20}  {valeur}")

        journaliser = logger.warning if rapport.get("rejete", 0) else logger.info
        journaliser(
            "Import %s : %s entrée(s), %s chargée(s), %s rejetée(s).",
            titre,
            rapport.get("entree", 0),
            rapport.get("charge", 0),
            rapport.get("rejete", 0),
        )
