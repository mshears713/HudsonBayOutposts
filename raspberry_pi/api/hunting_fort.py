"""
Hunting Fort API - FastAPI application for the hunting outpost.

This API provides RESTful endpoints for managing hunting fort operations,
including game tracking, hunting parties, pelts harvested, and seasonal reports.

Educational Note:
This Chapter 4 API demonstrates advanced themed operations with authentication.
It showcases:
- Game and wildlife tracking
- Hunting party management
- Pelt harvest records
- Seasonal hunting statistics
- Token-based authentication throughout

To run this API:
    uvicorn raspberry_pi.api.hunting_fort:app --host 0.0.0.0 --port 8002 --reload
"""

from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import sqlite3
from pathlib import Path as FilePath
import logging

# Import authentication middleware
from .auth_middleware import add_auth_routes, get_current_user, User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = FilePath(__file__).parent.parent / "db" / "data" / "hunting_fort.db"


# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================

class GameAnimal(BaseModel):
    """
    Represents a game animal species tracked by the hunting fort.

    Educational Note:
    Wildlife management is crucial for sustainable hunting. This model
    tracks population, seasonal patterns, and conservation status.
    """
    animal_id: Optional[int] = Field(None, description="Unique animal ID")
    species: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., description="Category: big_game, small_game, fur_bearer, waterfowl")
    typical_size: str = Field(..., description="Size range (e.g., '40-60 kg')")
    pelt_value: Optional[float] = Field(None, ge=0.0, description="Average pelt value in dollars")
    meat_yield: Optional[str] = Field(None, description="Typical meat yield")
    population_status: str = Field(..., pattern="^(abundant|common|fair|scarce|protected)$")
    best_season: str = Field(..., description="Primary hunting season")
    habitat: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "species": "Moose",
                "category": "big_game",
                "typical_size": "400-600 kg",
                "pelt_value": 50.00,
                "meat_yield": "200-400 kg",
                "population_status": "common",
                "best_season": "Fall/Winter",
                "habitat": "Boreal forest, wetlands"
            }
        }


class HuntingParty(BaseModel):
    """Represents a hunting party expedition."""
    party_id: Optional[int] = None
    leader_name: str = Field(..., min_length=1)
    party_size: int = Field(..., ge=1, le=20)
    start_date: str
    end_date: Optional[str] = None
    status: str = Field(..., pattern="^(planning|active|completed|cancelled)$")
    target_species: Optional[str] = None
    region: Optional[str] = None
    total_harvest: Optional[int] = Field(0, ge=0)
    success_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "leader_name": "Jean-Baptiste Lafleur",
                "party_size": 5,
                "start_date": "2025-01-15",
                "status": "active",
                "target_species": "Beaver",
                "region": "North Creek Territory",
                "total_harvest": 12
            }
        }


class PeltHarvest(BaseModel):
    """Represents a pelt harvest record."""
    harvest_id: Optional[int] = None
    party_id: int
    species: str
    quantity: int = Field(..., ge=1)
    quality: str = Field(..., pattern="^(poor|fair|good|prime|exceptional)$")
    date_harvested: str
    estimated_value: float = Field(..., ge=0.0)
    condition: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "party_id": 1,
                "species": "Beaver",
                "quantity": 3,
                "quality": "prime",
                "date_harvested": "2025-01-18",
                "estimated_value": 75.00,
                "condition": "Excellent winter coat"
            }
        }


class SeasonalReport(BaseModel):
    """Represents a seasonal hunting summary."""
    report_id: Optional[int] = None
    season: str = Field(..., description="Season name (e.g., 'Winter 2025')")
    year: int
    total_parties: int = Field(0, ge=0)
    total_hunters: int = Field(0, ge=0)
    total_pelts: int = Field(0, ge=0)
    total_value: float = Field(0.0, ge=0.0)
    top_species: Optional[str] = None
    weather_conditions: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "season": "Winter 2025",
                "year": 2025,
                "total_parties": 15,
                "total_hunters": 68,
                "total_pelts": 342,
                "total_value": 8550.00,
                "top_species": "Beaver",
                "weather_conditions": "Cold, ideal for trapping"
            }
        }


# ============================================================================
# FastAPI App Initialization
# ============================================================================

app = FastAPI(
    title="Hudson Bay Hunting Fort API",
    description="RESTful API for managing hunting fort operations, game tracking, and pelt harvests",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add authentication routes
add_auth_routes(app)


# ============================================================================
# Database Helper Functions
# ============================================================================

def get_db_connection():
    """
    Get a database connection.

    Educational Note:
    This helper function centralizes database connection logic.
    Always use context managers to ensure connections are properly closed.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def row_to_dict(row: sqlite3.Row) -> Dict:
    """Convert a database row to a dictionary."""
    return dict(row) if row else {}


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Hudson Bay Hunting Fort API",
        "version": "1.0.0",
        "description": "Manage hunting operations, game tracking, and pelt harvests",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Educational Note:
    Health checks are essential for monitoring distributed systems.
    They allow monitoring tools to verify the service is operational.
    """
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/status")
async def get_status():
    """
    Get hunting fort status summary.

    Educational Note:
    Status endpoints provide high-level metrics useful for dashboards
    and monitoring without requiring detailed queries.
    """
    try:
        conn = get_db_connection()

        # Get total game species
        total_species = conn.execute(
            "SELECT COUNT(*) as count FROM game_animals"
        ).fetchone()['count']

        # Get active hunting parties
        active_parties = conn.execute(
            "SELECT COUNT(*) as count FROM hunting_parties WHERE status = 'active'"
        ).fetchone()['count']

        # Get total pelts this season
        total_pelts = conn.execute(
            "SELECT COUNT(*) as count FROM pelt_harvests WHERE date_harvested >= date('now', 'start of year')"
        ).fetchone()['count']

        # Get total pelt value this season
        total_value = conn.execute(
            "SELECT COALESCE(SUM(estimated_value), 0) as total FROM pelt_harvests WHERE date_harvested >= date('now', 'start of year')"
        ).fetchone()['total']

        conn.close()

        return {
            "fort_name": "Hunting Fort",
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "tracked_species": total_species,
                "active_parties": active_parties,
                "pelts_this_season": total_pelts,
                "value_this_season": round(total_value, 2)
            }
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Game Animals Endpoints
# ============================================================================

@app.get("/animals", response_model=List[GameAnimal])
async def get_animals(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by population status")
):
    """
    Get list of game animals with optional filters.

    Educational Note:
    This endpoint demonstrates filtering with query parameters.
    The database query is built dynamically based on provided filters.
    """
    try:
        conn = get_db_connection()

        query = "SELECT * FROM game_animals WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if status:
            query += " AND population_status = ?"
            params.append(status)

        query += " ORDER BY species"

        rows = conn.execute(query, params).fetchall()
        conn.close()

        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting animals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/animals/{animal_id}", response_model=GameAnimal)
async def get_animal(animal_id: int = Path(..., gt=0)):
    """Get a specific game animal by ID."""
    try:
        conn = get_db_connection()
        row = conn.execute(
            "SELECT * FROM game_animals WHERE animal_id = ?",
            (animal_id,)
        ).fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail=f"Animal {animal_id} not found")

        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting animal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Hunting Parties Endpoints
# ============================================================================

@app.get("/parties", response_model=List[HuntingParty])
async def get_hunting_parties(
    status: Optional[str] = Query(None, description="Filter by status"),
    region: Optional[str] = Query(None, description="Filter by region")
):
    """Get list of hunting parties with optional filters."""
    try:
        conn = get_db_connection()

        query = "SELECT * FROM hunting_parties WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if region:
            query += " AND region = ?"
            params.append(region)

        query += " ORDER BY start_date DESC"

        rows = conn.execute(query, params).fetchall()
        conn.close()

        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting parties: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/parties/{party_id}", response_model=HuntingParty)
async def get_hunting_party(party_id: int = Path(..., gt=0)):
    """Get a specific hunting party by ID."""
    try:
        conn = get_db_connection()
        row = conn.execute(
            "SELECT * FROM hunting_parties WHERE party_id = ?",
            (party_id,)
        ).fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail=f"Party {party_id} not found")

        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting party: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Pelt Harvests Endpoints
# ============================================================================

@app.get("/harvests", response_model=List[PeltHarvest])
async def get_pelt_harvests(
    species: Optional[str] = Query(None, description="Filter by species"),
    quality: Optional[str] = Query(None, description="Filter by quality"),
    party_id: Optional[int] = Query(None, description="Filter by party ID")
):
    """Get list of pelt harvests with optional filters."""
    try:
        conn = get_db_connection()

        query = "SELECT * FROM pelt_harvests WHERE 1=1"
        params = []

        if species:
            query += " AND species = ?"
            params.append(species)

        if quality:
            query += " AND quality = ?"
            params.append(quality)

        if party_id:
            query += " AND party_id = ?"
            params.append(party_id)

        query += " ORDER BY date_harvested DESC"

        rows = conn.execute(query, params).fetchall()
        conn.close()

        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting harvests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/harvests/summary")
async def get_harvest_summary():
    """
    Get summary statistics for pelt harvests.

    Educational Note:
    Aggregate queries provide valuable insights from large datasets.
    This endpoint demonstrates SQL aggregation functions.
    """
    try:
        conn = get_db_connection()

        # Total harvests
        total = conn.execute(
            "SELECT COUNT(*) as count FROM pelt_harvests"
        ).fetchone()['count']

        # Total value
        total_value = conn.execute(
            "SELECT COALESCE(SUM(estimated_value), 0) as total FROM pelt_harvests"
        ).fetchone()['total']

        # Total pelts
        total_pelts = conn.execute(
            "SELECT COALESCE(SUM(quantity), 0) as total FROM pelt_harvests"
        ).fetchone()['total']

        # By species
        by_species = conn.execute("""
            SELECT species, COUNT(*) as records, SUM(quantity) as total_pelts,
                   SUM(estimated_value) as total_value
            FROM pelt_harvests
            GROUP BY species
            ORDER BY total_value DESC
        """).fetchall()

        # By quality
        by_quality = conn.execute("""
            SELECT quality, COUNT(*) as records, SUM(quantity) as total_pelts
            FROM pelt_harvests
            GROUP BY quality
            ORDER BY
                CASE quality
                    WHEN 'exceptional' THEN 1
                    WHEN 'prime' THEN 2
                    WHEN 'good' THEN 3
                    WHEN 'fair' THEN 4
                    WHEN 'poor' THEN 5
                END
        """).fetchall()

        conn.close()

        return {
            "total_records": total,
            "total_pelts": total_pelts,
            "total_value": round(total_value, 2),
            "by_species": [dict(row) for row in by_species],
            "by_quality": [dict(row) for row in by_quality]
        }
    except Exception as e:
        logger.error(f"Error getting harvest summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Seasonal Reports Endpoints
# ============================================================================

@app.get("/reports", response_model=List[SeasonalReport])
async def get_seasonal_reports(
    year: Optional[int] = Query(None, description="Filter by year")
):
    """Get seasonal hunting reports."""
    try:
        conn = get_db_connection()

        query = "SELECT * FROM seasonal_reports WHERE 1=1"
        params = []

        if year:
            query += " AND year = ?"
            params.append(year)

        query += " ORDER BY year DESC, season DESC"

        rows = conn.execute(query, params).fetchall()
        conn.close()

        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/{report_id}", response_model=SeasonalReport)
async def get_seasonal_report(report_id: int = Path(..., gt=0)):
    """Get a specific seasonal report by ID."""
    try:
        conn = get_db_connection()
        row = conn.execute(
            "SELECT * FROM seasonal_reports WHERE report_id = ?",
            (report_id,)
        ).fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Protected Endpoints (Require Authentication)
# ============================================================================

@app.post("/animals", response_model=GameAnimal, dependencies=[Depends(get_current_user)])
async def create_animal(animal: GameAnimal, current_user: User = Depends(get_current_user)):
    """
    Create a new game animal record (requires authentication).

    Educational Note:
    This protected endpoint requires a valid JWT token.
    Only authenticated users can add new game species to track.
    """
    try:
        conn = get_db_connection()

        cursor = conn.execute("""
            INSERT INTO game_animals
            (species, category, typical_size, pelt_value, meat_yield,
             population_status, best_season, habitat, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            animal.species, animal.category, animal.typical_size,
            animal.pelt_value, animal.meat_yield, animal.population_status,
            animal.best_season, animal.habitat, animal.notes
        ))

        animal_id = cursor.lastrowid
        conn.commit()

        # Fetch the created record
        row = conn.execute(
            "SELECT * FROM game_animals WHERE animal_id = ?",
            (animal_id,)
        ).fetchone()

        conn.close()

        logger.info(f"Animal created by {current_user.username}: {animal.species}")
        return dict(row)
    except Exception as e:
        logger.error(f"Error creating animal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parties", response_model=HuntingParty, dependencies=[Depends(get_current_user)])
async def create_hunting_party(party: HuntingParty, current_user: User = Depends(get_current_user)):
    """Create a new hunting party (requires authentication)."""
    try:
        conn = get_db_connection()

        cursor = conn.execute("""
            INSERT INTO hunting_parties
            (leader_name, party_size, start_date, end_date, status,
             target_species, region, total_harvest, success_rate, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            party.leader_name, party.party_size, party.start_date,
            party.end_date, party.status, party.target_species,
            party.region, party.total_harvest, party.success_rate, party.notes
        ))

        party_id = cursor.lastrowid
        conn.commit()

        row = conn.execute(
            "SELECT * FROM hunting_parties WHERE party_id = ?",
            (party_id,)
        ).fetchone()

        conn.close()

        logger.info(f"Hunting party created by {current_user.username}: {party.leader_name}")
        return dict(row)
    except Exception as e:
        logger.error(f"Error creating party: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/statistics", dependencies=[Depends(get_current_user)])
async def get_admin_statistics(current_user: User = Depends(get_current_user)):
    """
    Get comprehensive administrative statistics (requires authentication).

    Educational Note:
    Admin endpoints provide detailed system information for management.
    This demonstrates aggregating data from multiple tables.
    """
    try:
        conn = get_db_connection()

        # Game animals stats
        animal_stats = {
            "total_species": conn.execute("SELECT COUNT(*) as c FROM game_animals").fetchone()['c'],
            "by_category": [dict(row) for row in conn.execute("""
                SELECT category, COUNT(*) as count
                FROM game_animals
                GROUP BY category
                ORDER BY count DESC
            """).fetchall()],
            "by_status": [dict(row) for row in conn.execute("""
                SELECT population_status, COUNT(*) as count
                FROM game_animals
                GROUP BY population_status
                ORDER BY count DESC
            """).fetchall()]
        }

        # Hunting parties stats
        party_stats = {
            "total_parties": conn.execute("SELECT COUNT(*) as c FROM hunting_parties").fetchone()['c'],
            "active_parties": conn.execute("SELECT COUNT(*) as c FROM hunting_parties WHERE status = 'active'").fetchone()['c'],
            "by_status": [dict(row) for row in conn.execute("""
                SELECT status, COUNT(*) as count
                FROM hunting_parties
                GROUP BY status
                ORDER BY count DESC
            """).fetchall()]
        }

        # Harvest stats
        harvest_stats = {
            "total_records": conn.execute("SELECT COUNT(*) as c FROM pelt_harvests").fetchone()['c'],
            "total_pelts": conn.execute("SELECT COALESCE(SUM(quantity), 0) as c FROM pelt_harvests").fetchone()['c'],
            "total_value": conn.execute("SELECT COALESCE(SUM(estimated_value), 0) as c FROM pelt_harvests").fetchone()['c']
        }

        conn.close()

        return {
            "fort_name": "Hunting Fort",
            "generated_at": datetime.now().isoformat(),
            "generated_by": current_user.username,
            "animals": animal_stats,
            "parties": party_stats,
            "harvests": harvest_stats
        }
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Application Startup
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.

    Educational Note:
    Startup events are useful for initialization tasks like
    verifying database connections and logging configuration.
    """
    logger.info("Starting Hunting Fort API...")
    logger.info(f"Database path: {DB_PATH}")

    # Verify database exists
    if not DB_PATH.exists():
        logger.warning(f"Database not found at {DB_PATH}")
        logger.warning("Please run: python raspberry_pi/db/init_hunting_fort.py")
    else:
        logger.info("Database connection verified")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
