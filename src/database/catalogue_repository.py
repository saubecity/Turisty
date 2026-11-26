from database.connection import get_db


CORRESPONDANCES_INTERETS = {
    "Art de la parole": ["Culture et arts"],
    "Art et artisanat": ["Culture et arts"],
    "Bien-être": ["Sports et loisirs"],
    "Cinéma": ["Culture et arts", "Festivals et événements"],
    "Cirque": ["Culture et arts", "Famille et activités pour enfants"],
    "Club de lecture et littérature": ["Culture et arts"],
    "Cuisine": ["Gastronomie"],
    "Danse": ["Culture et arts", "Festivals et événements"],
    "Exposition": ["Culture et arts"],
    "Fête et marché": ["Festivals et événements"],
    "Heure du conte": ["Culture et arts", "Famille et activités pour enfants"],
    "Humour": ["Culture et arts", "Festivals et événements"],
    "Jardinage": ["Nature et plein air"],
    "Jeux": ["Sports et loisirs", "Famille et activités pour enfants"],
    "Initiation à la musique": ["Culture et arts", "Festivals et événements"],
    "Langues": ["Culture et arts"],
    "Musique": ["Culture et arts", "Festivals et événements"],
    "Société et histoire": ["Histoire et patrimoine"],
    "Sport et plein air": ["Nature et plein air", "Sports et loisirs"],
    "Théâtre": ["Culture et arts", "Festivals et événements"]
}


def determiner_interets(type_attraction):
    if not isinstance(type_attraction, str):
        return []

    return CORRESPONDANCES_INTERETS.get(type_attraction, []).copy()


def convertir_tranche_age(min_age, max_age):
    if min_age is None and max_age is None:
        return "Tous les âges"

    if min_age is None:
        return f"Jusqu'à {max_age} ans"

    if max_age is None:
        return f"{min_age} ans et plus"

    return f"{min_age}-{max_age} ans"


def charger_catalogue():
    with get_db() as conn:
        cur = conn.execute("""
            SELECT
                IdAttraction,
                NameAttraction,
                TypeAttraction,
                AdresseAttraction,
                Description,
                date_debut,
                date_fin,
                PrixAttraction,
                MinAge,
                MaxAge,
                Latitude,
                Longitude
            FROM Attraction
            WHERE status = 'active'
            ORDER BY NameAttraction
        """)

        lignes = cur.fetchall()

    catalogue = []

    for row in lignes:
        catalogue.append({
            "id_lieu": str(row["IdAttraction"]),
            "nom": row["NameAttraction"],
            "categorie": row["TypeAttraction"],
            "adresse": row["AdresseAttraction"],
            "description": row["Description"],
            "date_debut": row["date_debut"],
            "date_fin": row["date_fin"],
            "prix": row["PrixAttraction"],
            "unite_prix": "Par personne",
            "interets": determiner_interets(row["TypeAttraction"]),
            "tranche_age": convertir_tranche_age(
                row["MinAge"],
                row["MaxAge"]
            ),
            "latitude": row["Latitude"],
            "longitude": row["Longitude"]
        })

    return catalogue