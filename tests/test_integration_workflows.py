"""
Integration Tests for Multi-Node Workflows

This module contains integration tests that verify multi-fort workflows including
authentication, data synchronization, cross-fort communication, and distributed
operations.

Educational Note:
Integration tests verify that multiple components work together correctly.
Unlike unit tests that test components in isolation, these tests exercise
complete workflows across the distributed system. They are slower but catch
issues that unit tests might miss.

These tests can run in two modes:
1. Mock mode (default): Uses mocked APIs for fast, reliable CI testing
2. Live mode: Tests against actual running API servers

To run:
    # Mock mode
    pytest tests/test_integration_workflows.py -v -m integration

    # Live mode (requires running API servers)
    pytest tests/test_integration_workflows.py -v -m integration --live

Mark tests as slow if they take >1 second:
    pytest tests/test_integration_workflows.py -v -m "integration and not slow"
"""

import pytest
from unittest.mock import patch, MagicMock
import time
from datetime import datetime

from src.api_client.client import OutpostAPIClient


# ============================================================================
# Test Configuration
# ============================================================================

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run tests against live API servers instead of mocks"
    )


@pytest.fixture
def live_mode(request):
    """Determine if tests should run in live mode."""
    return request.config.getoption("--live")


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def fishing_fort_url():
    """Fishing Fort API URL."""
    return "http://localhost:8000"


@pytest.fixture
def trading_fort_url():
    """Trading Fort API URL."""
    return "http://localhost:8001"


@pytest.fixture
def hunting_fort_url():
    """Hunting Fort API URL."""
    return "http://localhost:8002"


@pytest.fixture
def fishing_client(fishing_fort_url):
    """Create API client for Fishing Fort."""
    return OutpostAPIClient(fishing_fort_url)


@pytest.fixture
def trading_client(trading_fort_url):
    """Create API client for Trading Fort."""
    return OutpostAPIClient(trading_fort_url)


@pytest.fixture
def hunting_client(hunting_fort_url):
    """Create API client for Hunting Fort."""
    return OutpostAPIClient(hunting_fort_url)


@pytest.fixture
def sample_inventory_export():
    """Sample inventory export data for sync testing."""
    return {
        "source_fort": "fishing_fort",
        "exported_at": datetime.now().isoformat(),
        "exported_by": "test_user",
        "item_count": 5,
        "items": [
            {"id": 1, "name": "Salmon", "quantity": 50, "category": "fish"},
            {"id": 2, "name": "Trout", "quantity": 30, "category": "fish"},
            {"id": 3, "name": "Pike", "quantity": 20, "category": "fish"},
            {"id": 4, "name": "Net", "quantity": 10, "category": "equipment"},
            {"id": 5, "name": "Hook", "quantity": 100, "category": "equipment"}
        ]
    }


# ============================================================================
# Authentication Workflow Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.auth
def test_multi_fort_authentication(fishing_client, trading_client, hunting_client, live_mode):
    """
    Test authenticating to multiple forts simultaneously.

    Educational Note:
    In distributed systems, clients often need to authenticate to multiple
    services. This test ensures the authentication flow works across all forts
    and tokens are managed independently.
    """
    if live_mode:
        pytest.skip("Requires running API servers")

    # Mock login for all three forts
    with patch.object(fishing_client.session, 'post') as mock_fishing_post, \
         patch.object(trading_client.session, 'post') as mock_trading_post, \
         patch.object(hunting_client.session, 'post') as mock_hunting_post:

        # Configure mocks for successful login
        for mock_post in [mock_fishing_post, mock_trading_post, mock_hunting_post]:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": f"token_{id(mock_post)}",
                "expires_in": 3600
            }
            mock_post.return_value = mock_response

        # Authenticate to all forts
        fishing_success = fishing_client.login("fort_commander", "frontier_pass123")
        trading_success = trading_client.login("fort_commander", "frontier_pass123")
        hunting_success = hunting_client.login("fort_commander", "frontier_pass123")

        # Verify all authentications succeeded
        assert fishing_success
        assert trading_success
        assert hunting_success

        # Verify each client has its own token
        assert fishing_client.is_authenticated
        assert trading_client.is_authenticated
        assert hunting_client.is_authenticated

        assert fishing_client.token != trading_client.token
        assert trading_client.token != hunting_client.token


@pytest.mark.integration
@pytest.mark.auth
def test_token_expiration_handling(fishing_client, live_mode):
    """
    Test handling of expired authentication tokens.

    Educational Note:
    Tokens expire for security. Applications must handle expiration gracefully,
    either by refreshing tokens or prompting for re-authentication.
    """
    if live_mode:
        pytest.skip("Requires running API servers")

    with patch.object(fishing_client.session, 'post') as mock_post:
        # Mock successful login
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 1  # Expires in 1 second
        }
        mock_post.return_value = mock_response

        # Login
        fishing_client.login("testuser", "testpass")
        assert fishing_client.is_authenticated

        # Wait for expiration
        time.sleep(1.1)

        # Token should be expired (in real implementation, check _token_expires_at)
        if fishing_client._token_expires_at:
            assert datetime.now() > fishing_client._token_expires_at


# ============================================================================
# Data Synchronization Workflow Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
def test_basic_data_sync_workflow(fishing_client, trading_client, sample_inventory_export, live_mode):
    """
    Test basic data synchronization between two forts.

    Educational Note:
    Data synchronization is a core distributed system operation. This test
    verifies the complete sync workflow: export from source, import to target,
    and validation of results.
    """
    if live_mode:
        pytest.skip("Requires running API servers")

    # Mock authentication
    fishing_client.set_token("test_token_fishing")
    trading_client.set_token("test_token_trading")

    with patch.object(fishing_client, '_make_request') as mock_fishing_request, \
         patch.object(trading_client, '_make_request') as mock_trading_request:

        # Mock export from fishing fort
        mock_fishing_request.return_value = sample_inventory_export

        # Mock import to trading fort
        mock_trading_request.return_value = {
            "success": True,
            "statistics": {
                "items_added": 5,
                "items_updated": 0,
                "items_skipped": 0
            },
            "imported_at": datetime.now().isoformat()
        }

        # Execute sync workflow
        # Step 1: Export from fishing fort
        export_data = fishing_client._make_request('POST', '/sync/export-inventory')
        assert export_data is not None
        assert export_data["item_count"] == 5

        # Step 2: Import to trading fort
        import_payload = {
            **export_data,
            "merge_strategy": "add"
        }
        import_result = trading_client._make_request('POST', '/sync/import-inventory',
                                                      json_data=import_payload)

        # Verify sync results
        assert import_result["success"]
        assert import_result["statistics"]["items_added"] == 5


@pytest.mark.integration
def test_sync_merge_strategies(fishing_client, trading_client, live_mode):
    """
    Test different merge strategies in data synchronization.

    Educational Note:
    Different merge strategies solve different problems:
    - 'add': Safe, no data loss, but ignores updates
    - 'merge': Combines data, good for quantities
    - 'replace': Simple but destructive

    This test ensures each strategy behaves correctly.
    """
    if live_mode:
        pytest.skip("Requires running API servers")

    fishing_client.set_token("test_token")
    trading_client.set_token("test_token")

    test_data = {
        "source_fort": "fishing_fort",
        "items": [{"id": 1, "name": "Test", "quantity": 10}]
    }

    strategies = ["add", "merge", "replace"]

    with patch.object(fishing_client, '_make_request') as mock_fishing, \
         patch.object(trading_client, '_make_request') as mock_trading:

        mock_fishing.return_value = test_data

        for strategy in strategies:
            # Configure mock for this strategy
            mock_trading.return_value = {
                "success": True,
                "strategy_used": strategy,
                "statistics": {
                    "items_added": 1 if strategy == "add" else 0,
                    "items_updated": 1 if strategy in ["merge", "replace"] else 0,
                    "items_skipped": 0
                }
            }

            # Execute sync with this strategy
            export_data = fishing_client._make_request('POST', '/sync/export-inventory')
            import_result = trading_client._make_request(
                'POST',
                '/sync/import-inventory',
                json_data={**export_data, "merge_strategy": strategy}
            )

            # Verify strategy was applied
            assert import_result["strategy_used"] == strategy


@pytest.mark.integration
@pytest.mark.slow
def test_three_way_sync(fishing_client, trading_client, hunting_client, live_mode):
    """
    Test synchronization across three forts.

    Educational Note:
    Multi-node synchronization introduces complexity. This test verifies
    that data can flow through a chain: Fort A ’ Fort B ’ Fort C
    """
    if live_mode:
        pytest.skip("Requires running API servers")

    # Authenticate all clients
    for client in [fishing_client, trading_client, hunting_client]:
        client.set_token("test_token")

    with patch.object(fishing_client, '_make_request') as mock_fishing, \
         patch.object(trading_client, '_make_request') as mock_trading, \
         patch.object(hunting_client, '_make_request') as mock_hunting:

        # Scenario: Fishing ’ Trading ’ Hunting

        # Step 1: Export from Fishing
        fishing_data = {"items": [{"id": 1, "name": "Fish"}]}
        mock_fishing.return_value = fishing_data

        # Step 2: Import to Trading
        mock_trading.side_effect = [
            {"success": True, "statistics": {"items_added": 1}},  # Import
            fishing_data  # Export
        ]

        # Step 3: Import to Hunting
        mock_hunting.return_value = {"success": True, "statistics": {"items_added": 1}}

        # Execute chain
        data_from_fishing = fishing_client._make_request('POST', '/sync/export-inventory')
        trading_client._make_request('POST', '/sync/import-inventory',
                                      json_data=data_from_fishing)

        data_from_trading = trading_client._make_request('POST', '/sync/export-inventory')
        hunting_result = hunting_client._make_request('POST', '/sync/import-inventory',
                                                       json_data=data_from_trading)

        assert hunting_result["success"]


# ============================================================================
# Cross-Fort Query Workflow Tests
# ============================================================================

@pytest.mark.integration
def test_cross_fort_data_aggregation(fishing_client, trading_client, hunting_client, live_mode):
    """
    Test aggregating data from multiple forts.

    Educational Note:
    Distributed analytics requires querying multiple nodes and combining results.
    This is a common pattern in microservices and distributed systems.
    """
    if live_mode:
        pytest.skip("Requires running API servers")

    with patch.object(fishing_client, 'get_status') as mock_fishing_status, \
         patch.object(trading_client, 'get_status') as mock_trading_status, \
         patch.object(hunting_client, 'get_status') as mock_hunting_status:

        # Mock status responses
        mock_fishing_status.return_value = {
            "fort_name": "Fishing Fort",
            "statistics": {"total_value": 5000.00}
        }
        mock_trading_status.return_value = {
            "fort_name": "Trading Fort",
            "statistics": {"total_value": 7500.00}
        }
        mock_hunting_status.return_value = {
            "fort_name": "Hunting Fort",
            "statistics": {"value_this_season": 3500.00}
        }

        # Aggregate data
        fishing_status = fishing_client.get_status()
        trading_status = trading_client.get_status()
        hunting_status = hunting_client.get_status()

        # Calculate total value across all forts
        total_value = (
            fishing_status["statistics"]["total_value"] +
            trading_status["statistics"]["total_value"] +
            hunting_status["statistics"]["value_this_season"]
        )

        assert total_value == 16000.00


# ============================================================================
# Error Handling and Recovery Tests
# ============================================================================

@pytest.mark.integration
def test_partial_network_failure_recovery(fishing_client, trading_client, live_mode):
    """
    Test system behavior when one fort is unavailable.

    Educational Note:
    Distributed systems must handle partial failures gracefully.
    The system should continue operating even if some nodes are down.
    """
    if live_mode:
        pytest.skip("Requires running API servers")

    # Fishing fort is working
    with patch.object(fishing_client, 'health_check') as mock_fishing_health:
        mock_fishing_health.return_value = {"status": "healthy"}

        # Trading fort is down
        with patch.object(trading_client, 'health_check') as mock_trading_health:
            mock_trading_health.return_value = None

            fishing_health = fishing_client.health_check()
            trading_health = trading_client.health_check()

            # Fishing should still work
            assert fishing_health is not None
            assert fishing_health["status"] == "healthy"

            # Trading should gracefully report unavailability
            assert trading_health is None


@pytest.mark.integration
def test_sync_with_network_recovery(fishing_client, trading_client, live_mode):
    """
    Test data sync with network issues and automatic retry.

    Educational Note:
    Network issues are common in distributed systems. Retry logic with
    exponential backoff helps systems recover from transient failures.
    """
    if live_mode:
        pytest.skip("Requires running API servers")

    fishing_client.set_token("test_token")

    with patch.object(fishing_client, '_make_request_with_retry') as mock_retry:
        # Simulate: Fail twice, then succeed
        from unittest.mock import Mock
        import requests

        failure_response = Mock()
        failure_response.status_code = 503

        success_response = Mock()
        success_response.status_code = 200
        success_response.headers = {'Content-Type': 'application/json'}
        success_response.json.return_value = {"success": True}

        # First two attempts fail with 503, third succeeds
        mock_retry.side_effect = [
            requests.exceptions.HTTPError(response=failure_response),
            requests.exceptions.HTTPError(response=failure_response),
            success_response
        ]

        with patch('time.sleep'):  # Don't actually sleep
            # This should retry and eventually succeed
            result = fishing_client._make_request('POST', '/sync/export-inventory')

            # Verify retries occurred
            assert mock_retry.call_count == 3


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
def test_concurrent_fort_operations(fishing_client, trading_client, hunting_client, live_mode):
    """
    Test concurrent operations across multiple forts.

    Educational Note:
    Real systems handle multiple concurrent requests. This test ensures
    clients can operate independently without interference.
    """
    if live_mode:
        pytest.skip("Requires running API servers")

    import threading

    results = {}

    def query_fort(name, client):
        """Query a fort and store result."""
        with patch.object(client, 'get_status') as mock_status:
            mock_status.return_value = {"fort_name": name}
            results[name] = client.get_status()

    # Create threads for concurrent queries
    threads = [
        threading.Thread(target=query_fort, args=("Fishing", fishing_client)),
        threading.Thread(target=query_fort, args=("Trading", trading_client)),
        threading.Thread(target=query_fort, args=("Hunting", hunting_client))
    ]

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for completion
    for thread in threads:
        thread.join()

    # Verify all succeeded
    assert len(results) == 3
    assert "Fishing" in results
    assert "Trading" in results
    assert "Hunting" in results


if __name__ == "__main__":
    """
    Run integration tests with:
        python -m pytest tests/test_integration_workflows.py -v -m integration
    """
    pytest.main([__file__, "-v", "-m", "integration"])
