from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__)


@api_bp.get("/hello")
def hello_world():
    """Return a simple greeting to verify the end-to-end flow."""
    return jsonify(message="Hello from Math Helper API")
