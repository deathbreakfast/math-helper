"""Consistency/streak achievement definitions - now handled by milestone achievements."""

from typing import Any

# This file is kept for backward compatibility but achievements are now in milestone.py
# Old consistency achievements (streak-2, streak-3, etc.) have been replaced with
# week-warrior-{tier} and perfect-streak-{tier} achievements in milestone.py

CONSISTENCY_ACHIEVEMENTS: dict[str, dict[str, Any]] = {}
