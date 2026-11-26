from flask import Blueprint, jsonify, request
 
import config
from cbir.feature_extractor import extract_batch
from cbir.index import get_index, text_mask
from cbir.preprocess import load_image_bytes
from cbir.similarity import search
from db import repository
from errors import api_error

 
bp = Blueprint("search", __name__, url_prefix="/api")
 
 
@bp.post("/search")
def search_by_image():
    # 1. Validation COTE SERVEUR
    file = request.files.get("image")
    if file is None or not file.filename:
        return api_error(400, "Aucune image envoyee (champ 'image').")
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in config.ALLOWED_EXTENSIONS:
        return api_error(415, "Format non supporte (jpg, jpeg, png, webp).")
    try:
        img = load_image_bytes(file.read())
    except Exception:
        return api_error(400, "Le fichier n'est pas une image valide.")
 
    # 2. Vecteur de la requete
    query_vec = extract_batch([img])[0]
 
   
 # 3. Comparaison avec le catalogue (matrice chargee une seule fois)
    docs, matrix = get_index()
    if matrix.shape[0] == 0:
        return jsonify(results=[], message="Catalogue vide : calculer d'abord les vecteurs.")
    # Texte facultatif : il FILTRE le catalogue, puis la similarite visuelle CLASSE le reste
    text = request.form.get("q", "").strip()
    mask = None
    if text:
        mask = text_mask(text)
        if not mask.any():
            return jsonify(results=[], message=f"Aucun produit ne correspond au texte '{text}'.")
    hits = search(query_vec, matrix, config.TOP_K, config.SIMILARITY_THRESHOLD, mask)
    if not hits:
        return jsonify(results=[], message="Aucun produit suffisamment similaire trouve.")
 
    # 4. Infos produits, DANS L'ORDRE du classement
    ids = [docs[i]["id"] for i, _ in hits]
    scores = {docs[i]["id"]: s for i, s in hits}
    found = repository.get_products_by_ids(ids)
    results = [repository.serialize(d, scores[str(d["_id"])]) for d in found]
    return jsonify(results=results)