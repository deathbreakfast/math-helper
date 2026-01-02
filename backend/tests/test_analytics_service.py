"""Comprehensive tests for AnalyticsService.

Tests cover all methods in AnalyticsService to achieve >80% coverage.
"""

import pytest
from datetime import date, datetime, timedelta

from app import create_app, db
from app.models import DailyStat, Question, Response, User
from app.services.analytics_service import AnalyticsService
from app.services.analytics import OperationStatsBuilder, StreakCalculator
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


class TestAnalyticsService:
    """Test suite for AnalyticsService static methods."""

    def test_format_speed_none(self):
        """Test _format_speed with None."""
        assert OperationStatsBuilder._format_speed(None) == 0.0

    def test_format_speed_with_value(self):
        """Test _format_speed with a value."""
        assert OperationStatsBuilder._format_speed(5000) == 5.0
        assert OperationStatsBuilder._format_speed(1234) == 1.2  # Rounded to 1 decimal
        assert OperationStatsBuilder._format_speed(999) == 1.0

    def test_build_operation_stats_empty(self):
        """Test _build_operation_stats with empty rows."""
        stats = OperationStatsBuilder.build([])
        
        assert stats["additionAccuracy"] == 0
        assert stats["subtractionAccuracy"] == 0
        assert stats["multiplicationAccuracy"] == 0
        assert stats["divisionAccuracy"] == 0
        assert stats["additionSpeed"] == 0.0
        assert stats["subtractionSpeed"] == 0.0
        assert stats["multiplicationSpeed"] == 0.0
        assert stats["divisionSpeed"] == 0.0

    def test_build_operation_stats_with_data(self):
        """Test _build_operation_stats with data."""
        from types import SimpleNamespace
        
        rows = [
            SimpleNamespace(operation="addition", attempts=10, correct=8, avg_duration_ms=2000.0),
            SimpleNamespace(operation="subtraction", attempts=5, correct=4, avg_duration_ms=3000.0),
            SimpleNamespace(operation="multiplication", attempts=20, correct=15, avg_duration_ms=4000.0),
            SimpleNamespace(operation="division", attempts=8, correct=6, avg_duration_ms=5000.0),
        ]
        
        stats = OperationStatsBuilder.build(rows)
        
        assert stats["additionAccuracy"] == 80  # 8/10 * 100
        assert stats["subtractionAccuracy"] == 80  # 4/5 * 100
        assert stats["multiplicationAccuracy"] == 75  # 15/20 * 100
        assert stats["divisionAccuracy"] == 75  # 6/8 * 100
        assert stats["additionSpeed"] == 2.0  # 2000/1000
        assert stats["subtractionSpeed"] == 3.0  # 3000/1000
        assert stats["multiplicationSpeed"] == 4.0  # 4000/1000
        assert stats["divisionSpeed"] == 5.0  # 5000/1000

    def test_build_operation_stats_zero_attempts(self):
        """Test _build_operation_stats with zero attempts."""
        from types import SimpleNamespace
        
        rows = [
            SimpleNamespace(operation="addition", attempts=0, correct=0, avg_duration_ms=None),
        ]
        
        stats = OperationStatsBuilder.build(rows)
        
        # Should skip rows with zero attempts
        assert stats["additionAccuracy"] == 0

    def test_build_operation_stats_unknown_operation(self):
        """Test _build_operation_stats with unknown operation."""
        from types import SimpleNamespace
        
        rows = [
            SimpleNamespace(operation="unknown", attempts=10, correct=8, avg_duration_ms=2000.0),
        ]
        
        stats = OperationStatsBuilder.build(rows)
        
        # Unknown operations should be skipped
        assert stats["additionAccuracy"] == 0

    def test_longest_consecutive_run_empty(self):
        """Test _longest_consecutive_run with empty list."""
        assert StreakCalculator._longest_consecutive_run([]) == 0

    def test_longest_consecutive_run_single_date(self):
        """Test _longest_consecutive_run with single date."""
        dates = [date(2024, 1, 1)]
        assert StreakCalculator._longest_consecutive_run(dates) == 1

    def test_longest_consecutive_run_consecutive(self):
        """Test _longest_consecutive_run with consecutive dates."""
        dates = [
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 3),
        ]
        assert StreakCalculator._longest_consecutive_run(dates) == 3

    def test_longest_consecutive_run_with_gaps(self):
        """Test _longest_consecutive_run with gaps."""
        dates = [
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 5),  # Gap
            date(2024, 1, 6),
            date(2024, 1, 7),
        ]
        assert StreakCalculator._longest_consecutive_run(dates) == 3  # Longest is 3

    def test_longest_consecutive_run_multiple_streaks(self):
        """Test _longest_consecutive_run with multiple streaks."""
        dates = [
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 5),  # Gap
            date(2024, 1, 6),
            date(2024, 1, 7),
            date(2024, 1, 8),
        ]
        assert StreakCalculator._longest_consecutive_run(dates) == 4  # Longest is 4

    def test_current_run_empty(self):
        """Test _current_run with empty list."""
        assert StreakCalculator._current_run([]) == 0

    def test_current_run_today(self):
        """Test _current_run with today's date."""
        today = date.today()
        dates = [today]
        assert StreakCalculator._current_run(dates) == 1

    def test_current_run_yesterday(self):
        """Test _current_run with yesterday's date."""
        yesterday = date.today() - timedelta(days=1)
        dates = [yesterday]
        assert StreakCalculator._current_run(dates) == 1

    def test_current_run_two_days_ago(self):
        """Test _current_run with date two days ago (broken streak)."""
        two_days_ago = date.today() - timedelta(days=2)
        dates = [two_days_ago]
        assert StreakCalculator._current_run(dates) == 0

    def test_current_run_consecutive_ending_today(self):
        """Test _current_run with consecutive dates ending today."""
        today = date.today()
        dates = [
            today - timedelta(days=2),
            today - timedelta(days=1),
            today,
        ]
        assert StreakCalculator._current_run(dates) == 3

    def test_current_run_consecutive_ending_yesterday(self):
        """Test _current_run with consecutive dates ending yesterday."""
        yesterday = date.today() - timedelta(days=1)
        dates = [
            yesterday - timedelta(days=2),
            yesterday - timedelta(days=1),
            yesterday,
        ]
        assert StreakCalculator._current_run(dates) == 3

    def test_current_run_with_gap(self):
        """Test _current_run with gap before last date."""
        today = date.today()
        dates = [
            today - timedelta(days=5),
            today - timedelta(days=4),
            today - timedelta(days=2),  # Gap before this
            today - timedelta(days=1),
            today,
        ]
        # The streak counts backwards: today, today-1, today-2 (3 consecutive)
        # Then breaks at today-4 (gap of 2 days)
        assert StreakCalculator._current_run(dates) == 3

    def test_compute_user_metrics_no_responses(self, app, test_user):
        """Test compute_user_metrics with no responses."""
        with app.app_context():
            metrics = AnalyticsService.compute_user_metrics(test_user.id)
            
            assert metrics["questions_answered"] == 0
            assert metrics["average_speed_seconds"] == 0.0
            assert metrics["last_activity_at"] is None
            assert metrics["operation_stats"]["currentStreak"] == 0
            assert metrics["operation_stats"]["bestStreak"] == 0

    def test_compute_user_metrics_with_responses(self, app, test_user, test_question):
        """Test compute_user_metrics with responses."""
        with app.app_context():
            # Create responses
            session = PracticeService.create_session(user_id=test_user.id)
            
            # Add multiple responses
            for i in range(5):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_question.id,
                    user_id=test_user.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=(i < 4),  # 4 correct, 1 incorrect
                    duration_ms=2000 + i * 100
                )
            
            metrics = AnalyticsService.compute_user_metrics(test_user.id)
            
            assert metrics["questions_answered"] == 5
            assert metrics["average_speed_seconds"] > 0
            assert metrics["last_activity_at"] is not None
            assert "additionAccuracy" in metrics["operation_stats"]

    def test_compute_user_metrics_with_multiple_operations(self, app, test_user):
        """Test compute_user_metrics with multiple operations."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            # Create questions for different operations
            q1 = PracticeService.create_question(
                operation="addition",
                operand1=1,
                operand2=1,
                correct_answer="2",
                prompt="1 + 1",
            )
            q2 = PracticeService.create_question(
                operation="subtraction",
                operand1=5,
                operand2=3,
                correct_answer="2",
                prompt="5 - 3",
            )
            
            # Add responses
            PracticeService.record_response(
                session_id=session.id,
                question_id=q1.id,
                user_id=test_user.id,
                submitted_answer="2",
                correct_answer="2",
                is_correct=True,
                duration_ms=2000
            )
            PracticeService.record_response(
                session_id=session.id,
                question_id=q2.id,
                user_id=test_user.id,
                submitted_answer="2",
                correct_answer="2",
                is_correct=True,
                duration_ms=3000
            )
            
            metrics = AnalyticsService.compute_user_metrics(test_user.id)
            
            assert metrics["questions_answered"] == 2
            assert metrics["operation_stats"]["additionAccuracy"] == 100
            assert metrics["operation_stats"]["subtractionAccuracy"] == 100

    def test_aggregate_daily_stats_single_date(self, app, test_user, test_question):
        """Test aggregate_daily_stats for a single date."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            today = date.today()
            
            # Create response with today's date
            response = PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=2000
            )
            # Set answered_at to today
            response.answered_at = datetime.combine(today, datetime.min.time())
            db.session.add(response)
            db.session.commit()
            
            AnalyticsService.aggregate_daily_stats(test_user.id, target_date=today)
            
            # Check daily stat was created
            stat = DailyStat.query.filter_by(
                user_id=test_user.id,
                date=today,
                operation="addition"
            ).first()
            
            assert stat is not None
            assert stat.questions_answered == 1
            assert stat.correct_count == 1
            assert stat.accuracy == 100.0

    def test_aggregate_daily_stats_all_dates(self, app, test_user, test_question):
        """Test aggregate_daily_stats for all dates."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # Create responses for different dates
            for stat_date in [yesterday, today]:
                response = PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_question.id,
                    user_id=test_user.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
                response.answered_at = datetime.combine(stat_date, datetime.min.time())
                db.session.add(response)
            
            db.session.commit()
            
            AnalyticsService.aggregate_daily_stats(test_user.id, target_date=None)
            
            # Check both daily stats were created
            stats = DailyStat.query.filter_by(user_id=test_user.id).all()
            assert len(stats) == 2

    def test_aggregate_daily_stats_updates_existing(self, app, test_user, test_question):
        """Test aggregate_daily_stats updates existing daily stat."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            today = date.today()
            
            # Create initial response
            response = PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=2000
            )
            response.answered_at = datetime.combine(today, datetime.min.time())
            db.session.add(response)
            db.session.commit()
            
            # Aggregate first time
            AnalyticsService.aggregate_daily_stats(test_user.id, target_date=today)
            
            # Add another response
            response2 = PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=False,
                duration_ms=3000
            )
            response2.answered_at = datetime.combine(today, datetime.min.time())
            db.session.add(response2)
            db.session.commit()
            
            # Aggregate again
            AnalyticsService.aggregate_daily_stats(test_user.id, target_date=today)
            
            # Check stat was updated
            stat = DailyStat.query.filter_by(
                user_id=test_user.id,
                date=today,
                operation="addition"
            ).first()
            
            assert stat.questions_answered == 2
            assert stat.correct_count == 1
            assert stat.accuracy == 50.0

    def test_get_time_series_data_default_range(self, app, test_user):
        """Test get_time_series_data with default range."""
        with app.app_context():
            today = date.today()
            
            # Create daily stats
            for i in range(3):
                stat_date = today - timedelta(days=i)
                daily_stat = DailyStat(
                    user_id=test_user.id,
                    date=stat_date,
                    operation="addition",
                    questions_answered=10,
                    correct_count=8,
                    accuracy=80.0,
                    avg_duration_ms=2000.0,
                    avg_speed_seconds=2.0
                )
                db.session.add(daily_stat)
            
            db.session.commit()
            
            data = AnalyticsService.get_time_series_data(test_user.id)
            
            assert len(data) == 3
            assert all("date" in d for d in data)
            assert all("addition" in d for d in data)

    def test_get_time_series_data_with_date_range(self, app, test_user):
        """Test get_time_series_data with date range."""
        with app.app_context():
            today = date.today()
            start_date = today - timedelta(days=5)
            end_date = today - timedelta(days=1)
            
            # Create daily stats
            for i in range(7):
                stat_date = today - timedelta(days=i)
                daily_stat = DailyStat(
                    user_id=test_user.id,
                    date=stat_date,
                    operation="addition",
                    questions_answered=10,
                    correct_count=8,
                    accuracy=80.0,
                    avg_duration_ms=2000.0,
                    avg_speed_seconds=2.0
                )
                db.session.add(daily_stat)
            
            db.session.commit()
            
            data = AnalyticsService.get_time_series_data(
                test_user.id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Should only include dates in range
            assert len(data) == 5  # 5 days in range

    def test_get_time_series_data_with_operation_filter(self, app, test_user):
        """Test get_time_series_data with operation filter."""
        with app.app_context():
            today = date.today()
            
            # Create daily stats for different operations
            for operation in ["addition", "subtraction"]:
                daily_stat = DailyStat(
                    user_id=test_user.id,
                    date=today,
                    operation=operation,
                    questions_answered=10,
                    correct_count=8,
                    accuracy=80.0,
                    avg_duration_ms=2000.0,
                    avg_speed_seconds=2.0
                )
                db.session.add(daily_stat)
            
            db.session.commit()
            
            data = AnalyticsService.get_time_series_data(
                test_user.id,
                operation="addition"
            )
            
            assert len(data) == 1
            assert data[0]["addition"] is not None
            assert data[0]["subtraction"] is None

    def test_get_weekly_gain_no_responses(self, app, test_user):
        """Test get_weekly_gain with no responses."""
        with app.app_context():
            gain = AnalyticsService.get_weekly_gain(test_user.id)
            assert gain == 0

    def test_get_weekly_gain_this_week_only(self, app, test_user, test_question):
        """Test get_weekly_gain with responses only this week."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            
            # Create responses this week
            for i in range(5):
                response = PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_question.id,
                    user_id=test_user.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
                response.answered_at = datetime.combine(week_start + timedelta(days=i), datetime.min.time())
                db.session.add(response)
            
            db.session.commit()
            
            gain = AnalyticsService.get_weekly_gain(test_user.id)
            assert gain == 5  # 5 this week, 0 last week

    def test_get_weekly_gain_last_week_only(self, app, test_user, test_question):
        """Test get_weekly_gain with responses only last week."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            last_week_start = week_start - timedelta(weeks=1)
            
            # Create responses last week
            for i in range(3):
                response = PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_question.id,
                    user_id=test_user.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
                response.answered_at = datetime.combine(last_week_start + timedelta(days=i), datetime.min.time())
                db.session.add(response)
            
            db.session.commit()
            
            gain = AnalyticsService.get_weekly_gain(test_user.id)
            assert gain == 0  # 0 this week, 3 last week (negative gain becomes 0)

    def test_get_weekly_gain_both_weeks(self, app, test_user, test_question):
        """Test get_weekly_gain with responses in both weeks."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            last_week_start = week_start - timedelta(weeks=1)
            
            # Create responses this week
            for i in range(5):
                response = PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_question.id,
                    user_id=test_user.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
                response.answered_at = datetime.combine(week_start + timedelta(days=i), datetime.min.time())
                db.session.add(response)
            
            # Create responses last week
            for i in range(3):
                response = PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_question.id,
                    user_id=test_user.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
                response.answered_at = datetime.combine(last_week_start + timedelta(days=i), datetime.min.time())
                db.session.add(response)
            
            db.session.commit()
            
            gain = AnalyticsService.get_weekly_gain(test_user.id)
            assert gain == 2  # 5 this week - 3 last week

    def test_compute_user_metrics_batch_empty(self, app):
        """Test compute_user_metrics_batch with empty list."""
        with app.app_context():
            result = AnalyticsService.compute_user_metrics_batch([])
            assert result == {}

    def test_compute_user_metrics_batch_single_user(self, app, test_user, test_question):
        """Test compute_user_metrics_batch with single user."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=2000
            )
            
            result = AnalyticsService.compute_user_metrics_batch([test_user.id])
            
            assert test_user.id in result
            assert result[test_user.id]["questions_answered"] == 1

    def test_compute_user_metrics_batch_multiple_users(self, app, test_question):
        """Test compute_user_metrics_batch with multiple users."""
        with app.app_context():
            user1 = User(display_name="User 1", pin="1234", avatar="🐯", level=1)
            user2 = User(display_name="User 2", pin="5678", avatar="🐰", level=1)
            db.session.add_all([user1, user2])
            db.session.commit()
            
            session1 = PracticeService.create_session(user_id=user1.id)
            session2 = PracticeService.create_session(user_id=user2.id)
            
            # Add responses for user1
            for _ in range(3):
                PracticeService.record_response(
                    session_id=session1.id,
                    question_id=test_question.id,
                    user_id=user1.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
            
            # Add responses for user2
            for _ in range(5):
                PracticeService.record_response(
                    session_id=session2.id,
                    question_id=test_question.id,
                    user_id=user2.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
            
            result = AnalyticsService.compute_user_metrics_batch([user1.id, user2.id])
            
            assert len(result) == 2
            assert result[user1.id]["questions_answered"] == 3
            assert result[user2.id]["questions_answered"] == 5

    def test_calculate_streaks_batch_empty(self, app):
        """Test _calculate_streaks_batch with empty list."""
        with app.app_context():
            result = StreakCalculator.calculate_streaks_batch([])
            assert result == {}

    def test_calculate_streaks_batch_with_daily_stats(self, app, test_user):
        """Test _calculate_streaks_batch using daily stats."""
        with app.app_context():
            today = date.today()
            
            # Create daily stats for consecutive days
            for i in range(3):
                stat_date = today - timedelta(days=i)
                daily_stat = DailyStat(
                    user_id=test_user.id,
                    date=stat_date,
                    operation="addition",
                    questions_answered=10,
                    correct_count=8,
                    accuracy=80.0
                )
                db.session.add(daily_stat)
            
            db.session.commit()
            
            result = StreakCalculator.calculate_streaks_batch([test_user.id])
            
            assert test_user.id in result
            assert result[test_user.id]["best"] == 3
            assert result[test_user.id]["current"] >= 1

    def test_calculate_streaks_batch_with_responses(self, app, test_user, test_question):
        """Test _calculate_streaks_batch using responses (fallback)."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            today = date.today()
            
            # Create responses for consecutive days
            for i in range(2):
                response = PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_question.id,
                    user_id=test_user.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
                response.answered_at = datetime.combine(today - timedelta(days=i), datetime.min.time())
                db.session.add(response)
            
            db.session.commit()
            
            result = StreakCalculator.calculate_streaks_batch([test_user.id])
            
            assert test_user.id in result
            assert result[test_user.id]["best"] == 2
            assert result[test_user.id]["current"] >= 1

    def test_calculate_streaks_batch_no_data(self, app, test_user):
        """Test _calculate_streaks_batch with user having no daily stats or responses."""
        with app.app_context():
            result = StreakCalculator.calculate_streaks_batch([test_user.id])
            
            assert test_user.id in result
            assert result[test_user.id]["current"] == 0
            assert result[test_user.id]["best"] == 0

    def test_calculate_streaks_with_daily_stats(self, app, test_user):
        """Test _calculate_streaks uses daily_stats when available."""
        with app.app_context():
            today = date.today()
            
            # Create daily stats
            for i in range(2):
                stat_date = today - timedelta(days=i)
                daily_stat = DailyStat(
                    user_id=test_user.id,
                    date=stat_date,
                    operation="addition",
                    questions_answered=10,
                    correct_count=8,
                    accuracy=80.0
                )
                db.session.add(daily_stat)
            
            db.session.commit()
            
            streaks = StreakCalculator.calculate_streaks(test_user.id)
            
            assert streaks["best"] == 2
            assert streaks["current"] >= 1

    def test_calculate_streaks_fallback_to_responses(self, app, test_user, test_question):
        """Test _calculate_streaks falls back to responses when no daily stats."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            today = date.today()
            
            # Create responses (no daily stats)
            for i in range(2):
                response = PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_question.id,
                    user_id=test_user.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
                response.answered_at = datetime.combine(today - timedelta(days=i), datetime.min.time())
                db.session.add(response)
            
            db.session.commit()
            
            streaks = StreakCalculator.calculate_streaks(test_user.id)
            
            assert streaks["best"] == 2
            assert streaks["current"] >= 1

    def test_get_weekly_gain_batch_empty(self, app):
        """Test get_weekly_gain_batch with empty list."""
        with app.app_context():
            result = AnalyticsService.get_weekly_gain_batch([])
            assert result == {}

    def test_get_weekly_gain_batch_multiple_users(self, app, test_question):
        """Test get_weekly_gain_batch with multiple users."""
        with app.app_context():
            user1 = User(display_name="User 1", pin="1234", avatar="🐯", level=1)
            user2 = User(display_name="User 2", pin="5678", avatar="🐰", level=1)
            db.session.add_all([user1, user2])
            db.session.commit()
            
            session1 = PracticeService.create_session(user_id=user1.id)
            session2 = PracticeService.create_session(user_id=user2.id)
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            
            # User1: 5 this week, 3 last week
            for i in range(5):
                response = PracticeService.record_response(
                    session_id=session1.id,
                    question_id=test_question.id,
                    user_id=user1.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
                response.answered_at = datetime.combine(week_start + timedelta(days=i), datetime.min.time())
                db.session.add(response)
            
            last_week_start = week_start - timedelta(weeks=1)
            for i in range(3):
                response = PracticeService.record_response(
                    session_id=session1.id,
                    question_id=test_question.id,
                    user_id=user1.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
                response.answered_at = datetime.combine(last_week_start + timedelta(days=i), datetime.min.time())
                db.session.add(response)
            
            # User2: 2 this week, 0 last week
            for i in range(2):
                response = PracticeService.record_response(
                    session_id=session2.id,
                    question_id=test_question.id,
                    user_id=user2.id,
                    submitted_answer="8",
                    correct_answer="8",
                    is_correct=True,
                    duration_ms=2000
                )
                response.answered_at = datetime.combine(week_start + timedelta(days=i), datetime.min.time())
                db.session.add(response)
            
            db.session.commit()
            
            result = AnalyticsService.get_weekly_gain_batch([user1.id, user2.id])
            
            assert result[user1.id] == 2  # 5 - 3
            assert result[user2.id] == 2  # 2 - 0

