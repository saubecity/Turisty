
import sqlite3
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from catalogue import filtrer_lieux, trouver_lieu
from database.catalogue_repository import charger_catalogue


router = APIRouter(
    prefix="/catalogue",
    tags=["Catalogue"]
)


@router.get("")
def afficher_catalogue(
    budget_max: Optional[float] = None,
    categorie: Optional[str] = None,
    interet: Optional[str] = None,
    tranche_age: Optional[str] = None,
    recherche: Optional[str] = None
) -> List[dict]:

    if budget_max is not None and budget_max < 0:
        raise HTTPException(
            status_code=422,
            detail="Le budget ne peut pas être négatif."
        )

    try:
        catalogue = charger_catalogue()

        resultats = filtrer_lieux(
            catalogue,
            budget_max=budget_max,
            categorie=categorie,
            interet=interet,
            tranche_age=tranche_age
        )

        if recherche:
            terme = recherche.strip().casefold()

            resultats = [
                lieu for lieu in resultats
                if terme in (lieu.get("nom") or "").casefold()
                or terme in (lieu.get("description") or "").casefold()
                or terme in (lieu.get("categorie") or "").casefold()
            ]

        return resultats

    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Le catalogue est temporairement indisponible."
        )


@router.get("/{id_lieu}")
def afficher_details_lieu(id_lieu: str) -> dict:

    try:
        catalogue = charger_catalogue()
        lieu = trouver_lieu(catalogue, id_lieu)

        if lieu is None:
            raise HTTPException(
                status_code=404,
                detail="Attraction introuvable."
            )

        return lieu

    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Le catalogue est temporairement indisponible."
        )
