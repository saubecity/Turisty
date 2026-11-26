
import unittest

from database.catalogue_repository import charger_catalogue
from programme import generer_programme
from catalogue import filtrer_lieux, trouver_lieu


class TestIntegrationCatalogueProgramme(unittest.TestCase):

    def test_catalogue_reel_est_charge(self):
        catalogue = charger_catalogue()

        self.assertIsInstance(catalogue, list)  # Vérifie que le catalogue est une liste.
        self.assertTrue(len(catalogue) > 0)  # Vérifie que le catalogue contient des attractions.

    def test_programme_avec_lieux_gratuits(self):
        catalogue = charger_catalogue()

        lieux_gratuits = []

        for lieu in catalogue:
            if lieu["prix"] == 0:
                lieux_gratuits.append(lieu)

        self.assertTrue(len(lieux_gratuits) >= 2)  # Vérifie qu'il existe au moins deux lieux gratuits.

        programme = generer_programme(
            lieux_gratuits,
            budget_total=0,
            nb_personnes=2,
            duree_jours=2
        )

        self.assertEqual(len(programme["journees"]), 2)  # Vérifie que deux journées sont générées.
        self.assertEqual(programme["cout_total"], 0)  # Vérifie que le séjour est gratuit.

    def test_programme_respecte_interet(self):
        catalogue = charger_catalogue()
        interet = "Gastronomie"

        lieux_eligibles = []

        for lieu in catalogue:
            if lieu["prix"] is not None and interet in lieu["interets"]:
                lieux_eligibles.append(lieu)

        self.assertTrue(len(lieux_eligibles) >= 2)  # Vérifie qu'il existe assez de lieux pour cet intérêt.

        programme = generer_programme(
            catalogue,
            budget_total=100000,
            nb_personnes=2,
            duree_jours=2,
            interet=interet
        )

        identifiants_eligibles = []

        for lieu in lieux_eligibles:
            identifiants_eligibles.append(lieu["id_lieu"])

        for journee in programme["journees"]:
            self.assertIn(journee["id_lieu"], identifiants_eligibles)  # Vérifie que chaque lieu correspond à l'intérêt choisi.

    def test_programme_respecte_tranche_age(self):
        catalogue = charger_catalogue()

        programme = generer_programme(
            catalogue,
            budget_total=100000,
            nb_personnes=2,
            duree_jours=2,
            tranche_age="Tous les âges"
        )

        self.assertEqual(len(programme["journees"]), 2)  # Vérifie que le programme contient deux journées.

    def test_programme_respecte_budget(self):
        catalogue = charger_catalogue()
        budget = 100

        programme = generer_programme(
            catalogue,
            budget_total=budget,
            nb_personnes=2,
            duree_jours=2
        )

        self.assertTrue(programme["cout_total"] <= budget)  # Vérifie que le coût respecte le budget.
        self.assertEqual(
            programme["budget_restant"],
            budget - programme["cout_total"]
        )  # Vérifie le calcul du budget restant.

    def test_programme_refuse_budget_negatif(self):
        catalogue = charger_catalogue()

        with self.assertRaises(ValueError):  # Vérifie que la fonction génère une erreur ValueError.
            generer_programme(
                catalogue,
                budget_total=-10,
                nb_personnes=2,
                duree_jours=2
            )

    def test_programme_refuse_duree_invalide(self):
        catalogue = charger_catalogue()

        with self.assertRaises(ValueError):  # Vérifie que la fonction refuse une durée invalide.
            generer_programme(
                catalogue,
                budget_total=100,
                nb_personnes=2,
                duree_jours=4
            )

    
    def test_recherche_identifiant_reel(self):
        catalogue = charger_catalogue()

        lieu_reference = catalogue[0]

        lieu_trouve = trouver_lieu(
            catalogue,
            lieu_reference["id_lieu"]
        )

        self.assertEqual(
            lieu_trouve["id_lieu"],
            lieu_reference["id_lieu"]
        )  # Vérifie que la recherche retourne le bon identifiant.

    def test_budget_zero_exclut_prix_inconnu(self):
        catalogue = charger_catalogue()

        resultats = filtrer_lieux(
            catalogue,
            budget_max=0
        )

        for lieu in resultats:
            self.assertEqual(
                lieu["prix"],
                0
            )  # Vérifie que seuls les lieux gratuits sont conservés.

    def test_programme_n_utilise_pas_prix_inconnu(self):
        catalogue = charger_catalogue()

        programme = generer_programme(
            catalogue,
            budget_total=0,
            nb_personnes=2,
            duree_jours=2
        )

        lieux_par_id = {}

        for lieu in catalogue:
            lieux_par_id[lieu["id_lieu"]] = lieu

        for journee in programme["journees"]:
            lieu = lieux_par_id[journee["id_lieu"]]

            self.assertIsNotNone(
                lieu["prix"]
            )  # Vérifie que le prix est connu.

            self.assertEqual(
                lieu["prix"],
                0
            )  # Vérifie que le lieu est gratuit.

    def test_programme_refuse_interet_inexistant(self):
        catalogue = charger_catalogue()

        with self.assertRaises(ValueError):  # Vérifie qu'une erreur est générée si aucun lieu ne correspond.
            generer_programme(
                catalogue,
                budget_total=100000,
                nb_personnes=2,
                duree_jours=2,
                interet="Interet inexistant"
            )



if __name__ == "__main__":
    unittest.main()
