import json
from contextlib import nullcontext
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from django.contrib.gis.geos import LineString, MultiPolygon, Point, Polygon
from django.http import QueryDict
from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from accounts.models import Utilisateur
from .import_pipeline.extraction import ErreurExtractionGeoJSON, lire_geojson
from .import_pipeline.chargement import remplacer_donnees
from .import_pipeline.validation import valider_borne, valider_segment_rue
from .models import Batiment, Borne, SegmentRue
from .views import RAYON_MAX_METRES, lire_bbox, lire_point, lire_rayon


class ValidationParametresGeospatiauxTests(SimpleTestCase):
    def test_lire_point_construit_un_point_wgs84(self):
        point = lire_point(QueryDict("lat=45.5019&lng=-73.5674"))

        self.assertEqual(point.srid, 4326)
        self.assertAlmostEqual(point.x, -73.5674)
        self.assertAlmostEqual(point.y, 45.5019)

    def test_lire_point_refuse_une_valeur_non_numerique(self):
        with self.assertRaises(ValidationError):
            lire_point(QueryDict("lat=Montreal&lng=-73.5674"))

    def test_lire_point_refuse_une_latitude_hors_limites(self):
        with self.assertRaises(ValidationError):
            lire_point(QueryDict("lat=91&lng=-73.5674"))

    def test_lire_rayon_utilise_la_valeur_par_defaut(self):
        rayon = lire_rayon(QueryDict(""), valeur_par_defaut=500)

        self.assertEqual(rayon, 500)

    def test_lire_rayon_refuse_zero_et_les_valeurs_negatives(self):
        for valeur in ("0", "-1"):
            with self.subTest(valeur=valeur), self.assertRaises(ValidationError):
                lire_rayon(QueryDict(f"rayon={valeur}"), valeur_par_defaut=500)

    def test_lire_rayon_refuse_une_recherche_trop_large(self):
        with self.assertRaises(ValidationError):
            lire_rayon(
                QueryDict(f"rayon={RAYON_MAX_METRES + 1}"),
                valeur_par_defaut=500,
            )

    def test_lire_bbox_construit_un_polygone_wgs84(self):
        zone = lire_bbox(QueryDict("bbox=-74,45,-73,46"))

        self.assertEqual(zone.srid, 4326)
        self.assertEqual(zone.extent, (-74.0, 45.0, -73.0, 46.0))

    def test_lire_bbox_exige_exactement_quatre_nombres(self):
        for valeur in ("-74,45,-73", "-74,45,-73,46,47", "a,45,-73,46"):
            with self.subTest(valeur=valeur), self.assertRaises(ValidationError):
                lire_bbox(QueryDict(f"bbox={valeur}"))

    def test_lire_bbox_refuse_des_limites_inversees(self):
        with self.assertRaises(ValidationError):
            lire_bbox(QueryDict("bbox=-73,46,-74,45"))


class ValidationImportTests(SimpleTestCase):
    def test_borne_exige_les_champs_utilises_par_la_transformation(self):
        feature = {
            "type": "Feature",
            "properties": {"ID": "B-1"},
            "geometry": {"type": "Point", "coordinates": [-73.5, 45.5]},
        }

        problemes = valider_borne(feature)

        self.assertIn("municipalite_manquante", problemes)
        self.assertIn("date_mise_a_jour_invalide", problemes)

    def test_borne_refuse_des_coordonnees_incompletes_sans_planter(self):
        feature = {
            "type": "Feature",
            "properties": {
                "ID": "B-1",
                "MUNICIPALITE": "60013",
                "MISEAJOUR": "2026-01-01",
            },
            "geometry": {"type": "Point", "coordinates": [-73.5]},
        }

        self.assertIn("coordonnees_implausibles", valider_borne(feature))

    def test_segment_refuse_une_vitesse_textuelle(self):
        feature = {
            "type": "Feature",
            "properties": {
                "ID": 1,
                "NOMGENERIQUE": "Rue Exemple",
                "TYPESEGMENTRUE": "Locale",
                "VITESSE": "rapide",
                "MISEAJOUR": "2026-01-01",
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[-73.5, 45.5], [-73.4, 45.6]],
            },
        }

        self.assertIn("vitesse_invalide", valider_segment_rue(feature))


class ExtractionGeoJSONTests(SimpleTestCase):
    def ecrire_fichier_temporaire(self, contenu):
        dossier = TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        chemin = Path(dossier.name) / "donnees.geojson"
        chemin.write_text(contenu, encoding="utf-8")
        return chemin

    def test_lire_geojson_retourne_les_features(self):
        feature = {
            "type": "Feature",
            "properties": {"ID": "B-1"},
            "geometry": {"type": "Point", "coordinates": [-73.5, 45.5]},
        }
        chemin = self.ecrire_fichier_temporaire(json.dumps({
            "type": "FeatureCollection",
            "features": [feature],
        }))

        self.assertEqual(lire_geojson(chemin), [feature])

    def test_lire_geojson_refuse_un_json_invalide(self):
        chemin = self.ecrire_fichier_temporaire("{json-invalide")

        with self.assertRaisesRegex(ErreurExtractionGeoJSON, "JSON valide"):
            lire_geojson(chemin)

    def test_lire_geojson_refuse_un_type_racine_incorrect(self):
        chemin = self.ecrire_fichier_temporaire(json.dumps({
            "type": "Feature",
            "features": [],
        }))

        with self.assertRaisesRegex(ErreurExtractionGeoJSON, "FeatureCollection"):
            lire_geojson(chemin)

    def test_lire_geojson_refuse_une_collection_vide(self):
        chemin = self.ecrire_fichier_temporaire(json.dumps({
            "type": "FeatureCollection",
            "features": [],
        }))

        with self.assertRaisesRegex(ErreurExtractionGeoJSON, "vide"):
            lire_geojson(chemin)

    def test_lire_geojson_refuse_un_fichier_absent(self):
        with self.assertRaisesRegex(ErreurExtractionGeoJSON, "introuvable"):
            lire_geojson("fichier-absent.geojson")


class VerificationChargementTests(SimpleTestCase):
    def construire_modele_simule(self, nombre_en_base):
        gestionnaire = Mock()
        gestionnaire.count.return_value = nombre_en_base
        modele = type("ActifSimule", (), {"objects": gestionnaire})
        return modele, gestionnaire

    @patch(
        "assets.import_pipeline.chargement.transaction.atomic",
        return_value=nullcontext(),
    )
    def test_remplacer_donnees_confirme_le_nombre_insere(self, atomic_simule):
        objets = [object(), object(), object()]
        modele, gestionnaire = self.construire_modele_simule(nombre_en_base=3)

        nombre_verifie = remplacer_donnees(modele, objets)

        self.assertEqual(nombre_verifie, 3)
        gestionnaire.all.return_value.delete.assert_called_once_with()
        gestionnaire.bulk_create.assert_called_once_with(objets, batch_size=1_000)

    @patch(
        "assets.import_pipeline.chargement.transaction.atomic",
        return_value=nullcontext(),
    )
    def test_remplacer_donnees_annule_si_le_nombre_est_incorrect(self, atomic_simule):
        objets = [object(), object(), object()]
        modele, _ = self.construire_modele_simule(nombre_en_base=2)

        with self.assertRaisesRegex(RuntimeError, "3 objets attendus, 2 trouves"):
            remplacer_donnees(modele, objets)


class APIgeospatialeTests(APITestCase):
    """Verifie les requetes spatiales sur une vraie base PostGIS de test."""

    @classmethod
    def setUpTestData(cls):
        cls.utilisateur = Utilisateur.objects.create_user(
            email="gestionnaire@example.com",
            password="mot-de-passe-test",
            prenom="Alice",
            nom="Gestionnaire",
            role=Utilisateur.Role.GESTIONNAIRE,
        )
        cls.borne_centre = Borne.objects.create(
            identifiant_source="BORNE-CENTRE",
            municipalite="MONTREAL",
            date_mise_a_jour_source="2026-01-01",
            geometrie=Point(-73.5674, 45.5019, srid=4326),
        )
        cls.borne_lointaine = Borne.objects.create(
            identifiant_source="BORNE-LOINTAINE",
            municipalite="MONTREAL",
            date_mise_a_jour_source="2026-01-01",
            geometrie=Point(-73.7, 45.6, srid=4326),
        )

        contour_proche = Polygon((
            (-73.5680, 45.5015),
            (-73.5670, 45.5015),
            (-73.5670, 45.5023),
            (-73.5680, 45.5023),
            (-73.5680, 45.5015),
        ), srid=4326)
        Batiment.objects.create(
            identifiant_source="BAT-PROCHE",
            nom="Caserne",
            usage="Municipal",
            adresse="1 rue Exemple",
            superficie=100,
            geometrie=MultiPolygon(contour_proche, srid=4326),
        )

        SegmentRue.objects.create(
            identifiant_source="RUE-PROCHE",
            nom="Rue Exemple",
            type_rue="Locale",
            date_mise_a_jour_source="2026-01-01",
            geometrie=LineString(
                (-73.5680, 45.5019),
                (-73.5668, 45.5019),
                srid=4326,
            ),
        )

    def setUp(self):
        self.client.force_authenticate(self.utilisateur)

    def test_carte_retourne_seulement_les_bornes_dans_la_zone(self):
        reponse = self.client.get(
            reverse("borne-carte"),
            {"bbox": "-73.58,45.49,-73.55,45.52"},
        )

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        identifiants = {
            feature["properties"]["identifiant_source"]
            for feature in reponse.data["results"]["features"]
        }
        self.assertEqual(identifiants, {"BORNE-CENTRE"})

    def test_proches_filtre_et_ordonne_les_bornes_par_distance(self):
        reponse = self.client.get(
            reverse("borne-proches"),
            {"lat": 45.5019, "lng": -73.5674, "rayon": 500},
        )

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        features = reponse.data["results"]["features"]
        self.assertEqual(len(features), 1)
        self.assertEqual(
            features[0]["properties"]["identifiant_source"],
            "BORNE-CENTRE",
        )
        self.assertAlmostEqual(
            features[0]["properties"]["distance_metres"],
            0,
            places=2,
        )

    def test_batiments_proches_retourne_le_batiment_dans_le_rayon(self):
        reponse = self.client.get(
            reverse("borne-batiments-proches", args=[self.borne_centre.pk]),
            {"rayon": 200},
        )

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        features = reponse.data["results"]["features"]
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]["properties"]["nom"], "Caserne")

    def test_rue_la_plus_proche_retourne_le_segment_attendu(self):
        reponse = self.client.get(
            reverse("borne-rue-la-plus-proche", args=[self.borne_centre.pk])
        )

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertEqual(reponse.data["rue"], "Rue Exemple")
        self.assertGreaterEqual(reponse.data["distance_metres"], 0)
