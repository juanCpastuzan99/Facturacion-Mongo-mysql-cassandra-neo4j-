from flask import Flask, render_template

from ...infrastructure.config.settings import settings
from .container import Container
from .routes.invoice_routes import invoice_bp
from .routes.person_routes import person_bp
from .routes.product_routes import product_bp
from .routes.recommendation_routes import recommendation_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = settings.flask_secret

    Container.instance()

    app.register_blueprint(person_bp, url_prefix="/persons")
    app.register_blueprint(product_bp, url_prefix="/products")
    app.register_blueprint(invoice_bp, url_prefix="/invoices")
    app.register_blueprint(recommendation_bp, url_prefix="/recommendations")

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, message="Página no encontrada"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500, message=str(e)), 500

    return app
