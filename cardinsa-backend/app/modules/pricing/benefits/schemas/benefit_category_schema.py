# app/modules/pricing/benefits/schemas/benefit_category_schema.py

"""
Benefit Category Schema

Pydantic schemas for Benefit Category validation and serialization.
Handles hierarchical category structures and multilingual support.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from enum import Enum


# ================================================================
# ENUMS (Matching Model Enums)
# ================================================================

class BenefitCategoryStatus(str, Enum):
    """Benefit category status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DISCONTINUED = "discontinued"


class BenefitCategoryType(str, Enum):
    """Benefit category type enumeration"""
    MEDICAL = "medical"
    DENTAL = "dental"
    VISION = "vision"
    WELLNESS = "wellness"
    MATERNITY = "maternity"
    EMERGENCY = "emergency"
    TRAVEL = "travel"
    OTHER = "other"


# ================================================================
# BASE SCHEMAS
# ================================================================

class BenefitCategoryBase(BaseModel):
    """Base schema for Benefit Category"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )
    
    # Basic Information
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="Unique category code")
    name: str = Field(..., min_length=1, max_length=200, description="Category name")
    name_ar: Optional[str] = Field(None, max_length=200, description="Category name in Arabic")
    
    description: Optional[str] = Field(None, description="Category description")
    description_ar: Optional[str] = Field(None, description="Category description in Arabic")
    
    # Hierarchy
    parent_id: Optional[UUID] = Field(None, description="Parent category ID")
    
    # Organization
    display_order: int = Field(default=0, description="Display order")
    category_type: BenefitCategoryType = Field(default=BenefitCategoryType.OTHER, description="Category type")
    
    # Status
    status: BenefitCategoryStatus = Field(default=BenefitCategoryStatus.ACTIVE, description="Category status")
    is_active: bool = Field(default=True, description="Whether category is active")
    
    # Dates
    effective_date: Optional[date] = Field(None, description="When category becomes effective")
    expiry_date: Optional[date] = Field(None, description="When category expires")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v and not v.strip():
            raise ValueError('Category name cannot be empty')
        return v.strip() if v else v
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if v and not v.strip():
            raise ValueError('Category code cannot be empty')
        if v:
            v = v.strip().upper()
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Category code must contain only alphanumeric characters, underscores, and hyphens')
        return v
    
    @model_validator(mode='after')
    def validate_dates(self):
        if self.effective_date and self.expiry_date:
            if self.expiry_date <= self.effective_date:
                raise ValueError('Expiry date must be after effective date')
        return self


# ================================================================
# CREATE SCHEMA
# ================================================================

class BenefitCategoryCreate(BenefitCategoryBase):
    """Schema for creating a new benefit category"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "MEDICAL_BASIC",
                "name": "Basic Medical",
                "name_ar": "الطبي الأساسي",
                "description": "Basic medical coverage category",
                "category_type": "medical",
                "display_order": 10,
                "is_active": True
            }
        }
    )


# ================================================================
# UPDATE SCHEMA
# ================================================================

class BenefitCategoryUpdate(BaseModel):
    """Schema for updating an existing benefit category"""
    
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Category name")
    name_ar: Optional[str] = Field(None, max_length=200, description="Category name in Arabic")
    
    description: Optional[str] = Field(None, description="Category description")
    description_ar: Optional[str] = Field(None, description="Category description in Arabic")
    
    parent_id: Optional[UUID] = Field(None, description="Parent category ID")
    display_order: Optional[int] = Field(None, description="Display order")
    category_type: Optional[BenefitCategoryType] = Field(None, description="Category type")
    
    status: Optional[BenefitCategoryStatus] = Field(None, description="Category status")
    is_active: Optional[bool] = Field(None, description="Whether category is active")
    
    effective_date: Optional[date] = Field(None, description="When category becomes effective")
    expiry_date: Optional[date] = Field(None, description="When category expires")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Category name cannot be empty')
        return v.strip() if v else v


# ================================================================
# RESPONSE SCHEMAS
# ================================================================

class BenefitCategoryResponse(BenefitCategoryBase):
    """Response schema for benefit category"""
    
    id: UUID = Field(..., description="Category ID")
    
    # Audit fields
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="Creator user ID")
    updated_by: Optional[UUID] = Field(None, description="Last updater user ID")


class BenefitCategoryWithChildren(BenefitCategoryResponse):
    """Response schema for benefit category with children"""
    
    children: List['BenefitCategoryResponse'] = Field(default_factory=list, description="Child categories")
    children_count: int = Field(default=0, description="Number of child categories")


class BenefitCategoryHierarchy(BenefitCategoryResponse):
    """Response schema for benefit category hierarchy"""
    
    hierarchy_path: List['BenefitCategoryResponse'] = Field(default_factory=list, description="Full hierarchy path")
    depth_level: int = Field(default=0, description="Depth level in hierarchy")


# ================================================================
# SUMMARY SCHEMAS
# ================================================================

class BenefitCategorySummary(BaseModel):
    """Lightweight benefit category summary"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    code: Optional[str]
    name: str
    category_type: BenefitCategoryType
    is_active: bool
    children_count: Optional[int] = None


# ================================================================
# FILTER AND QUERY SCHEMAS
# ================================================================

class BenefitCategoryFilter(BaseModel):
    """Filter schema for benefit categories"""
    
    model_config = ConfigDict(from_attributes=True)
    
    category_type: Optional[BenefitCategoryType] = None
    status: Optional[BenefitCategoryStatus] = None
    is_active: Optional[bool] = None
    parent_id: Optional[UUID] = None
    has_children: Optional[bool] = None
    
    search_term: Optional[str] = Field(None, description="Search in name and description")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    # Sorting
    sort_by: str = Field(default="display_order", description="Sort field")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")


class BenefitCategoryQuery(BaseModel):
    """Schema for querying benefit categories"""
    
    model_config = ConfigDict(from_attributes=True)
    
    category_type: Optional[BenefitCategoryType] = None
    status: Optional[BenefitCategoryStatus] = None
    is_active: Optional[bool] = None
    parent_id: Optional[UUID] = None
    
    # Text search
    search_term: Optional[str] = Field(None, description="Search term for name/description")
    
    # Hierarchy options
    include_children: bool = Field(default=False, description="Include child categories")
    include_hierarchy: bool = Field(default=False, description="Include full hierarchy path")
    root_only: bool = Field(default=False, description="Return only root categories")


# ================================================================
# BULK OPERATIONS
# ================================================================

class BenefitCategoryBulkCreate(BaseModel):
    """Schema for bulk category creation"""
    
    model_config = ConfigDict(from_attributes=True)
    
    categories: List[BenefitCategoryCreate] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of categories to create"
    )


class BenefitCategoryBulkUpdate(BaseModel):
    """Schema for bulk category updates"""
    
    model_config = ConfigDict(from_attributes=True)
    
    category_ids: List[UUID] = Field(..., min_length=1, description="Category IDs to update")
    updates: BenefitCategoryUpdate = Field(..., description="Updates to apply")


# ================================================================
# STATUS UPDATE SCHEMA
# ================================================================

class BenefitCategoryStatusUpdate(BaseModel):
    """Schema for updating category status"""
    
    model_config = ConfigDict(from_attributes=True)
    
    status: BenefitCategoryStatus = Field(..., description="New status")
    is_active: Optional[bool] = Field(None, description="Active flag")
    reason: Optional[str] = Field(None, description="Reason for status change")
    effective_date: Optional[date] = Field(None, description="When status change is effective")


# ================================================================
# TREE STRUCTURE SCHEMAS
# ================================================================

class BenefitCategoryTreeNode(BaseModel):
    """Schema for category tree node"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    code: Optional[str]
    name: str
    category_type: BenefitCategoryType
    display_order: int
    is_active: bool
    children: List['BenefitCategoryTreeNode'] = Field(default_factory=list)


class BenefitCategoryTree(BaseModel):
    """Schema for complete category tree"""
    
    model_config = ConfigDict(from_attributes=True)
    
    root_categories: List[BenefitCategoryTreeNode] = Field(default_factory=list)
    total_categories: int = Field(default=0)
    active_categories: int = Field(default=0)
    max_depth: int = Field(default=0)


# ================================================================
# STATISTICS SCHEMA
# ================================================================

class BenefitCategoryStats(BaseModel):
    """Schema for category statistics"""
    
    model_config = ConfigDict(from_attributes=True)
    
    total_categories: int = Field(default=0)
    active_categories: int = Field(default=0)
    inactive_categories: int = Field(default=0)
    root_categories: int = Field(default=0)
    categories_by_type: Dict[str, int] = Field(default_factory=dict)
    max_hierarchy_depth: int = Field(default=0)
    
    created_this_month: int = Field(default=0)
    updated_this_month: int = Field(default=0)


# ================================================================
# LIST RESPONSE SCHEMAS
# ================================================================

class BenefitCategoryListResponse(BaseModel):
    """Response schema for category lists"""
    
    model_config = ConfigDict(from_attributes=True)
    
    categories: List[BenefitCategoryResponse] = Field(default_factory=list)
    total_count: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(default=20)
    total_pages: int = Field(default=0)
    has_next: bool = Field(default=False)
    has_previous: bool = Field(default=False)


class BenefitCategorySummaryListResponse(BaseModel):
    """Response schema for category summary lists"""
    
    model_config = ConfigDict(from_attributes=True)
    
    categories: List[BenefitCategorySummary] = Field(default_factory=list)
    total_count: int = Field(default=0)


# ================================================================
# MISSING SCHEMAS (Add these to match your route imports)
# ================================================================

class BenefitCategoryTree(BaseModel):
    """Schema for benefit category tree structure"""
    
    model_config = ConfigDict(from_attributes=True)
    
    root_categories: List[BenefitCategoryTreeNode] = Field(default_factory=list)
    total_categories: int = Field(default=0)
    active_categories: int = Field(default=0)
    max_depth: int = Field(default=0)


class CategoryStatsResponse(BaseModel):
    """Schema for category statistics response"""
    
    model_config = ConfigDict(from_attributes=True)
    
    total_categories: int = Field(default=0)
    active_categories: int = Field(default=0)
    inactive_categories: int = Field(default=0)
    root_categories: int = Field(default=0)
    categories_by_type: Dict[str, int] = Field(default_factory=dict)
    max_hierarchy_depth: int = Field(default=0)
    created_this_month: int = Field(default=0)
    updated_this_month: int = Field(default=0)


class CategorySearchFilter(BaseModel):
    """Schema for category search filtering"""
    
    model_config = ConfigDict(from_attributes=True)
    
    search_term: Optional[str] = Field(None, description="Search term")
    category_type: Optional[BenefitCategoryType] = None
    status: Optional[BenefitCategoryStatus] = None
    is_active: Optional[bool] = None
    parent_id: Optional[UUID] = None


class CategoryMoveRequest(BaseModel):
    """Schema for moving category to new parent"""
    
    model_config = ConfigDict(from_attributes=True)
    
    category_id: UUID = Field(..., description="Category to move")
    new_parent_id: Optional[UUID] = Field(None, description="New parent category ID")
    reason: Optional[str] = Field(None, description="Reason for move")


class CategoryReorderRequest(BaseModel):
    """Schema for reordering categories"""
    
    model_config = ConfigDict(from_attributes=True)
    
    category_orders: List[Dict[str, Any]] = Field(
        ..., 
        description="List of {id: UUID, display_order: int}"
    )


class BulkCategoryOperation(BaseModel):
    """Schema for bulk category operations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    operation: str = Field(..., description="Operation type (activate, deactivate, delete)")
    category_ids: List[UUID] = Field(..., min_length=1, description="Category IDs to operate on")
    reason: Optional[str] = Field(None, description="Reason for operation")


class CategoryExportRequest(BaseModel):
    """Schema for category export requests"""
    
    model_config = ConfigDict(from_attributes=True)
    
    format: str = Field(default="csv", description="Export format (csv, xlsx, json)")
    include_inactive: bool = Field(default=False, description="Include inactive categories")
    include_hierarchy: bool = Field(default=True, description="Include hierarchy information")
    filters: Optional[CategorySearchFilter] = None


class CategoryImportRequest(BaseModel):
    """Schema for category import requests"""
    
    model_config = ConfigDict(from_attributes=True)
    
    file_data: str = Field(..., description="Base64 encoded file data")
    file_format: str = Field(default="csv", description="File format")
    update_existing: bool = Field(default=False, description="Update existing categories")
    dry_run: bool = Field(default=True, description="Perform validation only")


# ================================================================
# ALIASES FOR BACKWARD COMPATIBILITY
# ================================================================

# Add these aliases to match your route imports
CategoryTreeResponse = BenefitCategoryTree
CategoryStatsResponse = CategoryStatsResponse  # Already defined above
CategorySearchFilter = CategorySearchFilter    # Already defined above
CategoryMoveRequest = CategoryMoveRequest      # Already defined above
CategoryReorderRequest = CategoryReorderRequest # Already defined above
BulkCategoryOperation = BulkCategoryOperation  # Already defined above
CategoryExportRequest = CategoryExportRequest   # Already defined above
CategoryImportRequest = CategoryImportRequest   # Already defined above

# Fix forward references
BenefitCategoryWithChildren.model_rebuild()
BenefitCategoryHierarchy.model_rebuild()
BenefitCategoryTreeNode.model_rebuild()