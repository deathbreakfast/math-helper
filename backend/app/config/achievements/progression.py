"""Progression achievement definitions - replaced by generic {operation}-basics-{tier} achievements."""

# This file is kept for backward compatibility but achievements have been replaced with
# generic {operation}-basics-{tier} achievements in accuracy.py
# Old progression achievements (level-2-mastery, mixed-addition, etc.) should be replaced
# with quantity-based requirements using generic achievement codes

from typing import Any

PROGRESSION_ACHIEVEMENTS: dict[str, dict[str, Any]] = {}
