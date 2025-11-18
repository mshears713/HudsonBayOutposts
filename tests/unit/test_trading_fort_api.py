"""
Unit Tests for Trading Fort API

Educational Note:
These tests verify the Trading Fort API endpoints, which demonstrate
authentication-first design and complex data relationships.

Testing Focus:
- Goods management (CRUD operations)
- Trader registry
- Trade records and transactions
- Price history tracking
- Authentication requirements

To run these tests:
    pytest tests/unit/test_trading_fort_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import sqlite3
from datetime import datetime

from raspberry_pi.api.trading_fort import app


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def client():
    """Create a test client for the Trading Fort API."""
    return TestClient(app)


@pytest.fixture
def mock_db_connection():
    """Create a mock database connection."""
    mock_conn = MagicMock(spec=sqlite3.Connection)
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.row_factory = sqlite3.Row
    return mock_conn, mock_cursor


@pytest.fixture
def sample_good():
    """Sample trade good for testing."""
    return {
        "good_id": 1,
        "name": "Beaver Pelt",
        "category": "furs",
        "quantity": 150,
        "unit": "pelt",
        "base_price": 25.00,
        "current_price": 28.50,
        "quality": "excellent",
        "origin": "Northern Territories",
        "description": "Prime winter beaver",
        "last_updated": datetime.now().isoformat()
    }


@pytest.fixture
def sample_trader():
    """Sample trader for testing."""
    return {
        "trader_id": 1,
        "name": "John MacTavish",
        "trader_type": "trapper",
        "reputation": "excellent",
        "total_trades": 25,
        "total_value": 5000.0,
        "credit_limit": 1000.0,
        "last_trade_date": "2025-01-15",
        "notes": "Reliable trader",
        "registered_date": "2024-01-01"
    }


@pytest.fixture
def sample_trade_record():
    """Sample trade record for testing."""
    return {
        "trade_id": 1,
        "good_id": 1,
        "trader_id": 1,
        "trade_type": "buy",
        "quantity": 10,
        "price_per_unit": 28.50,
        "total_value": 285.0,
        "trade_date": "2025-01-15",
        "payment_method": "credit",
        "notes": "Good quality pelts",
        "created_at": datetime.now().isoformat()
    }


@pytest.fixture
def auth_token():
    """Generate a valid authentication token for testing."""
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
# Health and Status Endpoints Tests
# ============================================================================

def test_health_check(client):
    """
    Test the health check endpoint.

    Educational Note:
    Health checks should be fast and reliable, providing
    a quick way to verify the service is running.
    """
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "Trading Fort API"
    assert "version" in data
    assert "timestamp" in data


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_status(mock_db_func, client, mock_db_connection):
    """
    Test the status endpoint returns summary statistics.

    Educational Note:
    Status endpoints aggregate data from multiple tables,
    providing a high-level overview of the system state.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock database responses for stats
    def mock_row(data):
        row = Mock(spec=sqlite3.Row)
        row.keys.return_value = data.keys()
        row.__getitem__ = lambda self, key: data[key]
        row.get = lambda key, default=None: data.get(key, default)
        return row

    mock_cursor.fetchone.side_effect = [
        mock_row({"total_goods": 50, "total_value": 10000.0}),
        mock_row({"total_traders": 15}),
        mock_row({"total_trades": 100, "total_trade_value": 25000.0})
    ]

    response = client.get("/status")

    assert response.status_code == 200
    data = response.json()

    assert data["total_goods"] == 50
    assert data["total_goods_value"] == 10000.0
    assert data["total_traders"] == 15
    assert data["total_trades"] == 100


# ============================================================================
# Goods Endpoints Tests
# ============================================================================

@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_goods(mock_db_func, client, mock_db_connection):
    """Test retrieving all goods."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/goods")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_goods_with_category_filter(mock_db_func, client, mock_db_connection):
    """
    Test filtering goods by category.

    Educational Note:
    Query parameters allow flexible filtering without creating
    separate endpoints for each filter combination.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/goods?category=furs")

    assert response.status_code == 200

    # Verify SQL includes category filter
    call_args = mock_cursor.execute.call_args[0]
    assert "category = ?" in call_args[0]
    assert "furs" in call_args[1]


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_goods_with_quality_filter(mock_db_func, client, mock_db_connection):
    """Test filtering goods by quality."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/goods?quality=excellent")

    assert response.status_code == 200

    call_args = mock_cursor.execute.call_args[0]
    assert "quality = ?" in call_args[0]


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_good_by_id(mock_db_func, client, mock_db_connection, sample_good):
    """Test retrieving a specific good by ID."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Create mock Row
    mock_row = Mock(spec=sqlite3.Row)
    mock_row.keys.return_value = sample_good.keys()
    mock_row.__getitem__ = lambda self, key: sample_good[key]

    mock_cursor.fetchone.return_value = mock_row

    response = client.get("/goods/1")

    assert response.status_code == 200
    data = response.json()

    assert data["good_id"] == 1
    assert data["name"] == "Beaver Pelt"
    assert data["category"] == "furs"


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_good_not_found(mock_db_func, client, mock_db_connection):
    """Test retrieving non-existent good returns 404."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchone.return_value = None

    response = client.get("/goods/999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_create_good_requires_authentication(mock_db_func, client):
    """
    Test that creating goods requires authentication.

    Educational Note:
    Protected endpoints should reject requests without valid tokens.
    This is a key security feature of the Trading Fort API.
    """
    new_good = {
        "name": "Fox Pelt",
        "category": "furs",
        "quantity": 25,
        "unit": "pelt",
        "base_price": 15.00,
        "current_price": 18.00,
        "quality": "good"
    }

    response = client.post("/goods", json=new_good)

    assert response.status_code == 403  # Forbidden - no auth


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_create_good_with_authentication(mock_db_func, client, mock_db_connection, auth_token, sample_good):
    """Test creating a good with valid authentication."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.lastrowid = 42

    # Mock fetching created good
    mock_row = Mock(spec=sqlite3.Row)
    mock_row.keys.return_value = sample_good.keys()
    mock_row.__getitem__ = lambda self, key: sample_good[key]
    mock_cursor.fetchone.return_value = mock_row

    new_good = {
        "name": "Fox Pelt",
        "category": "furs",
        "quantity": 25,
        "unit": "pelt",
        "base_price": 15.00,
        "current_price": 18.00,
        "quality": "good"
    }

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/goods", json=new_good, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert "good_id" in data


# ============================================================================
# Traders Endpoints Tests
# ============================================================================

@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_traders(mock_db_func, client, mock_db_connection):
    """Test retrieving all traders."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/traders")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_traders_with_type_filter(mock_db_func, client, mock_db_connection):
    """
    Test filtering traders by type.

    Educational Note:
    Different trader types (trapper, merchant, etc.) have different
    characteristics. Filtering helps manage these distinctions.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/traders?trader_type=trapper")

    assert response.status_code == 200

    call_args = mock_cursor.execute.call_args[0]
    assert "trader_type = ?" in call_args[0]


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_trader_by_id(mock_db_func, client, mock_db_connection, sample_trader):
    """Test retrieving a specific trader by ID."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_row = Mock(spec=sqlite3.Row)
    mock_row.keys.return_value = sample_trader.keys()
    mock_row.__getitem__ = lambda self, key: sample_trader[key]

    mock_cursor.fetchone.return_value = mock_row

    response = client.get("/traders/1")

    assert response.status_code == 200
    data = response.json()

    assert data["trader_id"] == 1
    assert data["name"] == "John MacTavish"
    assert data["trader_type"] == "trapper"


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_trader_not_found(mock_db_func, client, mock_db_connection):
    """Test retrieving non-existent trader returns 404."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchone.return_value = None

    response = client.get("/traders/999")

    assert response.status_code == 404


# ============================================================================
# Trade Records Endpoints Tests
# ============================================================================

@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_trades(mock_db_func, client, mock_db_connection):
    """Test retrieving trade records."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/trades")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_trades_with_type_filter(mock_db_func, client, mock_db_connection):
    """
    Test filtering trades by type.

    Educational Note:
    Trade types (buy/sell/exchange) represent different transaction
    flows and need separate tracking for accounting.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/trades?trade_type=buy")

    assert response.status_code == 200

    call_args = mock_cursor.execute.call_args[0]
    assert "trade_type = ?" in call_args[0]


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_trades_by_trader(mock_db_func, client, mock_db_connection):
    """Test filtering trades by trader ID."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/trades?trader_id=5")

    assert response.status_code == 200

    call_args = mock_cursor.execute.call_args[0]
    assert "trader_id = ?" in call_args[0]


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_trade_summary(mock_db_func, client, mock_db_connection):
    """
    Test trade summary statistics.

    Educational Note:
    Aggregated summaries help understand trading patterns
    and business performance over time.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock aggregated results by trade type
    mock_cursor.fetchall.return_value = [
        ("buy", 50, 5000.0, 100.0),
        ("sell", 30, 3000.0, 100.0)
    ]

    response = client.get("/trades/summary")

    assert response.status_code == 200
    data = response.json()

    assert "summary_by_type" in data
    assert "timestamp" in data


# ============================================================================
# Price History Tests
# ============================================================================

@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_price_history(mock_db_func, client, mock_db_connection):
    """
    Test retrieving price history for a good.

    Educational Note:
    Price history tracking helps identify market trends,
    seasonal variations, and optimal trading times.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    # Mock good exists
    mock_cursor.fetchone.side_effect = [
        ("Beaver Pelt",),  # Good name
    ]

    # Mock price history
    mock_cursor.fetchall.return_value = [
        (28.50, "2025-01-15", "stable"),
        (27.00, "2025-01-14", "stable"),
        (29.00, "2025-01-13", "rising")
    ]

    response = client.get("/goods/1/price-history")

    assert response.status_code == 200
    data = response.json()

    assert data["good_id"] == 1
    assert "good_name" in data
    assert "history" in data
    assert isinstance(data["history"], list)


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_price_history_for_nonexistent_good(mock_db_func, client, mock_db_connection):
    """Test price history for non-existent good returns 404."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchone.return_value = None

    response = client.get("/goods/999/price-history")

    assert response.status_code == 404


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_price_history_with_custom_days(mock_db_func, client, mock_db_connection):
    """Test retrieving custom number of days of price history."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchone.side_effect = [("Beaver Pelt",)]
    mock_cursor.fetchall.return_value = []

    response = client.get("/goods/1/price-history?days=90")

    assert response.status_code == 200

    # Verify days parameter was used
    call_args = mock_cursor.execute.call_args_list[1][0]  # Second call
    assert 90 in call_args[1]


# ============================================================================
# Input Validation Tests
# ============================================================================

def test_create_good_invalid_category(client, auth_token):
    """
    Test that invalid good data is rejected.

    Educational Note:
    Pydantic validation ensures data integrity at the API boundary,
    preventing invalid data from reaching the database.
    """
    invalid_good = {
        "name": "Test Good",
        "category": "furs",
        "quantity": -5,  # Invalid: negative quantity
        "unit": "pelt",
        "base_price": 10.0,
        "current_price": 12.0
    }

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/goods", json=invalid_good, headers=headers)

    assert response.status_code == 422  # Validation error


@pytest.mark.parametrize("quality", ["poor", "fair", "good", "excellent"])
def test_good_quality_validation(quality, client, auth_token, mock_db_connection):
    """
    Test quality field accepts only valid values.

    Educational Note:
    Parameterized tests efficiently verify all valid enum values.
    """
    with patch('raspberry_pi.api.trading_fort.get_db_connection') as mock_db:
        mock_db.return_value = mock_db_connection[0]
        mock_db_connection[1].lastrowid = 1
        mock_db_connection[1].fetchone.return_value = None

        good_data = {
            "name": "Test Good",
            "category": "furs",
            "quantity": 10,
            "unit": "pelt",
            "base_price": 10.0,
            "current_price": 12.0,
            "quality": quality
        }

        headers = {"Authorization": f"Bearer {auth_token}"}
        # We're just testing that valid qualities don't cause validation errors
        # The actual response depends on mocking, but 422 should not occur
        response = client.post("/goods", json=good_data, headers=headers)

        # Should not be a validation error (422)
        assert response.status_code != 422


def test_trader_type_validation(client):
    """
    Test trader type field accepts only valid values.

    Educational Note:
    Enum validation prevents typos and ensures data consistency
    across the system.
    """
    # Testing by retrieving with valid trader type - should not error
    with patch('raspberry_pi.api.trading_fort.get_db_connection') as mock_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        mock_cursor.fetchall.return_value = []

        response = client.get("/traders?trader_type=trapper")
        assert response.status_code == 200


# ============================================================================
# Error Handling Tests
# ============================================================================

@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_database_error_handling(mock_db_func, client):
    """Test graceful handling of database errors."""
    mock_db_func.side_effect = Exception("Database connection failed")

    response = client.get("/goods")

    assert response.status_code == 500
    assert "Failed to fetch goods" in response.json()["detail"]


def test_invalid_endpoint_returns_404(client):
    """Test that invalid endpoints return 404."""
    response = client.get("/invalid-endpoint")

    assert response.status_code == 404


# ============================================================================
# Performance and Edge Cases
# ============================================================================

@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_get_trades_respects_limit(mock_db_func, client, mock_db_connection):
    """
    Test that trade records endpoint limits results.

    Educational Note:
    Limiting results prevents performance issues when datasets grow large.
    The API limits to 100 trades to keep responses manageable.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/trades")

    assert response.status_code == 200

    # Verify LIMIT clause in SQL
    call_args = mock_cursor.execute.call_args[0]
    assert "LIMIT 100" in call_args[0]


@patch('raspberry_pi.api.trading_fort.get_db_connection')
def test_price_history_days_validation(mock_db_func, client, mock_db_connection):
    """Test that price history days parameter is validated."""
    mock_conn, mock_cursor = mock_db_connection
    mock_db_func.return_value = mock_conn

    mock_cursor.fetchone.return_value = ("Test Good",)
    mock_cursor.fetchall.return_value = []

    # Test max limit (365 days)
    response = client.get("/goods/1/price-history?days=365")
    assert response.status_code == 200

    # Test exceeding max should fail validation
    response = client.get("/goods/1/price-history?days=400")
    assert response.status_code == 422
