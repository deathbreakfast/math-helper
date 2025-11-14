from flask import Blueprint, jsonify, request

from .models import User, db

api_bp = Blueprint("api", __name__)


@api_bp.get("/hello")
def hello_world():
    """Return a simple greeting to verify the end-to-end flow."""
    return jsonify(message="Hello from Math Helper API")


@api_bp.post("/users")
def create_user():
    """Persist a new learner with a plain-text 4-digit PIN."""

    payload = request.get_json(silent=True) or {}
    avatar = payload.get("avatar")
    display_name = (payload.get("name") or "").strip()
    pin = (payload.get("pin") or "").strip()

    errors: list[str] = []
    if len(display_name) < 2:
        errors.append("Name must be at least 2 characters long.")
    if not pin.isdigit() or len(pin) != 4:
        errors.append("PIN must be a 4-digit number.")
    if User.query.filter_by(display_name=display_name).first():
        errors.append("Name is already taken.")

    if errors:
        return jsonify({"errors": errors}), 400

    user = User(avatar=avatar, display_name=display_name, pin=pin)
    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            {
                "id": user.id,
                "avatar": user.avatar,
                "name": user.display_name,
                "pin": user.pin,
                "share_url_params": {"user": user.display_name, "pin": user.pin},
            }
        ),
        201,
    )
