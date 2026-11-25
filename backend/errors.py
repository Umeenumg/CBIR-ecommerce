from flask import jsonify
def api_error(code, message):
    """Reponse d'erreur JSON uniforme."""
    resp = jsonify(error={"code": code, "message": message})
    resp.status_code = code
    return resp
def register_handlers(app):
    @app.errorhandler(404)
    def not_found(_e):
        return api_error(404, "Ressource introuvable.")
    @app.errorhandler(413)
    def too_large(_e):
        return api_error(413, "Fichier trop volumineux (5 Mo maximum).")
    @app.errorhandler(500)
    def internal(_e):
        return api_error(500, "Erreur interne du serveur.")