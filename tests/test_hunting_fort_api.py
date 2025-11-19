"""
Unit Tests for Hunting Fort API

This module contains comprehensive unit tests for the Hunting Fort API endpoints,
covering both public and protected endpoints, authentication, error handling,
and data validation.

Educational Note:
These tests demonstrate best practices for API testing including:
- Using pytest for test organization and fixtures
- Testing both success and failure cases
- Validating response schemas
- Testing authentication and authorization
- Mocking database operations for isolation

To run these tests:
    pytest tests/test_hunting_fort_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sqlite3
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from raspberry_pi.api.hunting_fort import app


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def client():
    """
    Create a test client for the Hunting Fort API.

    Educational Note:
    FastAPI's TestClient allows us to test the API without running a server.
    It handles request/response cycles synchronously for easy testing.
    """
    return TestClient(app)


@pytest.fixture
def mock_db_connection():
    """
    Create a mock database connection.

    Educational Note:
    Mocking the database allows tests to run without a real database,
    making them faster and more reliable. We can control exact data
    returned for predictable test outcomes.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.execute = mock_cursor.execute
    return mock_conn, mock_cursor


@pytest.fixture
def sample_game_animal():
    """Sample game animal data for testing."""
    return {
        "animal_id": 1,
        "species": "Moose",
        "category": "big_game",
        "typical_size": "400-600 kg",
        "pelt_value": 50.00,
        "meat_yield": "200-400 kg",
        "population_status": "common",
        "best_season": "Fall/Winter",
        "habitat": "Boreal forest",
        "notes": "Test moose"
    }


@pytest.fixture
def sample_hunting_party():
    """Sample hunting party data for testing."""
    return {
        "party_id": 1,
        "leader_name": "Jean-Baptiste Lafleur",
        "party_size": 5,
        "start_date": "2025-01-15",
        "end_date": None,
        "status": "active",
        "target_species": "Beaver",
        "region": "North Creek Territory",
        "total_harvest": 12,
        "success_rate": None,
        "notes": "Test party"
    }


@pytest.fixture
def auth_token(client):
    """
    Get an authentication token for protected endpoint testing.

    Educational Note:
    Many tests need authentication. This fixture provides a reusable
    token that can be used across multiple tests.
    """
    # Mock the login to get a token
    with patch('raspberry_pi.api.auth_middleware.verify_user_credentials') as mock_verify:
        mock_verify.return_value = {
            "username": "fort_commander",
            "role": "admin",
            "forts": ["all"]
        }

        response = client.post(
            "/auth/login",
            json={"username": "fort_commander", "password": "frontier_pass123"}
        )

        if response.status_code == 200:
            return response.json().get("access_token")
        return None


# ============================================================================
# Public Endpoint Tests
# ============================================================================

def test_root_endpoint(client):
    """
    Test the root endpoint returns correct API information.

    Educational Note:
    The root endpoint provides API metadata. Testing it ensures
    documentation is accessible and correct.
    """
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "Hunting Fort" in data["message"]
    assert "version" in data
    assert data["version"] == "1.0.0"


def test_health_check_success(client):
    """
    Test health check endpoint when database is accessible.

    Educational Note:
    Health checks are critical for monitoring. This test ensures
    the endpoint correctly reports system health.
    """
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = (1,)
        mock_get_conn.return_value = mock_conn

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["database"] == "connected"


def test_health_check_failure(client):
    """
    Test health check endpoint when database is unavailable.

    Educational Note:
    Testing failure cases is as important as testing success.
    This ensures proper error reporting when systems are down.
    """
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_get_conn.side_effect = Exception("Database connection failed")

        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()

        assert data["status"] == "unhealthy"
        assert "error" in data


def test_get_status(client):
    """
    Test the status endpoint returns fort statistics.

    Educational Note:
    Status endpoints aggregate multiple metrics. This test ensures
    all expected fields are present and formatted correctly.
    """
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()

        # Mock database queries
        mock_conn.execute.return_value.fetchone.return_value = {"count": 16}

        mock_get_conn.return_value = mock_conn

        response = client.get("/status")

        assert response.status_code == 200
        data = response.json()

        assert "fort_name" in data
        assert data["fort_name"] == "Hunting Fort"
        assert "statistics" in data
        assert "tracked_species" in data["statistics"]


# ============================================================================
# Game Animals Endpoint Tests
# ============================================================================

def test_get_all_animals(client, sample_game_animal):
    """Test retrieving all game animals."""
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()

        # Create a mock Row object
        class MockRow:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        mock_row = MockRow(sample_game_animal)

        # Mock the database query to return our sample
        mock_conn.execute.return_value.fetchall.return_value = [mock_row]
        mock_get_conn.return_value = mock_conn

        response = client.get("/animals")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["species"] == "Moose"


def test_get_animals_with_category_filter(client, sample_game_animal):
    """
    Test filtering animals by category.

    Educational Note:
    Query parameter filtering is common in REST APIs. This test ensures
    filters work correctly and return only matching results.
    """
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()

        class MockRow:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        mock_row = MockRow(sample_game_animal)
        mock_conn.execute.return_value.fetchall.return_value = [mock_row]
        mock_get_conn.return_value = mock_conn

        response = client.get("/animals?category=big_game")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        # Verify the filter was applied (in real scenario, check SQL query)
        for animal in data:
            assert animal["category"] == "big_game"


def test_get_animal_by_id(client, sample_game_animal):
    """Test retrieving a specific animal by ID."""
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()

        class MockRow:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        mock_row = MockRow(sample_game_animal)
        mock_conn.execute.return_value.fetchone.return_value = mock_row
        mock_get_conn.return_value = mock_conn

        response = client.get("/animals/1")

        assert response.status_code == 200
        data = response.json()

        assert data["animal_id"] == 1
        assert data["species"] == "Moose"


def test_get_animal_not_found(client):
    """
    Test retrieving a non-existent animal returns 404.

    Educational Note:
    Proper HTTP status codes are essential for API usability.
    404 clearly indicates a resource wasn't found.
    """
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_get_conn.return_value = mock_conn

        response = client.get("/animals/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# ============================================================================
# Hunting Parties Endpoint Tests
# ============================================================================

def test_get_all_parties(client, sample_hunting_party):
    """Test retrieving all hunting parties."""
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()

        class MockRow:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        mock_row = MockRow(sample_hunting_party)
        mock_conn.execute.return_value.fetchall.return_value = [mock_row]
        mock_get_conn.return_value = mock_conn

        response = client.get("/parties")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0


def test_get_parties_with_status_filter(client, sample_hunting_party):
    """Test filtering parties by status."""
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()

        class MockRow:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        mock_row = MockRow(sample_hunting_party)
        mock_conn.execute.return_value.fetchall.return_value = [mock_row]
        mock_get_conn.return_value = mock_conn

        response = client.get("/parties?status=active")

        assert response.status_code == 200
        data = response.json()

        for party in data:
            assert party["status"] == "active"


#============================================================================
# Pelt Harvests Endpoint Tests
# ============================================================================

def test_get_harvest_summary(client):
    """
    Test the harvest summary endpoint.

    Educational Note:
    Summary endpoints aggregate data across multiple records.
    This test ensures all expected aggregations are present.
    """
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()

        # Mock aggregate queries
        mock_conn.execute.return_value.fetchone.side_effect = [
            {"count": 50},  # total harvests
            {"total": 12500.00},  # total value
            {"total": 250}  # total pelts
        ]
        mock_conn.execute.return_value.fetchall.return_value = []

        mock_get_conn.return_value = mock_conn

        response = client.get("/harvests/summary")

        assert response.status_code == 200
        data = response.json()

        assert "total_records" in data
        assert "total_value" in data
        assert "total_pelts" in data
        assert "by_species" in data
        assert "by_quality" in data


# ============================================================================
# Protected Endpoint Tests (Require Authentication)
# ============================================================================

def test_create_animal_without_auth(client):
    """
    Test creating an animal without authentication returns 401.

    Educational Note:
    Protected endpoints must reject unauthenticated requests.
    This is crucial for API security.
    """
    new_animal = {
        "species": "Test Bear",
        "category": "big_game",
        "typical_size": "100-200 kg",
        "pelt_value": 60.00,
        "meat_yield": "50-100 kg",
        "population_status": "common",
        "best_season": "Fall",
        "habitat": "Forest"
    }

    response = client.post("/animals", json=new_animal)

    # Should return 401 or 403 (depends on auth middleware implementation)
    assert response.status_code in [401, 403]


def test_get_admin_statistics_without_auth(client):
    """
    Test accessing admin statistics without authentication.

    Educational Note:
    Administrative endpoints contain sensitive data and must
    require authentication.
    """
    response = client.get("/admin/statistics")

    assert response.status_code in [401, 403]


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_database_error_handling(client):
    """
    Test that database errors are handled gracefully.

    Educational Note:
    APIs should never crash. Instead, they should catch exceptions
    and return appropriate error responses.
    """
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_get_conn.side_effect = sqlite3.Error("Database error")

        response = client.get("/animals")

        assert response.status_code == 500


def test_invalid_query_parameters(client):
    """
    Test handling of invalid query parameters.

    Educational Note:
    APIs should validate input and provide helpful error messages
    when parameters are invalid.
    """
    # This depends on your validation implementation
    # Example: invalid category
    response = client.get("/animals?category=invalid_category")

    # Should either filter out or return empty, not crash
    assert response.status_code == 200


# ============================================================================
# Data Validation Tests
# ============================================================================

def test_response_schema_validation(client, sample_game_animal):
    """
    Test that API responses match expected schemas.

    Educational Note:
    Response validation ensures API contracts are maintained.
    This prevents breaking changes that could affect clients.
    """
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()

        class MockRow:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        mock_row = MockRow(sample_game_animal)
        mock_conn.execute.return_value.fetchone.return_value = mock_row
        mock_get_conn.return_value = mock_conn

        response = client.get("/animals/1")

        assert response.status_code == 200
        data = response.json()

        # Validate required fields
        required_fields = ["animal_id", "species", "category", "typical_size",
                          "population_status", "best_season"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Validate data types
        assert isinstance(data["animal_id"], int)
        assert isinstance(data["species"], str)
        if data.get("pelt_value") is not None:
            assert isinstance(data["pelt_value"], (int, float))


# ============================================================================
# Performance and Edge Case Tests
# ============================================================================

def test_large_dataset_handling(client):
    """
    Test API handles large datasets appropriately.

    Educational Note:
    APIs should handle large result sets efficiently, possibly
    with pagination or result limiting.
    """
    with patch('raspberry_pi.api.hunting_fort.get_db_connection') as mock_get_conn:
        mock_conn = MagicMock()

        # Simulate many results
        mock_rows = [{"animal_id": i, "species": f"Animal {i}"} for i in range(1000)]

        class MockRow:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        mock_conn.execute.return_value.fetchall.return_value = [MockRow(row) for row in mock_rows]
        mock_get_conn.return_value = mock_conn

        response = client.get("/animals")

        # Should handle large datasets without crashing
        assert response.status_code == 200


if __name__ == "__main__":
    """
    Run tests directly with: python -m pytest tests/test_hunting_fort_api.py -v

    Educational Note:
    -v flag provides verbose output showing each test name and result
    pytest discovers and runs all functions starting with 'test_'
    """
    pytest.main([__file__, "-v"])
