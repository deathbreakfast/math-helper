"""API routes package - registers all route blueprints."""

from flask import Blueprint

from .achievements import achievements_bp
from .common import common_bp
from .levels import levels_bp
from .practice import practice_bp
from .tests import tests_bp
from .users import users_bp

# Create main API blueprint that combines all route blueprints
api_bp = Blueprint("api", __name__)

# Register all sub-blueprints with the main API blueprint
api_bp.register_blueprint(common_bp)
api_bp.register_blueprint(users_bp)
api_bp.register_blueprint(practice_bp)
api_bp.register_blueprint(tests_bp)
api_bp.register_blueprint(achievements_bp)
api_bp.register_blueprint(levels_bp)

__all__ = ["api_bp"]




