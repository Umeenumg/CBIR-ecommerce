
import csv
from bson import Binary

import config
from db.mongo import products
from cbir.preprocess import load_image
from cbir.feature_extractor import extract_batch


SOURCES_CSV = config.BASE_DIR.parent / "data" / "image_sources.csv"


def load_image_mapping():
    """Construit le mapping image catalogue -> ID de l'image originale."""

    mapping = {}

    with open(SOURCES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["role"] == "catalogue":
                mapping[row["image_file"]] = row["source_id"]

    return mapping


def main():
    col = products()

    # 1. Charger le mapping depuis image_sources.csv
    image_mapping = load_image_mapping()

    print("Images catalogue dans le CSV :", len(image_mapping))

    # 2. Traiter uniquement les produits sans features
    cursor = col.find({"features": {"$exists": False}})

    done = 0
    skipped = 0

    for doc in cursor:
        image_file = doc["image_path"]

        # 3. Retrouver l'identifiant de l'image originale
        source_id = image_mapping.get(image_file)

        if source_id is None:
            print("Mapping introuvable :", image_file)
            skipped += 1
            continue

        # 4. Construire le chemin vers l'image originale
        image_path = (
            config.IMAGES_DIR
            / doc["category"]
            / f"fashion_prod_{source_id}.jpg"
        )

        if not image_path.exists():
            print("Image introuvable :", image_path)
            skipped += 1
            continue

        # 5. Charger l'image et extraire son vecteur
        img = load_image(image_path)
        vec = extract_batch([img])[0]

        # 6. Convertir le vecteur en BSON Binary
        blob = Binary(vec.astype("float32").tobytes())

        # 7. Enregistrer le vecteur dans le document existant
        col.update_one(
            {"_id": doc["_id"]},
            {"$set": {"features": blob}}
        )

        done += 1
        print(done, doc["name"])

    print("\nTermine :", done, "vecteurs extraits")
    print("Images ignorees :", skipped)


if __name__ == "__main__":
    main()
