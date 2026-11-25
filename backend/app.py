from flask import Flask, jsonify
from flask_cors import CORS
 
import config
from errors import register_handlers
 
 
def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")
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
 
 
if __name__ == "__main__":
    create_app().run(debug=True, port=5000, use_reloader=False)