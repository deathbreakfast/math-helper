"""Concept-related API routes (concept unlock requirements, etc.)."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..config.concept_unlock_requirements import CONCEPT_UNLOCK_REQUIREMENTS
from ..services.achievement_service import AchievementService
from ..services.level_config_service import LevelConfigService


concepts_bp = Blueprint("concepts", __name__)


@concepts_bp.get("/concepts/requirements")
def get_concept_requirements():
    """Get unlock requirements for multiple concepts in one request.

    Query parameters:
    - concept_ids: comma-separated concept IDs
    - user_id: optional user id (to include completion status)

    Returns:
      { "requirements": { "<concept_id>": [ {achievement_code, quantity, metadata_filter, user_count?, completed?}, ... ] } }
    """
    concept_ids_param = request.args.get("concept_ids", "")
    user_id = request.args.get("user_id", type=int)

    if not concept_ids_param:
        return jsonify({"error": "concept_ids parameter is required (comma-separated list)"}), 400

    concept_ids = [c.strip() for c in concept_ids_param.split(",") if c.strip()]
    if not concept_ids:
        return jsonify({"error": "No valid concept_ids provided"}), 400

    requirements_by_concept: dict[str, list[dict]] = {}

    for concept_id in concept_ids:
        reqs: list[dict] = []

        # Prefer explicit concept unlock requirements (supports both descriptive and legacy ids).
        if concept_id in CONCEPT_UNLOCK_REQUIREMENTS:
            reqs = list(CONCEPT_UNLOCK_REQUIREMENTS.get(concept_id, []))
        # Fallback: legacy concepts use level progression configs as their unlock source (1:1)
        elif concept_id.startswith("c_concept_"):
            try:
                level_num = int(concept_id.split("_")[-1])
            except ValueError:
                level_num = None

            if level_num is not None:
                reqs = list(LevelConfigService.get_level_progression_config(level_num) or [])
        else:
            reqs = []

        # Enrich with counts if user_id provided
        if user_id:
            enriched: list[dict] = []
            for req in reqs:
                achievement_code = req.get("achievement_code", "")
                quantity = req.get("quantity", 1)
                metadata_filter = req.get("metadata_filter")

                count = AchievementService.count_achievements_by_code_with_filters(
                    user_id=user_id,
                    achievement_code=achievement_code,
                    metadata_filter=metadata_filter,
                )

                copied = req.copy()
                copied["user_count"] = count
                copied["completed"] = count >= quantity
                enriched.append(copied)

            reqs = enriched

        requirements_by_concept[concept_id] = reqs

    return jsonify({"requirements": requirements_by_concept})



