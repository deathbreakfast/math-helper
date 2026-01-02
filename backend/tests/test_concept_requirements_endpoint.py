"""Tests for /api/concepts/requirements endpoint."""

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
        u = User(display_name="ConceptReqUser", pin="1234", avatar="🐯", level=1)
        db.session.add(u)
        db.session.commit()
        _ = u.id
        return u


def test_concepts_requirements_enriches_counts_for_descriptive_concepts(app, user):
    with app.app_context():
        # Satisfy the first requirement for c_add_2s: level-master-bronze with concept_id c_add_1s
        db.session.add(
            Achievement(
                user_id=user.id,
                code="level-master-bronze",
                title="Level Master (Bronze)",
                description="Test",
                icon="🎯",
                category="accuracy",
                earned_at=datetime.utcnow(),
                achievement_metadata=json.dumps({"concept_id": "c_add_1s"}, sort_keys=True),
            )
        )
        db.session.commit()

    with app.test_client() as client:
        resp = client.get(f"/api/concepts/requirements?concept_ids=c_add_2s&user_id={user.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "requirements" in data
        assert "c_add_2s" in data["requirements"]

        reqs = data["requirements"]["c_add_2s"]
        assert isinstance(reqs, list)
        assert len(reqs) >= 1

        # Should include enriched fields
        assert any(r.get("achievement_code") == "level-master-bronze" and r.get("user_count") == 1 for r in reqs)


def test_concepts_requirements_uses_explicit_overrides_for_legacy_concepts(app, user):
    """Legacy concepts can have explicit unlock requirements that override level-progression defaults."""
    with app.test_client() as client:
        resp = client.get(f"/api/concepts/requirements?concept_ids=c_concept_001&user_id={user.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        reqs = data["requirements"]["c_concept_001"]
        # From MATH_CONCEPTS.md: requires level-master-bronze with concept_id c_add_9s, plus master-of-basic-addition-bronze
        assert any(
            r.get("achievement_code") == "level-master-bronze"
            and (r.get("metadata_filter") or {}).get("concept_id") == "c_add_9s"
            for r in reqs
        )
        assert any(r.get("achievement_code") == "master-of-basic-addition-bronze" for r in reqs)







