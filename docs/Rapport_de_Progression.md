# Turisty — Rapport de Progression

**Équipe :** The Avengers  
**Projet :** Turisty  
**Cours :** Langage de Script

## 1. Présentation du Projet

Turisty est un projet d’application qui a pour objectif d’aider les touristes, les nouveaux arrivants et les étudiants à découvrir Montréal. L’application permet de rechercher des activités, des restaurants et des hébergements selon le budget et les intérêts de l’utilisateur.

Le projet répond à un problème simple : les informations sur les lieux et les activités sont souvent réparties sur plusieurs sites. Turisty cherche à regrouper ces informations dans une seule application et à faciliter l’organisation des sorties et des séjours.

## 2. Fonctionnalités du Projet

Le projet comprend plusieurs fonctionnalités principales :

- **1. Catalogue et filtres :** Consulter les lieux et rechercher selon le budget, les intérêts, la catégorie et la tranche d’âge.
- **2. Comptes utilisateurs :** Créer un compte et se connecter à l’application.
- **3. Programme personnalisé :** Préparer un programme de un à trois jours selon le budget et les préférences.
- **4. Sorties collectives :** Créer une sortie et envoyer une demande pour participer.
- **5. Administration :** Gérer les lieux, les utilisateurs et les contenus signalés.

Ces fonctionnalités ont été organisées selon leur priorité dans le cahier des charges.

## 3. Organisation technique

Le projet utilise principalement les technologies suivantes :

- **Python :** Pour le développement du serveur et les traitements.
- **SQLite :** Pour la gestion des données.
- **HTML, CSS et JavaScript :** Pour l’interface Web.
- **MapLibre :** Pour l’affichage de la carte.

Une structure de base de données a également été préparée. Elle contient notamment les tables Compte, Attraction, Program, Étape, Sortie, Demande et Message. Ces tables permettent d'organiser les informations des utilisateurs, des lieux, des programmes et des sorties.

## 4. Travail réalisé par l’équipe

Plusieurs éléments du projet ont déjà été préparés.

La structure de la base de données a été définie avec les principales tables et leurs relations. Le fonctionnement des demandes de participation aux sorties a également été décrit et des cas de test ont été présentés.

De mon côté (Julián), je travaille sur le catalogue et les filtres. J’ai préparé un catalogue de six lieux fictifs à Montréal, comprenant des activités, des restaurants et des hébergements. J’ai également développé les fonctions permettant de filtrer les lieux selon plusieurs critères et de rechercher un lieu avec son identifiant.
(Sara ...)
(Massyl ...)
(Matheus ...)

## 5. Tests

Des cas de test ont été documentés pour vérifier le fonctionnement de certaines parties du projet.

Pour les demandes de participation aux sorties, trois situations sont présentées :

- Une demande normale lorsque des places sont disponibles.
- Une demande lorsque la sortie est complète.
- Une demande concernant une sortie inexistante.

Les résultats indiqués dans la documentation sont conformes aux résultats attendus.

Pour le catalogue, trois tests sont prévus :

- **T01 :** vérifier le filtre de prix avec une limite de 30 $ par personne.
- **T02 :** combiner plusieurs filtres, comme la catégorie, l’intérêt et la tranche d’âge.
- **T03 :** vérifier le comportement lorsqu’aucun lieu ne correspond aux critères.

Ces tests permettent de vérifier les principales fonctions de recherche et de filtrage.

## 6. Difficultés et solutions

Le projet demande de coordonner plusieurs fonctionnalités qui utilisent les mêmes informations, notamment les lieux, les utilisateurs et les sorties.

Il est donc important de conserver une structure de données cohérente entre les différentes parties du programme. La définition des tables et des champs permet de mieux organiser le travail et de faciliter la communication entre les membres de l’équipe.

## 7. Prochaines étapes

Les prochaines étapes consistent à poursuivre le développement des fonctionnalités, à intégrer les différentes parties du projet et à vérifier leur fonctionnement ensemble.

Il faudra également réaliser davantage de tests, corriger les erreurs éventuelles et vérifier que les fonctionnalités correspondent aux besoins définis dans le cahier des charges.

## 8. Conclusion

Le projet Turisty possède maintenant une structure générale, des fonctionnalités définies et plusieurs éléments techniques préparés. Le travail réalisé constitue une base pour poursuivre le développement de l’application.

La prochaine étape importante sera de réunir les différentes parties du projet afin d’obtenir un prototype fonctionnel et cohérent.