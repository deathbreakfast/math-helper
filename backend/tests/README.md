# Backend Tests

This directory contains backend tests for the Math Helper application.

## Test Organization

Tests are organized by feature area:

- `test_achievement_model.py` - Achievement model tests
- `test_achievement_service_session_tracking.py` - Achievement service with session tracking
- `test_api_protection.py` - API protection tests (TESTING environment variable)
- `test_generic_achievements.py` - Generic achievement system tests
- `test_server_record_service.py` - Server record service tests (Champion tier)
- `test_tests_tab.py` - Test definitions and attempts tests

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_achievement_model.py

# Run specific test
pytest tests/test_achievement_model.py::test_achievement_creation

# Run with verbose output
pytest -v
```

### Coverage Reports

Generate coverage reports using the provided script:

```bash
# Generate HTML and JSON coverage reports
./scripts/generate_coverage_report.sh

# Or run pytest directly with coverage
pytest --cov=app --cov-report=html --cov-report=term tests/
```

Coverage reports are generated in:
- HTML: `backend/coverage/html/index.html`
- JSON: `backend/coverage/coverage.json`

### Coverage Baseline

To generate the coverage baseline:

```bash
pytest tests/test_coverage_baseline.py --cov=app --cov-report=html --cov-report=term
```

Or use the coverage script:

```bash
./scripts/generate_coverage_report.sh
```

## Shared Fixtures

The `conftest.py` file provides shared fixtures for all tests:

### Available Fixtures

- `app` - Flask application with test database
- `test_user` - Basic test user
- `test_user_with_achievements` - Factory for users with achievements
- `test_question` - Basic test question
- `test_session` - Completed practice session with responses
- `test_test_session` - Completed test session
- `cleanup_after_test` - Automatic cleanup (autouse fixture)

### Using Fixtures

```python
def test_my_feature(app, test_user):
    """Test using shared fixtures."""
    with app.app_context():
        # Test logic here
        assert test_user.level == 1
```

### Creating Users with Achievements

```python
def test_with_achievements(app, test_user_with_achievements):
    """Test with user that has achievements."""
    user, achievements = test_user_with_achievements(
        achievement_codes=['addition-basics', 'first-victory'],
        level=2
    )
    
    with app.app_context():
        # Test logic
        assert len(achievements) == 2
```

## Test Configuration

### pytest.ini

Pytest configuration is in `backend/pytest.ini`:

- Test discovery patterns
- Coverage configuration options
- Test markers for categorization

### .coveragerc

Coverage configuration is in `backend/.coveragerc`:

- Source directories to cover
- Files/patterns to omit from coverage
- Report settings
- HTML report settings

## Test Patterns

### Basic Test Structure

```python
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_user_creation(app):
    """Test user creation."""
    with app.app_context():
        user = User(display_name="Test", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.level == 1
```

### Testing Services

```python
def test_achievement_service(app, test_user, test_session):
    """Test achievement service."""
    from app.services.achievement_service import AchievementService
    
    with app.app_context():
        service = AchievementService()
        achievements = service.check_achievements(test_user.id, test_session.id)
        
        assert len(achievements) > 0
```

### Testing API Endpoints

```python
def test_api_endpoint(app, test_user):
    """Test API endpoint."""
    with app.test_client() as client:
        response = client.get(f'/api/users/{test_user.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_user.id
```

## Coverage Baseline

The coverage baseline is informational - it documents the current test coverage state. It does not enforce specific coverage thresholds.

### Generating Baseline

1. Run all tests with coverage
2. Review the HTML report in `backend/coverage/html/index.html`
3. Document coverage percentages by module/function
4. Use as reference for tracking coverage improvements

### Coverage Goals

- Establish baseline metrics (no specific targets)
- Track coverage improvements over time
- Identify areas needing more test coverage

## Best Practices

1. **Use Shared Fixtures**: Leverage `conftest.py` fixtures instead of duplicating setup code
2. **Test Isolation**: Each test should be independent and not rely on other tests
3. **Cleanup**: Use fixtures with proper teardown (handled automatically)
4. **App Context**: Always use `app.app_context()` when accessing database
5. **Clear Test Names**: Use descriptive test names that explain what is being tested
6. **Test Organization**: Group related tests in the same file
7. **Coverage**: Aim for high coverage but focus on meaningful tests, not just numbers

## Dependencies

Required packages (see `requirements.txt`):

- `pytest` - Testing framework
- `pytest-cov` - Coverage plugin

Install dependencies:

```bash
pip install -r requirements.txt
```

## Continuous Integration

Tests should run in CI/CD pipelines. The coverage baseline can be used to track coverage trends over time.

