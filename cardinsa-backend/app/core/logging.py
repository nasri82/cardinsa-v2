# app/core/logging.py

import logging
import logging.config
import sys
import os
from typing import Optional
from pathlib import Path

def configure_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, logs only to console.
    """
    # Get log level from environment or use provided default
    LOG_LEVEL = os.getenv("LOG_LEVEL", log_level).upper()
    
    # Create logs directory if logging to file
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(lineno)-4d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "uvicorn": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "minimal": {
                "format": "%(levelname)s | %(name)s | %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "simple" if LOG_LEVEL in ["INFO", "WARNING", "ERROR"] else "detailed",
                "level": LOG_LEVEL,
            },
            "uvicorn_console": {
                "class": "logging.StreamHandler", 
                "stream": sys.stdout,
                "formatter": "uvicorn",
                "level": LOG_LEVEL,
            },
        },
        "loggers": {
            # Root logger
            "": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
                "propagate": False
            },
            # Application loggers
            "app": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
                "propagate": False
            },
            "app.modules": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
                "propagate": False
            },
            "app.core": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
                "propagate": False
            },
            # FastAPI/Uvicorn loggers
            "uvicorn": {
                "handlers": ["uvicorn_console"],
                "level": LOG_LEVEL,
                "propagate": False
            },
            "uvicorn.error": {
                "handlers": ["uvicorn_console"],
                "level": LOG_LEVEL,
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["uvicorn_console"],
                "level": "INFO",  # Usually want to see access logs
                "propagate": False
            },
            # Third-party loggers (usually less verbose)
            "sqlalchemy": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "WARNING",  # Set to INFO to see SQL queries
                "propagate": False
            },
            "alembic": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "fastapi": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "httpx": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False
            },
            "httpcore": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False
            }
        }
    }
    
    # Add file handler if log_file is specified
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
            "level": LOG_LEVEL,
        }
        
        # Add file handler to all loggers
        for logger_name in config["loggers"]:
            if "handlers" in config["loggers"][logger_name]:
                config["loggers"][logger_name]["handlers"].append("file")
    
    # Apply configuration
    logging.config.dictConfig(config)

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The name of the logger. If None, uses the calling module's name.
        
    Returns:
        Logger instance
    """
    if name is None:
        # Try to get the name from the calling module
        import inspect
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back
            caller_module = inspect.getmodule(caller_frame)
            if caller_module and hasattr(caller_module, '__name__'):
                name = caller_module.__name__
            else:
                name = "app"
        finally:
            del frame
    
    return logging.getLogger(name)

def setup_sql_logging(enable: bool = False) -> None:
    """
    Enable or disable SQL query logging.
    
    Args:
        enable: Whether to enable SQL logging
    """
    sql_logger = logging.getLogger("sqlalchemy.engine")
    if enable:
        sql_logger.setLevel(logging.INFO)
    else:
        sql_logger.setLevel(logging.WARNING)

def set_logger_level(logger_name: str, level: str) -> None:
    """
    Set the logging level for a specific logger.
    
    Args:
        logger_name: Name of the logger
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))

def get_app_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for an application module with consistent naming.
    
    Args:
        module_name: The module name (e.g., 'pricing.profiles.service')
        
    Returns:
        Logger instance with name 'app.modules.{module_name}'
    """
    logger_name = f"app.modules.{module_name}"
    return logging.getLogger(logger_name)

def log_function_call(logger: logging.Logger, func_name: str, **kwargs) -> None:
    """
    Log a function call with its parameters.
    
    Args:
        logger: Logger instance
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    if logger.isEnabledFor(logging.DEBUG):
        params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.debug(f"Calling {func_name}({params})")

def log_performance(logger: logging.Logger, operation: str, duration: float, **context) -> None:
    """
    Log performance metrics for an operation.
    
    Args:
        logger: Logger instance
        operation: Name of the operation
        duration: Duration in seconds
        **context: Additional context to log
    """
    context_str = ", ".join([f"{k}={v}" for k, v in context.items()]) if context else ""
    logger.info(f"Performance: {operation} took {duration:.3f}s {context_str}")

# Convenience functions for common logging patterns
def log_error_with_context(logger: logging.Logger, error: Exception, context: dict = None) -> None:
    """
    Log an error with additional context information.
    
    Args:
        logger: Logger instance
        error: The exception that occurred
        context: Additional context information
    """
    context_str = ""
    if context:
        context_str = " | Context: " + ", ".join([f"{k}={v}" for k, v in context.items()])
    
    logger.error(f"Error: {type(error).__name__}: {str(error)}{context_str}", exc_info=True)

def log_user_action(logger: logging.Logger, user_id: str, action: str, **details) -> None:
    """
    Log a user action for audit purposes.
    
    Args:
        logger: Logger instance
        user_id: ID of the user performing the action
        action: Description of the action
        **details: Additional details about the action
    """
    details_str = ", ".join([f"{k}={v}" for k, v in details.items()]) if details else ""
    logger.info(f"User Action: {user_id} performed '{action}' {details_str}")

# Initialize logging configuration when module is imported
# This ensures logging is configured early in the application lifecycle
configure_logging()

# Export commonly used functions
__all__ = [
    'configure_logging',
    'get_logger',
    'get_app_logger',
    'setup_sql_logging',
    'set_logger_level',
    'log_function_call',
    'log_performance',
    'log_error_with_context',
    'log_user_action',
]