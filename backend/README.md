# Hudson Bay Expedition Console - Backend

FastAPI-based backend providing REST APIs for the Hudson Bay Interactive Expedition Console.

## Overview

This backend service manages expedition data, outpost information, and live Raspberry Pi data aggregation. It uses:

- **FastAPI** for async REST APIs
- **PostgreSQL** for persistent storage
- **SQLAlchemy** (async) for ORM
- **Alembic** for database migrations
- **httpx** for async HTTP client to Raspberry Pi outposts

## Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- Virtual environment

### Installation

1. **Create and activate virtual environment:**

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql+asyncpg://hudsonbay:hudsonbay@localhost:5432/hudsonbay
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
SQL_ECHO=false
LOG_LEVEL=INFO
```

4. **Set up PostgreSQL database:**

```sql
CREATE USER hudsonbay WITH PASSWORD 'hudsonbay';
CREATE DATABASE hudsonbay OWNER hudsonbay;
GRANT ALL PRIVILEGES ON DATABASE hudsonbay TO hudsonbay;
```

5. **Run database migrations:**

```bash
# Generate initial migration (if needed)
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

6. **Start the development server:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Database Migrations

### Alembic Commands

- **Create a new migration:**
  ```bash
  alembic revision --autogenerate -m "Description of changes"
  ```

- **Apply migrations:**
  ```bash
  alembic upgrade head
  ```

- **Rollback last migration:**
  ```bash
  alembic downgrade -1
  ```

- **View migration history:**
  ```bash
  alembic history
  ```

- **Check current version:**
  ```bash
  alembic current
  ```

### Migration Workflow

1. Modify models in `models.py`
2. Generate migration: `alembic revision --autogenerate -m "Description"`
3. Review generated migration in `alembic/versions/`
4. Apply migration: `alembic upgrade head`

**Note:** Always review auto-generated migrations before applying them!

## API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py              # FastAPI application entrypoint
├── database.py          # Async database engine and session management
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic schemas for request/response (to be added)
├── api_client.py        # HTTP client for Raspberry Pi outposts (to be added)
├── scheduler.py         # Background tasks for live data fetching (to be added)
├── routes/              # API route modules
│   └── (routers to be added)
├── alembic/             # Database migration scripts
│   ├── versions/        # Migration version files
│   └── env.py           # Alembic environment configuration
├── alembic.ini          # Alembic configuration
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Database Models

### Outpost

Represents a Raspberry Pi outpost in the expedition network.

**Fields:**
- `id` (UUID): Primary key
- `name` (String): Unique outpost name
- `location_lat` (Float): Latitude (-90 to 90)
- `location_lon` (Float): Longitude (-180 to 180)
- `description` (Text): Outpost description
- `api_endpoint` (String): URL for outpost API
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

### ExpeditionLog

Represents a log entry from an outpost.

**Fields:**
- `id` (UUID): Primary key
- `timestamp` (DateTime): Event timestamp
- `outpost_id` (UUID): Foreign key to Outpost
- `event_type` (String): Type of event (e.g., "sensor_reading", "alert")
- `details` (JSON): Event-specific data
- `created_at` (DateTime): Database insertion timestamp

## API Endpoints (Planned)

### Outposts

- `GET /outposts` - List all outposts
- `GET /outposts/{id}` - Get outpost details
- `GET /outposts/{id}/live` - Get live data from outpost

### Expedition Logs

- `GET /expedition/logs` - List logs with filters and pagination
- `POST /expedition/logs` - Create new log entry

### Timeline

- `GET /timeline` - Get timeline events

### Achievements

- `GET /achievements` - List achievements
- `PUT /achievements/{id}` - Update achievement status

## Testing

### Run unit tests:

```bash
pytest tests/unit/
```

### Run integration tests:

```bash
pytest tests/integration/
```

### Run all tests with coverage:

```bash
pytest --cov=. --cov-report=html
```

## Development Tips

### Auto-reload with Uvicorn

The development server automatically reloads on code changes:

```bash
uvicorn main:app --reload
```

### SQL Query Logging

Enable SQL echo in `.env`:

```env
SQL_ECHO=true
```

### Database Connection Issues

If you encounter connection errors:

1. Verify PostgreSQL is running: `pg_isready`
2. Check DATABASE_URL format
3. Verify user permissions
4. Check firewall settings

### Async Best Practices

- Always use `await` with async functions
- Use `async with` for sessions
- Avoid blocking operations in async functions
- Use `asyncio.gather()` for concurrent operations

## Troubleshooting

### "Database does not exist" Error

```bash
createdb -U hudsonbay hudsonbay
```

### "Permission denied" Error

```sql
GRANT ALL PRIVILEGES ON DATABASE hudsonbay TO hudsonbay;
```

### Migration Conflicts

```bash
# Reset to base
alembic downgrade base

# Reapply migrations
alembic upgrade head
```

## License

Part of the Hudson Bay Interactive Expedition Console project.
