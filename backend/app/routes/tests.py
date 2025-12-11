"""Test-related API routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..services.test_service import TestService
from ..services.user_service import UserService

tests_bp = Blueprint("tests", __name__)


@tests_bp.get("/tests/definitions")
def get_test_definitions():
    """Get all test definitions (legacy + new).
    
    Query parameters:
        user_id: Optional user ID to filter by user level or check unlock status
        include_unlock_status: Optional boolean to include unlock_status for each test (requires user_id)
    """
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    include_unlock_status = request.args.get("include_unlock_status", "false").lower() == "true"
    user_level = None
    
    if user_id:
        user = UserService.get_user(user_id)
        if user:
            user_level = user.level
    
    definitions = TestService.get_all_test_definitions(
        user_level=user_level,
        user_id=user_id if include_unlock_status else None,
        include_unlock_status=include_unlock_status,
    )
    return jsonify({"definitions": definitions})


@tests_bp.get("/tests/attempts")
def get_all_test_attempts():
    """Get all test attempts for a user across all test types.
    
    Query parameters:
        user_id: Required user ID
    """
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    attempts = TestService.get_test_attempts(user_id, test_type=None)
    return jsonify({"attempts": attempts})


@tests_bp.get("/tests/<test_type>/attempts")
def get_test_attempts(test_type: str):
    """Get test attempts for a specific test type.
    
    Query parameters:
        user_id: Required user ID
    """
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    attempts = TestService.get_test_attempts(user_id, test_type=test_type)
    return jsonify({"test_type": test_type, "attempts": attempts})


@tests_bp.get("/tests/attempts/<int:attempt_id>/details")
def get_test_attempt_details(attempt_id: int):
    """Get detailed test attempt with all questions and responses."""
    attempt_detail = TestService.get_test_attempt_detail(attempt_id)
    
    if not attempt_detail:
        return jsonify({"error": "Test attempt not found"}), 404
    
    return jsonify(attempt_detail)



