"""
Unit Tests for Outpost API Client

This module contains comprehensive unit tests for the OutpostAPIClient,
focusing on authentication, retry logic, error handling, and request management.

Educational Note:
Testing client libraries is crucial because they're used throughout the application.
These tests verify:
- Retry logic with exponential backoff
- Authentication token management
- Error classification and handling
- Request/response cycles
- Edge cases and failure scenarios

To run:
    pytest tests/test_api_client.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from datetime import datetime, timedelta
import time

from src.api_client.client import OutpostAPIClient


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def api_url():
    """Base API URL for testing."""
    return "http://localhost:8000"


@pytest.fixture
def client(api_url):
    """Create a basic API client for testing."""
    return OutpostAPIClient(api_url)


@pytest.fixture
def authenticated_client(api_url):
    """Create an authenticated API client for testing."""
    client = OutpostAPIClient(api_url)
    client.set_token("test_token_12345")
    return client


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    response = Mock()
    response.status_code = 200
    response.headers = {'Content-Type': 'application/json'}
    response.json.return_value = {"message": "success"}
    return response


# ============================================================================
# Initialization Tests
# ============================================================================

def test_client_initialization(api_url):
    """
    Test client initializes with correct default values.

    Educational Note:
    Initialization tests ensure objects start in the correct state.
    """
    client = OutpostAPIClient(api_url)

    assert client.base_url == api_url
    assert client.timeout == 10
    assert client.max_retries == 3
    assert client.retry_backoff_factor == 2.0
    assert not client.is_authenticated
    assert client.token is None


def test_client_initialization_with_token(api_url):
    """Test client can be initialized with a pre-existing token."""
    token = "test_token_abc123"
    client = OutpostAPIClient(api_url, token=token)

    assert client.is_authenticated
    assert client.token == token
    assert 'Authorization' in client.session.headers
    assert client.session.headers['Authorization'] == f'Bearer {token}'


def test_client_initialization_custom_retry_config(api_url):
    """Test client accepts custom retry configuration."""
    client = OutpostAPIClient(
        api_url,
        max_retries=5,
        retry_backoff_factor=1.5
    )

    assert client.max_retries == 5
    assert client.retry_backoff_factor == 1.5


# ============================================================================
# Authentication Tests
# ============================================================================

def test_set_token(client):
    """
    Test manually setting authentication token.

    Educational Note:
    Token management is critical for authenticated APIs.
    This test ensures tokens are properly stored and used.
    """
    token = "new_test_token"
    client.set_token(token)

    assert client.is_authenticated
    assert client.token == token
    assert 'Authorization' in client.session.headers


def test_clear_token(authenticated_client):
    """Test clearing authentication token."""
    assert authenticated_client.is_authenticated

    authenticated_client.clear_token()

    assert not authenticated_client.is_authenticated
    assert authenticated_client.token is None
    assert 'Authorization' not in authenticated_client.session.headers


def test_login_success(client):
    """
    Test successful login flow.

    Educational Note:
    Login is a critical operation. This test ensures the complete
    OAuth2 password flow works correctly.
    """
    with patch.object(client.session, 'post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token_xyz",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        result = client.login("testuser", "testpass")

        assert result is True
        assert client.is_authenticated
        assert client.token == "new_token_xyz"
        assert client._token_expires_at is not None


def test_login_failure(client):
    """
    Test failed login attempt.

    Educational Note:
    Testing failure cases ensures the client handles errors gracefully
    and doesn't leak sensitive information.
    """
    with patch.object(client.session, 'post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid credentials"
        mock_post.return_value = mock_response

        result = client.login("baduser", "badpass")

        assert result is False
        assert not client.is_authenticated
        assert client.token is None


def test_login_preserves_old_token_on_failure(client):
    """Test that failed login doesn't clear existing token."""
    old_token = "existing_token"
    client.set_token(old_token)

    with patch.object(client.session, 'post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        client.login("testuser", "wrongpass")

        # Old token should be preserved
        assert client.token == old_token
        assert client.is_authenticated


# ============================================================================
# Retry Logic Tests
# ============================================================================

def test_is_retryable_error_connection_error(client):
    """
    Test connection errors are classified as retryable.

    Educational Note:
    Network connection errors are typically transient and
    should trigger retries.
    """
    error = requests.exceptions.ConnectionError("Connection refused")
    assert client._is_retryable_error(error) is True


def test_is_retryable_error_timeout(client):
    """Test timeout errors are classified as retryable."""
    error = requests.exceptions.Timeout("Request timed out")
    assert client._is_retryable_error(error) is True


def test_is_retryable_error_server_error(client):
    """
    Test 5xx server errors are retryable.

    Educational Note:
    Server errors (500, 502, 503, 504) are often temporary issues
    that resolve on retry.
    """
    response = Mock()

    for status_code in [500, 502, 503, 504]:
        response.status_code = status_code
        error = requests.exceptions.HTTPError(response=response)

        assert client._is_retryable_error(error) is True


def test_is_retryable_error_client_error(client):
    """
    Test 4xx client errors are NOT retryable.

    Educational Note:
    Client errors (400, 401, 404, etc.) indicate problems with
    the request itself and won't be fixed by retrying.
    """
    response = Mock()

    for status_code in [400, 401, 403, 404, 422]:
        response.status_code = status_code
        error = requests.exceptions.HTTPError(response=response)

        assert client._is_retryable_error(error) is False


def test_calculate_backoff_delay(client):
    """
    Test exponential backoff calculation.

    Educational Note:
    Exponential backoff prevents overwhelming a struggling server.
    Each retry waits longer than the previous one.
    """
    # Test default backoff factor (2.0)
    assert client._calculate_backoff_delay(0) == 1.0  # 1 * (2^0) = 1
    assert client._calculate_backoff_delay(1) == 2.0  # 1 * (2^1) = 2
    assert client._calculate_backoff_delay(2) == 4.0  # 1 * (2^2) = 4
    assert client._calculate_backoff_delay(3) == 8.0  # 1 * (2^3) = 8


def test_calculate_backoff_delay_custom_factor(api_url):
    """Test backoff calculation with custom factor."""
    client = OutpostAPIClient(api_url, retry_backoff_factor=1.5)

    assert client._calculate_backoff_delay(0) == 1.0    # 1 * (1.5^0) = 1
    assert client._calculate_backoff_delay(1) == 1.5    # 1 * (1.5^1) = 1.5
    assert client._calculate_backoff_delay(2) == 2.25   # 1 * (1.5^2) = 2.25


def test_retry_on_connection_error(client):
    """
    Test that connection errors trigger retries.

    Educational Note:
    This test verifies the complete retry flow: attempt, fail,
    wait, retry, eventually succeed or give up.
    """
    with patch.object(client.session, 'request') as mock_request:
        # First two attempts fail, third succeeds
        mock_request.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            Mock(status_code=200, headers={'Content-Type': 'application/json'},
                 json=lambda: {"data": "success"})
        ]

        with patch('time.sleep'):  # Don't actually sleep in tests
            response = client._make_request_with_retry(
                'GET',
                f'{client.base_url}/test',
                retry_enabled=True
            )

        assert response.status_code == 200
        assert mock_request.call_count == 3


def test_retry_exhaustion(client):
    """
    Test that retries eventually give up after max attempts.

    Educational Note:
    Infinite retries would hang the application. After max_retries,
    the error should be raised.
    """
    with patch.object(client.session, 'request') as mock_request:
        # All attempts fail
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with patch('time.sleep'):
            with pytest.raises(requests.exceptions.ConnectionError):
                client._make_request_with_retry(
                    'GET',
                    f'{client.base_url}/test',
                    retry_enabled=True
                )

        # Should attempt max_retries + 1 times (initial + retries)
        assert mock_request.call_count == client.max_retries + 1


def test_no_retry_on_client_error(client):
    """
    Test that client errors (4xx) don't trigger retries.

    Educational Note:
    Client errors indicate problems with the request that won't
    be fixed by retrying, so we fail fast.
    """
    with patch.object(client.session, 'request') as mock_request:
        response = Mock()
        response.status_code = 404
        response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=response)

        mock_request.return_value = response

        with pytest.raises(requests.exceptions.HTTPError):
            client._make_request_with_retry(
                'GET',
                f'{client.base_url}/test',
                retry_enabled=True
            )

        # Should only attempt once (no retries)
        assert mock_request.call_count == 1


def test_retry_disabled(client):
    """Test that retries can be disabled."""
    with patch.object(client.session, 'request') as mock_request:
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(requests.exceptions.ConnectionError):
            client._make_request_with_retry(
                'GET',
                f'{client.base_url}/test',
                retry_enabled=False  # Disable retries
            )

        # Should only attempt once
        assert mock_request.call_count == 1


# ============================================================================
# Request Making Tests
# ============================================================================

def test_make_request_success(client):
    """Test successful HTTP request."""
    with patch.object(client, '_make_request_with_retry') as mock_retry:
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"result": "success"}
        mock_retry.return_value = mock_response

        result = client._make_request('GET', '/test')

        assert result == {"result": "success"}


def test_make_request_non_json_response(client):
    """Test handling of non-JSON responses."""
    with patch.object(client, '_make_request_with_retry') as mock_retry:
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_retry.return_value = mock_response

        result = client._make_request('GET', '/test')

        # Should return the response object itself for non-JSON
        assert result == mock_response


def test_make_request_handles_timeout(client):
    """Test that timeouts are handled and return None."""
    with patch.object(client, '_make_request_with_retry') as mock_retry:
        mock_retry.side_effect = requests.exceptions.Timeout("Timeout")

        result = client._make_request('GET', '/test')

        assert result is None


def test_make_request_handles_connection_error(client):
    """Test that connection errors are handled and return None."""
    with patch.object(client, '_make_request_with_retry') as mock_retry:
        mock_retry.side_effect = requests.exceptions.ConnectionError("Connection failed")

        result = client._make_request('GET', '/test')

        assert result is None


# ============================================================================
# Endpoint Method Tests
# ============================================================================

def test_health_check(client):
    """Test health check endpoint method."""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {"status": "healthy"}

        result = client.health_check()

        mock_request.assert_called_once_with('GET', '/health')
        assert result["status"] == "healthy"


def test_get_status(client):
    """Test get status endpoint method."""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {"fort_name": "Test Fort"}

        result = client.get_status()

        mock_request.assert_called_once_with('GET', '/status')
        assert result["fort_name"] == "Test Fort"


def test_get_inventory_with_filter(client):
    """Test inventory retrieval with category filter."""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = [{"item": "test"}]

        result = client.get_inventory(category="fish")

        mock_request.assert_called_once_with('GET', '/inventory', params={'category': 'fish'})


def test_get_inventory_without_filter(client):
    """Test inventory retrieval without filters."""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = [{"item": "test"}]

        result = client.get_inventory()

        mock_request.assert_called_once_with('GET', '/inventory', params=None)


# ============================================================================
# Protected Endpoint Tests
# ============================================================================

def test_protected_endpoint_requires_authentication(client):
    """
    Test that protected endpoints check for authentication.

    Educational Note:
    Protected endpoints should validate authentication before
    making requests to avoid unnecessary network calls.
    """
    # Client is not authenticated
    assert not client.is_authenticated

    result = client.get_admin_stats()

    # Should return None without making a request
    assert result is None


def test_protected_endpoint_with_authentication(authenticated_client):
    """Test protected endpoints work with valid authentication."""
    with patch.object(authenticated_client, '_make_request') as mock_request:
        mock_request.return_value = {"stats": "data"}

        result = authenticated_client.get_admin_stats()

        assert result is not None
        mock_request.assert_called_once()


# ============================================================================
# Edge Case Tests
# ============================================================================

def test_base_url_trailing_slash_handling(api_url):
    """
    Test that trailing slashes in base URL are handled correctly.

    Educational Note:
    URL construction can cause issues with double slashes.
    Proper normalization prevents this.
    """
    client_with_slash = OutpostAPIClient(api_url + "/")

    assert client_with_slash.base_url == api_url  # Trailing slash removed


def test_endpoint_leading_slash_handling(client):
    """Test that leading slashes in endpoints are handled correctly."""
    with patch.object(client, '_make_request_with_retry') as mock_retry:
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {}
        mock_retry.return_value = mock_response

        # Both should work the same
        client._make_request('GET', '/test')
        client._make_request('GET', 'test')

        # Check that both calls resulted in the same URL
        calls = mock_retry.call_args_list
        assert calls[0][1]['url'] == calls[1][1]['url']


if __name__ == "__main__":
    """Run tests with: python -m pytest tests/test_api_client.py -v"""
    pytest.main([__file__, "-v"])
