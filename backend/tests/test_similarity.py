import numpy as np
 
from cbir.similarity import search
 
 
def unit(v):
    v = np.array(v, dtype="float32")
    return v / np.linalg.norm(v)
 
 
M = np.stack([unit([1, 0, 0]), unit([1, 1, 0]), unit([0, 0, 1])])
 
 
def test_meme_vecteur_score_1_et_en_tete():
    hits = search(unit([1, 0, 0]), M, k=3)
    assert hits[0][0] == 0
    assert abs(hits[0][1] - 1.0) < 1e-6
 
 
def test_tri_decroissant():
    scores = [s for _, s in search(unit([1, 0.2, 0]), M, k=3)]
    assert scores == sorted(scores, reverse=True)
 
 
def test_seuil_elimine_les_faibles():
    assert [i for i, _ in search(unit([1, 0, 0]), M, k=3, threshold=0.9)] == [0]
 
 
def test_catalogue_vide():
    assert search(unit([1, 0, 0]), np.zeros((0, 3), dtype="float32")) == []


def test_mask_exclut_les_produits_non_autorises():
    mask = np.array([False, True, True])
    ids = [i for i, _ in search(unit([1, 0, 0]), M, k=3, mask=mask)]
    assert 0 not in ids and ids[0] == 1
 
 
def test_mask_tout_faux_ne_renvoie_rien():
    assert search(unit([1, 0, 0]), M, k=3, mask=np.array([False, False, False])) == []