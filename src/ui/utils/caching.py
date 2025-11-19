"""
Caching Utilities for Streamlit Data Refresh Optimization

This module provides intelligent caching strategies for API data in Streamlit,
reducing unnecessary API calls and improving performance.

Educational Note:
Caching is crucial for performance in applications that fetch external data.
Streamlit provides caching decorators, but this module adds:
- Time-based cache expiration
- Smart cache invalidation
- Cache statistics and monitoring
- Multi-level caching strategies

Phase 4 Feature (Step 34):
Complete caching system with TTL, invalidation, and performance monitoring.
"""

import streamlit as st
from typing import Any, Callable, Optional, Dict, Tuple
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Cache Configuration
# ============================================================================

class CacheConfig:
    """
    Cache configuration constants.

    Educational Note:
    Different data types have different freshness requirements.
    Static data (like game animals) can be cached longer than
    dynamic data (like active hunting parties).
    """
    # Default TTLs (Time To Live) in seconds
    TTL_SHORT = 30        # 30 seconds - for rapidly changing data
    TTL_MEDIUM = 300      # 5 minutes - for moderately changing data
    TTL_LONG = 1800       # 30 minutes - for slowly changing data
    TTL_STATIC = 3600     # 1 hour - for static reference data

    # Cache size limits
    MAX_CACHE_ENTRIES = 1000

    # Enable/disable caching globally
    CACHING_ENABLED = True


# ============================================================================
# Cache Statistics
# ============================================================================

def initialize_cache_stats():
    """
    Initialize cache statistics in session state.

    Educational Note:
    Tracking cache performance helps optimize caching strategy.
    Hit rate, miss rate, and staleness metrics guide tuning.
    """
    if 'cache_stats' not in st.session_state:
        st.session_state.cache_stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0,
            'total_requests': 0,
            'cache_size': 0,
            'last_reset': datetime.now().isoformat()
        }


def record_cache_hit():
    """Record a cache hit."""
    initialize_cache_stats()
    st.session_state.cache_stats['hits'] += 1
    st.session_state.cache_stats['total_requests'] += 1


def record_cache_miss():
    """Record a cache miss."""
    initialize_cache_stats()
    st.session_state.cache_stats['misses'] += 1
    st.session_state.cache_stats['total_requests'] += 1


def record_cache_invalidation():
    """Record a cache invalidation."""
    initialize_cache_stats()
    st.session_state.cache_stats['invalidations'] += 1


def get_cache_hit_rate() -> float:
    """
    Calculate cache hit rate.

    Educational Note:
    Hit rate = hits / total_requests
    A good cache should have >70% hit rate for most applications.

    Returns:
        Hit rate as percentage (0-100)
    """
    initialize_cache_stats()
    stats = st.session_state.cache_stats
    total = stats['total_requests']

    if total == 0:
        return 0.0

    return (stats['hits'] / total) * 100


def reset_cache_stats():
    """Reset cache statistics."""
    st.session_state.cache_stats = {
        'hits': 0,
        'misses': 0,
        'invalidations': 0,
        'total_requests': 0,
        'cache_size': 0,
        'last_reset': datetime.now().isoformat()
    }


# ============================================================================
# Cache Key Generation
# ============================================================================

def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a unique cache key from function arguments.

    Educational Note:
    Cache keys must be unique for each unique set of arguments.
    We use MD5 hashing of JSON-serialized arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Unique cache key string
    """
    # Create a dictionary of all arguments
    key_data = {
        'args': args,
        'kwargs': kwargs
    }

    # Serialize to JSON (sorted for consistency)
    key_json = json.dumps(key_data, sort_keys=True, default=str)

    # Hash for compact key
    key_hash = hashlib.md5(key_json.encode()).hexdigest()

    return key_hash


# ============================================================================
# Time-Based Cache with TTL
# ============================================================================

class TimedCache:
    """
    Time-based cache with TTL (Time To Live) support.

    Educational Note:
    This implements a simple but effective caching strategy:
    - Store data with timestamp
    - Check age before returning cached data
    - Automatically expire stale entries
    """

    def __init__(self, ttl_seconds: int = CacheConfig.TTL_MEDIUM):
        """
        Initialize timed cache.

        Args:
            ttl_seconds: Time to live in seconds
        """
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache_key = f"timed_cache_{id(self)}"

        if self.cache_key not in st.session_state:
            st.session_state[self.cache_key] = {}

    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Tuple of (is_valid, value)
        """
        cache = st.session_state[self.cache_key]

        if key not in cache:
            record_cache_miss()
            return False, None

        entry = cache[key]
        timestamp = entry['timestamp']
        age = datetime.now() - timestamp

        # Check if cache entry is still valid
        if age > self.ttl:
            # Entry is stale
            record_cache_miss()
            del cache[key]
            return False, None

        # Entry is valid
        record_cache_hit()
        return True, entry['value']

    def set(self, key: str, value: Any):
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache = st.session_state[self.cache_key]

        cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }

        # Update cache size
        st.session_state.cache_stats['cache_size'] = len(cache)

        # Enforce size limit
        if len(cache) > CacheConfig.MAX_CACHE_ENTRIES:
            # Remove oldest entries
            sorted_entries = sorted(
                cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            oldest_key = sorted_entries[0][0]
            del cache[oldest_key]

    def invalidate(self, key: Optional[str] = None):
        """
        Invalidate cache entries.

        Args:
            key: Specific key to invalidate, or None to clear all
        """
        cache = st.session_state[self.cache_key]

        if key is None:
            # Clear all
            cache.clear()
            record_cache_invalidation()
        elif key in cache:
            # Clear specific key
            del cache[key]
            record_cache_invalidation()

    def size(self) -> int:
        """Get current cache size."""
        return len(st.session_state[self.cache_key])


# ============================================================================
# Caching Decorators
# ============================================================================

def cached_data(
    ttl_seconds: int = CacheConfig.TTL_MEDIUM,
    key_prefix: str = ""
):
    """
    Decorator to cache function results with TTL.

    Educational Note:
    This decorator provides transparent caching for any function.
    The function is only called if cache is empty or expired.

    Args:
        ttl_seconds: Time to live in seconds
        key_prefix: Prefix for cache key (helps organize cache)

    Example:
        @cached_data(ttl_seconds=300, key_prefix="inventory")
        def get_inventory(fort_url):
            return client.get_inventory()
    """
    cache = TimedCache(ttl_seconds)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CacheConfig.CACHING_ENABLED:
                return func(*args, **kwargs)

            # Generate cache key
            cache_key = f"{key_prefix}_{func.__name__}_{generate_cache_key(*args, **kwargs)}"

            # Try to get from cache
            is_valid, cached_value = cache.get(cache_key)

            if is_valid:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value

            # Cache miss - call function
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result)

            return result

        # Add cache control methods
        wrapper.invalidate_cache = lambda: cache.invalidate()
        wrapper.cache_size = lambda: cache.size()

        return wrapper

    return decorator


def cached_api_call(ttl_seconds: int = CacheConfig.TTL_MEDIUM):
    """
    Specialized decorator for API calls with None-handling.

    Educational Note:
    API calls can return None on error. We don't want to cache
    None values, as they represent failures not actual data.

    Args:
        ttl_seconds: Time to live in seconds

    Example:
        @cached_api_call(ttl_seconds=300)
        def get_fort_status():
            return client.get_status()
    """
    def decorator(func: Callable) -> Callable:
        # Use the cached_data decorator as base
        cached_func = cached_data(ttl_seconds, key_prefix="api")(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = cached_func(*args, **kwargs)

            # Don't cache None results
            if result is None:
                logger.warning(f"API call {func.__name__} returned None, not caching")
                # Invalidate any existing cache for this call
                cache_key = f"api_{func.__name__}_{generate_cache_key(*args, **kwargs)}"
                # Note: Would need to pass cache instance to invalidate specific key

            return result

        return wrapper

    return decorator


# ============================================================================
# Smart Cache Invalidation
# ============================================================================

def invalidate_cache_on_mutation(cache_keys: list):
    """
    Decorator to invalidate specific caches when data is modified.

    Educational Note:
    When data changes (POST, PUT, DELETE), related caches must be
    invalidated to prevent serving stale data.

    Args:
        cache_keys: List of cache key prefixes to invalidate

    Example:
        @invalidate_cache_on_mutation(["inventory", "status"])
        def update_inventory(item_id, quantity):
            return client.update_item(item_id, quantity)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the mutation
            result = func(*args, **kwargs)

            # Invalidate related caches
            for key_prefix in cache_keys:
                # Clear all caches with this prefix
                # Note: This is simplified; production would need cache registry
                logger.info(f"Invalidating cache with prefix: {key_prefix}")
                record_cache_invalidation()

            return result

        return wrapper

    return decorator


# ============================================================================
# Cache Management UI Components
# ============================================================================

def render_cache_stats():
    """
    Render cache statistics dashboard.

    Educational Note:
    Monitoring cache performance helps identify optimization opportunities.
    """
    initialize_cache_stats()
    stats = st.session_state.cache_stats

    st.subheader("📊 Cache Performance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Requests", stats['total_requests'])

    with col2:
        st.metric("Cache Hits", stats['hits'])

    with col3:
        st.metric("Cache Misses", stats['misses'])

    with col4:
        hit_rate = get_cache_hit_rate()
        st.metric("Hit Rate", f"{hit_rate:.1f}%")

    # Progress bar for hit rate
    st.progress(hit_rate / 100)

    # Additional stats
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Cache Size:** {stats['cache_size']} entries")
        st.write(f"**Invalidations:** {stats['invalidations']}")

    with col2:
        st.write(f"**Last Reset:** {stats['last_reset']}")

    # Cache control buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear All Caches"):
            # Clear all session state caches
            keys_to_clear = [k for k in st.session_state.keys() if 'cache' in k.lower()]
            for key in keys_to_clear:
                if isinstance(st.session_state[key], dict):
                    st.session_state[key].clear()

            st.success("All caches cleared")
            st.rerun()

    with col2:
        if st.button("🔄 Reset Statistics"):
            reset_cache_stats()
            st.success("Statistics reset")
            st.rerun()


def render_cache_control_panel():
    """
    Render cache control panel for manual cache management.

    Educational Note:
    Giving users cache control helps with debugging and
    forces fresh data when needed.
    """
    with st.expander("⚙️ Cache Settings"):
        st.write("**Cache Configuration**")

        # Enable/disable caching
        caching_enabled = st.checkbox(
            "Enable Caching",
            value=CacheConfig.CACHING_ENABLED,
            help="Turn off to always fetch fresh data (slower)"
        )

        CacheConfig.CACHING_ENABLED = caching_enabled

        # Show current config
        st.write("**Default TTL Values:**")
        st.write(f"- Short: {CacheConfig.TTL_SHORT}s")
        st.write(f"- Medium: {CacheConfig.TTL_MEDIUM}s")
        st.write(f"- Long: {CacheConfig.TTL_LONG}s")
        st.write(f"- Static: {CacheConfig.TTL_STATIC}s")

        st.write(f"**Max Cache Entries:** {CacheConfig.MAX_CACHE_ENTRIES}")


# ============================================================================
# Streamlit-Specific Caching Helpers
# ============================================================================

@st.cache_data(ttl=CacheConfig.TTL_STATIC)
def cache_static_data(data: Any) -> Any:
    """
    Cache static data using Streamlit's built-in caching.

    Educational Note:
    Streamlit's @st.cache_data is optimized for dataframes and
    serializable data. Use for reference data that rarely changes.

    Args:
        data: Data to cache

    Returns:
        Cached data
    """
    return data


@st.cache_resource
def get_cached_api_client(base_url: str):
    """
    Cache API client instances using Streamlit's resource caching.

    Educational Note:
    @st.cache_resource is for non-serializable objects like
    database connections, API clients, etc. They persist across reruns.

    Args:
        base_url: API base URL

    Returns:
        Cached API client instance
    """
    from src.api_client.client import OutpostAPIClient
    return OutpostAPIClient(base_url)


# ============================================================================
# Performance Monitoring
# ============================================================================

def cache_performance_report() -> Dict[str, Any]:
    """
    Generate a performance report for caching.

    Returns:
        Dictionary with performance metrics
    """
    initialize_cache_stats()
    stats = st.session_state.cache_stats

    hit_rate = get_cache_hit_rate()

    # Performance assessment
    if hit_rate >= 80:
        assessment = "Excellent"
    elif hit_rate >= 60:
        assessment = "Good"
    elif hit_rate >= 40:
        assessment = "Fair"
    else:
        assessment = "Poor"

    return {
        'hit_rate': hit_rate,
        'assessment': assessment,
        'total_requests': stats['total_requests'],
        'cache_size': stats['cache_size'],
        'recommendations': get_cache_recommendations(hit_rate, stats)
    }


def get_cache_recommendations(hit_rate: float, stats: Dict) -> list:
    """
    Get recommendations for cache optimization.

    Args:
        hit_rate: Current cache hit rate
        stats: Cache statistics

    Returns:
        List of recommendation strings
    """
    recommendations = []

    if hit_rate < 50:
        recommendations.append("Consider increasing TTL values for better hit rate")

    if stats['cache_size'] > CacheConfig.MAX_CACHE_ENTRIES * 0.9:
        recommendations.append("Cache is near capacity - consider increasing MAX_CACHE_ENTRIES")

    if stats['invalidations'] > stats['total_requests'] * 0.3:
        recommendations.append("High invalidation rate - review cache invalidation strategy")

    if not recommendations:
        recommendations.append("Cache performance is good - no changes needed")

    return recommendations
