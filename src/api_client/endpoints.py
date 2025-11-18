"""
API Endpoint abstractions and helpers.

This module provides convenient functions for common API operations
across multiple outposts.

Educational Note:
These utility functions demonstrate composition - building complex
operations from simple client methods.
"""

from typing import List, Dict, Any, Optional
from .client import OutpostAPIClient


def get_all_inventory_across_outposts(clients: List[OutpostAPIClient]) -> Dict[str, List]:
    """
    Fetch inventory from multiple outposts.

    Args:
        clients: List of API clients for different outposts

    Returns:
        Dictionary mapping client index to inventory data

    Educational Note:
    This demonstrates a multi-endpoint workflow - fetching data
    from multiple distributed nodes.
    """
    results = {}

    for i, client in enumerate(clients):
        inventory = client.get_inventory()
        if inventory:
            results[f"outpost_{i}"] = inventory

    return results


def get_combined_status(clients: List[OutpostAPIClient]) -> List[Dict]:
    """
    Get status from all outposts.

    Args:
        clients: List of API clients

    Returns:
        List of status dictionaries
    """
    statuses = []

    for client in clients:
        status = client.get_status()
        if status:
            status['api_url'] = client.base_url
            statuses.append(status)

    return statuses


def aggregate_catch_summaries(clients: List[OutpostAPIClient]) -> Dict[str, Any]:
    """
    Aggregate catch statistics across multiple fishing outposts.

    Args:
        clients: List of API clients for fishing outposts

    Returns:
        Aggregated catch statistics
    """
    all_summaries = []
    total_catches = 0

    for client in clients:
        summary = client.get_catch_summary()
        if summary:
            all_summaries.append(summary)
            total_catches += len(summary.get('summary', []))

    return {
        'outpost_count': len(all_summaries),
        'total_fish_types': total_catches,
        'summaries': all_summaries
    }
