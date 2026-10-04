import math
from datetime import datetime


def valeur_numerique(valeur):
    """Indique si une valeur est un nombre fini, sans accepter les booleens."""
    return (
        not isinstance(valeur, bool)
        and isinstance(valeur, (int, float))
        and math.isfinite(valeur)
    )


def valider_structure_feature(feature):
    """Valide la structure GeoJSON minimale d'une feature.
    Retourne la liste des problemes trouves (vide si tout est correct).
    """
    problemes = []

    if feature.get("type") != "Feature":
        problemes.append("type_feature_invalide")

    proprietes = feature.get("properties")
    if not isinstance(proprietes, dict) or not proprietes:
        problemes.append("proprietes_manquantes")

    geometrie = feature.get("geometry")
    if not geometrie:
        problemes.append("geometrie_manquante")
    elif not geometrie.get("coordinates"):
        problemes.append("coordonnees_manquantes")

    return problemes


def coordonnees_plausibles(coordonnees):
    """Verifie que des coordonnees sont dans les bornes valides d'un point GPS."""
    if not isinstance(coordonnees, (list, tuple)) or len(coordonnees) < 2:
        return False

    longitude, latitude = coordonnees[0], coordonnees[1]
    return (
        valeur_numerique(longitude)
        and valeur_numerique(latitude)
        and -180 <= longitude <= 180
        and -90 <= latitude <= 90
    )


def date_valide(valeur):
    """Verifie qu'une chaine represente bien une date au format AAAA-MM-JJ."""
    try:
        datetime.strptime(valeur, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def valider_borne(feature):
    """Valide les regles metier propres aux bornes d'incendie.
    Retourne la liste des problemes trouves (vide si tout est correct).
    """
    problemes = valider_structure_feature(feature)
    proprietes = feature.get("properties") or {}

    if not proprietes.get("ID"):
        problemes.append("identifiant_source_manquant")
    if not proprietes.get("MUNICIPALITE"):
        problemes.append("municipalite_manquante")

    date_mise_a_jour = proprietes.get("MISEAJOUR")
    if not date_valide(date_mise_a_jour):
        problemes.append("date_mise_a_jour_invalide")

    pression = proprietes.get("PRESSIONDYNAMIQUE")
    if pression is not None:
        if not valeur_numerique(pression):
            problemes.append("pression_invalide")
        elif pression < 0:
            problemes.append("pression_negative")

    date_entretien = proprietes.get("DATEENTRETIEN")
    if date_entretien is not None and not date_valide(date_entretien):
        problemes.append("date_entretien_invalide")

    geometrie = feature.get("geometry")
    if geometrie and geometrie.get("type") != "Point":
        problemes.append("type_geometrie_invalide")
    elif geometrie and not coordonnees_plausibles(geometrie["coordinates"]):
        problemes.append("coordonnees_implausibles")

    return problemes


def valider_batiment(feature):
    """Valide les regles metier propres aux batiments.
    Retourne la liste des problemes trouves (vide si tout est correct).
    """
    problemes = valider_structure_feature(feature)
    proprietes = feature.get("properties") or {}

    superficie = proprietes.get("SUPERFICIE")
    if superficie is None or not valeur_numerique(superficie):
        problemes.append("superficie_invalide")
    elif superficie < 0:
        problemes.append("superficie_negative")

    if not proprietes.get("USAGE"):
        problemes.append("usage_manquant")

    if not proprietes.get("ADRESSE"):
        problemes.append("adresse_manquante")

    date_creation = proprietes.get("DATE_CREATION")
    if date_creation is not None and not date_valide(date_creation):
        problemes.append("date_creation_invalide")

    geometrie = feature.get("geometry")
    if geometrie and geometrie.get("type") not in ("Polygon", "MultiPolygon"):
        problemes.append("type_geometrie_invalide")

    return problemes


def valider_segment_rue(feature):
    """Valide les regles metier propres aux segments de rue.
    Retourne la liste des problemes trouves (vide si tout est correct).
    """
    problemes = valider_structure_feature(feature)
    proprietes = feature.get("properties") or {}

    if not proprietes.get("ID"):
        problemes.append("identifiant_source_manquant")

    if not proprietes.get("TYPESEGMENTRUE"):
        problemes.append("type_rue_manquant")
    if not proprietes.get("NOMGENERIQUE"):
        problemes.append("nom_manquant")
    if not date_valide(proprietes.get("MISEAJOUR")):
        problemes.append("date_mise_a_jour_invalide")

    vitesse = proprietes.get("VITESSE")
    if vitesse is not None:
        if not valeur_numerique(vitesse):
            problemes.append("vitesse_invalide")
        elif not 0 < vitesse <= 130:
            problemes.append("vitesse_implausible")

    geometrie = feature.get("geometry")
    if geometrie and geometrie.get("type") != "LineString":
        problemes.append("type_geometrie_invalide")

    return problemes
