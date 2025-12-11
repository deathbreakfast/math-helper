"""Database migration script to update existing schema with new tables and foreign keys."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app import create_app
from app.database import init_db
from app.models import db
from app.services.level_config_service import LevelConfigService


def migrate_database(app=None):
    """Migrate existing database to new schema.
    
    Args:
        app: Optional Flask app instance. If not provided, creates a new one.
    """
    if app is None:
        app = create_app()

    with app.app_context():
        # Enable foreign keys
        db.session.execute(db.text("PRAGMA foreign_keys=ON"))
        db.session.commit()

        # Get database path - match Flask's default behavior
        db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
        if db_uri.startswith("sqlite:///"):
            # Remove sqlite:/// prefix
            db_relative_path = db_uri.replace("sqlite:///", "")
            # If it's an absolute path, use it directly
            if db_relative_path.startswith("/"):
                db_path = Path(db_relative_path)
            else:
                # Relative path - check instance folder first (Flask default), then current dir
                instance_path = Path("instance") / db_relative_path
                if instance_path.exists():
                    db_path = instance_path
                else:
                    db_path = Path(db_relative_path)
        else:
            # Default to instance folder
            db_path = Path("instance/math_helper.db")

        if not db_path.exists():
            print(f"Database not found at {db_path}, creating new database...")
            db.create_all()
            print("New database created successfully.")
            return

        # Connect directly to SQLite for migration
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        try:
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys=ON")

            # Check if new tables exist
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='practice_sessions'"
            )
            practice_sessions_exists = cursor.fetchone() is not None

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='flagged_questions'"
            )
            flagged_questions_exists = cursor.fetchone() is not None

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_stats'")
            daily_stats_exists = cursor.fetchone() is not None

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='level_progression'"
            )
            level_progression_exists = cursor.fetchone() is not None

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='level_problem_config'"
            )
            level_problem_config_exists = cursor.fetchone() is not None

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='server_records'"
            )
            server_records_exists = cursor.fetchone() is not None

            # Check if questions table exists and has new columns
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='questions'"
            )
            questions_exists = cursor.fetchone() is not None
            needs_question_update = False
            if questions_exists:
                cursor.execute("PRAGMA table_info(questions)")
                question_columns = {row[1] for row in cursor.fetchall()}
                needs_question_update = "operand1" not in question_columns

            # Check if responses table exists and has new columns
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='responses'"
            )
            responses_exists = cursor.fetchone() is not None
            needs_response_update = False
            if responses_exists:
                cursor.execute("PRAGMA table_info(responses)")
                response_columns = {row[1] for row in cursor.fetchall()}
                needs_response_update = "session_id" not in response_columns

            # Check if users table exists and has updated_at
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            )
            users_exists = cursor.fetchone() is not None
            needs_user_update = False
            if users_exists:
                cursor.execute("PRAGMA table_info(users)")
                user_columns = {row[1] for row in cursor.fetchall()}
                needs_user_update = "updated_at" not in user_columns

            print("Starting database migration...")

            # Create new tables
            if not practice_sessions_exists:
                print("Creating practice_sessions table...")
                cursor.execute(
                    """
                    CREATE TABLE practice_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        mode VARCHAR(32) NOT NULL,
                        level INTEGER,
                        is_test BOOLEAN NOT NULL DEFAULT 0,
                        test_type VARCHAR(64),
                        started_at DATETIME NOT NULL,
                        completed_at DATETIME,
                        total_questions INTEGER NOT NULL DEFAULT 0,
                        correct_count INTEGER NOT NULL DEFAULT 0,
                        accuracy REAL NOT NULL DEFAULT 0.0,
                        total_duration_ms INTEGER,
                        question_ids TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """
                )
                cursor.execute("CREATE INDEX ix_practice_sessions_user_id ON practice_sessions(user_id)")
                cursor.execute(
                    "CREATE INDEX ix_practice_sessions_started_at ON practice_sessions(started_at)"
                )
            else:
                # Check if new columns exist and add them if missing
                cursor.execute("PRAGMA table_info(practice_sessions)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if "is_test" not in columns:
                    print("Adding is_test column to practice_sessions table...")
                    cursor.execute("ALTER TABLE practice_sessions ADD COLUMN is_test BOOLEAN NOT NULL DEFAULT 0")
                
                if "test_type" not in columns:
                    print("Adding test_type column to practice_sessions table...")
                    cursor.execute("ALTER TABLE practice_sessions ADD COLUMN test_type VARCHAR(64)")
                
                if "question_ids" not in columns:
                    print("Adding question_ids column to practice_sessions table...")
                    cursor.execute("ALTER TABLE practice_sessions ADD COLUMN question_ids TEXT")

            if not flagged_questions_exists:
                print("Creating flagged_questions table...")
                cursor.execute(
                    """
                    CREATE TABLE flagged_questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        question_id INTEGER NOT NULL,
                        session_id INTEGER,
                        flagged_at DATETIME NOT NULL,
                        notes TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
                        FOREIGN KEY (session_id) REFERENCES practice_sessions(id) ON DELETE SET NULL,
                        UNIQUE(user_id, question_id, session_id)
                    )
                """
                )
                cursor.execute(
                    "CREATE INDEX ix_flagged_questions_user_id ON flagged_questions(user_id)"
                )
                cursor.execute(
                    "CREATE INDEX ix_flagged_questions_question_id ON flagged_questions(question_id)"
                )

            if not daily_stats_exists:
                print("Creating daily_stats table...")
                cursor.execute(
                    """
                    CREATE TABLE daily_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        date DATE NOT NULL,
                        operation VARCHAR(32) NOT NULL,
                        questions_answered INTEGER NOT NULL DEFAULT 0,
                        correct_count INTEGER NOT NULL DEFAULT 0,
                        accuracy REAL NOT NULL DEFAULT 0.0,
                        avg_duration_ms INTEGER,
                        avg_speed_seconds REAL,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        UNIQUE(user_id, date, operation)
                    )
                """
                )
                cursor.execute("CREATE INDEX ix_daily_stats_user_id ON daily_stats(user_id)")
                cursor.execute("CREATE INDEX ix_daily_stats_date ON daily_stats(date)")
                cursor.execute("CREATE INDEX ix_daily_stats_operation ON daily_stats(operation)")

            if not level_progression_exists:
                print("Creating level_progression table...")
                cursor.execute(
                    """
                    CREATE TABLE level_progression (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        target_level INTEGER NOT NULL,
                        required_achievement_code VARCHAR(64) NOT NULL,
                        "order" INTEGER,
                        created_at DATETIME NOT NULL,
                        UNIQUE(target_level, required_achievement_code)
                    )
                """
                )
                cursor.execute(
                    "CREATE INDEX ix_level_progression_target_level ON level_progression(target_level)"
                )

            if not level_problem_config_exists:
                print("Creating level_problem_config table...")
                cursor.execute(
                    """
                    CREATE TABLE level_problem_config (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        level INTEGER NOT NULL,
                        operation VARCHAR(32) NOT NULL,
                        min_operand1 INTEGER,
                        max_operand1 INTEGER,
                        min_operand2 INTEGER,
                        max_operand2 INTEGER,
                        layout_types TEXT,
                        answer_formats TEXT,
                        is_available BOOLEAN NOT NULL DEFAULT 1,
                        created_at DATETIME NOT NULL,
                        UNIQUE(level, operation)
                    )
                """
                )
                cursor.execute(
                    "CREATE INDEX ix_level_problem_config_level ON level_problem_config(level)"
                )
                cursor.execute(
                    "CREATE INDEX ix_level_problem_config_operation ON level_problem_config(operation)"
                )

            if not server_records_exists:
                print("Creating server_records table...")
                cursor.execute(
                    """
                    CREATE TABLE server_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        achievement_type VARCHAR(64) NOT NULL UNIQUE,
                        record_type VARCHAR(32) NOT NULL,
                        record_value REAL NOT NULL,
                        user_id INTEGER NOT NULL,
                        achieved_at DATETIME NOT NULL,
                        session_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (session_id) REFERENCES practice_sessions(id) ON DELETE SET NULL
                    )
                """
                )
                cursor.execute(
                    "CREATE INDEX ix_server_records_achievement_type ON server_records(achievement_type)"
                )
                cursor.execute(
                    "CREATE INDEX ix_server_records_record_type ON server_records(record_type)"
                )
                cursor.execute(
                    "CREATE INDEX ix_server_records_user_id ON server_records(user_id)"
                )

            # Update existing tables
            if needs_user_update:
                print("Adding updated_at column to users table...")
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN updated_at DATETIME")
                except sqlite3.OperationalError as e:
                    if "duplicate column" not in str(e).lower():
                        raise

            if needs_question_update:
                print("Migrating questions table...")
                # Create new questions table with all columns
                cursor.execute(
                    """
                    CREATE TABLE questions_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation VARCHAR(32) NOT NULL,
                        operand1 INTEGER NOT NULL,
                        operand2 INTEGER NOT NULL,
                        correct_answer TEXT NOT NULL,
                        prompt TEXT NOT NULL,
                        difficulty VARCHAR(32),
                        required_level INTEGER NOT NULL DEFAULT 1,
                        level_tag VARCHAR(32),
                        target_ms INTEGER,
                        hint TEXT,
                        answer_format VARCHAR(32),
                        accepted_answers TEXT,
                        layout_type VARCHAR(32),
                        layout_config TEXT,
                        math_type_label VARCHAR(128),
                        created_at DATETIME NOT NULL
                    )
                    """
                )

                # Copy existing data (try to extract operands from prompt if possible)
                if questions_exists:
                    cursor.execute("SELECT id, prompt, operation, level_tag, difficulty, created_at FROM questions")
                    old_questions = cursor.fetchall()

                    for qid, prompt, operation, level_tag, difficulty, created_at in old_questions:
                        # Try to parse operands from prompt (e.g., "5 + 3" -> operand1=5, operand2=3)
                        operand1 = 0
                        operand2 = 0
                        correct_answer = "0"

                        # Simple parsing attempt
                        try:
                            if operation:
                                parts = prompt.split()
                                if len(parts) >= 3:
                                    operand1 = int(parts[0])
                                    operand2 = int(parts[2])
                                    # Calculate correct answer
                                    if operation == "addition":
                                        correct_answer = str(operand1 + operand2)
                                    elif operation == "subtraction":
                                        correct_answer = str(operand1 - operand2)
                                    elif operation == "multiplication":
                                        correct_answer = str(operand1 * operand2)
                                    elif operation == "division":
                                        if operand2 != 0:
                                            correct_answer = str(operand1 // operand2)
                        except (ValueError, IndexError):
                            pass

                        cursor.execute(
                            """
                            INSERT INTO questions_new 
                            (id, operation, operand1, operand2, correct_answer, prompt, difficulty, 
                             required_level, level_tag, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (qid, operation or "addition", operand1, operand2, correct_answer, prompt, difficulty, 1, level_tag, created_at),
                        )

                # Drop old table if it exists and rename new one
                if questions_exists:
                    # Temporarily disable foreign key checks to allow dropping table
                    cursor.execute("PRAGMA foreign_keys=OFF")
                    try:
                        cursor.execute("DROP TABLE questions")
                    finally:
                        cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("ALTER TABLE questions_new RENAME TO questions")

                # Create indexes
                cursor.execute("CREATE INDEX ix_questions_operation ON questions(operation)")
                cursor.execute("CREATE INDEX ix_questions_required_level ON questions(required_level)")
                cursor.execute("CREATE INDEX ix_questions_level_tag ON questions(level_tag)")

            if needs_response_update:
                print("Migrating responses table...")
                # Add new columns
                try:
                    cursor.execute("ALTER TABLE responses ADD COLUMN session_id INTEGER")
                    cursor.execute(
                        "ALTER TABLE responses ADD COLUMN is_flagged BOOLEAN NOT NULL DEFAULT 0"
                    )
                except sqlite3.OperationalError as e:
                    if "duplicate column" not in str(e).lower():
                        raise

                # Update foreign key constraints (SQLite doesn't support ALTER TABLE for foreign keys)
                # We'll need to recreate the table
                cursor.execute(
                    """
                    CREATE TABLE responses_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER,
                        question_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        submitted_answer TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        is_correct BOOLEAN NOT NULL,
                        duration_ms INTEGER,
                        answered_at DATETIME NOT NULL,
                        is_flagged BOOLEAN NOT NULL DEFAULT 0,
                        FOREIGN KEY (session_id) REFERENCES practice_sessions(id) ON DELETE CASCADE,
                        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """
                )

                # Copy data if responses table exists
                if responses_exists:
                    cursor.execute(
                        """
                        INSERT INTO responses_new 
                        (id, question_id, user_id, submitted_answer, correct_answer, is_correct, 
                         duration_ms, answered_at, is_flagged)
                        SELECT id, question_id, user_id, submitted_answer, 
                               COALESCE(correct_answer, ''), 
                               COALESCE(is_correct, 0),
                               duration_ms, answered_at, 0
                        FROM responses
                    """
                    )

                # Drop old table if it exists and rename new one
                if responses_exists:
                    # Temporarily disable foreign key checks to allow dropping table
                    cursor.execute("PRAGMA foreign_keys=OFF")
                    try:
                        cursor.execute("DROP TABLE responses")
                    finally:
                        cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("ALTER TABLE responses_new RENAME TO responses")

                # Create indexes
                cursor.execute("CREATE INDEX ix_responses_session_id ON responses(session_id)")
                cursor.execute("CREATE INDEX ix_responses_question_id ON responses(question_id)")
                cursor.execute("CREATE INDEX ix_responses_user_id ON responses(user_id)")
                cursor.execute("CREATE INDEX ix_responses_answered_at ON responses(answered_at)")
                cursor.execute("CREATE INDEX ix_responses_is_flagged ON responses(is_flagged)")

            # Update achievements table indexes if needed
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='achievements'"
            )
            achievements_exists = cursor.fetchone() is not None
            if achievements_exists:
                cursor.execute("PRAGMA table_info(achievements)")
                achievement_columns = {row[1] for row in cursor.fetchall()}
                if "category" in achievement_columns:
                    # Check if index exists
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='index' AND name='ix_achievements_category'"
                    )
                    if cursor.fetchone() is None:
                        print("Adding index on achievements.category...")
                        cursor.execute("CREATE INDEX ix_achievements_category ON achievements(category)")
                
                # Migrate unique constraint to include achievement_metadata
                # Check if old constraint exists (SQLite stores unique constraints as indexes)
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name='uq_user_achievement_code'"
                )
                old_constraint_exists = cursor.fetchone() is not None
                
                # Check if new constraint exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name='uq_user_achievement_code_metadata'"
                )
                new_constraint_exists = cursor.fetchone() is not None
                
                if old_constraint_exists and not new_constraint_exists:
                    print("Migrating achievements unique constraint to include achievement_metadata...")
                    # Drop old unique index
                    cursor.execute("DROP INDEX IF EXISTS uq_user_achievement_code")
                    # Create new unique index including achievement_metadata
                    # Note: SQLite allows multiple NULLs in unique constraints, which is what we want
                    cursor.execute(
                        """
                        CREATE UNIQUE INDEX uq_user_achievement_code_metadata 
                        ON achievements(user_id, code, achievement_metadata)
                        """
                    )
                    print("Achievements unique constraint migrated successfully!")
                elif not new_constraint_exists:
                    # No old constraint exists, just create the new one
                    print("Creating achievements unique constraint with achievement_metadata...")
                    cursor.execute(
                        """
                        CREATE UNIQUE INDEX uq_user_achievement_code_metadata 
                        ON achievements(user_id, code, achievement_metadata)
                        """
                    )

            # Add composite indexes for performance optimization
            print("Adding composite indexes for performance optimization...")
            
            # Composite index on responses for streak calculations: (user_id, is_correct, answered_at)
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='ix_responses_user_correct_answered'"
            )
            if cursor.fetchone() is None:
                print("Adding composite index on responses(user_id, is_correct, answered_at)...")
                cursor.execute(
                    "CREATE INDEX ix_responses_user_correct_answered ON responses(user_id, is_correct, answered_at)"
                )
            
            # Composite index on achievements for filtering: (user_id, category, earned_at)
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='ix_achievements_user_category_earned'"
            )
            if cursor.fetchone() is None:
                print("Adding composite index on achievements(user_id, category, earned_at)...")
                cursor.execute(
                    "CREATE INDEX ix_achievements_user_category_earned ON achievements(user_id, category, earned_at)"
                )
            
            # Composite index on practice_sessions for test achievements: (user_id, test_type, completed_at)
            cursor.execute("PRAGMA table_info(practice_sessions)")
            session_columns = {row[1] for row in cursor.fetchall()}
            if "test_type" in session_columns and "completed_at" in session_columns:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name='ix_sessions_user_test_completed'"
                )
                if cursor.fetchone() is None:
                    print("Adding composite index on practice_sessions(user_id, test_type, completed_at)...")
                    cursor.execute(
                        "CREATE INDEX ix_sessions_user_test_completed ON practice_sessions(user_id, test_type, completed_at)"
                    )
            
            # Composite index on questions for operation+level queries: (operation, required_level)
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='ix_questions_operation_level'"
            )
            if cursor.fetchone() is None:
                print("Adding composite index on questions(operation, required_level)...")
                cursor.execute(
                    "CREATE INDEX ix_questions_operation_level ON questions(operation, required_level)"
                )
            
            # Composite index on responses for user+question joins: (user_id, question_id, is_correct)
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='ix_responses_user_question_correct'"
            )
            if cursor.fetchone() is None:
                print("Adding composite index on responses(user_id, question_id, is_correct)...")
                cursor.execute(
                    "CREATE INDEX ix_responses_user_question_correct ON responses(user_id, question_id, is_correct)"
                )

            # Create server_records table if it doesn't exist
            if not server_records_exists:
                print("Creating server_records table...")
                cursor.execute(
                    """
                    CREATE TABLE server_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        achievement_type VARCHAR(64) NOT NULL UNIQUE,
                        record_type VARCHAR(32) NOT NULL,
                        record_value REAL NOT NULL,
                        user_id INTEGER NOT NULL,
                        achieved_at DATETIME NOT NULL,
                        session_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (session_id) REFERENCES practice_sessions(id) ON DELETE SET NULL
                    )
                """
                )
                cursor.execute(
                    "CREATE INDEX ix_server_records_achievement_type ON server_records(achievement_type)"
                )
                cursor.execute(
                    "CREATE INDEX ix_server_records_record_type ON server_records(record_type)"
                )
                cursor.execute(
                    "CREATE INDEX ix_server_records_user_id ON server_records(user_id)"
                )

            conn.commit()
            print("Migration completed successfully!")

        except Exception as e:
            conn.rollback()
            print(f"Migration failed: {e}")
            raise
        finally:
            conn.close()

        # Reinitialize with SQLAlchemy to ensure everything is in sync
        db.create_all()
        
        # Populate level configs and progression requirements
        print("Populating level configurations...")
        try:
            LevelConfigService.sync_level_configs_to_database()
            print("Level configurations populated successfully!")
        except Exception as e:
            print(f"Warning: Failed to populate level configurations: {e}")
        
        print("Populating level progression requirements...")
        try:
            LevelConfigService.sync_progression_configs_to_database()
            print("Level progression requirements populated successfully!")
        except Exception as e:
            print(f"Warning: Failed to populate level progression requirements: {e}")


if __name__ == "__main__":
    migrate_database()

