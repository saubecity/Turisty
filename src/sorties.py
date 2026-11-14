from datetime import datetime, timedelta

STATUT_ATTENTE = "En attente"
STATUT_ACCEPTEE = "Acceptée"
STATUT_REFUSEE = "Refusée"


def demander_participation(conn, id_membre, id_sortie, maintenant):
    if id_membre is None:
        raise ValueError("Vous devez être identifié pour faire une demande.")

    ligne = conn.execute(
        "SELECT DateHeureSortie, NbPlacesMax FROM Sortie WHERE IdSortie = ?",
        (id_sortie,), 
    ).fetchone()
    if ligne is None:
        raise ValueError("Cette sortie n'existe pas.")
    date_heure, nb_places_max = ligne

    if datetime.fromisoformat(date_heure) < maintenant:
        raise ValueError("Cette sortie est déjà passée.")

    existante = conn.execute(
        "SELECT 1 FROM Demande WHERE IdSortie = ? AND IdCompte = ?",
        (id_sortie, id_membre),  
    ).fetchone()
    if existante is not None:
        raise ValueError("Vous avez déjà fait une demande pour cette sortie.")

 
    acceptees = conn.execute(
        "SELECT COUNT(*) FROM Demande WHERE IdSortie = ? AND StatutDemande = ?",
        (id_sortie, STATUT_ACCEPTEE),
    ).fetchone()[0]
    if acceptees >= nb_places_max: 
        raise ValueError("Cette sortie est complète.")

    return {"id_membre": id_membre, "id_sortie": id_sortie, "statut": STATUT_ATTENTE}

def enregistrer_demande(conn, demande):
    conn.execute(
        "INSERT INTO Demande (IdSortie, IdCompte, StatutDemande) VALUES (?, ?, ?)",
        (demande["id_sortie"], demande["id_membre"], demande["statut"]),
    )
    conn.commit()
def _inserer(conn, sql, valeurs):
    return conn.execute(sql, valeurs).lastrowid


def inserer_donnees_demo(conn):
    maintenant = datetime.now()
    futur = (maintenant + timedelta(days=7)).isoformat(sep=" ", timespec="seconds")
    passe = (maintenant - timedelta(days=7)).isoformat(sep=" ", timespec="seconds")

    sql_compte = "INSERT INTO Compte (NomCompte, EmailCompte, MotdePasse) VALUES (?, ?, ?)"
    organisateur = _inserer(conn, sql_compte, ("Organisateur Démo", "organisateur@demo.ca", "hash-demo"))
    membre_demo = _inserer(conn, sql_compte, ("Membre Démo", "membre@demo.ca", "hash-demo"))
    accepte_1 = _inserer(conn, sql_compte, ("Ami Accepté 1", "accepte1@demo.ca", "hash-demo"))
    accepte_2 = _inserer(conn, sql_compte, ("Ami Accepté 2", "accepte2@demo.ca", "hash-demo"))
    ami_refuse = _inserer(conn, sql_compte, ("Ami Refusé", "refuse@demo.ca", "hash-demo"))
    
    attraction = _inserer(
        conn,
        "INSERT INTO Attraction (NameAttraction, AdresseAttraction, TypeAttraction, PrixAttraction, AgeAttraction) "
        "VALUES (?, ?, ?, ?, ?)",
        ("Biodôme (démo)", "4777 avenue Pierre-De Coubertin", "activite", 20, "tous"),
    )

    sql_sortie = "INSERT INTO Sortie (IdCompte, IdAttraction, DateHeureSortie, NbPlacesMax) VALUES (?, ?, ?, ?)"
    sortie_libre = _inserer(conn, sql_sortie, (organisateur, attraction, futur, 3))
    sortie_complete = _inserer(conn, sql_sortie, (organisateur, attraction, futur, 2))
    sortie_passee = _inserer(conn, sql_sortie, (organisateur, attraction, passe, 3))


    sql_demande = "INSERT INTO Demande (IdSortie, IdCompte, StatutDemande) VALUES (?, ?, ?)"
    for id_sortie in (sortie_libre, sortie_complete):
        conn.execute(sql_demande, (id_sortie, accepte_1, STATUT_ACCEPTEE))
        conn.execute(sql_demande, (id_sortie, accepte_2, STATUT_ACCEPTEE))
    conn.execute(sql_demande, (sortie_libre, ami_refuse, STATUT_REFUSEE))
    conn.commit()

    return {
        "organisateur": organisateur,
        "membre_demo": membre_demo,
        "ami_refuse": ami_refuse,
        "sortie_libre": sortie_libre,
        "sortie_complete": sortie_complete,
        "sortie_passee": sortie_passee,
    }