import json
from pathlib import Path

from django.db import transaction

from ..models import Batiment, Borne, SegmentRue
from .extraction import lire_geojson
from .transformation import transformer_batiment, transformer_borne, transformer_segment_rue
from .validation import valider_batiment, valider_borne, valider_segment_rue


TAILLE_LOT = 1_000


def construire_collection_rejets(entrees_rejetees):
    """Construit un GeoJSON valide a partir des features rejetees,
    en ajoutant le motif de rejet dans les proprietes de chaque feature.
    """
    features = []
    for feature, motif in entrees_rejetees:
        feature_annotee = dict(feature)
        feature_annotee["properties"] = {
            **feature.get("properties", {}),
            "motif_rejet": motif,
        }
        features.append(feature_annotee)
    return {"type": "FeatureCollection", "features": features}


def ecrire_rejets(chemin_rejets, entrees_rejetees):
    """Ecrit le fichier de rejets avant de modifier la base de donnees."""
    Path(chemin_rejets).parent.mkdir(parents=True, exist_ok=True)
    with open(chemin_rejets, "w", encoding="utf-8") as fichier:
        json.dump(
            construire_collection_rejets(entrees_rejetees),
            fichier,
            ensure_ascii=False,
            indent=2,
        )


def remplacer_donnees(modele, objets):
    """Remplace atomiquement le snapshot d'un type d'actif.

    Si la suppression ou l'insertion echoue, transaction.atomic annule les
    deux operations et conserve le snapshot precedent.
    """
    if not objets:
        raise RuntimeError(
            f"Remplacement refuse pour {modele.__name__}: "
            "aucun objet valide a charger."
        )

    with transaction.atomic():
        modele.objects.all().delete()
        modele.objects.bulk_create(objets, batch_size=TAILLE_LOT)

        nombre_en_base = modele.objects.count()
        nombre_attendu = len(objets)
        if nombre_en_base != nombre_attendu:
            raise RuntimeError(
                f"Verification echouee pour {modele.__name__}: "
                f"{nombre_attendu} objets attendus, {nombre_en_base} trouves."
            )

    return nombre_en_base


def charger_bornes(chemin_source, chemin_rejets):
    """Charge les bornes depuis le GeoJSON source vers la base de donnees.
    Ecrit les features rejetees dans un GeoJSON separe et retourne un
    rapport resumant l'operation.
    """
    features = lire_geojson(chemin_source)

    identifiants_vus = set()
    entrees_rejetees = []
    objets_a_charger = []
    nombre_identifiants_dupliques = 0
    nombre_dates_entretien_manquantes = 0
    nombre_pressions_manquantes = 0

    for feature in features:
        problemes = valider_borne(feature)
        identifiant_source = feature.get("properties", {}).get("ID")

        if not problemes and identifiant_source in identifiants_vus:
            problemes = ["identifiant_source_duplique"]
            nombre_identifiants_dupliques += 1

        if problemes:
            entrees_rejetees.append((feature, ", ".join(problemes)))
            continue

        try:
            objet = Borne(**transformer_borne(feature))
        except (KeyError, TypeError, ValueError) as erreur:
            entrees_rejetees.append((feature, f"transformation_invalide: {erreur}"))
            continue

        objets_a_charger.append(objet)
        identifiants_vus.add(identifiant_source)

        proprietes = feature["properties"]
        if proprietes.get("DATEENTRETIEN") is None:
            nombre_dates_entretien_manquantes += 1
        if proprietes.get("PRESSIONDYNAMIQUE") is None:
            nombre_pressions_manquantes += 1

    ecrire_rejets(chemin_rejets, entrees_rejetees)
    nombre_verifie = remplacer_donnees(Borne, objets_a_charger)

    return {
        "entree": len(features),
        "charge": len(objets_a_charger),
        "verifie_en_base": nombre_verifie,
        "rejete": len(entrees_rejetees),
        "identifiants_dupliques": nombre_identifiants_dupliques,
        "dates_entretien_manquantes": nombre_dates_entretien_manquantes,
        "pressions_manquantes": nombre_pressions_manquantes,
    }



def charger_batiments(chemin_source, chemin_rejets):
    """Charge les batiments depuis le GeoJSON source vers la base de donnees.
    Ecrit les features rejetees dans un GeoJSON separe et retourne un
    rapport resumant l'operation.
    """
    features = lire_geojson(chemin_source)

    entrees_rejetees = []
    objets_a_charger = []
    nombre_noms_manquants = 0

    for feature in features:
        problemes = valider_batiment(feature)

        if problemes:
            entrees_rejetees.append((feature, ", ".join(problemes)))
            continue

        if not feature["properties"].get("NOM_BATIMENT"):
            nombre_noms_manquants += 1

        try:
            objets_a_charger.append(Batiment(**transformer_batiment(feature)))
        except (KeyError, TypeError, ValueError) as erreur:
            entrees_rejetees.append((feature, f"transformation_invalide: {erreur}"))

    ecrire_rejets(chemin_rejets, entrees_rejetees)
    nombre_verifie = remplacer_donnees(Batiment, objets_a_charger)

    return {
        "entree": len(features),
        "charge": len(objets_a_charger),
        "verifie_en_base": nombre_verifie,
        "rejete": len(entrees_rejetees),
        "noms_manquants": nombre_noms_manquants,
    }


def charger_segments_rue(chemin_source, chemin_rejets):
    """Charge les segments de rue depuis le GeoJSON source vers la base de
    donnees. Ecrit les features rejetees dans un GeoJSON separe et retourne
    un rapport resumant l'operation.
    """
    features = lire_geojson(chemin_source)

    entrees_rejetees = []
    objets_a_charger = []
    nombre_statuts_manquants = 0

    for feature in features:
        problemes = valider_segment_rue(feature)

        if problemes:
            entrees_rejetees.append((feature, ", ".join(problemes)))
            continue

        if not feature["properties"].get("STATUTSEGMENT"):
            nombre_statuts_manquants += 1

        try:
            objets_a_charger.append(SegmentRue(**transformer_segment_rue(feature)))
        except (KeyError, TypeError, ValueError) as erreur:
            entrees_rejetees.append((feature, f"transformation_invalide: {erreur}"))

    ecrire_rejets(chemin_rejets, entrees_rejetees)
    nombre_verifie = remplacer_donnees(SegmentRue, objets_a_charger)

    return {
        "entree": len(features),
        "charge": len(objets_a_charger),
        "verifie_en_base": nombre_verifie,
        "rejete": len(entrees_rejetees),
        "statuts_manquants": nombre_statuts_manquants,
    }
