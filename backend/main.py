"""
Hudson Bay Interactive Expedition Console - Backend API

This is the main FastAPI application entrypoint for the Hudson Bay expedition
console. It provides RESTful API endpoints for managing expedition data,
outposts, logs, and live Raspberry Pi data.

The application follows modern async patterns with FastAPI and PostgreSQL,
supporting multi-node distributed system visualization.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from database import get_session
from models import Outpost
from schemas import OutpostResponse, HealthResponse, MessageResponse

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

# TODO: Add global exception handlers for better error handling
# TODO: Add request logging middleware
# TODO: Add rate limiting for production deployment


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
