"""Level-related API routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..services.level_config_service import LevelConfigService

levels_bp = Blueprint("levels", __name__)

def _translate_test_type_metadata_filter(metadata_filter: object) -> object:
    """Translate legacy metadata_filter.test_type -> metadata_filter.concept_id.

    The app no longer uses test types. Some legacy level progression configs still reference
    test_type; convert them so the frontend can render concept-aware requirements and the
    backend can count achievements using concept_id metadata filters.
    """
    if not isinstance(metadata_filter, dict):
        return metadata_filter

    test_type = metadata_filter.get("test_type")
    if not test_type:
        return metadata_filter

    from ..config.legacy_test_type_to_level import LEGACY_TEST_TYPE_TO_LEVEL

    mapped_level = LEGACY_TEST_TYPE_TO_LEVEL.get(str(test_type))
    if mapped_level is None:
        # If unknown, just drop the test_type to avoid leaking legacy strings to the UI.
        copied = {**metadata_filter}
        copied.pop("test_type", None)
        return copied

    copied = {**metadata_filter, "concept_id": f"c_concept_{mapped_level:03d}"}
    copied.pop("test_type", None)
    return copied


@levels_bp.get("/levels")
def list_levels():
    """Get all level configurations."""
    levels = LevelConfigService.get_all_level_configs()
    return jsonify({"levels": levels})


@levels_bp.get("/levels/<int:level>")
def get_level(level: int):
    """Get configuration for a specific level."""
    config = LevelConfigService.get_level_config(level)
    if not config:
        return jsonify({"error": f"Level {level} not found"}), 404
    return jsonify({"level": level, "config": config})


@levels_bp.get("/levels/<int:level>/requirements")
def get_level_requirements(level: int):
    """Get achievement requirements for a specific level."""
    requirements = LevelConfigService.get_level_progression_config(level)
    # Normalize any legacy metadata filters before returning
    translated = []
    for req in requirements:
        copied = req.copy()
        copied["metadata_filter"] = _translate_test_type_metadata_filter(copied.get("metadata_filter"))
        translated.append(copied)
    requirements = translated
    return jsonify({"level": level, "requirements": requirements})


@levels_bp.get("/levels/requirements")
def get_batch_level_requirements():
    """Get achievement requirements for multiple levels in one request.
    
    Query parameter: levels (comma-separated list of level numbers)
    Optional query parameter: user_id (to include completion status)
    Example: /api/levels/requirements?levels=1,2,3,4,5&user_id=123
    """
    levels_param = request.args.get('levels', '')
    user_id = request.args.get('user_id', type=int)
    
    if not levels_param:
        return jsonify({"error": "levels parameter is required (comma-separated list)"}), 400
    
    try:
        levels = [int(level.strip()) for level in levels_param.split(',') if level.strip()]
    except ValueError:
        return jsonify({"error": "Invalid levels parameter. Must be comma-separated integers"}), 400
    
    if not levels:
        return jsonify({"error": "No valid levels provided"}), 400
    
    # Fetch requirements for all requested levels
    requirements_by_level = {}
    for level in levels:
        requirements = LevelConfigService.get_level_progression_config(level)
        # Normalize any legacy metadata filters before returning / counting
        translated = []
        for req in requirements:
            copied = req.copy()
            copied["metadata_filter"] = _translate_test_type_metadata_filter(copied.get("metadata_filter"))
            translated.append(copied)
        requirements = translated
        
        # If user_id provided, add completion status to each requirement
        if user_id:
            from ..services.user_service import UserService
            from ..models import User
            from .. import db
            
            user = db.session.get(User, user_id)
            if user:
                # Add completion status for each requirement
                enriched_requirements = []
                for req in requirements:
                    achievement_code = req.get("achievement_code", "")
                    quantity = req.get("quantity", 1)
                    metadata_filter = req.get("metadata_filter")
                    
                    # Count achievements with metadata filter support
                    from ..services.achievement_service import AchievementService
                    count = AchievementService.count_achievements_by_code_with_filters(
                        user_id=user.id,
                        achievement_code=achievement_code,
                        metadata_filter=metadata_filter,
                    )
                    
                    enriched_req = req.copy()
                    enriched_req["user_count"] = count
                    enriched_req["completed"] = count >= quantity
                    enriched_requirements.append(enriched_req)
                
                requirements = enriched_requirements
        
        requirements_by_level[level] = requirements
    
    return jsonify({"requirements": requirements_by_level})





