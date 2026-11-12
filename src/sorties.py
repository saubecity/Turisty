







if __name__ == "__main__":
    maintenant = datetime.now()
    for id_sortie in (1, 99):
        try:
            demande = demander_participation(2, id_sortie, SORTIES_DEMO, DEMANDES_DEMO, maintenant)
            print("OK :", demande)
        except ValueError as e:
            print("Refusé :", e)