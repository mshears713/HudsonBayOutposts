"""
Reusable API Client Module for Raspberry Pi Outposts

This module provides a clean abstraction layer for interacting with
outpost APIs, handling common tasks like error handling, retries,
authentication, and response parsing.

Educational Note:
API clients abstract the complexity of HTTP requests and provide a
clean Python interface. This makes code more maintainable and testable.

Phase 3 Enhancement:
This client now supports token-based authentication, allowing secure
access to protected API endpoints.
"""

import requests
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class OutpostAPIClient:
    """
    Client for interacting with Raspberry Pi outpost APIs with authentication support.

    Educational Note:
    This class follows the Single Responsibility Principle - it handles
    all API communication logic in one place. It now includes authentication
    management, automatically handling token storage and inclusion in requests.

    Phase 3 Feature:
    The client can authenticate with username/password and automatically
    include bearer tokens in subsequent requests to protected endpoints.
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        token: Optional[str] = None,
        max_retries: int = 3,
        retry_backoff_factor: float = 2.0
    ):
        """
        Initialize API client with optional authentication and retry configuration.

        Educational Note:
        The client can be initialized with or without a token. If you have
        a token already, pass it here. Otherwise, use the login() method
        to obtain one.

        Phase 3 Enhancement (Step 28):
        The client now supports automatic retries with exponential backoff for
        network failures and transient errors, improving reliability in
        distributed systems.

        Args:
            base_url: Base URL of the outpost API (e.g., http://192.168.1.100:8000)
            timeout: Request timeout in seconds
            token: Optional pre-existing authentication token
            max_retries: Maximum number of retry attempts for failed requests
            retry_backoff_factor: Multiplier for exponential backoff (default: 2.0)

        Example:
            # Without authentication
            client = OutpostAPIClient("http://192.168.1.100:8000")

            # With pre-existing token
            client = OutpostAPIClient("http://192.168.1.100:8000", token="eyJhbG...")

            # With custom retry configuration
            client = OutpostAPIClient(
                "http://192.168.1.100:8000",
                max_retries=5,
                retry_backoff_factor=1.5
            )

            # Login to get token
            client = OutpostAPIClient("http://192.168.1.100:8000")
            client.login("username", "password")
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self._token: Optional[str] = token
        self._token_expires_at: Optional[datetime] = None

        # Retry configuration
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor

        # If token provided, set it in session headers
        if self._token:
            self._set_auth_header()

    def _set_auth_header(self):
        """
        Set the authorization header in the session.

        Educational Note:
        Bearer token authentication uses the Authorization header with format:
        "Bearer <token>". This is a standard authentication method in REST APIs.
        """
        if self._token:
            self.session.headers.update({
                'Authorization': f'Bearer {self._token}'
            })
            logger.debug("Authentication header set in session")
        else:
            # Remove auth header if no token
            self.session.headers.pop('Authorization', None)
            logger.debug("Authentication header removed from session")

    @property
    def is_authenticated(self) -> bool:
        """
        Check if client has a valid authentication token.

        Educational Note:
        This property allows easy checking of authentication status:
        if client.is_authenticated:
            # Make authenticated requests
        """
        return self._token is not None

    @property
    def token(self) -> Optional[str]:
        """Get the current authentication token."""
        return self._token

    def set_token(self, token: str, expires_in: Optional[int] = None):
        """
        Manually set the authentication token.

        Educational Note:
        Use this if you have a token from another source and want to
        use it with this client.

        Args:
            token: The JWT token string
            expires_in: Optional token expiration time in seconds
        """
        self._token = token
        self._set_auth_header()

        if expires_in:
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

        logger.info("Authentication token set manually")

    def clear_token(self):
        """
        Clear the authentication token.

        Educational Note:
        Call this to log out or clear authentication state.
        """
        self._token = None
        self._token_expires_at = None
        self._set_auth_header()
        logger.info("Authentication token cleared")

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate with the API and obtain an access token.

        Educational Note:
        This method implements the OAuth2 password flow:
        1. Send username and password to /auth/login
        2. Receive access token in response
        3. Store token for use in subsequent requests

        Args:
            username: User's username
            password: User's password

        Returns:
            True if login successful, False otherwise

        Example:
            client = OutpostAPIClient("http://192.168.1.100:8000")
            if client.login("fort_commander", "frontier_pass123"):
                print("Login successful!")
                # Now can access protected endpoints
                stats = client.get_admin_stats()
        """
        try:
            # Temporarily clear auth header for login request
            old_token = self._token
            self._token = None
            self._set_auth_header()

            # Make login request
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password},
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                self._token = data.get('access_token')
                expires_in = data.get('expires_in', 3600)

                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                self._set_auth_header()

                logger.info(f"Login successful for user: {username}")
                return True
            else:
                logger.error(f"Login failed: {response.status_code} - {response.text}")
                # Restore old token if login failed
                self._token = old_token
                if old_token:
                    self._set_auth_header()
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            # Restore old token if login failed
            self._token = old_token
            if old_token:
                self._set_auth_header()
            return False

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently authenticated user.

        Educational Note:
        This endpoint is useful for:
        - Verifying the token is still valid
        - Getting user information (username, role, permissions)
        - Checking authentication status

        Returns:
            User information dict or None if not authenticated

        Example:
            user = client.get_current_user()
            if user:
                print(f"Logged in as: {user['username']} (role: {user['role']})")
        """
        if not self.is_authenticated:
            logger.warning("Attempted to get current user without authentication")
            return None

        return self._make_request('GET', '/auth/me')

    def list_available_users(self) -> Optional[Dict[str, Any]]:
        """
        Get list of available demo users (for educational purposes).

        Educational Note:
        This is a helper endpoint for learning. Production APIs would
        NOT expose available usernames!

        Returns:
            Dictionary of available users and their roles
        """
        return self._make_request('GET', '/auth/users')

    # ========================================================================
    # Enhanced Error Handling & Retry Logic (Phase 3, Step 28)
    # ========================================================================

    def _is_retryable_error(self, exception: Exception) -> bool:
        """
        Determine if an error is retryable.

        Educational Note:
        Not all errors should trigger retries. Network errors and timeouts
        are typically transient and worth retrying. Authentication errors,
        client errors (4xx), and validation errors should not be retried.

        Args:
            exception: The exception that occurred

        Returns:
            True if the error is retryable, False otherwise
        """
        # Network errors - should retry
        if isinstance(exception, (requests.exceptions.ConnectionError,
                                 requests.exceptions.Timeout)):
            return True

        # HTTP errors - check status code
        if isinstance(exception, requests.exceptions.HTTPError):
            # Retry on server errors (5xx) but not client errors (4xx)
            if exception.response is not None:
                status_code = exception.response.status_code
                # Retry on 500, 502, 503, 504 (server errors)
                return status_code in [500, 502, 503, 504]

        # Don't retry other errors
        return False

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.

        Educational Note:
        Exponential backoff prevents overwhelming a struggling server.
        Each retry waits longer than the last:
        - Attempt 1: 1 second
        - Attempt 2: 2 seconds
        - Attempt 3: 4 seconds
        - Attempt 4: 8 seconds
        etc.

        This gives the server time to recover and reduces network congestion.

        Args:
            attempt: Current retry attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff: base_delay * (backoff_factor ^ attempt)
        base_delay = 1.0
        delay = base_delay * (self.retry_backoff_factor ** attempt)

        logger.debug(f"Calculated backoff delay: {delay:.2f}s for attempt {attempt}")
        return delay

    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        retry_enabled: bool = True
    ) -> requests.Response:
        """
        Make HTTP request with automatic retry logic.

        Educational Note:
        This method implements the retry pattern with exponential backoff:
        1. Try the request
        2. If it fails with a retryable error, wait (with increasing delays)
        3. Try again up to max_retries times
        4. If all retries fail, raise the last exception

        Args:
            method: HTTP method
            url: Full URL to request
            params: Query parameters
            json_data: JSON body data
            files: Files for upload
            retry_enabled: Whether to enable retries (default: True)

        Returns:
            Response object if successful

        Raises:
            Exception from last retry attempt if all retries fail
        """
        last_exception = None
        max_attempts = self.max_retries + 1 if retry_enabled else 1

        for attempt in range(max_attempts):
            try:
                logger.debug(f"Request attempt {attempt + 1}/{max_attempts}: {method} {url}")

                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    files=files,
                    timeout=self.timeout
                )
                response.raise_for_status()

                # Success!
                if attempt > 0:
                    logger.info(f"Request succeeded on attempt {attempt + 1}/{max_attempts}")

                return response

            except Exception as e:
                last_exception = e

                # Check if we should retry
                if attempt < max_attempts - 1 and self._is_retryable_error(e):
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{max_attempts}): {str(e)}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    # Last attempt or non-retryable error
                    logger.error(
                        f"Request failed on attempt {attempt + 1}/{max_attempts}: {str(e)}"
                    )
                    raise

        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Request failed with unknown error")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        retry_enabled: bool = True
    ) -> Optional[Any]:
        """
        Make an HTTP request with enhanced error handling and retry logic.

        Educational Note:
        This method provides a clean interface for making API requests while
        handling common failure scenarios automatically. It uses the retry
        mechanism for network failures and provides detailed error messages.

        Phase 3 Enhancement (Step 28):
        Now includes automatic retries with exponential backoff for transient
        failures, improving reliability in distributed systems.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body data
            files: Files for upload
            retry_enabled: Whether to enable retries (default: True)

        Returns:
            Response data or None if failed
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self._make_request_with_retry(
                method=method,
                url=url,
                params=params,
                json_data=json_data,
                files=files,
                retry_enabled=retry_enabled
            )

            # Return JSON if content type is JSON
            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()
            else:
                return response

        except requests.exceptions.Timeout:
            logger.error(f"Request timed out after {self.max_retries} retries: {url}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection failed after {self.max_retries} retries: {url}")
            logger.error(f"  Hint: Check if the API server is running at {self.base_url}")
            return None
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"
            logger.error(f"HTTP {status_code} error: {url}")

            # Provide helpful error messages based on status code
            if status_code == 401:
                logger.error("  Hint: Authentication required. Did you call login()?")
            elif status_code == 403:
                logger.error("  Hint: Permission denied. Check user role/permissions.")
            elif status_code == 404:
                logger.error("  Hint: Endpoint not found. Check the API path.")
            elif status_code == 422:
                logger.error("  Hint: Validation error. Check request data format.")
            elif isinstance(status_code, int) and 500 <= status_code < 600:
                logger.error("  Hint: Server error. Check API logs for details.")

            return None
        except Exception as e:
            logger.error(f"Unexpected error: {url}")
            logger.error(f"  Error type: {type(e).__name__}")
            logger.error(f"  Error message: {str(e)}")
            return None

    # Health and Status
    def health_check(self) -> Optional[Dict[str, Any]]:
        """Check API health."""
        return self._make_request('GET', '/health')

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get outpost status."""
        return self._make_request('GET', '/status')

    # Inventory Operations
    def get_inventory(self, category: Optional[str] = None) -> Optional[List[Dict]]:
        """Get inventory items."""
        params = {'category': category} if category else None
        return self._make_request('GET', '/inventory', params=params)

    def get_inventory_item(self, item_id: int) -> Optional[Dict]:
        """Get specific inventory item."""
        return self._make_request('GET', f'/inventory/{item_id}')

    def create_inventory_item(self, item_data: Dict) -> Optional[Dict]:
        """Create new inventory item."""
        return self._make_request('POST', '/inventory', json_data=item_data)

    def update_inventory_item(self, item_id: int, item_data: Dict) -> Optional[Dict]:
        """Update inventory item."""
        return self._make_request('PUT', f'/inventory/{item_id}', json_data=item_data)

    def delete_inventory_item(self, item_id: int) -> bool:
        """Delete inventory item."""
        result = self._make_request('DELETE', f'/inventory/{item_id}')
        return result is not None

    # Catch Records
    def get_catches(self, fish_type: Optional[str] = None) -> Optional[List[Dict]]:
        """Get catch records."""
        params = {'fish_type': fish_type} if fish_type else None
        return self._make_request('GET', '/catches', params=params)

    def get_catch_summary(self) -> Optional[Dict]:
        """Get catch summary statistics."""
        return self._make_request('GET', '/catches/summary')

    # File Operations
    def list_files(self) -> Optional[Dict]:
        """List uploaded files."""
        return self._make_request('GET', '/files/list')

    def upload_file(self, file_path: str) -> Optional[Dict]:
        """Upload a file to the outpost."""
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        with open(path, 'rb') as f:
            files = {'file': (path.name, f)}
            return self._make_request('POST', '/files/upload', files=files)

    def download_file(self, filename: str, destination: str) -> bool:
        """Download a file from the outpost."""
        response = self._make_request('GET', f'/files/download/{filename}')

        if response and hasattr(response, 'content'):
            with open(destination, 'wb') as f:
                f.write(response.content)
            return True

        return False

    def delete_file(self, filename: str) -> bool:
        """Delete a file from the outpost."""
        result = self._make_request('DELETE', f'/files/{filename}')
        return result is not None

    # Log Operations
    def list_logs(self) -> Optional[Dict]:
        """List available log files."""
        return self._make_request('GET', '/logs/list')

    def get_log_content(self, log_name: str, lines: int = 100) -> Optional[Dict]:
        """Get log file content."""
        params = {'lines': lines}
        return self._make_request('GET', f'/logs/{log_name}', params=params)

    # System Information
    def get_disk_usage(self) -> Optional[Dict]:
        """Get disk usage statistics."""
        return self._make_request('GET', '/system/disk-usage')

    def get_system_info(self) -> Optional[Dict]:
        """Get system information."""
        return self._make_request('GET', '/system/info')

    # ========================================================================
    # Protected Endpoints (Require Authentication)
    # ========================================================================

    def delete_inventory_item_protected(self, item_id: int) -> Optional[Dict]:
        """
        Delete an inventory item using protected endpoint (requires authentication).

        Educational Note:
        This demonstrates accessing a protected endpoint. The client must
        have a valid authentication token (obtained via login()) before
        calling this method.

        Args:
            item_id: ID of item to delete

        Returns:
            Deletion confirmation or None if failed

        Example:
            client = OutpostAPIClient("http://192.168.1.100:8000")
            if client.login("fort_commander", "frontier_pass123"):
                result = client.delete_inventory_item_protected(5)
                if result:
                    print(f"Deleted by: {result['deleted_by']}")
        """
        if not self.is_authenticated:
            logger.error("Cannot delete item: Not authenticated")
            return None

        return self._make_request('DELETE', f'/inventory/{item_id}/protected')

    def get_admin_stats(self) -> Optional[Dict]:
        """
        Get comprehensive admin statistics (requires authentication).

        Educational Note:
        This protected endpoint provides detailed system information.
        Only authenticated users can access this data.

        Returns:
            Dictionary containing inventory, catches, database, and system stats

        Example:
            client = OutpostAPIClient("http://192.168.1.100:8000")
            client.login("fort_commander", "frontier_pass123")
            stats = client.get_admin_stats()
            if stats:
                print(f"Total inventory value: ${stats['inventory']['total_value']:.2f}")
                print(f"Total catches: {stats['catches']['total_records']}")
        """
        if not self.is_authenticated:
            logger.error("Cannot get admin stats: Not authenticated")
            return None

        return self._make_request('GET', '/admin/stats')
