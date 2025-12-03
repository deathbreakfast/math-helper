"""Backend tests for API protection with TESTING environment variable.

Tests verify that test setup APIs are protected and only available when TESTING=true.
"""

import pytest

from app import create_app, db
from app.models import User


@pytest.fixture
def app_with_testing():
    """Create Flask app with TESTING=true."""
    app = create_app(test_config={'TESTING': True})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def app_without_testing():
    """Create Flask app with TESTING=false."""
    app = create_app(test_config={'TESTING': False})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user(app_with_testing):
    """Create a test user."""
    with app_with_testing.app_context():
        user = User(display_name="TestUser", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        return user


def test_api_protection_001_test_setup_with_testing_enabled(app_with_testing, test_user):
    """API-PROT-001: Test setup endpoint works when TESTING=true."""
    with app_with_testing.test_client() as client:
        response = client.post(
            f'/api/users/{test_user.id}/test-setup',
            json={'level': 5}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['level'] == 5


def test_api_protection_002_test_setup_with_testing_disabled(app_without_testing):
    """API-PROT-002: Test setup endpoint returns 403 when TESTING=false."""
    # Create user in app_without_testing context
    with app_without_testing.app_context():
        user = User(display_name="TestUser", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    with app_without_testing.test_client() as client:
        response = client.post(
            f'/api/users/{user_id}/test-setup',
            json={'level': 5}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Not available in production' in data['error']


def test_api_protection_003_reset_user_with_testing_enabled(app_with_testing, test_user):
    """API-PROT-003: Reset user endpoint works when TESTING=true."""
    with app_with_testing.test_client() as client:
        response = client.delete(f'/api/users/{test_user.id}/reset')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


def test_api_protection_004_reset_user_with_testing_disabled(app_without_testing):
    """API-PROT-004: Reset user endpoint returns 403 when TESTING=false."""
    # Create user in app_without_testing context
    with app_without_testing.app_context():
        user = User(display_name="TestUser", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    with app_without_testing.test_client() as client:
        response = client.delete(f'/api/users/{user_id}/reset')
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Not available in production' in data['error']


def test_api_protection_005_delete_user_with_testing_enabled(app_with_testing, test_user):
    """API-PROT-005: Delete user endpoint works when TESTING=true."""
    with app_with_testing.test_client() as client:
        response = client.delete(f'/api/users/{test_user.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


def test_api_protection_006_delete_user_with_testing_disabled(app_without_testing):
    """API-PROT-006: Delete user endpoint returns 403 when TESTING=false."""
    # Create user in app_without_testing context
    with app_without_testing.app_context():
        user = User(display_name="TestUser", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    with app_without_testing.test_client() as client:
        response = client.delete(f'/api/users/{user_id}')
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Not available in production' in data['error']


def test_api_protection_007_reset_all_with_testing_enabled(app_with_testing):
    """API-PROT-007: Reset all data endpoint works when TESTING=true."""
    with app_with_testing.test_client() as client:
        response = client.delete('/api/reset')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


def test_api_protection_008_reset_all_with_testing_disabled(app_without_testing):
    """API-PROT-008: Reset all data endpoint returns 403 when TESTING=false."""
    with app_without_testing.test_client() as client:
        response = client.delete('/api/reset')
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Not available in production' in data['error']


def test_api_protection_009_default_testing_is_true():
    """API-PROT-009: Default TESTING config is True (until v1.0)."""
    # Create app without test_config to test default
    app = create_app()
    assert app.config.get('TESTING') is True


def test_api_protection_010_test_setup_awards_achievements_with_testing(app_with_testing, test_user):
    """API-PROT-010: Test setup can award achievements when TESTING=true."""
    with app_with_testing.test_client() as client:
        response = client.post(
            f'/api/users/{test_user.id}/test-setup',
            json={'achievements': ['first-steps']}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
