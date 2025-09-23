# app/modules/pricing/product/schemas/product_feature_schema.py

"""
Product Feature Schema

Pydantic schemas for Product Feature validation and serialization.
Handles features, benefits, and coverage options for insurance products.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal


# ================================================================
# ENUMS
# ================================================================

class FeatureType(str, Enum):
    """Feature types enumeration"""
    BASIC = "basic"
    OPTIONAL = "optional"
    RIDER = "rider"
    ADDON = "addon"
    MANDATORY = "mandatory"


class FeatureCategory(str, Enum):
    """Feature category enumeration"""
    MEDICAL = "medical"
    DENTAL = "dental"
    VISION = "vision"
    LIFE = "life"
    DISABILITY = "disability"
    ACCIDENT = "accident"
    CRITICAL_ILLNESS = "critical_illness"
    WELLNESS = "wellness"
    PREVENTIVE = "preventive"
    EMERGENCY = "emergency"
    MATERNITY = "maternity"
    MENTAL_HEALTH = "mental_health"
    OTHER = "other"


class FeatureStatus(str, Enum):
    """Feature status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DEPRECATED = "deprecated"
    SUSPENDED = "suspended"


# ================================================================
# BASE SCHEMAS
# ================================================================

class ProductFeatureBase(BaseModel):
    """Base schema for product features"""
    
    model_config = ConfigDict(from_attributes=True)
    
    feature_code: str = Field(..., min_length=1, max_length=50, description="Unique feature code")
    feature_name: str = Field(..., min_length=1, max_length=200, description="Feature name")
    description: Optional[str] = Field(None, description="Feature description")
    
    feature_type: FeatureType = Field(..., description="Type of feature")
    feature_category: FeatureCategory = Field(..., description="Feature category")
    
    # Coverage Details
    coverage_amount: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Coverage amount"
    )
    coverage_limit: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Maximum coverage limit"
    )
    deductible_amount: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Deductible amount"
    )
    copay_percentage: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=100, 
        decimal_places=2,
        description="Copayment percentage"
    )
    
    # Waiting Periods
    waiting_period_days: Optional[int] = Field(
        None, 
        ge=0,
        description="Waiting period in days"
    )
    benefit_period_days: Optional[int] = Field(
        None, 
        ge=0,
        description="Benefit period in days"
    )
    
    # Eligibility
    min_age: Optional[int] = Field(None, ge=0, le=150, description="Minimum age")
    max_age: Optional[int] = Field(None, ge=0, le=150, description="Maximum age")
    
    # Flags
    is_mandatory: bool = Field(default=False, description="Is feature mandatory")
    is_taxable: bool = Field(default=False, description="Is feature taxable")
    requires_underwriting: bool = Field(default=False, description="Requires underwriting")
    
    @field_validator('feature_code')
    @classmethod
    def validate_feature_code(cls, v: str) -> str:
        """Validate feature code format"""
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError("Feature code can only contain letters, numbers, hyphens, and underscores")
        return v.upper()
    
    @field_validator('max_age')
    @classmethod
    def validate_age_range(cls, v: Optional[int], values) -> Optional[int]:
        """Validate age range"""
        if v is not None and 'min_age' in values.data:
            min_age = values.data.get('min_age')
            if min_age is not None and v < min_age:
                raise ValueError("Maximum age must be greater than or equal to minimum age")
        return v


# ================================================================
# CREATE SCHEMA
# ================================================================

class ProductFeatureCreate(ProductFeatureBase):
    """Schema for creating a product feature"""
    
    product_id: UUID = Field(..., description="Associated product ID")
    
    # Optional pricing
    base_price: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Base price for feature"
    )
    
    # Metadata
    feature_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional feature metadata"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Feature tags"
    )
    
    # Dates
    effective_date: Optional[date] = Field(None, description="Effective date")
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    
    @field_validator('expiry_date')
    @classmethod
    def validate_dates(cls, v: Optional[date], values) -> Optional[date]:
        """Validate date range"""
        if v is not None and 'effective_date' in values.data:
            effective = values.data.get('effective_date')
            if effective is not None and v <= effective:
                raise ValueError("Expiry date must be after effective date")
        return v


# ================================================================
# UPDATE SCHEMA
# ================================================================

class ProductFeatureUpdate(BaseModel):
    """Schema for updating a product feature"""
    
    model_config = ConfigDict(from_attributes=True)
    
    feature_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    feature_type: Optional[FeatureType] = None
    feature_category: Optional[FeatureCategory] = None
    
    # Coverage Details
    coverage_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    coverage_limit: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    deductible_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    copay_percentage: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    
    # Waiting Periods
    waiting_period_days: Optional[int] = Field(None, ge=0)
    benefit_period_days: Optional[int] = Field(None, ge=0)
    
    # Eligibility
    min_age: Optional[int] = Field(None, ge=0, le=150)
    max_age: Optional[int] = Field(None, ge=0, le=150)
    
    # Pricing
    base_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    
    # Flags
    is_mandatory: Optional[bool] = None
    is_taxable: Optional[bool] = None
    requires_underwriting: Optional[bool] = None
    
    # Metadata
    feature_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    # Dates
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    # Status
    status: Optional[FeatureStatus] = None


# ================================================================
# RESPONSE SCHEMAS
# ================================================================

class ProductFeatureResponse(ProductFeatureBase):
    """Response schema for product feature"""
    
    id: UUID = Field(..., description="Feature ID")
    product_id: UUID = Field(..., description="Product ID")
    
    base_price: Optional[Decimal] = Field(None, description="Base price")
    
    feature_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
    
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    status: FeatureStatus = Field(..., description="Feature status")
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool = Field(default=False)


class ProductFeatureListResponse(BaseModel):
    """Response schema for feature list"""
    
    model_config = ConfigDict(from_attributes=True)
    
    features: List[ProductFeatureResponse] = Field(..., description="List of features")
    total_count: int = Field(..., ge=0, description="Total count")
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, le=100, description="Page size")
    total_pages: int = Field(..., ge=0, description="Total pages")


# ================================================================
# FILTER SCHEMAS
# ================================================================

class ProductFeatureFilter(BaseModel):
    """Filter schema for product features"""
    
    model_config = ConfigDict(from_attributes=True)
    
    product_id: Optional[UUID] = None
    feature_type: Optional[FeatureType] = None
    feature_category: Optional[FeatureCategory] = None
    status: Optional[FeatureStatus] = None
    
    is_mandatory: Optional[bool] = None
    is_taxable: Optional[bool] = None
    requires_underwriting: Optional[bool] = None
    
    min_coverage_amount: Optional[Decimal] = Field(None, ge=0)
    max_coverage_amount: Optional[Decimal] = Field(None, ge=0)
    
    search_term: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[List[str]] = None
    
    effective_date_from: Optional[date] = None
    effective_date_to: Optional[date] = None


# ================================================================
# BULK OPERATIONS
# ================================================================

class ProductFeatureBulkCreate(BaseModel):
    """Schema for bulk feature creation"""
    
    model_config = ConfigDict(from_attributes=True)
    
    features: List[ProductFeatureCreate] = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="List of features to create"
    )


class ProductFeatureBulkUpdate(BaseModel):
    """Schema for bulk feature updates"""
    
    model_config = ConfigDict(from_attributes=True)
    
    feature_ids: List[UUID] = Field(..., min_length=1, description="Feature IDs to update")
    updates: ProductFeatureUpdate = Field(..., description="Updates to apply")


# ================================================================
# PRICING SCHEMAS
# ================================================================

class FeaturePricingRequest(BaseModel):
    """Request schema for feature pricing calculation"""
    
    model_config = ConfigDict(from_attributes=True)
    
    feature_id: UUID = Field(..., description="Feature ID")
    age: Optional[int] = Field(None, ge=0, le=150, description="Insured age")
    coverage_amount: Optional[Decimal] = Field(None, ge=0, description="Coverage amount")
    apply_discounts: bool = Field(default=True, description="Apply discounts")
    apply_taxes: bool = Field(default=True, description="Apply taxes")


class FeaturePricingResponse(BaseModel):
    """Response schema for feature pricing"""
    
    model_config = ConfigDict(from_attributes=True)
    
    feature_id: UUID
    base_price: Decimal
    adjusted_price: Decimal
    discount_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    final_price: Decimal
    currency: str = Field(default="USD")
    calculation_details: Optional[Dict[str, Any]] = None


# ================================================================
# END OF SCHEMA
# ================================================================