import sqlite3
from datetime import datetime
from pathlib import Path
from database import connection

from sorties import (
    STATUT_ACCEPTEE,
    demander_participation,
    enregistrer_demande,
    inserer_donnees_demo,
)


def creer_base():
    conn = sqlite3.connect(":memory:")
    schema = Path(__file__).parent / "database" / "schema.sql"
    conn.executescript(schema.read_text(encoding="utf-8"))
    ids = inserer_donnees_demo(conn)
    return conn, ids


def tenter_demande(conn, id_membre, id_sortie):
    try:
        demande = demander_participation(conn, id_membre, id_sortie, datetime.now())
        enregistrer_demande(conn, demande)
        return "Demande enregistrée (" + demande["statut"] + ")"
    except ValueError as erreur:
        return str(erreur)
    except sqlite3.IntegrityError as erreur:
        return "Erreur de la base de données : " + str(erreur)


def afficher(code, titre, entree, attendu, observe):
    print(code, "-", titre)
    print("  Entrée  :", entree)
    print("  Attendu :", attendu)
    print("  Observé :", observe)
    if attendu == observe:
        print("  Verdict : RÉUSSI")
    else:
        print("  Verdict : ÉCHEC")
    print()


def t07_demande_valide():
    conn, ids = creer_base()
    sortie = ids["sortie_libre"]
    sql = "SELECT COUNT(*) FROM Demande WHERE IdSortie = ? AND StatutDemande = ?"
    avant = conn.execute(sql, (sortie, STATUT_ACCEPTEE)).fetchone()[0]
    observe = tenter_demande(conn, ids["membre_demo"], sortie)
    apres = conn.execute(sql, (sortie, STATUT_ACCEPTEE)).fetchone()[0]
    observe = observe + " ; places occupées : " + str(avant) + " -> " + str(apres)
    afficher("T07", "Demande valide", "membre démo, sortie libre (1 place libre)",
             "Demande enregistrée (En attente) ; places occupées : 2 -> 2", observe)


def t08_sortie_complete():
    conn, ids = creer_base()
    observe = tenter_demande(conn, ids["membre_demo"], ids["sortie_complete"])
    afficher("T08", "Sortie complète", "membre démo, sortie complète",
             "Cette sortie est complète.", observe)


def t09_demande_en_double():
    conn, ids = creer_base()
    membre = ids["membre_demo"]
    sortie = ids["sortie_libre"]
    tenter_demande(conn, membre, sortie)
    observe = tenter_demande(conn, membre, sortie)
    sql = "SELECT COUNT(*) FROM Demande WHERE IdSortie = ? AND IdCompte = ?"
    nb = conn.execute(sql, (sortie, membre)).fetchone()[0]
    observe = observe + " ; demandes enregistrées : " + str(nb)
    afficher("T09", "Demande en double", "membre démo, sortie libre, deux fois de suite",
             "Vous avez déjà fait une demande pour cette sortie. ; demandes enregistrées : 1", observe)


def r1_sortie_inexistante():
    conn, ids = creer_base()
    observe = tenter_demande(conn, ids["membre_demo"], 99999)
    afficher("R1", "Sortie inexistante", "membre démo, sortie 99999",
             "Cette sortie n'existe pas.", observe)


def r2_sortie_passee():
    conn, ids = creer_base()
    observe = tenter_demande(conn, ids["membre_demo"], ids["sortie_passee"])
    afficher("R2", "Sortie passée", "membre démo, sortie passée",
             "Cette sortie est déjà passée.", observe)


def r3_membre_non_identifie():
    conn, ids = creer_base()
    observe = tenter_demande(conn, None, ids["sortie_libre"])
    afficher("R3", "Membre non identifié", "aucun membre, sortie libre",
             "Vous devez être identifié pour faire une demande.", observe)


if __name__ == "__main__":
    t07_demande_valide()
    t08_sortie_complete()
    t09_demande_en_double()
    r1_sortie_inexistante()
    r2_sortie_passee()
    r3_membre_non_identifie()
