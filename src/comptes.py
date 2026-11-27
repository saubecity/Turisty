import hashlib
import hmac
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from database.connection import get_db


class ErreurCompte(ValueError):
    pass


def hacher(mot_de_passe):
    sel = secrets.token_bytes(16)
    empreinte = hashlib.scrypt(mot_de_passe.encode(), salt=sel, n=16384, r=8, p=1)
    return 'scrypt$' + sel.hex() + '$' + empreinte.hex()


def verifier(mot_de_passe, valeur):
    try:
        methode, sel, attendu = valeur.split('$')
        if methode != 'scrypt':
            return False
        observe = hashlib.scrypt(mot_de_passe.encode(), salt=bytes.fromhex(sel), n=16384, r=8, p=1)
        return hmac.compare_digest(observe.hex(), attendu)
    except (ValueError, TypeError):
        return False


def creer_compte(nom, courriel, mot_de_passe):
    nom, courriel = nom.strip(), courriel.strip().lower()
    if not 2 <= len(nom) <= 80:
        raise ErreurCompte('Le nom doit contenir entre 2 et 80 caractères.')
    if len(courriel) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', courriel):
        raise ErreurCompte('Le courriel est invalide.')
    if not 10 <= len(mot_de_passe) <= 128:
        raise ErreurCompte('Le mot de passe doit contenir entre 10 et 128 caractères.')
    try:
        with get_db() as conn:
            if conn.execute('SELECT 1 FROM Compte WHERE lower(EmailCompte)=?', (courriel,)).fetchone():
                raise ErreurCompte('Ce courriel est déjà utilisé.')
            cursor = conn.execute('INSERT INTO Compte (NomCompte,EmailCompte,MotdePasse) VALUES (?,?,?)',
                                  (nom, courriel, hacher(mot_de_passe)))
            return cursor.lastrowid
    except sqlite3.IntegrityError as erreur:
        raise ErreurCompte('Ce courriel est déjà utilisé.') from erreur


def ouvrir_session(courriel, mot_de_passe):
    with get_db() as conn:
        row = conn.execute('SELECT * FROM Compte WHERE lower(EmailCompte)=?',
                           (courriel.strip().lower(),)).fetchone()
        # Même coût de hachage pour un compte absent.
        valeur = row['MotdePasse'] if row else 'scrypt$' + '00' * 16 + '$' + '00' * 64
        valide = verifier(mot_de_passe, valeur)
        if not row or not valide:
            raise ErreurCompte('Courriel ou mot de passe incorrect.')
        jeton, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        expiration = (datetime.now(timezone.utc) + timedelta(hours=12)).isoformat()
        conn.execute('DELETE FROM SessionCompte WHERE Expiration < ?', (datetime.now(timezone.utc).isoformat(),))
        conn.execute('INSERT INTO SessionCompte VALUES (?,?,?,?)',
                     (hashlib.sha256(jeton.encode()).hexdigest(), row['IdCompte'], csrf, expiration))
        return jeton


def compte_session(jeton):
    if not jeton:
        return None
    with get_db() as conn:
        row = conn.execute('''SELECT c.IdCompte, c.NomCompte, c.EmailCompte, s.Csrf
            FROM SessionCompte s JOIN Compte c ON c.IdCompte=s.IdCompte
            WHERE s.JetonHash=? AND s.Expiration>?''',
            (hashlib.sha256(jeton.encode()).hexdigest(), datetime.now(timezone.utc).isoformat())).fetchone()
        return dict(row) if row else None


def fermer_session(jeton):
    with get_db() as conn:
        conn.execute('DELETE FROM SessionCompte WHERE JetonHash=?',
                     (hashlib.sha256(jeton.encode()).hexdigest(),))
