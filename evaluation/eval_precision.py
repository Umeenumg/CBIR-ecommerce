"""Evaluation Precision@K sur les images de requete.
 
Usage (depuis la racine du projet, Mongo lance, vecteurs calcules) :
    python evaluation/eval_precision.py
 
Entrees : evaluation/annotations.csv (file, expected_category) + evaluation/test_images/
Sorties : evaluation/results/results.csv et evaluation/results/failures.csv"""
import csv
import sys
import time
from pathlib import Path
 
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "evaluation"))
 
from cbir.feature_extractor import extract_batch
from cbir.index import get_index
from cbir.preprocess import load_image
from cbir.similarity import search
from metrics import evaluate
 
TEST_DIR = ROOT / "evaluation" / "test_images"
OUT_DIR = ROOT / "evaluation" / "results"
KS = (5, 10)
def main():
    docs, matrix = get_index()
    if matrix.shape[0] == 0:
        sys.exit("Catalogue vide : lance load_catalog puis compute_features.")
    with open(ROOT / "evaluation" / "annotations.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("annotations.csv est vide.")
    extract_batch([load_image(TEST_DIR / rows[0]["file"])])      # echauffement (1er appel lent)
    timings = {"extraction": [], "recherche": []}
    def retrieve(filename):
        img = load_image(TEST_DIR / filename)
        t0 = time.perf_counter()
        q = extract_batch([img])[0]
        t1 = time.perf_counter()
        hits = search(q, matrix, k=max(KS), threshold=-1.0)       # PAS de seuil pour evaluer
        t2 = time.perf_counter()
        timings["extraction"].append(t1 - t0)
        timings["recherche"].append(t2 - t1)
        return [(docs[i]["category"], s) for i, s in hits]
    report = evaluate(rows, retrieve, KS)
    header = f"{'categorie':<14}{'n':>3}   top1   P@5   P@10"
    print(header + "\n" + "-" * len(header))
    lines = []
    for cat, s in report["per_category"].items():
        print(f"{cat:<14}{s['n']:>3}   {s['top1']:.2f}   {s[5]:.2f}   {s[10]:.2f}")
        lines.append({"categorie": cat, "n": s["n"], "top1": round(s["top1"], 3),
                      "P@5": round(s[5], 3), "P@10": round(s[10], 3)})
    g = report["global"]
    print("-" * len(header))
    print(f"{'GLOBAL':<14}{g['n']:>3}   {g['top1']:.2f}   {g[5]:.2f}   {g[10]:.2f}")
    lines.append({"categorie": "GLOBAL", "n": g["n"], "top1": round(g["top1"], 3),
                  "P@5": round(g[5], 3), "P@10": round(g[10], 3)})
    n = len(timings["extraction"])
    print(f"\nTemps moyen : extraction {1000 * sum(timings['extraction']) / n:.0f} ms/image, "
          f"recherche {1000 * sum(timings['recherche']) / n:.2f} ms ({matrix.shape[0]} produits)")
    OUT_DIR.mkdir(exist_ok=True)
    with open(OUT_DIR / "results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["categorie", "n", "top1", "P@5", "P@10"])
        w.writeheader()
        w.writerows(lines)
    with open(OUT_DIR / "failures.csv", "w", newline="", encoding="utf-8") as f:
        fields = ["file", "expected", "top1_category", "top1_score", "top5"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(report["failures"])
    print(f"\n{len(report['failures'])} echec(s) en top-1 -> evaluation/results/failures.csv")
if __name__ == "__main__":
    main() 