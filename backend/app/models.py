from __future__ import annotations

from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    avatar = db.Column(db.String(64), nullable=True)
    display_name = db.Column(db.String(64), nullable=False, unique=True)
    # NOTE: PINs are stored in plain text for local-network prototypes only.
    pin = db.Column(db.String(4), nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    responses = db.relationship("Response", back_populates="user", cascade="all, delete")
    achievements = db.relationship(
        "Achievement",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Achievement.earned_at.desc()",
    )
    practice_sessions = db.relationship("PracticeSession", back_populates="user", cascade="all, delete")
    flagged_questions = db.relationship("FlaggedQuestion", back_populates="user", cascade="all, delete")
    daily_stats = db.relationship("DailyStat", back_populates="user", cascade="all, delete")


class PracticeSession(db.Model):
    __tablename__ = "practice_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mode = db.Column(db.String(32), nullable=False)  # standard/multiplication/division
    level = db.Column(db.Integer, nullable=True)
    concept_id = db.Column(db.String(64), nullable=True, index=True)  # e.g., "c_concept_001", "c_add_1s"
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    total_questions = db.Column(db.Integer, default=0, nullable=False)
    correct_count = db.Column(db.Integer, default=0, nullable=False)
    accuracy = db.Column(db.Float, default=0.0, nullable=False)
    total_duration_ms = db.Column(db.Integer, nullable=True)
    question_ids = db.Column(db.Text, nullable=True)  # JSON array of question IDs: [1, 2, 3, ...]

    user = db.relationship("User", back_populates="practice_sessions")
    responses = db.relationship("Response", back_populates="session", cascade="all, delete")
    flagged_questions = db.relationship("FlaggedQuestion", back_populates="session", cascade="all, delete")


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    operation = db.Column(db.String(32), nullable=False, index=True)  # addition/subtraction/multiplication/division
    operand1 = db.Column(db.Integer, nullable=False)
    operand2 = db.Column(db.Integer, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(32), nullable=True)  # Level 1, Level 2, etc.
    required_level = db.Column(db.Integer, default=1, nullable=False, index=True)  # minimum level to attempt
    level_tag = db.Column(db.String(32), nullable=True, index=True)
    target_ms = db.Column(db.Integer, nullable=True)
    hint = db.Column(db.Text, nullable=True)
    answer_format = db.Column(db.String(32), nullable=True)  # integer/remainder/fraction/decimal/mixed
    accepted_answers = db.Column(db.Text, nullable=True)  # JSON array
    layout_type = db.Column(db.String(32), nullable=True)  # vertical/horizontal/longDivision/partialProducts/work
    layout_config = db.Column(db.Text, nullable=True)  # JSON for ProblemLayoutConfig
    math_type_label = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    responses = db.relationship("Response", back_populates="question", cascade="all, delete")
    flagged_questions = db.relationship("FlaggedQuestion", back_populates="question", cascade="all, delete")


class Response(db.Model):
    __tablename__ = "responses"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    submitted_answer = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    duration_ms = db.Column(db.Integer, nullable=True)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_flagged = db.Column(db.Boolean, default=False, nullable=False, index=True)

    session = db.relationship("PracticeSession", back_populates="responses")
    question = db.relationship("Question", back_populates="responses")
    user = db.relationship("User", back_populates="responses")


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(8), nullable=False)
    category = db.Column(db.String(64), nullable=False, index=True)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey("practice_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    achievement_metadata = db.Column(db.Text, nullable=True)  # JSON string for level/operation filters

    __table_args__ = (
        db.UniqueConstraint("user_id", "code", "achievement_metadata", name="uq_user_achievement_code_metadata"),
    )

    user = db.relationship("User", back_populates="achievements")
    session = db.relationship("PracticeSession", backref="achievements")


class FlaggedQuestion(db.Model):
    __tablename__ = "flagged_questions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey("practice_sessions.id", ondelete="SET NULL"), nullable=True)
    flagged_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    __table_args__ = (db.UniqueConstraint("user_id", "question_id", "session_id", name="uq_flagged_question"),)

    user = db.relationship("User", back_populates="flagged_questions")
    question = db.relationship("Question", back_populates="flagged_questions")
    session = db.relationship("PracticeSession", back_populates="flagged_questions")


class DailyStat(db.Model):
    __tablename__ = "daily_stats"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    operation = db.Column(db.String(32), nullable=False, index=True)
    questions_answered = db.Column(db.Integer, default=0, nullable=False)
    correct_count = db.Column(db.Integer, default=0, nullable=False)
    accuracy = db.Column(db.Float, default=0.0, nullable=False)
    avg_duration_ms = db.Column(db.Integer, nullable=True)
    avg_speed_seconds = db.Column(db.Float, nullable=True)

    __table_args__ = (db.UniqueConstraint("user_id", "date", "operation", name="uq_daily_stat"),)

    user = db.relationship("User", back_populates="daily_stats")


class LevelProgression(db.Model):
    __tablename__ = "level_progression"

    id = db.Column(db.Integer, primary_key=True)
    target_level = db.Column(db.Integer, nullable=False, index=True)
    required_achievement_code = db.Column(db.String(64), nullable=False)
    order = db.Column(db.Integer, nullable=True)  # for ordering multiple requirements
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint("target_level", "required_achievement_code", name="uq_level_progression"),)


class LevelProblemConfig(db.Model):
    __tablename__ = "level_problem_config"

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False, index=True)
    operation = db.Column(db.String(32), nullable=False, index=True)
    min_operand1 = db.Column(db.Integer, nullable=True)
    max_operand1 = db.Column(db.Integer, nullable=True)
    min_operand2 = db.Column(db.Integer, nullable=True)
    max_operand2 = db.Column(db.Integer, nullable=True)
    layout_types = db.Column(db.Text, nullable=True)  # JSON array of allowed layout types
    answer_formats = db.Column(db.Text, nullable=True)  # JSON array of allowed answer formats
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint("level", "operation", name="uq_level_problem_config"),)


class ServerRecord(db.Model):
    __tablename__ = "server_records"

    id = db.Column(db.Integer, primary_key=True)
    achievement_type = db.Column(db.String(64), nullable=False, unique=True, index=True)
    record_type = db.Column(db.String(32), nullable=False)  # 'speed', 'accuracy', 'volume', 'streak'
    record_value = db.Column(db.Float, nullable=False)  # The actual record value
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("practice_sessions.id", ondelete="SET NULL"), nullable=True)

    user = db.relationship("User", backref="server_records")
    session = db.relationship("PracticeSession", backref="server_records")
