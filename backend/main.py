"""
Hudson Bay Interactive Expedition Console - Backend API

This is the main FastAPI application entrypoint for the Hudson Bay expedition
console. It provides RESTful API endpoints for managing expedition data,
outposts, logs, and live Raspberry Pi data.

The application follows modern async patterns with FastAPI and PostgreSQL,
supporting multi-node distributed system visualization.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Hudson Bay Expedition API",
    description="Backend API for the Interactive Expedition Console",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc",  # ReDoc documentation
)

# TODO: Add global exception handlers for better error handling
# TODO: Add request logging middleware
# TODO: Add rate limiting for production deployment


@app.get("/")
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


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status of the API
    """
    return {"status": "healthy", "service": "Hudson Bay API"}


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
