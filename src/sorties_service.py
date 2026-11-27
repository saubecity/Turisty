from datetime import datetime
from database.connection import get_db
from catalogue_service import disponible
from sorties import demander_participation, enregistrer_demande


def lister_sorties(id_compte=None):
    with get_db() as conn:
        rows = conn.execute('''SELECT s.*, a.NameAttraction, c.NomCompte,
            (SELECT COUNT(*) FROM Demande d WHERE d.IdSortie=s.IdSortie AND StatutDemande='Acceptée') AS occupes,
            (SELECT StatutDemande FROM Demande d WHERE d.IdSortie=s.IdSortie AND d.IdCompte=?) AS ma_demande
            FROM Sortie s JOIN Attraction a ON a.IdAttraction=s.IdAttraction
            JOIN Compte c ON c.IdCompte=s.IdCompte
            WHERE s.DateHeureSortie > ? ORDER BY s.DateHeureSortie''',
            (id_compte, datetime.now().isoformat(timespec='minutes'))).fetchall()
        return [dict(row) for row in rows]


def creer_sortie(id_compte, id_attraction, date_heure, places):
    try:
        moment = datetime.fromisoformat(date_heure)
    except ValueError as erreur:
        raise ValueError('La date de sortie est invalide.') from erreur
    if moment.tzinfo or moment <= datetime.now():
        raise ValueError('Choisissez une date et une heure locales futures.')
    if type(places) is not int or not 1 <= places <= 100:
        raise ValueError('Le nombre de places doit être compris entre 1 et 100.')
    with get_db() as conn:
        attraction = conn.execute("SELECT * FROM Attraction WHERE IdAttraction=? AND status='active'",
                                  (id_attraction,)).fetchone()
        if not attraction:
            raise ValueError('Attraction introuvable.')
        if not disponible(dict(attraction), moment.date()):
            raise ValueError('Cette attraction est indisponible à la date choisie.')
        return conn.execute('''INSERT INTO Sortie (IdCompte,IdAttraction,DateHeureSortie,NbPlacesMax)
            VALUES (?,?,?,?)''', (id_compte, id_attraction, moment.isoformat(timespec='minutes'), places)).lastrowid


def participer(id_compte, id_sortie):
    with get_db() as conn:
        conn.execute('BEGIN IMMEDIATE')
        sortie = conn.execute('SELECT IdCompte FROM Sortie WHERE IdSortie=?', (id_sortie,)).fetchone()
        if sortie and sortie['IdCompte'] == id_compte:
            raise ValueError('Vous organisez déjà cette sortie.')
        demande = demander_participation(conn, id_compte, id_sortie, datetime.now())
        enregistrer_demande(conn, demande)
        return demande


def demandes_organisateur(id_compte):
    with get_db() as conn:
        return [dict(row) for row in conn.execute('''SELECT d.*, c.NomCompte,a.NameAttraction
            FROM Demande d JOIN Compte c ON c.IdCompte=d.IdCompte
            JOIN Sortie s ON s.IdSortie=d.IdSortie JOIN Attraction a ON a.IdAttraction=s.IdAttraction
            WHERE s.IdCompte=? ORDER BY d.IdSortie DESC,c.NomCompte''', (id_compte,))]


def decider(id_organisateur, id_sortie, id_membre, statut):
    if statut not in ('Acceptée', 'Refusée'):
        raise ValueError('La décision est invalide.')
    with get_db() as conn:
        conn.execute('BEGIN IMMEDIATE')
        sortie = conn.execute('SELECT * FROM Sortie WHERE IdSortie=? AND IdCompte=?',
                              (id_sortie, id_organisateur)).fetchone()
        if not sortie:
            raise ValueError('Cette sortie ne vous appartient pas.')
        if datetime.fromisoformat(sortie['DateHeureSortie']) <= datetime.now():
            raise ValueError('Cette sortie est déjà passée.')
        demande = conn.execute('SELECT * FROM Demande WHERE IdSortie=? AND IdCompte=?',
                               (id_sortie, id_membre)).fetchone()
        if not demande or demande['StatutDemande'] != 'En attente':
            raise ValueError('Aucune demande en attente ne correspond.')
        occupes = conn.execute("SELECT COUNT(*) FROM Demande WHERE IdSortie=? AND StatutDemande='Acceptée'",
                               (id_sortie,)).fetchone()[0]
        if statut == 'Acceptée' and occupes >= sortie['NbPlacesMax']:
            raise ValueError('Cette sortie est complète.')
        conn.execute('UPDATE Demande SET StatutDemande=? WHERE IdSortie=? AND IdCompte=?',
                     (statut, id_sortie, id_membre))
