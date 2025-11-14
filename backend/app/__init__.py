from flask import Flask
from flask_cors import CORS

from .models import db
from .routes import api_bp


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory that wires up the bare-bones API blueprint."""

    app = Flask(__name__)
    app.config.from_mapping(
        APP_NAME="Math Helper",
        SQLALCHEMY_DATABASE_URI="sqlite:///math_helper.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    CORS(app)
    db.init_app(app)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    @app.get("/healthz")
    def health_check():
        return {"status": "ok"}

    return app
