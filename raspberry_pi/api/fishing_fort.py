"""
Fishing Fort API - FastAPI application for the fishing outpost.

This API provides RESTful endpoints for managing fishing fort inventory,
catch records, equipment, and weather logs.

Educational Note:
This demonstrates a complete themed API with CRUD operations (Create, Read,
Update, Delete). Each endpoint follows REST conventions for HTTP methods
and status codes.

To run this API:
    uvicorn raspberry_pi.api.fishing_fort:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI, HTTPException, Query, Path, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import sqlite3
from pathlib import Path as FilePath
import logging
import os
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = FilePath(__file__).parent.parent / "db" / "data" / "fishing_fort.db"


# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================

class InventoryItem(BaseModel):
    """
    Represents an inventory item at the fishing fort.

    Educational Note:
    Pydantic models provide automatic validation and serialization.
    The Field() function adds documentation and validation rules.
    """
    item_id: Optional[int] = Field(None, description="Unique item ID (auto-generated)")
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    category: str = Field(..., description="Category (food, tools, supplies)")
    quantity: int = Field(..., ge=0, description="Quantity in stock")
    unit: str = Field(..., description="Unit of measurement")
    value: float = Field(..., ge=0.0, description="Item value in frontier currency")
    description: Optional[str] = Field(None, description="Item description")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Fishing Line",
                "category": "supplies",
                "quantity": 500,
                "unit": "feet",
                "value": 25.0,
                "description": "Braided hemp line"
            }
        }


class InventoryItemCreate(BaseModel):
    """Model for creating new inventory items (excludes auto-generated fields)."""
    name: str = Field(..., min_length=1, max_length=100)
    category: str
    quantity: int = Field(..., ge=0)
    unit: str
    value: float = Field(..., ge=0.0)
    description: Optional[str] = None


class InventoryItemUpdate(BaseModel):
    """Model for updating inventory items (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = None
    value: Optional[float] = Field(None, ge=0.0)
    description: Optional[str] = None


class CatchRecord(BaseModel):
    """Represents a fishing catch record."""
    catch_id: Optional[int] = None
    fish_type: str
    quantity: int = Field(..., ge=1)
    weight_pounds: float = Field(..., gt=0.0)
    catch_date: str  # ISO format date
    location: Optional[str] = None
    fisher_name: Optional[str] = None
    quality: Optional[str] = Field(None, pattern="^(poor|fair|good|excellent)$")
    notes: Optional[str] = None
    created_at: Optional[str] = None


class StatusResponse(BaseModel):
    """Response model for outpost status."""
    outpost_name: str
    outpost_type: str
    status: str
    total_inventory_items: int
    total_inventory_value: float
    recent_catches_count: int
    last_updated: str


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Fishing Fort API",
    description="Hudson Bay Company Fishing Outpost RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================================
# Database Helper Functions
# ============================================================================

def get_db_connection() -> sqlite3.Connection:
    """
    Create and return a database connection.

    Returns:
        SQLite connection object

    Educational Note:
    We create a new connection for each request to avoid threading issues.
    In production, you might use connection pooling for better performance.
    """
    if not DB_PATH.exists():
        logger.error(f"Database not found at {DB_PATH}")
        raise HTTPException(
            status_code=500,
            detail="Database not initialized. Run init_fishing_fort.py first."
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert SQLite Row object to dictionary."""
    return {key: row[key] for key in row.keys()}


# ============================================================================
# Root and Metadata Endpoints
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Fishing Fort API",
        "outpost": "Hudson Bay Company - Fishing Fort",
        "documentation": "/docs",
        "endpoints": {
            "inventory": "/inventory",
            "catches": "/catches",
            "status": "/status"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Educational Note:
    Health checks should verify critical dependencies like database connectivity.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventory")
        count = cursor.fetchone()[0]
        conn.close()

        return {
            "status": "healthy",
            "database": "connected",
            "inventory_items": count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/status", response_model=StatusResponse)
async def get_outpost_status():
    """
    Get overall status and statistics for the fishing fort.

    Returns:
        StatusResponse with outpost metrics

    Educational Note:
    Status endpoints provide high-level overview data useful for dashboards
    and monitoring systems.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get inventory stats
        cursor.execute("SELECT COUNT(*), SUM(value) FROM inventory")
        inv_count, inv_value = cursor.fetchone()

        # Get recent catches (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM catch_records
            WHERE catch_date >= date('now', '-7 days')
        """)
        recent_catches = cursor.fetchone()[0]

        conn.close()

        return StatusResponse(
            outpost_name="Fishing Fort",
            outpost_type="fishing",
            status="operational",
            total_inventory_items=inv_count or 0,
            total_inventory_value=inv_value or 0.0,
            recent_catches_count=recent_catches or 0,
            last_updated=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


# ============================================================================
# Inventory Endpoints
# ============================================================================

@app.get("/inventory", response_model=List[InventoryItem])
async def get_inventory(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_quantity: Optional[int] = Query(None, ge=0, description="Minimum quantity"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return")
):
    """
    Get inventory items with optional filtering.

    Args:
        category: Filter by category (food, tools, supplies)
        min_quantity: Only return items with quantity >= this value
        limit: Maximum number of items to return

    Returns:
        List of inventory items

    Educational Note:
    Query parameters allow clients to filter results. This is more efficient
    than returning all data and filtering client-side.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query with filters
        query = "SELECT * FROM inventory WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if min_quantity is not None:
            query += " AND quantity >= ?"
            params.append(min_quantity)

        query += " ORDER BY category, name LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        # Convert to InventoryItem models
        items = [InventoryItem(**dict_from_row(row)) for row in rows]

        logger.info(f"Retrieved {len(items)} inventory items")
        return items

    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory: {str(e)}")


@app.get("/inventory/{item_id}", response_model=InventoryItem)
async def get_inventory_item(
    item_id: int = Path(..., gt=0, description="Inventory item ID")
):
    """
    Get a specific inventory item by ID.

    Args:
        item_id: The unique inventory item ID

    Returns:
        Single inventory item

    Educational Note:
    Path parameters are part of the URL and used for identifying specific resources.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM inventory WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

        return InventoryItem(**dict_from_row(row))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch item: {str(e)}")


@app.post("/inventory", response_model=InventoryItem, status_code=201)
async def create_inventory_item(item: InventoryItemCreate):
    """
    Create a new inventory item.

    Args:
        item: Inventory item data

    Returns:
        Created inventory item with generated ID

    Educational Note:
    POST requests create new resources. We return 201 (Created) status
    and include the new resource in the response.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO inventory (name, category, quantity, unit, value, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item.name, item.category, item.quantity, item.unit, item.value, item.description))

        item_id = cursor.lastrowid
        conn.commit()

        # Fetch the created item
        cursor.execute("SELECT * FROM inventory WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()

        logger.info(f"Created inventory item {item_id}: {item.name}")
        return InventoryItem(**dict_from_row(row))

    except sqlite3.IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(status_code=400, detail="Invalid inventory data")
    except Exception as e:
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create item: {str(e)}")


@app.put("/inventory/{item_id}", response_model=InventoryItem)
async def update_inventory_item(
    item_id: int,
    item: InventoryItemUpdate
):
    """
    Update an existing inventory item.

    Args:
        item_id: Item ID to update
        item: Updated item data (only provided fields will be updated)

    Returns:
        Updated inventory item

    Educational Note:
    PUT requests update existing resources. We use partial updates,
    only changing fields that are provided.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if item exists
        cursor.execute("SELECT * FROM inventory WHERE item_id = ?", (item_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

        # Build update query for provided fields
        updates = []
        params = []

        for field, value in item.dict(exclude_unset=True).items():
            updates.append(f"{field} = ?")
            params.append(value)

        if updates:
            params.append(item_id)
            query = f"UPDATE inventory SET {', '.join(updates)}, last_updated = CURRENT_TIMESTAMP WHERE item_id = ?"
            cursor.execute(query, params)
            conn.commit()

        # Fetch updated item
        cursor.execute("SELECT * FROM inventory WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()

        logger.info(f"Updated inventory item {item_id}")
        return InventoryItem(**dict_from_row(row))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update item: {str(e)}")


@app.delete("/inventory/{item_id}", status_code=204)
async def delete_inventory_item(item_id: int):
    """
    Delete an inventory item.

    Args:
        item_id: Item ID to delete

    Educational Note:
    DELETE requests remove resources. We return 204 (No Content) on success
    with no response body.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM inventory WHERE item_id = ?", (item_id,))
        deleted_rows = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted_rows == 0:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

        logger.info(f"Deleted inventory item {item_id}")
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete item: {str(e)}")


# ============================================================================
# Catch Records Endpoints
# ============================================================================

@app.get("/catches", response_model=List[CatchRecord])
async def get_catch_records(
    fish_type: Optional[str] = Query(None, description="Filter by fish type"),
    limit: int = Query(50, ge=1, le=500, description="Maximum results")
):
    """
    Get catch records with optional filtering.

    Args:
        fish_type: Filter by fish type (salmon, trout, pike, etc.)
        limit: Maximum number of records to return

    Returns:
        List of catch records
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM catch_records WHERE 1=1"
        params = []

        if fish_type:
            query += " AND fish_type = ?"
            params.append(fish_type)

        query += " ORDER BY catch_date DESC, catch_id DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        records = [CatchRecord(**dict_from_row(row)) for row in rows]
        logger.info(f"Retrieved {len(records)} catch records")
        return records

    except Exception as e:
        logger.error(f"Error fetching catch records: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch catches: {str(e)}")


@app.get("/catches/summary")
async def get_catch_summary():
    """
    Get summary statistics for catch records.

    Returns:
        Dictionary with catch statistics by fish type

    Educational Note:
    Summary endpoints aggregate data on the server side, reducing
    data transfer and computation on the client.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                fish_type,
                COUNT(*) as catch_count,
                SUM(quantity) as total_quantity,
                SUM(weight_pounds) as total_weight,
                AVG(weight_pounds) as avg_weight
            FROM catch_records
            GROUP BY fish_type
            ORDER BY total_weight DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        summary = [dict_from_row(row) for row in rows]
        return {
            "summary": summary,
            "total_types": len(summary),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating catch summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


# ============================================================================
# File Operations and Logs Endpoints
# ============================================================================

# Create uploads directory
UPLOAD_DIR = FilePath(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

LOGS_DIR = FilePath("/var/log")  # Standard Linux logs directory


@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the outpost.

    Args:
        file: The file to upload

    Returns:
        Dictionary with upload details

    Educational Note:
    File uploads in FastAPI use multipart/form-data encoding.
    Always validate file types and sizes in production!
    """
    try:
        # Validate file size (max 10MB for educational purposes)
        contents = await file.read()
        file_size = len(contents)

        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")

        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"File uploaded: {file.filename} ({file_size} bytes)")

        return {
            "filename": file.filename,
            "size_bytes": file_size,
            "path": str(file_path),
            "uploaded_at": datetime.now().isoformat(),
            "message": "File uploaded successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/files/list")
async def list_uploaded_files():
    """
    List all uploaded files.

    Returns:
        List of uploaded files with metadata

    Educational Note:
    This demonstrates directory listing and file metadata retrieval.
    """
    try:
        files = []

        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        return {
            "files": files,
            "total_count": len(files),
            "upload_directory": str(UPLOAD_DIR)
        }

    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@app.get("/files/download/{filename}")
async def download_file(filename: str):
    """
    Download a previously uploaded file.

    Args:
        filename: Name of file to download

    Returns:
        File content

    Educational Note:
    FileResponse streams files efficiently without loading entire file
    into memory. Important for large files!
    """
    try:
        file_path = UPLOAD_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Not a file")

        logger.info(f"File downloaded: {filename}")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """
    Delete an uploaded file.

    Args:
        filename: Name of file to delete

    Educational Note:
    Be careful with file deletion in production - consider soft deletes
    or moving to trash instead of permanent deletion.
    """
    try:
        file_path = UPLOAD_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        file_path.unlink()
        logger.info(f"File deleted: {filename}")

        return {
            "message": f"File {filename} deleted successfully",
            "deleted_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.get("/logs/list")
async def list_log_files():
    """
    List available log files.

    Returns:
        List of log files

    Educational Note:
    System logs contain valuable diagnostic information. Common logs:
    - syslog: System messages
    - auth.log: Authentication attempts
    - kern.log: Kernel messages
    """
    try:
        # Common log files to check
        common_logs = [
            "syslog",
            "auth.log",
            "kern.log",
            "dmesg",
            "daemon.log"
        ]

        available_logs = []

        # Check system logs
        for log_name in common_logs:
            log_path = LOGS_DIR / log_name
            if log_path.exists():
                stat = log_path.stat()
                available_logs.append({
                    "filename": log_name,
                    "path": str(log_path),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        # Add application logs if they exist
        app_log_dir = FilePath(__file__).parent.parent / "logs"
        if app_log_dir.exists():
            for log_path in app_log_dir.glob("*.log"):
                stat = log_path.stat()
                available_logs.append({
                    "filename": log_path.name,
                    "path": str(log_path),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "type": "application"
                })

        return {
            "logs": available_logs,
            "total_count": len(available_logs)
        }

    except Exception as e:
        logger.error(f"Error listing logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list logs: {str(e)}")


@app.get("/logs/{log_name}")
async def get_log_content(
    log_name: str,
    lines: int = Query(100, ge=1, le=10000, description="Number of lines to return"),
    offset: int = Query(0, ge=0, description="Line offset to start from")
):
    """
    Retrieve log file content.

    Args:
        log_name: Name of log file
        lines: Number of lines to return (default 100)
        offset: Line offset to start from (default 0)

    Returns:
        Log content and metadata

    Educational Note:
    For large log files, we paginate results to avoid memory issues.
    In production, consider using log aggregation tools like ELK stack.
    """
    try:
        # Try system logs first
        log_path = LOGS_DIR / log_name

        # If not found, try application logs
        if not log_path.exists():
            app_log_path = FilePath(__file__).parent.parent / "logs" / log_name
            if app_log_path.exists():
                log_path = app_log_path

        if not log_path.exists():
            raise HTTPException(status_code=404, detail=f"Log file '{log_name}' not found")

        # Read log file with pagination
        with open(log_path, 'r', errors='ignore') as f:
            all_lines = f.readlines()

        total_lines = len(all_lines)
        start_idx = offset
        end_idx = min(start_idx + lines, total_lines)

        selected_lines = all_lines[start_idx:end_idx]

        return {
            "log_name": log_name,
            "total_lines": total_lines,
            "returned_lines": len(selected_lines),
            "offset": offset,
            "content": "".join(selected_lines),
            "lines": [line.rstrip('\n') for line in selected_lines],
            "has_more": end_idx < total_lines
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading log {log_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read log: {str(e)}")


@app.get("/system/disk-usage")
async def get_disk_usage():
    """
    Get disk usage information.

    Returns:
        Disk usage statistics

    Educational Note:
    Monitoring disk usage is essential for system health.
    Running out of disk space can cause system failures.
    """
    try:
        import shutil

        # Get disk usage for root filesystem
        total, used, free = shutil.disk_usage("/")

        return {
            "total_gb": total / (1024**3),
            "used_gb": used / (1024**3),
            "free_gb": free / (1024**3),
            "percent_used": (used / total) * 100,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get disk usage: {str(e)}")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("🎣 Starting Fishing Fort API...")
    print(f"📂 Database: {DB_PATH}")
    print("📡 Server will start at http://0.0.0.0:8000")
    print("📚 Documentation: http://0.0.0.0:8000/docs")

    uvicorn.run(
        "fishing_fort:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
