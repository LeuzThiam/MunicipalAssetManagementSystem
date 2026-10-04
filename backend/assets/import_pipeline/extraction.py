import json


class ErreurExtractionGeoJSON(ValueError):
    """Signale qu'un fichier ne respecte pas la structure GeoJSON attendue."""


def lire_geojson(chemin_fichier):
    """Lit et valide la structure racine d'une FeatureCollection GeoJSON."""
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as fichier:
            donnees = json.load(fichier)
    except FileNotFoundError as erreur:
        raise ErreurExtractionGeoJSON(
            f"Fichier GeoJSON introuvable : {chemin_fichier}"
        ) from erreur
    except json.JSONDecodeError as erreur:
        raise ErreurExtractionGeoJSON(
            f"Le fichier n'est pas un JSON valide : {chemin_fichier}"
        ) from erreur

    if not isinstance(donnees, dict):
        raise ErreurExtractionGeoJSON("La racine GeoJSON doit etre un objet.")

    if donnees.get("type") != "FeatureCollection":
        raise ErreurExtractionGeoJSON(
            "Le GeoJSON doit etre une FeatureCollection."
        )

    features = donnees.get("features")
    if not isinstance(features, list):
        raise ErreurExtractionGeoJSON(
            "La propriete 'features' doit etre une liste."
        )

    if not features:
        raise ErreurExtractionGeoJSON(
            "La FeatureCollection est vide; l'import est annule par securite."
        )

    return features

