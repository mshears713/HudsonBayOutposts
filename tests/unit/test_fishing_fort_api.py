"""
Unit Tests for Fishing Fort API

Educational Note:
These tests verify individual API endpoints work correctly in isolation.
We use pytest and FastAPI's TestClient to simulate HTTP requests without
needing a running server.

Key Testing Concepts:
- Fixtures provide reusable test data and setup
- Mocking isolates code from external dependencies (like databases)
- Parametrize allows testing multiple scenarios efficiently
- Each test should be independent and repeatable

To run these tests:
    pytest tests/unit/test_fishing_fort_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import sqlite3
from datetime import datetime

# Import the app
from raspberry_pi.api.fishing_fort import app, get_db_connection, dict_from_row


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def client():
    """
    Create a test client for the Fishing Fort API.

    Educational Note:
    TestClient simulates HTTP requests without starting a real server.
    It's faster and more reliable for unit testing.
    """
    return TestClient(app)


@pytest.fixture
def mock_db_connection():
    """
    Create a mock database connection.

    Educational Note:
    Mocking the database allows tests to run without an actual database,
    making them faster and more isolated.
    """
    mock_conn = MagicMock(spec=sqlite3.Connection)
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.row_factory = sqlite3.Row
    return mock_conn, mock_cursor


@pytest.fixture
def sample_inventory_item():
    """Sample inventory item for testing."""
    return {
        "item_id": 1,
        "name": "Fishing Line",
        "category": "supplies",
        "quantity": 500,
        "unit": "feet",
        "value": 25.0,
        "description": "Braided hemp line",
        "last_updated": datetime.now().isoformat()
    }


@pytest.fixture
def sample_catch_record():
    """Sample catch record for testing."""
    return {
        "catch_id": 1,
        "fish_type": "salmon",
        "quantity": 10,
        "weight_pounds": 85.5,
        "catch_date": "2025-01-15",
        "location": "Northern River",
        "fisher_name": "John",
        "quality": "excellent",
        "notes": "Great catch",
        "created_at": datetime.now().isoformat()
    }


@pytest.fixture
def auth_token():
    """
    Generate a valid authentication token for testing protected endpoints.

    Educational Note:
    Protected endpoints require authentication. This fixture provides
    a valid token for testing those endpoints.
    """
    from raspberry_pi.api.auth_middleware import create_access_token

    token = create_access_token(
        data={
            "sub": "fort_commander",
            "role": "admin",
            "fort": "all"
        }
    )
    return token


# ============================================================================
# Root and Health Endpoints Tests
# ============================================================================

def test_root_endpoint(client):
    """
    Test the root endpoint returns API information.

    Educational Note:
    The root endpoint should provide basic API metadata and
    links to documentation and key resources.
    """
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "outpost" in data
    assert "documentation" in data
    assert "endpoints" in data
    assert data["outpost"] == "Hudson Bay Company - Fishing Fort"


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_health_check_success(mock_db_func, client, mock_db_connection):
    """
    Test health check endpoint when database is accessible.

    Educational Note:
    Health checks verify the API and its dependencies (like the database)
    are functioning properly. This is essential for monitoring.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock successful database query
    mock_cursor.fetchone.return_value = [10]  # 10 items in inventory

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "inventory_items" in data
    assert "timestamp" in data


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_health_check_failure(mock_db_func, client):
    """
    Test health check when database is unavailable.

    Educational Note:
    Proper error handling in health checks helps quickly identify
    system issues in production.
    """
    # Simulate database connection failure
    mock_db_func.side_effect = Exception("Database connection failed")

    response = client.get("/health")

    assert response.status_code == 500
    assert "Health check failed" in response.json()["detail"]


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_get_outpost_status(mock_db_func, client, mock_db_connection):
    """Test the outpost status endpoint."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock database responses
    mock_cursor.fetchone.side_effect = [
        (15, 1500.0),  # inventory count and value
        (25,),         # recent catches count
    ]

    response = client.get("/status")

    assert response.status_code == 200
    data = response.json()

    assert data["outpost_name"] == "Fishing Fort"
    assert data["outpost_type"] == "fishing"
    assert data["status"] == "operational"
    assert data["total_inventory_items"] == 15
    assert data["total_inventory_value"] == 1500.0
    assert data["recent_catches_count"] == 25


# ============================================================================
# Inventory Endpoints Tests
# ============================================================================

@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_get_inventory_all_items(mock_db_func, client, mock_db_connection, sample_inventory_item):
    """
    Test retrieving all inventory items.

    Educational Note:
    This tests the GET /inventory endpoint without filters.
    We mock the database to return sample data.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Create a mock Row object
    mock_row = Mock(spec=sqlite3.Row)
    mock_row.keys.return_value = sample_inventory_item.keys()
    for key, value in sample_inventory_item.items():
        mock_row.__getitem__ = Mock(side_effect=lambda k: sample_inventory_item[k])

    # Mock database returning sample items
    mock_cursor.fetchall.return_value = [mock_row]

    response = client.get("/inventory")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_get_inventory_with_category_filter(mock_db_func, client, mock_db_connection):
    """Test filtering inventory by category."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/inventory?category=supplies")

    assert response.status_code == 200

    # Verify the SQL query was called with category filter
    call_args = mock_cursor.execute.call_args[0]
    assert "category = ?" in call_args[0]
    assert "supplies" in call_args[1]


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_get_inventory_item_by_id(mock_db_func, client, mock_db_connection, sample_inventory_item):
    """Test retrieving a specific inventory item by ID."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Create mock Row object
    mock_row = Mock(spec=sqlite3.Row)
    mock_row.keys.return_value = sample_inventory_item.keys()
    for key, value in sample_inventory_item.items():
        setattr(mock_row, key, value)

    def getitem(key):
        return sample_inventory_item[key]
    mock_row.__getitem__ = getitem

    mock_cursor.fetchone.return_value = mock_row

    response = client.get("/inventory/1")

    assert response.status_code == 200
    data = response.json()

    assert data["item_id"] == 1
    assert data["name"] == "Fishing Line"


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_get_inventory_item_not_found(mock_db_func, client, mock_db_connection):
    """
    Test retrieving non-existent inventory item returns 404.

    Educational Note:
    Proper HTTP status codes are important for API usability.
    404 indicates the resource doesn't exist.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchone.return_value = None

    response = client.get("/inventory/999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_create_inventory_item(mock_db_func, client, mock_db_connection, sample_inventory_item):
    """
    Test creating a new inventory item.

    Educational Note:
    POST requests create new resources. We test that:
    1. Request is processed correctly
    2. Returns 201 (Created) status
    3. Returns the created item with generated ID
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock the ID generation
    mock_cursor.lastrowid = 42

    # Mock fetching the created item
    mock_row = Mock(spec=sqlite3.Row)
    mock_row.keys.return_value = sample_inventory_item.keys()
    mock_row.__getitem__ = lambda self, key: sample_inventory_item[key]
    mock_cursor.fetchone.return_value = mock_row

    new_item = {
        "name": "New Fishing Rod",
        "category": "tools",
        "quantity": 10,
        "unit": "piece",
        "value": 50.0,
        "description": "High quality rod"
    }

    response = client.post("/inventory", json=new_item)

    assert response.status_code == 201
    data = response.json()

    assert "item_id" in data


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_update_inventory_item(mock_db_func, client, mock_db_connection, sample_inventory_item):
    """Test updating an existing inventory item."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock item exists check
    mock_cursor.fetchone.side_effect = [
        Mock(spec=sqlite3.Row),  # Item exists
        Mock(spec=sqlite3.Row, keys=lambda: sample_inventory_item.keys(),
             __getitem__=lambda self, key: sample_inventory_item[key])  # Updated item
    ]

    update_data = {
        "quantity": 600
    }

    response = client.put("/inventory/1", json=update_data)

    assert response.status_code == 200


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_update_nonexistent_inventory_item(mock_db_func, client, mock_db_connection):
    """Test updating non-existent item returns 404."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchone.return_value = None

    update_data = {"quantity": 600}
    response = client.put("/inventory/999", json=update_data)

    assert response.status_code == 404


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_delete_inventory_item(mock_db_func, client, mock_db_connection):
    """
    Test deleting an inventory item.

    Educational Note:
    DELETE requests return 204 (No Content) on success.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.rowcount = 1  # One row deleted

    response = client.delete("/inventory/1")

    assert response.status_code == 204


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_delete_nonexistent_inventory_item(mock_db_func, client, mock_db_connection):
    """Test deleting non-existent item returns 404."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.rowcount = 0  # No rows deleted

    response = client.delete("/inventory/999")

    assert response.status_code == 404


# ============================================================================
# Catch Records Endpoints Tests
# ============================================================================

@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_get_catch_records(mock_db_func, client, mock_db_connection):
    """Test retrieving catch records."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/catches")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_get_catch_records_with_filter(mock_db_func, client, mock_db_connection):
    """Test filtering catch records by fish type."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/catches?fish_type=salmon")

    assert response.status_code == 200

    # Verify filter was applied
    call_args = mock_cursor.execute.call_args[0]
    assert "fish_type = ?" in call_args[0]


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_get_catch_summary(mock_db_func, client, mock_db_connection):
    """
    Test catch summary statistics endpoint.

    Educational Note:
    Summary endpoints aggregate data server-side, which is more
    efficient than returning all records and aggregating client-side.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock aggregated results
    mock_cursor.fetchall.return_value = []

    response = client.get("/catches/summary")

    assert response.status_code == 200
    data = response.json()

    assert "summary" in data
    assert "total_types" in data
    assert "timestamp" in data


# ============================================================================
# File Operations Tests
# ============================================================================

@patch('raspberry_pi.api.fishing_fort.UPLOAD_DIR')
def test_upload_file(mock_upload_dir, client, tmp_path):
    """
    Test file upload endpoint.

    Educational Note:
    File uploads use multipart/form-data encoding.
    We test file size limits and successful uploads.
    """
    mock_upload_dir.__truediv__ = lambda self, name: tmp_path / name

    # Create a small test file
    test_file_content = b"Test file content"
    files = {"file": ("test.txt", test_file_content, "text/plain")}

    response = client.post("/files/upload", files=files)

    assert response.status_code == 200
    data = response.json()

    assert data["filename"] == "test.txt"
    assert data["size_bytes"] == len(test_file_content)


def test_upload_file_too_large(client):
    """Test that files exceeding size limit are rejected."""
    # Create a file larger than 10MB
    large_content = b"x" * (11 * 1024 * 1024)  # 11 MB
    files = {"file": ("large.bin", large_content, "application/octet-stream")}

    response = client.post("/files/upload", files=files)

    assert response.status_code == 413  # Payload Too Large
    assert "too large" in response.json()["detail"].lower()


# ============================================================================
# Authentication Tests
# ============================================================================

@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_protected_endpoint_without_auth(mock_db_func, client):
    """
    Test that protected endpoints reject unauthenticated requests.

    Educational Note:
    Protected endpoints should return 401 (Unauthorized) when
    no valid authentication token is provided.
    """
    response = client.delete("/inventory/1/protected")

    assert response.status_code == 403  # Forbidden - no credentials


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_protected_endpoint_with_auth(mock_db_func, client, mock_db_connection, auth_token):
    """Test protected endpoint with valid authentication."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock item exists
    mock_cursor.fetchone.return_value = Mock(spec=sqlite3.Row)

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.delete("/inventory/1/protected", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "deleted_by" in data


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_admin_stats_endpoint(mock_db_func, client, mock_db_connection, auth_token):
    """Test admin statistics endpoint requires authentication."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock database stats
    mock_cursor.fetchone.side_effect = [
        Mock(spec=sqlite3.Row, keys=lambda: ["total_items", "total_quantity", "total_value", "unique_categories"],
             __getitem__=lambda self, k: {"total_items": 10, "total_quantity": 100,
                                          "total_value": 500.0, "unique_categories": 3}[k]),
        Mock(spec=sqlite3.Row, keys=lambda: ["total_catches", "total_fish", "total_weight", "unique_species"],
             __getitem__=lambda self, k: {"total_catches": 5, "total_fish": 50,
                                          "total_weight": 200.0, "unique_species": 4}[k]),
        (1024*1024,)  # DB size
    ]

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/admin/stats", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert "inventory" in data
    assert "catches" in data
    assert "database" in data
    assert "system" in data


# ============================================================================
# Data Synchronization Tests
# ============================================================================

@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_export_inventory_for_sync(mock_db_func, client, mock_db_connection, auth_token):
    """
    Test exporting inventory for synchronization.

    Educational Note:
    Data sync between distributed systems requires exporting data
    in a standardized format that other nodes can import.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/sync/export-inventory", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["source_fort"] == "fishing_fort"
    assert "export_timestamp" in data
    assert "inventory" in data
    assert "sync_format_version" in data


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_import_inventory_from_sync(mock_db_func, client, mock_db_connection, auth_token):
    """Test importing inventory from another fort."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock database operations
    mock_cursor.fetchone.return_value = None  # No existing items

    sync_data = {
        "source_fort": "trading_fort",
        "inventory": [
            {
                "name": "Trade Goods",
                "category": "supplies",
                "quantity": 50,
                "unit": "units",
                "value": 100.0,
                "description": "Imported goods"
            }
        ]
    }

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/sync/import-inventory", json=sync_data, headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "statistics" in data


def test_get_sync_status(client):
    """Test sync status endpoint."""
    response = client.get("/sync/status")

    assert response.status_code == 200
    data = response.json()

    assert data["fort_name"] == "fishing_fort"
    assert data["sync_enabled"] == True
    assert "supported_operations" in data


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_invalid_endpoint_returns_404(client):
    """Test that invalid endpoints return 404."""
    response = client.get("/nonexistent-endpoint")

    assert response.status_code == 404


@patch('raspberry_pi.api.fishing_fort.get_db_connection')
def test_database_error_handling(mock_db_func, client):
    """
    Test that database errors are handled gracefully.

    Educational Note:
    Robust error handling prevents exposing internal errors to clients
    and provides meaningful error messages.
    """
    mock_db_func.side_effect = Exception("Database error")

    response = client.get("/inventory")

    assert response.status_code == 500
    assert "Failed to fetch inventory" in response.json()["detail"]


# ============================================================================
# Input Validation Tests
# ============================================================================

def test_create_inventory_invalid_data(client):
    """
    Test that invalid input data is rejected.

    Educational Note:
    Pydantic models automatically validate input.
    Invalid data returns 422 (Unprocessable Entity).
    """
    invalid_item = {
        "name": "",  # Empty name (invalid)
        "category": "supplies",
        "quantity": -5,  # Negative quantity (invalid)
        "unit": "pieces",
        "value": -10.0  # Negative value (invalid)
    }

    response = client.post("/inventory", json=invalid_item)

    assert response.status_code == 422  # Validation error


@pytest.mark.parametrize("field,value", [
    ("quantity", -1),
    ("quantity", "not a number"),
    ("value", -5.0),
    ("name", ""),
])
def test_create_inventory_field_validation(client, field, value):
    """
    Test field validation using parameterized tests.

    Educational Note:
    Parametrized tests allow testing multiple scenarios
    with the same test logic, improving test coverage.
    """
    item_data = {
        "name": "Test Item",
        "category": "supplies",
        "quantity": 10,
        "unit": "pieces",
        "value": 5.0
    }
    item_data[field] = value

    response = client.post("/inventory", json=item_data)

    assert response.status_code == 422
