"""
Token-Based Authentication Middleware for Raspberry Pi Outpost APIs

This module provides simplified JWT-based authentication for securing API endpoints.

Educational Note:
Authentication is crucial for protecting API endpoints. This implementation uses
JSON Web Tokens (JWT), a compact and self-contained way to securely transmit
information between parties.

Key Concepts:
- Tokens encode user identity and expiration time
- Clients include tokens in Authorization headers
- Server validates tokens before granting access to protected endpoints

Security Note:
This is an educational implementation suitable for local networks. Production
systems would need additional security measures like HTTPS, refresh tokens,
token revocation, and secure secret management.
"""

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt, JWTError
import secrets
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

# Educational Note: In production, this should be stored securely (env vars, secrets manager)
# For this learning project, we use a generated secret per session
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Tokens valid for 1 hour

# Educational Note: Simple in-memory user store for learning purposes
# In production, this would be a database with hashed passwords
USERS_DB = {
    "fort_commander": {
        "username": "fort_commander",
        "password": "frontier_pass123",  # In production: use hashed passwords!
        "role": "admin",
        "fort": "all"
    },
    "fishing_chief": {
        "username": "fishing_chief",
        "password": "fish_pass123",
        "role": "manager",
        "fort": "fishing"
    },
    "trader": {
        "username": "trader",
        "password": "trade_pass123",
        "role": "user",
        "fort": "trading"
    }
}


# ============================================================================
# Pydantic Models
# ============================================================================

class Token(BaseModel):
    """
    Token response model.

    Educational Note:
    The access_token is a JWT that clients include in subsequent requests.
    The token_type indicates how to use it (Bearer authentication).
    """
    access_token: str
    token_type: str
    expires_in: int  # Seconds until expiration

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class TokenData(BaseModel):
    """Data stored within the JWT token."""
    username: Optional[str] = None
    role: Optional[str] = None
    fort: Optional[str] = None


class LoginRequest(BaseModel):
    """
    Login credentials model.

    Educational Note:
    Clients send username and password to get a token.
    The token is then used for subsequent authenticated requests.
    """
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "fort_commander",
                "password": "frontier_pass123"
            }
        }


class User(BaseModel):
    """User information model."""
    username: str
    role: str
    fort: str


# ============================================================================
# Authentication Functions
# ============================================================================

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Verify user credentials.

    Educational Note:
    This checks if the username exists and password matches.
    In production, passwords would be hashed using bcrypt or similar.

    Args:
        username: The username to authenticate
        password: The password to verify

    Returns:
        User data if authenticated, None otherwise
    """
    user = USERS_DB.get(username)
    if not user:
        logger.warning(f"Authentication failed: User '{username}' not found")
        return None

    # Educational Note: Direct comparison is insecure!
    # Production code should use: bcrypt.checkpw(password.encode(), user['hashed_password'])
    if user["password"] != password:
        logger.warning(f"Authentication failed: Invalid password for user '{username}'")
        return None

    logger.info(f"User '{username}' authenticated successfully")
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a JWT access token.

    Educational Note:
    JWT tokens have three parts:
    1. Header (algorithm and type)
    2. Payload (user data and expiration)
    3. Signature (ensures token hasn't been tampered with)

    Args:
        data: Dictionary of data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add standard JWT claims
    to_encode.update({
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at time
    })

    # Encode and sign the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    logger.info(f"Created access token for user: {data.get('sub')} (expires: {expire})")
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token.

    Educational Note:
    This function:
    1. Validates the token signature
    2. Checks if the token has expired
    3. Extracts and returns the user data

    Args:
        token: JWT token string

    Returns:
        TokenData object with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            logger.warning("Token validation failed: No username in token")
            raise credentials_exception

        # Extract user data
        token_data = TokenData(
            username=username,
            role=payload.get("role"),
            fort=payload.get("fort")
        )

        logger.debug(f"Token validated successfully for user: {username}")
        return token_data

    except JWTError as e:
        error_msg = str(e)
        if "expired" in error_msg.lower():
            logger.warning("Token validation failed: Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.warning(f"Token validation failed: {error_msg}")
        raise credentials_exception


# ============================================================================
# FastAPI Security Dependencies
# ============================================================================

# Educational Note: HTTPBearer automatically extracts tokens from Authorization headers
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    """
    FastAPI dependency to get the current authenticated user.

    Educational Note:
    This is used as a dependency in protected endpoints:

    @app.get("/protected")
    def protected_endpoint(current_user: User = Depends(get_current_user)):
        return {"message": f"Hello {current_user.username}"}

    The dependency:
    1. Extracts the token from the Authorization header
    2. Validates the token
    3. Returns the user information
    4. Raises 401 if authentication fails

    Args:
        credentials: Automatically extracted from Authorization header

    Returns:
        User object with authenticated user data
    """
    token = credentials.credentials
    token_data = verify_token(token)

    # Get user from database
    user = USERS_DB.get(token_data.username)
    if user is None:
        logger.warning(f"User '{token_data.username}' not found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return User(
        username=user["username"],
        role=user["role"],
        fort=user["fort"]
    )


def require_role(required_role: str):
    """
    FastAPI dependency factory to require specific roles.

    Educational Note:
    This creates role-based access control (RBAC).

    Usage:
        @app.get("/admin-only")
        def admin_endpoint(user: User = Depends(require_role("admin"))):
            return {"message": "Admin access granted"}

    Args:
        required_role: The role required to access the endpoint

    Returns:
        Dependency function that checks user role
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            logger.warning(
                f"Access denied: User '{current_user.username}' "
                f"(role: {current_user.role}) requires role: {required_role}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}",
            )
        return current_user

    return role_checker


# ============================================================================
# Helper Functions
# ============================================================================

def get_available_users() -> Dict[str, str]:
    """
    Get list of available demo users.

    Educational Note:
    This helper is useful for demos and testing. It shows what users
    are available without exposing passwords.

    Returns:
        Dictionary mapping usernames to roles
    """
    return {
        username: user["role"]
        for username, user in USERS_DB.items()
    }


def add_auth_routes(app):
    """
    Add authentication routes to a FastAPI app.

    Educational Note:
    This function adds login and user info endpoints to your API.
    Call it in your main app file:

        from auth_middleware import add_auth_routes
        app = FastAPI()
        add_auth_routes(app)

    Args:
        app: FastAPI application instance
    """

    @app.post("/auth/login", response_model=Token, tags=["Authentication"])
    def login(login_request: LoginRequest):
        """
        Authenticate and receive an access token.

        Educational Note:
        This is how the authentication flow works:
        1. Client sends username and password
        2. Server verifies credentials
        3. Server generates a JWT token
        4. Client stores token and includes it in future requests

        The client should include the token in subsequent requests:
            Authorization: Bearer <token>
        """
        # Authenticate user
        user = authenticate_user(login_request.username, login_request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = create_access_token(
            data={
                "sub": user["username"],
                "role": user["role"],
                "fort": user["fort"]
            }
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )


    @app.get("/auth/me", response_model=User, tags=["Authentication"])
    def get_current_user_info(current_user: User = Depends(get_current_user)):
        """
        Get information about the currently authenticated user.

        Educational Note:
        This endpoint demonstrates using the authentication dependency.
        It's useful for clients to verify their token is still valid
        and get user information.
        """
        return current_user


    @app.get("/auth/users", tags=["Authentication"])
    def list_available_users():
        """
        Get list of available demo users (for educational purposes).

        Educational Note:
        This endpoint helps learners by showing what demo users exist.
        In a production system, you wouldn't expose this information!
        """
        return {
            "users": get_available_users(),
            "note": "This is for educational purposes. Production APIs would not expose user lists!"
        }
