from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Utilisateur
from assets.models import Borne
from inspections.models import Inspection
from interventions.models import Intervention


class HealthEndpointTests(APITestCase):
    def test_health_returns_ok(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "ok"})


class TableauDeBordApiTests(APITestCase):
    def setUp(self):
        self.gestionnaire = Utilisateur.objects.create_user(
            email="gestionnaire@example.com",
            password="mot-de-passe-test",
            prenom="Moussa",
            nom="Ndiaye",
            role=Utilisateur.Role.GESTIONNAIRE,
        )
        self.borne = Borne.objects.create(
            identifiant_source="R01-061",
            municipalite="60013",
            pression_dynamique=54,
            date_mise_a_jour_source="2026-01-01",
            geometrie=Point(-73.56, 45.5, srid=4326),
        )

    def test_retourne_les_indicateurs_metier(self):
        Inspection.objects.create(
            borne=self.borne,
            inspecteur=self.gestionnaire,
            date_inspection=timezone.localdate(),
            etat=Inspection.Etat.BON,
        )
        Intervention.objects.create(
            borne=self.borne,
            creee_par=self.gestionnaire,
            type=Intervention.Type.ENTRETIEN,
            description="Entretien préventif.",
        )
        self.client.force_authenticate(self.gestionnaire)

        reponse = self.client.get(reverse("tableau-de-bord"))

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertEqual(reponse.data["bornes_total"], 1)
        self.assertEqual(reponse.data["bornes_sans_entretien"], 1)
        self.assertEqual(reponse.data["pression_moyenne"], 54.0)
        self.assertEqual(reponse.data["interventions_ouvertes"], 1)
        self.assertEqual(reponse.data["inspections_ce_mois"], 1)

    def test_refuse_un_utilisateur_anonyme(self):
        reponse = self.client.get(reverse("tableau-de-bord"))

        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)
