# app/core/exceptions.py

from functools import wraps
from typing import Callable, Any
import logging
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, NoResultFound
from starlette import status

logger = logging.getLogger(__name__)

# ==================== CUSTOM EXCEPTION CLASSES ====================

class BaseAppException(Exception):
    """Base exception class for application-specific errors"""
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class BusinessLogicError(BaseAppException):
    """Raised when business logic rules are violated"""
    def __init__(self, message: str, code: str = "BUSINESS_LOGIC_ERROR", details: dict = None):
        super().__init__(message, code, details)

class ValidationError(BaseAppException):
    """Raised when data validation fails"""
    def __init__(self, message: str, code: str = "VALIDATION_ERROR", details: dict = None):
        super().__init__(message, code, details)

class NotFoundError(BaseAppException):
    """Raised when a requested resource is not found"""
    def __init__(self, message: str, code: str = "NOT_FOUND", details: dict = None):
        super().__init__(message, code, details)

class ConflictError(BaseAppException):
    """Raised when there's a data conflict (duplicate, constraint violation)"""
    def __init__(self, message: str, code: str = "CONFLICT", details: dict = None):
        super().__init__(message, code, details)

class PermissionDeniedError(BaseAppException):
    """Raised when user lacks permission for an operation"""
    def __init__(self, message: str, code: str = "PERMISSION_DENIED", details: dict = None):
        super().__init__(message, code, details)

class AuthenticationError(BaseAppException):
    """Raised when authentication fails"""
    def __init__(self, message: str, code: str = "AUTHENTICATION_ERROR", details: dict = None):
        super().__init__(message, code, details)

class UnauthorizedError(BaseAppException):
    """Raised when user is not authorized for an operation"""
    def __init__(self, message: str, code: str = "UNAUTHORIZED", details: dict = None):
        super().__init__(message, code, details)

class ServiceUnavailableError(BaseAppException):
    """Raised when an external service is unavailable"""
    def __init__(self, message: str, code: str = "SERVICE_UNAVAILABLE", details: dict = None):
        super().__init__(message, code, details)

class RateLimitError(BaseAppException):
    """Raised when rate limits are exceeded"""
    def __init__(self, message: str, code: str = "RATE_LIMIT_EXCEEDED", details: dict = None):
        super().__init__(message, code, details)

class ConfigurationError(BaseAppException):
    """Raised when there's a configuration issue"""
    def __init__(self, message: str, code: str = "CONFIGURATION_ERROR", details: dict = None):
        super().__init__(message, code, details)

class DatabaseOperationError(BaseAppException):
    """Raised when database operations fail"""
    def __init__(self, message: str, code: str = "DATABASE_OPERATION_ERROR", details: dict = None):
        super().__init__(message, code, details)

# ==================== CONVENIENCE ALIASES ====================

# Aliases for backward compatibility
EntityNotFoundError = NotFoundError
DatabaseError = DatabaseOperationError

# ==================== DECORATOR FOR ROUTE EXCEPTION HANDLING ====================

def handle_exceptions(func: Callable) -> Callable:
    """
    Decorator to handle common exceptions in route handlers.
    Catches and converts exceptions to appropriate HTTP responses.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        
        except HTTPException:
            # Re-raise FastAPI HTTP exceptions as-is
            raise
        
        except BusinessLogicError as e:
            logger.warning(f"BusinessLogicError in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": e.message,
                    "code": e.code,
                    "details": e.details
                }
            )
        
        except ValidationError as e:
            logger.warning(f"ValidationError in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": e.message,
                    "code": e.code,
                    "details": e.details
                }
            )
        
        except NotFoundError as e:
            logger.warning(f"NotFoundError in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": e.message,
                    "code": e.code,
                    "details": e.details
                }
            )
        
        except ConflictError as e:
            logger.warning(f"ConflictError in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": e.message,
                    "code": e.code,
                    "details": e.details
                }
            )
        
        except PermissionDeniedError as e:
            logger.warning(f"PermissionDeniedError in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": e.message,
                    "code": e.code,
                    "details": e.details
                }
            )
        
        except AuthenticationError as e:
            logger.warning(f"AuthenticationError in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": e.message,
                    "code": e.code,
                    "details": e.details
                }
            )
        
        except UnauthorizedError as e:
            logger.warning(f"UnauthorizedError in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": e.message,
                    "code": e.code,
                    "details": e.details
                }
            )
        
        except ServiceUnavailableError as e:
            logger.error(f"ServiceUnavailableError in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": e.message,
                    "code": e.code,
                    "details": e.details
                }
            )
        
        except RateLimitError as e:
            logger.warning(f"RateLimitError in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": e.message,
                    "code": e.code,
                    "details": e.details
                }
            )
        
        except DatabaseOperationError as e:
            logger.error(f"DatabaseOperationError in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": e.message,
                    "code": e.code,
                    "details": e.details
                }
            )
        
        except ValueError as e:
            logger.warning(f"ValueError in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        except NoResultFound as e:
            logger.warning(f"NoResultFound in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )
        
        except IntegrityError as e:
            logger.error(f"IntegrityError in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity constraint violation (duplicate or constraint error)"
            )
        
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        
        except PermissionError as e:
            logger.warning(f"PermissionError in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )
    
    return wrapper

# ==================== GLOBAL EXCEPTION HANDLERS ====================

def install_exception_handlers(app) -> None:
    """
    Install global exception handlers for the FastAPI app.
    These handle exceptions that aren't caught by route decorators.
    """
    
    @app.exception_handler(BusinessLogicError)
    async def business_logic_error_handler(request: Request, exc: BusinessLogicError):
        logger.warning(f"Global BusinessLogicError: {exc.message}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": {
                    "message": exc.message,
                    "code": exc.code,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        logger.warning(f"Global ValidationError: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={
                "detail": {
                    "message": exc.message,
                    "code": exc.code,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError):
        logger.warning(f"Global NotFoundError: {exc.message}")
        return JSONResponse(
            status_code=404,
            content={
                "detail": {
                    "message": exc.message,
                    "code": exc.code,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(ConflictError)
    async def conflict_error_handler(request: Request, exc: ConflictError):
        logger.warning(f"Global ConflictError: {exc.message}")
        return JSONResponse(
            status_code=409,
            content={
                "detail": {
                    "message": exc.message,
                    "code": exc.code,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(UnauthorizedError)
    async def unauthorized_error_handler(request: Request, exc: UnauthorizedError):
        logger.warning(f"Global UnauthorizedError: {exc.message}")
        return JSONResponse(
            status_code=401,
            content={
                "detail": {
                    "message": exc.message,
                    "code": exc.code,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(DatabaseOperationError)
    async def database_operation_error_handler(request: Request, exc: DatabaseOperationError):
        logger.error(f"Global DatabaseOperationError: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": {
                    "message": exc.message,
                    "code": exc.code,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.error(f"Global IntegrityError: {str(exc)}")
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Integrity error (constraint or duplicate).",
                "error": str(exc.orig) if exc.orig else str(exc),
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Global SQLAlchemyError: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Database error.", "error": str(exc)},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.warning(f"Global ValueError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"}
        )

# ==================== UTILITY FUNCTIONS ====================

def raise_not_found(resource: str, identifier: str = None) -> None:
    """Raise a standardized NotFoundError"""
    message = f"{resource} not found"
    if identifier:
        message += f" with identifier: {identifier}"
    raise NotFoundError(message)

def raise_conflict(resource: str, reason: str = None) -> None:
    """Raise a standardized ConflictError"""
    message = f"Conflict with {resource}"
    if reason:
        message += f": {reason}"
    raise ConflictError(message)

def raise_validation_error(field: str, value: Any, reason: str = None) -> None:
    """Raise a standardized ValidationError"""
    message = f"Validation failed for field '{field}'"
    if reason:
        message += f": {reason}"
    details = {"field": field, "value": str(value)}
    raise ValidationError(message, details=details)

def raise_business_logic_error(message: str, code: str = None, **details) -> None:
    """Raise a standardized BusinessLogicError"""
    raise BusinessLogicError(message, code=code, details=details)

def raise_unauthorized(message: str = "Unauthorized", code: str = None, **details) -> None:
    """Raise a standardized UnauthorizedError"""
    raise UnauthorizedError(message, code=code, details=details)

# ==================== EXPORTS ====================

__all__ = [
    'BaseAppException',
    'BusinessLogicError',
    'ValidationError',
    'NotFoundError',
    'ConflictError',
    'PermissionDeniedError',
    'AuthenticationError',
    'UnauthorizedError',
    'ServiceUnavailableError',
    'RateLimitError',
    'ConfigurationError',
    'DatabaseOperationError',
    'EntityNotFoundError',  # Alias for NotFoundError
    'DatabaseError',        # Alias for DatabaseOperationError
    'handle_exceptions',
    'install_exception_handlers',
    'raise_not_found',
    'raise_conflict',
    'raise_validation_error',
    'raise_business_logic_error',
    'raise_unauthorized',
]