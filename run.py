"""Punto de entrada de la aplicación Flask."""

from app.infrastructure.config.settings import settings
from app.interfaces.web.app_factory import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host=settings.flask_host, port=settings.flask_port, debug=settings.flask_debug)
