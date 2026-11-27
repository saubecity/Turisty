# Turisty — Contributions et progression de la soumission 3

Équipe The Avengers 

## Notre point de départ

À la deuxième soumission, on avait préparé le schéma SQLite, la connexion, l’import d’événements, le catalogue, un générateur de séjour et la logique des demandes de participation. On pouvait lancer des scripts et vérifier plusieurs résultats dans le terminal. L’interface et les routes de l’application restaient à relier.


## Partie de Julián — Catalogue et découverte

Le travail reçu comprend `src/catalogue.py`, `src/database/catalogue_repository.py` et les fichiers de tests du catalogue, des coordonnées, des statistiques et de l’intégration catalogue-programme. On utilise leurs fonctions pour charger les attractions, filtrer les lieux et retrouver un identifiant.

Les compléments de cette version sont dans `src/catalogue_service.py`, les routes de catalogue de `src/main.py` et l’écran de découverte de `src/web/`. Ils ajoutent la recherche par titre, la pagination, l’affichage des fiches et des informations absentes, ainsi que les dates nécessaires au séjour. L’information d’âge non fournie reste signalée dans l’écran.

## Partie de Sara — Programme personnalisé

`src/programme.py` conserve le principe du programme d’un à trois jours et des calculs par personne. On a corrigé les validations, l’utilisation d’un lieu « Tous les âges », les coordonnées facultatives et le test de budget insuffisant. Le générateur tient maintenant compte de la date choisie et trouve une combinaison d’attractions différentes compatible avec chaque journée.

`src/database/programme_repository.py` ajoute la sauvegarde du programme et de ses étapes dans une seule transaction, puis la consultation et la suppression pour le compte concerné. Les coûts retenus et le nombre de personnes sont conservés. L’interface permet de saisir les critères, voir le programme, l’enregistrer et le retrouver après réouverture.

## Partie de Massyl — Base, import et backend


`dataset.py` conserve l’objectif de téléchargement des événements publics, avec des délais d’attente, une validation des données, une limite de taille et un cache mis à jour après réussite. Les événements payants dont le montant n’est pas connu conservent un prix inconnu. Une erreur externe laisse les données locales disponibles.

`main.py` initialise la base au démarrage, relie les routes et sert les fichiers HTML/CSS/JavaScript. Le lancement direct démarre maintenant le serveur. Neuf activités fictives clairement indiquées sont préparées pour une démonstration hors ligne. La réinitialisation volontaire gère aussi une base absente.

## Partie de Matheus  — Comptes et sorties

Les fonctions historiques de `src/sorties.py` et les six scénarios de `src/test_sorties.py` ont été conservés. La version finale les réutilise depuis `src/sorties_service.py`.

`src/comptes.py` ajoute la création de comptes, la connexion, le hachage des mots de passe, les sessions et la déconnexion. Le site permet de créer une sortie future, de demander à participer et de suivre la réponse. L’organisateur peut accepter ou refuser les demandes. Le nombre de participants acceptés est vérifié dans une transaction pour éviter un dépassement de capacité.

## Interface et tests communs

L’interface ajoutée par l'aide de l'IA se trouve dans `src/web/index.html`, `style.css` et `app.js`. Les écrans utilisent la même API : découverte, programme, séjours enregistrés, comptes et sorties. Les messages d’erreur sont affichés à l’utilisateur.

Les tests historiques sont conservés. `src/test_final.py` ajoute 30 tests portant sur le parcours API, la génération, les comptes, les droits d’accès, les transactions, les sorties et les erreurs de ressources. `tester.py` prépare les données nécessaires et exécute tous les tests automatiques. Les preuves détaillées sont dans  plan de tests final.

## Aide reçue de l’IA

 une IA générative a aidé à préparer les compléments de la dernière soumission : adaptation du générateur, routes vers L'API, interface HTML/CSS/JavaScript. 

## Limites de la version

Le programme propose une activité par jour. Il ne calcule pas les trajets, repas et hébergements. Les prix et restrictions réels doivent être vérifiés auprès des lieux. Les informations d’âge absentes restent inconnues. La carte interactive, le chat et l’administration avancée restent des pistes d’amélioration. la démonstration utilise les données locales.
