
from database.catalogue_repository import charger_catalogue

catalogue = charger_catalogue()

print(f"\nNombre d'attractions : {len(catalogue)}\n")

for lieu in catalogue[:10]:
    print(f"ID : {lieu['id_lieu']}")
    print(f"Nom : {lieu['nom']}")
    print(f"Catégorie : {lieu['categorie']}")
    print(f"Prix : {lieu['prix']}")
    print(f"Adresse : {lieu['adresse']}")
    print("-" * 40)