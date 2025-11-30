"""Level mastery achievements aggregated from all level ranges."""

from typing import Any

from .levels_5_10 import LEVELS_5_10_MASTERY
from .levels_11_15 import LEVELS_11_15_MASTERY
from .levels_16_20 import LEVELS_16_20_MASTERY
from .levels_21_25 import LEVELS_21_25_MASTERY

# Combine all level mastery achievements
LEVEL_MASTERY_ACHIEVEMENTS: dict[str, dict[str, Any]] = {
    **LEVELS_5_10_MASTERY,
    **LEVELS_11_15_MASTERY,
    **LEVELS_16_20_MASTERY,
    **LEVELS_21_25_MASTERY,
}

