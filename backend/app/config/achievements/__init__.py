"""Achievement definitions aggregated from all categories."""

from typing import Any

from .accuracy import ACCURACY_ACHIEVEMENTS
from .consistency import CONSISTENCY_ACHIEVEMENTS
from .milestone import MILESTONE_ACHIEVEMENTS
from .progression import PROGRESSION_ACHIEVEMENTS
from .speed import SPEED_ACHIEVEMENTS
from .test import TEST_ACHIEVEMENTS, _generate_test_tier_achievements
from ..tests.test_achievements import get_new_test_achievements

# Combine all achievement categories
# Note: LEVEL_MASTERY_ACHIEVEMENTS removed - replaced by generic {operation}-basics-{tier} achievements
# CONSISTENCY_ACHIEVEMENTS and SPEED_ACHIEVEMENTS are now empty - replaced by milestone achievements
ACHIEVEMENTS_CONFIG: dict[str, dict[str, Any]] = {
    **MILESTONE_ACHIEVEMENTS,
    **ACCURACY_ACHIEVEMENTS,
    **PROGRESSION_ACHIEVEMENTS,
    **TEST_ACHIEVEMENTS,
    **SPEED_ACHIEVEMENTS,
    **CONSISTENCY_ACHIEVEMENTS,
}

# Add test tier achievements (generated dynamically for legacy tests)
ACHIEVEMENTS_CONFIG.update(_generate_test_tier_achievements())

# Add new test tier achievements (generated dynamically for new tests)
ACHIEVEMENTS_CONFIG.update(get_new_test_achievements())

