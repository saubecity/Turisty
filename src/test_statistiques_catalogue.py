from collections import Counter
from database.catalogue_repository import charger_catalogue

catalogue = charger_catalogue()

prix_gratuits = sum(1 for lieu in catalogue if lieu["prix"] == 0)
prix_inconnus = sum(1 for lieu in catalogue if lieu["prix"] is None)
prix_connus = sum(1 for lieu in catalogue if lieu["prix"] is not None)
adresses_connues = sum(1 for lieu in catalogue if lieu["adresse"] is not None)

categories = Counter(lieu["categorie"] for lieu in catalogue)

print("TOTAL :", len(catalogue))
print("Prix gratuits :", prix_gratuits)
print("Prix inconnus :", prix_inconnus)
print("Prix connus :", prix_connus)
print("Adresses connues :", adresses_connues)

print("\nCatégories :")
for categorie, nombre in categories.most_common():
    print(f"{categorie} : {nombre}")