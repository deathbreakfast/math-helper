"""Tests for /api/levels/requirements endpoint enrichment and metadata translation."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from app import create_app, db
from app.models import Achievement, User


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
        u = User(display_name="ReqUser", pin="1234", avatar="🐯", experience=0)
        db.session.add(u)
        db.session.commit()
        _ = u.id
        return u


def test_levels_requirements_translates_test_type_to_concept_id_and_enriches_counts(app, user):
    """Legacy test_type metadata filters should be translated to concept_id and counted correctly."""
    with app.app_context():
        u = db.session.get(User, user.id)

        # Level 2 progression includes accuracy-ace-gold with legacy test_type "addition-1digit"
        # We create an achievement with concept_id metadata.
        db.session.add(
            Achievement(
                user_id=u.id,
                code="accuracy-ace-gold",
                title="Accuracy Ace (Gold)",
                description="Test",
                icon="🎯",
                category="accuracy",
                earned_at=datetime.utcnow(),
                achievement_metadata=json.dumps({"concept_id": "c_concept_001"}, sort_keys=True),
            )
        )
        db.session.commit()

    with app.test_client() as client:
        resp = client.get(f"/api/levels/requirements?levels=2&user_id={user.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "requirements" in data
        # JSON object keys are strings
        assert "2" in data["requirements"]

        reqs = data["requirements"]["2"]
        assert isinstance(reqs, list)

        # Ensure the legacy test_type isn't leaked and concept_id is present for the translated requirement(s)
        found_translated = False
        for req in reqs:
            mf = req.get("metadata_filter") or {}
            assert "test_type" not in mf
            if req.get("achievement_code") == "accuracy-ace-gold" and mf.get("concept_id") == "c_concept_001":
                found_translated = True
                assert req.get("user_count") is not None
                assert req.get("completed") in (True, False)
        assert found_translated is True


