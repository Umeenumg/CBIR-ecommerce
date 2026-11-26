"""Aide au choix du seuil de similarite.

Idee : on compare le score top-1 de deux groupes de requetes
  - PERTINENTES : evaluation/test_images (annotations.csv), objets presents dans le catalogue
  - HORS CATALOGUE : evaluation/hors_catalogue/*.jpg, objets ABSENTS du catalogue
Un bon seuil garde presque toutes les requetes pertinentes ET rejette presque toutes les autres.

Usage :  python evaluation/calibrate_threshold.py"""
import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "evaluation"))

from cbir.feature_extractor import extract_batch
from cbir.index import get_index
from cbir.preprocess import load_image
from cbir.similarity import search
from metrics import best_threshold, threshold_table

TEST_DIR = ROOT / "evaluation" / "test_images"
OUT_DIR = ROOT / "evaluation" / "hors_catalogue"


def top1_score(path, matrix):
    q = extract_batch([load_image(path)])[0]
    hits = search(q, matrix, k=1, threshold=-1.0)
    return hits[0][1]


def describe(name, scores):
    med = statistics.median(scores)
    print(f"{name:<18} n={len(scores):<3} min={min(scores):.3f}  "
          f"mediane={med:.3f}  max={max(scores):.3f}")


def main():
    _, matrix = get_index()
    with open(ROOT / "evaluation" / "annotations.csv", newline="", encoding="utf-8") as f:
        relevant_files = [TEST_DIR / r["file"] for r in csv.DictReader(f)]
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    irrelevant_files = sorted(p for p in OUT_DIR.glob("*") if p.suffix.lower() in exts)
    if not relevant_files or not irrelevant_files:
        sys.exit("Il faut des requetes pertinentes (annotations.csv) ET des images dans "
                 "evaluation/hors_catalogue/ "
                 "(10 a 15 objets absents du catalogue : banane, velo, mug, plante, voiture...).")

    relevant = [top1_score(p, matrix) for p in relevant_files]
    irrelevant = [top1_score(p, matrix) for p in irrelevant_files]
    describe("pertinentes", relevant)
    describe("hors catalogue", irrelevant)

    thresholds = [0.30 + 0.05 * i for i in range(14)]          # 0.30 ... 0.95
    rows = threshold_table(relevant, irrelevant, thresholds)
    print(f"\n{'seuil':>6}  {'pertinentes gardees':>20}  "
          f"{'hors catalogue rejetees':>24}  {'moyenne':>8}")
    for r in rows:
        print(f"{r['threshold']:>6.2f}  {r['relevant_kept']:>19.0%}  "
              f"{r['irrelevant_rejected']:>23.0%}  {r['balanced']:>8.2f}")
    best = best_threshold(rows)
    print(f"\nSeuil suggere : {best}  -> mets SIMILARITY_THRESHOLD={best} dans backend/.env")
    print("(puis redemarre le serveur)")
    print("A toi de decider : ce choix et ce compromis doivent etre justifies dans le rapport.")


if __name__ == "__main__":
    main()
