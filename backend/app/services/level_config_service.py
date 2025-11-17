"""Level configuration service for managing level definitions, achievements, and progression."""

from __future__ import annotations

from typing import Any

from ..config.levels_config import ACHIEVEMENTS_CONFIG, LEVELS_CONFIG, LEVEL_PROGRESSION_CONFIG
from ..database import log_query, transaction
from ..models import LevelProblemConfig, LevelProgression, db
from .practice_service import PracticeService


class LevelConfigService:
    """Service for managing level configurations."""

    @staticmethod
    def get_level_config(level: int) -> dict[str, Any] | None:
        """Get configuration for a specific level."""
        return LEVELS_CONFIG.get(level)

    @staticmethod
    def get_all_level_configs() -> dict[int, dict[str, Any]]:
        """Get all level configurations."""
        return LEVELS_CONFIG.copy()

    @staticmethod
    def get_achievement_config(achievement_code: str) -> dict[str, Any] | None:
        """Get configuration for a specific achievement."""
        return ACHIEVEMENTS_CONFIG.get(achievement_code)

    @staticmethod
    def get_all_achievement_configs() -> dict[str, dict[str, Any]]:
        """Get all achievement configurations."""
        return ACHIEVEMENTS_CONFIG.copy()

    @staticmethod
    def get_level_progression_config(level: int) -> list[dict[str, Any]]:
        """Get progression requirements for a specific level."""
        return LEVEL_PROGRESSION_CONFIG.get(level, [])

    @staticmethod
    def get_all_progression_configs() -> dict[int, list[dict[str, Any]]]:
        """Get all level progression configurations."""
        return LEVEL_PROGRESSION_CONFIG.copy()

    @staticmethod
    @log_query
    def sync_level_configs_to_database() -> None:
        """Sync level configurations from config file to database."""
        for level, config in LEVELS_CONFIG.items():
            operation = config["operation"]
            operand1_min = config["operand1_range"]["min"]
            operand1_max = config["operand1_range"]["max"]
            operand2_min = config["operand2_range"]["min"]
            operand2_max = config["operand2_range"]["max"]
            
            layout_types = [config["layout_type"]]
            if config.get("partial_products_mode"):
                layout_types.append("partialProducts")
            
            answer_formats = [config["answer_format"]]
            
            PracticeService.create_level_problem_config(
                level=level,
                operation=operation,
                min_operand1=operand1_min,
                max_operand1=operand1_max,
                min_operand2=operand2_min,
                max_operand2=operand2_max,
                layout_types=layout_types,
                answer_formats=answer_formats,
                is_available=True,
            )

    @staticmethod
    @log_query
    def sync_progression_configs_to_database() -> None:
        """Sync progression configurations from config file to database."""
        for level, requirements in LEVEL_PROGRESSION_CONFIG.items():
            for req in requirements:
                achievement_code = req["achievement_code"]
                order = req.get("order", 1)
                
                # Check if already exists
                existing = LevelProgression.query.filter_by(
                    target_level=level,
                    required_achievement_code=achievement_code
                ).first()
                
                if not existing:
                    with transaction():
                        progression = LevelProgression(
                            target_level=level,
                            required_achievement_code=achievement_code,
                            order=order,
                        )
                        db.session.add(progression)
                        db.session.flush()

