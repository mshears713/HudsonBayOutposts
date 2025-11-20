# Hudson Bay Expedition Console - Backend

FastAPI-based backend providing REST APIs for the Hudson Bay Interactive Expedition Console.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL="postgresql+asyncpg://hudsonbay:hudsonbay@localhost:5432/hudsonbay"

# Run migrations (creates tables)
alembic upgrade head

# Seed sample data
python seed_data.py

# Start server
uvicorn main:app --reload
```

**Server runs at:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

## API Endpoints

### Core Endpoints

- `GET /` - Welcome message and API info
- `GET /health` - Health check for monitoring

### Outposts

- `GET /outposts` - List all outposts
- `GET /outposts/{id}` - Get specific outpost by ID

### Expedition Logs

- `GET /expedition/logs` - List logs with filtering
  - Query params: `outpost_id`, `event_type`, `limit`, `offset`
- `POST /expedition/logs` - Create new log entry

### Example Requests

**Get all outposts:**
```bash
curl http://localhost:8000/outposts
```

**Get logs for specific outpost:**
```bash
curl "http://localhost:8000/expedition/logs?outpost_id=UUID&limit=10"
```

**Create a log entry:**
```bash
curl -X POST http://localhost:8000/expedition/logs \
  -H "Content-Type: application/json" \
  -d '{
    "outpost_id": "UUID",
    "event_type": "sensor_reading",
    "details": {"temperature": 22.5, "humidity": 60}
  }'
```

## Database Models

### Outpost
- `id` (UUID) - Primary key
- `name` (String) - Unique outpost name
- `location_lat` (Float) - Latitude
- `location_lon` (Float) - Longitude
- `description` (Text) - Description
- `api_endpoint` (String) - API URL
- `created_at`, `updated_at` - Timestamps

### ExpeditionLog
- `id` (UUID) - Primary key
- `timestamp` (DateTime) - Event time
- `outpost_id` (UUID) - Foreign key to Outpost
- `event_type` (String) - Event category
- `details` (JSON) - Event data
- `created_at` - Creation timestamp

## Database Setup

### Create Database

```sql
CREATE USER hudsonbay WITH PASSWORD 'hudsonbay';
CREATE DATABASE hudsonbay OWNER hudsonbay;
GRANT ALL PRIVILEGES ON DATABASE hudsonbay TO hudsonbay;
```

### Run Migrations

```bash
# Generate migration (after model changes)
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Seed Data

```bash
python seed_data.py
```

This creates 4 sample outposts with locations and sample log entries.

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hudsonbay
CORS_ORIGINS=http://localhost:3000
SQL_ECHO=false
LOG_LEVEL=INFO
```

## Development

### Auto-reload Server

```bash
uvicorn main:app --reload
```

### View Logs

Enable SQL logging:
```env
SQL_ECHO=true
```

### Testing

```bash
pytest tests/
```

## Project Structure

```
backend/
├── main.py              # FastAPI app and endpoints
├── database.py          # Async database setup
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic validation schemas
├── api_client.py        # HTTP client for Pi outposts
├── seed_data.py         # Database seeding script
├── alembic/             # Migration scripts
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

## Troubleshooting

**Database connection error:**
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL format
- Ensure user has permissions

**Import errors:**
```bash
pip install -r requirements.txt
```

**Migration conflicts:**
```bash
alembic downgrade base
alembic upgrade head
```

## License

Part of the Hudson Bay Interactive Expedition Console project.
