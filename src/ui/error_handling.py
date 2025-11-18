"""
Comprehensive Error Handling for Streamlit UI

Educational Note:
Robust error handling improves user experience by:
1. Providing clear, actionable error messages
2. Preventing app crashes from external failures
3. Logging errors for debugging
4. Offering recovery options (retry, fallbacks)
5. Maintaining app state during errors

This module provides:
- Custom exception classes
- Error display components
- Retry mechanisms
- Error logging
- User-friendly error messages
"""

import streamlit as st
import logging
import traceback
import functools
import time
from typing import Callable, Any, Optional, Dict, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import requests


# ============================================================================
# Error Categories
# ============================================================================

class ErrorSeverity(Enum):
    """
    Error severity levels for categorization.

    Educational Note:
    Different severities help prioritize issues and determine
    appropriate user feedback and recovery strategies.
    """
    INFO = "info"           # Informational, no action needed
    WARNING = "warning"     # Non-critical, continues functioning
    ERROR = "error"         # Significant issue, feature may not work
    CRITICAL = "critical"   # System-level failure


class ErrorCategory(Enum):
    """
    Categories of errors for better organization.

    Educational Note:
    Categorizing errors helps with:
    - Targeted troubleshooting guidance
    - Metrics and monitoring
    - User support and documentation
    """
    NETWORK = "network"             # Connection, timeout issues
    AUTHENTICATION = "authentication"  # Auth, permission issues
    VALIDATION = "validation"       # Input validation errors
    DATABASE = "database"           # Database/storage errors
    API = "api"                     # API-specific errors
    SYSTEM = "system"               # System-level errors
    USER_INPUT = "user_input"       # User input errors
    UNKNOWN = "unknown"             # Uncategorized errors


# ============================================================================
# Custom Exception Classes
# ============================================================================

@dataclass
class ErrorDetails:
    """
    Detailed error information for logging and display.

    Educational Note:
    Structured error data makes debugging easier and enables
    better error reporting and analytics.
    """
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    user_message: str  # User-friendly version
    technical_details: Optional[str] = None
    suggestions: Optional[List[str]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class OutpostError(Exception):
    """
    Base exception for Raspberry Pi Frontier errors.

    Educational Note:
    Custom exceptions make it easier to handle specific error
    types differently and provide contextual information.
    """

    def __init__(self, details: ErrorDetails):
        self.details = details
        super().__init__(details.message)


class NetworkError(OutpostError):
    """Errors related to network connectivity."""
    pass


class AuthenticationError(OutpostError):
    """Errors related to authentication and authorization."""
    pass


class ValidationError(OutpostError):
    """Errors related to input validation."""
    pass


class APIError(OutpostError):
    """Errors from API responses."""
    pass


# ============================================================================
# Logger Configuration
# ============================================================================

def setup_error_logger(name: str = "frontier_ui") -> logging.Logger:
    """
    Configure logger for UI errors.

    Educational Note:
    Proper logging is crucial for debugging production issues.
    Logs should capture enough detail without exposing sensitive info.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_error_logger()


# ============================================================================
# Error Display Components
# ============================================================================

def display_error(
    error_details: ErrorDetails,
    show_technical: bool = False,
    expandable: bool = True
):
    """
    Display an error message in the Streamlit UI.

    Educational Note:
    Good error messages:
    1. Explain what went wrong in user-friendly terms
    2. Suggest how to fix it
    3. Provide technical details for advanced users
    4. Don't expose sensitive information

    Args:
        error_details: Structured error information
        show_technical: Whether to show technical details by default
        expandable: Whether to make technical details expandable
    """
    # Map severity to Streamlit message type
    severity_map = {
        ErrorSeverity.INFO: st.info,
        ErrorSeverity.WARNING: st.warning,
        ErrorSeverity.ERROR: st.error,
        ErrorSeverity.CRITICAL: st.error
    }

    display_func = severity_map.get(error_details.severity, st.error)

    # Display user-friendly message
    display_func(error_details.user_message)

    # Show suggestions if available
    if error_details.suggestions:
        with st.container():
            st.markdown("**💡 Suggestions:**")
            for suggestion in error_details.suggestions:
                st.markdown(f"- {suggestion}")

    # Show technical details if requested
    if error_details.technical_details:
        if expandable:
            with st.expander("🔧 Technical Details"):
                st.code(error_details.technical_details, language="text")
        elif show_technical:
            st.caption("Technical Details:")
            st.code(error_details.technical_details, language="text")


def display_exception(
    exception: Exception,
    user_message: str = "An unexpected error occurred",
    show_traceback: bool = False
):
    """
    Display an exception with optional traceback.

    Educational Note:
    Tracebacks help developers debug but can confuse users.
    Show them conditionally (debug mode, admin users, etc.)

    Args:
        exception: The exception to display
        user_message: User-friendly error message
        show_traceback: Whether to show full traceback
    """
    st.error(user_message)

    if show_traceback:
        with st.expander("🐛 Error Traceback"):
            st.code(traceback.format_exc(), language="python")

    logger.error(f"{user_message}: {str(exception)}", exc_info=True)


def show_retry_button(
    retry_func: Callable,
    label: str = "🔄 Retry",
    key: Optional[str] = None
) -> bool:
    """
    Display a retry button for failed operations.

    Educational Note:
    Retry buttons give users control over recovery from transient failures.

    Args:
        retry_func: Function to call on retry
        label: Button label
        key: Unique key for the button

    Returns:
        True if retry was clicked
    """
    if st.button(label, key=key, type="secondary"):
        try:
            retry_func()
            st.success("✅ Operation completed successfully!")
            return True
        except Exception as e:
            display_exception(e, "Retry failed")
            return False
    return False


# ============================================================================
# Error Handling Decorators
# ============================================================================

def handle_errors(
    user_message: str = "An error occurred",
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    show_traceback: bool = False
):
    """
    Decorator to automatically handle errors in functions.

    Educational Note:
    Decorators wrap functions with additional logic.
    This pattern centralizes error handling, reducing code duplication.

    Usage:
        @handle_errors(user_message="Failed to load data")
        def load_data():
            # Function code that might raise errors
            pass

    Args:
        user_message: User-friendly error message
        category: Error category
        severity: Error severity
        show_traceback: Whether to show traceback

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Create error details
                error_details = ErrorDetails(
                    severity=severity,
                    category=category,
                    message=str(e),
                    user_message=user_message,
                    technical_details=traceback.format_exc() if show_traceback else str(e)
                )

                # Display error
                display_error(error_details, show_technical=show_traceback)

                # Log error
                logger.error(
                    f"{user_message}: {str(e)}",
                    exc_info=True,
                    extra={'category': category.value}
                )

                return None

        return wrapper

    return decorator


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function on failure with exponential backoff.

    Educational Note:
    Retries help recover from transient failures (network issues, etc.)
    Exponential backoff prevents overwhelming failing services.

    Usage:
        @retry_on_failure(max_attempts=3, delay=1.0)
        def fetch_data():
            # Code that might fail transiently
            pass

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Backoff multiplier for exponential backoff
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        # Final attempt failed, re-raise
                        raise

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay}s..."
                    )

                    # Show retry indicator in UI
                    with st.spinner(f"Retrying... (Attempt {attempt}/{max_attempts})"):
                        time.sleep(current_delay)

                    attempt += 1
                    current_delay *= backoff

        return wrapper

    return decorator


# ============================================================================
# Network Error Handlers
# ============================================================================

def handle_api_error(response: requests.Response, outpost_name: str = "outpost"):
    """
    Handle API error responses with appropriate user messages.

    Educational Note:
    Different HTTP status codes indicate different problems.
    Proper handling provides better user guidance.

    Args:
        response: requests.Response object
        outpost_name: Name of the outpost for error messages

    Raises:
        APIError: With detailed error information
    """
    status_code = response.status_code

    # Define error messages for common status codes
    error_messages = {
        400: ("Invalid request", "Check your input data and try again."),
        401: ("Authentication required", "Please log in or check your credentials."),
        403: ("Access denied", "You don't have permission to perform this action."),
        404: ("Resource not found", "The requested resource doesn't exist."),
        408: ("Request timeout", "The server took too long to respond."),
        429: ("Too many requests", "You're making requests too quickly. Please slow down."),
        500: ("Server error", "The server encountered an error. Try again later."),
        502: ("Bad gateway", "Unable to connect to the outpost. Check if it's online."),
        503: ("Service unavailable", "The outpost is temporarily unavailable."),
        504: ("Gateway timeout", "The outpost didn't respond in time.")
    }

    user_msg, suggestion = error_messages.get(
        status_code,
        ("Unknown error", "An unexpected error occurred.")
    )

    # Create detailed error
    error_details = ErrorDetails(
        severity=ErrorSeverity.ERROR if status_code < 500 else ErrorSeverity.CRITICAL,
        category=ErrorCategory.API,
        message=f"API error {status_code}: {response.text}",
        user_message=f"❌ Failed to connect to {outpost_name}: {user_msg}",
        technical_details=f"Status Code: {status_code}\nResponse: {response.text}",
        suggestions=[suggestion, "Check the outpost status and network connection."]
    )

    raise APIError(error_details)


def handle_network_error(
    exception: Exception,
    outpost_name: str = "outpost",
    operation: str = "connect"
):
    """
    Handle network-related errors with user-friendly messages.

    Educational Note:
    Network errors are common in distributed systems.
    Good error messages help users diagnose connectivity issues.

    Args:
        exception: The network exception
        outpost_name: Name of the outpost
        operation: Operation being performed

    Raises:
        NetworkError: With detailed error information
    """
    suggestions = [
        "Verify the outpost is powered on and connected to the network",
        "Check that you're on the same network as the outpost",
        "Confirm the IP address and port are correct",
        "Ensure firewall rules allow the connection"
    ]

    error_details = ErrorDetails(
        severity=ErrorSeverity.ERROR,
        category=ErrorCategory.NETWORK,
        message=str(exception),
        user_message=f"❌ Cannot {operation} to {outpost_name}",
        technical_details=traceback.format_exc(),
        suggestions=suggestions
    )

    raise NetworkError(error_details)


# ============================================================================
# Validation Error Handlers
# ============================================================================

def validate_not_empty(value: str, field_name: str) -> str:
    """
    Validate that a field is not empty.

    Educational Note:
    Input validation prevents errors downstream and provides
    immediate feedback to users.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        The validated value

    Raises:
        ValidationError: If validation fails
    """
    if not value or not value.strip():
        error_details = ErrorDetails(
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.VALIDATION,
            message=f"{field_name} is required",
            user_message=f"⚠️ {field_name} cannot be empty",
            suggestions=[f"Please enter a value for {field_name}"]
        )
        raise ValidationError(error_details)

    return value.strip()


def validate_ip_address(ip: str) -> str:
    """
    Validate IP address format.

    Args:
        ip: IP address to validate

    Returns:
        The validated IP address

    Raises:
        ValidationError: If validation fails
    """
    import ipaddress

    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        error_details = ErrorDetails(
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.VALIDATION,
            message=f"Invalid IP address: {ip}",
            user_message=f"⚠️ '{ip}' is not a valid IP address",
            suggestions=[
                "Use format: 192.168.1.100",
                "Check for typos in the IP address"
            ]
        )
        raise ValidationError(error_details)


def validate_port(port: int) -> int:
    """
    Validate port number.

    Args:
        port: Port number to validate

    Returns:
        The validated port

    Raises:
        ValidationError: If validation fails
    """
    if not (1 <= port <= 65535):
        error_details = ErrorDetails(
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.VALIDATION,
            message=f"Invalid port: {port}",
            user_message=f"⚠️ Port must be between 1 and 65535",
            suggestions=["Common ports: 8000 (HTTP), 22 (SSH), 443 (HTTPS)"]
        )
        raise ValidationError(error_details)

    return port


# ============================================================================
# Error Recovery Helpers
# ============================================================================

def with_fallback(primary_func: Callable, fallback_func: Callable, *args, **kwargs) -> Any:
    """
    Execute primary function with automatic fallback on failure.

    Educational Note:
    Fallbacks improve resilience by providing alternative paths
    when primary operations fail.

    Args:
        primary_func: Primary function to execute
        fallback_func: Fallback function if primary fails
        *args: Arguments to pass to functions
        **kwargs: Keyword arguments to pass to functions

    Returns:
        Result from primary or fallback function
    """
    try:
        return primary_func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Primary function failed: {str(e)}. Using fallback.")
        try:
            return fallback_func(*args, **kwargs)
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {str(fallback_error)}")
            raise


def safe_session_state_access(key: str, default: Any = None) -> Any:
    """
    Safely access session state with default fallback.

    Educational Note:
    Defensive programming prevents crashes from missing session data.

    Args:
        key: Session state key
        default: Default value if key doesn't exist

    Returns:
        Session state value or default
    """
    try:
        return st.session_state.get(key, default)
    except Exception as e:
        logger.error(f"Error accessing session state key '{key}': {str(e)}")
        return default


# ============================================================================
# Error Boundary Component
# ============================================================================

class ErrorBoundary:
    """
    Error boundary context manager for sections of UI code.

    Educational Note:
    Error boundaries isolate failures to specific UI sections,
    preventing total app crashes.

    Usage:
        with ErrorBoundary("Loading data"):
            # Code that might fail
            load_data()
    """

    def __init__(self, operation: str, show_traceback: bool = False):
        self.operation = operation
        self.show_traceback = show_traceback

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # An exception occurred
            display_exception(
                exc_val,
                user_message=f"Error during {self.operation}",
                show_traceback=self.show_traceback
            )

            # Log the error
            logger.error(
                f"Error boundary caught exception in '{self.operation}': {str(exc_val)}",
                exc_info=(exc_type, exc_val, exc_tb)
            )

            # Return True to suppress the exception
            return True

        return False
