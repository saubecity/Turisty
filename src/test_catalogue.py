import unittest

from catalogue import catalogue, filtrer_lieux, trouver_lieu
from database.catalogue_repository import determiner_interets


class TestCatalogue(unittest.TestCase):

    def test_budget_a_la_limite(self):
        resultats = filtrer_lieux(catalogue, budget_max=30)
        ids = [lieu["id_lieu"] for lieu in resultats]

        self.assertIn("L001", ids)
        self.assertNotIn("L002", ids)

    def test_plusieurs_filtres(self):
        resultats = filtrer_lieux(
            catalogue,
            categorie="Activité",
            interet="Arts",
            tranche_age="16-17 ans"
        )

        self.assertEqual(len(resultats), 2)

    def test_aucun_resultat(self):
        resultats = filtrer_lieux(
            catalogue,
            budget_max=5,
            categorie="Hébergement",
            interet="Nature",
            tranche_age="16-17 ans"
        )

        self.assertEqual(resultats, [])

    def test_budget_negatif(self):
        with self.assertRaises(ValueError):
            filtrer_lieux(catalogue, budget_max=-1)

    def test_budget_non_numerique(self):
        with self.assertRaises(ValueError):
            filtrer_lieux(catalogue, budget_max="beaucoup")

    def test_catalogue_vide(self):
        self.assertEqual(filtrer_lieux([]), [])

    def test_prix_inconnu_sans_budget(self):
        lieux = [
            {"id_lieu": "X1", "nom": "Événement", "prix": None}
        ]

        self.assertEqual(filtrer_lieux(lieux), lieux)

    def test_prix_inconnu_avec_budget(self):
        lieux = [
            {"id_lieu": "X1", "nom": "Événement", "prix": None}
        ]

        self.assertEqual(filtrer_lieux(lieux, budget_max=20), [])

    def test_champs_facultatifs_absents(self):
        lieux = [
            {"id_lieu": "X1", "nom": "Lieu sans détails"}
        ]

        self.assertEqual(filtrer_lieux(lieux), lieux)

        self.assertEqual(
            filtrer_lieux(lieux, categorie="Activité"),
            []
        )

    def test_entrees_invalides(self):
        lieux = [
            None,
            "texte",
            {"id_lieu": "X1", "nom": "Lieu valide"}
        ]

        resultats = filtrer_lieux(lieux)

        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0]["id_lieu"], "X1")

    def test_interet_sous_forme_de_chaine(self):
        lieux = [
            {"id_lieu": "X1", "interets": "Arts"}
        ]

        self.assertEqual(
            filtrer_lieux(lieux, interet="Arts"),
            lieux
        )

    def test_trouver_lieu_existant(self):
        lieu = trouver_lieu(catalogue, "L001")

        self.assertIsNotNone(lieu)
        self.assertEqual(lieu["nom"], "Musée des arts")

    def test_trouver_lieu_inexistant(self):
        self.assertIsNone(
            trouver_lieu(catalogue, "INEXISTANT")
        )

    def test_filtrage_ne_modifie_pas_catalogue(self):
        nombre_initial = len(catalogue)

        filtrer_lieux(catalogue, budget_max=10)

        self.assertEqual(len(catalogue), nombre_initial)


    def test_tous_les_ages_compatibles_avec_une_tranche(self):
        lieux = [
            {
                "id_lieu": "X1",
                "nom": "Musée",
                "tranche_age": "Tous les âges"
            },
            {
                "id_lieu": "X2",
                "nom": "Activité réservée",
                "tranche_age": "18 ans et plus"
            }
        ]

        resultats = filtrer_lieux(
            lieux,
            tranche_age="16-17 ans"
        )

        ids = [lieu["id_lieu"] for lieu in resultats]

        self.assertIn("X1", ids)
        self.assertNotIn("X2", ids)

    
    def test_filtrer_interet_gastronomie(self):
        lieux = [
            {
                "id_lieu": "X1",
                "categorie": "Cuisine",
                "prix": 20,
                "interets": determiner_interets("Cuisine"),
                "tranche_age": "Tous les âges"
            },
            {
                "id_lieu": "X2",
                "categorie": "Exposition",
                "prix": 10,
                "interets": determiner_interets("Exposition"),
                "tranche_age": "Tous les âges"
            }
        ]

        resultats = filtrer_lieux(
            lieux,
            interet="Gastronomie"
        )

        self.assertEqual(
            [lieu["id_lieu"] for lieu in resultats],
            ["X1"]
        )

    def test_filtrer_interet_multiple(self):
        lieux = [
            {
                "id_lieu": "X1",
                "categorie": "Sport et plein air",
                "prix": 15,
                "interets": determiner_interets("Sport et plein air")
            }
        ]

        resultats_nature = filtrer_lieux(
            lieux,
            interet="Nature et plein air"
        )

        resultats_sport = filtrer_lieux(
            lieux,
            interet="Sports et loisirs"
        )

        self.assertEqual(len(resultats_nature), 1)
        self.assertEqual(len(resultats_sport), 1)

    def test_filtrer_interet_avec_budget_et_categorie(self):
        lieux = [
            {
                "id_lieu": "X1",
                "categorie": "Cuisine",
                "prix": 20,
                "interets": determiner_interets("Cuisine"),
                "tranche_age": "Tous les âges"
            },
            {
                "id_lieu": "X2",
                "categorie": "Cuisine",
                "prix": 40,
                "interets": determiner_interets("Cuisine"),
                "tranche_age": "Tous les âges"
            },
            {
                "id_lieu": "X3",
                "categorie": "Exposition",
                "prix": 15,
                "interets": determiner_interets("Exposition"),
                "tranche_age": "Tous les âges"
            }
        ]

        resultats = filtrer_lieux(
            lieux,
            budget_max=25,
            categorie="Cuisine",
            interet="Gastronomie"
        )

        self.assertEqual(
            [lieu["id_lieu"] for lieu in resultats],
            ["X1"]
        )

    def test_filtrer_interet_inexistant(self):
        lieux = [
            {
                "id_lieu": "X1",
                "categorie": "Cuisine",
                "prix": 20,
                "interets": determiner_interets("Cuisine")
            }
        ]

        resultats = filtrer_lieux(
            lieux,
            interet="Interet inexistant"
        )

        self.assertEqual(resultats, [])



if __name__ == "__main__":
    unittest.main()