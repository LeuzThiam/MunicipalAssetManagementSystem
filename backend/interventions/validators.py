from django.utils import timezone
from rest_framework import serializers

from .models import Intervention


def valider_chronologie_intervention(statut, planifiee_le, terminee_le):
    """Vérifie la cohérence des dates avec l'état de l'intervention."""
    if statut == Intervention.Statut.TERMINEE and not terminee_le:
        raise serializers.ValidationError({
            "terminee_le": "La date de réalisation est obligatoire pour une intervention terminée."
        })

    if statut != Intervention.Statut.TERMINEE and terminee_le:
        raise serializers.ValidationError({
            "terminee_le": "La date de réalisation est réservée aux interventions terminées."
        })

    if terminee_le and terminee_le > timezone.now():
        raise serializers.ValidationError({
            "terminee_le": "La date de réalisation ne peut pas être future."
        })

    if terminee_le and planifiee_le and terminee_le < planifiee_le:
        raise serializers.ValidationError({
            "terminee_le": "La réalisation ne peut pas précéder la date planifiée."
        })
