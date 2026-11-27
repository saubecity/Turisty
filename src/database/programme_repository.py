from database.connection import get_db


def sauvegarder_programme(id_compte, nom, programme):
    nom = nom.strip()
    if not 1 <= len(nom) <= 100:
        raise ValueError('Donnez un nom de 1 à 100 caractères au séjour.')
    if not programme.get('date_debut') or not programme['journees']:
        raise ValueError('Le programme doit contenir des journées datées.')
    with get_db() as conn:
        cursor = conn.execute('''INSERT INTO program
            (IdCompte,Nomprogram,budget,StartDate,EndDate,NbPersonnes,CoutTotal,Interet,TrancheAge,Categorie)
            VALUES (?,?,?,?,?,?,?,?,?,?)''',
            (id_compte, nom, programme['budget_total'], programme['date_debut'],
             programme['journees'][-1]['date'], programme['nb_personnes'], programme['cout_total'],
             programme.get('interet'), programme.get('tranche_age'), programme.get('categorie')))
        id_programme = cursor.lastrowid
        for jour in programme['journees']:
            step = conn.execute('INSERT INTO Etape (IdProgram,IdAttraction,StartDate,EndDate) VALUES (?,?,?,?)',
                                (id_programme, int(jour['id_lieu']), jour['date'], jour['date']))
            conn.execute('INSERT INTO EtapeDetails VALUES (?,?,?,?)',
                         (step.lastrowid, jour['numero_jour'], jour['nom'], jour['cout']))
        return id_programme


def lister_programmes(id_compte):
    with get_db() as conn:
        programmes = [dict(row) for row in conn.execute(
            'SELECT * FROM program WHERE IdCompte=? ORDER BY IdProgram DESC', (id_compte,))]
        for programme in programmes:
            programme['journees'] = [dict(row) for row in conn.execute('''
                SELECT e.IdAttraction AS id_lieu, e.StartDate AS date,
                       COALESCE(d.NomLieu,a.NameAttraction) AS nom,
                       d.NumeroJour AS numero_jour, d.Cout AS cout
                FROM Etape e JOIN Attraction a ON a.IdAttraction=e.IdAttraction
                LEFT JOIN EtapeDetails d ON d.IdEtape=e.IdEtape
                WHERE e.IdProgram=? ORDER BY e.StartDate,e.IdEtape''', (programme['IdProgram'],))]
        return programmes


def supprimer_programme(id_compte, id_programme):
    with get_db() as conn:
        cursor = conn.execute('DELETE FROM program WHERE IdProgram=? AND IdCompte=?',
                              (id_programme, id_compte))
        if not cursor.rowcount:
            raise ValueError('Programme introuvable pour ce compte.')
