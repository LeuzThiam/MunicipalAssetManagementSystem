from django.conf import settings
from django.db import models

from assets.models import Borne


class Inspection(models.Model):
    class Etat(models.TextChoices):
        BON = "BON", "Bon état"
        A_SURVEILLER = "A_SURVEILLER", "À surveiller"
        REPARATION_REQUISE = "REPARATION_REQUISE", "Réparation requise"
        HORS_SERVICE = "HORS_SERVICE", "Hors service"

    borne = models.ForeignKey(Borne, on_delete=models.CASCADE, related_name="inspections")
    inspecteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inspections",
    )
    date_inspection = models.DateField()
    etat = models.CharField(max_length=24, choices=Etat.choices)
    pression_observee = models.PositiveIntegerField(null=True, blank=True)
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_inspection", "-date_creation"]

    def __str__(self):
        return f"Inspection {self.borne.identifiant_source} du {self.date_inspection}"
