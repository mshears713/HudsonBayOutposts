"""
Outpost data models representing Hudson Bay Company frontier forts.

This module defines the data structures for outposts (Raspberry Pi nodes) in the
distributed learning system. Each outpost represents a thematic frontier fort
with unique APIs and data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class OutpostType(Enum):
    """Thematic types for different outpost forts."""
    FISHING = "fishing"
    HUNTING = "hunting"
    TRADING = "trading"
    EXPLORATION = "exploration"


class OutpostStatus(Enum):
    """Current operational status of an outpost."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class Outpost:
    """
    Represents a single Raspberry Pi outpost in the frontier network.

    Attributes:
        name: Human-readable name of the outpost (e.g., "Fort William")
        outpost_type: Thematic category of the outpost
        ip_address: Network IP address for API access
        port: Port number for the FastAPI server (default: 8000)
        ssh_port: SSH port for remote access (default: 22)
        status: Current operational status
        api_base_url: Computed base URL for API endpoints
        last_seen: Timestamp of last successful connection
        metadata: Additional thematic or custom data about the outpost
    """

    name: str
    outpost_type: OutpostType
    ip_address: str
    port: int = 8000
    ssh_port: int = 22
    status: OutpostStatus = OutpostStatus.OFFLINE
    last_seen: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def api_base_url(self) -> str:
        """Construct the base URL for API endpoints."""
        return f"http://{self.ip_address}:{self.port}"

    @property
    def is_online(self) -> bool:
        """Check if the outpost is currently online."""
        return self.status == OutpostStatus.ONLINE

    def update_status(self, status: OutpostStatus) -> None:
        """
        Update the outpost status and timestamp.

        Args:
            status: New status to set
        """
        self.status = status
        if status == OutpostStatus.ONLINE:
            self.last_seen = datetime.now()

    def get_endpoint_url(self, endpoint: str) -> str:
        """
        Construct full URL for a specific API endpoint.

        Args:
            endpoint: The endpoint path (e.g., "/inventory" or "inventory")

        Returns:
            Full URL including base URL and endpoint
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith('/'):
            endpoint = f'/{endpoint}'
        return f"{self.api_base_url}{endpoint}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert outpost to dictionary representation."""
        return {
            'name': self.name,
            'type': self.outpost_type.value,
            'ip_address': self.ip_address,
            'port': self.port,
            'ssh_port': self.ssh_port,
            'status': self.status.value,
            'api_base_url': self.api_base_url,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'metadata': self.metadata
        }


@dataclass
class OutpostInventoryItem:
    """
    Represents an inventory item stored at an outpost.

    This is a sample data model for thematic items that might be tracked
    in the outpost's database.
    """

    item_id: int
    name: str
    category: str
    quantity: int
    description: str = ""
    value: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory item to dictionary."""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'description': self.description,
            'value': self.value
        }
