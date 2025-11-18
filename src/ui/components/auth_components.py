"""
Authentication UI Components for Streamlit Dashboard

This module provides reusable Streamlit components for authentication flows,
including login forms, user status displays, and authentication management.

Educational Note:
These components demonstrate how to build secure authentication UIs in Streamlit.
They handle login/logout flows, token management, and user session state.

Phase 3 Feature:
Complete authentication integration with visual feedback and error handling.
"""

import streamlit as st
from typing import Optional, Dict, Any, Callable
from src.api_client.client import OutpostAPIClient
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Session State Management
# ============================================================================

def initialize_auth_session_state():
    """
    Initialize authentication-related session state variables.

    Educational Note:
    Streamlit's session state persists data between reruns. This is perfect
    for maintaining authentication state across user interactions.
    """
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if 'auth_token' not in st.session_state:
        st.session_state.auth_token = None

    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

    if 'auth_clients' not in st.session_state:
        # Dictionary to store authenticated clients for each fort
        st.session_state.auth_clients = {}


def is_authenticated() -> bool:
    """
    Check if user is authenticated.

    Returns:
        True if user is authenticated, False otherwise
    """
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[Dict]:
    """
    Get current authenticated user information.

    Returns:
        User dictionary or None if not authenticated
    """
    return st.session_state.get('current_user')


def set_authentication(user_info: Dict, token: str):
    """
    Set authentication state after successful login.

    Args:
        user_info: Dictionary containing user information
        token: Authentication token
    """
    st.session_state.authenticated = True
    st.session_state.current_user = user_info
    st.session_state.auth_token = token
    logger.info(f"User authenticated: {user_info.get('username')}")


def clear_authentication():
    """
    Clear authentication state (logout).

    Educational Note:
    When logging out, we clear all auth-related session state to
    ensure no sensitive data remains in memory.
    """
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.auth_token = None
    st.session_state.auth_clients = {}
    logger.info("User logged out")


# ============================================================================
# Login Components
# ============================================================================

def render_login_form(
    api_url: str,
    on_success: Optional[Callable] = None,
    show_demo_users: bool = True
) -> bool:
    """
    Render a login form for authentication.

    Educational Note:
    This component demonstrates form handling in Streamlit. It:
    1. Collects user credentials
    2. Attempts authentication
    3. Manages session state
    4. Provides visual feedback

    Args:
        api_url: Base URL of the API to authenticate against
        on_success: Optional callback function to run after successful login
        show_demo_users: Whether to show available demo users

    Returns:
        True if login successful, False otherwise

    Example Usage:
        if render_login_form("http://192.168.1.100:8000"):
            st.success("Login successful!")
    """
    st.subheader("🔐 Fort Commander Login")

    # Show demo users if requested
    if show_demo_users:
        with st.expander("📋 Available Demo Users", expanded=False):
            st.info("""
            **Available Demo Accounts:**

            - **fort_commander** / frontier_pass123 (Admin - all forts)
            - **fishing_chief** / fish_pass123 (Manager - fishing fort)
            - **trader** / trade_pass123 (User - trading fort)

            *Educational Note: In production, user lists would NOT be exposed!*
            """)

    # Create login form
    with st.form("login_form"):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            help="Use one of the demo accounts listed above"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Passwords are transmitted securely to the API"
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            submit = st.form_submit_button("🚪 Login", use_container_width=True)

        with col2:
            st.caption("First time? Use a demo account from above")

    # Process login
    if submit:
        if not username or not password:
            st.error("⚠️ Please enter both username and password")
            return False

        # Show progress while authenticating
        with st.spinner("🔄 Authenticating..."):
            try:
                # Create API client and attempt login
                client = OutpostAPIClient(api_url)
                success = client.login(username, password)

                if success:
                    # Get user information
                    user_info = client.get_current_user()

                    if user_info:
                        # Store authentication state
                        set_authentication(user_info, client.token)

                        # Show success message
                        st.success(f"✅ Welcome, {user_info['username']}!")
                        st.balloons()

                        # Run callback if provided
                        if on_success:
                            on_success(user_info)

                        # Trigger rerun to update UI
                        st.rerun()
                        return True
                    else:
                        st.error("❌ Login succeeded but couldn't retrieve user info")
                        return False
                else:
                    st.error("❌ Invalid username or password")
                    return False

            except Exception as e:
                logger.error(f"Login error: {e}")
                st.error(f"❌ Login failed: {str(e)}")
                return False

    return False


def render_compact_login(api_url: str) -> bool:
    """
    Render a compact login form suitable for sidebars.

    Args:
        api_url: Base URL of the API

    Returns:
        True if login successful
    """
    st.markdown("### 🔐 Login")

    username = st.text_input("Username", key="compact_username")
    password = st.text_input("Password", type="password", key="compact_password")

    if st.button("Login", use_container_width=True):
        if username and password:
            with st.spinner("Authenticating..."):
                try:
                    client = OutpostAPIClient(api_url)
                    if client.login(username, password):
                        user_info = client.get_current_user()
                        if user_info:
                            set_authentication(user_info, client.token)
                            st.success("Login successful!")
                            st.rerun()
                            return True
                except Exception as e:
                    st.error(f"Login failed: {e}")

    return False


# ============================================================================
# User Status Components
# ============================================================================

def render_user_status_badge():
    """
    Render a user status badge showing authentication state.

    Educational Note:
    This provides quick visual feedback about authentication status.
    Useful for placing in sidebars or headers.
    """
    if is_authenticated():
        user = get_current_user()
        st.success(f"✅ Logged in as **{user['username']}** ({user['role']})")
    else:
        st.warning("⚠️ Not authenticated")


def render_user_profile_card():
    """
    Render a detailed user profile card.

    Educational Note:
    This shows all available user information in a formatted card.
    Useful for profile pages or settings areas.
    """
    if not is_authenticated():
        st.info("👤 Please log in to view your profile")
        return

    user = get_current_user()

    st.markdown("### 👤 User Profile")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Username", user['username'])
        st.metric("Role", user['role'].capitalize())

    with col2:
        st.metric("Fort Access", user['fort'].capitalize())
        st.metric("Status", "Active" if is_authenticated() else "Inactive")

    # Role badge
    role_colors = {
        'admin': '🔴',
        'manager': '🟡',
        'user': '🟢'
    }
    st.info(f"{role_colors.get(user['role'], '⚪')} **Role Level:** {user['role'].upper()}")


def render_logout_button(
    on_logout: Optional[Callable] = None,
    button_text: str = "🚪 Logout"
):
    """
    Render a logout button.

    Args:
        on_logout: Optional callback to run after logout
        button_text: Custom button text
    """
    if st.button(button_text, use_container_width=True):
        clear_authentication()

        if on_logout:
            on_logout()

        st.success("✅ Logged out successfully")
        st.rerun()


# ============================================================================
# Authentication Guards
# ============================================================================

def require_authentication(
    api_url: str,
    message: str = "This feature requires authentication"
) -> bool:
    """
    Guard function that requires authentication to proceed.

    Educational Note:
    This is a common pattern in web applications - checking authentication
    before allowing access to protected features.

    Args:
        api_url: API URL for login form
        message: Message to show when not authenticated

    Returns:
        True if authenticated, False otherwise

    Example Usage:
        if not require_authentication("http://192.168.1.100:8000"):
            return  # Exit early if not authenticated

        # Protected code here
        st.write("This is only shown to authenticated users")
    """
    if not is_authenticated():
        st.warning(f"🔒 {message}")
        render_login_form(api_url)
        return False

    return True


def require_role(
    required_role: str,
    message: Optional[str] = None
) -> bool:
    """
    Guard function that requires a specific role.

    Args:
        required_role: Required role (e.g., 'admin', 'manager')
        message: Custom error message

    Returns:
        True if user has required role, False otherwise

    Example Usage:
        if not require_role('admin'):
            return  # Exit if not admin

        # Admin-only code here
    """
    if not is_authenticated():
        st.error("🔒 Authentication required")
        return False

    user = get_current_user()
    if user['role'] != required_role:
        default_msg = f"This feature requires {required_role} role"
        st.error(f"⛔ {message or default_msg}")
        st.info(f"Your role: {user['role']}")
        return False

    return True


# ============================================================================
# Authenticated Client Management
# ============================================================================

def get_authenticated_client(fort_name: str, api_url: str) -> Optional[OutpostAPIClient]:
    """
    Get an authenticated API client for a specific fort.

    Educational Note:
    This creates and caches authenticated clients in session state,
    avoiding repeated authentication for the same fort.

    Args:
        fort_name: Name of the fort (e.g., 'fishing', 'trading')
        api_url: Base URL of the fort's API

    Returns:
        Authenticated OutpostAPIClient or None if not authenticated

    Example Usage:
        client = get_authenticated_client('fishing', 'http://192.168.1.100:8000')
        if client:
            inventory = client.get_inventory()
    """
    if not is_authenticated():
        return None

    # Check if we already have a client for this fort
    if fort_name in st.session_state.auth_clients:
        return st.session_state.auth_clients[fort_name]

    # Create new authenticated client
    token = st.session_state.auth_token
    client = OutpostAPIClient(api_url, token=token)

    # Cache it
    st.session_state.auth_clients[fort_name] = client

    return client


# ============================================================================
# Authentication Workflow Components
# ============================================================================

def render_auth_status_sidebar():
    """
    Render authentication status in sidebar with login/logout controls.

    Educational Note:
    This is a complete authentication widget perfect for app sidebars.
    It shows status and provides login/logout functionality in one place.
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔐 Authentication")

        if is_authenticated():
            user = get_current_user()

            st.success(f"✅ **{user['username']}**")
            st.caption(f"Role: {user['role']} | Fort: {user['fort']}")

            if st.button("🚪 Logout", use_container_width=True):
                clear_authentication()
                st.rerun()

        else:
            st.warning("⚠️ Not logged in")
            st.caption("Login to access protected features")

        st.markdown("---")


def render_feature_with_auth(
    api_url: str,
    feature_name: str,
    render_feature: Callable,
    required_role: Optional[str] = None
):
    """
    Render a feature with authentication requirement.

    Educational Note:
    This is a higher-order component that wraps features requiring auth.
    It handles the entire auth flow automatically.

    Args:
        api_url: API URL for authentication
        feature_name: Name of the feature (for messages)
        render_feature: Function that renders the actual feature
        required_role: Optional required role

    Example Usage:
        def my_feature():
            st.write("This is protected content")

        render_feature_with_auth(
            "http://192.168.1.100:8000",
            "Admin Dashboard",
            my_feature,
            required_role='admin'
        )
    """
    if not require_authentication(api_url, f"{feature_name} requires authentication"):
        return

    if required_role and not require_role(required_role, f"{feature_name} requires {required_role} role"):
        return

    # User is authenticated and has required role - render the feature
    render_feature()
