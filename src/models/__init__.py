"""
Data models for the Raspberry Pi Frontier project.

This package contains dataclasses and schemas for:
- Outposts (Raspberry Pi nodes)
- User profiles and progress tracking
- Inventory and thematic data
"""

from src.models.outpost import (
    Outpost,
    OutpostType,
    OutpostStatus,
    OutpostInventoryItem
)

from src.models.user import (
    UserProfile,
    ChapterProgress,
    ChapterStatus
)

__all__ = [
    # Outpost models
    'Outpost',
    'OutpostType',
    'OutpostStatus',
    'OutpostInventoryItem',
    # User models
    'UserProfile',
    'ChapterProgress',
    'ChapterStatus',
]
