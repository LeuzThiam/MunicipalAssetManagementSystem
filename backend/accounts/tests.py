from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Utilisateur


class AuthentificationTests(APITestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="lecteur@ville.ca", password="mot-de-passe-solide",
            prenom="Lina", nom="Roy", role=Utilisateur.Role.LECTEUR,
        )

    def test_connexion_retourne_les_jetons_et_le_profil(self):
        connexion = self.client.post(reverse("connexion"), {
            "email": self.utilisateur.email, "password": "mot-de-passe-solide",
        })
        self.assertEqual(connexion.status_code, status.HTTP_200_OK)
        self.assertIn("access", connexion.data)
        self.assertIn("refresh", connexion.data)
        profil = self.client.get(
            reverse("utilisateur-courant"),
            HTTP_AUTHORIZATION=f"Bearer {connexion.data['access']}",
        )
        self.assertEqual(profil.status_code, status.HTTP_200_OK)
        self.assertEqual(profil.data["role"], Utilisateur.Role.LECTEUR)

    def test_profil_refuse_un_utilisateur_anonyme(self):
        reponse = self.client.get(reverse("utilisateur-courant"))
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deconnexion_invalide_le_jeton_de_rafraichissement(self):
        connexion = self.client.post(reverse("connexion"), {
            "email": self.utilisateur.email, "password": "mot-de-passe-solide",
        })
        self.client.force_authenticate(self.utilisateur)
        deconnexion = self.client.post(
            reverse("deconnexion"), {"refresh": connexion.data["refresh"]},
        )
        self.assertEqual(deconnexion.status_code, status.HTTP_205_RESET_CONTENT)
        rafraichissement = self.client.post(
            reverse("connexion-rafraichir"), {"refresh": connexion.data["refresh"]},
        )
        self.assertEqual(rafraichissement.status_code, status.HTTP_401_UNAUTHORIZED)


class AdministrationUtilisateursTests(APITestCase):
    def setUp(self):
        self.admin = Utilisateur.objects.create_user(
            email="admin@ville.ca", password="mot-de-passe-solide",
            prenom="Alex", nom="Gagnon", role=Utilisateur.Role.ADMIN,
        )
        self.lecteur = Utilisateur.objects.create_user(
            email="lecteur@ville.ca", password="mot-de-passe-solide",
            prenom="Lina", nom="Roy", role=Utilisateur.Role.LECTEUR,
        )

    def test_administrateur_peut_creer_et_modifier_un_utilisateur(self):
        self.client.force_authenticate(self.admin)
        creation = self.client.post(reverse("utilisateur-list"), {
            "email": "inspecteur@ville.ca", "prenom": "Samir", "nom": "Diallo",
            "role": Utilisateur.Role.INSPECTEUR,
            "mot_de_passe": "mot-de-passe-solide",
        })
        self.assertEqual(creation.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("mot_de_passe", creation.data)
        modification = self.client.patch(
            reverse("utilisateur-detail", args=[creation.data["id"]]),
            {"role": Utilisateur.Role.GESTIONNAIRE},
        )
        self.assertEqual(modification.status_code, status.HTTP_200_OK)
        self.assertEqual(modification.data["role"], Utilisateur.Role.GESTIONNAIRE)

    def test_lecteur_ne_peut_pas_administrer_les_utilisateurs(self):
        self.client.force_authenticate(self.lecteur)
        self.assertEqual(
            self.client.get(reverse("utilisateur-list")).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_administrateur_ne_peut_pas_desactiver_son_propre_compte(self):
        self.client.force_authenticate(self.admin)
        reponse = self.client.patch(
            reverse("utilisateur-detail", args=[self.admin.id]), {"is_active": False},
        )
        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
