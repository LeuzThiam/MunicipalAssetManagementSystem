from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from .management.commands.analyser_indexation_spatiale import (
    Command,
    extraire_types_parcours,
)


class AnalyseIndexationSpatialeTests(SimpleTestCase):
    def test_extraire_types_parcours_conserve_toute_la_hierarchie(self):
        plan = {
            "Node Type": "Aggregate",
            "Plans": [
                {
                    "Node Type": "Bitmap Heap Scan",
                    "Plans": [{"Node Type": "Bitmap Index Scan"}],
                }
            ],
        }

        self.assertEqual(
            extraire_types_parcours(plan),
            ["Aggregate", "Bitmap Heap Scan", "Bitmap Index Scan"],
        )

    def test_requete_proximite_ne_provient_que_de_la_table_fournie(self):
        requete = Command._requete_proximite("assets_borne")

        self.assertIn("FROM assets_borne", requete)
        self.assertIn("ST_DWithin", requete)
        self.assertEqual(requete.count("%s"), 3)

    def test_commande_refuse_un_rayon_nul(self):
        with self.assertRaisesMessage(
            CommandError,
            "Le rayon doit etre strictement positif.",
        ):
            call_command(
                "analyser_indexation_spatiale",
                rayon=0,
                stdout=StringIO(),
            )

    def test_commande_refuse_des_coordonnees_hors_limites(self):
        with self.assertRaisesMessage(
            CommandError,
            "La latitude doit etre comprise entre -90 et 90.",
        ):
            call_command(
                "analyser_indexation_spatiale",
                latitude=91,
                stdout=StringIO(),
            )
