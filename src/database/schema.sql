-- this file is executed on server start to insure the table structures exist
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
    AdresseAttraction TEXT,
    Description TEXT,
    date_debut TEXT,
    date_fin TEXT,
    TypeAttraction    TEXT    NOT NULL,
    PrixAttraction    NUMERIC DEFAULT 0 CHECK (PrixAttraction >= 0),
    MinAge INTEGER CHECK (MinAge >= 0), -- can be NULL for no min or max age, if both are NULL, the event has no age restrictions
    MaxAge INTEGER CHECK (MaxAge >= MinAge),
    Latitude REAL,
    Longitude REAL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'postponed')),
    dataset_id TEXT,
    FOREIGN KEY (dataset_id) REFERENCES dataset_metadata(dataset_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_attraction_triple ON Attraction(NameAttraction, date_debut, dataset_id);

CREATE TABLE IF NOT EXISTS program (
    IdProgram  INTEGER PRIMARY KEY AUTOINCREMENT,
    IdCompte   INTEGER NOT NULL,
    Nomprogram TEXT    NOT NULL,
    budget     NUMERIC NOT NULL CHECK (budget >= 0),
    StartDate TEXT NOT NULL,
    EndDate TEXT NOT NULL CHECK (EndDate >= StartDate),
    FOREIGN KEY (IdCompte) REFERENCES Compte (IdCompte) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Etape (
    IdEtape      INTEGER PRIMARY KEY AUTOINCREMENT,
    IdProgram    INTEGER NOT NULL,
    IdAttraction INTEGER NOT NULL,
    StartDate TEXT NOT NULL,
    EndDate TEXT NOT NULL CHECK (EndDate >= StartDate),
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

-- this table exists to sync external datasets with ours
CREATE TABLE IF NOT EXISTS dataset_metadata (
    dataset_id TEXT PRIMARY KEY,
    dataset_url TEXT NOT NULL,
    fetched_date TEXT NOT NULL, -- as a date
    expiration_date TEXT NOT NULL
)
