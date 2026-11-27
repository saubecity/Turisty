import math
from datetime import date
from database.connection import get_db
from database.catalogue_repository import charger_catalogue


def catalogue_complet():
    lieux = charger_catalogue()
    with get_db() as conn:
        details = {str(row['IdAttraction']): dict(row) for row in conn.execute(
            'SELECT IdAttraction, date_debut, date_fin, MinAge, MaxAge FROM Attraction')}
    for lieu in lieux:
        row = details[lieu['id_lieu']]
        lieu.update(date_debut=row['date_debut'], date_fin=row['date_fin'],
                    age_min=row['MinAge'], age_max=row['MaxAge'])
        lieu['age_precise'] = row['MinAge'] is not None or row['MaxAge'] is not None
        lieu['demonstration'] = lieu['nom'].startswith('Démo — ')
        prix = lieu.get('prix')
        if prix is not None and (not math.isfinite(prix) or prix < 0):
            lieu['prix'] = None
        if str(lieu.get('categorie', '')).lower() in ('', 'nan'):
            lieu['categorie'] = 'Autre'
        for key in ('latitude', 'longitude'):
            value = lieu.get(key)
            if value is not None and not math.isfinite(value):
                lieu[key] = None
    return lieux


def disponible(lieu, jour):
    for field, lower in (('date_debut', True), ('date_fin', False)):
        value = lieu.get(field)
        if value:
            try:
                event_date = date.fromisoformat(value[:10])
            except (TypeError, ValueError):
                return False
            if lower and jour < event_date:
                return False
            if not lower and jour > event_date:
                return False
    return True
