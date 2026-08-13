from django.contrib.gis.db import models as gis_models
from django.db import models


class Borne(models.Model):
    # Identifiant interne = id (auto). identifiant_source = identifiant fourni
    # par la municipalite — non unique en amont, la source contient des doublons.
    identifiant_source = models.CharField(max_length=50, db_index=True)
    municipalite = models.CharField(max_length=20)
    date_entretien = models.DateField(null=True, blank=True)
    pression_dynamique = models.PositiveIntegerField(null=True, blank=True)
    date_mise_a_jour_source = models.DateField()
    geometrie = gis_models.PointField(srid=4326)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Borne {self.identifiant_source}"


class Batiment(models.Model):
    # Pas d'identifiant dans les donnees brutes de batiments -> nullable.
    identifiant_source = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    nom = models.CharField(max_length=255, null=True, blank=True)
    usage = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    superficie = models.FloatField()
    date_creation_source = models.DateField(null=True, blank=True)
    # MultiPolygon meme si la source est surtout du Polygon simple ->
    # normalisation a faire au moment de l'import .
    geometrie = gis_models.MultiPolygonField(srid=4326)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom or self.adresse


class SegmentRue(models.Model):
    identifiant_source = models.CharField(max_length=50, db_index=True)
    nom = models.CharField(max_length=255)
    type_rue = models.CharField(max_length=100)
    type_camionnage = models.CharField(max_length=100, null=True, blank=True)
    limite_vitesse = models.PositiveIntegerField(null=True, blank=True)
    statut = models.CharField(max_length=50, null=True, blank=True)
    autobus_autorise = models.BooleanField(default=False)
    stationnement_hiver_interdit = models.BooleanField(default=False)
    date_mise_a_jour_source = models.DateField()
    geometrie = gis_models.LineStringField(srid=4326)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom