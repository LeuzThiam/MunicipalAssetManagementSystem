from django.utils import timezone
from rest_framework import serializers

from .models import Inspection


class InspectionSerializer(serializers.ModelSerializer):
    inspecteur_nom = serializers.SerializerMethodField()
    borne_identifiant = serializers.CharField(source="borne.identifiant_source", read_only=True)

    class Meta:
        model = Inspection
        fields = [
            "id", "borne", "borne_identifiant", "inspecteur", "inspecteur_nom",
            "date_inspection", "etat", "pression_observee", "commentaire",
            "date_creation", "date_modification",
        ]
        read_only_fields = ["inspecteur", "date_creation", "date_modification"]

    def get_inspecteur_nom(self, objet):
        return f"{objet.inspecteur.prenom} {objet.inspecteur.nom}".strip()

    def validate_date_inspection(self, valeur):
        if valeur > timezone.localdate():
            raise serializers.ValidationError("Une inspection ne peut pas avoir une date future.")
        return valeur
