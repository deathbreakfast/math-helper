"""Database wrapper with logging and transaction management."""

from __future__ import annotations

import functools
import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Callable, Generator, TypeVar

from flask import current_app
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .models import db

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Configure SQLite connection with optimized settings for performance and concurrency."""
    cursor = dbapi_conn.cursor()
    try:
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
    except Exception:
        pass  # Continue even if this fails
    
    # Enable WAL mode for better concurrent read/write performance
    # WAL mode may not work in all environments (e.g., network filesystems)
    # But we should still try to enable it for performance, even in tests
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
    except Exception:
        # If WAL mode fails, continue with default journal mode
        pass
    
    # Set busy timeout to 30 seconds (prevents hanging on lock contention)
    try:
        cursor.execute("PRAGMA busy_timeout=30000")
    except Exception:
        pass
    
    # Use NORMAL synchronous mode (good balance of safety and performance)
    try:
        cursor.execute("PRAGMA synchronous=NORMAL")
    except Exception:
        pass
    
    # Set cache size to 64MB (negative value means KB, so -64000 = 64MB)
    try:
        cursor.execute("PRAGMA cache_size=-64000")
    except Exception:
        pass
    
    cursor.close()


def log_query(func: F) -> F:
    """Decorator to log database operations with timing."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        func_name = f"{func.__module__}.{func.__name__}"
        start_time = time.time()

        try:
            logger.debug(f"Executing database operation: {func_name}")
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Database operation completed: {func_name} ({duration_ms:.2f}ms)")
            return result
        except SQLAlchemyError as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Database operation failed: {func_name} ({duration_ms:.2f}ms) - {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            raise
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Unexpected error in database operation: {func_name} ({duration_ms:.2f}ms) - {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            raise

    return wrapper  # type: ignore


@contextmanager
def transaction() -> Generator[None, None, None]:
    """Context manager for database transactions with automatic rollback on error."""

    try:
        logger.debug("Starting database transaction")
        yield
        db.session.commit()
        logger.debug("Database transaction committed")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database transaction rolled back due to error: {type(e).__name__}: {str(e)}")
        raise


@log_query
def execute_query(query: str, params: dict[str, Any] | None = None) -> Any:
    """Execute a raw SQL query with logging."""
    if params is None:
        params = {}
    return db.session.execute(text(query), params)


def get_session():
    """Get the current database session."""
    return db.session


def init_db(app):
    """Initialize database with foreign key support."""
    with app.app_context():
        # Check if we should clear DB on startup (for testing)
        if os.getenv("CLEAR_DB_ON_START", "false").lower() == "true":
            logger.info("CLEAR_DB_ON_START is set - clearing database on startup")
            from .models import (
                Achievement,
                DailyStat,
                FlaggedQuestion,
                LevelProblemConfig,
                LevelProgression,
                PracticeSession,
                Question,
                Response,
                ServerRecord,
                TestAttempt,
                User,
            )
            # Note: db is already imported at module level, don't re-import it
            
            # Delete all data in proper order to respect foreign key constraints
            with transaction():
                # Delete child records first (order matters for foreign keys)
                # Delete records that reference User, PracticeSession, or Question first
                TestAttempt.query.delete()
                DailyStat.query.delete()
                FlaggedQuestion.query.delete()
                Response.query.delete()
                Achievement.query.delete()
                ServerRecord.query.delete()  # References User and PracticeSession
                PracticeSession.query.delete()  # References User
                
                # Delete parent records
                User.query.delete()
                Question.query.delete()
                
                # Delete config tables (optional - these can be re-seeded)
                LevelProblemConfig.query.delete()
                LevelProgression.query.delete()
                
                # Reset SQLite sequence counters so IDs start from 1 after wipe
                try:
                    db.session.execute(text("DELETE FROM sqlite_sequence WHERE name IN ('practice_sessions', 'users', 'questions', 'responses', 'achievements', 'test_attempts', 'daily_stats', 'flagged_questions', 'server_records', 'level_problem_configs', 'level_progressions')"))
                    db.session.commit()
                    logger.info("SQLite sequence counters reset")
                except Exception as e:
                    logger.warning(f"Could not reset SQLite sequence counters: {e}")
                    # Continue anyway - this is optional
            
            logger.info("Database cleared successfully")
        
        # Configure SQLite with optimized settings
        # These may fail in some environments (e.g., network filesystems, test environments)
        # So we try each one individually and continue even if some fail
        try:
            db.session.execute(text("PRAGMA foreign_keys=ON"))
        except Exception:
            pass
        
        try:
            db.session.execute(text("PRAGMA journal_mode=WAL"))
        except Exception as e:
            logger.debug(f"Could not enable WAL mode: {e}. Continuing with default journal mode.")
        
        try:
            db.session.execute(text("PRAGMA busy_timeout=30000"))
        except Exception:
            pass
        
        try:
            db.session.execute(text("PRAGMA synchronous=NORMAL"))
        except Exception:
            pass
        
        try:
            db.session.execute(text("PRAGMA cache_size=-64000"))
        except Exception:
            pass
        
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        
        # Verify WAL mode is enabled
        wal_result = db.session.execute(text("PRAGMA journal_mode")).scalar()
        if wal_result and wal_result.upper() == "WAL":
            logger.info(f"SQLite WAL mode enabled successfully (journal_mode={wal_result})")
        else:
            logger.warning(f"SQLite WAL mode may not be enabled (journal_mode={wal_result})")
        
        # Log cache size for debugging
        cache_size = db.session.execute(text("PRAGMA cache_size")).scalar()
        logger.info(f"SQLite cache_size configured: {cache_size} pages")
        
        # Run migrations to ensure schema is up to date
        # Only run if database exists (migration handles new DB creation)
        # Skip migration in test mode - tests use db.create_all() which handles schema creation
        if not app.config.get('TESTING', False):
            try:
                import sys
                from pathlib import Path
                import sqlite3
                
                # Check if database exists
                db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
                if db_uri.startswith("sqlite:///"):
                    db_relative_path = db_uri.replace("sqlite:///", "")
                    if db_relative_path.startswith("/"):
                        db_path = Path(db_relative_path)
                    else:
                        instance_path = Path("instance") / db_relative_path
                        db_path = instance_path if instance_path.exists() else Path(db_relative_path)
                    
                    # Only run migration if database exists
                    if db_path.exists():
                        backend_dir = Path(__file__).parent.parent
                        if str(backend_dir) not in sys.path:
                            sys.path.insert(0, str(backend_dir))
                        from migrate import migrate_database
                        migrate_database(app)  # Pass the app instance to avoid creating new context
                        
                        # Verify composite indexes are created
                        expected_indexes = [
                            "ix_responses_user_correct_answered",
                            "ix_achievements_user_category_earned",
                            "ix_sessions_user_test_completed",
                            "ix_questions_operation_level",
                            "ix_responses_user_question_correct",
                        ]
                        for index_name in expected_indexes:
                            result = db.session.execute(
                                text("SELECT name FROM sqlite_master WHERE type='index' AND name=:name"),
                                {"name": index_name}
                            ).scalar()
                            if result:
                                logger.debug(f"Composite index verified: {index_name}")
                            else:
                                logger.warning(f"Composite index not found: {index_name} (may be created on next migration)")
            except Exception as e:
                logger.warning(f"Migration check failed: {e}")
        
        db.create_all()
        logger.info("Database initialized with foreign key support and performance optimizations")

