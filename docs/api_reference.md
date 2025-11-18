# Raspberry Pi Frontier - API Reference

## Overview

This document provides comprehensive API documentation for all outpost endpoints implemented in Phase 2.

## Base URL

Each outpost runs its own API server. The base URL format is:

```
http://<outpost-ip>:<port>
```

Default port: `8000`

## Authentication

**Phase 2 Note**: Authentication is not yet implemented. All endpoints are publicly accessible.
Authentication will be added in Phase 3.

---

## Core Endpoints

### Health Check

**GET** `/health`

Check if the API is running and responsive.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "inventory_items": 10,
  "timestamp": "2024-11-18T12:00:00"
}
```

### Outpost Status

**GET** `/status`

Get overall outpost status and statistics.

**Response:**
```json
{
  "outpost_name": "Fishing Fort",
  "outpost_type": "fishing",
  "status": "operational",
  "total_inventory_items": 10,
  "total_inventory_value": 650.0,
  "recent_catches_count": 5,
  "last_updated": "2024-11-18T12:00:00"
}
```

---

## Inventory Management

### List Inventory

**GET** `/inventory`

Retrieve all inventory items with optional filtering.

**Query Parameters:**
- `category` (optional): Filter by category (food, tools, supplies)
- `min_quantity` (optional): Minimum quantity threshold
- `limit` (optional): Maximum results (default: 100)

**Response:**
```json
[
  {
    "item_id": 1,
    "name": "Fishing Line",
    "category": "supplies",
    "quantity": 500,
    "unit": "feet",
    "value": 25.0,
    "description": "Braided hemp line",
    "last_updated": "2024-11-18T12:00:00"
  }
]
```

### Get Inventory Item

**GET** `/inventory/{item_id}`

Retrieve a specific inventory item.

**Response:** Single inventory item object

### Create Inventory Item

**POST** `/inventory`

Create a new inventory item.

**Request Body:**
```json
{
  "name": "New Item",
  "category": "supplies",
  "quantity": 10,
  "unit": "pieces",
  "value": 50.0,
  "description": "Optional description"
}
```

**Response:** Created inventory item with `item_id`

**Status Code:** `201 Created`

### Update Inventory Item

**PUT** `/inventory/{item_id}`

Update an existing inventory item (partial update supported).

**Request Body:** Same as create, but all fields optional

**Response:** Updated inventory item

### Delete Inventory Item

**DELETE** `/inventory/{item_id}`

Delete an inventory item.

**Response:** No content

**Status Code:** `204 No Content`

---

## Catch Records (Fishing Fort Only)

### List Catch Records

**GET** `/catches`

Retrieve fishing catch records.

**Query Parameters:**
- `fish_type` (optional): Filter by fish type
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
[
  {
    "catch_id": 1,
    "fish_type": "salmon",
    "quantity": 45,
    "weight_pounds": 180.5,
    "catch_date": "2024-11-15",
    "location": "North River Bend",
    "fisher_name": "Jacques Dubois",
    "quality": "excellent",
    "notes": "Large run, very fresh"
  }
]
```

### Catch Summary

**GET** `/catches/summary`

Get aggregated catch statistics by fish type.

**Response:**
```json
{
  "summary": [
    {
      "fish_type": "salmon",
      "catch_count": 3,
      "total_quantity": 201,
      "total_weight": 804.5,
      "avg_weight": 268.17
    }
  ],
  "total_types": 5,
  "timestamp": "2024-11-18T12:00:00"
}
```

---

## File Operations

### Upload File

**POST** `/files/upload`

Upload a file to the outpost.

**Request:** `multipart/form-data` with file field

**Response:**
```json
{
  "filename": "data.csv",
  "size_bytes": 1024,
  "path": "/path/to/uploads/data.csv",
  "uploaded_at": "2024-11-18T12:00:00",
  "message": "File uploaded successfully"
}
```

**Status Code:** `200 OK`

**Limitations:** Max file size: 10MB

### List Files

**GET** `/files/list`

List all uploaded files.

**Response:**
```json
{
  "files": [
    {
      "filename": "data.csv",
      "size_bytes": 1024,
      "modified": "2024-11-18T12:00:00"
    }
  ],
  "total_count": 1,
  "upload_directory": "/path/to/uploads"
}
```

### Download File

**GET** `/files/download/{filename}`

Download a previously uploaded file.

**Response:** File content (binary)

**Content-Type:** `application/octet-stream`

### Delete File

**DELETE** `/files/{filename}`

Delete an uploaded file.

**Response:**
```json
{
  "message": "File data.csv deleted successfully",
  "deleted_at": "2024-11-18T12:00:00"
}
```

---

## Log Management

### List Logs

**GET** `/logs/list`

List available system and application logs.

**Response:**
```json
{
  "logs": [
    {
      "filename": "syslog",
      "path": "/var/log/syslog",
      "size_bytes": 1048576,
      "modified": "2024-11-18T12:00:00"
    }
  ],
  "total_count": 5
}
```

### Get Log Content

**GET** `/logs/{log_name}`

Retrieve log file content with pagination.

**Query Parameters:**
- `lines` (optional): Number of lines to return (default: 100, max: 10000)
- `offset` (optional): Line offset to start from (default: 0)

**Response:**
```json
{
  "log_name": "syslog",
  "total_lines": 10000,
  "returned_lines": 100,
  "offset": 0,
  "content": "...",
  "lines": ["line 1", "line 2", "..."],
  "has_more": true
}
```

---

## System Information

### Disk Usage

**GET** `/system/disk-usage`

Get disk usage statistics.

**Response:**
```json
{
  "total_gb": 32.0,
  "used_gb": 8.5,
  "free_gb": 23.5,
  "percent_used": 26.56,
  "timestamp": "2024-11-18T12:00:00"
}
```

### System Info

**GET** `/system/info`

Get detailed system information (from base_app.py).

**Response:**
```json
{
  "platform": {
    "system": "Linux",
    "release": "5.10.0",
    "machine": "armv7l",
    "processor": "..."
  },
  "cpu": {
    "percent": 15.2,
    "count": 4
  },
  "memory": {
    "total_mb": 1024,
    "available_mb": 512,
    "percent_used": 50.0
  },
  "disk": {
    "total_gb": 32.0,
    "used_gb": 8.5,
    "free_gb": 23.5,
    "percent_used": 26.56
  },
  "timestamp": "2024-11-18T12:00:00"
}
```

---

## Error Responses

All endpoints return consistent error formats:

```json
{
  "error": "Error message",
  "detail": "Detailed explanation",
  "timestamp": "2024-11-18T12:00:00"
}
```

### Common HTTP Status Codes

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST (resource created)
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File too large
- `500 Internal Server Error`: Server-side error

---

## Multi-Outpost Workflows

### Example: Aggregate Inventory

Fetch inventory from multiple outposts:

```python
from src.api_client.client import OutpostAPIClient
from src.api_client.endpoints import get_all_inventory_across_outposts

clients = [
    OutpostAPIClient("http://192.168.1.100:8000"),
    OutpostAPIClient("http://192.168.1.101:8000")
]

all_inventory = get_all_inventory_across_outposts(clients)
```

### Example: Status Dashboard

```python
from src.api_client.endpoints import get_combined_status

statuses = get_combined_status(clients)
for status in statuses:
    print(f"{status['outpost_name']}: {status['status']}")
```

---

## Interactive Documentation

Each outpost provides auto-generated interactive API documentation:

- **Swagger UI**: `http://<outpost-ip>:8000/docs`
- **ReDoc**: `http://<outpost-ip>:8000/redoc`

These interfaces allow you to test endpoints directly from your browser.

---

## Next Steps

Phase 3 will add:
- Token-based authentication
- Additional outpost types (Hunting Fort, Trading Fort)
- Data synchronization endpoints
- Enhanced error handling and retries

---

*Last Updated: November 18, 2024 - Phase 2*
