# Catalogue des lieux fictifs de Montréal

catalogue = [
    {
        "id_lieu": "L001",
        "nom": "Musée des arts",
        "categorie": "Activité",
        "adresse": "Montréal (adresse fictive)",
        "description": "Visite d'un musée avec des œuvres artistiques.",
        "prix": 30,
        "unite_prix": "Par personne",
        "interets": ["Arts"],
        "tranche_age": "16-17 ans"
    },
    {
        "id_lieu": "L002",
        "nom": "Atelier de peinture",
        "categorie": "Activité",
        "adresse": "Montréal (adresse fictive)",
        "description": "Atelier pour découvrir et pratiquer la peinture.",
        "prix": 35,
        "unite_prix": "Par personne",
        "interets": ["Arts"],
        "tranche_age": "16-17 ans"
    },
    {
        "id_lieu": "L003",
        "nom": "Restaurant La Petite Italie",
        "categorie": "Restaurant",
        "adresse": "Montréal (adresse fictive)",
        "description": "Restaurant proposant des plats italiens.",
        "prix": 25,
        "unite_prix": "Par personne",
        "interets": ["Gastronomie", "Culture"],
        "tranche_age": "18 ans et plus"
    },
    {
        "id_lieu": "L004",
        "nom": "Restaurant Saveurs d'Asie",
        "categorie": "Restaurant",
        "adresse": "Montréal (adresse fictive)",
        "description": "Restaurant proposant des plats asiatiques.",
        "prix": 20,
        "unite_prix": "Par personne",
        "interets": ["Gastronomie"],
        "tranche_age": "16-17 ans"
    },
    {
        "id_lieu": "L005",
        "nom": "Auberge du Centre",
        "categorie": "Hébergement",
        "adresse": "Montréal (adresse fictive)",
        "description": "Hébergement simple situé au centre de Montréal.",
        "prix": 40,
        "unite_prix": "Par personne",
        "interets": ["Culture"],
        "tranche_age": "18 ans et plus"
    },
    {
        "id_lieu": "L006",
        "nom": "Hébergement Le Petit Montréal",
        "categorie": "Hébergement",
        "adresse": "Montréal (adresse fictive)",
        "description": "Hébergement confortable pour découvrir la ville.",
        "prix": 45,
        "unite_prix": "Par personne",
        "interets": ["Nature", "Culture"],
        "tranche_age": "18 ans et plus"
    }
]


def filtrer_lieux(catalogue, budget_max=None, categorie=None, interet=None, tranche_age=None):
    resultats = []

    if budget_max is not None and budget_max != "":
        try:
            budget_max = float(budget_max)
        except (ValueError, TypeError):
            raise ValueError("Le budget doit être un nombre.")

        if budget_max < 0:
            raise ValueError("Le budget ne peut pas être négatif.")

    for lieu in catalogue:
        if budget_max is not None and budget_max != "" and lieu["prix"] > budget_max:
            continue

        if categorie is not None and categorie != "" and lieu["categorie"] != categorie:
            continue

        if interet is not None and interet != "" and interet not in lieu["interets"]:
            continue

        if tranche_age is not None and tranche_age != "" and lieu["tranche_age"] != tranche_age:
            continue

        resultats.append(lieu)

    return resultats


def trouver_lieu(catalogue, id_lieu):
    for lieu in catalogue:
        if lieu["id_lieu"] == id_lieu:
            return lieu

    return None


if __name__ == "__main__":
    # T01 - Prix à la limite
    resultats_t01 = filtrer_lieux(catalogue, 30, "Activité", "Arts", "16-17 ans")
    lieu_30_trouve = False
    lieu_35_trouve = False

    for lieu in resultats_t01:
        if lieu["id_lieu"] == "L001":
            lieu_30_trouve = True
        if lieu["id_lieu"] == "L002":
            lieu_35_trouve = True

    if lieu_30_trouve and not lieu_35_trouve:
        print("T01 - Prix à la limite : Réussi")
    else:
        print("T01 - Prix à la limite : Échoué")

    # T02 - Plusieurs filtres
    resultats_t02 = filtrer_lieux(catalogue, None, "Activité", "Arts", "16-17 ans")

    if len(resultats_t02) == 2:
        print("T02 - Plusieurs filtres : Réussi")
    else:
        print("T02 - Plusieurs filtres : Échoué")

    # T03 - Aucun résultat
    nombre_lieux_avant = len(catalogue)
    resultats_t03 = filtrer_lieux(catalogue, 5, "Hébergement", "Nature", "16-17 ans")

    if len(resultats_t03) == 0 and len(catalogue) == nombre_lieux_avant:
        print("T03 - Aucun résultat : Réussi")
    else:
        print("T03 - Aucun résultat : Échoué")