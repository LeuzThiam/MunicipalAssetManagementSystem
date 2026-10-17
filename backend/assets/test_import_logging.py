from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase


RAPPORT_SANS_REJET = {
    "entree": 10,
    "charge": 10,
    "verifie_en_base": 10,
    "rejete": 0,
}


class JournalisationImportTests(SimpleTestCase):
    @patch(
        "assets.management.commands.importer_donnees.charger_segments_rue",
        return_value=RAPPORT_SANS_REJET,
    )
    @patch(
        "assets.management.commands.importer_donnees.charger_batiments",
        return_value={**RAPPORT_SANS_REJET, "rejete": 2, "charge": 8},
    )
    @patch(
        "assets.management.commands.importer_donnees.charger_bornes",
        return_value=RAPPORT_SANS_REJET,
    )
    def test_commande_journalise_debut_rapports_et_fin(
        self,
        charger_bornes_simule,
        charger_batiments_simule,
        charger_segments_simule,
    ):
        with self.assertLogs("municipal.import", level="INFO") as journaux:
            call_command("importer_donnees", stdout=StringIO())

        texte = "\n".join(journaux.output)
        self.assertIn("Import des données municipales démarré", texte)
        self.assertIn("WARNING:municipal.import:Import Batiments", texte)
        self.assertIn("Import des données municipales terminé avec succès", texte)

    @patch(
        "assets.management.commands.importer_donnees.charger_bornes",
        side_effect=RuntimeError("source indisponible"),
    )
    def test_commande_journalise_une_erreur_et_la_propage(self, charger_simule):
        with self.assertLogs("municipal.import", level="ERROR") as journaux:
            with self.assertRaisesRegex(RuntimeError, "source indisponible"):
                call_command("importer_donnees", stdout=StringIO())

        self.assertIn("Échec de l'import", journaux.output[0])
