PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Compte (
    IdCompte    INTEGER PRIMARY KEY AUTOINCREMENT,
    NomCompte   TEXT    NOT NULL,
    EmailCompte TEXT    NOT NULL UNIQUE,
    MotdePasse  TEXT    NOT NULL, -- as a hash
    RoleCompte  TEXT    NOT NULL DEFAULT 'membre' 
);

CREATE TABLE IF NOT EXISTS Attraction (
    IdAttraction      INTEGER PRIMARY KEY AUTOINCREMENT,
    NameAttraction    TEXT    NOT NULL,
    AdresseAttraction TEXT    NOT NULL,
    TypeAttraction    TEXT    NOT NULL,
    PrixAttraction    NUMERIC NOT NULL DEFAULT 0 CHECK (PrixAttraction >= 0),
    AgeAttraction     TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS program (
    IdProgram  INTEGER PRIMARY KEY AUTOINCREMENT,
    IdCompte   INTEGER NOT NULL,
    Nomprogram TEXT    NOT NULL,
    budget     NUMERIC NOT NULL CHECK (budget >= 0),
    NbDays     INTEGER NOT NULL CHECK (NbDays BETWEEN 1 AND 3),
    FOREIGN KEY (IdCompte) REFERENCES Compte (IdCompte) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Etape (
    IdEtape      INTEGER PRIMARY KEY AUTOINCREMENT,
    IdProgram    INTEGER NOT NULL,
    IdAttraction INTEGER NOT NULL,
    Numerojour   INTEGER NOT NULL CHECK (Numerojour BETWEEN 1 AND 3),
    FOREIGN KEY (IdProgram)    REFERENCES program (IdProgram) ON DELETE CASCADE,
    FOREIGN KEY (IdAttraction) REFERENCES Attraction (IdAttraction)
);

CREATE TABLE IF NOT EXISTS Sortie (
    IdSortie        INTEGER PRIMARY KEY AUTOINCREMENT,
    IdCompte        INTEGER NOT NULL,
    IdAttraction    INTEGER NOT NULL,
    DateHeureSortie TEXT    NOT NULL,
    NbPlacesMax     INTEGER NOT NULL CHECK (NbPlacesMax >= 1),
    FOREIGN KEY (IdCompte)     REFERENCES Compte (IdCompte),
    FOREIGN KEY (IdAttraction) REFERENCES Attraction (IdAttraction)
);

CREATE TABLE IF NOT EXISTS Demande (
    IdSortie      INTEGER NOT NULL,
    IdCompte      INTEGER NOT NULL,
    StatutDemande TEXT    NOT NULL DEFAULT 'En attente'
        CHECK (StatutDemande IN ('En attente', 'Acceptée', 'Refusée')),
    PRIMARY KEY (IdSortie, IdCompte),
    FOREIGN KEY (IdSortie) REFERENCES Sortie (IdSortie) ON DELETE CASCADE,
    FOREIGN KEY (IdCompte) REFERENCES Compte (IdCompte) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Message (
    IdMessage      INTEGER PRIMARY KEY AUTOINCREMENT,
    IdSortie       INTEGER NOT NULL,
    IdCompte       INTEGER NOT NULL,
    ContenuMessage TEXT    NOT NULL,
    DateEnvoi      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (IdSortie) REFERENCES Sortie (IdSortie) ON DELETE CASCADE,
    FOREIGN KEY (IdCompte) REFERENCES Compte (IdCompte) ON DELETE CASCADE
);