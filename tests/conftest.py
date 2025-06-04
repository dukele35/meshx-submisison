import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing."""
    return "name,age,salary\nJohn,30,50000\nJane,25,45000"


@pytest.fixture
def empty_csv_content():
    """Empty CSV content for testing."""
    return ""