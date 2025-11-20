"""
Hudson Bay Interactive Expedition Console - Backend API

This is the main FastAPI application entrypoint for the Hudson Bay expedition
console. It provides RESTful API endpoints for managing expedition data,
outposts, logs, and live Raspberry Pi data.

The application follows modern async patterns with FastAPI and PostgreSQL,
supporting multi-node distributed system visualization.
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
import os

from database import get_session, init_db
from models import Outpost, ExpeditionLog
from schemas import (
    OutpostResponse,
    ExpeditionLogCreate,
    ExpeditionLogResponse,
    HealthResponse,
    MessageResponse
)

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Hudson Bay Expedition API",
    description="Backend API for the Interactive Expedition Console",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc",  # ReDoc documentation
)

# Configure CORS for frontend access
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()


@app.get("/", response_model=MessageResponse)
async def root():
    """
    Root endpoint returning a welcome message.

    This endpoint serves as a health check and welcome message for the API.

    Returns:
        dict: Welcome message with API information
    """
    return {
        "message": "Welcome to Hudson Bay Expedition API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status of the API
    """
    return {"status": "healthy", "service": "Hudson Bay API"}


@app.get("/outposts", response_model=list[OutpostResponse])
async def get_outposts(session: AsyncSession = Depends(get_session)):
    """
    Get all outposts from the database.

    Returns:
        list[OutpostResponse]: List of all outposts
    """
    result = await session.execute(select(Outpost))
    outposts = result.scalars().all()
    return outposts


@app.get("/outposts/{outpost_id}", response_model=OutpostResponse)
async def get_outpost(outpost_id: str, session: AsyncSession = Depends(get_session)):
    """
    Get a specific outpost by ID.

    Args:
        outpost_id: UUID of the outpost

    Returns:
        OutpostResponse: Outpost details

    Raises:
        HTTPException: 404 if outpost not found
    """
    result = await session.execute(
        select(Outpost).where(Outpost.id == outpost_id)
    )
    outpost = result.scalar_one_or_none()

    if not outpost:
        raise HTTPException(status_code=404, detail="Outpost not found")

    return outpost


@app.post("/expedition/logs", response_model=ExpeditionLogResponse, status_code=201)
async def create_expedition_log(
    log: ExpeditionLogCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new expedition log entry.

    Args:
        log: Log data to create

    Returns:
        ExpeditionLogResponse: Created log entry

    Raises:
        HTTPException: 404 if outpost not found
    """
    # Verify outpost exists
    result = await session.execute(
        select(Outpost).where(Outpost.id == log.outpost_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Outpost not found")

    # Create log entry
    db_log = ExpeditionLog(
        outpost_id=log.outpost_id,
        event_type=log.event_type,
        details=log.details,
        timestamp=log.timestamp or datetime.utcnow()
    )

    session.add(db_log)
    await session.commit()
    await session.refresh(db_log)

    return db_log


@app.get("/expedition/logs", response_model=list[ExpeditionLogResponse])
async def get_expedition_logs(
    outpost_id: Optional[str] = Query(None, description="Filter by outpost ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get expedition logs with optional filtering and pagination.

    Args:
        outpost_id: Filter logs by outpost ID (optional)
        event_type: Filter logs by event type (optional)
        limit: Maximum number of logs to return (default: 50)
        offset: Number of logs to skip (default: 0)

    Returns:
        list[ExpeditionLogResponse]: List of expedition logs
    """
    query = select(ExpeditionLog).order_by(ExpeditionLog.timestamp.desc())

    # Apply filters
    if outpost_id:
        query = query.where(ExpeditionLog.outpost_id == outpost_id)
    if event_type:
        query = query.where(ExpeditionLog.event_type == event_type)

    # Apply pagination
    query = query.limit(limit).offset(offset)

    result = await session.execute(query)
    logs = result.scalars().all()

    return logs


if __name__ == "__main__":
    import uvicorn
    # Run the application with uvicorn for development
    # In production, use: uvicorn main:app --host 0.0.0.0 --port 8000
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
