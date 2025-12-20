"""Tests for SessionEngineService (concept-based practice)."""

import pytest

from app import create_app, db
from app.models import User
from app.services.session_engine_service import SessionEngineService


@pytest.fixture
def app():
    app = create_app(test_config={"TESTING": True})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def user(app):
    with app.app_context():
        u = User(display_name="SessionUser", pin="1234", avatar="🐯", level=10, experience=0)
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
        return u


def test_generate_session_with_concept_id_returns_concept_id_and_questions(app, user):
    with app.app_context():
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            concept_id="c_concept_001",
        )

        assert result["session_id"] is not None
        assert result["concept_id"] == "c_concept_001"
        assert result["level"] is not None
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) > 0


def test_generate_session_default_selects_concept(app, user):
    with app.app_context():
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
        )

        assert result["concept_id"] is not None
        assert isinstance(result["concept_id"], str)
        assert result["concept_id"].startswith("c_concept_")
        assert result["level"] is not None
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) > 0

