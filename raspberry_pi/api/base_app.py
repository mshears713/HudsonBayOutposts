"""
Base FastAPI application skeleton for Raspberry Pi outposts.

This module provides a foundational FastAPI server template that can be
deployed to each Raspberry Pi. It includes basic endpoints, health checks,
and documentation setup.

Educational Note:
FastAPI is a modern Python web framework that automatically generates
interactive API documentation (OpenAPI/Swagger). It uses Python type hints
for request/response validation and serialization.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import platform
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for request/response validation
class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current server time")
    hostname: str = Field(..., description="Server hostname")
    uptime_seconds: float = Field(..., description="System uptime in seconds")


class OutpostMetadata(BaseModel):
    """Metadata about the outpost."""
    name: str = Field(..., description="Outpost name")
    type: str = Field(..., description="Outpost type (fishing, hunting, etc.)")
    version: str = Field(default="1.0.0", description="API version")
    description: str = Field(..., description="Outpost description")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(..., description="Error timestamp")


# Create FastAPI application
app = FastAPI(
    title="Raspberry Pi Frontier - Outpost API",
    description="RESTful API for Hudson Bay Company frontier outpost",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc alternative documentation
)


# Startup/shutdown event handlers
@app.on_event("startup")
async def startup_event():
    """
    Actions to perform when the API server starts.

    Educational Note:
    Startup events are perfect for initializing database connections,
    loading configuration, or setting up background tasks.
    """
    logger.info("Starting Raspberry Pi Outpost API...")
    logger.info(f"Platform: {platform.system()} {platform.release()}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform when the API server shuts down.

    Educational Note:
    Use shutdown events to clean up resources, close database connections,
    or save state before the server terminates.
    """
    logger.info("Shutting down Raspberry Pi Outpost API...")


# Root endpoint
@app.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint providing basic API information.

    Returns:
        Dictionary with welcome message and documentation links

    Educational Note:
    The root endpoint is often used to provide API metadata and
    links to documentation. It's what users see when they visit
    the base URL.
    """
    return {
        "message": "Welcome to the Raspberry Pi Frontier Outpost API",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring service status.

    Returns:
        HealthResponse with system information

    Educational Note:
    Health checks are essential for monitoring distributed systems.
    They allow you to quickly verify that a service is running and
    responsive. Many orchestration tools use health endpoints to
    manage service availability.
    """
    try:
        boot_time = psutil.boot_time()
        uptime = datetime.now().timestamp() - boot_time

        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            hostname=platform.node(),
            uptime_seconds=uptime
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/metadata", response_model=OutpostMetadata)
async def get_metadata():
    """
    Get metadata about this outpost.

    Returns:
        OutpostMetadata with information about the outpost

    Educational Note:
    This is a placeholder that should be customized for each outpost.
    In a real deployment, this would load configuration from a file
    or environment variables.
    """
    return OutpostMetadata(
        name="Base Outpost",
        type="template",
        version="1.0.0",
        description="Template API for Raspberry Pi Frontier outposts"
    )


@app.get("/system/info")
async def system_info():
    """
    Get system information about the Raspberry Pi.

    Returns:
        Dictionary with system metrics

    Educational Note:
    This endpoint demonstrates how to gather system information
    programmatically. It's useful for monitoring and diagnostics.
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count(),
            },
            "memory": {
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024),
                "percent_used": memory.percent,
            },
            "disk": {
                "total_gb": disk.total / (1024 * 1024 * 1024),
                "used_gb": disk.used / (1024 * 1024 * 1024),
                "free_gb": disk.free / (1024 * 1024 * 1024),
                "percent_used": disk.percent,
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Global HTTP exception handler.

    Educational Note:
    Centralized error handling ensures consistent error responses
    across your API. This makes it easier for clients to handle errors.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Global exception handler for uncaught exceptions.

    Educational Note:
    Always catch unexpected errors to prevent exposing sensitive
    information in stack traces. Log the full error internally
    but return a safe message to clients.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# Main entry point for development
if __name__ == "__main__":
    import uvicorn

    # Educational Note:
    # Uvicorn is an ASGI server for running FastAPI applications.
    # In production, you'd typically run this via command line:
    # uvicorn base_app:app --host 0.0.0.0 --port 8000

    uvicorn.run(
        "base_app:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
