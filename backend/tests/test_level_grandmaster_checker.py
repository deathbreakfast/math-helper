"""Tests for MathGrandmasterChecker."""

import pytest

from app.config.achievements import ACHIEVEMENTS_CONFIG
from app.config.concepts_config import CONCEPTS_CONFIG
from app.models import Achievement
from app.services.achievements.achievement_checkers.math_grandmaster_checker import (
    MathGrandmasterChecker,
)
from app.services.achievements.achievement_utils import create_achievement
from app.services.level_config_service import LevelConfigService
from app.utils.tier_utils import ALL_TIERS


@pytest.fixture
def achievement_configs():
    """Get achievement configs for testing."""
    return LevelConfigService.get_all_achievement_configs()


@pytest.fixture
def math_grandmaster_checker(achievement_configs):
    """Create a MathGrandmasterChecker instance."""
    return MathGrandmasterChecker(achievement_configs)


def _create_math_master_achievement(user_id: int, concept_id: str, tier: str) -> Achievement:
    """Create a Math Master achievement for a specific concept and tier."""
    code = f"math-master-{tier}"
    config = ACHIEVEMENTS_CONFIG.get(code)
    if not config:
        raise ValueError(f"Achievement {code} not found in config")

    return create_achievement(
        user_id=user_id,
        code=code,
        title=config["title"],
        description=config["description"],
        icon=config["icon"],
        category=config["category"],
        metadata={"concept_id": concept_id},
    )


@pytest.mark.parametrize("tier", ALL_TIERS)
def test_math_grandmaster_awards_for_all_concepts_by_tier(
    app,
    test_user,
    math_grandmaster_checker,
    tier,
):
    """Test Math Grandmaster is awarded when all concepts meet a tier."""
    with app.app_context():
        concept_ids = list(CONCEPTS_CONFIG.keys())
        if not concept_ids:
            pytest.skip("No concepts found in config")

        for concept_id in concept_ids:
            _create_math_master_achievement(test_user.id, concept_id, tier)

        result = math_grandmaster_checker.check(test_user, tier=tier)

        assert len(result) == 1, f"Should award math-grandmaster-{tier}"
        assert result[0].code == f"math-grandmaster-{tier}"


def test_math_grandmaster_not_awarded_when_missing_concept(
    app,
    test_user,
    math_grandmaster_checker,
):
    """Test Math Grandmaster is not awarded if any concept is missing."""
    with app.app_context():
        concept_ids = list(CONCEPTS_CONFIG.keys())
        if len(concept_ids) < 2:
            pytest.skip("Need at least 2 concepts for this test")

        missing_concept = concept_ids[-1]
        for concept_id in concept_ids:
            if concept_id != missing_concept:
                _create_math_master_achievement(test_user.id, concept_id, "silver")

        result = math_grandmaster_checker.check(test_user, tier="silver")

        assert len(result) == 0, "Should not award math-grandmaster-silver when one concept is missing"


def test_math_grandmaster_tier_substitution(
    app,
    test_user,
    math_grandmaster_checker,
):
    """Test higher Math Master tiers qualify for lower Math Grandmaster tiers."""
    with app.app_context():
        concept_ids = list(CONCEPTS_CONFIG.keys())
        if len(concept_ids) < 2:
            pytest.skip("Need at least 2 concepts for this test")

        for idx, concept_id in enumerate(concept_ids):
            if idx == 0:
                _create_math_master_achievement(test_user.id, concept_id, "gold")
            elif idx == 1:
                _create_math_master_achievement(test_user.id, concept_id, "platinum")
            else:
                _create_math_master_achievement(test_user.id, concept_id, "silver")

        result = math_grandmaster_checker.check(test_user, tier="silver")

        assert len(result) == 1, "Should award math-grandmaster-silver with higher-tier substitutions"
        assert result[0].code == "math-grandmaster-silver"


def test_math_grandmaster_not_awarded_twice(
    app,
    test_user,
    math_grandmaster_checker,
):
    """Test Math Grandmaster is not awarded twice for the same tier."""
    with app.app_context():
        code = "math-grandmaster-bronze"
        config = ACHIEVEMENTS_CONFIG.get(code)
        if not config:
            pytest.skip("Math Grandmaster bronze config not found")

        create_achievement(
            user_id=test_user.id,
            code=code,
            title=config["title"],
            description=config["description"],
            icon=config["icon"],
            category=config["category"],
        )

        result = math_grandmaster_checker.check(test_user, tier="bronze")

        assert len(result) == 0, "Should not award math-grandmaster-bronze twice"
