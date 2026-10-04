from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Batiment, Borne, SegmentRue


class BorneSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Borne
        geo_field = "geometrie"
        fields = "__all__"


class BorneAvecDistanceSerializer(GeoFeatureModelSerializer):
    distance_metres = serializers.SerializerMethodField()

    class Meta:
        model = Borne
        geo_field = "geometrie"
        fields = [
            "id", "identifiant_source", "municipalite", "date_entretien",
            "pression_dynamique", "date_mise_a_jour_source",
            "date_creation", "date_modification", "distance_metres",
        ]

    def get_distance_metres(self, objet):
        return objet.distance.m if hasattr(objet, "distance") else None


class BatimentSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Batiment
        geo_field = "geometrie"
        fields = "__all__"


class BatimentAvecDistanceSerializer(GeoFeatureModelSerializer):
    distance_metres = serializers.SerializerMethodField()

    class Meta:
        model = Batiment
        geo_field = "geometrie"
        fields = [
            "id", "identifiant_source", "nom", "usage", "adresse", "superficie",
            "date_creation_source", "date_creation", "date_modification", "distance_metres",
        ]

    def get_distance_metres(self, objet):
        return objet.distance.m if hasattr(objet, "distance") else None


class SegmentRueSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = SegmentRue
        geo_field = "geometrie"
        fields = "__all__"