"""Achievement configuration service.

This service provides access to achievement configurations.
Legacy level-related functionality has been removed.
"""

from __future__ import annotations

from typing import Any

from ..config.achievements import ACHIEVEMENTS_CONFIG


class AchievementConfigService:
    """Service for managing achievement configurations."""

    @staticmethod
    def get_achievement_config(achievement_code: str) -> dict[str, Any] | None:
        """Get configuration for a specific achievement."""
        return ACHIEVEMENTS_CONFIG.get(achievement_code)

    @staticmethod
    def get_all_achievement_configs() -> dict[str, dict[str, Any]]:
        """Get all achievement configurations."""
        return ACHIEVEMENTS_CONFIG.copy()


# Backward compatibility alias
LevelConfigService = AchievementConfigService

