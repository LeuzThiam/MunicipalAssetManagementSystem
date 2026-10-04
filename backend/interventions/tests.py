from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Utilisateur
from assets.models import Borne
from .models import Intervention


class InterventionApiTests(APITestCase):
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
            date_mise_a_jour_source="2026-01-01",
            geometrie=Point(-73.56, 45.5, srid=4326),
        )
        self.client.force_authenticate(self.gestionnaire)

    def test_gestionnaire_cree_une_intervention(self):
        reponse = self.client.post(reverse("intervention-list"), {
            "borne": self.borne.pk,
            "type": Intervention.Type.REPARATION,
            "priorite": Intervention.Priorite.HAUTE,
            "statut": Intervention.Statut.PLANIFIEE,
            "description": "Remplacer la vanne principale.",
            "planifiee_le": timezone.now(),
        })

        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED)
        intervention = Intervention.objects.get()
        self.assertEqual(intervention.creee_par, self.gestionnaire)
        self.assertEqual(intervention.borne, self.borne)

    def test_utilisateur_anonyme_ne_peut_pas_consulter_les_interventions(self):
        self.client.force_authenticate(user=None)

        reponse = self.client.get(reverse("intervention-list"))

        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inspecteur_ne_peut_pas_creer_une_intervention(self):
        inspecteur = Utilisateur.objects.create_user(
            email="inspecteur@example.com",
            password="mot-de-passe-test",
            prenom="Awa",
            nom="Diop",
            role=Utilisateur.Role.INSPECTEUR,
        )
        self.client.force_authenticate(inspecteur)

        reponse = self.client.post(reverse("intervention-list"), {
            "borne": self.borne.pk,
            "type": Intervention.Type.ENTRETIEN,
            "description": "Graissage préventif.",
        })

        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)

    def test_intervention_terminee_exige_une_date_de_realisation(self):
        reponse = self.client.post(reverse("intervention-list"), {
            "borne": self.borne.pk,
            "type": Intervention.Type.REPARATION,
            "statut": Intervention.Statut.TERMINEE,
            "description": "Travaux terminés.",
        })

        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("terminee_le", reponse.data["erreurs"])
