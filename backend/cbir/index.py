import numpy as np
 
from db.repository import load_vectors
 
_docs = None
_matrix = None
_texts = None
 
 
def get_index():
    """Charge les vecteurs depuis Mongo UNE seule fois (au premier appel)."""
    global _docs, _matrix, _texts
    if _matrix is None:
        _docs, _matrix = load_vectors()
        _texts = [f"{d['name']} {d['brand']} {d['category']}".lower() for d in _docs]
    return _docs, _matrix
 
 
def text_mask(text):
    """Masque booleen : True pour les produits dont nom, marque ou categorie contient `text`."""
    get_index()
    t = text.strip().lower()
    return np.array([t in s for s in _texts], dtype=bool)