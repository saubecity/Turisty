# Turisty — Rapport de progression de la soumission 2

- **Équipe** — The Avengers
- **Projet** — Turisty
- **Cours** — Langage de Script

## 1. Présentation du projet

Turisty est un projet d’application qui a pour objectif d’aider les touristes, les nouveaux arrivants et les étudiants à découvrir Montréal. L’application doit permettre de rechercher des activités, des restaurants et des hébergements selon le budget et les intérêts de l’utilisateur.

Les informations sur les lieux et les activités sont souvent réparties sur plusieurs sites. Turisty cherche à les regrouper pour faciliter l’organisation des sorties et des séjours.

## 2. Fonctionnalités prévues

- **Catalogue et filtres** — Consulter les lieux et les filtrer selon le budget, les intérêts, la catégorie et la tranche d’âge.
- **Comptes utilisateurs** — Créer un compte et se connecter à l’application.
- **Programme personnalisé** — Préparer un programme de séjour sur un à trois jours selon le budget et les préférences.
- **Sorties collectives** — Créer une sortie et envoyer une demande pour y participer.
- **Administration** — Gérer les lieux, les utilisateurs et les contenus signalés.

## 3. Organisation technique

Le prototype utilise Python pour les traitements, SQLite pour stocker les données et FastAPI comme base du serveur. Pour les prochaines étapes, le projet prévoit HTML, CSS et JavaScript pour l’interface Web ainsi que MapLibre pour la carte.

Le schéma SQLite contient notamment les tables `Compte`, `Attraction`, `program`, `Etape`, `Sortie`, `Demande` et `Message`. Un programme est lié à un compte et chacune de ses étapes est liée à une attraction.

## 4. Travail réalisé par l’équipe

- **Julián** a préparé un catalogue de six lieux fictifs à Montréal, avec des activités, des restaurants et des hébergements. Il a développé les fonctions qui filtrent les lieux selon plusieurs critères et qui permettent de retrouver un lieu par son identifiant.
- **Sara Touré** a travaillé sur la génération du programme de séjour dans `src/programme.py`. Cette partie utilise le catalogue de Julián pour proposer un séjour selon la durée, le budget, le nombre de personnes, les intérêts et la tranche d’âge. Elle calcule le coût total et le budget restant.
- **Massyl** a travaillé sur la base SQLite et sur l’import des événements publics de Montréal. Le script prépare les tables, récupère les données ouvertes et ajoute ou met à jour les événements dans la table `Attraction`. Il garde aussi la date du dernier téléchargement pour éviter de répéter l’import à chaque lancement.
- **Matheus Cavalcanti** a travaillé sur les demandes de participation aux sorties. Son code vérifie les conditions de participation et enregistre les demandes valides avec le statut « En attente » dans SQLite. Il a aussi préparé des données de démonstration et six scénarios de test.

## 5. Recherches et utilisation de l’intelligence artificielle

Comme demandé par vous monsieur, nous précisons l’aide utilisée pour introduire les fonctions Python, une notion que nous n’avions pas encore vue en classe et aussi pour l'utilisation de fastAPI. 

## 6. Tests réalisés

### Catalogue et filtres

- **T01** — Avec une limite de 30 $ par personne, le filtre inclut le lieu à exactement 30 $ et exclut celui à 35 $.
- **T02** — En combinant la catégorie, l’intérêt et la tranche d’âge, le filtre renvoie les deux activités qui correspondent aux critères.
- **T03** — Quand aucun lieu ne correspond aux critères, le filtre renvoie une liste vide.

### Génération du programme de séjour

Les valeurs des trois scénarios sont écrites à la fin de `src/programme.py`. Elles sont envoyées à la fonction quand on lance le fichier. Le script affiche les résultats dans le terminal sans demander de saisie au clavier.

- **T04 — Séjour valide.** Pour deux personnes, deux jours et un budget de 150 $, le programme propose le Musée des arts le premier jour et l’Atelier de peinture le deuxième. Le séjour coûte `(30 + 35) × 2 = 130 $`. Il reste 20 $.
- **T05 — Durée invalide.** Le test envoie volontairement une durée de quatre jours. Le message qui indique que la durée doit être de un à trois jours est le résultat attendu.
- **T06 — Budget insuffisant.** Avec les mêmes préférences que dans T04 et un budget de 100 $, le script indique qu’aucun programme ne respecte le budget.

### Demandes de participation

Les six scénarios de `src/test_sorties.py` ont réussi sur une base SQLite temporaire. Une demande valide est enregistrée avec le statut « En attente ». Les cinq autres scénarios vérifient le refus d’une demande pour une sortie complète, d’une demande en double, d’une demande pour une sortie inexistante ou passée et d’une demande sans membre identifié.

### Import des événements

L’exécution de `src/main.py` a préparé la base et synchronisé les données ouvertes. La lecture de la base fournie a confirmé la présence de 4 004 lignes dans la table `Attraction`. Ce nombre correspond à l’état de la base au moment de la vérification et peut évoluer après une nouvelle synchronisation.

Pour reproduire les tests du catalogue, du séjour et des demandes, on peut lancer ces commandes depuis la racine du dépôt.

```powershell
python -X utf8 .\src\catalogue.py
python -X utf8 .\src\programme.py
python -X utf8 .\src\test_sorties.py
```

## 7. État du prototype et difficultés d’intégration

Le lancement de `main.py` prépare la base et synchronise les événements. Le serveur FastAPI peut aussi être lancé séparément. Sa page de test `/docs` s’ouvre et affiche « No operations defined in spec! » parce qu’aucune route de Turisty n’est déclarée dans cette version. Il manque donc le point d’entrée qui permettrait au navigateur d’envoyer les critères de séjour à Python et de recevoir le résultat pour l’afficher.

La démonstration du générateur utilise les six lieux fictifs de `catalogue.py`. Les événements importés sont stockés dans SQLite et leurs champs diffèrent de ceux du catalogue fictif. Par exemple, le générateur attend une unité de prix par personne ainsi que des champs pour les intérêts et la tranche d’âge. Il faut adapter les données de la table `Attraction` à ce format et décider comment traiter les événements dont le prix est inconnu avant de les utiliser dans le calcul du séjour.

La table `Compte` existe dans SQLite. L’inscription et la connexion restent à développer. Le séjour généré s’affiche dans le terminal et sa sauvegarde dans `program` et `Etape` reste à programmer. Les demandes de participation sont enregistrées pendant les tests sur une base temporaire. Il reste à les relier à un formulaire et au compte du membre connecté.

## 8. Prochaines étapes

1. Relier un formulaire et une route FastAPI au générateur pour recevoir les critères de l’utilisateur et lui afficher un programme.
2. Adapter les données SQLite au format attendu par les filtres et vérifier le calcul avec des événements importés.
3. Ajouter l’inscription et la connexion, puis associer les séjours sauvegardés et les demandes de participation au compte du membre.
4. Tester le parcours complet depuis le navigateur, de la saisie des critères à l’affichage et à l’enregistrement du résultat.

## 9. Conclusion

Cette soumission présente un prototype qui permet de tester le filtrage du catalogue, la génération d’un séjour sur des données de démonstration, les demandes de participation dans SQLite et l’import d’événements de Montréal. Le travail restant consiste à relier ces éléments pour que l’utilisateur puisse les utiliser depuis le site.