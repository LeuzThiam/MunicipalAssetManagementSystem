from rest_framework import serializers

from .models import Intervention


class InterventionSerializer(serializers.ModelSerializer):
    createur_nom = serializers.SerializerMethodField()
    borne_identifiant = serializers.CharField(source="borne.identifiant_source", read_only=True)

    class Meta:
        model = Intervention
        fields = [
            "id", "borne", "borne_identifiant", "creee_par", "createur_nom",
            "type", "priorite", "statut", "description", "planifiee_le",
            "terminee_le", "date_creation", "date_modification",
        ]
        read_only_fields = ["creee_par", "date_creation", "date_modification"]

    def get_createur_nom(self, objet):
        return f"{objet.creee_par.prenom} {objet.creee_par.nom}".strip()

    def validate(self, donnees):
        statut = donnees.get("statut", getattr(self.instance, "statut", None))
        terminee_le = donnees.get("terminee_le", getattr(self.instance, "terminee_le", None))
        if statut == Intervention.Statut.TERMINEE and not terminee_le:
            raise serializers.ValidationError({
                "terminee_le": "La date de réalisation est obligatoire pour une intervention terminée."
            })
        return donnees
