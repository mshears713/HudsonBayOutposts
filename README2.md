# Hudson Bay Interactive Expedition Console

---

## Overview

The **Hudson Bay Interactive Expedition Console** is an advanced, interactive web application designed to transform an educational Raspberry Pi API exercise into a rich, distributed system visualization platform. At its core, this project models a digital frontier where multiple Raspberry Pi outposts serve as nodes within an expansive expedition map. Users explore these outposts through a dynamic map-driven React UI, interact with live API data from Pis, and track their journey progress through logs, timelines, and narrative content.

This system not only amplifies the original API learning concept into an immersive experience but also offers a comprehensive full-stack development challenge. With back-end services powered by FastAPI interfacing with PostgreSQL, and a React front-end incorporating real-time data visualization and multi-node orchestration, this project reinforces mastery in modern RESTful API consumption, state management, asynchronous processing, and persistent data handling.

**Targeted at intermediate developers and AI agents alike**, the solution is designed for autonomous end-to-end execution without human intervention, ensuring a seamless build process that runs over 1-3 hours continuously. By completing this project, users and AI agents will acquire practical expertise in scalable full-stack design applied to distributed systems.

---

## Autonomous Execution Guide

**For AI Agents (Claude Code, etc.):**

This README is optimized for fully autonomous execution. To successfully deliver the complete Hudson Bay project, you must:

1. Execute all five phases sequentially, following each phase's detailed steps without skipping.
2. Obey all inter-step dependencies strictly before beginning each step.
3. Operate continuously without user intervention, input, or pauses.
4. Fully implement all functionalities—no placeholders or stubs.
5. Perform systematic testing and error handling as instructed at each step.
6. Save all progress diligently; only the final integrated product shall be surfaced to the user.

**Execution Strategy:**

- Follow steps numerically from 1 through 50.
- Complete phases fully before starting subsequent phases.
- Build comprehensive, production-quality code with detailed inline documentation and error handling.
- Where applicable, write and execute unit or integration tests promptly.
- Maintain code clarity, modularity, and adhere to best practices.
- Generate all required documentation, environment configurations, and deployment artifacts.

---

## Teaching Goals

### Learning Goals

- Master RESTful API design and consumption across multiple distributed Raspberry Pi endpoints with concurrent data fetching and integration.
- Practice component-centric UI development with map-driven architecture, employing React and TypeScript for dynamic visualization and real-time updates.
- Understand advanced state management strategies combining React Context and reducers to support complex multi-node workflows and story progression.
- Implement backend persistence for expedition logs and timelines using asynchronous database access patterns in FastAPI and PostgreSQL.
- Gain experience designing and building multi-node workflow coordination and comparative analytics synthesizing data from heterogeneous sensor nodes.

### Technical Goals

- Build a responsive, interactive web expedition console featuring a zoomable map and live data panels for multiple Raspberry Pi outposts.
- Implement robust backend REST APIs supporting data retrieval, log creation, timeline event management, achievements, and live Raspberry Pi data proxying.
- Architect and implement persistent storage using PostgreSQL with Alembic migrations and asynchronous ORM via SQLAlchemy.
- Enable multi-node orchestration workflows and real-time expedition story progression within both frontend and backend layers.
- Develop rich frontend analytics components using Plotly for comparative visualization across distributed nodes.
- Provide full coverage of unit and integration testing for backend APIs and frontend components.

### Priority Notes

- This project is suitable for intermediate developers with foundational knowledge of APIs and Raspberry Pi basics.
- The challenge lies in integrating multiple systems and applying asynchronous, distributed design principles with a focus on maintainability and scalability.
- The web application is the centerpiece and not an optional add-on; it transforms the original linear exploration into an interactive, replayable platform.
- While extensive cross-platform development is out of scope, the architecture provisions for future integration with mobile and desktop mission controllers.

---

## Technology Stack

- **Frontend:** React with TypeScript
  *Chosen for its component-based architecture, strong typing, and vibrant ecosystem supporting advanced UI workflows such as map integration, state management, and visualization.*
  *Key features: React Router v6 for navigation, React Context for state management, use of React hooks and functional components, integration with plotly.js for rich charts.*
  *Critical setup: TypeScript configuring strict type checking, CSS modules or styled-components for responsive styling.*

- **Backend:** FastAPI (Python 3.10+)
  *Selected for asynchronous-first design, automatic OpenAPI generation, and seamless integration with async ORM patterns*
  *Key features: async REST endpoints, dependency injection, ease of testing.*
  *Critical setup: Virtual environments, environment variable configuration, initial error logging setup.*

- **Database:** PostgreSQL
  *Reliable, feature-rich relational database with async driver support.*
  *Key features: support for JSON fields, timezone-aware datetime storage.*
  *Critical setup: Alembic migrations, async SQLAlchemy ORM integration.*

- **Libraries:**
  - `pandas` for data processing
  - `plotly` for frontend data visualization via React wrapper
  - `httpx` for async HTTP clients in backend API calls
  - `pytest` and related plugins for testing

**Framework Rationale:**
The stack choice balances accessibility and complexity, targeting intermediate developers aiming to grow skills in full-stack distributed systems. Modern asynchronous Python with FastAPI aligns well with React's event-driven frontend, enabling robust real-time data interactions. PostgreSQL's maturity and ecosystem fit well with the persistence and analytics requirements.

---

## Architecture Overview

The Hudson Bay Interactive Expedition Console is structured as a modular monorepo comprising two distinct codebases:

- `/backend` — FastAPI server managing database interactions, REST API endpoints, and proxying to Raspberry Pi outposts.
- `/frontend` — React/TypeScript SPA providing the expedition console UI with map-driven outpost exploration.

**Data Flow:**

1. **Frontend** sends REST requests (via `fetch` or axios) to **Backend API** endpoints for outposts, expedition logs, timelines, achievements, and live data.
2. **Backend** uses asynchronous database sessions (SQLAlchemy + asyncpg) to persist and query data in PostgreSQL.
3. For live data, **Backend** asynchronously fetches from multiple Raspberry Pi outposts' HTTP APIs using `httpx.AsyncClient` and serves it through proxy endpoints.
4. Periodic background scheduler tasks in backend fetch and store live data snapshots updating expedition logs.
5. Frontend components consume this data, manage global state with React Context, and render dynamic visualizations (maps, timelines, analytics charts).
6. Narrative content and achievements provide richness to the expedition story progression, integrated within UI and backend storage.
7. Docker configuration orchestrates backend, frontend, and database for consistent deployment environments.

**Directory Structure:**

```
root/
│
├── backend/
│   ├── main.py               # FastAPI app entrypoint
│   ├── api_client.py         # Pi outpost API client using httpx
│   ├── database.py           # Async DB engine/session setup
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic schemas for API
│   ├── routes/               # Routers for modular APIs
│   ├── scheduler.py          # Background scheduler tasks
│   ├── tests/                # Backend unit and integration tests
│   ├── migrations/           # Alembic migration scripts
│   └── README.md             # Backend setup and usage docs
│
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   ├── pages/             # React Router pages
│   │   ├── api/               # API access utilities
│   │   ├── context/           # React Context state management
│   │   ├── interfaces/        # TypeScript interfaces
│   │   ├── hooks/             # Custom React hooks for data fetching
│   │   ├── styles/            # CSS modules / styled-components
│   │   ├── App.tsx            # Application root
│   │   └── index.tsx          # Client entry point
│   ├── public/                # Static assets
│   ├── tests/                 # Frontend tests (Jest, RTL)
│   └── README.md              # Frontend usage and docs
│
├── docker-compose.yml          # Orchestration for backend/frontend/postgres
├── .env.example               # Environment variable templates
├── DEPLOYMENT.md              # Deployment instructions
└── README.md                  # This master README
```

---

## Implementation Plan

> **IMPORTANT:** Execute all five phases sequentially, fully completing each step with functional code, tests, and documentation before starting the next.

---

### Phase 1: Foundations & Setup

**Overview:**
Establish the foundational project structure, basic backend and frontend scaffolding, initial database setup with models, API client skeleton, and CORS configuration.

**Completion Criteria:**
A working split backend and frontend codebase with initialized Git repo, FastAPI backend ready with database connection, React app scaffolded with routing and interfaces, and basic middleware enabled.

---

#### Step 1: Initialize Git repository and project folders

**What to Build:**
Create a root project directory. Initialize Git. Add `/backend` and `/frontend` folders. Add `.gitignore` ignoring typical Python and Node artifacts. Commit initial empty structure with a `README.md` placeholder.

**Implementation Details:**
- In root, run `git init`.
- Create `/backend` and `/frontend` folders.
- Create `.gitignore` including entries: `node_modules/`, `.venv/`, `__pycache__/`, `.env`.
- Write minimal `README.md` with project title and brief purpose.
- Commit with message: "Initial project structure with backend and frontend folders".

**Dependencies:** None
**Acceptance Criteria:**
Git repo initialized with structure and .gitignore committed successfully.

---

#### Step 2: Set up FastAPI backend with virtual environment

**What to Build:**
Backend virtual environment with FastAPI and Uvicorn installed. Create `main.py` with basic FastAPI app and root GET endpoint returning JSON welcome message. Export requirements.txt.

**Implementation Details:**
- In `/backend`, run `python3 -m venv .venv` then activate.
- Install `fastapi` and `uvicorn`.
- Create `main.py` defining `app = FastAPI()`.
- Define `@app.get('/')` returning JSON `{ "message": "Welcome to Hudson Bay Expedition API" }`.
- Add docstrings explaining app creation.
- Add placeholder comments for error handling middleware for future.
- Freeze requirements to `requirements.txt`.
- Commit changes.

**Dependencies:** Step 1
**Acceptance Criteria:**
Backend starts successfully with `uvicorn main:app`, root endpoint accessible and returns expected JSON.

---

#### Step 3: Configure PostgreSQL database and connection in backend

**What to Build:**
Async SQLAlchemy setup connecting to PostgreSQL via environment-configured `DATABASE_URL`. Provide async session generator for dependency injection.

**Implementation Details:**
- Install `sqlalchemy[asyncio]` and `asyncpg`.
- Create `database.py` with `create_async_engine` using `os.getenv("DATABASE_URL")`.
- Define `AsyncSession` and `get_session()` async generator yielding session.
- Add exception handling to log DB connection issues with clear messages.
- Comment extensively on async lifecycle.
- Commit code.

**Dependencies:** Step 2
**Acceptance Criteria:**
Backend connects asynchronously to PostgreSQL without errors; `get_session` callable from routes for DB access.

---

#### Step 4: Define database models for outposts and expedition logs

**What to Build:**
Define SQLAlchemy ORM models `Outpost` and `ExpeditionLog` reflecting required fields with validations and docstrings.

**Implementation Details:**
- Create `models.py` using `declarative_base()`.
- Define `Outpost` with UUID primary key, name(string), lat/lon(float), description(text).
- Define `ExpeditionLog` with UUID id, timestamp, foreign key to outpost_id, event_type(string), details(JSON).
- Add `__repr__` methods.
- Include validators for non-null, unique constraints.
- Comment on fields and corner cases.
- Commit code.

**Dependencies:** Step 3
**Acceptance Criteria:**
Models defined and importable; data fields and relationships correct for further migrations.

---

#### Step 5: Create initial database migration scripts

**What to Build:**
Alembic setup and initial schema migration reflecting `Outpost` and `ExpeditionLog` tables deployed on PostgreSQL.

**Implementation Details:**
- Install `alembic` in backend env.
- Initialize alembic directory with `alembic init alembic/`.
- Configure `alembic.ini` to use `DATABASE_URL`.
- Modify `env.py` to load async engine and import models.
- Generate migration with `alembic revision --autogenerate -m 'Initial schema'`.
- Apply migration: `alembic upgrade head`.
- Document migration usage in backend README.
- Add error handling notes and rollback instructions in migration comments.
- Commit migration files.

**Dependencies:** Step 4
**Acceptance Criteria:**
Tables created in DB without errors; Alembic migration scripts present and documented.

---

#### Step 6: Initialize React app with TypeScript support

**What to Build:**
Create React application in `/frontend` with TypeScript template, base folder structure, and minimal `App.tsx`.

**Implementation Details:**
- Run `npx create-react-app . --template typescript` inside `/frontend`.
- Confirm strict mode in `tsconfig.json`.
- Remove boilerplate example files.
- Create folders: `/components`, `/pages`, `/interfaces`, `/api`.
- Add basic `App.tsx` component typed with props and JSDoc.
- Add README.md describing frontend scaffold.
- Run `npm start` and confirm no TypeScript errors.
- Commit initial frontend setup.

**Dependencies:** Step 1
**Acceptance Criteria:**
Frontend app runs locally with no errors; folder structure committed.

---

#### Step 7: Set up React Router and basic route structure

**What to Build:**
Integrate React Router v6 with routes: `/`, `/outposts`, `/outpost/:id`. Create placeholder pages with correct typing and error boundary for 404.

**Implementation Details:**
- Install `react-router-dom@6` and `@types/react-router-dom`.
- Wrap `App` with `<BrowserRouter>`.
- Define `<Routes>` with paths and corresponding components inside `/pages/`.
- Add simple components with React.FC typing and placeholder UI.
- Implement 404 fallback route.
- Add prop type guards on route params.
- Comment routing code extensively.
- Commit changes.

**Dependencies:** Step 6
**Acceptance Criteria:**
Routing works as expected; navigation between routes renders placeholders; 404 handled.

---

#### Step 8: Design TypeScript interfaces for outpost data and logs

**What to Build:**
Define `Outpost` and `ExpeditionLog` interfaces matching backend models with JSDoc.

**Implementation Details:**
- Create `interfaces/outpost.ts`.
- Define `Outpost` with id(string UUID), name(string), locationLat(number), locationLon(number), description(string).
- Define `ExpeditionLog` with id(string), timestamp(string ISO), outpostId(string), eventType(string), details typed as `Record<string, unknown>`.
- Include type guards for runtime validation.
- Add detailed comments and JSDoc.
- Commit interfaces.

**Dependencies:** Step 6, Step 4
**Acceptance Criteria:**
Interfaces type-safe and consistent with backend schema, ready for API client integration.

---

#### Step 9: Implement backend API client skeleton with HTTPX

**What to Build:**
Build asynchronous Python HTTP client to fetch live data from Raspberry Pi outposts with retries and error handling.

**Implementation Details:**
- In `/backend/api_client.py`, create class `PiOutpostClient`.
- Use `httpx.AsyncClient` with configurable base URL.
- Define `async fetch_live_data(outpost_url: str) -> dict`.
- Implement timeout and retry logic (2 retries with exponential backoff).
- Handle `httpx.RequestError`, `HTTPStatusError`; log detailed errors.
- Docstring methods specifying usage and exceptions.
- Add unit tests mocking HTTP calls with `pytest-asyncio` and `respx`.
- Commit code.

**Dependencies:** Step 3
**Acceptance Criteria:**
Client class works asynchronously; tests simulate normal and failed HTTP fetch scenarios.

---

#### Step 10: Set up cross-origin resource sharing (CORS) middleware in FastAPI

**What to Build:**
Configure `CORSMiddleware` to allow frontend requests from localhost and configurable origins.

**Implementation Details:**
- Modify `main.py` to add middleware with allowed origins from environment variables.
- Allow methods: `GET, POST, PUT, DELETE, OPTIONS`.
- Allow headers: `Authorization`, `Content-Type`.
- Include comments on security implications.
- Test with frontend dev server making API requests.
- Commit changes.

**Dependencies:** Step 2
**Acceptance Criteria:**
Backend accepts cross-origin requests from frontend without CORS errors.

---

### Phase 2: Core Functionality & API Integration

**Overview:**
Implement core REST API endpoints, frontend components fetching data, map integration, backend proxy to live Pi data, narrative content integration, state management, and background scheduler.

**Completion Criteria:**
Users can view and explore outposts, fetch live Pi data, see narrative content, interact with expedition logs and timeline. Backend supports core APIs with proper data persistence and proxying.

---

#### Step 11: Implement GET /outposts endpoint returning stored outposts

**What to Build:**
List all outposts stored in the DB, serialized with Pydantic response schemas.

**Implementation Details:**
- Create `routes/outposts.py` with an APIRouter.
- Define async endpoint `@router.get('/outposts')`.
- Use async DB session dependency.
- Query all `Outpost` asynchronously.
- Return serialized list via Pydantic schema in `schemas.py`.
- Handle DB errors with 500 responses.
- Document API with OpenAPI-compatible docstrings.
- Register router in `main.py`.
- Commit code.

**Dependencies:** Steps 4, 10
**Acceptance Criteria:**
Endpoint returns JSON array of outposts; API docs generated.

---

#### Step 12: Implement POST /expedition/logs endpoint for adding logs

**What to Build:**
Allow adding new expedition logs via POST request.

**Implementation Details:**
- Define Pydantic input model for log creation.
- Validate input strictly.
- Insert new `ExpeditionLog` with timestamp.
- Commit DB transaction atomically.
- Return saved log with ID and timestamp.
- Handle validation errors (422) and DB issues (500).
- Log creation events.
- Add detailed docstrings.
- Commit code.

**Dependencies:** Steps 4, 10
**Acceptance Criteria:**
Logs can be created via POST and returned with proper data.

---

#### Step 13: Implement GET /expedition/logs endpoint with optional filters

**What to Build:**
Support querying logs with filters (outpost_id, start_time, end_time), pagination included.

**Implementation Details:**
- Parse and validate optional query parameters.
- Build dynamic SQL query with filters.
- Sort results ascending by timestamp.
- Support `limit` and `offset` query params.
- Timezone-aware datetime handling.
- Return Pydantic-serialized array.
- Error handling for invalid filters.
- Document the API extensively.
- Add unit tests for filter combinations.
- Commit code.

**Dependencies:** Steps 4, 10
**Acceptance Criteria:**
Logs endpoint supports filter/pagination and returns correct data.

---

#### Step 14: Build React OutpostList component fetching /outposts

**What to Build:**
Display list of outposts fetched from backend.

**Implementation Details:**
- Create `/frontend/components/OutpostList.tsx` as functional component.
- Use `useEffect` to fetch `/outposts`, storing data in `useState`.
- Handle loading and error UI states with messages.
- Render names linked to outpost detail routes.
- Read API base URL from environment config.
- Comment fetching and error handling logic.
- Commit component.

**Dependencies:** Steps 8, 11
**Acceptance Criteria:**
Outpost list loads from backend and displays correctly with loading/error handling.

---

#### Step 15: Integrate static map UI with Leaflet showing outpost markers

**What to Build:**
Render interactive map showing markers for each outpost location.

**Implementation Details:**
- Install `react-leaflet` and dependencies.
- Create `ExpeditionMap.tsx` component accepting array of `Outpost`.
- Use `<MapContainer>`, `<TileLayer>`, `<Marker>`, `<Popup>`.
- Center and zoom configurable via env variables.
- Bind marker popups to name/description.
- Style container for responsiveness.
- Comment map integration and leaflet events.
- Handle missing/out-of-range coordinates gracefully.
- Commit component.

**Dependencies:** Steps 14, 8
**Acceptance Criteria:**
Map displays outpost markers accurately with interactive popups.

---

#### Step 16: Create OutpostDetail page fetching live API data from Pi outposts

**What to Build:**
Show outpost details and live sensor/status data with periodic updates.

**Implementation Details:**
- Accept `outpostId` from route.
- Fetch outpost metadata and live data via backend `/outpost/{id}/live` proxy.
- Use polling every 30 seconds using `setInterval` with cleanup.
- Show loading spinners and error states.
- Strongly type response with interfaces.
- Use React Context or local state as appropriate.
- Comment polling and error handling logic.
- Commit page.

**Dependencies:** Steps 7, 17, 8
**Acceptance Criteria:**
Outpost detail page loads data and updates live every 30 seconds without leaks.

---

#### Step 17: Implement backend proxy endpoint /outpost/{id}/live to fetch Pi data

**What to Build:**
Proxy backend endpoint fetching live data from physical Pi using `PiOutpostClient`.

**Implementation Details:**
- Define route with path param `id`.
- Query DB for outpost URL/IP.
- Fetch live data with retries and timeout.
- Return Pi data JSON as-is to frontend.
- Handle errors: 404 (outpost not found), 502 (Pi unreachable), 400 (malformed data).
- Log errors.
- Secure endpoint from leaking sensitive info.
- Docstring with response schema.
- Write test cases for normal and failure cases.
- Commit route.

**Dependencies:** Steps 9, 11
**Acceptance Criteria:**
Live data proxy endpoint responsive and robust with error codes.

---

#### Step 18: Add narrative content support in backend and frontend

**What to Build:**
Add database model and API to serve narrative content linked to outposts/events. Display narrative markdown in UI.

**Implementation Details:**
- Add `NarrativeContent` model with outpost relation and timestamp.
- Create endpoints to fetch narrative content with filtering.
- Define Pydantic schemas.
- Frontend: Add narrative panel rendering markdown using `react-markdown`.
- Cache content and show empty states gracefully.
- Add detailed commenting on story progression integration.
- Prepare for role-based permissions for future.
- Commit additions.

**Dependencies:** Steps 4, 14, 16
**Acceptance Criteria:**
Narrative text fetches and displays correctly within outpost pages.

---

#### Step 19: Implement frontend state management with React Context for expedition data

**What to Build:**
Centralized expedition data state including outposts, logs, live data, narrative.

**Implementation Details:**
- In `/context/ExpeditionContext.tsx`, define Context with `useReducer`.
- Strongly type state and actions.
- Provide fetch/refetch methods for API.
- Wrap main app component with provider.
- Add JSDoc and comments describing state shape and usage.
- Handle errors gracefully.
- Commit context implementation.

**Dependencies:** Steps 6, 14, 16, 18
**Acceptance Criteria:**
Global state available via context, enabling cross-component communication.

---

#### Step 20: Create backend scheduler to periodically fetch and store live data

**What to Build:**
Background scheduler fetching live sensor data from all outposts every 5 minutes and storing logs.

**Implementation Details:**
- Use APScheduler or `asyncio` tasks in `scheduler.py`.
- Fetch all outposts asynchronously with concurrency control.
- Use `PiOutpostClient` with retries.
- Insert new `ExpeditionLog` entries per fetch.
- Handle partial failures without aborting entire batch.
- Start scheduler via FastAPI startup event.
- Add detailed logging for audit.
- Commit scheduler.

**Dependencies:** Steps 9, 4, 12
**Acceptance Criteria:**
Scheduler runs in background, fetching/storing live data logs periodically without errors.

---

### Phase 3: Additional Features & Refinements

**Overview:**
Add expedition timeline events, achievements, multi-node workflow coordination, comparative analytics, offline handling, and corresponding UI components.

**Completion Criteria:**
Rich expedition features including timelines, achievements display, multi-node state visualization, analytics charts, and robust offline handling enable enhanced user insight.

---

#### Step 21: Add database model for expedition timeline events

**What to Build:**
Define `TimelineEvent` model with timestamp, title, description, and metadata.

**Implementation Details:**
- Add model in `models.py`.
- Generate Alembic migration.
- Include constraints and docstrings.
- Write unit tests for model validation.
- Commit changes.

**Dependencies:** Step 4
**Acceptance Criteria:**
TimelineEvent model persists and migrations applied correctly.

---

#### Step 22: Implement backend /timeline endpoint returning sorted events

**What to Build:**
Async endpoint returning ordered timeline events supporting filtering & pagination.

**Implementation Details:**
- Create GET `/timeline` endpoint.
- Support filters like date range, keywords.
- Return Pydantic-serialized event list.
- Add caching headers.
- Document API.
- Commit code.

**Dependencies:** Steps 21, 10
**Acceptance Criteria:**
Timeline events retrievable with filtering and sorting.

---

#### Step 23: Create React TimelineView component rendering event list

**What to Build:**
UI component rendering timeline with collapsible event details and accessibility.

**Implementation Details:**
- Fetch timeline data from backend.
- Format timestamps with `date-fns`.
- Add animations for expand/collapse.
- Use ARIA roles.
- Handle loading and errors.
- Comment data fetching and rendering logic.
- Commit component.

**Dependencies:** Steps 22, 8
**Acceptance Criteria:**
Timeline is visually clear, accessible, and responsive.

---

#### Step 24: Add achievement tracking database model and API

**What to Build:**
Add models for achievements and linking tables, REST API for retrieval and updates.

**Implementation Details:**
- Define `Achievement` and join model.
- Alembic migrations.
- Input validation via Pydantic.
- Endpoints for listing achievements and updating status.
- Error handling.
- Document API fully.
- Commit backend code.

**Dependencies:** Step 4
**Acceptance Criteria:**
Achievement data CRUD supported reliably.

---

#### Step 25: Build frontend AchievementPanel to display unlocked achievements

**What to Build:**
Visual panel presenting unlocked and locked achievements with interactive UI.

**Implementation Details:**
- Fetch data asynchronously.
- Display achievements with icons & tooltips.
- Animate unlocking.
- Integrate with expedition context.
- Support error/loading states.
- Accessibility considerations.
- Commit component.

**Dependencies:** Steps 24, 19, 8
**Acceptance Criteria:**
Achievements panel updates dynamically reflecting backend state.

---

#### Step 26: Implement multi-node workflow coordination in backend

**What to Build:**
`NodeWorkflowManager` to maintain node states and transitions.

**Implementation Details:**
- Implement state machine managing node statuses.
- Concurrency-safe updates.
- API endpoints to query and update workflows.
- Scheduler integration for live data influence.
- Docstring thoroughness.
- Commit code.

**Dependencies:** Steps 4, 20
**Acceptance Criteria:**
Multi-node state transitions managed and queryable reliably.

---

#### Step 27: Create React NodeWorkflow component showing node states

**What to Build:**
UI element showing nodes' current workflow states with status indicators and interactions.

**Implementation Details:**
- Use context to fetch node states.
- Use icons/colors to show status.
- Allow toggling details/history.
- Implement polling or basic real-time updates.
- Accessibility support.
- Comment mapping statuses to visuals.
- Commit component.

**Dependencies:** Steps 26, 19, 8
**Acceptance Criteria:**
Node workflow UI reflects backend states and updates dynamically.

---

#### Step 28: Develop comparative analytics backend endpoint

**What to Build:**
API delivering aggregated comparative sensor data for selected outposts/metrics.

**Implementation Details:**
- Accept query params defining metrics and outposts.
- Aggregate with SQL functions or Python.
- Return structured JSON for charts.
- Validate inputs with errors on bad requests.
- Add caching.
- Unit tests for aggregation correctness.
- Commit backend code.

**Dependencies:** Steps 4, 12, 13
**Acceptance Criteria:**
Comparative analytics endpoint provides accurate aggregated data.

---

#### Step 29: Design frontend ComparativeAnalytics component with Plotly charts

**What to Build:**
Render multiple sensor metrics comparisons using interactive Plotly charts.

**Implementation Details:**
- Fetch comparative analytics from backend.
- Use `react-plotly.js`; configure axes, legends.
- UI controls for selecting outposts and metrics.
- Add tooltips and filtering.
- Handle no data/error states.
- Comments explaining data and chart setup.
- Commit component.

**Dependencies:** Steps 28, 8
**Acceptance Criteria:**
Analytics charts render correctly, are interactive and responsive.

---

#### Step 30: Implement offline and error handling for unreachable outposts

**What to Build:**
Robust error detection and fallback UIs for network or Pi endpoint failures.

**Implementation Details:**
- Enhance proxy and scheduler with explicit error codes/descriptions.
- Frontend shows offline indicators with retry logic.
- Implement exponential backoff on live data fetches.
- Log offline nodes in scheduler.
- Comments explaining offline detection and UX impact.
- Commit backend and frontend.

**Dependencies:** Steps 17, 20, 16
**Acceptance Criteria:**
Offline/outpost unreachable states handled gracefully in backend & frontend.

---

### Phase 4: Polish, Testing & Optimization

**Overview:**
Add responsive styling, comprehensive unit and integration tests, performance optimizations, centralized logging, error boundaries, and data caching patterns.

**Completion Criteria:**
Project fully tested, polished for responsiveness and performance, with robust error handling and clear logs.

---

#### Step 31: Add responsive CSS styles for the expedition console UI

**What to Build:**
CSS modules or styled-components providing responsive layouts for all UI components.

**Implementation Details:**
- Use CSS grid/flexbox.
- Define breakpoints with media queries.
- Style maps, lists, panels, navbars uniformly.
- Include accessibility-focused contrast.
- Document styling choices.
- Commit styles.

**Dependencies:** Steps 6, 14, 15
**Acceptance Criteria:**
UI adapts elegantly to mobile and desktop layouts.

---

#### Step 32: Write unit tests for backend database models and API endpoints

**What to Build:**
Comprehensive pytest suite covering models, routes, and API client.

**Implementation Details:**
- Use pytest, pytest-asyncio, testcontainers or ephemeral PostgreSQL.
- Mock HTTP calls with pytest-mock.
- Test validation, error handling, pagination, concurrency.
- Write fixtures for consistent DB state.
- Document test purpose and coverage.
- Commit tests.

**Dependencies:** Steps 4, 11, 12, 13, 17
**Acceptance Criteria:**
Test suite runs cleanly with thorough coverage.

---

#### Step 33: Build integration tests for frontend API calls and state updates

**What to Build:**
Jest + React Testing Library tests simulating component mounting and user workflows.

**Implementation Details:**
- Mock API with MSW.
- Test OutpostList, OutpostDetail, TimelineView, and context state updates.
- Cover error and loading states.
- Add accessibility checks.
- Integrate tests in npm scripts.
- Commit tests.

**Dependencies:** Steps 14, 16, 19, 23
**Acceptance Criteria:**
Frontend components tested for correct data flow and rendering.

---

#### Step 34: Optimize backend live data fetching with async concurrency

**What to Build:**
Use `asyncio.gather` with semaphores for concurrent Pi data fetches with error isolation.

**Implementation Details:**
- Refactor scheduler and proxy data fetches.
- Limit concurrent requests to avoid resource exhaustion.
- Log partial fetch results and errors separately.
- Benchmark improvements.
- Comment concurrency strategies.
- Commit optimized code.

**Dependencies:** Steps 20, 17
**Acceptance Criteria:**
Live data fetching completes faster without concurrency errors.

---

#### Step 35: Add centralized error logging in backend with detailed traceback

**What to Build:**
Unified backend logging setup capturing exception tracebacks and state changes.

**Implementation Details:**
- Configure Python logging with rotating file handlers.
- Global exception handlers in FastAPI capturing errors.
- Log expected and unexpected errors with appropriate levels.
- Document logging config.
- Commit logger setup.

**Dependencies:** Steps 2, 17, 20
**Acceptance Criteria:**
Logs capture detailed error info for diagnostics.

---

#### Step 36: Implement frontend error boundaries for critical components

**What to Build:**
Reusable React error boundary with fallback UIs wrapping key components.

**Implementation Details:**
- Use class component extending `React.Component`.
- Catch rendering errors and display user-friendly messages.
- Provide retry button logic.
- Type with TypeScript.
- Log errors to console/backend monitoring endpoint.
- Commit ErrorBoundary and update component wraps.

**Dependencies:** Steps 14, 16, 23, 29
**Acceptance Criteria:**
UI gracefully handles rendering errors preventing app crashes.

---

#### Step 37: Enhance frontend data fetching with stale-while-revalidate pattern

**What to Build:**
Implement caching mechanism returning stale data immediately and refreshing asynchronously.

**Implementation Details:**
- Create custom hook `useFetchWithCache` or integrate `useSWR`.
- Typing with generics for API data.
- Support cache expiration configurable via env.
- Manage loading and fallback UI states.
- Unit test hook logic.
- Commit hook.

**Dependencies:** Steps 14, 16, 19
**Acceptance Criteria:**
Data fetching is optimized with cache while refreshing in background.

---

#### Step 38: Add pagination and filtering capabilities to expedition logs UI

**What to Build:**
Logs component with frontend controls for filtering by date, outpost, and event type, supporting pagination.

**Implementation Details:**
- Create inputs/selects for filters with debounce handling.
- Implement pagination controls with limit/offset.
- Reflect filter and pagination state in API queries.
- Validate inputs.
- Display log count and page status.
- Comment data flow and state synchronization.
- Commit UI enhancements.

**Dependencies:** Steps 13, 19, 8
**Acceptance Criteria:**
Users can filter and paginate logs with responsive UI and correct data.

---

#### Step 39: Conduct full manual end-to-end test of core expedition workflows

**What to Build:**
Perform thorough manual testing covering all core flows and error scenarios.

**Implementation Details:**
- Test viewing outposts, loading live data, timeline events, logs, achievements.
- Validate multi-node workflows and offline behavior.
- Use browser dev tools and backend logs.
- Document test cases and results.
- Commit test report.

**Dependencies:** Steps 11, 12, 16, 23, 24, 26
**Acceptance Criteria:**
All core features work as intended; issues documented and fixed.

---

#### Step 40: Profile and improve frontend rendering performance

**What to Build:**
Optimize React rendering with memoization, lazy loading, and virtualized lists.

**Implementation Details:**
- Profile with React Developer Tools.
- Memoize components with `React.memo`, `useCallback`, `useMemo`.
- Implement virtualization for large lists.
- Code split with `React.lazy` and `Suspense`.
- Minimize inline object/array props.
- Comment optimization reasons.
- Commit enhancements.

**Dependencies:** Steps 14, 15, 16, 23, 29
**Acceptance Criteria:**
Frontend demonstrates improved render performance without regressions.

---

### Phase 5: Documentation, Examples & Deployment Preparation

**Overview:**
Finalize project with comprehensive READMEs, example data seeds, API docs, Postman collections, Docker orchestration, environment configurations, deployment guide, and final release preparation.

**Completion Criteria:**
Project is fully documented, containerized, and ready for seamless deployment and future extension.

---

#### Step 41: Create backend README with setup, API docs, and usage instructions

**What to Build:**
Detailed backend setup instructions, environment variables, API documentation with examples.

**Implementation Details:**
- Write `/backend/README.md`.
- Include environment setup, DB migration, starting server.
- Document all main API endpoints.
- Provide sample curl/HTTPie commands.
- Add troubleshooting tips.
- Commit README.

---

#### Step 42: Create frontend README describing project structure and usage

**What to Build:**
Document frontend architecture, folder structure, development scripts, API integration, styling, and testing.

**Implementation Details:**
- Write `/frontend/README.md`.
- Add installation and dev commands.
- Document environment variables.
- Include usage notes and screenshots.
- Troubleshooting section.
- Commit README.

---

#### Step 43: Add example seed data scripts for outposts and logs

**What to Build:**
Python scripts to seed DB with realistic outposts and logs.

**Implementation Details:**
- Create `/backend/seeds/seed_data.py`.
- Use SQLAlchemy ORM to insert sample data.
- Commit with seed run instructions.

---

#### Step 44: Create example Postman collection or HTTP client config

**What to Build:**
Export Postman collection with curated requests for all APIs.

**Implementation Details:**
- Organize requests hierarchically.
- Add environment variables for base URL.
- Comment requests for clarity.
- Place `/docs/HudsonBay.postman_collection.json`.
- Document usage in backend README.

---

#### Step 45: Configure Docker setup for backend and frontend

**What to Build:**
Dockerfiles for backend and frontend, plus docker-compose orchestration with PostgreSQL.

**Implementation Details:**
- Backend Dockerfile: python slim, install deps, migrate DB, run uvicorn.
- Frontend Dockerfile: Node build + serve static files.
- `docker-compose.yml` mapping ports and volumes.
- Healthchecks and environment configs.
- Test full stack with `docker-compose up`.
- Commit Docker configs.

---

#### Step 46: Add environment variable support and configurations

**What to Build:**
Load env vars in backend using `python-dotenv` and frontend with `.env` files.

**Implementation Details:**
- Define Config class in backend reading `DATABASE_URL`, `CORS_ORIGINS`, `LOG_LEVEL`.
- Frontend `.env` with `REACT_APP_API_URL`.
- Validate presence on startup.
- Document env vars in READMEs.
- Commit configs.

---

#### Step 47: Perform final integration validation in Docker environment

**What to Build:**
Full system validation running backend, frontend, and DB in containers.

**Implementation Details:**
- Run all services.
- Test user flows, error cases.
- Check logs for issues.
- Run tests in containers where possible.
- Fix any integration bugs.
- Commit fixes and test report.

---

#### Step 48: Generate API OpenAPI documentation and frontend API typings

**What to Build:**
Export OpenAPI spec and generate TypeScript typings for frontend.

**Implementation Details:**
- Save `openapi.json` from FastAPI.
- Use `openapi-typescript` or swagger-typescript-api.
- Integrate typings into frontend API client.
- Automate generation script.
- Document process in READMEs.

---

#### Step 49: Create deployment guide covering environment, database, and build

**What to Build:**
Comprehensive deployment instructions covering all infrastructure aspects.

**Implementation Details:**
- Write `DEPLOYMENT.md`.
- Environment variables setup.
- DB provisioning and migrations.
- Docker/manual deployment options.
- Firewall and network config.
- Security considerations.
- Rollback plans.
- Commit guide.

---

#### Step 50: Archive final project artifacts and commit full deliverables

**What to Build:**
Prepare final release archive and tag repository.

**Implementation Details:**
- Ensure all code, tests, docs, configs committed.
- Tag repo as `v1.0.0`.
- Create zip/tarball of complete project.
- Document archive contents.
- Push to remote repo if configured.
- Commit final metadata.

---

## Implementation Strategy for AI Agents

- Begin with Phase 1, Step 1 and proceed sequentially.
- Fully implement each step with production-ready code; avoid placeholders.
- Write comprehensive inline documentation and adhere to coding best practices.
- Run tests as instructed to verify correctness before moving forward.
- Handle all anticipated error cases.
- Maintain consistent project structure and record progress.
- For frontend, ensure all UI components are responsive and accessible.
- For backend, ensure asynchronous database access and HTTP communication functions smoothly.
- Generate and maintain documentation and configuration files as per guidelines.
- Use environment variables for all sensitive or configuration data.
- Employ concurrency and scheduling effectively in backend processes.
- Leverage reusability with Context and hooks in frontend.
- Final deliverable is fully functional, documented, and deployable without any missing parts.

---

## Setup Instructions

- **Python version:** 3.10 or higher required
- **Backend virtual environment:**
  ```bash
  python3 -m venv backend/.venv
  source backend/.venv/bin/activate
  pip install -r backend/requirements.txt
  ```
- **Node version:** 16 or higher recommended
- **Frontend dependencies:**
  ```bash
  cd frontend
  npm install
  npm start
  ```
- **Environment Variables:**

  - Backend `.env` example:
    ```
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hudsonbay
    CORS_ORIGINS=http://localhost:3000
    LOG_LEVEL=INFO
    ```
  - Frontend `.env` example:
    ```
    REACT_APP_API_URL=http://localhost:8000
    ```

- **Database:**

  - Install and run PostgreSQL; create user and database.
  - Run Alembic migrations:
    ```bash
    cd backend
    alembic upgrade head
    ```
- **Starting services:**

  - Backend:
    ```bash
    uvicorn main:app --reload
    ```
  - Frontend:
    ```bash
    npm start
    ```
- **Docker environment:** Use docker-compose following instructions in `docker-compose.yml` and DEPLOYMENT.md for integrated environment setup.

---

## Testing Strategy

- **Unit tests:**
  Backend tests cover models, API routes, client fetch logic using `pytest`, `pytest-asyncio`. Frontend tests use `jest` and `@testing-library/react` with MSW to mock APIs.

- **Integration tests:**
  Simulate key user flows on frontend and backend, e.g., fetching outposts, adding logs, navigating UI, ensuring state updates.

- **Manual testing:**
  Follow manual test plan in step 39, simulate network failures, offline modes, and user interactions.

- **Edge cases:**
  - Invalid IDs or query params
  - Network timeouts and errors from Pis
  - Empty datasets and filtered results
  - Concurrent API calls and state changes

- **Validation:**
  Compliance with acceptance criteria per step is baseline.

---

## Success Metrics

- All planned backend and frontend functionalities implemented and tested.
- Application runs seamlessly with no unhandled exceptions or crashes.
- API endpoints respond correctly with proper validation and error codes.
- Frontend UI displays data dynamically, supporting navigation, visualization, and story progression.
- Logging and error boundaries capture and handle failures gracefully.
- Documentation complete for users and maintainers.
- Project containerized and deployable using Docker.
- Codebase well organized, documented with docstrings and comments.
- Final delivery tagged and archived cleanly in the source repository.

---

## Project Completion Checklist

- [ ] All 50 steps completed sequentially
- [ ] Each phase fully implemented and verified
- [ ] No placeholder or unfinished code remains
- [ ] Robust error handling across backend and frontend
- [ ] Code comprehensively documented with comments and docstrings
- [ ] README files for backend, frontend, and overall project finalized
- [ ] Unit and integration tests written and passing
- [ ] Full manual end-to-end tests documented and passed
- [ ] Responsive and accessible UI styling completed
- [ ] Docker setup configured and verified
- [ ] Environment variables and configuration files documented
- [ ] OpenAPI documentation and frontend typings generated
- [ ] Deployment guide complete and clear
- [ ] Final commit tagged as `v1.0.0` and project archived

---

*End of Hudson Bay Interactive Expedition Console README*
