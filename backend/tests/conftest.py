"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock user data"""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "company_name": "Test Company",
        "company_size": 25,
        "industry": "Software"
    }


@pytest.fixture
def mock_grant():
    """Mock grant data"""
    return {
        "id": "test-grant-id",
        "name": "Test Grant Program",
        "type": "federal",
        "category": "innovation",
        "max_funding": 500000,
        "description": "Test grant description",
        "historical_success_rate": 0.65
    }


@pytest.fixture
def mock_application():
    """Mock application data"""
    return {
        "id": "test-app-id",
        "project_title": "Test Project",
        "project_description": "Test description",
        "total_budget": 300000,
        "requested_funding": 250000,
        "own_contribution": 50000,
        "status": "draft"
    }

