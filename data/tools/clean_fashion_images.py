
from pathlib import Path
import pandas as pd

CSV_PATH = Path("data/downloads/fashion_subset/styles_subset.csv")
IMAGES_DIR = Path("data/downloads/fashion_subset/images")

df = pd.read_csv(CSV_PATH)

# IDs des produits présents dans le CSV
valid_ids = set(df["id"].astype(str))

# Images réellement présentes
image_files = list(IMAGES_DIR.glob("*.jpg"))

to_keep = []
to_remove = []

for image in image_files:
    if image.stem in valid_ids:
        to_keep.append(image)
    else:
        to_remove.append(image)

print("Images actuelles :", len(image_files))
print("Images à garder  :", len(to_keep))
print("Images en trop   :", len(to_remove))

print("\nAucune image supprimée. Vérification uniquement.")
# Supprimer uniquement les images absentes du CSV
for image in to_remove:
    image.unlink()

print(f"\n{len(to_remove)} images supprimées.")
print(f"{len(to_keep)} images conservées.")