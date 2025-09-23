# app/modules/pricing/product/schemas/plan_type_schema.py

"""
Plan Type Schema

Pydantic schemas for Plan Type validation and serialization.
Handles insurance plan configurations and tier management.
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

class PlanTier(str, Enum):
    """Plan tier enumeration"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class PlanCategory(str, Enum):
    """Plan category enumeration"""
    INDIVIDUAL = "individual"
    FAMILY = "family"
    GROUP = "group"
    CORPORATE = "corporate"
    GOVERNMENT = "government"
    SME = "sme"
    STUDENT = "student"
    SENIOR = "senior"
    SPECIAL = "special"


class PlanStatus(str, Enum):
    """Plan status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    DISCONTINUED = "discontinued"
    DRAFT = "draft"


class NetworkType(str, Enum):
    """Network type enumeration"""
    PPO = "ppo"
    HMO = "hmo"
    EPO = "epo"
    POS = "pos"
    HDHP = "hdhp"
    INDEMNITY = "indemnity"
    EXCLUSIVE = "exclusive"
    OPEN = "open"


# ================================================================
# BASE SCHEMAS
# ================================================================

class PlanTypeBase(BaseModel):
    """Base schema for plan types"""
    
    model_config = ConfigDict(from_attributes=True)
    
    plan_code: str = Field(..., min_length=1, max_length=50, description="Unique plan code")
    plan_name: str = Field(..., min_length=1, max_length=200, description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    
    plan_tier: PlanTier = Field(..., description="Plan tier level")
    plan_category: PlanCategory = Field(..., description="Plan category")
    network_type: Optional[NetworkType] = Field(None, description="Network type")
    
    # Coverage Limits
    annual_limit: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Annual coverage limit"
    )
    lifetime_limit: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Lifetime coverage limit"
    )
    out_of_pocket_max: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Out of pocket maximum"
    )
    
    # Deductibles
    individual_deductible: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Individual deductible"
    )
    family_deductible: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Family deductible"
    )
    
    # Member Limits
    min_members: Optional[int] = Field(None, ge=1, description="Minimum members")
    max_members: Optional[int] = Field(None, ge=1, description="Maximum members")
    max_dependents: Optional[int] = Field(None, ge=0, description="Maximum dependents")
    
    # Age Limits
    min_enrollment_age: Optional[int] = Field(None, ge=0, le=150, description="Minimum enrollment age")
    max_enrollment_age: Optional[int] = Field(None, ge=0, le=150, description="Maximum enrollment age")
    
    # Flags
    is_renewable: bool = Field(default=True, description="Is plan renewable")
    requires_medical_exam: bool = Field(default=False, description="Requires medical exam")
    allows_dependents: bool = Field(default=True, description="Allows dependents")
    international_coverage: bool = Field(default=False, description="International coverage")
    
    @field_validator('plan_code')
    @classmethod
    def validate_plan_code(cls, v: str) -> str:
        """Validate plan code format"""
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError("Plan code can only contain letters, numbers, hyphens, and underscores")
        return v.upper()
    
    @field_validator('max_members')
    @classmethod
    def validate_member_limits(cls, v: Optional[int], values) -> Optional[int]:
        """Validate member limits"""
        if v is not None and 'min_members' in values.data:
            min_members = values.data.get('min_members')
            if min_members is not None and v < min_members:
                raise ValueError("Maximum members must be greater than or equal to minimum members")
        return v
    
    @field_validator('max_enrollment_age')
    @classmethod
    def validate_age_limits(cls, v: Optional[int], values) -> Optional[int]:
        """Validate age limits"""
        if v is not None and 'min_enrollment_age' in values.data:
            min_age = values.data.get('min_enrollment_age')
            if min_age is not None and v < min_age:
                raise ValueError("Maximum enrollment age must be greater than or equal to minimum enrollment age")
        return v


# ================================================================
# CREATE SCHEMA
# ================================================================

class PlanTypeCreate(PlanTypeBase):
    """Schema for creating a plan type"""
    
    product_id: UUID = Field(..., description="Associated product ID")
    
    # Pricing
    base_premium: Decimal = Field(..., ge=0, decimal_places=2, description="Base premium amount")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="Currency code")
    
    # Payment Terms
    payment_frequency: Optional[str] = Field(
        default="monthly",
        pattern="^(monthly|quarterly|semi-annual|annual)$",
        description="Payment frequency"
    )
    grace_period_days: Optional[int] = Field(
        default=30,
        ge=0,
        description="Grace period in days"
    )
    
    # Waiting Periods
    general_waiting_period: Optional[int] = Field(
        default=0,
        ge=0,
        description="General waiting period in days"
    )
    pre_existing_waiting_period: Optional[int] = Field(
        default=0,
        ge=0,
        description="Pre-existing condition waiting period in days"
    )
    
    # Metadata
    plan_type_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional plan metadata"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Plan tags"
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

class PlanTypeUpdate(BaseModel):
    """Schema for updating a plan type"""
    
    model_config = ConfigDict(from_attributes=True)
    
    plan_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    plan_tier: Optional[PlanTier] = None
    plan_category: Optional[PlanCategory] = None
    network_type: Optional[NetworkType] = None
    
    # Coverage Limits
    annual_limit: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    lifetime_limit: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    out_of_pocket_max: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    
    # Deductibles
    individual_deductible: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    family_deductible: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    
    # Member Limits
    min_members: Optional[int] = Field(None, ge=1)
    max_members: Optional[int] = Field(None, ge=1)
    max_dependents: Optional[int] = Field(None, ge=0)
    
    # Age Limits
    min_enrollment_age: Optional[int] = Field(None, ge=0, le=150)
    max_enrollment_age: Optional[int] = Field(None, ge=0, le=150)
    
    # Pricing
    base_premium: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    
    # Payment Terms
    payment_frequency: Optional[str] = Field(
        None,
        pattern="^(monthly|quarterly|semi-annual|annual)$"
    )
    grace_period_days: Optional[int] = Field(None, ge=0)
    
    # Waiting Periods
    general_waiting_period: Optional[int] = Field(None, ge=0)
    pre_existing_waiting_period: Optional[int] = Field(None, ge=0)
    
    # Flags
    is_renewable: Optional[bool] = None
    requires_medical_exam: Optional[bool] = None
    allows_dependents: Optional[bool] = None
    international_coverage: Optional[bool] = None
    
    # Metadata
    plan_type_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    # Dates
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    # Status
    status: Optional[PlanStatus] = None


# ================================================================
# RESPONSE SCHEMAS
# ================================================================

class PlanTypeResponse(PlanTypeBase):
    """Response schema for plan type"""
    
    id: UUID = Field(..., description="Plan type ID")
    product_id: UUID = Field(..., description="Product ID")
    
    base_premium: Decimal = Field(..., description="Base premium")
    currency: str = Field(..., description="Currency code")
    
    payment_frequency: str = Field(..., description="Payment frequency")
    grace_period_days: int = Field(..., description="Grace period")
    
    general_waiting_period: int = Field(..., description="General waiting period")
    pre_existing_waiting_period: int = Field(..., description="Pre-existing waiting period")
    
    plan_type_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
    
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    status: PlanStatus = Field(..., description="Plan status")
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool = Field(default=False)


class PlanTypeListResponse(BaseModel):
    """Response schema for plan type list"""
    
    model_config = ConfigDict(from_attributes=True)
    
    plans: List[PlanTypeResponse] = Field(..., description="List of plan types")
    total_count: int = Field(..., ge=0, description="Total count")
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, le=100, description="Page size")
    total_pages: int = Field(..., ge=0, description="Total pages")


# ================================================================
# FILTER SCHEMAS
# ================================================================

class PlanTypeFilter(BaseModel):
    """Filter schema for plan types"""
    
    model_config = ConfigDict(from_attributes=True)
    
    product_id: Optional[UUID] = None
    plan_tier: Optional[PlanTier] = None
    plan_category: Optional[PlanCategory] = None
    network_type: Optional[NetworkType] = None
    status: Optional[PlanStatus] = None
    
    is_renewable: Optional[bool] = None
    requires_medical_exam: Optional[bool] = None
    allows_dependents: Optional[bool] = None
    international_coverage: Optional[bool] = None
    
    min_premium: Optional[Decimal] = Field(None, ge=0)
    max_premium: Optional[Decimal] = Field(None, ge=0)
    
    min_deductible: Optional[Decimal] = Field(None, ge=0)
    max_deductible: Optional[Decimal] = Field(None, ge=0)
    
    search_term: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[List[str]] = None
    
    effective_date_from: Optional[date] = None
    effective_date_to: Optional[date] = None


# ================================================================
# COMPARISON SCHEMAS
# ================================================================

class PlanComparison(BaseModel):
    """Schema for plan comparison"""
    
    model_config = ConfigDict(from_attributes=True)
    
    plan_ids: List[UUID] = Field(
        ..., 
        min_length=2, 
        max_length=5,
        description="Plan IDs to compare"
    )
    include_features: bool = Field(default=True, description="Include features comparison")
    include_pricing: bool = Field(default=True, description="Include pricing comparison")
    include_coverage: bool = Field(default=True, description="Include coverage comparison")


class PlanComparisonResponse(BaseModel):
    """Response schema for plan comparison"""
    
    model_config = ConfigDict(from_attributes=True)
    
    plans: List[PlanTypeResponse] = Field(..., description="Compared plans")
    feature_comparison: Optional[Dict[str, Any]] = None
    pricing_comparison: Optional[Dict[str, Any]] = None
    coverage_comparison: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None


# ================================================================
# ELIGIBILITY SCHEMAS
# ================================================================

class PlanEligibilityRequest(BaseModel):
    """Request schema for plan eligibility check"""
    
    model_config = ConfigDict(from_attributes=True)
    
    age: int = Field(..., ge=0, le=150, description="Applicant age")
    member_count: Optional[int] = Field(1, ge=1, description="Number of members")
    dependent_count: Optional[int] = Field(0, ge=0, description="Number of dependents")
    pre_existing_conditions: Optional[List[str]] = Field(
        default_factory=list,
        description="Pre-existing conditions"
    )
    location: Optional[str] = Field(None, description="Location/region")


class PlanEligibilityResponse(BaseModel):
    """Response schema for plan eligibility"""
    
    model_config = ConfigDict(from_attributes=True)
    
    eligible_plans: List[UUID] = Field(..., description="List of eligible plan IDs")
    ineligible_plans: List[Dict[str, Any]] = Field(
        ...,
        description="Plans with reasons for ineligibility"
    )
    recommendations: Optional[List[str]] = Field(
        default_factory=list,
        description="Recommendations"
    )


# ================================================================
# END OF SCHEMA
# ================================================================