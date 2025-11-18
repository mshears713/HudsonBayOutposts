"""
Cached API Client with Performance Optimization

Educational Note:
This module extends the base OutpostAPIClient with intelligent caching.
Caching reduces redundant API calls, improving performance and reducing
server load.

Key Concepts:
- Different cache durations for different data types
- Conditional caching (only cache in demo mode, etc.)
- Manual cache invalidation when data changes
- Cache statistics for monitoring

Usage:
    # Instead of OutpostAPIClient, use CachedOutpostAPIClient
    client = CachedOutpostAPIClient("http://192.168.1.100:8000")

    # First call - fetches from API
    status = client.get_status()

    # Second call within TTL - returns cached data
    status = client.get_status()  # Instant!
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from .client import OutpostAPIClient
from ..utils.caching import (
    cache_api_data,
    cache_static_data,
    cache_if_demo_mode,
    CacheConfig,
    cache_manager,
    monitor_performance
)

logger = logging.getLogger(__name__)


class CachedOutpostAPIClient(OutpostAPIClient):
    """
    API Client with intelligent caching for improved performance.

    Educational Note:
    This class extends OutpostAPIClient by wrapping methods with
    caching decorators. Methods are cached based on their data type:
    - Status/health: Short TTL (frequent updates)
    - Inventory: Medium TTL (changes occasionally)
    - Static data: Long TTL (rarely changes)
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize cached API client.

        Args:
            Same as OutpostAPIClient
        """
        super().__init__(*args, **kwargs)
        logger.info("Initialized CachedOutpostAPIClient with caching enabled")

    def invalidate_cache(self, cache_type: str = "all"):
        """
        Manually invalidate caches.

        Educational Note:
        Call this when you know data has changed and want to
        force fresh data on the next request.

        Args:
            cache_type: Type of cache to invalidate
                - "all": Clear all caches
                - "status": Clear status caches
                - "inventory": Clear inventory caches
                - "catches": Clear catch caches

        Example:
            # After updating inventory
            client.create_inventory_item(new_item)
            client.invalidate_cache("inventory")  # Force refresh
        """
        if cache_type == "all":
            st.cache_data.clear()
            logger.info("Cleared all API caches")
        else:
            # Streamlit doesn't support selective clearing by default
            # But we can clear session state caches
            cache_keys = [
                key for key in st.session_state.keys()
                if key.startswith(f'_cache_') and cache_type in key
            ]
            for key in cache_keys:
                del st.session_state[key]
            logger.info(f"Cleared {cache_type} caches ({len(cache_keys)} entries)")

    # ========================================================================
    # Cached Health and Status Methods
    # ========================================================================

    @cache_api_data(ttl=CacheConfig.STATUS_CHECK_TTL)
    @monitor_performance
    def health_check(self) -> Optional[Dict[str, Any]]:
        """
        Get API health status (cached for 30 seconds).

        Educational Note:
        Health checks are cached briefly since we want relatively
        fresh status information but don't need real-time updates.
        """
        return super().health_check()

    @cache_api_data(ttl=CacheConfig.STATUS_CHECK_TTL)
    @monitor_performance
    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get outpost status (cached for 30 seconds).

        Educational Note:
        Status data changes frequently but not constantly.
        A 30-second cache balances freshness with performance.
        """
        return super().get_status()

    # ========================================================================
    # Cached Inventory Methods
    # ========================================================================

    @cache_api_data(ttl=CacheConfig.API_DATA_TTL)
    @monitor_performance
    def get_inventory(self, category: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Get inventory items (cached for 1 minute).

        Educational Note:
        Inventory data is cached for 1 minute. If you modify inventory,
        call invalidate_cache("inventory") to force a refresh.

        Args:
            category: Optional category filter

        Returns:
            List of inventory items
        """
        return super().get_inventory(category)

    @cache_api_data(ttl=CacheConfig.API_DATA_TTL)
    def get_inventory_item(self, item_id: int) -> Optional[Dict]:
        """
        Get specific inventory item (cached).

        Args:
            item_id: Item ID

        Returns:
            Item data or None
        """
        return super().get_inventory_item(item_id)

    def create_inventory_item(self, item_data: Dict) -> Optional[Dict]:
        """
        Create inventory item and invalidate cache.

        Educational Note:
        When creating new items, we invalidate the inventory cache
        so subsequent get_inventory() calls return fresh data.
        """
        result = super().create_inventory_item(item_data)
        if result:
            self.invalidate_cache("inventory")
            logger.debug("Invalidated inventory cache after creation")
        return result

    def update_inventory_item(self, item_id: int, item_data: Dict) -> Optional[Dict]:
        """
        Update inventory item and invalidate cache.

        Educational Note:
        Updates invalidate cache to ensure consistency.
        """
        result = super().update_inventory_item(item_id, item_data)
        if result:
            self.invalidate_cache("inventory")
            logger.debug("Invalidated inventory cache after update")
        return result

    def delete_inventory_item(self, item_id: int) -> bool:
        """
        Delete inventory item and invalidate cache.

        Educational Note:
        Deletions invalidate cache to prevent showing deleted items.
        """
        result = super().delete_inventory_item(item_id)
        if result:
            self.invalidate_cache("inventory")
            logger.debug("Invalidated inventory cache after deletion")
        return result

    # ========================================================================
    # Cached Catch Records Methods
    # ========================================================================

    @cache_api_data(ttl=CacheConfig.API_DATA_TTL)
    @monitor_performance
    def get_catches(self, fish_type: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Get catch records (cached for 1 minute).

        Args:
            fish_type: Optional fish type filter

        Returns:
            List of catch records
        """
        return super().get_catches(fish_type)

    @cache_api_data(ttl=CacheConfig.API_DATA_TTL)
    def get_catch_summary(self) -> Optional[Dict]:
        """
        Get catch summary statistics (cached).

        Educational Note:
        Summary data is relatively expensive to compute (aggregations),
        so caching provides significant performance improvement.
        """
        return super().get_catch_summary()

    # ========================================================================
    # Cached File Operations
    # ========================================================================

    @cache_api_data(ttl=CacheConfig.API_DATA_TTL)
    def list_files(self) -> Optional[Dict]:
        """
        List uploaded files (cached for 1 minute).

        Returns:
            Dict with file list
        """
        return super().list_files()

    def upload_file(self, file_path: str) -> Optional[Dict]:
        """
        Upload file and invalidate file list cache.

        Args:
            file_path: Path to file to upload

        Returns:
            Upload result
        """
        result = super().upload_file(file_path)
        if result:
            # Invalidate file list cache
            st.cache_data.clear()
            logger.debug("Invalidated file list cache after upload")
        return result

    def delete_file(self, filename: str) -> bool:
        """
        Delete file and invalidate cache.

        Args:
            filename: Name of file to delete

        Returns:
            True if successful
        """
        result = super().delete_file(filename)
        if result:
            st.cache_data.clear()
            logger.debug("Invalidated file list cache after deletion")
        return result

    # ========================================================================
    # Cached Log Operations
    # ========================================================================

    @cache_api_data(ttl=CacheConfig.API_DATA_TTL)
    def list_logs(self) -> Optional[Dict]:
        """
        List available logs (cached).

        Educational Note:
        Available logs rarely change, so this can be cached longer.
        """
        return super().list_logs()

    @cache_api_data(ttl=30)  # Cache log content for 30 seconds
    def get_log_content(self, log_name: str, lines: int = 100) -> Optional[Dict]:
        """
        Get log content (cached briefly).

        Educational Note:
        Logs are cached briefly because they update frequently.
        Users can force refresh by changing the lines parameter.

        Args:
            log_name: Name of log file
            lines: Number of lines to retrieve

        Returns:
            Log content
        """
        return super().get_log_content(log_name, lines)

    # ========================================================================
    # Cached System Information
    # ========================================================================

    @cache_api_data(ttl=CacheConfig.STATUS_CHECK_TTL)
    def get_disk_usage(self) -> Optional[Dict]:
        """
        Get disk usage (cached for 30 seconds).

        Educational Note:
        Disk usage changes slowly, so short caching is fine.
        """
        return super().get_disk_usage()

    @cache_static_data(ttl=CacheConfig.STATIC_DATA_TTL)
    def get_system_info(self) -> Optional[Dict]:
        """
        Get system information (cached for 1 hour).

        Educational Note:
        System info (OS, hardware) rarely changes, so we can
        cache it for a long time.
        """
        return super().get_system_info()

    # ========================================================================
    # Cached Protected Endpoints
    # ========================================================================

    @monitor_performance
    def delete_inventory_item_protected(self, item_id: int) -> Optional[Dict]:
        """
        Delete item via protected endpoint and invalidate cache.

        Args:
            item_id: ID of item to delete

        Returns:
            Deletion result
        """
        result = super().delete_inventory_item_protected(item_id)
        if result:
            self.invalidate_cache("inventory")
            logger.debug("Invalidated inventory cache after protected deletion")
        return result

    @cache_api_data(ttl=CacheConfig.API_DATA_TTL)
    @monitor_performance
    def get_admin_stats(self) -> Optional[Dict]:
        """
        Get admin statistics (cached for 1 minute).

        Educational Note:
        Admin stats aggregate multiple data sources, making them
        expensive to compute. Caching significantly improves performance.

        Returns:
            Comprehensive statistics
        """
        return super().get_admin_stats()

    # ========================================================================
    # Authentication Methods (No Caching)
    # ========================================================================

    def login(self, username: str, password: str) -> bool:
        """
        Login (not cached).

        Educational Note:
        Authentication requests should NEVER be cached for security reasons.
        Each login attempt must be verified with the server.
        """
        result = super().login(username, password)
        if result:
            # Clear all caches on login (user context may have changed)
            st.cache_data.clear()
            logger.info("Cleared all caches after login")
        return result

    def clear_token(self):
        """
        Logout and clear caches.

        Educational Note:
        On logout, we clear caches to prevent showing data from
        the previous user session.
        """
        super().clear_token()
        st.cache_data.clear()
        logger.info("Cleared all caches after logout")

    # ========================================================================
    # Cache Management Helpers
    # ========================================================================

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.

        Educational Note:
        Monitoring cache hits/misses helps tune cache settings.

        Returns:
            Dict with cache statistics
        """
        return cache_manager.get_stats()

    def warm_cache(self):
        """
        Pre-load commonly accessed data into cache.

        Educational Note:
        Cache warming loads frequently-accessed data before users
        request it, improving perceived performance.

        Example:
            # On app startup
            client = CachedOutpostAPIClient("http://...")
            client.login("user", "pass")
            client.warm_cache()  # Pre-load common data
        """
        logger.info("Warming cache with common data...")

        try:
            # Load common endpoints that users typically access first
            self.health_check()
            self.get_status()
            self.get_inventory()
            self.list_files()

            logger.info("Cache warming completed successfully")
        except Exception as e:
            logger.warning(f"Cache warming failed: {e}")
            # Don't raise - cache warming is optional

    @property
    def cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        return CacheConfig.CACHING_ENABLED

    def enable_cache(self):
        """Enable caching globally."""
        CacheConfig.CACHING_ENABLED = True
        logger.info("Caching enabled")

    def disable_cache(self):
        """
        Disable caching globally.

        Educational Note:
        Useful for debugging or when you need guaranteed fresh data.
        """
        CacheConfig.CACHING_ENABLED = False
        st.cache_data.clear()
        logger.info("Caching disabled and cleared")


# ============================================================================
# Convenience Function
# ============================================================================

def create_cached_client(
    base_url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    warm_cache: bool = False
) -> CachedOutpostAPIClient:
    """
    Factory function to create and configure a cached API client.

    Educational Note:
    Factory functions provide a convenient way to create objects with
    common configuration patterns.

    Args:
        base_url: Outpost API URL
        username: Optional username for auto-login
        password: Optional password for auto-login
        warm_cache: Whether to pre-load cache

    Returns:
        Configured CachedOutpostAPIClient

    Example:
        # Create client with auto-login and cache warming
        client = create_cached_client(
            "http://192.168.1.100:8000",
            username="fort_commander",
            password="frontier_pass123",
            warm_cache=True
        )
    """
    client = CachedOutpostAPIClient(base_url)

    # Auto-login if credentials provided
    if username and password:
        if client.login(username, password):
            logger.info(f"Auto-login successful for {username}")

            # Warm cache if requested
            if warm_cache:
                client.warm_cache()
        else:
            logger.warning(f"Auto-login failed for {username}")

    return client
