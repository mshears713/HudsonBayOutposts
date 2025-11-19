"""
Database Models for Hudson Bay Expedition Console

This module defines SQLAlchemy ORM models for the expedition system,
including outposts and expedition logs. All models use UUIDs for primary
keys to enable distributed system compatibility and prevent ID collisions.

Models are designed with comprehensive validation, relationships, and
documentation to support the full-stack expedition console application.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    CheckConstraint,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from database import Base


class Outpost(Base):
    """
    Represents a Raspberry Pi outpost in the Hudson Bay expedition network.

    Each outpost is a physical Raspberry Pi device located at specific
    coordinates, providing sensor data and API endpoints. Outposts serve
    as the distributed nodes in the expedition system.

    Attributes:
        id (UUID): Unique identifier for the outpost
        name (str): Human-readable name of the outpost (e.g., "Fort Churchill")
        location_lat (float): Latitude coordinate (-90 to 90)
        location_lon (float): Longitude coordinate (-180 to 180)
        description (str): Detailed description of the outpost's purpose and features
        api_endpoint (str): URL/IP address for the outpost's API
        created_at (datetime): Timestamp when the outpost was registered
        updated_at (datetime): Timestamp of last update

    Relationships:
        expedition_logs: All logs associated with this outpost

    Constraints:
        - Name must be unique and non-empty
        - Latitude must be between -90 and 90
        - Longitude must be between -180 and 180
        - API endpoint must be a valid URL format
    """

    __tablename__ = "outposts"

    # Primary key using UUID for distributed system compatibility
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for the outpost"
    )

    # Outpost identification and location
    name = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique name of the outpost"
    )

    location_lat = Column(
        Float,
        nullable=False,
        doc="Latitude coordinate of the outpost"
    )

    location_lon = Column(
        Float,
        nullable=False,
        doc="Longitude coordinate of the outpost"
    )

    description = Column(
        Text,
        nullable=True,
        doc="Detailed description of the outpost"
    )

    api_endpoint = Column(
        String(512),
        nullable=True,
        doc="API endpoint URL for this outpost (e.g., http://192.168.1.100:8000)"
    )

    # Timestamps for tracking changes
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        doc="Timestamp when outpost was created"
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Timestamp when outpost was last updated"
    )

    # Relationship to expedition logs
    expedition_logs = relationship(
        "ExpeditionLog",
        back_populates="outpost",
        cascade="all, delete-orphan",
        doc="All expedition logs for this outpost"
    )

    # Table-level constraints
    __table_args__ = (
        CheckConstraint(
            "location_lat >= -90 AND location_lat <= 90",
            name="check_latitude_range"
        ),
        CheckConstraint(
            "location_lon >= -180 AND location_lon <= 180",
            name="check_longitude_range"
        ),
        Index("idx_outpost_location", "location_lat", "location_lon"),
        {"comment": "Raspberry Pi outposts in the expedition network"}
    )

    @validates("name")
    def validate_name(self, key, name):
        """
        Validate that outpost name is not empty.

        Args:
            key: Field name being validated
            name: Name value to validate

        Returns:
            str: Validated name

        Raises:
            ValueError: If name is empty or only whitespace
        """
        if not name or not name.strip():
            raise ValueError("Outpost name cannot be empty")
        return name.strip()

    @validates("location_lat")
    def validate_latitude(self, key, lat):
        """
        Validate latitude is within valid range.

        Args:
            key: Field name being validated
            lat: Latitude value to validate

        Returns:
            float: Validated latitude

        Raises:
            ValueError: If latitude is outside -90 to 90 range
        """
        if lat is None:
            raise ValueError("Latitude is required")
        if lat < -90 or lat > 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
        return lat

    @validates("location_lon")
    def validate_longitude(self, key, lon):
        """
        Validate longitude is within valid range.

        Args:
            key: Field name being validated
            lon: Longitude value to validate

        Returns:
            float: Validated longitude

        Raises:
            ValueError: If longitude is outside -180 to 180 range
        """
        if lon is None:
            raise ValueError("Longitude is required")
        if lon < -180 or lon > 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
        return lon

    def __repr__(self):
        """String representation of the outpost."""
        return (
            f"<Outpost(id={self.id}, name='{self.name}', "
            f"location=({self.location_lat}, {self.location_lon}))>"
        )


class ExpeditionLog(Base):
    """
    Represents a log entry in the expedition journal.

    Expedition logs capture events, sensor readings, and activities from
    outposts. They form a timeline of the expedition's progress and provide
    data for analytics and visualization.

    Attributes:
        id (UUID): Unique identifier for the log entry
        timestamp (datetime): When the log entry was created
        outpost_id (UUID): Foreign key to the associated outpost
        event_type (str): Category of the log (e.g., "sensor_reading", "alert", "status")
        details (dict): JSON field containing event-specific data
        created_at (datetime): When this log was stored in the database

    Relationships:
        outpost: The outpost this log is associated with

    Common event_types:
        - "sensor_reading": Sensor data from the outpost
        - "status_update": Outpost operational status change
        - "alert": Warning or error condition
        - "manual_entry": User-created log entry
        - "system_event": Automated system activity

    Details JSON structure varies by event_type but typically includes:
        {
            "temperature": 23.5,
            "humidity": 65.2,
            "source": "DHT22",
            "notes": "Optional human-readable notes"
        }
    """

    __tablename__ = "expedition_logs"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for the log entry"
    )

    # Timestamp of the event (may differ from created_at)
    timestamp = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
        doc="Timestamp when the event occurred"
    )

    # Foreign key to outpost
    outpost_id = Column(
        UUID(as_uuid=True),
        ForeignKey("outposts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of the outpost that generated this log"
    )

    # Event classification
    event_type = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Type of event (e.g., 'sensor_reading', 'alert', 'status')"
    )

    # Flexible JSON field for event details
    details = Column(
        JSON,
        nullable=False,
        default=dict,
        doc="JSON object containing event-specific data"
    )

    # Database creation timestamp
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        doc="Timestamp when this log was created in the database"
    )

    # Relationship to outpost
    outpost = relationship(
        "Outpost",
        back_populates="expedition_logs",
        doc="The outpost associated with this log"
    )

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("idx_log_outpost_timestamp", "outpost_id", "timestamp"),
        Index("idx_log_event_type_timestamp", "event_type", "timestamp"),
        {"comment": "Expedition log entries from outposts"}
    )

    @validates("event_type")
    def validate_event_type(self, key, event_type):
        """
        Validate that event_type is not empty.

        Args:
            key: Field name being validated
            event_type: Event type value to validate

        Returns:
            str: Validated event type

        Raises:
            ValueError: If event_type is empty
        """
        if not event_type or not event_type.strip():
            raise ValueError("Event type cannot be empty")
        return event_type.strip()

    @validates("details")
    def validate_details(self, key, details):
        """
        Validate that details is a dictionary.

        Args:
            key: Field name being validated
            details: Details value to validate

        Returns:
            dict: Validated details

        Raises:
            ValueError: If details is not a dict
        """
        if details is None:
            return {}
        if not isinstance(details, dict):
            raise ValueError("Details must be a dictionary")
        return details

    def __repr__(self):
        """String representation of the expedition log."""
        return (
            f"<ExpeditionLog(id={self.id}, outpost_id={self.outpost_id}, "
            f"event_type='{self.event_type}', timestamp={self.timestamp})>"
        )
