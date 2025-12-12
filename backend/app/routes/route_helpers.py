"""Route helper utilities for common patterns like request parsing, validation, and error handling."""

from __future__ import annotations

from typing import Any, Callable

from flask import jsonify, request

from ..services.user_service import UserService


def get_json_payload() -> dict[str, Any]:
    """Extract and return JSON payload from request.
    
    Returns:
        Dictionary with request payload, or empty dict if no payload
    """
    return request.get_json(silent=True) or {}


def get_user_id_from_payload(payload: dict[str, Any] | None = None) -> int | None:
    """Extract user_id from payload (supports both userId and user_id keys).
    
    Args:
        payload: Optional payload dict (if None, extracts from request)
        
    Returns:
        User ID as integer, or None if not found/invalid
    """
    if payload is None:
        payload = get_json_payload()
    
    user_id = payload.get("userId") or payload.get("user_id")
    if user_id is not None:
        try:
            return int(user_id)
        except (TypeError, ValueError):
            return None
    return None


def get_user_from_payload(
    payload: dict[str, Any] | None = None,
    require_pin: bool = False,
    pin: str | None = None
) -> tuple[Any | None, dict[str, Any] | None]:
    """Get user from payload with optional PIN verification.
    
    Args:
        payload: Optional payload dict (if None, extracts from request)
        require_pin: If True, requires valid PIN verification
        pin: Optional PIN string (if None, extracts from payload)
        
    Returns:
        Tuple of (user object or None, error dict or None)
    """
    if payload is None:
        payload = get_json_payload()
    
    user_id = get_user_id_from_payload(payload)
    user_name = (payload.get("userName") or payload.get("user_name") or "").strip()
    
    # Find user by ID or name
    user = None
    if user_id is not None:
        try:
            user = UserService.get_user(int(user_id))
        except (TypeError, ValueError):
            pass
    
    if user is None and user_name:
        user = UserService.get_user_by_name(user_name)
    
    if user is None:
        return None, {"error": "Learner not found. Create the profile before practicing."}
    
    # PIN verification if required
    if require_pin:
        if pin is None:
            pin = (payload.get("pin") or "").strip()
        
        if not pin.isdigit() or len(pin) != 4:
            return None, {"error": "A 4-digit PIN is required to submit practice."}
        
        if not UserService.verify_pin(user, pin):
            return None, {"error": "PIN verification failed for this learner."}
    
    return user, None


def validate_required_fields(
    payload: dict[str, Any],
    required_fields: list[str],
    field_aliases: dict[str, list[str]] | None = None
) -> tuple[bool, str | None]:
    """Validate that required fields are present in payload.
    
    Args:
        payload: Payload dictionary
        required_fields: List of required field names
        field_aliases: Optional dict mapping field names to lists of aliases
        
    Returns:
        Tuple of (is_valid, error_message or None)
    """
    if field_aliases is None:
        field_aliases = {}
    
    for field in required_fields:
        # Check primary field name
        if field in payload and payload[field] is not None:
            continue
        
        # Check aliases
        aliases = field_aliases.get(field, [])
        found = False
        for alias in aliases:
            if alias in payload and payload[alias] is not None:
                found = True
                break
        
        if not found:
            return False, f"Missing required field: {field}"
    
    return True, None


def create_error_response(error_message: str, status_code: int = 400) -> tuple[Any, int]:
    """Create a standardized error response.
    
    Args:
        error_message: Error message string
        status_code: HTTP status code
        
    Returns:
        Tuple of (jsonify response, status_code)
    """
    return jsonify({"error": error_message}), status_code


def create_success_response(data: dict[str, Any] | list[Any], status_code: int = 200) -> tuple[Any, int]:
    """Create a standardized success response.
    
    Args:
        data: Response data (dict or list)
        status_code: HTTP status code
        
    Returns:
        Tuple of (jsonify response, status_code)
    """
    if isinstance(data, dict):
        return jsonify(data), status_code
    else:
        return jsonify(data), status_code


def handle_service_error(func: Callable) -> Callable:
    """Decorator to handle common service errors and convert to HTTP responses.
    
    Usage:
        @handle_service_error
        def my_route():
            result = SomeService.do_something()
            return create_success_response(result)
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return create_error_response(str(e), 400)
        except KeyError as e:
            return create_error_response(f"Missing required field: {e}", 400)
        except Exception as e:
            return create_error_response(f"Internal server error: {str(e)}", 500)
    wrapper.__name__ = func.__name__
    return wrapper
