"""Database wrapper with logging and transaction management."""

from __future__ import annotations

import functools
import logging
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
    """Enable foreign key constraints in SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
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
        # Enable foreign keys for SQLite
        db.session.execute(text("PRAGMA foreign_keys=ON"))
        db.session.commit()
        
        # Run migrations to ensure schema is up to date
        # Only run if database exists (migration handles new DB creation)
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
        except Exception as e:
            logger.warning(f"Migration check failed: {e}")
        
        db.create_all()
        logger.info("Database initialized with foreign key support")

