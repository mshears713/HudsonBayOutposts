"""
Reusable API Client Module for Raspberry Pi Outposts

This module provides a clean abstraction layer for interacting with
outpost APIs, handling common tasks like error handling, retries,
and response parsing.

Educational Note:
API clients abstract the complexity of HTTP requests and provide a
clean Python interface. This makes code more maintainable and testable.
"""

import requests
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class OutpostAPIClient:
    """
    Client for interacting with Raspberry Pi outpost APIs.

    Educational Note:
    This class follows the Single Responsibility Principle - it handles
    all API communication logic in one place.
    """

    def __init__(self, base_url: str, timeout: int = 10):
        """
        Initialize API client.

        Args:
            base_url: Base URL of the outpost API (e.g., http://192.168.1.100:8000)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Optional[Any]:
        """
        Make an HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body data
            files: Files for upload

        Returns:
            Response data or None if failed
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Return JSON if content type is JSON
            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()
            else:
                return response

        except requests.exceptions.Timeout:
            logger.error(f"Request timed out: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection failed: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
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
