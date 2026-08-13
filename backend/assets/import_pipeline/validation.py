from datetime import datetime


def valider_structure_feature(feature):
    """Valide la structure GeoJSON minimale d'une feature.
    Retourne la liste des problemes trouves (vide si tout est correct).
    """
    problemes = []

    if feature.get("type") != "Feature":
        problemes.append("type_feature_invalide")

    if not feature.get("properties"):
        problemes.append("proprietes_manquantes")

    geometrie = feature.get("geometry")
    if not geometrie:
        problemes.append("geometrie_manquante")
    elif not geometrie.get("coordinates"):
        problemes.append("coordonnees_manquantes")

    return problemes


def coordonnees_plausibles(coordonnees):
    """Verifie que des coordonnees sont dans les bornes valides d'un point GPS."""
    longitude, latitude = coordonnees[0], coordonnees[1]
    return -180 <= longitude <= 180 and -90 <= latitude <= 90


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
    proprietes = feature.get("properties", {})

    if not proprietes.get("ID"):
        problemes.append("identifiant_source_manquant")

    pression = proprietes.get("PRESSIONDYNAMIQUE")
    if pression is not None and pression < 0:
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
    proprietes = feature.get("properties", {})

    superficie = proprietes.get("SUPERFICIE")
    if superficie is not None and superficie < 0:
        problemes.append("superficie_negative")

    if not proprietes.get("USAGE"):
        problemes.append("usage_manquant")

    if not proprietes.get("ADRESSE"):
        problemes.append("adresse_manquante")

    geometrie = feature.get("geometry")
    if geometrie and geometrie.get("type") not in ("Polygon", "MultiPolygon"):
        problemes.append("type_geometrie_invalide")

    return problemes


def valider_segment_rue(feature):
    """Valide les regles metier propres aux segments de rue.
    Retourne la liste des problemes trouves (vide si tout est correct).
    """
    problemes = valider_structure_feature(feature)
    proprietes = feature.get("properties", {})

    if not proprietes.get("ID"):
        problemes.append("identifiant_source_manquant")

    if not proprietes.get("TYPESEGMENTRUE"):
        problemes.append("type_rue_manquant")

    vitesse = proprietes.get("VITESSE")
    if vitesse is not None and not (0 < vitesse <= 130):
        problemes.append("vitesse_implausible")

    geometrie = feature.get("geometry")
    if geometrie and geometrie.get("type") != "LineString":
        problemes.append("type_geometrie_invalide")

    return problemes