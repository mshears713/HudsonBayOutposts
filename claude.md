# Raspberry Pi Frontier - Claude Context

## Project Overview

Raspberry Pi Frontier is an immersive 10-chapter interactive learning adventure built with Streamlit and FastAPI. It teaches distributed systems, API design, SSH management, and authentication through a creative historical narrative of managing Raspberry Pi "Hudson Bay Company outposts."

**Key Characteristics:**
- Educational project designed for intermediate Python developers
- 3-4 week learning timeline
- Hands-on emphasis on SSH, RESTful APIs, authentication, and distributed systems
- Creative frontier/historical fort theming for engagement
- Centralized Streamlit dashboard controlling distributed Raspberry Pi nodes

## Target Audience & Learning Goals

**Learner Profile:**
- Intermediate Python developers
- Basic networking knowledge
- Interest in distributed systems and API development

**Primary Learning Objectives:**
1. Master SSH usage for remote Raspberry Pi management
2. Design and consume RESTful APIs with JSON payloads
3. Develop multi-endpoint workflows across distributed nodes
4. Implement token-based API authentication
5. Understand distributed systems concepts (data sync, orchestration, visualization)

## Architecture Overview

### System Design

The project implements a distributed architecture where:
- **Multiple Raspberry Pis** act as "outposts," each running independent FastAPI servers
- Each Pi has its own SQLite database with thematic data
- A **centralized Streamlit dashboard** (on user's laptop) orchestrates all interactions
- Communication occurs via HTTP REST APIs and SSH

```
User's Laptop (Streamlit Frontend)
         |
         | HTTP REST + SSH
         |
   +-----+-----+-----+
   |     |     |     |
 Pi:   Pi:   Pi:   Pi:
Fishing Hunting Trading ...
 Fort   Fort   Fort
  |      |      |
SQLite SQLite SQLite
  DB     DB     DB
```

### Key Architectural Decisions

1. **Decoupled API Services**: Each Pi hosts isolated APIs with unique data and auth configs
2. **Centralized Dashboard**: Streamlit orchestrates and visualizes all Pi interactions
3. **Authenticated Multi-Endpoint Workflows**: Token-based auth secures API access
4. **Data Synchronization Patterns**: APIs enable stateful data exchanges between nodes

## Technology Stack

### Core Technologies

**Frontend: Streamlit**
- Purpose: Centralized "frontier dashboard" for visualization and interaction
- Why: Rapid development, interactive UI, perfect for educational features
- Learning Resources: https://docs.streamlit.io/

**Backend: FastAPI**
- Purpose: Modern async Python API development on each Raspberry Pi
- Why: Automatic OpenAPI docs, clean syntax, minimal boilerplate
- Learning Resources: https://fastapi.tiangolo.com/tutorial/

**Storage: SQLite**
- Purpose: Lightweight relational storage on each Pi
- Why: No additional setup, perfect for constrained environments
- Learning Resources: https://www.sqlitetutorial.net/

### Special Libraries

- `paramiko`: SSH command execution from Python
- `pandas`: Data manipulation and presentation
- `requests`: API consumption on client side
- `pytest`: Testing and validation

### Environment Requirements

- Python 3.9 or higher
- Virtual environment for dependency isolation
- Local network connectivity between laptop and all Raspberry Pis
- SSH enabled on all Raspberry Pis

## Project Structure

### Expected Directory Organization

```
HudsonBayOutposts/
├── README.md                    # Comprehensive project documentation
├── requirements.txt             # Python dependencies
├── main.py                      # Streamlit app entry point
├── .env                         # Configuration (Pi IPs, credentials, tokens)
├── src/
│   ├── api_client/              # Reusable API client module
│   │   ├── __init__.py
│   │   ├── client.py            # API client with auth support
│   │   └── endpoints.py         # Endpoint abstractions
│   ├── ssh_module/              # Paramiko-based SSH utilities
│   │   ├── __init__.py
│   │   └── executor.py          # Remote command execution
│   ├── models/                  # Data models and schemas
│   │   ├── __init__.py
│   │   ├── outpost.py           # Outpost data models
│   │   └── user.py              # User progress tracking
│   ├── ui/                      # Streamlit UI components
│   │   ├── __init__.py
│   │   ├── navigation.py        # Multi-page navigation
│   │   ├── chapters/            # Chapter-specific UI
│   │   ├── components/          # Reusable UI components
│   │   └── themes.py            # Frontier-themed styling
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── auth.py              # Authentication helpers
│       └── sync.py              # Data synchronization logic
├── raspberry_pi/                # Code deployed to Raspberry Pis
│   ├── api/                     # FastAPI applications
│   │   ├── fishing_fort.py      # Chapter 1 API
│   │   ├── hunting_fort.py      # Chapter 2 API
│   │   ├── trading_fort.py      # Chapter 3 API
│   │   └── auth_middleware.py   # Token-based auth
│   ├── db/                      # Database scripts
│   │   ├── init_db.py           # Database initialization
│   │   └── schemas/             # SQL schemas by fort
│   └── setup/                   # Pi setup scripts
│       └── pi_setup.sh          # Automated environment prep
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   │   ├── test_api_client.py
│   │   ├── test_ssh_module.py
│   │   └── test_endpoints.py
│   └── integration/             # Integration tests
│       └── test_multi_node.py   # Multi-Pi workflow tests
└── docs/                        # Additional documentation
    ├── architecture.md          # Architecture diagrams
    ├── api_reference.md         # API endpoint documentation
    ├── setup_guide.md           # Detailed setup instructions
    └── troubleshooting.md       # Common issues and solutions
```

## Development Phases

The project follows a structured 5-phase implementation plan with 50 total steps:

### Phase 1: Foundations & Environment Setup (Steps 1-10)
- Virtual environment and dependency installation
- SSH configuration for all Raspberry Pis
- Project directory structure and Git initialization
- Data model definition
- SQLite database initialization on each Pi
- Basic FastAPI skeleton
- SSH command execution module with Paramiko
- Streamlit app scaffold with navigation
- User progress tracking with dataclasses
- Documentation of setup procedures

### Phase 2: Core API Development & Basic Integration (Steps 11-20)
- Thematic data schemas for outpost APIs
- GET/POST endpoints for inventory management
- Streamlit components for data fetching and display
- Remote shell command utilities in UI
- Status endpoints for outpost metadata
- File operations and logs retrieval APIs
- File upload/download UI components
- Reusable API client module
- First multi-endpoint workflow combining two Pis
- Updated architecture diagrams

### Phase 3: Feature Expansion & API Authentication (Steps 21-30)
- Token-based authentication in FastAPI
- Authenticated request support in API client
- Chapter 3 API with new thematic datasets
- Authentication UI components and login flow
- Authenticated multi-endpoint workflows
- Data synchronization APIs between Pis
- UI for triggering data sync
- Error handling and retry logic in API client
- Chapter 4 outpost with additional endpoints
- Documentation of auth and multi-node workflows

### Phase 4: Polish, Testing & Optimization (Steps 31-40)
- Unit tests for all FastAPI endpoints
- Integration tests for multi-node workflows
- Comprehensive error handling in Streamlit UI
- Data refresh optimization with caching
- SQLite indexing for performance
- Logging features on Pi APIs
- Progress visualization enhancements
- User acceptance testing
- Bug fixes and performance improvements
- Automated test scripts and CI setup

### Phase 5: Documentation, Examples & Deployment (Steps 41-50)
- Comprehensive user guide for dashboard
- Developer guide for API extension
- Example scripts demonstrating API usage
- Thematic branding and UI styling
- Raspberry Pi setup scripts and configs
- Troubleshooting FAQ
- Video walkthrough
- Distribution packaging
- Final full-system testing
- README finalization

## Key Components

### 1. Streamlit Dashboard (main.py)
- Central control interface running on user's laptop
- Multi-page navigation mimicking learning chapters
- Real-time data visualization from all Pi nodes
- Interactive tools for SSH commands and API calls
- Progress tracking and visual feedback
- Educational tooltips and help sections

### 2. FastAPI Services (raspberry_pi/api/)
- Independent API server on each Raspberry Pi
- Thematic RESTful endpoints (inventory, status, logs, sync)
- SQLite-backed data persistence
- Token-based authentication middleware
- Automatic OpenAPI documentation
- Logging and error handling

### 3. API Client Module (src/api_client/)
- Abstraction layer for API interactions
- Built-in authentication token management
- Error handling with retry logic
- Endpoint-specific methods
- Response validation

### 4. SSH Execution Module (src/ssh_module/)
- Paramiko-based remote command execution
- Secure credential management
- Command output capture and parsing
- Error detection and reporting

### 5. Data Models (src/models/)
- Python dataclasses for outposts and users
- Progress tracking structures
- SQLite schema definitions
- Pydantic models for API validation

### 6. Testing Suite (tests/)
- Unit tests for individual components
- Integration tests for multi-Pi workflows
- Pytest-based test framework
- CI/CD integration ready

## Educational Features

The project emphasizes educational scaffolding throughout:

### Inline Learning Support
- **Tooltips**: Just-in-time explanations for UI elements and code
- **Inline Comments**: Detailed code documentation explaining logic
- **Progressive Disclosure**: Reveals complexity gradually as users advance
- **Interactive Demos**: Safe experimentation environments for SSH and API calls
- **Visual Diagrams**: Architecture, workflow, and API interaction illustrations
- **Contextual Help**: Searchable, categorized guidance throughout the UI

### Teaching Methodologies
- Narrative-driven learning through frontier fort theming
- Hands-on exercises with immediate visual feedback
- Multi-chapter progression building on prior knowledge
- Example scripts with detailed annotations
- Troubleshooting guidance embedded in error messages

## Development Workflow

### Setup Process
1. Create Python virtual environment
2. Install dependencies from requirements.txt
3. Configure SSH access to all Raspberry Pis
4. Initialize SQLite databases on each Pi
5. Deploy FastAPI servers to Pis
6. Configure .env file with Pi IPs and credentials
7. Launch Streamlit app: `streamlit run main.py`

### Testing Workflow
- Run unit tests: `pytest tests/unit/`
- Run integration tests: `pytest tests/integration/`
- Run all tests with coverage: `pytest --cov=src tests/`
- Frequent testing after changes before merging

### Code Quality Standards
- Modular, well-documented code
- Type hints where beneficial
- Comprehensive error handling
- Security-conscious implementation (input validation, auth)
- Avoid common vulnerabilities (XSS, SQL injection, command injection)

### Git Practices
- Clean, descriptive commit messages
- Feature branches for major additions
- Frequent commits during development
- Version control for all code and documentation

## API Design Patterns

### Authentication Flow
1. Client requests token from `/auth/token` endpoint
2. Server validates credentials and returns JWT token
3. Client includes token in `Authorization: Bearer <token>` header
4. Server validates token on protected endpoints
5. Token renewal handled automatically by API client

### Endpoint Conventions
- GET endpoints for data retrieval
- POST endpoints for data creation
- PUT endpoints for updates
- DELETE endpoints for removal
- Consistent JSON response formats
- Proper HTTP status codes

### Multi-Node Workflows
1. Dashboard queries status from all Pis
2. User selects operation involving multiple nodes
3. API client orchestrates sequential or parallel calls
4. Results aggregated and visualized in UI
5. Error handling for partial failures

## Common Tasks

### Adding a New Pi Outpost
1. Define thematic data schema in `raspberry_pi/db/schemas/`
2. Create initialization script for SQLite database
3. Implement FastAPI application in `raspberry_pi/api/`
4. Add unique themed endpoints
5. Update API client with new endpoint methods
6. Create Streamlit UI components for new fort
7. Add chapter navigation in dashboard
8. Write unit and integration tests
9. Update documentation and architecture diagrams

### Implementing a New API Endpoint
1. Define Pydantic model for request/response
2. Create endpoint function in appropriate FastAPI app
3. Add database operations if needed
4. Implement authentication if required
5. Add endpoint to API client module
6. Create or update UI component to consume endpoint
7. Write unit tests for endpoint
8. Update API documentation

### Adding Authentication to an Endpoint
1. Import auth dependency: `from auth_middleware import verify_token`
2. Add dependency to endpoint: `token: str = Depends(verify_token)`
3. Update API client to include token in requests
4. Update UI to handle authentication state
5. Test authenticated access

### Creating a Multi-Pi Workflow
1. Identify required endpoints across Pis
2. Define workflow logic in API client or dedicated module
3. Handle authentication for each Pi if needed
4. Implement error handling and retries
5. Create Streamlit UI to trigger and visualize workflow
6. Write integration tests simulating multi-node interaction

### Debugging Pi Connectivity Issues
1. Verify SSH access: `ssh pi@<pi_ip>`
2. Check FastAPI server status on Pi
3. Verify firewall rules allow HTTP traffic
4. Test API endpoint directly: `curl http://<pi_ip>:8000/endpoint`
5. Check logs on Pi: `tail -f api.log`
6. Verify network connectivity from laptop to Pi

## Security Considerations

### Current Security Scope
- Token-based authentication (simplified for learning)
- Input validation on API endpoints
- Secure SSH key-based authentication
- Environment variables for sensitive data
- Local network only (no internet exposure)

### Explicitly Out of Scope
- OAuth or advanced auth mechanisms
- Comprehensive security hardening
- Production-ready encryption
- Cloud deployment security
- Advanced firewall configurations

### Security Best Practices to Follow
- Never commit credentials to Git
- Use .env files for configuration (gitignored)
- Validate all user inputs
- Sanitize commands for SSH execution
- Use parameterized SQL queries
- Implement rate limiting where appropriate
- Log security-relevant events

## Testing Approach

### Unit Testing
- Test individual functions and methods
- Mock external dependencies (API calls, SSH)
- Focus on business logic and edge cases
- Aim for high code coverage

### Integration Testing
- Test multi-component interactions
- Simulate multi-Pi workflows
- Test authentication flows end-to-end
- Verify data synchronization

### User Acceptance Testing
- Structured testing with real users
- Feedback collection built into UI
- Issue tracking and resolution
- Iterative refinement based on feedback

## Performance Optimization

### Caching Strategies
- Streamlit's `@st.cache_data` for expensive operations
- API response caching where appropriate
- SQLite query result caching

### Database Optimization
- Indexes on frequently queried columns
- Query optimization for complex joins
- Connection pooling if needed

### UI Responsiveness
- Async operations for long-running tasks
- Progress indicators for user feedback
- Lazy loading of data
- Efficient Streamlit component updates

## Troubleshooting Common Issues

### SSH Connection Failures
- Verify SSH is enabled on Pi
- Check network connectivity
- Confirm credentials are correct
- Ensure firewall allows SSH (port 22)

### API Endpoint Not Responding
- Verify FastAPI server is running on Pi
- Check correct IP address and port
- Test with curl or browser first
- Review Pi logs for errors

### Authentication Errors
- Verify token is valid and not expired
- Check token is properly included in headers
- Confirm auth middleware is configured
- Review auth logs

### Data Synchronization Issues
- Check network connectivity between Pis
- Verify sync endpoints are accessible
- Review sync logic for race conditions
- Check database locks or conflicts

### Streamlit UI Not Updating
- Check cache settings
- Verify data fetch logic
- Look for exceptions in console
- Restart Streamlit app if needed

## Documentation Standards

### Code Documentation
- Docstrings for all functions and classes
- Inline comments for complex logic
- Type hints for function signatures
- README in each major directory

### API Documentation
- Automatic OpenAPI docs via FastAPI
- Manual API reference in docs/
- Example requests and responses
- Authentication requirements clearly stated

### User Documentation
- Step-by-step setup guide
- Chapter-by-chapter walkthroughs
- Troubleshooting FAQ
- Video demonstrations

## Success Criteria

### Functional Requirements
- All Pi APIs respond correctly to requests
- Authentication works across all endpoints
- File operations complete successfully
- Data synchronization executes without errors
- Dashboard visualizes all data accurately
- User progress tracked correctly

### Learning Objectives Met
- Users demonstrate SSH proficiency
- Users can design and consume RESTful APIs
- Users understand multi-endpoint workflows
- Users implement authentication correctly
- Users grasp distributed system basics

### Quality Standards
- Code is modular and well-documented
- Unit and integration tests pass
- Error handling is comprehensive
- UI is intuitive and educational
- Performance meets acceptable levels

## Extension Opportunities

After completing the core project, users can explore:

### Advanced Features
- OAuth 2.0 implementation
- WebSocket support for real-time updates
- Advanced distributed algorithms
- Cloud integration (AWS, Azure)
- Container orchestration with Docker/Kubernetes

### Related Projects
- IoT sensor data collection networks
- Distributed task scheduling systems
- API gateway development
- Edge computing applications
- Home automation systems

## Working with Claude

### When Requesting Code Changes
- Specify which phase/step you're working on
- Indicate which Pi or component is affected
- Mention if changes require testing
- Note any educational features to preserve

### When Debugging
- Provide error messages and logs
- Specify which component is failing
- Describe expected vs. actual behavior
- Mention what you've already tried

### When Adding Features
- Explain the educational value
- Specify which chapter/fort it belongs to
- Indicate any dependencies on other features
- Request appropriate tests and documentation

### Best Practices for Claude Interactions
- Reference specific files and line numbers when possible
- Ask for explanations of complex logic
- Request inline comments for learning
- Ask for tests alongside implementation
- Request documentation updates with code changes

## Project Timeline & Effort

- **Total Duration**: 3-4 weeks
- **Complexity**: Medium to medium-high
- **Target Audience**: Intermediate Python developers
- **Prerequisites**: Basic networking, Python fundamentals
- **Time Commitment**: Part-time, progressive learning

## Additional Resources

### Official Documentation Links
- Streamlit: https://docs.streamlit.io/
- FastAPI: https://fastapi.tiangolo.com/tutorial/
- SQLite: https://www.sqlitetutorial.net/
- Paramiko: https://docs.paramiko.org/
- Pytest: https://docs.pytest.org/

### Learning Paths
1. Start with Phase 1 foundations
2. Progress through phases sequentially
3. Complete chapter exercises in order
4. Build on previous knowledge
5. Experiment with extensions after completion

---

## Quick Reference Commands

### Development Commands
```bash
# Activate virtual environment
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run main.py

# Run tests
pytest tests/
pytest tests/unit/
pytest tests/integration/
pytest --cov=src tests/

# SSH to Pi
ssh pi@<pi_ip>

# Deploy to Pi
scp -r raspberry_pi/ pi@<pi_ip>:~/

# Start FastAPI on Pi
uvicorn api.fishing_fort:app --host 0.0.0.0 --port 8000
```

### Git Commands
```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit"

# Feature branch workflow
git checkout -b feature/new-api-endpoint
git add .
git commit -m "Add hunting fort endpoint"
git checkout main
git merge feature/new-api-endpoint
```

### Database Commands (on Pi)
```bash
# Initialize database
python raspberry_pi/db/init_db.py

# Access SQLite database
sqlite3 data/fishing_fort.db
.schema
.tables
SELECT * FROM inventory;
.quit
```

---

## File Naming Conventions

- Python files: `snake_case.py`
- Test files: `test_<module_name>.py`
- Database files: `<fort_name>.db`
- Documentation: `lowercase_with_underscores.md`
- Configuration: `.env`, `config.yml`

## Code Style Guidelines

- Follow PEP 8 for Python code
- Use type hints where beneficial
- Keep functions focused and small
- Document all public APIs
- Use descriptive variable names
- Group imports: standard library, third-party, local
- Maximum line length: 88 characters (Black default)

## Important Notes for AI Assistance

### Context Awareness
- This is an educational project - preserve learning features
- Maintain the frontier/historical theming
- Keep code accessible to intermediate developers
- Prioritize clarity over clever optimizations

### Scope Boundaries
- Focus on local network, not cloud deployment
- Keep security implementations educational, not production-grade
- Avoid over-engineering solutions
- Stay within 3-4 week complexity budget

### Educational Priority
- Include inline comments explaining concepts
- Add tooltips to UI elements
- Provide example usage in documentation
- Think about progressive skill building
- Make error messages educational

---

This document provides comprehensive context for working with the Raspberry Pi Frontier project. Refer to it when making changes, adding features, or helping users understand the codebase.
