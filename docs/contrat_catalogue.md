
# Contrat de données du catalogue

## 1. Objectif

Le catalogue fournit un format commun pour consulter et filtrer les attractions de Montréal, qu'elles proviennent des données importées dans SQLite ou des données fictives utilisées pour les tests.

## 2. Structure d'une attraction

| Champ | Type | Description |
|---|---|---|
| id_lieu | str | Identifiant unique de l'attraction |
| nom | str | Nom de l'attraction |
| categorie | str ou None | Catégorie de l'attraction |
| adresse | str ou None | Adresse de l'attraction |
| description | str ou None | Description de l'attraction |
| date_debut | str ou None | Date de début, si disponible |
| date_fin | str ou None | Date de fin, si disponible |
| prix | int, float ou None | Prix de l'attraction |
| unite_prix | str | Unité du prix |
| interets | list[str] | Intérêts associés à l'attraction |
| tranche_age | str | Tranche d'âge recommandée ou autorisée |
| latitude | float ou None | Latitude géographique |
| longitude | float ou None | Longitude géographique |

## 3. Règles de gestion

- Un prix égal à 0 représente une activité gratuite.
- Un prix égal à None représente un prix inconnu.
- Un prix inconnu ne doit jamais être converti en 0.
- Sans filtre de budget, les activités gratuites et celles dont le prix est inconnu peuvent être affichées.
- Avec un budget maximal, les activités dont le prix est inconnu sont exclues.
- Lorsque MinAge et MaxAge sont tous les deux NULL, l'activité est considérée comme accessible à tous les âges.
- Les dates, les adresses et les coordonnées peuvent être absentes.
- Les identifiants des attractions sont convertis en chaînes de caractères dans le catalogue.

## 4. Exemple d'attraction

```python
attraction = {
    "id_lieu": "123",
    "nom": "Exposition artistique",
    "categorie": "Exposition",
    "adresse": None,
    "description": "Une exposition artistique à Montréal.",
    "date_debut": None,
    "date_fin": None,
    "prix": None,
    "unite_prix": "Par personne",
    "interets": ["Culture et arts"],
    "tranche_age": "Tous les âges",
    "latitude": None,
    "longitude": None
}
```

## 5. Modules concernés

- `catalogue.py` : filtrage des attractions et recherche par identifiant.
- `database/catalogue_repository.py` : lecture des attractions depuis SQLite et adaptation des données au format du catalogue.
- `catalogue_routes.py` : consultation du catalogue à travers l'API FastAPI.
- `test_catalogue.py` : tests des filtres et de la recherche.
- `test_catalogue_repository.py` : tests de lecture et d'adaptation des données SQLite.
- `test_catalogue_routes.py` : tests des routes de consultation du catalogue.
