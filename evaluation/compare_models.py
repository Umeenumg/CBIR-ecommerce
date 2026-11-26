"""BONUS : comparaison MobileNetV2 / ResNet50 (meme catalogue, memes requetes, SANS Mongo).
Usage (depuis la racine) :  python evaluation/compare_models.py
Lit : data/products.csv, backend/static/images/, evaluation/annotations.csv,
      evaluation/test_images/"""
import csv
import sys
import time
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evaluation"))
from metrics import evaluate
IMAGES = ROOT / "backend" / "static" / "images"
TEST_DIR = ROOT / "evaluation" / "test_images"
KS = (5, 10)
def build(name):
    if name == "MobileNetV2":
        from tensorflow.keras.applications import MobileNetV2 as Net
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as prep
    else:
        from tensorflow.keras.applications import ResNet50 as Net
        from tensorflow.keras.applications.resnet50 import preprocess_input as prep
    model = Net(weights="imagenet", include_top=False, pooling="avg", input_shape=(224, 224, 3))
    return model, prep
def vectors(model, prep, paths, batch=32):
    out = []
    for i in range(0, len(paths), batch):
        arrays = [np.asarray(Image.open(p).convert("RGB").resize((224, 224)), dtype="float32")
                  for p in paths[i:i + batch]]
        feats = model.predict(prep(np.stack(arrays)), verbose=0)
        out.append(feats / np.linalg.norm(feats, axis=1, keepdims=True))
    return np.vstack(out).astype("float32")
def main():
    with open(ROOT / "data" / "products.csv", newline="", encoding="utf-8") as f:
        products = list(csv.DictReader(f))
    with open(ROOT / "evaluation" / "annotations.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cat_paths = [IMAGES / p["image_file"] for p in products]
    categories = [p["category"] for p in products]
    query_paths = {r["file"]: TEST_DIR / r["file"] for r in rows}
    names = list(query_paths)
    print(f"{'modele':<13}{'dim':>5}  {'top1':>5} {'P@5':>5} {'P@10':>5}   {'ms/image':>9}")
    for name in ("MobileNetV2", "ResNet50"):
        model, prep = build(name)
        t0 = time.perf_counter()
        M = vectors(model, prep, cat_paths)
        ms_per_image = 1000 * (time.perf_counter() - t0) / len(cat_paths)
        Q = dict(zip(names, vectors(model, prep, [query_paths[n] for n in names])))
 
        def retrieve(filename):
            scores = M @ Q[filename]
            order = np.argsort(-scores)[:max(KS)]
            return [(categories[i], float(scores[i])) for i in order]
 
        g = evaluate(rows, retrieve, KS)["global"]
        print(f"{name:<13}{M.shape[1]:>5}  {g['top1']:>5.2f} {g[5]:>5.2f} {g[10]:>5.2f}"
              f"   {ms_per_image:>9.0f}")
 
 
if __name__ == "__main__":
    main()