import sqlite3
from datetime import datetime
from pathlib import Path

from sorties import (
    STATUT_ACCEPTEE,
    STATUT_ATTENTE,
    demander_participation,
    enregistrer_demande,
    inserer_donnees_demo,
)

SQL_ACCEPTEES = "SELECT COUNT(*) FROM Demande WHERE IdSortie = ? AND StatutDemande = ?"
SQL_DEMANDES_DU_MEMBRE = "SELECT COUNT(*) FROM Demande WHERE IdSortie = ? AND IdCompte = ?"

resultats = []  # un True ou un False par test


def creer_base_test():
    """Base SQLite en mémoire : le schéma du projet + les données de démonstration."""
    conn = sqlite3.connect(":memory:")
    schema = Path(__file__).parent / "database" / "schema.sql"
    conn.executescript(schema.read_text(encoding="utf-8"))
    ids = inserer_donnees_demo(conn)
    return conn, ids


def compter(conn, sql, valeurs):
    return conn.execute(sql, valeurs).fetchone()[0]


def essayer(conn, id_membre, id_sortie):
    """Appelle la fonction testée. Renvoie (demande, None) si acceptée, (None, message) si refusée."""
    try:
        return demander_participation(conn, id_membre, id_sortie, datetime.now()), None
    except ValueError as e:
        return None, str(e)


def afficher(code, titre, entree, attendu, observe, reussi):
    print(f"{code} - {titre}")
    print(f"  Entrée  : {entree}")
    print(f"  Attendu : {attendu}")
    print(f"  Observé : {observe}")
    print(f"  Verdict : {'RÉUSSI' if reussi else 'ÉCHEC'}\n")
    resultats.append(reussi)


def test_refus(conn, code, titre, id_membre, id_sortie, message_attendu):
    """Test générique : la demande doit être refusée avec exactement ce message."""
    demande, erreur = essayer(conn, id_membre, id_sortie)
    observe = f"Refusé : {erreur}" if erreur else f"Acceptée : {demande}"
    afficher(code, titre, f"membre {id_membre}, sortie {id_sortie}",
             f"Refusé : {message_attendu}", observe, erreur == message_attendu)


def t07_demande_valide():
    conn, ids = creer_base_test()
    sortie = ids["sortie_libre"]
    avant = compter(conn, SQL_ACCEPTEES, (sortie, STATUT_ACCEPTEE))
    demande, erreur = essayer(conn, ids["membre_demo"], sortie)
    if demande is not None:
        enregistrer_demande(conn, demande)
    apres = compter(conn, SQL_ACCEPTEES, (sortie, STATUT_ACCEPTEE))
    reussi = demande is not None and demande["statut"] == STATUT_ATTENTE and avant == apres
    if demande is not None:
        observe = f"Demande « {demande['statut']} » créée, places occupées {avant} -> {apres}"
    else:
        observe = f"Refusé : {erreur}"
    afficher("T07", "Demande valide", f"membre {ids['membre_demo']}, sortie {sortie} (1 place libre)",
             "Demande « En attente » créée, places occupées inchangées", observe, reussi)


def t09_demande_en_double():
    conn, ids = creer_base_test()
    membre, sortie = ids["membre_demo"], ids["sortie_libre"]
    premiere, _ = essayer(conn, membre, sortie)
    enregistrer_demande(conn, premiere)
    _, erreur = essayer(conn, membre, sortie)
    nb = compter(conn, SQL_DEMANDES_DU_MEMBRE, (sortie, membre))
    message = "Vous avez déjà fait une demande pour cette sortie."
    resultat = f"Refusé : {erreur}" if erreur else "Acceptée"
    afficher("T09", "Demande en double", f"membre {membre}, sortie {sortie}, deux fois de suite",
             f"Refusé : {message} / 1 seule demande enregistrée",
             f"{resultat} / {nb} demande(s) enregistrée(s)", erreur == message and nb == 1)


if __name__ == "__main__":
    t07_demande_valide()

    conn, ids = creer_base_test()
    test_refus(conn, "T08", "Sortie complète", ids["membre_demo"], ids["sortie_complete"],
               "Cette sortie est complète.")

    t09_demande_en_double()

    test_refus(conn, "T09b", "Demande en double après un refus", ids["ami_refuse"], ids["sortie_libre"],
               "Vous avez déjà fait une demande pour cette sortie.")
    test_refus(conn, "R1", "Sortie inexistante", ids["membre_demo"], 99999,
               "Cette sortie n'existe pas.")
    test_refus(conn, "R2", "Sortie passée", ids["membre_demo"], ids["sortie_passee"],
               "Cette sortie est déjà passée.")
    test_refus(conn, "R3", "Membre non identifié", None, ids["sortie_libre"],
               "Vous devez être identifié pour faire une demande.")

    print(f"{sum(resultats)}/{len(resultats)} tests réussis")