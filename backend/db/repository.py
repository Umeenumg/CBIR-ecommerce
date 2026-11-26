import numpy as np
from db.mongo import products
import re
from bson import ObjectId
from bson.errors import InvalidId


# Exclude features when retrieving product information
NO_FEATURES = {"features": 0}


def load_vectors():
    """Renvoie (docs, M) : docs = liste de dicts, M = matrice (N, 1280)."""

    docs, vectors = [], []

    cursor = products().find({"features": {"$exists": True}})

    for d in cursor:
        docs.append({"id": str(d["_id"]), "name": d["name"], "category": d["category"],
             "brand": d.get("brand", "")})

        vectors.append(
            np.frombuffer(d["features"], dtype="float32")
        )

    if not vectors:
        return docs, np.zeros((0, 1280), dtype="float32")

    return docs, np.stack(vectors)


def serialize(doc, score=None):
    """Document Mongo -> dict JSON (ObjectId converti en texte)."""

    out = {
        "id": str(doc["_id"]),
        "name": doc.get("name"),
        "category": doc.get("category"),
        "brand": doc.get("brand"),
        "price": doc.get("price"),
        "description": doc.get("description"),
        "image_url": f"/images/{doc.get('category')}/{doc.get('image_path')}",
    }

    if score is not None:
        out["score"] = round(float(score), 3)

    return out


def get_product(product_id):
    try:
        oid = ObjectId(product_id)
    except (InvalidId, TypeError):
        return None

    doc = products().find_one({"_id": oid}, NO_FEATURES)

    return serialize(doc) if doc else None


def random_products(n=12):
    docs = products().aggregate([
        {"$sample": {"size": n}},
        {"$project": NO_FEATURES}
    ])

    return [serialize(d) for d in docs]


def list_products(category=None, q=None, limit=50):
    query = {}

    if category:
        query["category"] = category

    if q:
        rx = {"$regex": re.escape(q), "$options": "i"}
        query["$or"] = [
            {"name": rx},
            {"brand": rx},
            {"category": rx}
        ]

    return [
        serialize(d)
        for d in products().find(query, NO_FEATURES).limit(limit)
    ]


def get_products_by_ids(ids):
    """Renvoie les documents dans le MEME ordre que `ids`."""

    oids = [ObjectId(i) for i in ids]

    found = {
        str(d["_id"]): d
        for d in products().find(
            {"_id": {"$in": oids}},
            NO_FEATURES
        )
    }

    return [found[i] for i in ids if i in found]