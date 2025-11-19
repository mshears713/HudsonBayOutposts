"""
Enhanced Logging Configuration for Raspberry Pi APIs

This module provides comprehensive logging setup for all fort APIs including
request logging, error tracking, performance monitoring, and structured logging.

Educational Note:
Proper logging is essential for production systems. Good logs help with:
- Debugging issues
- Performance monitoring
- Security auditing
- Understanding user behavior
- Compliance and troubleshooting

Phase 4 Feature (Step 36):
Production-ready logging with request tracking, performance metrics, and structured output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Optional, Dict, Any
from functools import wraps
import time

# ============================================================================
# Logging Configuration
# ============================================================================

class LogConfig:
    """
    Centralized logging configuration.

    Educational Note:
    Consistent logging configuration across all APIs ensures
    uniform log format and makes centralized log analysis easier.
    """
    # Log levels
    LEVEL_DEBUG = logging.DEBUG
    LEVEL_INFO = logging.INFO
    LEVEL_WARNING = logging.WARNING
    LEVEL_ERROR = logging.ERROR
    LEVEL_CRITICAL = logging.CRITICAL

    # Log file paths
    LOG_DIR = Path(__file__).parent.parent / "logs"
    API_LOG_FILE = LOG_DIR / "api.log"
    ERROR_LOG_FILE = LOG_DIR / "errors.log"
    ACCESS_LOG_FILE = LOG_DIR / "access.log"
    PERFORMANCE_LOG_FILE = LOG_DIR / "performance.log"

    # Log format
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DETAILED_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'

    # Performance thresholds (milliseconds)
    SLOW_REQUEST_THRESHOLD = 1000  # 1 second
    VERY_SLOW_REQUEST_THRESHOLD = 5000  # 5 seconds

    # Log rotation settings
    MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5


# ============================================================================
# Logger Setup
# ============================================================================

def setup_logging(
    log_level: int = LogConfig.LEVEL_INFO,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True
) -> logging.Logger:
    """
    Set up comprehensive logging for API server.

    Educational Note:
    This creates multiple log handlers for different purposes:
    - Console: For development and immediate feedback
    - File: For persistent logs and analysis
    - Error file: Dedicated error tracking
    - Access file: Request/response logging

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Whether to log to files
        enable_console_logging: Whether to log to console

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    LogConfig.LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(LogConfig.LOG_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handlers
    if enable_file_logging:
        from logging.handlers import RotatingFileHandler

        # Main API log
        api_handler = RotatingFileHandler(
            LogConfig.API_LOG_FILE,
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT
        )
        api_handler.setLevel(log_level)
        api_formatter = logging.Formatter(LogConfig.DETAILED_FORMAT)
        api_handler.setFormatter(api_formatter)
        logger.addHandler(api_handler)

        # Error log (only errors and above)
        error_handler = RotatingFileHandler(
            LogConfig.ERROR_LOG_FILE,
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(LogConfig.DETAILED_FORMAT)
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)

    logger.info("Logging initialized")
    return logger


# ============================================================================
# Request Logging
# ============================================================================

class RequestLogger:
    """
    Logger for HTTP requests with performance tracking.

    Educational Note:
    Request logging helps understand API usage patterns,
    identify performance issues, and debug problems.
    """

    def __init__(self, logger_name: str = "api.requests"):
        self.logger = logging.getLogger(logger_name)
        self.access_logger = self._setup_access_logger()

    def _setup_access_logger(self) -> logging.Logger:
        """Set up dedicated access log."""
        access_logger = logging.getLogger("api.access")
        access_logger.setLevel(logging.INFO)

        # Only add handler if not already present
        if not access_logger.handlers:
            from logging.handlers import RotatingFileHandler

            handler = RotatingFileHandler(
                LogConfig.ACCESS_LOG_FILE,
                maxBytes=LogConfig.MAX_BYTES,
                backupCount=LogConfig.BACKUP_COUNT
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(message)s'
            )
            handler.setFormatter(formatter)
            access_logger.addHandler(handler)

        return access_logger

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: Optional[str] = None,
        user: Optional[str] = None,
        **kwargs
    ):
        """
        Log an HTTP request with metadata.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status_code: HTTP status code
            duration_ms: Request duration in milliseconds
            client_ip: Client IP address
            user: Authenticated user (if any)
            **kwargs: Additional metadata
        """
        # Build log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': round(duration_ms, 2),
            'client_ip': client_ip,
            'user': user or 'anonymous',
            **kwargs
        }

        # Log to access log (structured JSON)
        self.access_logger.info(json.dumps(log_entry))

        # Log to main log with level based on status code
        log_msg = f"{method} {path} - {status_code} - {duration_ms:.2f}ms"

        if status_code >= 500:
            self.logger.error(log_msg)
        elif status_code >= 400:
            self.logger.warning(log_msg)
        elif duration_ms > LogConfig.VERY_SLOW_REQUEST_THRESHOLD:
            self.logger.warning(f"VERY SLOW REQUEST: {log_msg}")
        elif duration_ms > LogConfig.SLOW_REQUEST_THRESHOLD:
            self.logger.warning(f"Slow request: {log_msg}")
        else:
            self.logger.info(log_msg)


# ============================================================================
# Performance Logging
# ============================================================================

class PerformanceLogger:
    """
    Logger for performance metrics and slow operations.

    Educational Note:
    Performance logging helps identify bottlenecks and
    optimize system performance over time.
    """

    def __init__(self, logger_name: str = "api.performance"):
        self.logger = logging.getLogger(logger_name)
        self._setup_performance_logger()

    def _setup_performance_logger(self):
        """Set up dedicated performance log."""
        if not self.logger.handlers:
            from logging.handlers import RotatingFileHandler

            handler = RotatingFileHandler(
                LogConfig.PERFORMANCE_LOG_FILE,
                maxBytes=LogConfig.MAX_BYTES,
                backupCount=LogConfig.BACKUP_COUNT
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_operation(
        self,
        operation: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a timed operation.

        Args:
            operation: Operation description
            duration_ms: Operation duration in milliseconds
            metadata: Additional metadata
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration_ms': round(duration_ms, 2),
            'metadata': metadata or {}
        }

        self.logger.info(json.dumps(entry))

        # Warn on slow operations
        if duration_ms > LogConfig.SLOW_REQUEST_THRESHOLD:
            self.logger.warning(f"Slow operation: {operation} took {duration_ms:.2f}ms")


# ============================================================================
# Decorators for Automatic Logging
# ============================================================================

def log_endpoint(logger: Optional[logging.Logger] = None):
    """
    Decorator to automatically log API endpoint calls.

    Educational Note:
    Decorators provide reusable logging without cluttering endpoint code.

    Args:
        logger: Optional custom logger

    Example:
        @log_endpoint()
        def get_animals():
            return animals
    """
    if logger is None:
        logger = logging.getLogger("api.endpoints")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Log entry
            logger.debug(f"Entering {func.__name__}")

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                logger.info(
                    f"{func.__name__} completed in {duration_ms:.2f}ms"
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"{func.__name__} failed after {duration_ms:.2f}ms: {str(e)}",
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_performance(operation_name: Optional[str] = None):
    """
    Decorator to log operation performance.

    Args:
        operation_name: Custom operation name (defaults to function name)

    Example:
        @log_performance("database_query")
        def get_all_animals():
            return db.query(...)
    """
    perf_logger = PerformanceLogger()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                perf_logger.log_operation(op_name, duration_ms)

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                perf_logger.log_operation(
                    op_name,
                    duration_ms,
                    {'error': str(e)}
                )
                raise

        return wrapper
    return decorator


# ============================================================================
# Structured Logging
# ============================================================================

class StructuredLogger:
    """
    Logger for structured JSON logging.

    Educational Note:
    Structured logs (JSON format) are easier to parse and analyze
    programmatically compared to plain text logs.
    """

    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    def log_event(
        self,
        event_type: str,
        level: int = logging.INFO,
        **kwargs
    ):
        """
        Log a structured event.

        Args:
            event_type: Type of event
            level: Log level
            **kwargs: Event metadata
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            **kwargs
        }

        self.logger.log(level, json.dumps(event))


# ============================================================================
# FastAPI Middleware Integration
# ============================================================================

def create_request_logging_middleware(app):
    """
    Create middleware for automatic request logging.

    Educational Note:
    Middleware intercepts all requests, providing a single
    point to add logging without modifying each endpoint.

    Args:
        app: FastAPI application instance

    Example:
        from fastapi import FastAPI
        app = FastAPI()
        create_request_logging_middleware(app)
    """
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    import time

    request_logger = RequestLogger()

    class LoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Record start time
            start_time = time.time()

            # Get client IP
            client_ip = request.client.host if request.client else None

            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log request
            request_logger.log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                client_ip=client_ip,
                query_params=str(request.query_params) if request.query_params else None
            )

            return response

    app.add_middleware(LoggingMiddleware)


# ============================================================================
# Log Analysis Helpers
# ============================================================================

def analyze_logs(log_file: Path, limit: int = 100) -> Dict[str, Any]:
    """
    Analyze log file and extract statistics.

    Educational Note:
    Log analysis helps understand system behavior and identify issues.

    Args:
        log_file: Path to log file
        limit: Number of recent entries to analyze

    Returns:
        Dictionary with analysis results
    """
    if not log_file.exists():
        return {'error': 'Log file not found'}

    stats = {
        'total_entries': 0,
        'by_level': {},
        'recent_errors': [],
        'slow_requests': []
    }

    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()[-limit:]

            for line in lines:
                stats['total_entries'] += 1

                # Count by level
                for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                    if level in line:
                        stats['by_level'][level] = stats['by_level'].get(level, 0) + 1

                # Track errors
                if 'ERROR' in line or 'CRITICAL' in line:
                    stats['recent_errors'].append(line.strip())

                # Track slow requests
                if 'Slow' in line or 'SLOW' in line:
                    stats['slow_requests'].append(line.strip())

    except Exception as e:
        stats['error'] = str(e)

    return stats


# ============================================================================
# Initialization Function
# ============================================================================

def initialize_api_logging(
    fort_name: str,
    log_level: int = LogConfig.LEVEL_INFO
) -> logging.Logger:
    """
    Initialize logging for a fort API.

    Args:
        fort_name: Name of the fort (for log identification)
        log_level: Logging level

    Returns:
        Configured logger

    Example:
        from raspberry_pi.api.logging_config import initialize_api_logging
        logger = initialize_api_logging("Hunting Fort", logging.INFO)
    """
    logger = setup_logging(log_level)
    logger.info(f"Starting {fort_name} API with enhanced logging")

    return logger
