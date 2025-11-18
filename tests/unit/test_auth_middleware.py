"""
Unit Tests for Authentication Middleware

Educational Note:
Authentication is a critical security component. These tests verify:
- Token generation and validation
- User authentication flow
- Access control and authorization
- Token expiration handling
- Error cases and edge conditions

Security Testing Best Practices:
- Test both valid and invalid credentials
- Verify token expiration
- Test authorization (role-based access)
- Ensure proper error messages don't leak sensitive info

To run these tests:
    pytest tests/unit/test_auth_middleware.py -v
"""

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from datetime import datetime, timedelta
from jose import jwt
import time

from raspberry_pi.api.auth_middleware import (
    authenticate_user,
    create_access_token,
    verify_token,
    get_current_user,
    require_role,
    add_auth_routes,
    Token,
    TokenData,
    User,
    LoginRequest,
    SECRET_KEY,
    ALGORITHM,
    USERS_DB
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def test_app():
    """
    Create a test FastAPI app with authentication routes.

    Educational Note:
    We create a fresh app for testing to ensure test isolation
    and avoid side effects between tests.
    """
    app = FastAPI()
    add_auth_routes(app)

    # Add a protected test endpoint
    @app.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        return {"message": f"Hello {current_user.username}"}

    # Add a role-protected endpoint
    @app.get("/admin-only")
    def admin_route(current_user: User = Depends(require_role("admin"))):
        return {"message": "Admin access granted"}

    return app


@pytest.fixture
def client(test_app):
    """Create a test client."""
    return TestClient(test_app)


@pytest.fixture
def valid_credentials():
    """Valid user credentials for testing."""
    return {
        "username": "fort_commander",
        "password": "frontier_pass123"
    }


@pytest.fixture
def invalid_credentials():
    """Invalid credentials for testing."""
    return {
        "username": "nonexistent",
        "password": "wrongpass"
    }


@pytest.fixture
def valid_token():
    """Generate a valid authentication token."""
    return create_access_token(
        data={
            "sub": "fort_commander",
            "role": "admin",
            "fort": "all"
        }
    )


# ============================================================================
# User Authentication Tests
# ============================================================================

def test_authenticate_user_valid_credentials(valid_credentials):
    """
    Test authentication with valid credentials.

    Educational Note:
    This verifies the authentication function correctly validates
    users and returns user data when credentials match.
    """
    user = authenticate_user(
        username=valid_credentials["username"],
        password=valid_credentials["password"]
    )

    assert user is not None
    assert user["username"] == "fort_commander"
    assert user["role"] == "admin"
    assert user["fort"] == "all"


def test_authenticate_user_invalid_username():
    """
    Test authentication fails with invalid username.

    Educational Note:
    Security best practice: Don't reveal whether username or password
    was wrong - just that authentication failed.
    """
    user = authenticate_user(username="nonexistent", password="anypass")

    assert user is None


def test_authenticate_user_invalid_password():
    """Test authentication fails with wrong password."""
    user = authenticate_user(username="fort_commander", password="wrongpass")

    assert user is None


def test_authenticate_user_empty_credentials():
    """Test authentication fails with empty credentials."""
    user = authenticate_user(username="", password="")

    assert user is None


@pytest.mark.parametrize("username,password,expected_role", [
    ("fort_commander", "frontier_pass123", "admin"),
    ("fishing_chief", "fish_pass123", "manager"),
    ("trader", "trade_pass123", "user"),
])
def test_authenticate_different_users(username, password, expected_role):
    """
    Test authentication for all demo users.

    Educational Note:
    Parametrized tests verify all user types work correctly,
    ensuring comprehensive coverage.
    """
    user = authenticate_user(username=username, password=password)

    assert user is not None
    assert user["role"] == expected_role


# ============================================================================
# Token Generation Tests
# ============================================================================

def test_create_access_token():
    """
    Test JWT token creation.

    Educational Note:
    Tokens should contain user data and expiration info.
    They're signed to prevent tampering.
    """
    data = {
        "sub": "test_user",
        "role": "user",
        "fort": "fishing"
    }

    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    # Verify token can be decoded
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "test_user"
    assert payload["role"] == "user"
    assert "exp" in payload  # Expiration timestamp
    assert "iat" in payload  # Issued at timestamp


def test_create_access_token_with_custom_expiration():
    """
    Test token creation with custom expiration time.

    Educational Note:
    Different use cases may need different token lifetimes.
    Short-lived tokens are more secure but less convenient.
    """
    data = {"sub": "test_user"}
    expires_delta = timedelta(minutes=15)

    token = create_access_token(data, expires_delta=expires_delta)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    # Verify expiration is approximately 15 minutes from now
    exp_time = datetime.utcfromtimestamp(payload["exp"])
    expected_exp = datetime.utcnow() + expires_delta

    # Allow 5 second margin for test execution time
    time_diff = abs((exp_time - expected_exp).total_seconds())
    assert time_diff < 5


def test_token_contains_issued_at_time():
    """
    Test that tokens include issued-at timestamp.

    Educational Note:
    The 'iat' (issued at) claim helps with token tracking
    and debugging authentication issues.
    """
    token = create_access_token({"sub": "user"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert "iat" in payload

    # Verify it's recent (within last 5 seconds)
    iat_time = datetime.utcfromtimestamp(payload["iat"])
    time_diff = (datetime.utcnow() - iat_time).total_seconds()
    assert time_diff < 5


# ============================================================================
# Token Verification Tests
# ============================================================================

def test_verify_valid_token(valid_token):
    """
    Test verification of a valid token.

    Educational Note:
    Token verification ensures the token:
    1. Has a valid signature (not tampered)
    2. Hasn't expired
    3. Contains required claims
    """
    token_data = verify_token(valid_token)

    assert isinstance(token_data, TokenData)
    assert token_data.username == "fort_commander"
    assert token_data.role == "admin"
    assert token_data.fort == "all"


def test_verify_expired_token():
    """
    Test that expired tokens are rejected.

    Educational Note:
    Token expiration is a key security feature. Old tokens
    should not grant access even if otherwise valid.
    """
    # Create an already-expired token
    expired_token = create_access_token(
        data={"sub": "test_user"},
        expires_delta=timedelta(seconds=-1)  # Already expired
    )

    # Give it a moment to definitely be expired
    time.sleep(1)

    with pytest.raises(HTTPException) as exc_info:
        verify_token(expired_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "expired" in exc_info.value.detail.lower()


def test_verify_tampered_token(valid_token):
    """
    Test that tampered tokens are rejected.

    Educational Note:
    JWT signatures prevent tampering. Modifying any part
    of the token invalidates the signature.
    """
    # Tamper with the token by modifying it
    tampered_token = valid_token[:-10] + "tampered!!"

    with pytest.raises(HTTPException) as exc_info:
        verify_token(tampered_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_verify_malformed_token():
    """Test that malformed tokens are rejected."""
    malformed_token = "not.a.valid.jwt.token"

    with pytest.raises(HTTPException) as exc_info:
        verify_token(malformed_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_verify_token_without_username():
    """
    Test that tokens without username are rejected.

    Educational Note:
    The 'sub' (subject) claim should contain the username.
    Tokens without it are invalid for our system.
    """
    # Create token without 'sub' field
    data = {"role": "admin"}  # Missing 'sub'
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        verify_token(token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Login Endpoint Tests
# ============================================================================

def test_login_with_valid_credentials(client, valid_credentials):
    """
    Test login endpoint with valid credentials.

    Educational Note:
    Successful login should return:
    1. Access token
    2. Token type (Bearer)
    3. Expiration time
    """
    response = client.post("/auth/login", json=valid_credentials)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "token_type" in data
    assert "expires_in" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_with_invalid_credentials(client, invalid_credentials):
    """
    Test login fails with invalid credentials.

    Educational Note:
    Failed logins should return 401 Unauthorized with
    generic error message (don't reveal if username or password was wrong).
    """
    response = client.post("/auth/login", json=invalid_credentials)

    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_with_wrong_password(client):
    """Test login fails with correct username but wrong password."""
    credentials = {
        "username": "fort_commander",
        "password": "wrongpassword"
    }

    response = client.post("/auth/login", json=credentials)

    assert response.status_code == 401


def test_login_returns_valid_token(client, valid_credentials):
    """
    Test that login returns a token that can be verified.

    Educational Note:
    The returned token should be immediately usable
    for authenticated requests.
    """
    response = client.post("/auth/login", json=valid_credentials)
    token = response.json()["access_token"]

    # Verify the token works
    token_data = verify_token(token)
    assert token_data.username == valid_credentials["username"]


# ============================================================================
# Protected Endpoint Tests
# ============================================================================

def test_protected_endpoint_with_valid_token(client, valid_token):
    """
    Test accessing protected endpoint with valid token.

    Educational Note:
    Protected endpoints require the Authorization header:
    Authorization: Bearer <token>
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.get("/protected", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_protected_endpoint_without_token(client):
    """
    Test accessing protected endpoint without token.

    Educational Note:
    Requests without authentication should be rejected
    with 403 Forbidden.
    """
    response = client.get("/protected")

    assert response.status_code == 403


def test_protected_endpoint_with_invalid_token(client):
    """Test protected endpoint rejects invalid tokens."""
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.get("/protected", headers=headers)

    assert response.status_code == 401


def test_protected_endpoint_with_expired_token(client):
    """Test protected endpoint rejects expired tokens."""
    expired_token = create_access_token(
        data={"sub": "test_user"},
        expires_delta=timedelta(seconds=-1)
    )

    time.sleep(1)

    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/protected", headers=headers)

    assert response.status_code == 401


# ============================================================================
# Current User Endpoint Tests
# ============================================================================

def test_get_current_user_info(client, valid_token):
    """
    Test retrieving current user information.

    Educational Note:
    The /auth/me endpoint lets clients verify their token
    and get user details without making a separate request.
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "fort_commander"
    assert data["role"] == "admin"
    assert data["fort"] == "all"


def test_get_current_user_without_auth(client):
    """Test /auth/me requires authentication."""
    response = client.get("/auth/me")

    assert response.status_code == 403


# ============================================================================
# Role-Based Access Control Tests
# ============================================================================

def test_admin_endpoint_with_admin_token(client, valid_token):
    """
    Test admin-only endpoint with admin user.

    Educational Note:
    Role-based access control (RBAC) restricts endpoints
    to users with specific roles.
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.get("/admin-only", headers=headers)

    assert response.status_code == 200


def test_admin_endpoint_with_non_admin_token(client):
    """
    Test admin-only endpoint rejects non-admin users.

    Educational Note:
    Even with valid authentication, users lacking the
    required role should be denied access (403 Forbidden).
    """
    # Create token for non-admin user
    user_token = create_access_token(
        data={
            "sub": "trader",
            "role": "user",
            "fort": "trading"
        }
    )

    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/admin-only", headers=headers)

    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


@pytest.mark.parametrize("username,role,expected_status", [
    ("fort_commander", "admin", 200),  # Admin - should succeed
    ("fishing_chief", "manager", 403),  # Manager - should fail
    ("trader", "user", 403),  # User - should fail
])
def test_admin_endpoint_role_enforcement(client, username, role, expected_status):
    """
    Test admin endpoint enforces role requirements.

    Educational Note:
    This parameterized test verifies RBAC works correctly
    for all user roles in the system.
    """
    token = create_access_token(
        data={
            "sub": username,
            "role": role,
            "fort": "all"
        }
    )

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/admin-only", headers=headers)

    assert response.status_code == expected_status


# ============================================================================
# Available Users Endpoint Tests
# ============================================================================

def test_list_available_users(client):
    """
    Test listing available demo users.

    Educational Note:
    This endpoint helps learners discover demo users.
    In production, you would never expose user lists!
    """
    response = client.get("/auth/users")

    assert response.status_code == 200
    data = response.json()

    assert "users" in data
    assert "note" in data
    assert "fort_commander" in data["users"]
    assert data["users"]["fort_commander"] == "admin"


# ============================================================================
# Security Best Practices Tests
# ============================================================================

def test_token_secret_key_is_secure():
    """
    Test that secret key is sufficiently long.

    Educational Note:
    Short secret keys are vulnerable to brute force attacks.
    Keys should be at least 256 bits (32 bytes) for HS256.
    """
    assert len(SECRET_KEY) >= 32


def test_password_not_in_token(valid_credentials, valid_token):
    """
    Test that passwords are never included in tokens.

    Educational Note:
    Tokens should only contain necessary user info,
    never sensitive data like passwords!
    """
    payload = jwt.decode(valid_token, SECRET_KEY, algorithms=[ALGORITHM])

    # Ensure no password-related fields
    assert "password" not in payload
    assert "pwd" not in payload
    assert "pass" not in payload


def test_error_messages_dont_leak_info(client):
    """
    Test that error messages don't leak sensitive information.

    Educational Note:
    Error messages should be helpful but not reveal system
    internals or help attackers probe the system.
    """
    # Test with invalid username
    response = client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "anypass"
    })

    error_detail = response.json()["detail"]

    # Should NOT say "username not found" or similar
    # Should be generic: "Incorrect username or password"
    assert "Incorrect username or password" in error_detail
    assert "not found" not in error_detail.lower()


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

def test_authentication_with_special_characters():
    """
    Test authentication handles special characters.

    Educational Note:
    User inputs may contain special characters.
    The system should handle them safely.
    """
    user = authenticate_user(
        username="user@#$%",
        password="pass!@#$"
    )

    # Should return None (invalid user) not crash
    assert user is None


def test_token_verification_with_none():
    """Test token verification handles None gracefully."""
    with pytest.raises(Exception):  # Should raise some exception, not crash
        verify_token(None)


def test_token_verification_with_empty_string():
    """Test token verification handles empty string."""
    with pytest.raises(HTTPException):
        verify_token("")


def test_login_with_missing_fields(client):
    """
    Test login with missing required fields.

    Educational Note:
    Pydantic validation should catch missing fields
    before they reach the authentication logic.
    """
    response = client.post("/auth/login", json={"username": "test"})
    # Missing password field

    assert response.status_code == 422  # Validation error
