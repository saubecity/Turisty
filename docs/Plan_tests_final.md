# Plan de tests final — Turisty

Exécution du 2026-11-26

68 tests automatiques réussis : 38 conservés et 30 ajoutés. Les 30 tests ajoutés utilisent des bases temporaires. La commande `python tester.py --rapport` renouvelle la preuve détaillée dans `Resultats_tests.json`.

| ID | Module | Entrée / situation | Attendu | Observé | Verdict |
| --- | --- | --- | --- | --- | --- |
| F01 | Page et routes | Ouvrir /, les fichiers statiques et le schéma API | Réponses HTTP 200, routes de programmes présentes | HTTP 200 et routes vérifiées | RÉUSSI |
| F02 | Hors ligne | Lancer avec une base neuve et bloquer le réseau | Catalogue de démonstration disponible | Au moins 9 attractions accessibles | RÉUSSI |
| F03 | Compte | Créer un compte et se connecter | Mot de passe haché et cookie HttpOnly | Préfixe scrypt, mot de passe absent, HttpOnly présent | RÉUSSI |
| F04 | Courriel | Réutiliser le même courriel en majuscules | Refus et aucun doublon | HTTP 400, un seul compte | RÉUSSI |
| F05 | Connexion | Mot de passe incorrect | Connexion refusée | HTTP 401 | RÉUSSI |
| F06 | Accès | Sauvegarde sans connexion | Refus | HTTP 401 | RÉUSSI |
| F07 | Persistance | Sauvegarder un séjour de deux jours puis relire | Programme complet et deux étapes avec coûts | HTTP 201, deux étapes, coûts et personnes retrouvés | RÉUSSI |
| F08 | Propriété | Un autre compte consulte et supprime le séjour | Séjour invisible et suppression refusée | Liste vide, suppression HTTP 400 | RÉUSSI |
| F09 | Transaction | Deuxième étape avec attraction inexistante | Annulation du programme et de toutes ses étapes | Trois tables restent vides | RÉUSSI |
| F10 | Calcul | 200 $, 2 personnes, 2 jours en Gastronomie, données fictives | 56 $ de coût, 144 $ restants | Valeurs exactes vérifiées | RÉUSSI |
| F11 | Budget | Même séjour avec 1 $ | Refus de budget | HTTP 400 | RÉUSSI |
| F12 | Durée | 0 jour, 4 jours ou booléen | Validation refusée | HTTP 422 pour chaque entrée | RÉUSSI |
| F13 | Personnes | 0, -1, True ou 1,5 personne | Validation refusée | HTTP 422 pour chaque entrée | RÉUSSI |
| F14 | Date | Séjour commençant hier | Refus | HTTP 400 | RÉUSSI |
| F15 | Âge et champs facultatifs | Tous les âges avec demande 16-17, coordonnées absentes et catalogue historique | Génération sans erreur | Coordonnée None et séjour historique de deux jours | RÉUSSI |
| F16 | Données invalides | Budget NaN, infini, booléen ; entrée None et prix NaN | Refus contrôlé | ValueError attendues | RÉUSSI |
| F17 | Prix | Filtre budget zéro et attraction à prix inconnu | Gratuits seulement sous budget, prix inconnu conservé sans budget | Prix nuls filtrés et un prix inconnu dans les données de test | RÉUSSI |
| F18 | Événement passé | Rendre les activités Cuisine terminées | Exclusion du catalogue à venir et du séjour daté | Catalogue vide pour Cuisine, génération HTTP 400 | RÉUSSI |
| F19 | Participation | Créer une sortie, demander puis redemander | Première demande en attente, doublon refusé | Création et demande HTTP 201, doublon HTTP 400 | RÉUSSI |
| F20 | Décision | Décision par un autre compte, puis acceptations au-delà de la capacité | Droits et capacité respectés | Refus non-organisateur ; une acceptation ; dépassement refusé ; refus du second enregistré | RÉUSSI |
| F21 | CSRF et origine | Écriture sans jeton et requête depuis une autre origine | Requêtes refusées | HTTP 403 pour les deux situations | RÉUSSI |
| F22 | Session | Se déconnecter puis réutiliser l’ancien cookie | Session révoquée | Compte retourné nul | RÉUSSI |
| F23 | Redémarrage | Relancer le cycle de vie sur le même fichier SQLite | Séjour retrouvé avec la session valide | Séjour Persistant retrouvé | RÉUSSI |
| F24 | Réinitialisation | Effacer une base puis recommencer et initialiser | Aucune erreur sur une base absente | Schéma recréé et zéro compte | RÉUSSI |
| F25 | Cache | Simuler un téléchargement échoué | Cache reste expiré | Expiration vérifiée après ValueError | RÉUSSI |
| F26 | GeoJSON | Objet absent, features nul, liste vide ou événement sans titre | Refus sans import invalide | ValueError pour chaque cas | RÉUSSI |
| F27 | Import | Importer deux fois le même événement de prix inconnu | Un seul événement, prix inconnu et coordonnées conservées | Une ligne, prix NULL, latitude 45,5 | RÉUSSI |
| F28 | Réseau | Simuler un délai d’attente HTTP | Erreur contrôlée et catalogue accessible | Erreur renvoyée, catalogue HTTP 200 | RÉUSSI |
| F29 | Dates | Lieu gratuit disponible deux jours et lieu payant limité au premier | Affectation sur les jours compatibles | Lieu payant jour 1, gratuit jour 2 | RÉUSSI |
| F30 | Optimalité | 30 jeux aléatoires à graine fixe et comparaison exhaustive | Même minimum ou même absence de solution | Conformité vérifiée sur les 30 jeux | RÉUSSI |

## Scénarios historiques de Matheus

Les six scénarios de `python src/test_sorties.py` affichent tous un résultat conforme : demande valide, sortie complète, doublon, sortie inexistante, sortie passée et membre non identifié. Leur sortie est conservée dans `Scenarios_sorties_resultats.txt`.

## Vérification dans le navigateur

Parcours exécuté dans Chromium sur une base temporaire : catalogue → inscription → connexion → génération → sauvegarde → consultation après rechargement → création de sortie → demande depuis un second compte → acceptation → statut mis à jour. Aucun message d’erreur JavaScript détecté. Contrôle de mise en page à 1440 px et à 390 px, sans débordement horizontal de page.

## Vérification de la source externe

Une tentative réelle de téléchargement depuis Montréal a échoué dans l’environnement de préparation. Le démarrage local et les tests de panne simulée sont concluants. Le succès d’une actualisation réelle sur l’ordinateur de l’équipe reste à vérifier avec `python src/main.py --sync`.

## Bogue découvert et corrigé

Le scénario historique de budget insuffisant sélectionnait des activités gratuites et ne provoquait plus le refus attendu. F11 utilise une base temporaire avec des activités payantes. F15 couvre aussi la régression sur « Tous les âges » et les coordonnées facultatives. F29 évite qu’un choix immédiat du lieu le moins cher bloque à tort une journée suivante.
