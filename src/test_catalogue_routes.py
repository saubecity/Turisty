
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from catalogue_routes import afficher_catalogue, afficher_details_lieu


class TestCatalogueRoutes(unittest.TestCase):

    def setUp(self):
        self.lieux = [
            {
                "id_lieu": "101",
                "nom": "Musée de Montréal",
                "categorie": "Exposition",
                "description": "Une exposition artistique.",
                "prix": 15,
                "interets": ["Culture et arts"],
                "tranche_age": "Tous les âges"
            },
            {
                "id_lieu": "102",
                "nom": "Atelier de cuisine",
                "categorie": "Cuisine",
                "description": "Un atelier gastronomique.",
                "prix": 0,
                "interets": ["Gastronomie"],
                "tranche_age": "Tous les âges"
            },
            {
                "id_lieu": "103",
                "nom": "Événement spécial",
                "categorie": "Festival",
                "description": "Un événement à Montréal.",
                "prix": None,
                "interets": ["Culture et arts"],
                "tranche_age": "Tous les âges"
            }
        ]

    @patch("catalogue_routes.charger_catalogue")
    def test_afficher_catalogue(self, charger):
        charger.return_value = self.lieux

        resultat = afficher_catalogue()

        self.assertEqual(len(resultat), 3)

    @patch("catalogue_routes.charger_catalogue")
    def test_filtrer_catalogue_par_budget(self, charger):
        charger.return_value = self.lieux

        resultat = afficher_catalogue(budget_max=15)

        identifiants = [lieu["id_lieu"] for lieu in resultat]

        self.assertIn("101", identifiants)
        self.assertIn("102", identifiants)
        self.assertNotIn("103", identifiants)

    @patch("catalogue_routes.charger_catalogue")
    def test_rechercher_catalogue(self, charger):
        charger.return_value = self.lieux

        resultat = afficher_catalogue(recherche="MUSÉE")

        self.assertEqual(len(resultat), 1)
        self.assertEqual(resultat[0]["id_lieu"], "101")

    @patch("catalogue_routes.charger_catalogue")
    def test_afficher_details_existants(self, charger):
        charger.return_value = self.lieux

        resultat = afficher_details_lieu("102")

        self.assertEqual(resultat["nom"], "Atelier de cuisine")

    @patch("catalogue_routes.charger_catalogue")
    def test_attraction_introuvable(self, charger):
        charger.return_value = self.lieux

        with self.assertRaises(HTTPException) as erreur:
            afficher_details_lieu("999")

        self.assertEqual(erreur.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
