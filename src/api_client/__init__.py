"""
API Client Module

Provides clients for interacting with Raspberry Pi outpost APIs.

Educational Note:
This module offers two client options:
- OutpostAPIClient: Base client with no caching
- CachedOutpostAPIClient: Performance-optimized client with intelligent caching

For most use cases, prefer CachedOutpostAPIClient for better performance.
"""

from .client import OutpostAPIClient
from .cached_client import CachedOutpostAPIClient, create_cached_client

__all__ = [
    'OutpostAPIClient',
    'CachedOutpostAPIClient',
    'create_cached_client'
]
