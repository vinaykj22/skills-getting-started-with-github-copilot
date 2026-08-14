"""
Pytest configuration and fixtures for Mergington High School Activities API tests.

Fixtures provided:
- client: TestClient for making HTTP requests to the FastAPI app
- reset_activities: Fixture that resets activities to initial state before each test
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provide a TestClient for making requests to the app.
    This fixture is used across all tests.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset activities to initial state before each test.
    This ensures test isolation - tests don't affect each other.
    
    Stores original state before test, restores after test completes.
    """
    # Store original activities state
    original_state = {}
    
    # Deep copy each activity's participant list
    for activity_name, activity_data in activities.items():
        original_state[activity_name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()
        }
    
    yield  # Test runs here
    
    # Restore to original state after test
    for activity_name, activity_data in activities.items():
        activities[activity_name]["participants"] = original_state[activity_name]["participants"].copy()
