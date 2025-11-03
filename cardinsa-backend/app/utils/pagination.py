# app/utils/pagination.py

"""
Comprehensive Pagination Utilities

Provides pagination functionality for FastAPI applications with SQLAlchemy,
including response models, parameter validation, and utility functions.
"""

from math import ceil
from typing import Tuple, Generic, TypeVar, List, Optional, Any, Dict
from sqlalchemy import func, select, asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum

# Import existing pagination models if available
try:
    from app.modules.common.pagination_models import PageParams as CommonPageParams, PageMeta as CommonPageMeta
    HAS_COMMON_MODELS = True
except ImportError:
    HAS_COMMON_MODELS = False

# Generic type for paginated items
T = TypeVar('T')


# =====================================================================
# ENUMS
# =====================================================================

class SortDirection(str, Enum):
    """Sort direction enumeration"""
    ASC = "asc"
    DESC = "desc"


# =====================================================================
# PARAMETER MODELS
# =====================================================================

class PageParams(BaseModel):
    """Page parameters for pagination requests"""
    
    model_config = ConfigDict(from_attributes=True)
    
    page: int = Field(default=1, ge=1, le=10000, description="Page number (1-based)")
    size: int = Field(default=20, ge=1, le=100, description="Number of items per page")
    
    @field_validator('page')
    @classmethod
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be at least 1')
        return v
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        if v < 1:
            raise ValueError('Size must be at least 1')
        if v > 100:
            raise ValueError('Size cannot exceed 100')
        return v
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.size
    
    @property
    def limit(self) -> int:
        """Alias for size for database queries"""
        return self.size


class PaginationParams(PageParams):
    """Extended pagination parameters with sorting"""
    
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_direction: SortDirection = Field(default=SortDirection.ASC, description="Sort direction")
    
    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v):
        if v is not None and not v.strip():
            return None
        return v


# =====================================================================
# METADATA MODELS
# =====================================================================

class PageMeta(BaseModel):
    """Pagination metadata"""
    
    model_config = ConfigDict(from_attributes=True)
    
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=0, description="Total number of pages")
    
    @property
    def has_next(self) -> bool:
        """Check if there is a next page"""
        return self.page < self.pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page"""
        return self.page > 1
    
    @property
    def is_first_page(self) -> bool:
        """Check if this is the first page"""
        return self.page == 1
    
    @property
    def is_last_page(self) -> bool:
        """Check if this is the last page"""
        return self.page >= self.pages
    
    @property
    def start_index(self) -> int:
        """Get the starting index of items on current page (1-based)"""
        if self.total == 0:
            return 0
        return ((self.page - 1) * self.size) + 1
    
    @property
    def end_index(self) -> int:
        """Get the ending index of items on current page (1-based)"""
        if self.total == 0:
            return 0
        return min(self.page * self.size, self.total)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'page': self.page,
            'size': self.size,
            'total': self.total,
            'pages': self.pages,
            'has_next': self.has_next,
            'has_previous': self.has_previous,
            'is_first_page': self.is_first_page,
            'is_last_page': self.is_last_page,
            'start_index': self.start_index,
            'end_index': self.end_index
        }


# =====================================================================
# RESPONSE MODELS
# =====================================================================

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[T] = Field(..., description="Items in the current page")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")
    
    @property
    def has_next(self) -> bool:
        """Check if there is a next page"""
        return self.page < self.pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page"""
        return self.page > 1
    
    @property
    def meta(self) -> PageMeta:
        """Get pagination metadata"""
        return PageMeta(
            page=self.page,
            size=self.size,
            total=self.total,
            pages=self.pages
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (useful for JSON responses)"""
        return {
            'items': [item.dict() if hasattr(item, 'dict') else item for item in self.items],
            'pagination': self.meta.to_dict()
        }


class PaginatedListResponse(PaginatedResponse[T]):
    """Paginated list response with additional metadata"""
    
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Applied filters")
    sort_applied: Optional[Dict[str, str]] = Field(None, description="Applied sorting")
    query_time_ms: Optional[float] = Field(None, description="Query execution time in milliseconds")


# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================

def paginate(
    db: Session, 
    stmt: Select, 
    params: PageParams,
    count_query: Optional[Select] = None
) -> Tuple[List[Any], PageMeta]:
    """
    Paginate a SQLAlchemy query
    
    Args:
        db: Database session
        stmt: SQLAlchemy select statement
        params: Pagination parameters
        count_query: Optional custom count query
        
    Returns:
        Tuple of (items, pagination_meta)
    """
    # Count total items
    if count_query is not None:
        total = db.execute(count_query).scalar_one()
    else:
        # Remove ordering and limiting from count query for performance
        count_stmt = select(func.count()).select_from(
            stmt.order_by(None).limit(None).offset(None).subquery()
        )
        total = db.execute(count_stmt).scalar_one()
    
    # Calculate pages
    pages = ceil(total / params.size) if params.size > 0 else 0
    
    # Fetch items for current page
    page_stmt = stmt.limit(params.size).offset(params.offset)
    items = db.execute(page_stmt).scalars().all()
    
    # Create metadata
    meta = PageMeta(
        page=params.page,
        size=params.size,
        total=total,
        pages=pages
    )
    
    return items, meta


def paginate_query(
    db: Session,
    query_stmt: Select,
    page: int = 1,
    size: int = 20,
    max_size: int = 100
) -> Tuple[List[Any], PageMeta]:
    """
    Simple pagination function with validation
    
    Args:
        db: Database session
        query_stmt: SQLAlchemy select statement
        page: Page number (1-based)
        size: Items per page
        max_size: Maximum allowed page size
        
    Returns:
        Tuple of (items, pagination_meta)
    """
    # Validate parameters
    page = max(1, page)
    size = min(max(1, size), max_size)
    
    params = PageParams(page=page, size=size)
    return paginate(db, query_stmt, params)


def apply_sort(
    stmt: Select, 
    model: Any, 
    sort_by: Optional[str] = None, 
    sort_direction: Optional[str] = None
) -> Select:
    """
    Apply sorting to a SQLAlchemy query
    
    Args:
        stmt: SQLAlchemy select statement
        model: SQLAlchemy model class
        sort_by: Field name to sort by
        sort_direction: Sort direction ('asc' or 'desc')
        
    Returns:
        Modified select statement with sorting applied
    """
    if not sort_by:
        return stmt
    
    # Get the column from the model
    column = getattr(model, sort_by, None)
    if column is None:
        return stmt
    
    # Apply sorting direction
    direction = (sort_direction or "asc").lower()
    if direction == "desc":
        return stmt.order_by(column.desc())
    else:
        return stmt.order_by(column.asc())


def apply_filters(
    stmt: Select,
    model: Any,
    filters: Dict[str, Any]
) -> Select:
    """
    Apply filters to a SQLAlchemy query
    
    Args:
        stmt: SQLAlchemy select statement
        model: SQLAlchemy model class
        filters: Dictionary of field names and values to filter by
        
    Returns:
        Modified select statement with filters applied
    """
    for field_name, value in filters.items():
        if value is None:
            continue
            
        column = getattr(model, field_name, None)
        if column is None:
            continue
            
        # Handle different filter types
        if isinstance(value, list):
            stmt = stmt.where(column.in_(value))
        elif isinstance(value, str) and value.startswith('%') and value.endswith('%'):
            # LIKE filter
            stmt = stmt.where(column.like(value))
        else:
            # Exact match
            stmt = stmt.where(column == value)
    
    return stmt


def create_paginated_response(
    items: List[T],
    meta: PageMeta,
    filters: Optional[Dict[str, Any]] = None,
    sort_info: Optional[Dict[str, str]] = None
) -> PaginatedListResponse[T]:
    """
    Create a paginated response object
    
    Args:
        items: List of items for current page
        meta: Pagination metadata
        filters: Applied filters
        sort_info: Applied sorting information
        
    Returns:
        PaginatedListResponse object
    """
    return PaginatedListResponse(
        items=items,
        total=meta.total,
        page=meta.page,
        size=meta.size,
        pages=meta.pages,
        filters_applied=filters,
        sort_applied=sort_info
    )


# =====================================================================
# BACKWARDS COMPATIBILITY
# =====================================================================

# If common pagination models exist, create aliases for compatibility
if HAS_COMMON_MODELS:
    # Use existing models as base and extend them
    class ExtendedPageParams(CommonPageParams):
        @property
        def offset(self) -> int:
            return (self.page - 1) * self.size
    
    class ExtendedPageMeta(CommonPageMeta):
        @property
        def has_next(self) -> bool:
            return self.page < self.pages
        
        @property
        def has_previous(self) -> bool:
            return self.page > 1


# =====================================================================
# EXPORTS
# =====================================================================

__all__ = [
    # Parameter models
    'PageParams',
    'PaginationParams',
    
    # Metadata models
    'PageMeta',
    
    # Response models
    'PaginatedResponse',
    'PaginatedListResponse',
    
    # Enums
    'SortDirection',
    
    # Utility functions
    'paginate',
    'paginate_query',
    'apply_sort',
    'apply_filters',
    'create_paginated_response',
    
    # Generic type
    'T'
]