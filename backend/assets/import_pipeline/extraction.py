import json


def lire_geojson(chemin_fichier):
    """Lit un fichier GeoJSON et retourne la liste de ses features."""
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)
    return donnees.get("features", [])

