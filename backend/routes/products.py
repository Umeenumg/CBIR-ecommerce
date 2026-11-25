from flask import Blueprint, jsonify, request

from db import repository
from errors import api_error
 
bp = Blueprint("products", __name__, url_prefix="/api/products")
 
 
@bp.get("/random")
def random_products():
    try:
        limit = int(request.args.get("limit", 12))
    except ValueError:
        return api_error(400, "Parametre limit invalide.")
    limit = min(max(limit, 1), 50)
    return jsonify(results=repository.random_products(limit))
 
 
@bp.get("")
def list_products():
    results = repository.list_products(
        category=request.args.get("category"), q=request.args.get("q"))
    return jsonify(results=results)
 
 
@bp.get("/<product_id>")
def get_product(product_id):
    product = repository.get_product(product_id)
    if product is None:
        return api_error(404, "Produit introuvable.")
    return jsonify(product)