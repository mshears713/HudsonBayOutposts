# Testing Guide for Raspberry Pi Frontier

This directory contains comprehensive test suites for the Raspberry Pi Frontier project.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_fishing_fort_api.py      # Fishing Fort API endpoints
│   ├── test_trading_fort_api.py      # Trading Fort API endpoints
│   └── test_auth_middleware.py       # Authentication system
├── integration/             # Integration tests for multi-component workflows
│   └── test_multi_node_workflows.py  # Multi-Pi distributed workflows
└── README.md               # This file
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests for a specific file
pytest tests/unit/test_fishing_fort_api.py
```

### Run Tests with Coverage

```bash
# Generate coverage report
pytest --cov=src --cov=raspberry_pi --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Tests with Verbose Output

```bash
pytest -v  # Verbose mode
pytest -vv # Extra verbose mode
pytest -s  # Show print statements
```

### Run Specific Test Functions

```bash
# Run a specific test
pytest tests/unit/test_fishing_fort_api.py::test_root_endpoint

# Run tests matching a pattern
pytest -k "test_auth"
pytest -k "test_inventory"
```

## Test Markers

Tests can be marked with custom markers for categorization:

```bash
# Run only API tests
pytest -m api

# Run only auth tests
pytest -m auth

# Run integration tests
pytest -m integration

# Run all except slow tests
pytest -m "not slow"
```

## Educational Notes

### Unit Tests

**Purpose:** Test individual components in isolation

**Key Concepts:**
- **Mocking:** Replace external dependencies (databases, APIs) with controlled test doubles
- **Fixtures:** Reusable test data and setup code
- **Parametrization:** Test multiple scenarios with the same test logic
- **Assertions:** Verify expected behavior and outcomes

**Example:**
```python
def test_get_inventory_item(mock_db, sample_item):
    """Test retrieving a specific inventory item."""
    # Arrange: Setup test data
    mock_db.return_value = sample_item

    # Act: Execute the code being tested
    response = client.get("/inventory/1")

    # Assert: Verify expected results
    assert response.status_code == 200
    assert response.json()["name"] == sample_item["name"]
```

### Integration Tests

**Purpose:** Test multiple components working together

**Key Concepts:**
- **Multi-component interactions:** APIs working with other APIs
- **Workflow testing:** Complete user scenarios from start to finish
- **Distributed systems:** Multiple nodes communicating
- **Error handling:** Graceful handling of failures across components

**Example:**
```python
def test_sync_workflow(fishing_client, trading_client):
    """Test data synchronization between two forts."""
    # Export from fishing fort
    export_data = fishing_client.post("/sync/export")

    # Import to trading fort
    import_result = trading_client.post("/sync/import", json=export_data.json())

    # Verify sync completed
    assert import_result.json()["status"] == "success"
```

## Test Design Principles

### 1. Independence

Each test should be independent and not rely on other tests:

```python
# Good - independent
def test_create_item():
    item = create_item({"name": "Test"})
    assert item["name"] == "Test"

# Bad - depends on other test
def test_update_item():
    # Assumes test_create_item ran first
    item = get_item(1)  # May not exist!
```

### 2. Clarity

Test names should clearly describe what they test:

```python
# Good - clear purpose
def test_authentication_fails_with_invalid_password()

# Bad - unclear
def test_auth()
```

### 3. Coverage

Aim to test:
- **Happy paths:** Normal, expected usage
- **Edge cases:** Boundary conditions, empty inputs, large inputs
- **Error cases:** Invalid inputs, failures, exceptions

### 4. Isolation

Use mocking to isolate code from external dependencies:

```python
@patch('app.database.get_connection')
def test_with_mocked_database(mock_db):
    """Test isolated from actual database."""
    mock_db.return_value = MockConnection()
    # Test code here
```

## Common Testing Patterns

### Testing API Endpoints

```python
def test_api_endpoint():
    response = client.get("/endpoint")
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

### Testing Authentication

```python
def test_protected_endpoint(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200
```

### Testing Error Handling

```python
def test_handles_database_error(mock_db):
    mock_db.side_effect = Exception("DB Error")
    response = client.get("/endpoint")
    assert response.status_code == 500
```

### Parametrized Testing

```python
@pytest.mark.parametrize("input,expected", [
    (5, 10),
    (10, 20),
    (0, 0),
])
def test_double_function(input, expected):
    assert double(input) == expected
```

## Test Coverage Goals

- **Unit Tests:** Aim for 80%+ code coverage
- **Integration Tests:** Cover all major workflows
- **API Endpoints:** Test all endpoints with various scenarios
- **Authentication:** Test all auth flows and edge cases
- **Error Handling:** Test all error paths

## Continuous Integration

Tests should run automatically on:
- Every commit (pre-commit hooks)
- Pull requests
- Main branch merges

See `pytest.ini` for CI configuration.

## Troubleshooting

### Tests Fail with Import Errors

Ensure you're in the project root and the virtual environment is activated:

```bash
cd /path/to/HudsonBayOutposts
source env/bin/activate  # or env\Scripts\activate on Windows
pip install -e .
```

### Tests Pass Locally But Fail in CI

Check for:
- Hard-coded paths
- Timezone dependencies
- Order-dependent tests
- Missing test dependencies

### Mocking Issues

If mocks aren't working:
1. Verify the patch path matches the import path in the code
2. Ensure mock is applied before the function is called
3. Check mock return values match expected types

## Best Practices

1. **Write tests first:** Consider TDD (Test-Driven Development)
2. **Keep tests fast:** Use mocking to avoid slow I/O
3. **One assertion per test:** Focus each test on one behavior
4. **Use descriptive names:** Test names document expected behavior
5. **Clean up after tests:** Reset state, close connections
6. **Document complex tests:** Add comments explaining non-obvious logic
7. **Review test failures:** Failed tests often reveal bugs
8. **Update tests with code:** Keep tests synchronized with implementation

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://docs.pytest.org/en/latest/goodpractices.html)
- [Mocking Guide](https://docs.python.org/3/library/unittest.mock.html)

## Contributing

When adding new features:
1. Write unit tests for new functions/methods
2. Write integration tests for new workflows
3. Ensure all tests pass before committing
4. Aim for high test coverage on new code

## Questions?

Refer to inline test documentation and comments for detailed explanations of testing patterns and strategies used in this project.
