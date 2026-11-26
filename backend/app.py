from flask import Flask, jsonify
from flask_cors import CORS
 
import config
from errors import register_handlers
import csv
from pathlib import Path
from flask import send_file, abort
from functools import lru_cache
 
def create_app():
    app = Flask(__name__)
    @lru_cache(maxsize=1)
    def load_image_mapping():
        csv_path = config.BASE_DIR.parent / "data" / "image_sources.csv"

        with open(csv_path, newline="", encoding="utf-8") as f:
            return {
                row["image_file"]: row["source_id"]
                for row in csv.DictReader(f)
                if row["role"] == "catalogue"
            }

    @app.get("/images/<category>/<image_file>")
    def serve_image(category, image_file):
        source_id = load_image_mapping().get(image_file)

        if source_id is None:
            abort(404)

        image_path = (
            config.IMAGES_DIR / category /
            f"fashion_prod_{source_id}.jpg"
        ).resolve()

        if not image_path.is_relative_to(config.IMAGES_DIR.resolve()):
            abort(404)

        if not image_path.is_file():
            abort(404)

        return send_file(image_path)
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
    CORS(app)
 
    from routes.products import bp as products_bp
    from routes.search import bp as search_bp
 
    app.register_blueprint(products_bp)
    app.register_blueprint(search_bp)
    register_handlers(app)
 
    @app.get("/api/health")
    def health():
        return jsonify(status="ok")
 
    return app
 
def warm_up():
    """Optionnel : charge matrice + modele au demarrage (la 1re recherche n'est plus lente)."""
    from cbir.feature_extractor import get_model
    from cbir.index import get_index
 
    get_index()
    get_model()
 
 
if __name__ == "__main__":
    app = create_app()
    warm_up()
    app.run(debug=True, port=5000, use_reloader=False)