"""Telecharge SEULEMENT une partie de "Fashion Product Images Dataset" (Kaggle) :
styles.csv (petit) + les images des categories choisies. Pas les 25 Go !

  pip install kagglehub
  python data/tools/download_fashion_subset.py --list-categories
  python data/tools/download_fashion_subset.py --categories "Watches,Handbags,Casual Shoes" --per-category 60

Sortie : data/downloads/fashion_subset/  (styles_subset.csv + images/<id>.jpg)
Le script affiche ensuite la commande import_dataset.py a lancer."""
import argparse
import csv
import random
import shutil
import sys
from collections import Counter
from pathlib import Path

import kagglehub

HANDLE = "paramaggarwal/fashion-product-images-dataset"
PREFIXES = ["", "fashion-dataset/", "fashion-dataset/fashion-dataset/"]   # structure possible du dataset
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "downloads" / "fashion_subset"
MAX_CONSECUTIVE_FAILS = 25


def fetch(relpath):
    """Telecharge UN fichier du dataset (kagglehub le garde en cache). Renvoie un Path, ou None."""
    try:
        return Path(kagglehub.dataset_download(HANDLE, path=relpath))
    except Exception:  # noqa: BLE001
        return None


def read_rows(csv_path):
    """Lit styles.csv en ignorant les lignes mal formees."""
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if None not in r and r.get("id") and r.get("articleType")]
        return reader.fieldnames, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--categories", help='valeurs exactes de articleType, separees par des virgules')
    ap.add_argument("--per-category", type=int, default=60)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--list-categories", action="store_true")
    args = ap.parse_args()

    # 1. styles.csv : on essaie les emplacements possibles
    styles, prefix = None, None
    for p in PREFIXES:
        styles = fetch(f"{p}styles.csv")
        if styles:
            prefix = p
            break
    if not styles:
        sys.exit("styles.csv introuvable. Verifie le nom du fichier dans l'onglet Data de la page Kaggle, "
                 "et que tu es connecte (kagglehub.login()).")
    fieldnames, rows = read_rows(styles)
    counts = Counter(r["articleType"].strip() for r in rows)
    print(f"styles.csv : {len(rows)} produits, {len(counts)} categories")

    if args.list_categories or not args.categories:
        for cat, n in counts.most_common(40):
            print(f"{n:>7}  {cat}")
        if not args.categories:
            print('\nEnsuite : --categories "Watches,Handbags,..." (noms EXACTS de la liste)')
        return

    wanted = [c.strip() for c in args.categories.split(",") if c.strip()]
    unknown = [c for c in wanted if c not in counts]
    if unknown:
        sys.exit(f"Categories inconnues : {unknown}. Lance --list-categories.")

    # 2. ou sont les images ?
    rng = random.Random(args.seed)
    probe = rng.sample(rows, min(8, len(rows)))
    img_prefix = None
    for p in PREFIXES:
        if any(fetch(f"{p}images/{r['id']}.jpg") for r in probe):
            img_prefix = p
            break
    if img_prefix is None:
        sys.exit("Dossier images introuvable (essaye de regarder l'arborescence dans l'onglet Data de Kaggle).")

    # 3. on telecharge seulement les images choisies
    (OUT / "images").mkdir(parents=True, exist_ok=True)
    kept = []
    for cat in wanted:
        candidates = [r for r in rows if r["articleType"].strip() == cat]
        rng.shuffle(candidates)
        got, fails = 0, 0
        for r in candidates:
            if got >= args.per_category:
                break
            dest = OUT / "images" / f"{r['id']}.jpg"
            if not dest.exists():
                local = fetch(f"{img_prefix}images/{r['id']}.jpg")
                if local is None:
                    fails += 1
                    if fails >= MAX_CONSECUTIVE_FAILS:
                        sys.exit(f"{fails} echecs de suite pour '{cat}' : verifie ta connexion / ton login Kaggle.")
                    continue
                shutil.copy(local, dest)
            fails = 0
            got += 1
            kept.append(r)
            if got % 20 == 0:
                print(f"  [{cat}] {got}/{args.per_category}")
        print(f"[{cat}] -> {got} images")

    csv_out = OUT / "styles_subset.csv"
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(kept)
    cats = ",".join(wanted)
    print(f"\n{len(kept)} produits -> {csv_out}")
    print("\nEtape suivante (depuis la racine du projet) :")
    print(f'python data/tools/import_dataset.py --csv "{csv_out}" --images "{OUT / "images"}" '
          f'--id-col id --category-col articleType --name-col productDisplayName '
          f'--categories "{cats}" --per-category {args.per_category} '
          f'--source "Fashion Product Images Dataset (Kaggle)"')


if __name__ == "__main__":
    main()
