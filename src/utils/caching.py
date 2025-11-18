"""
Caching Utilities for Streamlit Performance Optimization

Educational Note:
Caching is crucial for performance in data-heavy applications. It:
1. Reduces redundant API calls and database queries
2. Speeds up UI responsiveness
3. Reduces server load
4. Improves user experience

Streamlit provides built-in caching decorators:
- @st.cache_data: For data that can be serialized (DataFrames, lists, dicts)
- @st.cache_resource: For resources that shouldn't be serialized (DB connections, models)

This module provides:
- Smart caching strategies
- Cache invalidation logic
- Time-based cache expiration
- Conditional caching based on app state
"""

import streamlit as st
import hashlib
import json
import time
from typing import Any, Callable, Optional, Dict, List
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Cache Configuration
# ============================================================================

class CacheConfig:
    """
    Global cache configuration.

    Educational Note:
    Centralized configuration makes it easy to tune caching behavior
    across the entire application.
    """
    # Default TTL (Time To Live) in seconds
    DEFAULT_TTL = 300  # 5 minutes

    # API data cache TTL
    API_DATA_TTL = 60  # 1 minute (API data changes frequently)

    # Static data cache TTL
    STATIC_DATA_TTL = 3600  # 1 hour (static data rarely changes)

    # Status check cache TTL
    STATUS_CHECK_TTL = 30  # 30 seconds (frequent status updates)

    # Enable/disable caching globally
    CACHING_ENABLED = True

    # Show cache statistics in UI
    SHOW_CACHE_STATS = False


# ============================================================================
# Cache Key Generation
# ============================================================================

def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a unique cache key from function arguments.

    Educational Note:
    Cache keys must be unique for different inputs but identical
    for the same inputs. We use hashing to create deterministic keys.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        SHA256 hash as cache key
    """
    # Combine args and kwargs into a single string
    key_data = {
        'args': args,
        'kwargs': kwargs
    }

    # Convert to JSON and hash
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    cache_key = hashlib.sha256(key_string.encode()).hexdigest()

    return cache_key


# ============================================================================
# Streamlit Cache Decorators
# ============================================================================

def cache_api_data(ttl: int = CacheConfig.API_DATA_TTL, show_spinner: bool = True):
    """
    Cache API data with configurable TTL.

    Educational Note:
    This decorator uses Streamlit's @st.cache_data which:
    1. Stores the function result
    2. Returns cached result for same inputs
    3. Automatically invalidates after TTL expires

    Usage:
        @cache_api_data(ttl=60)
        def fetch_inventory(outpost_id):
            return api_client.get_inventory(outpost_id)

    Args:
        ttl: Time to live in seconds
        show_spinner: Whether to show loading spinner

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @st.cache_data(ttl=ttl, show_spinner=show_spinner)
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CacheConfig.CACHING_ENABLED:
                return func(*args, **kwargs)

            logger.debug(f"Cache miss for {func.__name__} - fetching data")
            result = func(*args, **kwargs)
            logger.debug(f"Cached {func.__name__} for {ttl}s")
            return result

        return wrapper
    return decorator


def cache_static_data(ttl: int = CacheConfig.STATIC_DATA_TTL):
    """
    Cache static data that rarely changes.

    Educational Note:
    Static data (configuration, reference data) can be cached longer
    since it doesn't change frequently.

    Args:
        ttl: Time to live in seconds

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @st.cache_data(ttl=ttl, show_spinner=False)
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CacheConfig.CACHING_ENABLED:
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def cache_resource(show_spinner: bool = False):
    """
    Cache non-serializable resources like connections.

    Educational Note:
    @st.cache_resource is for objects that:
    1. Can't be serialized (database connections, ML models)
    2. Should be shared across reruns
    3. Need manual cleanup

    Usage:
        @cache_resource()
        def get_database_connection():
            return create_connection()

    Args:
        show_spinner: Whether to show loading spinner

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @st.cache_resource(show_spinner=show_spinner)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# Conditional Caching
# ============================================================================

def cache_if_demo_mode(ttl: int = CacheConfig.DEFAULT_TTL):
    """
    Only cache when in demo mode.

    Educational Note:
    Conditional caching allows different behavior in different modes.
    Demo mode can use cached data, while live mode fetches fresh data.

    Args:
        ttl: Time to live in seconds

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if in demo mode
            demo_mode = st.session_state.get('demo_mode', False)

            if demo_mode and CacheConfig.CACHING_ENABLED:
                # Use cached version
                cached_func = st.cache_data(ttl=ttl)(func)
                return cached_func(*args, **kwargs)
            else:
                # Call directly without caching
                return func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# Manual Cache Management
# ============================================================================

class CacheManager:
    """
    Manual cache management for fine-grained control.

    Educational Note:
    Sometimes you need manual cache control for:
    - Invalidating specific entries
    - Managing cache size
    - Custom expiration logic
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check if expired
        if datetime.now() > entry['expires_at']:
            logger.debug(f"Cache expired for key: {key}")
            del self._cache[key]
            return None

        logger.debug(f"Cache hit for key: {key}")
        return entry['value']

    def set(self, key: str, value: Any, ttl: int = CacheConfig.DEFAULT_TTL):
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        expires_at = datetime.now() + timedelta(seconds=ttl)

        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }

        logger.debug(f"Cached key: {key} (TTL: {ttl}s)")

    def invalidate(self, key: str):
        """
        Invalidate a specific cache entry.

        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Invalidated cache key: {key}")

    def invalidate_all(self):
        """Invalidate all cache entries."""
        self._cache.clear()
        logger.info("Cleared all cache entries")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total_entries = len(self._cache)
        expired_count = 0

        now = datetime.now()
        for entry in self._cache.values():
            if now > entry['expires_at']:
                expired_count += 1

        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_count,
            'expired_entries': expired_count
        }


# Global cache manager instance
cache_manager = CacheManager()


# ============================================================================
# Session State Caching
# ============================================================================

def cache_in_session(key: str, ttl: Optional[int] = None):
    """
    Cache data in Streamlit session state.

    Educational Note:
    Session state is per-user and persists across reruns.
    It's perfect for user-specific cached data.

    Args:
        key: Session state key
        ttl: Optional time to live in seconds

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"_cache_{key}_{generate_cache_key(*args, **kwargs)}"

            # Check if cached in session state
            if cache_key in st.session_state:
                cached_data = st.session_state[cache_key]

                # Check TTL if specified
                if ttl is not None:
                    cache_time = cached_data.get('timestamp', 0)
                    if time.time() - cache_time > ttl:
                        # Expired
                        logger.debug(f"Session cache expired: {cache_key}")
                        del st.session_state[cache_key]
                    else:
                        logger.debug(f"Session cache hit: {cache_key}")
                        return cached_data['value']
                else:
                    logger.debug(f"Session cache hit: {cache_key}")
                    return cached_data['value']

            # Cache miss - compute value
            logger.debug(f"Session cache miss: {cache_key}")
            value = func(*args, **kwargs)

            # Store in session state
            st.session_state[cache_key] = {
                'value': value,
                'timestamp': time.time()
            }

            return value

        return wrapper
    return decorator


# ============================================================================
# Cache Invalidation Helpers
# ============================================================================

def invalidate_cache_on_change(watch_key: str):
    """
    Invalidate cache when a watched session state key changes.

    Educational Note:
    Cache invalidation is critical when data changes.
    This decorator automatically invalidates cache when
    a specific session state value changes.

    Args:
        watch_key: Session state key to watch

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get current value of watched key
            current_value = st.session_state.get(watch_key)

            # Generate cache key
            cache_key = f"_cache_{func.__name__}_{generate_cache_key(*args, **kwargs)}"
            watch_value_key = f"{cache_key}_watch"

            # Check if watched value changed
            if watch_value_key in st.session_state:
                if st.session_state[watch_value_key] != current_value:
                    # Value changed - invalidate cache
                    logger.debug(f"Watched key '{watch_key}' changed - invalidating cache")
                    if cache_key in st.session_state:
                        del st.session_state[cache_key]

            # Store current watch value
            st.session_state[watch_value_key] = current_value

            # Check cache
            if cache_key in st.session_state:
                return st.session_state[cache_key]

            # Compute and cache
            result = func(*args, **kwargs)
            st.session_state[cache_key] = result

            return result

        return wrapper
    return decorator


def clear_all_caches():
    """
    Clear all Streamlit caches.

    Educational Note:
    Sometimes you need to clear all caches (e.g., on logout,
    configuration change, or manual refresh).
    """
    st.cache_data.clear()
    st.cache_resource.clear()
    cache_manager.invalidate_all()

    # Clear session state caches
    cache_keys = [key for key in st.session_state.keys() if key.startswith('_cache_')]
    for key in cache_keys:
        del st.session_state[key]

    logger.info("Cleared all caches")


# ============================================================================
# Cache Statistics UI Component
# ============================================================================

def display_cache_stats():
    """
    Display cache statistics in the UI.

    Educational Note:
    Showing cache stats helps with:
    - Performance monitoring
    - Debugging cache issues
    - Understanding cache effectiveness
    """
    if not CacheConfig.SHOW_CACHE_STATS:
        return

    with st.expander("📊 Cache Statistics", expanded=False):
        stats = cache_manager.get_stats()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Entries", stats['total_entries'])

        with col2:
            st.metric("Active Entries", stats['active_entries'])

        with col3:
            st.metric("Expired Entries", stats['expired_entries'])

        if st.button("🗑️ Clear All Caches"):
            clear_all_caches()
            st.success("✅ All caches cleared!")
            st.rerun()


# ============================================================================
# Smart Refresh Strategies
# ============================================================================

class SmartRefresh:
    """
    Intelligent refresh strategies for data.

    Educational Note:
    Different data has different refresh requirements:
    - Critical data: Refresh frequently
    - Static data: Refresh rarely
    - User-requested: Refresh on demand
    """

    @staticmethod
    def should_refresh(
        last_refresh: Optional[datetime],
        min_interval: int = 30,
        force: bool = False
    ) -> bool:
        """
        Determine if data should be refreshed.

        Args:
            last_refresh: Last refresh timestamp
            min_interval: Minimum interval between refreshes (seconds)
            force: Force refresh regardless of interval

        Returns:
            True if should refresh
        """
        if force:
            return True

        if last_refresh is None:
            return True

        elapsed = (datetime.now() - last_refresh).total_seconds()
        return elapsed >= min_interval

    @staticmethod
    def refresh_on_interval(interval: int = 60):
        """
        Decorator to refresh data on time interval.

        Args:
            interval: Refresh interval in seconds

        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = f"_refresh_{func.__name__}"

                last_refresh = st.session_state.get(key)

                if SmartRefresh.should_refresh(last_refresh, interval):
                    result = func(*args, **kwargs)
                    st.session_state[key] = datetime.now()
                    return result

                # Use cached data
                cache_key = f"_data_{func.__name__}"
                return st.session_state.get(cache_key)

            return wrapper
        return decorator


# ============================================================================
# Performance Monitoring
# ============================================================================

def monitor_performance(func: Callable) -> Callable:
    """
    Monitor function execution time.

    Educational Note:
    Performance monitoring helps identify slow operations
    that need caching or optimization.

    Args:
        func: Function to monitor

    Returns:
        Wrapped function with timing
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time

        if elapsed > 1.0:  # Log if takes more than 1 second
            logger.warning(
                f"{func.__name__} took {elapsed:.2f}s - consider caching"
            )
        else:
            logger.debug(f"{func.__name__} completed in {elapsed:.3f}s")

        return result

    return wrapper
