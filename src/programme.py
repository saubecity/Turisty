from catalogue import catalogue, filtrer_lieux


def generer_programme(lieux, budget_total, nb_personnes, duree_jours,
                      interet=None, tranche_age=None):
    if not isinstance(budget_total, (int, float)) or budget_total < 0:
        raise ValueError("Le budget total doit être un nombre positif ou nul.")

    if not isinstance(nb_personnes, int) or nb_personnes < 1:
        raise ValueError("Il faut au moins une personne.")

    if not isinstance(duree_jours, int) or duree_jours < 1 or duree_jours > 3:
        raise ValueError("La durée du séjour doit être de 1 à 3 jours.")

    lieux_compatibles = filtrer_lieux(
        lieux, interet=interet, tranche_age=tranche_age
    )

    lieux_disponibles = []
    for lieu in lieux_compatibles:
        if lieu["unite_prix"] == "Par personne":
            lieux_disponibles.append(lieu)

    if len(lieux_disponibles) < duree_jours:
        raise ValueError("Il n'y a pas assez de lieux compatibles.")

    journees = []
    cout_total = 0

    for numero_jour in range(1, duree_jours + 1):
        indice_moins_cher = 0

        for i in range(1, len(lieux_disponibles)):
            if lieux_disponibles[i]["prix"] < lieux_disponibles[indice_moins_cher]["prix"]:
                indice_moins_cher = i

        lieu = lieux_disponibles.pop(indice_moins_cher)
        cout_jour = lieu["prix"] * nb_personnes
        cout_total = cout_total + cout_jour

        journees.append({
            "numero_jour": numero_jour,
            "id_lieu": lieu["id_lieu"],
            "nom": lieu["nom"],
            "cout": cout_jour
        })

    if cout_total > budget_total:
        raise ValueError("Aucun programme ne respecte ce budget.")

    return {
        "duree_jours": duree_jours,
        "nb_personnes": nb_personnes,
        "budget_total": budget_total,
        "journees": journees,
        "cout_total": cout_total,
        "budget_restant": budget_total - cout_total
    }


if __name__ == "__main__":
    print("T04 - Séjour valide")
    programme = generer_programme(
        catalogue, 150, 2, 2, "Arts", "16-17 ans"
    )

    for journee in programme["journees"]:
        print("Jour", journee["numero_jour"], ":", journee["nom"])

    print("Coût total :", programme["cout_total"], "$")
    print("Budget restant :", programme["budget_restant"], "$")

    print("\nT05 - Durée invalide")
    try:
        generer_programme(catalogue, 150, 2, 4)
    except ValueError as erreur:
        print(erreur)

    print("\nT06 - Budget insuffisant")
    try:
        generer_programme(catalogue, 100, 2, 2, "Arts", "16-17 ans")
    except ValueError as erreur:
        print(erreur)