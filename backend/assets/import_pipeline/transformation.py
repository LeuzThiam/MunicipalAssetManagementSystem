from datetime import datetime
from django.contrib.gis.geos import LineString
from django.contrib.gis.geos import Point

import json

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon


def parser_date(valeur):
    """Convertit une chaine 'AAAA-MM-JJ' en objet date, ou None si absente."""
    if valeur is None:
        return None
    return datetime.strptime(valeur, "%Y-%m-%d").date()


def transformer_borne(feature):
    """Convertit une feature GeoJSON brute (deja validee) en dictionnaire
    pret a etre passe au modele Borne.
    """
    proprietes = feature["properties"]
    longitude, latitude = feature["geometry"]["coordinates"]

    return {
        "identifiant_source": proprietes["ID"],
        "municipalite": proprietes["MUNICIPALITE"],
        "date_entretien": parser_date(proprietes.get("DATEENTRETIEN")),
        "pression_dynamique": proprietes.get("PRESSIONDYNAMIQUE"),
        "date_mise_a_jour_source": parser_date(proprietes["MISEAJOUR"]),
        "geometrie": Point(longitude, latitude, srid=4326),
    }



def normaliser_geometrie_batiment(geometrie_geojson):
    """Convertit une geometrie GeoJSON (Polygon ou MultiPolygon) en MultiPolygon,
    pour que toutes les geometries de Batiment aient un type uniforme.
    """
    geometrie = GEOSGeometry(json.dumps(geometrie_geojson), srid=4326)
    if isinstance(geometrie, Polygon):
        return MultiPolygon(geometrie, srid=4326)
    return geometrie


def transformer_batiment(feature):
    """Convertit une feature GeoJSON brute (deja validee) en dictionnaire
    pret a etre passe au modele Batiment.
    """
    proprietes = feature["properties"]

    return {
        "identifiant_source": None,
        "nom": proprietes.get("NOM_BATIMENT"),
        "usage": proprietes["USAGE"],
        "adresse": proprietes["ADRESSE"],
        "superficie": proprietes["SUPERFICIE"],
        "date_creation_source": parser_date(proprietes.get("DATE_CREATION")),
        "geometrie": normaliser_geometrie_batiment(feature["geometry"]),
    }

def transformer_segment_rue(feature):
    """Convertit une feature GeoJSON brute (deja validee) en dictionnaire
    pret a etre passe au modele SegmentRue.
    """
    proprietes = feature["properties"]

    return {
        "identifiant_source": str(proprietes["ID"]),
        "nom": proprietes["NOMGENERIQUE"],
        "type_rue": proprietes["TYPESEGMENTRUE"],
        "type_camionnage": proprietes.get("TYPECAMIONNAGE"),
        "limite_vitesse": proprietes.get("VITESSE"),
        "statut": proprietes.get("STATUTSEGMENT"),
        "autobus_autorise": proprietes.get("AUTOBUS") == "Oui",
        "stationnement_hiver_interdit": proprietes.get("INTERDICTIONSTATIONNERHIVER") == "Oui",
        "date_mise_a_jour_source": parser_date(proprietes["MISEAJOUR"]),
        "geometrie": LineString(feature["geometry"]["coordinates"], srid=4326),
    }