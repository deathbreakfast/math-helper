"""Test configuration module."""

from .test_achievements import get_new_test_achievements
from .test_definitions import (
    get_all_test_definitions,
    get_test_definition,
    get_test_definitions_by_level,
    NEW_TEST_DEFINITIONS,
)

__all__ = [
    "NEW_TEST_DEFINITIONS",
    "get_test_definition",
    "get_all_test_definitions",
    "get_test_definitions_by_level",
    "get_new_test_achievements",
]

