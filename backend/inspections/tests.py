from datetime import timedelta

from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Utilisateur
from assets.models import Borne
from .models import Inspection


class InspectionApiTests(APITestCase):
    def setUp(self):
        self.inspecteur = Utilisateur.objects.create_user(
            email="inspecteur@example.com",
            password="mot-de-passe-test",
            prenom="Awa",
            nom="Diop",
            role=Utilisateur.Role.INSPECTEUR,
        )
        self.borne = Borne.objects.create(
            identifiant_source="R01-061",
            municipalite="60013",
            date_mise_a_jour_source="2026-01-01",
            geometrie=Point(-73.56, 45.5, srid=4326),
        )
        self.client.force_authenticate(self.inspecteur)

    def test_inspecteur_cree_une_inspection_pour_une_borne(self):
        reponse = self.client.post(reverse("inspection-list"), {
            "borne": self.borne.pk,
            "date_inspection": timezone.localdate(),
            "etat": Inspection.Etat.BON,
            "pression_observee": 54,
            "commentaire": "Borne accessible et fonctionnelle.",
        })

        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED)
        inspection = Inspection.objects.get()
        self.assertEqual(inspection.inspecteur, self.inspecteur)
        self.assertEqual(inspection.borne, self.borne)

    def test_date_future_est_refusee(self):
        reponse = self.client.post(reverse("inspection-list"), {
            "borne": self.borne.pk,
            "date_inspection": timezone.localdate() + timedelta(days=1),
            "etat": Inspection.Etat.BON,
        })

        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date_inspection", reponse.data["erreurs"])
