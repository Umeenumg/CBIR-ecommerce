
"""BONUS : comparaison MobileNetV2 / ResNet50 (meme catalogue, memes requetes, SANS Mongo).
Usage depuis la racine :
    python evaluation/compare_models.py

Lit :
    data/products.csv
    data/image_sources.csv
    data/raw/
    evaluation/annotations.csv
    evaluation/test_images/
"""

import csv
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "evaluation"))
from metrics import evaluate

RAW_DIR = ROOT / "data" / "raw"
TEST_DIR = ROOT / "evaluation" / "test_images"

KS = (5, 10)



def load_image_mapping(products):
    """Map image_file -> chemin de l'image originale dans data/raw/."""
    mapping = {}

    with open(
        ROOT / "data" / "image_sources.csv",
        newline="",
        encoding="utf-8"
    ) as f:
        for row in csv.DictReader(f):
            if row["role"] == "catalogue":
                image_file = row["image_file"]

                product = next(
                    (p for p in products if p["image_file"] == image_file),
                    None
                )

                if product is None:
                    continue

                category = product["category"]
                source_id = row["source_id"]

                mapping[image_file] = (
                    RAW_DIR / category / f"fashion_prod_{source_id}.jpg"
                )

    return mapping



def build(name):
    if name == "MobileNetV2":
        from tensorflow.keras.applications import MobileNetV2 as Net
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as prep
    else:
        from tensorflow.keras.applications import ResNet50 as Net
        from tensorflow.keras.applications.resnet50 import preprocess_input as prep

    model = Net(
        weights="imagenet",
        include_top=False,
        pooling="avg",
        input_shape=(224, 224, 3)
    )

    return model, prep


def vectors(model, prep, paths, batch=32):
    out = []

    for i in range(0, len(paths), batch):
        arrays = [
            np.asarray(
                Image.open(p).convert("RGB").resize((224, 224)),
                dtype="float32"
            )
            for p in paths[i:i + batch]
        ]

        feats = model.predict(prep(np.stack(arrays)), verbose=0)

        norms = np.linalg.norm(feats, axis=1, keepdims=True)
        feats = feats / np.maximum(norms, 1e-12)

        out.append(feats)

    return np.vstack(out).astype("float32")


def main():
    with open(
        ROOT / "data" / "products.csv",
        newline="",
        encoding="utf-8"
    ) as f:
        products = list(csv.DictReader(f))

    with open(
        ROOT / "evaluation" / "annotations.csv",
        newline="",
        encoding="utf-8"
    ) as f:
        rows = list(csv.DictReader(f))

    image_mapping = load_image_mapping(products)

    # Images du catalogue
    cat_paths = []
    categories = []

    for product in products:
        image_file = product["image_file"]

        if image_file not in image_mapping:
            raise ValueError(
                f"Image absente de image_sources.csv : {image_file}"
            )

        path = image_mapping[image_file]

        if not path.is_file():
            raise FileNotFoundError(f"Image introuvable : {path}")

        cat_paths.append(path)
        categories.append(product["category"])

    # Images de test
    query_paths = {
        row["file"]: TEST_DIR / row["file"]
        for row in rows
    }

    for name, path in query_paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Image de test introuvable : {path}")

    names = list(query_paths)

    print(f"Catalogue : {len(cat_paths)} images")
    print(f"Requetes  : {len(names)} images")
    print()

    print(
        f"{'modele':<13}{'dim':>5}  "
        f"{'top1':>5} {'P@5':>5} {'P@10':>5}   {'ms/image':>9}"
    )

    for name in ("MobileNetV2", "ResNet50"):
        model, prep = build(name)

        t0 = time.perf_counter()
        M = vectors(model, prep, cat_paths)
        ms_per_image = (
            1000 * (time.perf_counter() - t0) / len(cat_paths)
        )

        Q = dict(
            zip(
                names,
                vectors(model, prep, [query_paths[n] for n in names])
            )
        )

        def retrieve(filename):
            scores = M @ Q[filename]
            order = np.argsort(-scores)[:max(KS)]

            return [
                (categories[i], float(scores[i]))
                for i in order
            ]

        g = evaluate(rows, retrieve, KS)["global"]

        print(
            f"{name:<13}{M.shape[1]:>5}  "
            f"{g['top1']:>5.2f} {g[5]:>5.2f} {g[10]:>5.2f}"
            f"   {ms_per_image:>9.0f}"
        )


if __name__ == "__main__":
    main()
