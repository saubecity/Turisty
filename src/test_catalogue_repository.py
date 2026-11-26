
import unittest

from database.catalogue_repository import (
    charger_catalogue,
    determiner_interets,
)


class TestCatalogueRepository(unittest.TestCase):

    def test_charger_catalogue_retourne_une_liste(self):
        resultat = charger_catalogue()
        self.assertIsInstance(resultat, list)

    def test_attractions_ont_les_champs_attendus(self):
        resultat = charger_catalogue()

        if not resultat:
            self.skipTest("Aucune attraction disponible dans la base de données")

        champs = {
            "id_lieu",
            "nom",
            "categorie",
            "adresse",
            "latitude",
            "longitude",
            "date_debut",
            "date_fin",
            "description",
            "date_debut",
            "date_fin",
            "prix",
            "unite_prix",
            "interets",
            "tranche_age"
        }

        for lieu in resultat:
            champs_manquants = champs - lieu.keys()

            self.assertFalse(
                champs_manquants,
                f"Champs manquants : {champs_manquants}"
            )

    def test_identifiants_sont_des_chaines(self):
        resultat = charger_catalogue()

        for lieu in resultat:
            self.assertIsInstance(lieu["id_lieu"], str)

    def test_type_cuisine_correspond_a_gastronomie(self):
        self.assertEqual(
            determiner_interets("Cuisine"),
            ["Gastronomie"]
        )

    def test_type_sport_correspond_a_deux_interets(self):
        self.assertEqual(
            determiner_interets("Sport et plein air"),
            ["Nature et plein air", "Sports et loisirs"]
        )

    def test_type_inconnu_retourne_une_liste_vide(self):
        self.assertEqual(
            determiner_interets("Type inconnu"),
            []
        )

    def test_type_absent_retourne_une_liste_vide(self):
        self.assertEqual(
            determiner_interets(None),
            []
        )

    def test_interets_sont_attribues_au_catalogue(self):
        resultat = charger_catalogue()

        if not resultat:
            self.skipTest("Aucune attraction disponible dans la base de données")

        attractions_cuisine = [
            lieu for lieu in resultat
            if lieu["categorie"] == "Cuisine"
        ]

        for lieu in attractions_cuisine:
            self.assertIn("Gastronomie", lieu["interets"])


if __name__ == "__main__":
    unittest.main()
