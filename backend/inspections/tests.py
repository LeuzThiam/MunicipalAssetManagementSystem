from datetime import timedelta

from django.contrib.gis.geos import Point
from django.test import SimpleTestCase
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

    def test_lecteur_ne_peut_pas_creer_une_inspection(self):
        lecteur = Utilisateur.objects.create_user(
            email="lecteur@example.com",
            password="mot-de-passe-test",
            prenom="Lina",
            nom="Roy",
            role=Utilisateur.Role.LECTEUR,
        )
        self.client.force_authenticate(lecteur)

        reponse = self.client.post(reverse("inspection-list"), {
            "borne": self.borne.pk,
            "date_inspection": timezone.localdate(),
            "etat": Inspection.Etat.BON,
        })

        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)

    def test_inspecteur_peut_modifier_sa_propre_inspection(self):
        inspection = Inspection.objects.create(
            borne=self.borne,
            inspecteur=self.inspecteur,
            date_inspection=timezone.localdate(),
            etat=Inspection.Etat.A_SURVEILLER,
        )

        reponse = self.client.patch(
            reverse("inspection-detail", args=[inspection.pk]),
            {"commentaire": "Contrôle complémentaire à prévoir."},
        )

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        inspection.refresh_from_db()
        self.assertEqual(inspection.commentaire, "Contrôle complémentaire à prévoir.")

    def test_inspecteur_ne_peut_pas_modifier_inspection_autrui(self):
        autre_inspecteur = Utilisateur.objects.create_user(
            email="autre.inspecteur@example.com",
            password="mot-de-passe-test",
            prenom="Noah",
            nom="Martin",
            role=Utilisateur.Role.INSPECTEUR,
        )
        inspection = Inspection.objects.create(
            borne=self.borne,
            inspecteur=autre_inspecteur,
            date_inspection=timezone.localdate(),
            etat=Inspection.Etat.BON,
        )

        reponse = self.client.patch(
            reverse("inspection-detail", args=[inspection.pk]),
            {"commentaire": "Modification non autorisée."},
        )

        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrateur_peut_modifier_inspection_autrui(self):
        administrateur = Utilisateur.objects.create_user(
            email="admin@example.com",
            password="mot-de-passe-test",
            prenom="Alex",
            nom="Gagnon",
            role=Utilisateur.Role.ADMIN,
        )
        inspection = Inspection.objects.create(
            borne=self.borne,
            inspecteur=self.inspecteur,
            date_inspection=timezone.localdate(),
            etat=Inspection.Etat.BON,
        )
        self.client.force_authenticate(administrateur)

        reponse = self.client.patch(
            reverse("inspection-detail", args=[inspection.pk]),
            {"etat": Inspection.Etat.REPARATION_REQUISE},
        )

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        inspection.refresh_from_db()
        self.assertEqual(inspection.etat, Inspection.Etat.REPARATION_REQUISE)


class InspectionModeleTests(SimpleTestCase):
    def test_representation_decrit_la_borne_et_la_date(self):
        inspecteur = Utilisateur(
            email="inspecteur@example.com",
            prenom="Awa",
            nom="Diop",
        )
        borne = Borne(identifiant_source="R01-061")
        inspection = Inspection(
            borne=borne,
            inspecteur=inspecteur,
            date_inspection=timezone.localdate(),
            etat=Inspection.Etat.BON,
        )

        self.assertEqual(
            str(inspection),
            f"Inspection R01-061 du {timezone.localdate()}",
        )
