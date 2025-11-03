# app/modules/pricing/product/schemas/product_catalog_schema.py

"""
Product Catalog Schema

Pydantic schemas for Product Catalog validation and serialization.
Handles request/response validation for product-related operations.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from enum import Enum


# ================================================================
# ENUMS (Matching Model Enums)
# ================================================================

class ProductCategoryEnum(str, Enum):
    """Product category enumeration"""
    MEDICAL = "medical"
    MOTOR = "motor"
    LIFE = "life"
    TRAVEL = "travel"
    PROPERTY = "property"
    LIABILITY = "liability"
    MARINE = "marine"
    AVIATION = "aviation"
    OTHER = "other"


class ProductTypeEnum(str, Enum):
    """Product type enumeration"""
    INDIVIDUAL = "individual"
    GROUP = "group"
    FAMILY = "family"
    CORPORATE = "corporate"
    SME = "sme"
    GOVERNMENT = "government"


class ProductStatusEnum(str, Enum):
    """Product lifecycle status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISCONTINUED = "discontinued"
    ARCHIVED = "archived"


class DistributionChannelEnum(str, Enum):
    """Distribution channel enumeration"""
    DIRECT = "direct"
    BROKER = "broker"
    AGENT = "agent"
    BANCASSURANCE = "bancassurance"
    DIGITAL = "digital"
    PARTNERSHIP = "partnership"
    AGGREGATOR = "aggregator"


# ================================================================
# BASE SCHEMAS
# ================================================================

class ProductCatalogBase(BaseModel):
    """Base schema for Product Catalog"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
            UUID: lambda v: str(v)
        }
    )
    
    # Basic Information
    product_code: str = Field(..., min_length=1, max_length=50, description="Unique product identifier code")
    product_name: str = Field(..., min_length=1, max_length=100, description="Product display name")
    product_name_ar: Optional[str] = Field(None, max_length=100, description="Product name in Arabic")
    product_category: ProductCategoryEnum = Field(..., description="Product category")
    product_type: ProductTypeEnum = Field(..., description="Product type")
    
    # Description
    description: Optional[str] = Field(None, description="Detailed product description")
    description_ar: Optional[str] = Field(None, description="Product description in Arabic")
    short_description: Optional[str] = Field(None, max_length=500, description="Brief product summary")
    key_features: Optional[Dict[str, Any]] = Field(None, description="Key product features")
    
    # Market Configuration
    target_market: Optional[Dict[str, Any]] = Field(None, description="Target market segments")
    distribution_channels: Optional[List[str]] = Field(None, description="Allowed distribution channels")
    geographic_coverage: Optional[Dict[str, Any]] = Field(None, description="Geographic coverage")
    
    # Product Rules
    min_entry_age: Optional[int] = Field(None, ge=0, le=150, description="Minimum entry age")
    max_entry_age: Optional[int] = Field(None, ge=0, le=150, description="Maximum entry age")
    min_coverage_amount: Optional[int] = Field(None, ge=0, description="Minimum coverage amount")
    max_coverage_amount: Optional[int] = Field(None, ge=0, description="Maximum coverage amount")
    waiting_period_days: int = Field(default=0, ge=0, description="Waiting period in days")
    
    @field_validator('product_code')
    @classmethod
    def validate_product_code(cls, v: str) -> str:
        """Validate product code format"""
        if not v or not v.strip():
            raise ValueError("Product code cannot be empty")
        # Ensure alphanumeric and certain special characters
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError("Product code can only contain letters, numbers, hyphens, and underscores")
        return v.upper()
    
    @model_validator(mode='after')
    def validate_age_range(self):
        """Validate age range consistency"""
        if self.min_entry_age and self.max_entry_age:
            if self.min_entry_age > self.max_entry_age:
                raise ValueError("Minimum entry age cannot be greater than maximum entry age")
        return self
    
    @model_validator(mode='after')
    def validate_coverage_amount_range(self):
        """Validate coverage amount range"""
        if self.min_coverage_amount and self.max_coverage_amount:
            if self.min_coverage_amount > self.max_coverage_amount:
                raise ValueError("Minimum coverage amount cannot be greater than maximum coverage amount")
        return self


# ================================================================
# CREATE SCHEMA
# ================================================================

class ProductCatalogCreate(ProductCatalogBase):
    """Schema for creating a Product Catalog"""
    
    # Optional fields with defaults for creation
    product_status: ProductStatusEnum = Field(default=ProductStatusEnum.DRAFT, description="Initial product status")
    is_active: bool = Field(default=False, description="Whether product is active")
    is_new_business_allowed: bool = Field(default=True, description="Whether new policies allowed")
    is_renewal_allowed: bool = Field(default=True, description="Whether renewals allowed")
    
    # Regulatory & Compliance
    regulatory_approvals: Optional[Dict[str, Any]] = Field(None, description="Regulatory approvals")
    regulatory_code: Optional[str] = Field(None, max_length=100, description="Regulatory code")
    compliance_requirements: Optional[Dict[str, Any]] = Field(None, description="Compliance requirements")
    license_number: Optional[str] = Field(None, max_length=100, description="License number")
    
    # Pricing & Underwriting
    underwriting_rules: Optional[Dict[str, Any]] = Field(None, description="Underwriting rules")
    underwriting_guidelines: Optional[str] = Field(None, description="Underwriting guidelines")
    risk_assessment_required: bool = Field(default=True, description="Risk assessment required")
    medical_underwriting_required: bool = Field(default=False, description="Medical underwriting required")
    
    # Terms & Conditions
    policy_terms: Optional[Dict[str, Any]] = Field(None, description="Policy terms")
    coverage_options: Optional[Dict[str, Any]] = Field(None, description="Coverage options")
    exclusions: Optional[Dict[str, Any]] = Field(None, description="Exclusions")
    riders_available: Optional[Dict[str, Any]] = Field(None, description="Available riders")
    
    # Commission & Incentives
    commission_structure: Optional[Dict[str, Any]] = Field(None, description="Commission structure")
    incentive_programs: Optional[Dict[str, Any]] = Field(None, description="Incentive programs")
    referral_fee_structure: Optional[Dict[str, Any]] = Field(None, description="Referral fees")
    
    # Dates
    launch_date: Optional[date] = Field(None, description="Product launch date")
    sunset_date: Optional[date] = Field(None, description="Product sunset date")
    
    # Additional
    product_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Product configuration")
    feature_flags: Optional[Dict[str, Any]] = Field(None, description="Feature toggles")
    tags: Optional[List[str]] = Field(None, description="Product tags")


# ================================================================
# UPDATE SCHEMA
# ================================================================

class ProductCatalogUpdate(BaseModel):
    """Schema for updating a Product Catalog"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # All fields optional for partial updates
    product_name: Optional[str] = Field(None, min_length=1, max_length=100)
    product_name_ar: Optional[str] = Field(None, max_length=100)
    product_category: Optional[ProductCategoryEnum] = None
    product_type: Optional[ProductTypeEnum] = None
    
    description: Optional[str] = None
    description_ar: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    key_features: Optional[Dict[str, Any]] = None
    
    target_market: Optional[Dict[str, Any]] = None
    distribution_channels: Optional[List[str]] = None
    geographic_coverage: Optional[Dict[str, Any]] = None
    
    min_entry_age: Optional[int] = Field(None, ge=0, le=150)
    max_entry_age: Optional[int] = Field(None, ge=0, le=150)
    min_coverage_amount: Optional[int] = Field(None, ge=0)
    max_coverage_amount: Optional[int] = Field(None, ge=0)
    waiting_period_days: Optional[int] = Field(None, ge=0)
    
    product_status: Optional[ProductStatusEnum] = None
    is_active: Optional[bool] = None
    is_new_business_allowed: Optional[bool] = None
    is_renewal_allowed: Optional[bool] = None
    
    regulatory_approvals: Optional[Dict[str, Any]] = None
    regulatory_code: Optional[str] = Field(None, max_length=100)
    compliance_requirements: Optional[Dict[str, Any]] = None
    license_number: Optional[str] = Field(None, max_length=100)
    
    underwriting_rules: Optional[Dict[str, Any]] = None
    underwriting_guidelines: Optional[str] = None
    risk_assessment_required: Optional[bool] = None
    medical_underwriting_required: Optional[bool] = None
    
    policy_terms: Optional[Dict[str, Any]] = None
    coverage_options: Optional[Dict[str, Any]] = None
    exclusions: Optional[Dict[str, Any]] = None
    riders_available: Optional[Dict[str, Any]] = None
    
    commission_structure: Optional[Dict[str, Any]] = None
    incentive_programs: Optional[Dict[str, Any]] = None
    referral_fee_structure: Optional[Dict[str, Any]] = None
    
    launch_date: Optional[date] = None
    sunset_date: Optional[date] = None
    
    product_metadata: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    feature_flags: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    @model_validator(mode='after')
    def validate_age_range(self):
        """Validate age range consistency"""
        if self.min_entry_age is not None and self.max_entry_age is not None:
            if self.min_entry_age > self.max_entry_age:
                raise ValueError("Minimum entry age cannot be greater than maximum entry age")
        return self
    
    @model_validator(mode='after')
    def validate_coverage_amount_range(self):
        """Validate coverage amount range"""
        if self.min_coverage_amount is not None and self.max_coverage_amount is not None:
            if self.min_coverage_amount > self.max_coverage_amount:
                raise ValueError("Minimum coverage amount cannot be greater than maximum coverage amount")
        return self


# ================================================================
# RESPONSE SCHEMAS
# ================================================================

class ProductCatalogResponse(ProductCatalogBase):
    """Schema for Product Catalog responses"""
    
    id: UUID = Field(..., description="Product unique identifier")
    product_status: ProductStatusEnum = Field(..., description="Current product status")
    is_active: bool = Field(..., description="Whether product is active")
    is_new_business_allowed: bool = Field(..., description="Whether new business allowed")
    is_renewal_allowed: bool = Field(..., description="Whether renewals allowed")
    
    version: str = Field(default="1.0.0", description="Product version")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="Creator user ID")
    updated_by: Optional[UUID] = Field(None, description="Last updater user ID")
    
    # Additional response fields
    plans_count: Optional[int] = Field(None, description="Number of associated plans")
    features_count: Optional[int] = Field(None, description="Number of associated features")


class ProductCatalogSummary(BaseModel):
    """Summary schema for Product Catalog listings"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Product unique identifier")
    product_code: str = Field(..., description="Product code")
    product_name: str = Field(..., description="Product name")
    product_category: ProductCategoryEnum = Field(..., description="Product category")
    product_type: ProductTypeEnum = Field(..., description="Product type")
    product_status: ProductStatusEnum = Field(..., description="Product status")
    is_active: bool = Field(..., description="Whether product is active")
    launch_date: Optional[date] = Field(None, description="Launch date")
    created_at: datetime = Field(..., description="Creation timestamp")



class ProductCatalogListResponse(BaseModel):
    """Response schema for paginated product list"""
    
    model_config = ConfigDict(from_attributes=True)
    
    products: List[ProductCatalogResponse] = Field(..., description="List of products")
    total_count: int = Field(..., ge=0, description="Total number of products")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    
# ================================================================
# QUERY SCHEMAS
# ================================================================

class ProductCatalogQuery(BaseModel):
    """Schema for querying Product Catalogs"""
    
    model_config = ConfigDict(from_attributes=True)
    
    product_category: Optional[ProductCategoryEnum] = None
    product_type: Optional[ProductTypeEnum] = None
    product_status: Optional[ProductStatusEnum] = None
    is_active: Optional[bool] = None
    is_new_business_allowed: Optional[bool] = None
    distribution_channel: Optional[str] = None
    search_term: Optional[str] = Field(None, description="Search in name and description")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    # Sorting
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


# ================================================================
# STATUS UPDATE SCHEMA
# ================================================================

class ProductCatalogStatusUpdate(BaseModel):
    """Schema for updating product status"""
    
    model_config = ConfigDict(from_attributes=True)
    
    status: ProductStatusEnum = Field(..., description="New status")
    reason: Optional[str] = Field(None, description="Reason for status change")
    effective_date: Optional[date] = Field(None, description="When status change is effective")
    notes: Optional[str] = Field(None, description="Additional notes")


# ================================================================
# BULK OPERATIONS
# ================================================================

class ProductCatalogBulkCreate(BaseModel):
    """Schema for bulk product creation"""
    
    model_config = ConfigDict(from_attributes=True)
    
    products: List[ProductCatalogCreate] = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="List of products to create"
    )


class ProductCatalogBulkUpdate(BaseModel):
    """Schema for bulk product updates"""
    
    model_config = ConfigDict(from_attributes=True)
    
    product_ids: List[UUID] = Field(..., min_length=1, description="Product IDs to update")
    updates: ProductCatalogUpdate = Field(..., description="Updates to apply")

# ================================================================
# FILTER SCHEMA
# ================================================================

class ProductCatalogFilter(BaseModel):
    """Filter schema for product catalog queries"""
    
    model_config = ConfigDict(from_attributes=True)
    
    product_type: Optional[ProductTypeEnum] = None
    product_category: Optional[ProductCategoryEnum] = None
    status: Optional[ProductStatusEnum] = None
    is_active: Optional[bool] = None
    requires_underwriting: Optional[bool] = None
    
    min_age_limit: Optional[int] = Field(None, ge=0)
    max_age_limit: Optional[int] = Field(None, le=150)
    
    search_term: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[List[str]] = None
    
    effective_date_from: Optional[date] = None
    effective_date_to: Optional[date] = None
    expiry_date_from: Optional[date] = None
    expiry_date_to: Optional[date] = None


# ================================================================
# CLONE SCHEMA
# ================================================================


class ProductCatalogClone(BaseModel):
    """Schema for cloning a product"""
    
    model_config = ConfigDict(from_attributes=True)
    
    source_product_id: UUID = Field(..., description="Source product ID to clone from")
    new_product_code: str = Field(..., min_length=1, max_length=50, description="New product code")
    new_product_name: str = Field(..., min_length=1, max_length=100, description="New product name")
    include_features: bool = Field(default=True, description="Clone features as well")
    include_commission: bool = Field(default=True, description="Clone commission structure")
    include_underwriting: bool = Field(default=True, description="Clone underwriting rules")
    
    @field_validator('new_product_code')
    @classmethod
    def validate_product_code(cls, v: str) -> str:
        """Validate product code format"""
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError("Product code can only contain letters, numbers, hyphens, and underscores")
        return v.upper()


# ================================================================
# END OF SCHEMA
# ================================================================