"""
HTTP Client for Raspberry Pi Outposts

Async HTTP client using httpx to fetch live data from Raspberry Pi outpost APIs.
"""

import logging
import httpx
from typing import Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class PiOutpostClient:
    """
    Async HTTP client for communicating with Raspberry Pi outpost APIs.

    Handles retries, timeouts, and error handling for robust communication.
    """

    def __init__(self, timeout: float = 10.0, max_retries: int = 2):
        """
        Initialize the outpost client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries

    async def fetch_live_data(self, outpost_url: str) -> Dict[str, Any]:
        """
        Fetch live data from a Raspberry Pi outpost.

        Args:
            outpost_url: Base URL of the outpost API

        Returns:
            Dict containing live sensor data or status

        Raises:
            httpx.RequestError: On network errors
            httpx.HTTPStatusError: On HTTP errors
        """
        retry_count = 0
        last_exception = None

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while retry_count <= self.max_retries:
                try:
                    logger.info(f"Fetching live data from {outpost_url} (attempt {retry_count + 1})")

                    response = await client.get(f"{outpost_url}/status")
                    response.raise_for_status()

                    data = response.json()
                    logger.info(f"Successfully fetched data from {outpost_url}")
                    return data

                except httpx.RequestError as e:
                    last_exception = e
                    logger.warning(f"Request error on attempt {retry_count + 1}: {e}")
                    retry_count += 1

                    if retry_count <= self.max_retries:
                        # Exponential backoff: 2^retry seconds
                        wait_time = 2 ** retry_count
                        logger.info(f"Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)

                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP error {e.response.status_code}: {e}")
                    raise

            # All retries exhausted
            logger.error(f"Failed to fetch data from {outpost_url} after {self.max_retries + 1} attempts")
            raise last_exception
