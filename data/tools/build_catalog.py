
"""Construit le catalogue a partir des images triees de data/raw/<categorie>/.

Pour chaque categorie :
  - supprime les images trop petites et les doublons exacts,
  - met N_TEST images de cote -> evaluation/test_images/,
  - copie le reste -> backend/static/images/,
puis ecrit :
  - data/products.csv
  - evaluation/annotations.csv
  - data/image_sources.csv

Usage depuis la racine :
  python -m data.tools.build_catalog --tests 6 --seed 42
"""

import argparse
import csv
import hashlib
import random
from pathlib import Path

from PIL import Image

from data.tools.categories import config_for


ROOT = Path(__file__).resolve().parents[2]

RAW = ROOT / "data" / "raw"
OUT_IMG = ROOT / "backend" / "static" / "images"
TEST_DIR = ROOT / "evaluation" / "test_images"

PRODUCTS_CSV = ROOT / "data" / "products.csv"
ANNOT_CSV = ROOT / "evaluation" / "annotations.csv"
SOURCES_OUT = ROOT / "data" / "image_sources.csv"

MAX_SIDE = 500
MIN_SIDE = 200


def file_hash(path):
    """Calcule une empreinte SHA-256 du contenu exact du fichier."""
    digest = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()

def extract_brand(name):
    if not name:
        return ""

    known_brands = [
        "United Colors of Benetton",
        "Gini and Jony",
        "American Tourister",
        "Peter England",
        "Van Heusen",
        "Park Avenue",
        "Lino Perros",
        "Vital Gear",
        "Timberland",
        "Provogue",
        "Wrangler",
        "Playboy",
        "Chromozome",
        "Heart 2 Heart",
        "New Hide",
        "Levitate",
        "Fastrack",
        "Wildcraft",
        "Baggit",
        "Arrow",
        "Parx",
        "Stoln",
        "Avirate",
        "Hanes",
        "Pieces",
        "Adidas",
        "Nike",
        "Puma",
        "Lee",
        "Fossil",
        "Belkin",
        "Levis",
        "Levi's",
    ]

    name_lower = name.strip().lower()

    for brand in known_brands:
        if name_lower.startswith(brand.lower()):
            return brand

    return ""
def load_valid(folder):
    """Charge les images valides et elimine uniquement les doublons exacts."""

    kept = []
    hashes = set()

    skipped = {
        "petite": 0,
        "doublon": 0,
        "illisible": 0
    }

    for p in sorted(folder.glob("*.jpg")):

        # 1. Verification de l'image
        try:
            with Image.open(p) as original:
                original.load()

                if min(original.size) < MIN_SIDE:
                    skipped["petite"] += 1
                    continue

                img = original.convert("RGB")

        except Exception:
            skipped["illisible"] += 1
            continue

        # 2. Detection des doublons exacts
        digest = file_hash(p)

        if digest in hashes:
            skipped["doublon"] += 1
            continue

        hashes.add(digest)

        # 3. Conservation de l'image
        kept.append((p, img))

    return kept, skipped


def save_jpeg(img, dest):
    """Redimensionne et sauvegarde une image au format JPEG."""

    img = img.copy()
    img.thumbnail((MAX_SIDE, MAX_SIDE))

    img.save(dest, "JPEG", quality=88)


def clear_old(folder, prefix):
    """Supprime les anciens fichiers generes pour une categorie."""

    if folder.exists():
        for old in folder.glob(f"{prefix}_*.jpg"):
            old.unlink()


def load_csv_mapping(path):
    """Charge un CSV et construit un dictionnaire indexe par file."""

    if not path.exists():
        return {}

    with open(path, newline="", encoding="utf-8") as f:
        return {
            row["file"]: row
            for row in csv.DictReader(f)
        }


def main():

    ap = argparse.ArgumentParser()

    ap.add_argument(
        "--tests",
        type=int,
        default=6,
        help="Nombre d'images de requete par categorie"
    )

    ap.add_argument(
        "--seed",
        type=int,
        default=42
    )

    args = ap.parse_args()

    if args.tests < 0:
        ap.error("--tests doit etre positif ou nul")

    rng = random.Random(args.seed)

    # Creation des dossiers de sortie
    OUT_IMG.mkdir(parents=True, exist_ok=True)
    TEST_DIR.mkdir(parents=True, exist_ok=True)

    # Chargement des sources et metadonnees
    credits = load_csv_mapping(RAW / "sources.csv")
    meta = load_csv_mapping(RAW / "metadata.csv")

    products = []
    annotations = []
    sources = []

    # Detection des categories disponibles
    categories = sorted(
        d.name for d in RAW.iterdir() if d.is_dir()
    ) if RAW.exists() else []

    if not categories:
        print("Aucun dossier dans data/raw/.")
        print("Lance import_dataset.py ou fetch_pexels.py d'abord.")
        return

    # Traitement de chaque categorie
    for cat in categories:

        cfg = config_for(cat)
        folder = RAW / cat

        kept, skipped = load_valid(folder)

        rng.shuffle(kept)

        tests = kept[:args.tests]
        catalogue = kept[args.tests:]

        # Nettoyage des anciennes images generees
        clear_old(OUT_IMG, cat)
        clear_old(TEST_DIR, cat)

        def src_row(name, role, key):
            c = credits.get(key, {})

            return {
                "image_file": name,
                "role": role,
                "source": c.get("source", ""),
                "source_id": c.get("source_id", ""),
                "author": c.get("author", ""),
                "url": c.get("url", "")
            }

        # Images de requete
        for j, (p, img) in enumerate(tests, 1):

            name = f"{cat}_q{j}.jpg"

            save_jpeg(img, TEST_DIR / name)

            annotations.append({
                "file": name,
                "expected_category": cat
            })

            sources.append(
                src_row(name, "requete", f"{cat}/{p.name}")
            )

        # Images du catalogue
        lo, hi = cfg["price"]

        for i, (p, img) in enumerate(catalogue, 1):

            name = f"{cat}_{i:02d}.jpg"

            save_jpeg(img, OUT_IMG / name)

            m = meta.get(f"{cat}/{p.name}", {})

            brand = m.get("brand") or extract_brand(m.get("name", ""))

            model = (
                f"{rng.choice(['Pro', 'Lite', 'Max', 'Plus', 'S'])} "
                f"{rng.randint(100, 999)}"
            )

            default_name = f"{cfg['label']} {brand} {model}"

            price = (
                float(m["price"])
                if m.get("price")
                else round(rng.uniform(lo, hi), 2)
            )

            products.append({
                "name": m.get("name") or default_name,
                "category": cat,
                "brand": brand,
                "price": price,
                "description": (
                    m.get("description")
                    or (
                        f"{m.get('name') or default_name}. "
                        f"Produit de la categorie "
                        f"{cfg['label'].lower()}."
                    )
                ),
                "image_file": name
            })

            sources.append(
                src_row(name, "catalogue", f"{cat}/{p.name}")
            )

        print(
            f"[{cat}] "
            f"catalogue={len(catalogue)}  "
            f"requetes={len(tests)}  "
            f"ecartees={skipped}"
        )

    # Ecriture du catalogue
    fields = [
        "name",
        "category",
        "brand",
        "price",
        "description",
        "image_file"
    ]

    with open(PRODUCTS_CSV, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(f, fieldnames=fields)

        writer.writeheader()
        writer.writerows(products)

    # Ecriture des annotations
    with open(ANNOT_CSV, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=["file", "expected_category"]
        )

        writer.writeheader()
        writer.writerows(annotations)

    # Ecriture des sources
    with open(SOURCES_OUT, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image_file",
                "role",
                "source",
                "source_id",
                "author",
                "url"
            ]
        )

        writer.writeheader()
        writer.writerows(sources)

    # Resume final
    print("\n" + "=" * 45)
    print(f"Total : {len(products)} produits -> data/products.csv")
    print(f"        {len(annotations)} requetes -> evaluation/annotations.csv")
    print(f"        {len(sources)} sources -> data/image_sources.csv")
    print("=" * 45)

    print(
        "\nEtape suivante : verifier le catalogue "
        "avant le chargement dans MongoDB."
    )


if __name__ == "__main__":
    main()
