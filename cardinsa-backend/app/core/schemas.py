# app/core/schemas.py

"""
Core Schemas Module
==================

Base Pydantic schemas and common schema patterns used throughout the application.
Provides consistent schema base classes, validation patterns, and common field types.
"""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict, validator
from uuid import UUID
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum


# =============================================================================
# BASE SCHEMA CLASSES
# =============================================================================

class BaseSchema(BaseModel):
    """
    Enhanced base schema class with common functionality
    
    Features:
    - Consistent configuration across all schemas
    - Common validation patterns
    - JSON serialization support
    - From ORM attribute mapping
    """
    
    model_config = ConfigDict(
        # Enable ORM mode for SQLAlchemy model conversion
        from_attributes=True,
        # Allow population by field name and alias
        populate_by_name=True,
        # Validate assignment (useful for updates)
        validate_assignment=True,
        # Use enum values instead of names in JSON
        use_enum_values=True,
        # Custom JSON encoders for common types
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            time: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v) if v else None,
            Decimal: lambda v: float(v) if v else None,
            set: list  # Convert sets to lists for JSON
        },
        # Handle extra fields
        extra='forbid'  # Reject unknown fields
    )
    
    def dict_with_computed(self, **kwargs) -> Dict[str, Any]:
        """
        Export to dictionary including computed properties
        """
        data = self.model_dump(**kwargs)
        
        # Add computed properties if they exist
        for attr_name in dir(self):
            if not attr_name.startswith('_') and hasattr(self.__class__, attr_name):
                attr = getattr(self.__class__, attr_name)
                if isinstance(attr, property):
                    try:
                        data[attr_name] = getattr(self, attr_name)
                    except Exception:
                        # Skip properties that can't be computed
                        pass
        
        return data


class TimestampSchema(BaseSchema):
    """
    Base schema with timestamp fields for auditing
    
    Includes created_at and updated_at fields commonly used across entities
    """
    
    created_at: datetime = Field(
        ..., 
        description="Timestamp when record was created"
    )
    
    updated_at: Optional[datetime] = Field(
        None, 
        description="Timestamp when record was last updated"
    )


class AuditSchema(TimestampSchema):
    """
    Base schema with full audit fields
    
    Includes timestamp fields plus user tracking for comprehensive auditing
    """
    
    created_by: Optional[UUID] = Field(
        None, 
        description="User who created this record"
    )
    
    updated_by: Optional[UUID] = Field(
        None, 
        description="User who last updated this record"
    )


class ArchiveSchema(BaseSchema):
    """
    Base schema with soft delete functionality
    """
    
    archived_at: Optional[datetime] = Field(
        None, 
        description="Timestamp when record was soft deleted"
    )
    
    archived_by: Optional[UUID] = Field(
        None, 
        description="User who archived this record"
    )
    
    @property
    def is_archived(self) -> bool:
        """Check if record is archived"""
        return self.archived_at is not None
    
    @property
    def is_active(self) -> bool:
        """Check if record is active (not archived)"""
        return self.archived_at is None


class FullAuditSchema(AuditSchema, ArchiveSchema):
    """
    Complete audit schema combining timestamps, user tracking, and soft delete
    """
    pass


# =============================================================================
# PAGINATION SCHEMAS
# =============================================================================

class PaginationParams(BaseSchema):
    """
    Standard pagination parameters
    """
    
    page: int = Field(
        default=1, 
        ge=1, 
        description="Page number (1-based)"
    )
    
    page_size: int = Field(
        default=20, 
        ge=1, 
        le=100, 
        description="Number of items per page (max 100)"
    )
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database queries"""
        return self.page_size


class PaginationMetadata(BaseSchema):
    """
    Pagination metadata for responses
    """
    
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    
    @classmethod
    def from_params(
        cls, 
        params: PaginationParams, 
        total_items: int
    ) -> 'PaginationMetadata':
        """Create metadata from pagination params and total count"""
        import math
        
        total_pages = math.ceil(total_items / params.page_size) if total_items > 0 else 0
        
        return cls(
            page=params.page,
            page_size=params.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_previous=params.page > 1
        )


T = TypeVar('T')

class PaginationSchema(BaseSchema, Generic[T]):
    """
    Generic pagination response schema
    """
    
    items: List[T] = Field(..., description="List of items for current page")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")
    
    @classmethod
    def create(
        cls, 
        items: List[T], 
        params: PaginationParams, 
        total_items: int
    ) -> 'PaginationSchema[T]':
        """Create paginated response"""
        return cls(
            items=items,
            pagination=PaginationMetadata.from_params(params, total_items)
        )


# =============================================================================
# COMMON RESPONSE SCHEMAS
# =============================================================================

class SuccessResponse(BaseSchema):
    """
    Standard success response
    """
    
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional response data")


class ErrorResponse(BaseSchema):
    """
    Standard error response
    """
    
    success: bool = Field(default=False, description="Operation success status")
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class ValidationErrorDetail(BaseSchema):
    """
    Validation error detail
    """
    
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Any = Field(None, description="Invalid value")
    code: Optional[str] = Field(None, description="Error code")


class ValidationErrorResponse(ErrorResponse):
    """
    Validation error response with field-specific details
    """
    
    validation_errors: List[ValidationErrorDetail] = Field(
        default_factory=list, 
        description="Field-specific validation errors"
    )


# =============================================================================
# SEARCH AND FILTER SCHEMAS
# =============================================================================

class BaseSearchParams(BaseSchema):
    """
    Base search parameters
    """
    
    search: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100, 
        description="Search term"
    )
    
    sort_by: Optional[str] = Field(
        None, 
        description="Field to sort by"
    )
    
    sort_order: Optional[str] = Field(
        default="asc", 
        patterm="^(asc|desc)$", 
        description="Sort order (asc/desc)"
    )


class DateRangeFilter(BaseSchema):
    """
    Date range filter
    """
    
    start_date: Optional[date] = Field(None, description="Start date (inclusive)")
    end_date: Optional[date] = Field(None, description="End date (inclusive)")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError('end_date must be after start_date')
        return v


class NumericRangeFilter(BaseSchema):
    """
    Numeric range filter
    """
    
    min_value: Optional[Decimal] = Field(None, description="Minimum value (inclusive)")
    max_value: Optional[Decimal] = Field(None, description="Maximum value (inclusive)")
    
    @validator('max_value')
    def validate_numeric_range(cls, v, values):
        min_value = values.get('min_value')
        if min_value is not None and v is not None and v < min_value:
            raise ValueError('max_value must be greater than or equal to min_value')
        return v


# =============================================================================
# BULK OPERATION SCHEMAS
# =============================================================================

class BulkOperationStatus(str, Enum):
    """Status of bulk operation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"


class BulkOperationResult(BaseSchema):
    """
    Result of bulk operations
    """
    
    operation_id: Optional[UUID] = Field(None, description="Operation identifier")
    status: BulkOperationStatus = Field(..., description="Operation status")
    total_requested: int = Field(..., ge=0, description="Total items requested")
    successful: int = Field(..., ge=0, description="Successfully processed items")
    failed: int = Field(..., ge=0, description="Failed items")
    skipped: int = Field(default=0, ge=0, description="Skipped items")
    
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    
    created_ids: List[UUID] = Field(default_factory=list, description="IDs of created items")
    updated_ids: List[UUID] = Field(default_factory=list, description="IDs of updated items")
    
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Operation start time")
    completed_at: Optional[datetime] = Field(None, description="Operation completion time")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_requested == 0:
            return 0.0
        return (self.successful / self.total_requested) * 100
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate operation duration in seconds"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


# =============================================================================
# FILE OPERATION SCHEMAS
# =============================================================================

class FileInfo(BaseSchema):
    """
    File information schema
    """
    
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    file_hash: Optional[str] = Field(None, description="File hash (SHA-256)")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")


class FileUploadResponse(BaseSchema):
    """
    File upload response
    """
    
    file_id: UUID = Field(..., description="Uploaded file identifier")
    file_url: Optional[str] = Field(None, description="File access URL")
    file_info: FileInfo = Field(..., description="File information")


# =============================================================================
# HEALTH CHECK SCHEMAS
# =============================================================================

class ComponentHealth(BaseSchema):
    """
    Health status of individual component
    """
    
    name: str = Field(..., description="Component name")
    status: str = Field(..., description="Health status")
    message: Optional[str] = Field(None, description="Status message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    checked_at: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")


class HealthCheckResponse(BaseSchema):
    """
    Overall health check response
    """
    
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: Optional[str] = Field(None, description="Application version")
    environment: Optional[str] = Field(None, description="Environment name")
    components: List[ComponentHealth] = Field(default_factory=list, description="Component health details")


# =============================================================================
# EXPORT ALL SCHEMAS
# =============================================================================

__all__ = [
    # Base schemas
    'BaseSchema',
    'TimestampSchema', 
    'AuditSchema',
    'ArchiveSchema',
    'FullAuditSchema',
    
    # Pagination schemas
    'PaginationParams',
    'PaginationMetadata',
    'PaginationSchema',
    
    # Response schemas
    'SuccessResponse',
    'ErrorResponse',
    'ValidationErrorDetail',
    'ValidationErrorResponse',
    
    # Search schemas
    'BaseSearchParams',
    'DateRangeFilter',
    'NumericRangeFilter',
    
    # Bulk operation schemas
    'BulkOperationStatus',
    'BulkOperationResult',
    
    # File schemas
    'FileInfo',
    'FileUploadResponse',
    
    # Health check schemas
    'ComponentHealth',
    'HealthCheckResponse'
]