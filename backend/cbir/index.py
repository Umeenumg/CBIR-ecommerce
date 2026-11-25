
from db.repository import load_vectors
_docs = None
_matrix = None
def get_index():
    """Charge les vecteurs depuis Mongo UNE seule fois (au premier appel)."""
    global _docs, _matrix
    if _matrix is None:
        _docs, _matrix = load_vectors()
    return _docs, _matrix