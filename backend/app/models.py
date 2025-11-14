from __future__ import annotations

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    avatar = db.Column(db.String(64), nullable=True)
    display_name = db.Column(db.String(64), nullable=False, unique=True)
    # NOTE: PINs are stored in plain text for local-network prototypes only.
    pin = db.Column(db.String(4), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    responses = db.relationship("Response", back_populates="user", cascade="all, delete")


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    operation = db.Column(db.String(32), nullable=False)
    level_tag = db.Column(db.String(32), nullable=True)
    difficulty = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    responses = db.relationship("Response", back_populates="question", cascade="all, delete")


class Response(db.Model):
    __tablename__ = "responses"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    submitted_answer = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, nullable=True)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    question = db.relationship("Question", back_populates="responses")
    user = db.relationship("User", back_populates="responses")

