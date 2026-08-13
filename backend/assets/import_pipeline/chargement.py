import json
from pathlib import Path

from ..models import Borne, Batiment
from .extraction import lire_geojson
from .transformation import transformer_borne
from .validation import valider_borne
from .transformation import transformer_batiment, transformer_borne
from .validation import valider_batiment, valider_borne

from ..models import Batiment, Borne, SegmentRue
from .transformation import transformer_batiment, transformer_borne, transformer_segment_rue
from .validation import valider_batiment, valider_borne, valider_segment_rue


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


def charger_bornes(chemin_source, chemin_rejets):
    """Charge les bornes depuis le GeoJSON source vers la base de donnees.
    Ecrit les features rejetees dans un GeoJSON separe et retourne un
    rapport resumant l'operation.
    """
    features = lire_geojson(chemin_source)

    identifiants_vus = set()
    entrees_rejetees = []
    nombre_charge = 0
    nombre_dates_entretien_manquantes = 0
    nombre_pressions_manquantes = 0

    for feature in features:
        problemes = valider_borne(feature)
        identifiant_source = feature.get("properties", {}).get("ID")

        if not problemes and identifiant_source in identifiants_vus:
            problemes = ["identifiant_source_duplique"]

        if problemes:
            entrees_rejetees.append((feature, ", ".join(problemes)))
            continue

        identifiants_vus.add(identifiant_source)

        proprietes = feature["properties"]
        if proprietes.get("DATEENTRETIEN") is None:
            nombre_dates_entretien_manquantes += 1
        if proprietes.get("PRESSIONDYNAMIQUE") is None:
            nombre_pressions_manquantes += 1

        Borne.objects.create(**transformer_borne(feature))
        nombre_charge += 1

    Path(chemin_rejets).parent.mkdir(parents=True, exist_ok=True)
    with open(chemin_rejets, "w", encoding="utf-8") as fichier:
        json.dump(construire_collection_rejets(entrees_rejetees), fichier, ensure_ascii=False, indent=2)

    return {
        "entree": len(features),
        "charge": nombre_charge,
        "rejete": len(entrees_rejetees),
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
    nombre_charge = 0
    nombre_noms_manquants = 0

    for feature in features:
        problemes = valider_batiment(feature)

        if problemes:
            entrees_rejetees.append((feature, ", ".join(problemes)))
            continue

        if not feature["properties"].get("NOM_BATIMENT"):
            nombre_noms_manquants += 1

        Batiment.objects.create(**transformer_batiment(feature))
        nombre_charge += 1

    Path(chemin_rejets).parent.mkdir(parents=True, exist_ok=True)
    with open(chemin_rejets, "w", encoding="utf-8") as fichier:
        json.dump(construire_collection_rejets(entrees_rejetees), fichier, ensure_ascii=False, indent=2)

    return {
        "entree": len(features),
        "charge": nombre_charge,
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
    nombre_charge = 0
    nombre_statuts_manquants = 0

    for feature in features:
        problemes = valider_segment_rue(feature)

        if problemes:
            entrees_rejetees.append((feature, ", ".join(problemes)))
            continue

        if not feature["properties"].get("STATUTSEGMENT"):
            nombre_statuts_manquants += 1

        SegmentRue.objects.create(**transformer_segment_rue(feature))
        nombre_charge += 1

    Path(chemin_rejets).parent.mkdir(parents=True, exist_ok=True)
    with open(chemin_rejets, "w", encoding="utf-8") as fichier:
        json.dump(construire_collection_rejets(entrees_rejetees), fichier, ensure_ascii=False, indent=2)

    return {
        "entree": len(features),
        "charge": nombre_charge,
        "rejete": len(entrees_rejetees),
        "statuts_manquants": nombre_statuts_manquants,
    }