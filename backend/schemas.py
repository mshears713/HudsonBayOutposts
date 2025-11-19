"""
Pydantic Schemas for API Request/Response Validation

Defines data validation and serialization schemas for the Hudson Bay API.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class OutpostBase(BaseModel):
    """Base schema for Outpost data"""
    name: str = Field(..., min_length=1, max_length=255, description="Outpost name")
    location_lat: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    location_lon: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    description: Optional[str] = Field(None, description="Outpost description")
    api_endpoint: Optional[str] = Field(None, max_length=512, description="API endpoint URL")


class OutpostCreate(OutpostBase):
    """Schema for creating a new outpost"""
    pass


class OutpostResponse(OutpostBase):
    """Schema for outpost API responses"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpeditionLogBase(BaseModel):
    """Base schema for ExpeditionLog data"""
    outpost_id: UUID = Field(..., description="ID of the outpost")
    event_type: str = Field(..., min_length=1, max_length=100, description="Event type")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event details")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")


class ExpeditionLogCreate(ExpeditionLogBase):
    """Schema for creating a new expedition log"""
    pass


class ExpeditionLogResponse(ExpeditionLogBase):
    """Schema for expedition log API responses"""
    id: UUID
    created_at: datetime
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    service: str


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    version: Optional[str] = None
    docs: Optional[str] = None
    status: Optional[str] = None
