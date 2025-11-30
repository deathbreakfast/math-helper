"""Test configuration module."""

from .test_achievements import get_new_test_achievements, NEW_TEST_TIER_ACHIEVEMENTS
from .test_definitions import (
    get_all_test_definitions,
    get_test_definition,
    get_test_definitions_by_level,
    NEW_TEST_DEFINITIONS,
)

__all__ = [
    "NEW_TEST_DEFINITIONS",
    "NEW_TEST_TIER_ACHIEVEMENTS",
    "get_test_definition",
    "get_all_test_definitions",
    "get_test_definitions_by_level",
    "get_new_test_achievements",
]

