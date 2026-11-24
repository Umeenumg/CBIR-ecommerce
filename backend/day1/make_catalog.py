import csv
import random
import shutil
from pathlib import Path
 
SRC = Path("catalogue")
IMG_DST = Path("../static/images")
CSV_DST = Path("../data/products.csv")
IMG_DST.mkdir(parents=True, exist_ok=True)
CSV_DST.parent.mkdir(parents=True, exist_ok=True)
 
random.seed(1)
rows = []
for cat_dir in sorted(SRC.iterdir()):
    for i, img in enumerate(sorted(cat_dir.glob("*.*")), 1):
        new_name = f"{cat_dir.name}_{i:02d}{img.suffix.lower()}"
        shutil.copy(img, IMG_DST / new_name)
        rows.append({
            "name": f"{cat_dir.name.capitalize()} {i}",
            "category": cat_dir.name,
            "brand": random.choice(["Acme", "Nova", "Orion"]),
            "price": round(random.uniform(20, 900), 2),
            "description": f"Produit de test ({cat_dir.name})",
            "image_file": new_name,
        })
 
fields = ["name", "category", "brand", "price", "description", "image_file"]
with open(CSV_DST, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "produits ->", CSV_DST)