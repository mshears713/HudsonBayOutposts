"""
Trading Fort API - FastAPI application for the trading outpost.

This API provides RESTful endpoints for managing trading fort goods,
trade records, traders, and price history.

Educational Note:
This Chapter 3 API demonstrates a complete trading system with authentication.
It showcases:
- CRUD operations for goods and traders
- Trade transaction management
- Price history tracking
- Token-based authentication from the start

To run this API:
    uvicorn raspberry_pi.api.trading_fort:app --host 0.0.0.0 --port 8001 --reload
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
DB_PATH = FilePath(__file__).parent.parent / "db" / "data" / "trading_fort.db"


# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================

class Good(BaseModel):
    """
    Represents a trade good in the trading fort inventory.

    Educational Note:
    Trade goods are the foundation of the fort's economy. This model
    tracks inventory, pricing, and quality information.
    """
    good_id: Optional[int] = Field(None, description="Unique good ID")
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., description="Category: furs, tools, trade_goods, provisions")
    quantity: int = Field(..., ge=0)
    unit: str
    base_price: float = Field(..., gt=0.0)
    current_price: float = Field(..., gt=0.0)
    quality: Optional[str] = Field(None, pattern="^(poor|fair|good|excellent)$")
    origin: Optional[str] = None
    description: Optional[str] = None
    last_updated: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Beaver Pelt",
                "category": "furs",
                "quantity": 150,
                "unit": "pelt",
                "base_price": 25.00,
                "current_price": 28.50,
                "quality": "excellent",
                "origin": "Northern Territories",
                "description": "Prime winter beaver"
            }
        }


class GoodCreate(BaseModel):
    """Model for creating new goods."""
    name: str = Field(..., min_length=1, max_length=100)
    category: str
    quantity: int = Field(..., ge=0)
    unit: str
    base_price: float = Field(..., gt=0.0)
    current_price: float = Field(..., gt=0.0)
    quality: Optional[str] = Field(None, pattern="^(poor|fair|good|excellent)$")
    origin: Optional[str] = None
    description: Optional[str] = None


class Trader(BaseModel):
    """Represents a trader in the trading fort registry."""
    trader_id: Optional[int] = None
    name: str = Field(..., min_length=1)
    trader_type: str = Field(..., pattern="^(trapper|native_trader|fort_trader|merchant)$")
    reputation: Optional[str] = Field(None, pattern="^(poor|fair|good|excellent)$")
    total_trades: Optional[int] = 0
    total_value: Optional[float] = 0.0
    credit_limit: Optional[float] = 0.0
    last_trade_date: Optional[str] = None
    notes: Optional[str] = None
    registered_date: Optional[str] = None


class TradeRecord(BaseModel):
    """Represents a trade transaction."""
    trade_id: Optional[int] = None
    good_id: int
    trader_id: int
    trade_type: str = Field(..., pattern="^(buy|sell|exchange)$")
    quantity: int = Field(..., gt=0)
    price_per_unit: float = Field(..., gt=0.0)
    total_value: float = Field(..., gt=0.0)
    trade_date: str
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None


class TradeSummary(BaseModel):
    """Summary statistics for trading fort."""
    total_goods: int
    total_goods_value: float
    total_traders: int
    total_trades: int
    total_trade_value: float
    last_updated: str


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Trading Fort API",
    description="Hudson Bay Company Trading Outpost RESTful API with Authentication",
    version="2.0.0",
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
    Create and return a database connection.

    Educational Note:
    Each request gets its own connection which is closed after use.
    In production with high traffic, consider connection pooling.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def dict_from_row(row) -> Dict:
    """Convert SQLite Row to dictionary."""
    return {key: row[key] for key in row.keys()} if row else {}


# ============================================================================
# Health and Status Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status of the API
    """
    return {
        "status": "healthy",
        "service": "Trading Fort API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status", response_model=TradeSummary)
async def get_status():
    """
    Get trading fort status and summary statistics.

    Educational Note:
    This aggregates data from multiple tables to provide a snapshot
    of the fort's trading activity and inventory.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get goods stats
        cursor.execute("""
            SELECT
                COUNT(*) as total_goods,
                SUM(quantity * current_price) as total_value
            FROM goods
        """)
        goods_stats = dict_from_row(cursor.fetchone())

        # Get trader count
        cursor.execute("SELECT COUNT(*) as total_traders FROM traders")
        traders_stats = dict_from_row(cursor.fetchone())

        # Get trade stats
        cursor.execute("""
            SELECT
                COUNT(*) as total_trades,
                SUM(total_value) as total_trade_value
            FROM trade_records
        """)
        trade_stats = dict_from_row(cursor.fetchone())

        conn.close()

        return TradeSummary(
            total_goods=goods_stats.get('total_goods', 0),
            total_goods_value=goods_stats.get('total_value', 0.0) or 0.0,
            total_traders=traders_stats.get('total_traders', 0),
            total_trades=trade_stats.get('total_trades', 0),
            total_trade_value=trade_stats.get('total_trade_value', 0.0) or 0.0,
            last_updated=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


# ============================================================================
# Goods Endpoints
# ============================================================================

@app.get("/goods", response_model=List[Good])
async def get_goods(
    category: Optional[str] = Query(None, description="Filter by category"),
    quality: Optional[str] = Query(None, description="Filter by quality")
):
    """
    Get all trade goods with optional filters.

    Educational Note:
    This demonstrates query parameter filtering. The API is flexible
    enough to return all goods or filter by specific criteria.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM goods WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if quality:
            query += " AND quality = ?"
            params.append(quality)

        query += " ORDER BY category, name"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [Good(**dict_from_row(row)) for row in rows]

    except Exception as e:
        logger.error(f"Error fetching goods: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch goods: {str(e)}")


@app.get("/goods/{good_id}", response_model=Good)
async def get_good(good_id: int = Path(..., description="Good ID")):
    """Get a specific trade good by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM goods WHERE good_id = ?", (good_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail=f"Good {good_id} not found")

        return Good(**dict_from_row(row))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching good {good_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch good: {str(e)}")


@app.post("/goods", response_model=Good, status_code=201, dependencies=[Depends(get_current_user)])
async def create_good(good: GoodCreate, current_user: User = Depends(get_current_user)):
    """
    Create a new trade good (requires authentication).

    Educational Note:
    This endpoint is protected - only authenticated users can add goods.
    The Depends(get_current_user) dependency ensures authentication.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO goods (name, category, quantity, unit, base_price, current_price, quality, origin, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            good.name, good.category, good.quantity, good.unit,
            good.base_price, good.current_price, good.quality,
            good.origin, good.description
        ))

        conn.commit()
        good_id = cursor.lastrowid
        conn.close()

        logger.info(f"Good created: {good.name} (ID: {good_id}) by {current_user.username}")

        # Fetch and return the created good
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goods WHERE good_id = ?", (good_id,))
        row = cursor.fetchone()
        conn.close()

        return Good(**dict_from_row(row))

    except Exception as e:
        logger.error(f"Error creating good: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create good: {str(e)}")


# ============================================================================
# Traders Endpoints
# ============================================================================

@app.get("/traders", response_model=List[Trader])
async def get_traders(
    trader_type: Optional[str] = Query(None, description="Filter by trader type")
):
    """Get all traders with optional filtering."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM traders WHERE 1=1"
        params = []

        if trader_type:
            query += " AND trader_type = ?"
            params.append(trader_type)

        query += " ORDER BY name"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [Trader(**dict_from_row(row)) for row in rows]

    except Exception as e:
        logger.error(f"Error fetching traders: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch traders: {str(e)}")


@app.get("/traders/{trader_id}", response_model=Trader)
async def get_trader(trader_id: int = Path(..., description="Trader ID")):
    """Get a specific trader by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM traders WHERE trader_id = ?", (trader_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail=f"Trader {trader_id} not found")

        return Trader(**dict_from_row(row))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trader {trader_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trader: {str(e)}")


# ============================================================================
# Trade Records Endpoints
# ============================================================================

@app.get("/trades", response_model=List[TradeRecord])
async def get_trades(
    trade_type: Optional[str] = Query(None, description="Filter by trade type"),
    trader_id: Optional[int] = Query(None, description="Filter by trader")
):
    """
    Get trade records with optional filtering.

    Educational Note:
    Trade history is crucial for understanding market dynamics and
    trader relationships.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM trade_records WHERE 1=1"
        params = []

        if trade_type:
            query += " AND trade_type = ?"
            params.append(trade_type)

        if trader_id:
            query += " AND trader_id = ?"
            params.append(trader_id)

        query += " ORDER BY trade_date DESC LIMIT 100"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [TradeRecord(**dict_from_row(row)) for row in rows]

    except Exception as e:
        logger.error(f"Error fetching trades: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trades: {str(e)}")


@app.get("/trades/summary")
async def get_trade_summary():
    """
    Get trade summary statistics.

    Educational Note:
    Aggregated statistics help understand overall trading patterns.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                trade_type,
                COUNT(*) as count,
                SUM(total_value) as total_value,
                AVG(total_value) as avg_value
            FROM trade_records
            GROUP BY trade_type
        """)
        rows = cursor.fetchall()

        summary = {row[0]: {
            'count': row[1],
            'total_value': row[2] or 0.0,
            'avg_value': row[3] or 0.0
        } for row in rows}

        conn.close()

        return {
            "summary_by_type": summary,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting trade summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


# ============================================================================
# Price History Endpoint
# ============================================================================

@app.get("/goods/{good_id}/price-history")
async def get_price_history(
    good_id: int = Path(..., description="Good ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days of history")
):
    """
    Get price history for a specific good.

    Educational Note:
    Price history helps identify market trends and seasonal variations.
    This is useful for trading strategy and forecasting.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First verify good exists
        cursor.execute("SELECT name FROM goods WHERE good_id = ?", (good_id,))
        good = cursor.fetchone()
        if not good:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Good {good_id} not found")

        # Get price history
        cursor.execute("""
            SELECT price, recorded_date, market_condition
            FROM price_history
            WHERE good_id = ?
            ORDER BY recorded_date DESC
            LIMIT ?
        """, (good_id, days))

        rows = cursor.fetchall()
        conn.close()

        history = [{
            'price': row[0],
            'date': row[1],
            'market_condition': row[2]
        } for row in rows]

        return {
            "good_id": good_id,
            "good_name": good[0],
            "history": history,
            "records_count": len(history)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get price history: {str(e)}")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("🏪 Starting Trading Fort API...")
    print(f"📂 Database: {DB_PATH}")
    print("📡 Server will start at http://0.0.0.0:8001")
    print("📚 Documentation: http://0.0.0.0:8001/docs")
    print("🔐 Authentication enabled")

    uvicorn.run(
        "trading_fort:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
