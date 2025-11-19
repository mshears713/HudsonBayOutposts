"""
Comprehensive Error Handling Components for Streamlit UI

This module provides robust error handling utilities for the Streamlit dashboard,
including error display, recovery suggestions, logging, and user-friendly messaging.

Educational Note:
Proper error handling is crucial for user experience. This module demonstrates:
- Graceful error display without technical details overwhelming users
- Actionable recovery suggestions
- Error logging for debugging
- Categorized error types for appropriate handling
- User-friendly messaging

Phase 4 Feature (Step 33):
Complete error handling system with recovery suggestions and logging.
"""

import streamlit as st
import logging
import traceback
from typing import Optional, Callable, Any, Dict
from datetime import datetime
from functools import wraps
import sys

logger = logging.getLogger(__name__)


# ============================================================================
# Error Categories
# ============================================================================

class ErrorCategory:
    """
    Categorize errors for appropriate handling.

    Educational Note:
    Different error types need different handling approaches.
    Network errors should suggest retrying, authentication errors
    should prompt login, etc.
    """
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    VALIDATION = "validation"
    DATABASE = "database"
    UNKNOWN = "unknown"


# ============================================================================
# Error Detection and Classification
# ============================================================================

def classify_error(exception: Exception) -> str:
    """
    Classify an exception into an error category.

    Educational Note:
    Classifying errors helps provide relevant recovery suggestions.
    We inspect the exception type and message to determine the category.

    Args:
        exception: The exception to classify

    Returns:
        Error category string
    """
    error_msg = str(exception).lower()
    exception_type = type(exception).__name__.lower()

    # Network errors
    if any(keyword in error_msg for keyword in [
        'connection', 'timeout', 'network', 'unreachable', 'refused'
    ]) or 'connection' in exception_type:
        return ErrorCategory.NETWORK

    # Authentication errors
    if any(keyword in error_msg for keyword in [
        'auth', 'token', 'login', 'credential', 'unauthorized', '401'
    ]):
        return ErrorCategory.AUTHENTICATION

    # Permission errors
    if any(keyword in error_msg for keyword in [
        'permission', 'forbidden', 'access denied', '403'
    ]):
        return ErrorCategory.PERMISSION

    # Validation errors
    if any(keyword in error_msg for keyword in [
        'validation', 'invalid', 'required', 'format', '422'
    ]):
        return ErrorCategory.VALIDATION

    # Database errors
    if any(keyword in error_msg for keyword in [
        'database', 'sqlite', 'sql', 'query'
    ]) or 'database' in exception_type:
        return ErrorCategory.DATABASE

    return ErrorCategory.UNKNOWN


def get_error_recovery_suggestions(category: str, exception: Exception) -> list:
    """
    Get user-friendly recovery suggestions based on error category.

    Educational Note:
    Users need actionable guidance, not just error messages.
    These suggestions help users fix problems themselves.

    Args:
        category: Error category
        exception: The exception that occurred

    Returns:
        List of recovery suggestion strings
    """
    suggestions = {
        ErrorCategory.NETWORK: [
            "Check your network connection",
            "Verify the API server is running",
            "Ensure the API URL is correct",
            "Try refreshing the page",
            "Contact your administrator if the problem persists"
        ],
        ErrorCategory.AUTHENTICATION: [
            "Try logging in again",
            "Check your username and password",
            "Your session may have expired - please re-authenticate",
            "Clear your browser cache and try again"
        ],
        ErrorCategory.PERMISSION: [
            "You may not have permission for this action",
            "Try logging in with an administrator account",
            "Contact your administrator to request access",
            "Check that your user role has the required permissions"
        ],
        ErrorCategory.VALIDATION: [
            "Check that all required fields are filled",
            "Verify your input format is correct",
            "Review the field requirements and try again",
            "See the API documentation for expected formats"
        ],
        ErrorCategory.DATABASE: [
            "The database may be unavailable",
            "Try again in a few moments",
            "Contact your administrator if the issue persists",
            "Check database logs for more details"
        ],
        ErrorCategory.UNKNOWN: [
            "An unexpected error occurred",
            "Try refreshing the page",
            "If the problem persists, contact support",
            "Check the browser console for more details"
        ]
    }

    return suggestions.get(category, suggestions[ErrorCategory.UNKNOWN])


# ============================================================================
# Error Display Components
# ============================================================================

def display_error(
    error: Exception,
    title: str = "Error",
    show_details: bool = False,
    show_recovery: bool = True
):
    """
    Display an error message with optional details and recovery suggestions.

    Educational Note:
    This provides a consistent, user-friendly error display across the app.
    Technical details are hidden by default but available via expander.

    Args:
        error: The exception to display
        title: Error title/header
        show_details: Whether to show technical details by default
        show_recovery: Whether to show recovery suggestions
    """
    # Classify the error
    category = classify_error(error)

    # Display error message
    st.error(f"**{title}**")
    st.write(str(error))

    # Show recovery suggestions
    if show_recovery:
        suggestions = get_error_recovery_suggestions(category, error)

        with st.expander("=¡ How to fix this", expanded=True):
            st.write("**Try these steps:**")
            for i, suggestion in enumerate(suggestions, 1):
                st.write(f"{i}. {suggestion}")

    # Technical details (collapsed by default)
    if show_details or st.session_state.get('show_technical_details', False):
        with st.expander("=' Technical Details", expanded=False):
            st.code(traceback.format_exc())

            # Error metadata
            st.write("**Error Metadata:**")
            st.json({
                "type": type(error).__name__,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "message": str(error)
            })


def display_warning(
    message: str,
    title: str = "Warning",
    details: Optional[str] = None
):
    """
    Display a warning message.

    Educational Note:
    Warnings inform users of potential issues without blocking functionality.

    Args:
        message: Warning message
        title: Warning title
        details: Optional additional details
    """
    st.warning(f"**{title}**")
    st.write(message)

    if details:
        with st.expander("More details"):
            st.write(details)


def display_info(
    message: str,
    title: Optional[str] = None,
    icon: str = "9"
):
    """
    Display an informational message.

    Args:
        message: Info message
        title: Optional title
        icon: Icon to display
    """
    if title:
        st.info(f"{icon} **{title}**\n\n{message}")
    else:
        st.info(f"{icon} {message}")


# ============================================================================
# Error Handling Decorators
# ============================================================================

def handle_errors(
    error_title: str = "Operation Failed",
    show_recovery: bool = True,
    log_errors: bool = True,
    return_value_on_error: Any = None
):
    """
    Decorator to handle errors in Streamlit functions.

    Educational Note:
    Decorators provide reusable error handling across functions.
    This prevents code duplication and ensures consistent error handling.

    Args:
        error_title: Title for error display
        show_recovery: Whether to show recovery suggestions
        log_errors: Whether to log errors
        return_value_on_error: Value to return if error occurs

    Example:
        @handle_errors(error_title="Failed to load data")
        def load_fort_data():
            return client.get_inventory()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error
                if log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}",
                        exc_info=True
                    )

                # Display error to user
                display_error(
                    e,
                    title=error_title,
                    show_recovery=show_recovery
                )

                return return_value_on_error

        return wrapper
    return decorator


def safe_api_call(
    error_message: str = "API call failed",
    default_value: Any = None
):
    """
    Decorator specifically for API calls with retry information.

    Educational Note:
    API calls are common failure points. This decorator provides
    specialized handling with network-specific guidance.

    Args:
        error_message: Custom error message
        default_value: Value to return on error

    Example:
        @safe_api_call(error_message="Failed to fetch inventory")
        def get_inventory():
            return client.get_inventory()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # Check if result is None (API returned None)
                if result is None:
                    st.warning(
                        f"{error_message}. The API returned no data. "
                        "This might indicate a connection issue or empty result."
                    )
                    return default_value

                return result

            except Exception as e:
                category = classify_error(e)

                if category == ErrorCategory.NETWORK:
                    st.error(f"**Network Error: {error_message}**")
                    st.write(str(e))

                    with st.expander("=¡ Network Troubleshooting", expanded=True):
                        st.write("**Check these items:**")
                        st.write("1. Is the API server running?")
                        st.write("2. Can you ping the server?")
                        st.write("3. Is the URL correct?")
                        st.write("4. Are there firewall rules blocking access?")
                        st.write("5. Check API server logs for errors")
                else:
                    display_error(e, title=error_message)

                logger.error(f"API call failed in {func.__name__}: {str(e)}")
                return default_value

        return wrapper
    return decorator


# ============================================================================
# Error Logging Configuration
# ============================================================================

def initialize_error_logging(
    log_file: str = "logs/streamlit_errors.log",
    log_level: int = logging.ERROR
):
    """
    Initialize error logging for the Streamlit app.

    Educational Note:
    Logging captures errors for later analysis. File logs persist
    across sessions and help debug production issues.

    Args:
        log_file: Path to log file
        log_level: Logging level
    """
    import os

    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger.info("Error logging initialized")


# ============================================================================
# Error Recovery Components
# ============================================================================

def render_retry_button(
    callback: Callable,
    button_text: str = "= Retry",
    key: Optional[str] = None
):
    """
    Render a retry button for failed operations.

    Educational Note:
    Giving users a retry button provides immediate recovery option
    without requiring page refresh.

    Args:
        callback: Function to call on retry
        button_text: Button label
        key: Streamlit button key
    """
    if st.button(button_text, key=key):
        with st.spinner("Retrying..."):
            try:
                result = callback()
                st.success(" Operation succeeded!")
                return result
            except Exception as e:
                display_error(e, title="Retry failed")
                return None


def render_error_summary():
    """
    Render a summary of errors that occurred in the session.

    Educational Note:
    Tracking errors in session state helps users and developers
    understand patterns and recurring issues.
    """
    if 'error_log' not in st.session_state:
        st.session_state.error_log = []

    if st.session_state.error_log:
        with st.expander(f"  Session Errors ({len(st.session_state.error_log)})"):
            for i, error_entry in enumerate(reversed(st.session_state.error_log[-10:]), 1):
                st.write(f"**{i}. {error_entry['timestamp']}**")
                st.write(f"   {error_entry['message']}")
                st.write(f"   Category: {error_entry['category']}")
                st.divider()


def log_error_to_session(error: Exception, context: str = ""):
    """
    Log error to session state for summary display.

    Args:
        error: Exception that occurred
        context: Context where error occurred
    """
    if 'error_log' not in st.session_state:
        st.session_state.error_log = []

    st.session_state.error_log.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'message': str(error),
        'type': type(error).__name__,
        'category': classify_error(error),
        'context': context
    })

    # Keep only last 50 errors
    st.session_state.error_log = st.session_state.error_log[-50:]


# ============================================================================
# User Feedback Components
# ============================================================================

def render_feedback_form():
    """
    Render a feedback form for users to report issues.

    Educational Note:
    User feedback helps identify issues and improve the application.
    This provides a structured way to collect error reports.
    """
    with st.expander("=Ý Report an Issue"):
        st.write("Help us improve by reporting issues you encounter.")

        issue_type = st.selectbox(
            "Issue Type",
            ["Bug", "Feature Request", "Performance Issue", "Other"]
        )

        description = st.text_area(
            "Description",
            placeholder="Describe the issue you encountered..."
        )

        steps_to_reproduce = st.text_area(
            "Steps to Reproduce (optional)",
            placeholder="1. Go to...\n2. Click on...\n3. See error"
        )

        if st.button("Submit Feedback"):
            if description:
                # In production, this would send to a tracking system
                feedback_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'type': issue_type,
                    'description': description,
                    'steps': steps_to_reproduce,
                    'session_errors': st.session_state.get('error_log', [])[-5:]
                }

                logger.info(f"User feedback submitted: {feedback_entry}")

                st.success(" Thank you for your feedback!")
                st.info("In production, this would be sent to the development team.")
            else:
                st.warning("Please provide a description.")


# ============================================================================
# Context Managers
# ============================================================================

class error_handler:
    """
    Context manager for error handling in code blocks.

    Educational Note:
    Context managers provide clean error handling for code blocks
    without needing decorators.

    Example:
        with error_handler("Loading data"):
            data = load_expensive_data()
    """

    def __init__(
        self,
        operation_name: str,
        show_recovery: bool = True,
        suppress: bool = False
    ):
        self.operation_name = operation_name
        self.show_recovery = show_recovery
        self.suppress = suppress

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(
                f"Error during '{self.operation_name}': {exc_val}",
                exc_info=True
            )

            display_error(
                exc_val,
                title=f"Error: {self.operation_name}",
                show_recovery=self.show_recovery
            )

            log_error_to_session(exc_val, self.operation_name)

            # Suppress the exception if requested
            return self.suppress

        return False
