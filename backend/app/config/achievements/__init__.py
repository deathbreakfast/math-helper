"""Achievement definitions aggregated from all categories."""

from typing import Any

from .accuracy import ACCURACY_ACHIEVEMENTS
from .consistency import CONSISTENCY_ACHIEVEMENTS
from .milestone import MILESTONE_ACHIEVEMENTS
from .progression import PROGRESSION_ACHIEVEMENTS
from .speed import SPEED_ACHIEVEMENTS

# Combine all achievement categories
# Note: Test achievements have been removed - use existing achievements with metadata instead
# CONSISTENCY_ACHIEVEMENTS and SPEED_ACHIEVEMENTS are now empty - replaced by milestone achievements
ACHIEVEMENTS_CONFIG: dict[str, dict[str, Any]] = {
    **MILESTONE_ACHIEVEMENTS,
    **ACCURACY_ACHIEVEMENTS,
    **PROGRESSION_ACHIEVEMENTS,
    **SPEED_ACHIEVEMENTS,
    **CONSISTENCY_ACHIEVEMENTS,
}

