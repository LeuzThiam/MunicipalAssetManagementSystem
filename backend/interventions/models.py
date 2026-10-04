from django.conf import settings
from django.db import models

from assets.models import Borne


class Intervention(models.Model):
    class Type(models.TextChoices):
        ENTRETIEN = "ENTRETIEN", "Entretien"
        REPARATION = "REPARATION", "Réparation"
        REMPLACEMENT = "REMPLACEMENT", "Remplacement"
        URGENCE = "URGENCE", "Urgence"

    class Priorite(models.TextChoices):
        BASSE = "BASSE", "Basse"
        NORMALE = "NORMALE", "Normale"
        HAUTE = "HAUTE", "Haute"
        URGENTE = "URGENTE", "Urgente"

    class Statut(models.TextChoices):
        OUVERTE = "OUVERTE", "Ouverte"
        PLANIFIEE = "PLANIFIEE", "Planifiée"
        EN_COURS = "EN_COURS", "En cours"
        TERMINEE = "TERMINEE", "Terminée"
        ANNULEE = "ANNULEE", "Annulée"

    borne = models.ForeignKey(Borne, on_delete=models.CASCADE, related_name="interventions")
    creee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="interventions_creees",
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    priorite = models.CharField(max_length=12, choices=Priorite.choices, default=Priorite.NORMALE)
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.OUVERTE)
    description = models.TextField()
    planifiee_le = models.DateTimeField(null=True, blank=True)
    terminee_le = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return f"Intervention {self.borne.identifiant_source} — {self.get_type_display()}"
