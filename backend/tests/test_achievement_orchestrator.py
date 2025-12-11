"""Comprehensive tests for AchievementOrchestrator.

Tests cover all methods in AchievementOrchestrator to achieve >80% coverage.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app import create_app, db
from app.models import Achievement, PracticeSession, Question, Response, User
from app.services.achievements.achievement_orchestrator import AchievementOrchestrator
from app.services.practice_service import PracticeService


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app(test_config={'TESTING': True})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(display_name="Test User", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def test_question(app):
    """Create a test question."""
    with app.app_context():
        question = Question(
            operation="addition",
            operand1=5,
            operand2=3,
            correct_answer="8",
            prompt="5 + 3",
            required_level=1,
            difficulty="Level 1",
            target_ms=4000,
        )
        db.session.add(question)
        db.session.commit()
        db.session.refresh(question)
        return question


@pytest.fixture
def achievement_configs():
    """Create mock achievement configs."""
    return {
        "first-steps": {
            "title": "First Steps",
            "description": "Answer your first question",
            "icon": "🎯",
            "category": "milestone",
            "requirements": {
                "type": "question_count",
                "quantity": 1
            }
        }
    }


@pytest.fixture
def orchestrator(achievement_configs):
    """Create an AchievementOrchestrator instance."""
    return AchievementOrchestrator(achievement_configs)


class TestAchievementOrchestrator:
    """Test suite for AchievementOrchestrator."""

    def test_init(self, achievement_configs):
        """Test __init__ initializes orchestrator with checkers."""
        orchestrator = AchievementOrchestrator(achievement_configs)
        
        assert orchestrator.achievement_configs == achievement_configs
        assert orchestrator.milestone_checker is not None
        assert orchestrator.level_checker is not None
        assert orchestrator.level_master_checker is not None
        assert orchestrator.level_grandmaster_checker is not None
        assert orchestrator.human_calculator_checker is not None

    def test_ensure_achievements_no_responses(self, app, test_user, orchestrator):
        """Test ensure_achievements with user having no responses."""
        with app.app_context():
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 0,
                    "average_speed_seconds": 0.0,
                    "operation_stats": {}
                }
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    achievements = orchestrator.ensure_achievements(test_user)
                    
                    assert isinstance(achievements, list)
                    assert mock_metrics.called

    def test_ensure_achievements_no_new_activity(self, app, test_user, test_question, orchestrator):
        """Test ensure_achievements skips checking when no new activity."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            # Create response
            response = PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=2000
            )
            response.answered_at = datetime.utcnow() - timedelta(days=2)
            db.session.add(response)
            
            # Create achievement that's newer than response
            achievement = Achievement(
                user_id=test_user.id,
                code="first-steps",
                title="First Steps",
                description="Answer your first question",
                icon="🎯",
                category="milestone",
                earned_at=datetime.utcnow() - timedelta(days=1)  # Newer than response
            )
            db.session.add(achievement)
            db.session.commit()
            
            # Should skip expensive checking
            achievements = orchestrator.ensure_achievements(test_user)
            
            # Should return existing achievements
            assert len(achievements) >= 1
            assert any(a.code == "first-steps" for a in achievements)

    def test_ensure_achievements_with_new_activity(self, app, test_user, test_question, orchestrator):
        """Test ensure_achievements processes when there's new activity."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            # Create response that's newer than any achievement
            response = PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=2000
            )
            response.answered_at = datetime.utcnow()
            db.session.add(response)
            
            # Create old achievement
            achievement = Achievement(
                user_id=test_user.id,
                code="first-steps",
                title="First Steps",
                description="Answer your first question",
                icon="🎯",
                category="milestone",
                earned_at=datetime.utcnow() - timedelta(days=2)  # Older than response
            )
            db.session.add(achievement)
            db.session.commit()
            
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 1,
                    "average_speed_seconds": 2.0,
                    "operation_stats": {},
                    "last_activity_at": datetime.utcnow()
                }
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    achievements = orchestrator.ensure_achievements(test_user)
                    
                    # Should have processed (not skipped)
                    assert mock_metrics.called or mock_check.called

    def test_ensure_achievements_with_metrics(self, app, test_user, orchestrator):
        """Test ensure_achievements uses provided metrics."""
        with app.app_context():
            metrics = {
                "questions_answered": 10,
                "average_speed_seconds": 3.0,
                "operation_stats": {"currentStreak": 5},
                "last_activity_at": datetime.utcnow()
            }
            
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    achievements = orchestrator.ensure_achievements(test_user, metrics=metrics)
                    
                    # Should not call compute_user_metrics since metrics provided
                    assert not mock_metrics.called

    def test_ensure_achievements_with_session_id(self, app, test_user, orchestrator):
        """Test ensure_achievements passes session_id to checkers."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 0,
                    "average_speed_seconds": 0.0,
                    "operation_stats": {}
                }
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    achievements = orchestrator.ensure_achievements(test_user, session_id=session.id)
                    
                    # Verify session_id was passed
                    assert mock_check.called
                    call_kwargs = mock_check.call_args[1]
                    assert call_kwargs.get("session_id") == session.id

    def test_ensure_achievements_calls_all_checkers(self, app, test_user, orchestrator):
        """Test ensure_achievements calls all checkers."""
        with app.app_context():
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 0,
                    "average_speed_seconds": 0.0,
                    "operation_stats": {}
                }
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    with patch.object(orchestrator.level_checker, 'check') as mock_level:
                        mock_level.return_value = []
                        
                        with patch.object(orchestrator.level_master_checker, 'check') as mock_master:
                            mock_master.return_value = []
                            
                            with patch.object(orchestrator.level_grandmaster_checker, 'check') as mock_grandmaster:
                                mock_grandmaster.return_value = []
                                
                                with patch.object(orchestrator.human_calculator_checker, 'check') as mock_calculator:
                                    mock_calculator.return_value = []
                                    
                                    achievements = orchestrator.ensure_achievements(test_user)
                                    
                                    # Verify all checkers were called
                                    assert mock_check.called
                                    assert mock_level.called
                                    assert mock_master.called
                                    assert mock_grandmaster.called
                                    assert mock_calculator.call_count == 2  # Bronze and silver

    def test_ensure_achievements_commits_on_new_achievements(self, app, test_user, orchestrator):
        """Test ensure_achievements commits when new achievements are awarded."""
        with app.app_context():
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 1,
                    "average_speed_seconds": 2.0,
                    "operation_stats": {},
                    "last_activity_at": datetime.utcnow()
                }
                
                new_achievement = Achievement(
                    user_id=test_user.id,
                    code="first-steps",
                    title="First Steps",
                    description="Answer your first question",
                    icon="🎯",
                    category="milestone"
                )
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = [new_achievement]
                    
                    with patch.object(db.session, 'commit') as mock_commit:
                        achievements = orchestrator.ensure_achievements(test_user)
                        
                        # Should have committed
                        assert mock_commit.called

    def test_ensure_achievements_with_data(self, app, test_user, orchestrator):
        """Test ensure_achievements_with_data uses pre-loaded data."""
        with app.app_context():
            metrics = {
                "questions_answered": 10,
                "average_speed_seconds": 3.0,
                "operation_stats": {}
            }
            
            existing_achievements = []
            user_responses = []
            user_sessions = []
            
            with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                mock_check.return_value = []
                
                with patch.object(orchestrator.level_checker, 'check') as mock_level:
                    mock_level.return_value = []
                    
                    achievements = orchestrator.ensure_achievements_with_data(
                        test_user,
                        metrics,
                        existing_achievements,
                        user_responses,
                        user_sessions
                    )
                    
                    assert isinstance(achievements, list)
                    assert mock_check.called
                    assert mock_level.called

    def test_ensure_achievements_with_data_commits(self, app, test_user, orchestrator):
        """Test ensure_achievements_with_data commits on new achievements."""
        with app.app_context():
            metrics = {
                "questions_answered": 1,
                "average_speed_seconds": 2.0,
                "operation_stats": {}
            }
            
            new_achievement = Achievement(
                user_id=test_user.id,
                code="first-steps",
                title="First Steps",
                description="Answer your first question",
                icon="🎯",
                category="milestone"
            )
            
            with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                mock_check.return_value = [new_achievement]
                
                with patch.object(db.session, 'commit') as mock_commit:
                    achievements = orchestrator.ensure_achievements_with_data(
                        test_user,
                        metrics,
                        [],
                        [],
                        []
                    )
                    
                    # Should have committed
                    assert mock_commit.called

    def test_ensure_achievements_batch_empty(self, app, orchestrator):
        """Test ensure_achievements_batch with empty list."""
        with app.app_context():
            result = orchestrator.ensure_achievements_batch([], {})
            assert result == {}

    def test_ensure_achievements_batch_single_user(self, app, test_user, orchestrator):
        """Test ensure_achievements_batch with single user."""
        with app.app_context():
            metrics = {
                test_user.id: {
                    "questions_answered": 10,
                    "average_speed_seconds": 3.0,
                    "operation_stats": {}
                }
            }
            
            with patch.object(orchestrator, 'ensure_achievements_with_data') as mock_ensure:
                mock_ensure.return_value = []
                
                result = orchestrator.ensure_achievements_batch([test_user], metrics)
                
                assert test_user.id in result
                assert mock_ensure.called

    def test_ensure_achievements_batch_multiple_users(self, app, orchestrator):
        """Test ensure_achievements_batch with multiple users."""
        with app.app_context():
            user1 = User(display_name="User 1", pin="1234", avatar="🐯", level=1)
            user2 = User(display_name="User 2", pin="5678", avatar="🐰", level=1)
            db.session.add_all([user1, user2])
            db.session.commit()
            
            metrics = {
                user1.id: {
                    "questions_answered": 10,
                    "average_speed_seconds": 3.0,
                    "operation_stats": {}
                },
                user2.id: {
                    "questions_answered": 5,
                    "average_speed_seconds": 2.0,
                    "operation_stats": {}
                }
            }
            
            with patch.object(orchestrator, 'ensure_achievements_with_data') as mock_ensure:
                mock_ensure.return_value = []
                
                result = orchestrator.ensure_achievements_batch([user1, user2], metrics)
                
                assert len(result) == 2
                assert user1.id in result
                assert user2.id in result
                assert mock_ensure.call_count == 2

    def test_ensure_achievements_batch_loads_data(self, app, test_user, test_question, orchestrator):
        """Test ensure_achievements_batch batch loads achievements, responses, and sessions."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            response = PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=2000
            )
            
            achievement = Achievement(
                user_id=test_user.id,
                code="first-steps",
                title="First Steps",
                description="Answer your first question",
                icon="🎯",
                category="milestone"
            )
            db.session.add(achievement)
            db.session.commit()
            
            metrics = {
                test_user.id: {
                    "questions_answered": 1,
                    "average_speed_seconds": 2.0,
                    "operation_stats": {}
                }
            }
            
            with patch.object(orchestrator, 'ensure_achievements_with_data') as mock_ensure:
                mock_ensure.return_value = [achievement]
                
                result = orchestrator.ensure_achievements_batch([test_user], metrics)
                
                # Verify data was passed to ensure_achievements_with_data
                call_args = mock_ensure.call_args[0]
                assert call_args[0] == test_user
                assert call_args[1] == metrics[test_user.id]
                assert len(call_args[2]) >= 1  # Existing achievements
                assert len(call_args[3]) >= 1  # Responses
                assert len(call_args[4]) >= 1  # Sessions

    def test_ensure_achievements_no_most_recent_achievement(self, app, test_user, test_question, orchestrator):
        """Test ensure_achievements when user has responses but no achievements."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            response = PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=2000
            )
            db.session.commit()
            
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 1,
                    "average_speed_seconds": 2.0,
                    "operation_stats": {}
                }
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    achievements = orchestrator.ensure_achievements(test_user)
                    
                    # Should process (not skip) since no achievements exist
                    assert mock_metrics.called or mock_check.called

    def test_ensure_achievements_returns_all_achievements(self, app, test_user, orchestrator):
        """Test ensure_achievements returns all user achievements."""
        with app.app_context():
            # Create existing achievements
            achievement1 = Achievement(
                user_id=test_user.id,
                code="first-steps",
                title="First Steps",
                description="Answer your first question",
                icon="🎯",
                category="milestone"
            )
            achievement2 = Achievement(
                user_id=test_user.id,
                code="speed-demon-bronze",
                title="Speed Demon (Bronze)",
                description="Fast speed",
                icon="⚡",
                category="speed"
            )
            db.session.add_all([achievement1, achievement2])
            db.session.commit()
            
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 0,
                    "average_speed_seconds": 0.0,
                    "operation_stats": {}
                }
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    achievements = orchestrator.ensure_achievements(test_user)
                    
                    # Should return all achievements
                    assert len(achievements) >= 2
                    codes = [a.code for a in achievements]
                    assert "first-steps" in codes
                    assert "speed-demon-bronze" in codes

    def test_ensure_achievements_awards_level_achievements(self, app, test_user, orchestrator):
        """Test ensure_achievements awards level-specific achievements."""
        with app.app_context():
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 0,
                    "average_speed_seconds": 0.0,
                    "operation_stats": {}
                }
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    level_achievement = Achievement(
                        user_id=test_user.id,
                        code="perfect-streak-bronze",
                        title="Perfect Streak (Bronze)",
                        description="Perfect streak",
                        icon="🔥",
                        category="consistency"
                    )
                    
                    with patch.object(orchestrator.level_checker, 'check') as mock_level:
                        mock_level.return_value = [level_achievement]
                        
                        with patch.object(db.session, 'commit') as mock_commit:
                            achievements = orchestrator.ensure_achievements(test_user)
                            
                            # Should have committed level achievements
                            assert mock_commit.called

    def test_ensure_achievements_awards_level_master_achievements(self, app, test_user, orchestrator):
        """Test ensure_achievements awards Level Master achievements."""
        with app.app_context():
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 0,
                    "average_speed_seconds": 0.0,
                    "operation_stats": {}
                }
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    with patch.object(orchestrator.level_checker, 'check') as mock_level:
                        mock_level.return_value = []
                        
                        level_master_achievement = Achievement(
                            user_id=test_user.id,
                            code="level-master-bronze",
                            title="Level Master (Bronze)",
                            description="30 consecutive correct",
                            icon="⭐",
                            category="milestone"
                        )
                        
                        with patch.object(orchestrator.level_master_checker, 'check') as mock_master:
                            mock_master.return_value = [level_master_achievement]
                            
                            with patch.object(db.session, 'commit') as mock_commit:
                                achievements = orchestrator.ensure_achievements(test_user)
                                
                                # Should have committed level master achievements
                                assert mock_commit.called

    def test_ensure_achievements_awards_level_grandmaster_achievements(self, app, test_user, orchestrator):
        """Test ensure_achievements awards Level Grandmaster achievements."""
        with app.app_context():
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 0,
                    "average_speed_seconds": 0.0,
                    "operation_stats": {}
                }
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    with patch.object(orchestrator.level_checker, 'check') as mock_level:
                        mock_level.return_value = []
                        
                        with patch.object(orchestrator.level_master_checker, 'check') as mock_master:
                            mock_master.return_value = []
                            
                            level_grandmaster_achievement = Achievement(
                                user_id=test_user.id,
                                code="level-grandmaster-bronze",
                                title="Level Grandmaster (Bronze)",
                                description="Level Master on all levels",
                                icon="👑",
                                category="milestone"
                            )
                            
                            with patch.object(orchestrator.level_grandmaster_checker, 'check') as mock_grandmaster:
                                mock_grandmaster.return_value = [level_grandmaster_achievement]
                                
                                with patch.object(db.session, 'commit') as mock_commit:
                                    achievements = orchestrator.ensure_achievements(test_user)
                                    
                                    # Should have committed level grandmaster achievements
                                    assert mock_commit.called

    def test_ensure_achievements_awards_human_calculator_achievements(self, app, test_user, orchestrator):
        """Test ensure_achievements awards Human Calculator achievements."""
        with app.app_context():
            with patch('app.services.achievements.achievement_orchestrator.AnalyticsService.compute_user_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "questions_answered": 0,
                    "average_speed_seconds": 0.0,
                    "operation_stats": {}
                }
                
                with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                    mock_check.return_value = []
                    
                    with patch.object(orchestrator.level_checker, 'check') as mock_level:
                        mock_level.return_value = []
                        
                        with patch.object(orchestrator.level_master_checker, 'check') as mock_master:
                            mock_master.return_value = []
                            
                            with patch.object(orchestrator.level_grandmaster_checker, 'check') as mock_grandmaster:
                                mock_grandmaster.return_value = []
                                
                                human_calculator_achievement = Achievement(
                                    user_id=test_user.id,
                                    code="human-calculator-bronze",
                                    title="Human Calculator (Bronze)",
                                    description="Lightning Fast on all levels",
                                    icon="🧮",
                                    category="milestone"
                                )
                                
                                with patch.object(orchestrator.human_calculator_checker, 'check') as mock_calculator:
                                    mock_calculator.return_value = [human_calculator_achievement]
                                    
                                    with patch.object(db.session, 'commit') as mock_commit:
                                        achievements = orchestrator.ensure_achievements(test_user)
                                        
                                        # Should have committed human calculator achievements
                                        assert mock_commit.called

    def test_ensure_achievements_with_data_awards_level_achievements(self, app, test_user, orchestrator):
        """Test ensure_achievements_with_data awards level achievements."""
        with app.app_context():
            metrics = {
                "questions_answered": 10,
                "average_speed_seconds": 3.0,
                "operation_stats": {}
            }
            
            level_achievement = Achievement(
                user_id=test_user.id,
                code="perfect-streak-bronze",
                title="Perfect Streak (Bronze)",
                description="Perfect streak",
                icon="🔥",
                category="consistency"
            )
            
            with patch('app.services.achievement_service.AchievementService.check_all_achievements') as mock_check:
                mock_check.return_value = []
                
                with patch.object(orchestrator.level_checker, 'check') as mock_level:
                    mock_level.return_value = [level_achievement]
                    
                    with patch.object(db.session, 'commit') as mock_commit:
                        achievements = orchestrator.ensure_achievements_with_data(
                            test_user,
                            metrics,
                            [],
                            [],
                            []
                        )
                        
                        # Should have committed level achievements
                        assert mock_commit.called

