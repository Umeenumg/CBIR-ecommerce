import numpy as np

 
 
def search(query_vec, M, k=12, threshold=0.0):
    """Renvoie [(indice, score), ...] du plus au moins similaire.
    Vecteurs normalises -> cosinus = produit scalaire."""
    if M.shape[0] == 0:
        return []
    scores = M @ query_vec
    order = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in order if scores[i] >= threshold]