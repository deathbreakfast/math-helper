import os
from flask import Flask
from flask_cors import CORS

from .database import init_db
from .models import db
from .routes import api_bp


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory that wires up the API blueprint with database wrapper."""

    app = Flask(__name__)
    app.config.from_mapping(
        APP_NAME="Math Helper",
        SQLALCHEMY_DATABASE_URI="sqlite:///math_helper.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_pre_ping": True,
        },
        # Default TESTING to true until v1.0
        # Can be overridden with TESTING=false environment variable
        TESTING=os.getenv('TESTING', 'true').lower() == 'true',
    )

    if test_config:
        app.config.update(test_config)

    CORS(app)
    db.init_app(app)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Initialize database with foreign key support
    init_db(app)

    @app.get("/healthz")
    def health_check():
        return {"status": "ok"}

    return app
