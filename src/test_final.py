import itertools
import math
import os
from pathlib import Path
import random
import sqlite3
import tempfile
import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

import requests
from fastapi.testclient import TestClient
from main import app
from programme import generer_programme
from catalogue import catalogue
from database import connection, database, dataset
from database.programme_repository import sauvegarder_programme


class TestApplicationFinale(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.environ = patch.dict(os.environ, {'TURISTY_DB': str(Path(self.temp.name) / 'test.sqlite3')})
        self.environ.start()
        self.client = TestClient(app)
        self.client.__enter__()
        self.criteres = {'budget_total': 200, 'nb_personnes': 2, 'duree_jours': 2,
                         'date_debut': date.today().isoformat(), 'interet': 'Gastronomie'}

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.environ.stop()
        self.temp.cleanup()

    def connecter(self, courriel='sara@example.test'):
        infos = {'courriel': courriel, 'mot_de_passe': 'MotDePasse-test-2026'}
        reponse = self.client.post('/api/comptes', json={**infos, 'nom': 'Membre test'})
        self.assertEqual(reponse.status_code, 201)
        reponse = self.client.post('/api/connexion', json=infos)
        self.assertEqual(reponse.status_code, 200)
        self.client.headers['X-CSRF-Token'] = reponse.json()['Csrf']
        return reponse.json()['IdCompte']

    def test_F01_page_et_routes(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertIn('/api/programmes', self.client.get('/openapi.json').json()['paths'])
        self.assertEqual(self.client.get('/static/app.js').status_code, 200)

    def test_F02_demarrage_hors_ligne(self):
        with patch('requests.get', side_effect=requests.ConnectionError('hors ligne')):
            resultat = self.client.get('/api/catalogue').json()
        self.assertGreaterEqual(resultat['total'], 9)

    def test_F03_inscription_hachage(self):
        self.connecter()
        with connection.get_db() as conn:
            valeur = conn.execute('SELECT MotdePasse FROM Compte').fetchone()[0]
        self.assertTrue(valeur.startswith('scrypt$'))
        self.assertNotIn('MotDePasse', valeur)
        self.assertIn('HttpOnly', self.client.post(
            '/api/connexion', json={'courriel': 'sara@example.test', 'mot_de_passe': 'MotDePasse-test-2026'}).headers['set-cookie'])

    def test_F04_doublon_courriel(self):
        self.connecter()
        resultat = self.client.post('/api/comptes', json={'nom': 'Autre membre', 'courriel': 'SARA@example.test', 'mot_de_passe': 'Autre-mot-de-passe'})
        self.assertEqual(resultat.status_code, 400)
        with connection.get_db() as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM Compte').fetchone()[0], 1)

    def test_F05_mauvais_mot_de_passe(self):
        self.connecter()
        self.assertEqual(self.client.post('/api/connexion', json={'courriel': 'sara@example.test', 'mot_de_passe': 'incorrect'}).status_code, 401)

    def test_F06_visiteur_sauvegarde_refusee(self):
        self.assertEqual(self.client.post('/api/programmes', json={**self.criteres, 'nom': 'Voyage'}).status_code, 401)

    def test_F07_sauvegarde_et_relecture(self):
        self.connecter()
        reponse = self.client.post('/api/programmes', json={**self.criteres, 'nom': 'Week-end'})
        self.assertEqual(reponse.status_code, 201)
        resultat = self.client.get('/api/programmes').json()
        self.assertEqual(len(resultat), 1)
        self.assertEqual(len(resultat[0]['journees']), 2)
        self.assertEqual(resultat[0]['NbPersonnes'], 2)
        self.assertEqual(sum(j['cout'] for j in resultat[0]['journees']), resultat[0]['CoutTotal'])
        with connection.get_db() as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM EtapeDetails').fetchone()[0], 2)

    def test_F08_programmes_prives(self):
        self.connecter()
        saved = self.client.post('/api/programmes', json={**self.criteres, 'nom': 'Privé'}).json()
        self.connecter('autre@example.test')
        self.assertEqual(self.client.get('/api/programmes').json(), [])
        self.assertEqual(self.client.delete('/api/programmes/' + str(saved['id_programme'])).status_code, 400)

    def test_F09_annulation_transaction(self):
        id_compte = self.connecter()
        programme = self.client.post('/api/programmes/generer', json=self.criteres).json()
        programme['journees'][-1]['id_lieu'] = '9999999'
        with self.assertRaises(sqlite3.IntegrityError):
            sauvegarder_programme(id_compte, 'Échec', programme)
        with connection.get_db() as conn:
            for table in ('program', 'Etape', 'EtapeDetails'):
                self.assertEqual(conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0], 0)

    def test_F10_generation_valide(self):
        resultat = self.client.post('/api/programmes/generer', json=self.criteres)
        self.assertEqual(resultat.status_code, 200)
        self.assertEqual(resultat.json()['cout_total'], 56)
        self.assertEqual(resultat.json()['budget_restant'], 144)

    def test_F11_budget_insuffisant(self):
        self.assertEqual(self.client.post('/api/programmes/generer', json={**self.criteres, 'budget_total': 1}).status_code, 400)

    def test_F12_duree_invalide(self):
        for duree in (0, 4, True):
            self.assertEqual(self.client.post('/api/programmes/generer', json={**self.criteres, 'duree_jours': duree}).status_code, 422)

    def test_F13_personnes_invalides(self):
        for nombre in (0, -1, True, 1.5):
            self.assertEqual(self.client.post('/api/programmes/generer', json={**self.criteres, 'nb_personnes': nombre}).status_code, 422)

    def test_F14_date_passee(self):
        hier = (date.today() - timedelta(days=1)).isoformat()
        self.assertEqual(self.client.post('/api/programmes/generer', json={**self.criteres, 'date_debut': hier}).status_code, 400)

    def test_F15_age_et_coordonnees_facultatives(self):
        lieux = [{'id_lieu': '1', 'nom': 'Démo', 'prix': 0, 'tranche_age': 'Tous les âges'}]
        programme = generer_programme(lieux, 0, 1, 1, tranche_age='16-17 ans')
        self.assertIsNone(programme['journees'][0]['latitude'])
        self.assertEqual(len(generer_programme(catalogue, 150, 2, 2)['journees']), 2)

    def test_F16_valeurs_non_finies(self):
        for valeur in (math.nan, math.inf, True):
            with self.assertRaises(ValueError):
                generer_programme([], valeur, 1, 1)
        with self.assertRaises(ValueError):
            generer_programme([None, {'prix': math.nan}], 10, 1, 1)

    def test_F17_prix_inconnu_exclu(self):
        resultat = self.client.get('/api/catalogue?budget_max=0').json()
        self.assertTrue(all(lieu['prix'] == 0 for lieu in resultat['items']))
        inconnu = [lieu for lieu in self.client.get('/api/catalogue').json()['items'] if lieu['prix'] is None]
        self.assertEqual(len(inconnu), 1)

    def test_F18_evenement_passe_exclu(self):
        with connection.get_db() as conn:
            conn.execute("UPDATE Attraction SET date_fin='2000-01-01' WHERE TypeAttraction='Cuisine'")
        self.assertEqual(self.client.post('/api/programmes/generer', json=self.criteres).status_code, 400)
        self.assertEqual(self.client.get('/api/catalogue?categorie=Cuisine').json()['total'], 0)

    def test_F19_creation_sortie_et_demande(self):
        self.connecter()
        lieu = self.client.get('/api/catalogue').json()['items'][0]['id_lieu']
        moment = (datetime.now() + timedelta(days=1)).isoformat(timespec='minutes')
        sortie = self.client.post('/api/sorties', json={'id_attraction': int(lieu), 'date_heure': moment, 'places': 1})
        self.assertEqual(sortie.status_code, 201)
        self.id_sortie = sortie.json()['id_sortie']
        self.connecter('participant@example.test')
        self.assertEqual(self.client.post(f'/api/sorties/{self.id_sortie}/demandes').status_code, 201)
        self.assertEqual(self.client.post(f'/api/sorties/{self.id_sortie}/demandes').status_code, 400)

    def test_F20_organisateur_decision_capacite(self):
        organisateur = self.connecter()
        lieu = int(self.client.get('/api/catalogue').json()['items'][0]['id_lieu'])
        moment = (datetime.now() + timedelta(days=1)).isoformat(timespec='minutes')
        sortie = self.client.post('/api/sorties', json={'id_attraction': lieu, 'date_heure': moment, 'places': 1}).json()['id_sortie']
        premier = self.connecter('premier@example.test')
        self.client.post(f'/api/sorties/{sortie}/demandes')
        second = self.connecter('second@example.test')
        self.client.post(f'/api/sorties/{sortie}/demandes')
        url = f'/api/sorties/{sortie}/demandes/{premier}'
        self.assertEqual(self.client.patch(url, json={'statut': 'Acceptée'}).status_code, 400)
        reponse = self.client.post('/api/connexion', json={'courriel': 'sara@example.test', 'mot_de_passe': 'MotDePasse-test-2026'})
        self.client.headers['X-CSRF-Token'] = reponse.json()['Csrf']
        self.assertEqual(self.client.patch(url, json={'statut': 'Acceptée'}).status_code, 200)
        self.assertEqual(self.client.patch(f'/api/sorties/{sortie}/demandes/{second}', json={'statut': 'Acceptée'}).status_code, 400)
        self.assertEqual(self.client.patch(f'/api/sorties/{sortie}/demandes/{second}', json={'statut': 'Refusée'}).status_code, 200)

    def test_F21_protection_csrf(self):
        self.connecter()
        del self.client.headers['X-CSRF-Token']
        self.assertEqual(self.client.post('/api/programmes', json={**self.criteres, 'nom': 'X'}).status_code, 403)
        self.assertEqual(self.client.post('/api/connexion', headers={'Origin': 'https://autre.test'}, json={'courriel': 'x', 'mot_de_passe': 'x'}).status_code, 403)

    def test_F22_deconnexion(self):
        self.connecter()
        cookie = self.client.cookies.get('turisty_session')
        self.assertEqual(self.client.post('/api/deconnexion').status_code, 200)
        self.client.cookies.set('turisty_session', cookie)
        self.assertIsNone(self.client.get('/api/moi').json()['compte'])

    def test_F23_persistance_apres_redemarrage(self):
        self.connecter()
        self.client.post('/api/programmes', json={**self.criteres, 'nom': 'Persistant'})
        with TestClient(app) as autre:
            autre.cookies.set('turisty_session', self.client.cookies.get('turisty_session'))
            self.assertEqual(autre.get('/api/programmes').json()[0]['Nomprogram'], 'Persistant')

    def test_F24_reset_dossier_absent(self):
        database.remove()
        database.remove()
        connection.init_schema()
        with connection.get_db() as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM Compte').fetchone()[0], 0)

    def test_F25_cache_echec(self):
        item = dataset.DatasetMetadata(lambda *args: None, 'test', 'https://example.test/')
        with patch.object(item, 'get_resource', side_effect=ValueError('échec')):
            with self.assertRaises(ValueError):
                item.update()
        self.assertTrue(item.cache_expired)

    def test_F26_geojson_invalide(self):
        for valeur in ({}, {'features': None}, {'features': []}, {'features': [{'properties': {}}]}):
            with self.assertRaises(ValueError):
                dataset.general_sync_handler(valeur, 'test')

    def test_F27_import_prix_inconnu(self):
        payload = {'features': [{'properties': {'titre': 'Import test', 'date_debut': '2026-12-01',
            'date_fin': '2026-12-02', 'cout': None}, 'geometry': {'type': 'Point', 'coordinates': [-73.5, 45.5]}}]}
        dataset.general_sync_handler(payload, 'test')
        dataset.general_sync_handler(payload, 'test')
        with connection.get_db() as conn:
            row = conn.execute("SELECT COUNT(*),PrixAttraction,Latitude FROM Attraction WHERE NameAttraction='Import test'").fetchone()
            self.assertEqual(row[0], 1)
            self.assertIsNone(row[1])
            self.assertEqual(row[2], 45.5)

    def test_F28_erreur_reseau_controlee(self):
        with patch('requests.get', side_effect=requests.Timeout('test')):
            erreurs = dataset.sync()
        self.assertTrue(erreurs)
        self.assertEqual(self.client.get('/api/catalogue').status_code, 200)

    def test_F29_dates_affectation_non_gloutonne(self):
        demain = (date.today() + timedelta(days=1)).isoformat()
        lieux = [dict(id_lieu='1', nom='Libre', prix=0),
                 dict(id_lieu='2', nom='Aujourd’hui seulement', prix=5, date_fin=date.today().isoformat())]
        programme = generer_programme(lieux, 10, 1, 2, date_debut=date.today())
        self.assertEqual([j['id_lieu'] for j in programme['journees']], ['2', '1'])
        self.assertEqual(programme['journees'][1]['date'], demain)

    def test_F30_optimum_compare_exhaustif(self):
        rng = random.Random(42)
        today = date.today()
        for _ in range(30):
            lieux = []
            for i in range(6):
                start = rng.randrange(3)
                end = rng.randrange(start, 3)
                lieux.append(dict(id_lieu=str(i), nom=str(i), prix=rng.randrange(20),
                    date_debut=(today + timedelta(days=start)).isoformat(),
                    date_fin=(today + timedelta(days=end)).isoformat()))
            possibles = []
            for selection in itertools.permutations(lieux, 3):
                if all(l['date_debut'] <= (today + timedelta(days=i)).isoformat() <= l['date_fin'] for i,l in enumerate(selection)):
                    possibles.append(sum(l['prix'] for l in selection))
            if possibles:
                self.assertEqual(generer_programme(lieux, 1000, 1, 3, date_debut=today)['cout_total'], min(possibles))
            else:
                with self.assertRaises(ValueError):
                    generer_programme(lieux, 1000, 1, 3, date_debut=today)


if __name__ == '__main__':
    unittest.main()
