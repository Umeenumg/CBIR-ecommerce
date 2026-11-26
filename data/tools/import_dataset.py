"""Importe des produits depuis un dataset Kaggle (ou autre) : un CSV de metadonnees + un dossier d'images.

Le script remplit data/raw/<categorie>/ (comme fetch_pexels.py), puis tu lances build_catalog.py.

Exemple (Fashion Product Images : styles.csv + images/<id>.jpg) :
  python data/tools/import_dataset.py ^
      --csv D:/datasets/fashion/styles.csv --images D:/datasets/fashion/images ^
      --id-col id --category-col articleType --name-col productDisplayName ^
      --categories Watches,Handbags,Perfume,"Casual Shoes",Backpacks,Sunglasses ^
      --per-category 60 --source "Fashion Product Images Dataset (Kaggle)"

Options utiles :
  --top 8           au lieu de --categories : prend les 8 categories les plus frequentes
  --brand-col ...   colonne marque (sinon : marque inventee)
  --price-col ...   colonne prix (sinon : prix inventes)
  --list-categories affiche les categories disponibles (avec leur nombre) puis s'arrete
  --ext .jpg        extension des images (defaut .jpg)

Les lignes mal formees du CSV (virgules en trop) sont ignorees."""
import argparse
import csv
import random
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SOURCES = RAW / "sources.csv"
META = RAW / "metadata.csv"
SOURCE_FIELDS = ["file", "category", "query", "source", "source_id", "author", "url"]
META_FIELDS = ["file", "name", "brand", "price", "description"]


def slug(text):
    """'Casual Shoes' -> 'casual_shoes'"""
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")


def read_rows(csv_path, needed):
    """Lit le CSV en ignorant les lignes mal formees (plus de champs que d'en-tetes, champs manquants)."""
    rows, bad = [], 0
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            if None in row or any(row.get(c) in (None, "") for c in needed):
                bad += 1
                continue
            rows.append(row)
    return rows, bad


def append_rows(path, fields, rows):
    new_file = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new_file:
            w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="fichier de metadonnees (ex. styles.csv)")
    ap.add_argument("--images", required=True, help="dossier des images")
    ap.add_argument("--id-col", required=True, help="colonne identifiant (= nom du fichier image)")
    ap.add_argument("--category-col", required=True, help="colonne categorie")
    ap.add_argument("--name-col", help="colonne nom du produit")
    ap.add_argument("--brand-col")
    ap.add_argument("--price-col")
    ap.add_argument("--categories", help="liste separee par des virgules (valeurs exactes de la colonne)")
    ap.add_argument("--top", type=int, default=8, help="si --categories absent : N categories les plus frequentes")
    ap.add_argument("--per-category", type=int, default=60)
    ap.add_argument("--ext", default=".jpg")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--source", default="Dataset", help="nom du dataset (pour les credits / le rapport)")
    ap.add_argument("--list-categories", action="store_true")
    args = ap.parse_args()

    needed = [args.id_col, args.category_col]
    rows, bad = read_rows(args.csv, needed)
    print(f"{len(rows)} lignes lues ({bad} ignorees : mal formees ou incompletes)")
    counts = Counter(r[args.category_col].strip() for r in rows)

    if args.list_categories:
        for cat, n in counts.most_common(40):
            print(f"{n:>7}  {cat}")
        return

    if args.categories:
        wanted = [c.strip() for c in args.categories.split(",") if c.strip()]
        unknown = [c for c in wanted if c not in counts]
        if unknown:
            sys.exit(f"Categories inconnues : {unknown}. Utilise --list-categories pour voir les valeurs exactes.")
    else:
        wanted = [c for c, _ in counts.most_common(args.top)]
    print("Categories retenues :", wanted)

    rng = random.Random(args.seed)
    images_dir = Path(args.images)
    RAW.mkdir(parents=True, exist_ok=True)
    src_rows, meta_rows = [], []

    for cat in wanted:
        key = slug(cat)
        folder = RAW / key
        folder.mkdir(exist_ok=True)
        candidates = [r for r in rows if r[args.category_col].strip() == cat]
        rng.shuffle(candidates)
        done = len(list(folder.glob("*.jpg")))
        for r in candidates:
            if done >= args.per_category:
                break
            src = images_dir / f"{r[args.id_col].strip()}{args.ext}"
            if not src.exists():
                continue
            dest = folder / f"{slug(args.source)[:12]}_{r[args.id_col].strip()}.jpg"
            if dest.exists():
                continue
            shutil.copy(src, dest)
            done += 1
            rel = f"{key}/{dest.name}"
            src_rows.append({"file": rel, "category": key, "query": "", "source": args.source,
                             "source_id": r[args.id_col].strip(), "author": "", "url": ""})
            meta_rows.append({
                "file": rel,
                "name": (r.get(args.name_col) or "").strip() if args.name_col else "",
                "brand": (r.get(args.brand_col) or "").strip() if args.brand_col else "",
                "price": (r.get(args.price_col) or "").strip() if args.price_col else "",
                "description": "",
            })
        print(f"[{key}] -> {done} images")

    append_rows(SOURCES, SOURCE_FIELDS, src_rows)
    append_rows(META, META_FIELDS, meta_rows)
    print("Termine. Etape suivante : TRIE data/raw/<categorie>/ puis lance build_catalog.py")


if __name__ == "__main__":
    main()
