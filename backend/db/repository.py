import numpy as np
from db.mongo import products
 
 
def load_vectors():
    """Renvoie (docs, M) : docs = liste de dicts, M = matrice (N, 1280)."""
    docs, vectors = [], []
    cursor = products().find({"features": {"$exists": True}})
    for d in cursor:
              docs.append({"id": str(d["_id"]), "name": d["name"], "category": d["category"]})
              vectors.append(np.frombuffer(d["features"], dtype="float32"))
              if not vectors:
                  return docs, np.zeros((0, 1280), dtype="float32")
              return docs, np.stack(vectors)