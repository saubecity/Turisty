from datetime import date, timedelta
from database.connection import get_db


DEMO_LIEUX = [
    ('Atelier de peinture', 'Art et artisanat', 15, 45.514, -73.565),
    ('Exposition au bord du fleuve', 'Exposition', 0, 45.508, -73.550),
    ('Initiation à la musique', 'Musique', 12, 45.521, -73.572),
    ('Cuisine à partager', 'Cuisine', 25, 45.519, -73.580),
    ('Saveurs de Montréal', 'Cuisine', 18, 45.525, -73.578),
    ('Balade gourmande', 'Cuisine', 10, 45.527, -73.571),
    ('Promenade nature', 'Sport et plein air', 0, 45.504, -73.590),
    ('Jardin urbain', 'Jardinage', 8, 45.533, -73.586),
    ('Rencontre littéraire', 'Club de lecture et littérature', None, 45.510, -73.567),
]


def preparer_demo():
    debut = date.today().isoformat()
    fin = (date.today() + timedelta(days=365)).isoformat()
    with get_db() as conn:
        for nom, categorie, prix, lat, lon in DEMO_LIEUX:
            nom = 'Démo — ' + nom
            if conn.execute('SELECT 1 FROM Attraction WHERE NameAttraction=? AND dataset_id IS NULL', (nom,)).fetchone():
                continue
            conn.execute('''INSERT INTO Attraction (NameAttraction,TypeAttraction,PrixAttraction,
                date_debut,date_fin,Latitude,Longitude,Description,AdresseAttraction)
                VALUES (?,?,?,?,?,?,?,?,?)''',
                (nom, categorie, prix, debut, fin, lat, lon,
                 'Activité fictive pour tester Turisty. Dates et tarifs de démonstration.',
                 'Montréal — lieu fictif'))
