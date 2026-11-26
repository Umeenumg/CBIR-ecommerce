import numpy as np
 
 
def search(query_vec, M, k=12, threshold=0.0, mask=None):
    """Renvoie [(indice, score), ...] du plus au moins similaire.
    Vecteurs normalises -> cosinus = produit scalaire.
 
    mask : tableau booleen optionnel (True = produit autorise). Sert a combiner
           le filtre TEXTE (qui elimine des produits) et le classement VISUEL.
    """
    if M.shape[0] == 0:
        return []
    scores = M @ query_vec
    if mask is not None:
        scores = np.where(mask, scores, -np.inf)       # produits exclus : jamais retenus
    order = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in order
            if np.isfinite(scores[i]) and scores[i] >= threshold]