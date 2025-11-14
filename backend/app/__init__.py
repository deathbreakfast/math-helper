from flask import Flask
from flask_cors import CORS

from .routes import api_bp


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory that wires up the bare-bones API blueprint."""

    app = Flask(__name__)
    app.config.from_mapping(APP_NAME="Math Helper")

    if test_config:
        app.config.update(test_config)

    CORS(app)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/healthz")
    def health_check():
        return {"status": "ok"}

    return app
