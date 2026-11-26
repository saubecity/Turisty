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
    if budget_max is not None and budget_max != "":
        try:
            budget_max = float(budget_max)
        except (ValueError, TypeError):
            raise ValueError("Le budget doit être un nombre.")

        if budget_max < 0:
            raise ValueError("Le budget ne peut pas être négatif.")

    resultats = []

    for lieu in catalogue:
        if not isinstance(lieu, dict):
            continue

        if budget_max is not None and budget_max != "":
            prix = lieu.get("prix")

            if prix is None or prix == "":
                continue

            try:
                prix = float(prix)
            except (ValueError, TypeError):
                continue

            if prix < 0 or prix > budget_max:
                continue

        if categorie is not None and categorie != "":
            if lieu.get("categorie") != categorie:
                continue

        if interet is not None and interet != "":
            interets = lieu.get("interets", [])

            if isinstance(interets, str):
                interets = [interets]

            if not isinstance(interets, (list, tuple, set)):
                continue

            if interet not in interets:
                continue

        if tranche_age is not None and tranche_age != "":
            tranche_lieu = lieu.get("tranche_age")

            if tranche_lieu != "Tous les âges" and tranche_lieu != tranche_age:
                continue

        resultats.append(lieu)

    return resultats



def trouver_lieu(catalogue, id_lieu):
    if id_lieu is None or id_lieu == "":
        return None

    for lieu in catalogue:
        if isinstance(lieu, dict) and lieu.get("id_lieu") == id_lieu:
            return lieu

    return None