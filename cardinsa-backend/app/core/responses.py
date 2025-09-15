from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from starlette import status

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response model for consistent response structure.
    """
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response model for list endpoints.
    """
    success: bool = True
    message: Optional[str] = None
    data: List[T] = []
    pagination: Dict[str, Any] = {
        "page": 1,
        "page_size": 20,
        "total_items": 0,
        "total_pages": 0,
        "has_next": False,
        "has_prev": False
    }
    errors: Optional[List[str]] = None

def create_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a successful API response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        meta: Additional metadata
    
    Returns:
        JSONResponse with success structure
    """
    response_data = APIResponse(
        success=True,
        message=message,
        data=data,
        meta=meta
    )
    return JSONResponse(
        status_code=status_code,
        content=response_data.model_dump(exclude_none=True)
    )

def create_error_response(
    message: str = "An error occurred",
    errors: Optional[List[str]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    data: Any = None
) -> JSONResponse:
    """
    Create an error API response.
    
    Args:
        message: Error message
        errors: List of detailed errors
        status_code: HTTP status code
        data: Optional data to include
    
    Returns:
        JSONResponse with error structure
    """
    response_data = APIResponse(
        success=False,
        message=message,
        data=data,
        errors=errors or []
    )
    return JSONResponse(
        status_code=status_code,
        content=response_data.model_dump(exclude_none=True)
    )

# Additional helper functions
def success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Alias for create_response for consistency.
    """
    return create_response(data=data, message=message, status_code=status_code, meta=meta)

def error_response(
    message: str = "An error occurred",
    errors: Optional[List[str]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    data: Any = None
) -> JSONResponse:
    """
    Alias for create_error_response for consistency.
    """
    return create_error_response(message=message, errors=errors, status_code=status_code, data=data)

def created_response(
    data: Any = None,
    message: str = "Resource created successfully"
) -> JSONResponse:
    """
    Create a 201 Created response.
    """
    return create_response(
        data=data,
        message=message,
        status_code=status.HTTP_201_CREATED
    )

def no_content_response(
    message: str = "Operation completed successfully"
) -> JSONResponse:
    """
    Create a 204 No Content response.
    """
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None
    )

def not_found_response(
    message: str = "Resource not found"
) -> JSONResponse:
    """
    Create a 404 Not Found response.
    """
    return create_error_response(
        message=message,
        status_code=status.HTTP_404_NOT_FOUND
    )

def forbidden_response(
    message: str = "Insufficient permissions"
) -> JSONResponse:
    """
    Create a 403 Forbidden response.
    """
    return create_error_response(
        message=message,
        status_code=status.HTTP_403_FORBIDDEN
    )

def unauthorized_response(
    message: str = "Authentication required"
) -> JSONResponse:
    """
    Create a 401 Unauthorized response.
    """
    return create_error_response(
        message=message,
        status_code=status.HTTP_401_UNAUTHORIZED
    )

def conflict_response(
    message: str = "Resource conflict",
    errors: Optional[List[str]] = None
) -> JSONResponse:
    """
    Create a 409 Conflict response.
    """
    return create_error_response(
        message=message,
        errors=errors,
        status_code=status.HTTP_409_CONFLICT
    )

def validation_error_response(
    message: str = "Validation failed",
    errors: Optional[List[str]] = None
) -> JSONResponse:
    """
    Create a 422 Validation Error response.
    """
    return create_error_response(
        message=message,
        errors=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

def paginated_response(
    items: List[Any],
    page: int,
    page_size: int,
    total_items: int,
    message: str = "Data retrieved successfully"
) -> JSONResponse:
    """
    Create a paginated response.
    
    Args:
        items: List of items for current page
        page: Current page number
        page_size: Items per page
        total_items: Total number of items
        message: Success message
    
    Returns:
        JSONResponse with paginated structure
    """
    import math
    
    total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    response_data = PaginatedResponse(
        success=True,
        message=message,
        data=items,
        pagination={
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data.model_dump(exclude_none=True)
    )

# Response models for OpenAPI documentation
class SuccessResponseModel(BaseModel):
    """Standard success response model for OpenAPI docs"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None

class ErrorResponseModel(BaseModel):
    """Standard error response model for OpenAPI docs"""
    success: bool = False
    message: str = "An error occurred"
    errors: Optional[List[str]] = None
    data: Optional[Dict[str, Any]] = None