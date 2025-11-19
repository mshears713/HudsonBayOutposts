# Hudson Bay Interactive Expedition Console

## 45-Minute Quickstart Implementation

This is a **streamlined foundation** for the Hudson Bay Interactive Expedition Console - a full-stack React + FastAPI + PostgreSQL application for visualizing and managing distributed Raspberry Pi outposts.

---

## ✅ What's Implemented (Complete Phase 1)

### Backend (FastAPI + PostgreSQL)

**Core Infrastructure:**
- ✅ FastAPI application with async support
- ✅ PostgreSQL database connection (async SQLAlchemy)
- ✅ Alembic migrations configured
- ✅ CORS middleware for frontend integration

**Database Models:**
- ✅ `Outpost` model with validation
- ✅ `ExpeditionLog` model with JSON details field

**API Endpoints:**
- ✅ `GET /` - Welcome/status endpoint
- ✅ `GET /health` - Health check
- ✅ `GET /outposts` - List all outposts with Pydantic validation

**Components:**
- ✅ Pydantic schemas for type-safe API contracts
- ✅ HTTPX async client for Raspberry Pi communication
- ✅ Async database session management with error handling

### Frontend (React + TypeScript)

**Core Setup:**
- ✅ React 18 with TypeScript strict mode
- ✅ React Router v6 with 3 routes (Home, Outposts, 404)
- ✅ Organized folder structure

**Components:**
- ✅ `OutpostList` - Fetches and displays outposts
- ✅ TypeScript interfaces matching backend models
- ✅ API client with error handling and loading states

**Features:**
- ✅ Async data fetching from backend
- ✅ Error boundaries and user feedback
- ✅ Responsive card-based layout
- ✅ Navigation between pages

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL 12+

### 1. Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create database
createdb hudsonbay

# Set environment
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/hudsonbay"

# Run migrations (when you have a running database)
# alembic upgrade head

# Start server
uvicorn main:app --reload
```

**Backend runs at:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend
npm install
npm start
```

**Frontend runs at:** http://localhost:3000

---

## Project Structure

```
HudsonBayOutposts/
├── backend/
│   ├── main.py            # FastAPI app with CORS and endpoints
│   ├── database.py        # Async SQLAlchemy configuration
│   ├── models.py          # ORM models
│   ├── schemas.py         # Pydantic schemas
│   ├── api_client.py      # HTTPX client
│   ├── alembic/           # Migrations
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/OutpostList.tsx
    │   ├── pages/
    │   ├── interfaces/outpost.ts
    │   ├── api/client.ts
    │   └── App.tsx
    └── package.json
```

---

## Environment Variables

### Backend `.env`
```env
DATABASE_URL=postgresql+asyncpg://hudsonbay:hudsonbay@localhost:5432/hudsonbay
CORS_ORIGINS=http://localhost:3000
SQL_ECHO=false
```

### Frontend `.env`
```env
REACT_APP_API_URL=http://localhost:8000
```

---

## Next Steps (Roadmap)

### Phase 2: Core Features
1. Interactive Leaflet map
2. Live data proxy endpoints
3. Expedition logs CRUD
4. React Context state management

### Phase 3: Advanced Features
5. Timeline visualization
6. Achievements system
7. Plotly analytics charts
8. Background scheduler tasks

### Phase 4: Production
9. Testing (pytest, Jest)
10. Docker setup
11. Deployment guide

---

## Technology Stack

- **Backend:** FastAPI, SQLAlchemy (async), PostgreSQL, Alembic, HTTPX, Pydantic
- **Frontend:** React 18, TypeScript, React Router v6
- **Future:** Leaflet, Plotly.js, date-fns, react-markdown

---

## What You Get

✅ **Full-stack foundation** ready for extension  
✅ **Type-safe** interfaces on both ends  
✅ **Working API** with database persistence  
✅ **Frontend** fetching and displaying data  
✅ **Development environment** configured  

**Total implementation time:** ~45 minutes

This provides a **production-quality foundation** that can be extended iteratively!
