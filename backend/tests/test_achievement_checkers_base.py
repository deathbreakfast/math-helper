"""Tests for base achievement checker interface."""

import pytest
from abc import ABC

from app.models import User, Achievement
from app.services.achievements.achievement_checkers.base_checker import AchievementChecker


class TestAchievementCheckerBase:
    """Test the abstract base class for achievement checkers."""
    
    def test_base_checker_is_abstract(self, app):
        """Test that AchievementChecker is an abstract class."""
        with app.app_context():
            # Should not be able to instantiate directly
            with pytest.raises(TypeError):
                AchievementChecker()
    
    def test_base_checker_has_check_method(self, app):
        """Test that AchievementChecker defines check method."""
        with app.app_context():
            # Check that check method exists (even if abstract)
            assert hasattr(AchievementChecker, 'check')
            assert callable(getattr(AchievementChecker, 'check', None))
    
    def test_concrete_checker_must_implement_check(self, app):
        """Test that concrete checkers must implement check method."""
        with app.app_context():
            # Create a concrete checker without implementing check
            class IncompleteChecker(AchievementChecker):
                pass
            
            # Should raise TypeError when trying to instantiate
            with pytest.raises(TypeError):
                IncompleteChecker()
    
    def test_concrete_checker_can_be_instantiated(self, app, test_user):
        """Test that a properly implemented checker can be instantiated."""
        with app.app_context():
            # Create a concrete checker with check method
            class TestChecker(AchievementChecker):
                def check(self, user: User, metrics: dict = None, session_id: int = None) -> list[Achievement]:
                    return []
            
            checker = TestChecker()
            assert checker is not None
            assert isinstance(checker, AchievementChecker)
    
    def test_concrete_checker_returns_achievements(self, app, test_user):
        """Test that a concrete checker's check method returns a list."""
        with app.app_context():
            class TestChecker(AchievementChecker):
                def check(self, user: User, metrics: dict = None, session_id: int = None) -> list[Achievement]:
                    return []
            
            checker = TestChecker()
            result = checker.check(test_user)
            assert isinstance(result, list)






