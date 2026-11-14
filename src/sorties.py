from datetime import datetime, timedelta

STATUT_ATTENTE = "En attente"
STATUT_ACCEPTEE = "Acceptée"
STATUT_REFUSEE = "Refusée"


def demander_participation(conn, id_membre, id_sortie, maintenant):
    """Vérifie une demande de participation à une sortie.

    Si la demande est valide, renvoie un dict
    {"id_membre": ..., "id_sortie": ..., "statut": "En attente"} (le membre 4 l'enregistre).
    Si elle est refusée, lève ValueError avec un message en français.
    """
    # 1. le membre est identifié
    if id_membre is None:
        raise ValueError("Vous devez être identifié pour faire une demande.")

    # 2. la sortie existe
    ligne = conn.execute(
        "SELECT DateHeureSortie, NbPlacesMax FROM Sortie WHERE IdSortie = ?",
        (id_sortie,),  # la virgule est obligatoire : c'est un tuple d'un seul élément
    ).fetchone()
    if ligne is None:
        raise ValueError("Cette sortie n'existe pas.")
    date_heure, nb_places_max = ligne

    # 3. la sortie n'est pas déjà passée
    if datetime.fromisoformat(date_heure) < maintenant:
        raise ValueError("Cette sortie est déjà passée.")

    # 4. ce membre n'a pas déjà fait une demande pour cette sortie (peu importe son statut)
    existante = conn.execute(
        "SELECT 1 FROM Demande WHERE IdSortie = ? AND IdCompte = ?",
        (id_sortie, id_membre),  # même ordre que les ? : d'abord la sortie, ensuite le membre
    ).fetchone()
    if existante is not None:
        raise ValueError("Vous avez déjà fait une demande pour cette sortie.")

    # 5. il reste une place : seules les demandes acceptées occupent une place
    # COUNT(*) compte les lignes qui correspondent ; fetchone()[0] sort ce nombre de la ligne
    acceptees = conn.execute(
        "SELECT COUNT(*) FROM Demande WHERE IdSortie = ? AND StatutDemande = ?",
        (id_sortie, STATUT_ACCEPTEE),
    ).fetchone()[0]
    if acceptees >= nb_places_max:  # autant d'acceptées que de places : c'est plein
        raise ValueError("Cette sortie est complète.")

    return {"id_membre": id_membre, "id_sortie": id_sortie, "statut": STATUT_ATTENTE}


def enregistrer_demande(conn, demande):
    """Enregistre dans la base une demande validée par demander_participation.

    Si l'écriture échoue, une exception sqlite3 est levée : ne pas confirmer au membre.
    """
    conn.execute(
        "INSERT INTO Demande (IdSortie, IdCompte, StatutDemande) VALUES (?, ?, ?)",
        (demande["id_sortie"], demande["id_membre"], demande["statut"]),
    )
    conn.commit()


def _inserer(conn, sql, valeurs):
    """Exécute un INSERT et renvoie l'identifiant de la ligne créée."""
    return conn.execute(sql, valeurs).lastrowid


def inserer_donnees_demo(conn):
    """Ajoute les données de démonstration. À appeler une seule fois, sur une base vide.

    Crée un organisateur, un membre fictif, deux membres déjà acceptés, un membre refusé,
    et trois sorties : future avec une place libre, complète, passée.
    Renvoie un dict avec les identifiants créés.
    """
    maintenant = datetime.now()
    futur = (maintenant + timedelta(days=7)).isoformat(sep=" ", timespec="seconds")
    passe = (maintenant - timedelta(days=7)).isoformat(sep=" ", timespec="seconds")

    sql_compte = "INSERT INTO Compte (NomCompte, EmailCompte, MotdePasse) VALUES (?, ?, ?)"
    organisateur = _inserer(conn, sql_compte, ("Organisateur Démo", "organisateur@demo.ca", "hash-demo"))
    membre_demo = _inserer(conn, sql_compte, ("Membre Démo", "membre@demo.ca", "hash-demo"))
    accepte_1 = _inserer(conn, sql_compte, ("Ami Accepté 1", "accepte1@demo.ca", "hash-demo"))
    accepte_2 = _inserer(conn, sql_compte, ("Ami Accepté 2", "accepte2@demo.ca", "hash-demo"))
    ami_refuse = _inserer(conn, sql_compte, ("Ami Refusé", "refuse@demo.ca", "hash-demo"))

    # une sortie doit être liée à un lieu : on en crée un seul pour la démonstration
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

    # sortie libre : 2 acceptées sur 3 places (1 libre) + 1 refusée / sortie complète : 2 acceptées sur 2
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