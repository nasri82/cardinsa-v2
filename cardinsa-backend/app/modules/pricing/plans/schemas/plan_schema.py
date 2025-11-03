# app/modules/pricing/plans/schemas/plan_schema.py

"""
Plan Schema - Production Ready

Pydantic schemas for Plan validation and serialization.
Handles request/response validation and data transformation.
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, validator, ConfigDict
from pydantic.types import constr, condecimal


# ================================================================
# ENUMS (Matching model enums)
# ================================================================

class PlanType(str, Enum):
    """Plan type enumeration"""
    INDIVIDUAL = "individual"
    FAMILY = "family"
    GROUP = "group"
    CORPORATE = "corporate"
    SME = "sme"
    GOVERNMENT = "government"
    STUDENT = "student"
    SENIOR = "senior"
    CUSTOM = "custom"


class PlanTier(str, Enum):
    """Plan tier levels"""
    BASIC = "basic"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    CUSTOM = "custom"


class PlanStatus(str, Enum):
    """Plan lifecycle status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISCONTINUED = "discontinued"
    ARCHIVED = "archived"


class ApprovalStatus(str, Enum):
    """Regulatory approval status"""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONDITIONAL = "conditional"


class Visibility(str, Enum):
    """Plan visibility settings"""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    INTERNAL = "internal"
    PARTNER = "partner"


class PaymentFrequency(str, Enum):
    """Premium payment frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    SINGLE = "single"


# ================================================================
# BASE SCHEMAS
# ================================================================

class PlanBase(BaseModel):
    """Base schema for Plan"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Basic Information
    plan_code: constr(min_length=1, max_length=50) = Field(
        ...,
        description="Unique plan code within company"
    )
    name: constr(min_length=1, max_length=200) = Field(
        ...,
        description="Plan display name"
    )
    name_ar: Optional[constr(max_length=200)] = Field(
        None,
        description="Plan name in Arabic"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed plan description"
    )
    description_ar: Optional[str] = Field(
        None,
        description="Plan description in Arabic"
    )
    
    # Plan Configuration
    plan_type: PlanType = Field(
        PlanType.INDIVIDUAL,
        description="Type of plan"
    )
    plan_tier: Optional[PlanTier] = Field(
        PlanTier.SILVER,
        description="Plan tier level"
    )
    
    # Pricing
    premium_amount: condecimal(ge=0, decimal_places=2) = Field(
        ...,
        description="Base premium amount"
    )
    currency: str = Field(
        'USD',
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code"
    )
    coverage_period_months: int = Field(
        12,
        gt=0,
        le=120,
        description="Coverage period in months"
    )
    payment_frequency: PaymentFrequency = Field(
        PaymentFrequency.MONTHLY,
        description="Premium payment frequency"
    )
    profit_target: Optional[condecimal(ge=-100, le=100, decimal_places=2)] = Field(
        None,
        description="Target profit margin percentage"
    )


# ================================================================
# CREATE SCHEMA
# ================================================================

class PlanCreate(PlanBase):
    """Schema for creating a Plan"""
    
    # Required Foreign Keys
    product_id: UUID = Field(
        ...,
        description="Reference to product catalog"
    )
    company_id: UUID = Field(
        ...,
        description="Company offering this plan"
    )
    
    # Optional Configuration
    is_active: bool = Field(
        False,
        description="Is plan currently active"
    )
    is_default: bool = Field(
        False,
        description="Is default plan for product"
    )
    visibility: Visibility = Field(
        Visibility.PUBLIC,
        description="Plan visibility setting"
    )
    
    # Dates
    effective_date: Optional[date] = Field(
        None,
        description="Plan effective start date"
    )
    expiry_date: Optional[date] = Field(
        None,
        description="Plan expiration date"
    )
    start_date: Optional[date] = Field(
        None,
        description="Sales start date"
    )
    end_date: Optional[date] = Field(
        None,
        description="Sales end date"
    )
    
    # Market & Distribution
    target_market_segment: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Target market segments"
    )
    distribution_channels: Optional[List[str]] = Field(
        default_factory=list,
        description="Allowed distribution channels"
    )
    commission_structure: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Commission structure by channel"
    )
    
    # Underwriting & Eligibility
    underwriting_guidelines: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Underwriting rules"
    )
    minimum_group_size: Optional[int] = Field(
        None,
        ge=1,
        description="Minimum group size"
    )
    maximum_group_size: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum group size"
    )
    minimum_age: Optional[int] = Field(
        None,
        ge=0,
        le=150,
        description="Minimum enrollment age"
    )
    maximum_issue_age: Optional[int] = Field(
        None,
        ge=0,
        le=150,
        description="Maximum enrollment age"
    )
    
    # Waiting Periods & Terms
    waiting_periods: Optional[Dict[str, int]] = Field(
        default_factory=dict,
        description="Waiting periods by benefit type"
    )
    renewal_terms: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Renewal terms and conditions"
    )
    
    # Documents
    policy_terms_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL to policy terms"
    )
    marketing_materials_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL to marketing materials"
    )
    
    # Metadata
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Searchable tags"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """Validate date ranges"""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    @validator('maximum_issue_age')
    def validate_ages(cls, v, values):
        """Validate age ranges"""
        if v and 'minimum_age' in values and values['minimum_age']:
            if v < values['minimum_age']:
                raise ValueError('Maximum age must be greater than minimum age')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        """Validate currency code"""
        return v.upper()


# ================================================================
# UPDATE SCHEMA
# ================================================================

class PlanUpdate(BaseModel):
    """Schema for updating a Plan"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # All fields optional for partial updates
    name: Optional[constr(min_length=1, max_length=200)] = None
    name_ar: Optional[constr(max_length=200)] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    
    # Status & Configuration
    status: Optional[PlanStatus] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    visibility: Optional[Visibility] = None
    
    # Pricing Updates
    premium_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    profit_target: Optional[condecimal(ge=-100, le=100, decimal_places=2)] = None
    
    # Date Updates
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    # Market & Distribution Updates
    target_market_segment: Optional[Dict[str, Any]] = None
    distribution_channels: Optional[List[str]] = None
    commission_structure: Optional[Dict[str, Any]] = None
    
    # Underwriting Updates
    underwriting_guidelines: Optional[Dict[str, Any]] = None
    waiting_periods: Optional[Dict[str, int]] = None
    renewal_terms: Optional[Dict[str, Any]] = None
    
    # Metadata Updates
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# ================================================================
# RESPONSE SCHEMAS
# ================================================================

class PlanResponse(BaseModel):
    """Basic Plan response schema"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    plan_code: str
    product_id: UUID
    company_id: UUID
    name: str
    name_ar: Optional[str]
    description: Optional[str]
    plan_type: str
    plan_tier: Optional[str]
    status: str
    is_active: bool
    is_default: bool
    visibility: str
    version: int
    
    # Pricing
    premium_amount: Decimal
    currency: str
    coverage_period_months: int
    payment_frequency: str
    profit_target: Optional[Decimal]
    
    # Dates
    effective_date: Optional[date]
    expiry_date: Optional[date]
    start_date: Optional[date]
    end_date: Optional[date]
    
    # Eligibility
    minimum_age: Optional[int]
    maximum_issue_age: Optional[int]
    minimum_group_size: Optional[int]
    
    # Regulatory
    regulatory_approval_status: str
    regulatory_filing_reference: Optional[str]
    approval_required: bool
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Metadata
    tags: Optional[List[str]]


class PlanDetailResponse(PlanResponse):
    """Detailed Plan response with relationships"""
    
    # Additional Details
    target_market_segment: Optional[Dict[str, Any]]
    distribution_channels: Optional[List[str]]
    commission_structure: Optional[Dict[str, Any]]
    underwriting_guidelines: Optional[Dict[str, Any]]
    waiting_periods: Optional[Dict[str, int]]
    renewal_terms: Optional[Dict[str, Any]]
    
    # Documents
    policy_terms_url: Optional[str]
    marketing_materials_url: Optional[str]
    brochure_url: Optional[str]
    
    # Related Data Counts
    territory_count: Optional[int] = 0
    coverage_count: Optional[int] = 0
    benefit_count: Optional[int] = 0
    exclusion_count: Optional[int] = 0
    
    # Metadata
    metadata: Optional[Dict[str, Any]]
    
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to include relationship counts"""
        data = super().from_orm(obj)
        
        # Add relationship counts if available
        if hasattr(obj, 'territories'):
            data.territory_count = len(obj.territories)
        if hasattr(obj, 'coverage_links'):
            data.coverage_count = len(obj.coverage_links)
        if hasattr(obj, 'benefit_schedules'):
            data.benefit_count = len(obj.benefit_schedules)
        if hasattr(obj, 'exclusions'):
            data.exclusion_count = len(obj.exclusions)
        
        return data


# ================================================================
# SEARCH & FILTER SCHEMAS
# ================================================================

class PlanSearchFilters(BaseModel):
    """Schema for plan search filters"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # ID Filters
    product_id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    
    # Type Filters
    plan_type: Optional[PlanType] = None
    plan_tier: Optional[PlanTier] = None
    
    # Status Filters
    status: Optional[PlanStatus] = None
    is_active: Optional[bool] = None
    
    # Text Search
    search_term: Optional[str] = Field(
        None,
        min_length=2,
        description="Search in name, code, description"
    )
    
    # Premium Range
    min_premium: Optional[Decimal] = Field(None, ge=0)
    max_premium: Optional[Decimal] = Field(None, ge=0)
    
    # Date Filters
    effective_date_from: Optional[date] = None
    effective_date_to: Optional[date] = None
    
    # Sorting
    sort_by: Optional[str] = Field(
        'created_at',
        description="Field to sort by"
    )
    sort_order: Optional[str] = Field(
        'desc',
        pattern='^(asc|desc)$',
        description="Sort order"
    )


# ================================================================
# COMPARISON & ELIGIBILITY SCHEMAS
# ================================================================

class PlanComparisonRequest(BaseModel):
    """Request schema for plan comparison"""
    
    plan_ids: List[UUID] = Field(
        ...,
        min_items=2,
        max_items=5,
        description="Plans to compare"
    )
    include_coverage: bool = Field(
        True,
        description="Include coverage comparison"
    )
    include_benefits: bool = Field(
        True,
        description="Include benefits comparison"
    )
    include_exclusions: bool = Field(
        True,
        description="Include exclusions comparison"
    )


class PlanComparisonResponse(BaseModel):
    """Response schema for plan comparison"""
    
    model_config = ConfigDict(from_attributes=True)
    
    plans: List[Dict[str, Any]]
    recommendation: Optional[Dict[str, Any]]
    comparison_date: datetime


class PlanEligibilityCheck(BaseModel):
    """Schema for eligibility check"""
    
    age: Optional[int] = Field(
        None,
        ge=0,
        le=150,
        description="Applicant age"
    )
    gender: Optional[str] = Field(
        None,
        description="Applicant gender"
    )
    location: Optional[str] = Field(
        None,
        description="Applicant location/territory"
    )
    occupation: Optional[str] = Field(
        None,
        description="Applicant occupation"
    )
    group_size: Optional[int] = Field(
        None,
        ge=1,
        description="Group size for group plans"
    )
    pre_existing_conditions: Optional[List[str]] = Field(
        default_factory=list,
        description="Pre-existing medical conditions"
    )
    income_level: Optional[str] = Field(
        None,
        description="Income level category"
    )


class PlanEligibilityResponse(BaseModel):
    """Response schema for eligibility check"""
    
    model_config = ConfigDict(from_attributes=True)
    
    plan_id: UUID
    eligible: bool
    reasons: List[str] = Field(
        default_factory=list,
        description="Reasons for ineligibility"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings or conditions"
    )
    requirements: List[str] = Field(
        default_factory=list,
        description="Requirements to meet"
    )


# ================================================================
# PRICING SCHEMAS
# ================================================================

class PlanPricingRequest(BaseModel):
    """Request schema for premium calculation"""
    
    age: Optional[int] = Field(
        None,
        ge=0,
        le=150,
        description="Member age"
    )
    group_size: Optional[int] = Field(
        None,
        ge=1,
        description="Group size"
    )
    territory_code: Optional[str] = Field(
        None,
        description="Territory/location code"
    )
    risk_factors: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional risk factors"
    )
    optional_coverages: Optional[List[UUID]] = Field(
        default_factory=list,
        description="Selected optional coverages"
    )
    discount_codes: Optional[List[str]] = Field(
        default_factory=list,
        description="Applicable discount codes"
    )


class PlanPricingResponse(BaseModel):
    """Response schema for premium calculation"""
    
    model_config = ConfigDict(from_attributes=True)
    
    plan_id: UUID
    base_premium: Decimal
    adjustments: List[Dict[str, Any]]
    final_premium: Decimal
    currency: str
    coverage_period_months: int
    calculation_date: datetime
    
    # Breakdown
    age_adjustment: Optional[Decimal] = None
    group_discount: Optional[Decimal] = None
    territory_adjustment: Optional[Decimal] = None
    risk_loading: Optional[Decimal] = None
    discounts: Optional[Decimal] = None
    taxes: Optional[Decimal] = None


# ================================================================
# TERRITORY SCHEMAS
# ================================================================

class PlanTerritoryCreate(BaseModel):
    """Schema for creating plan territory"""
    
    model_config = ConfigDict(from_attributes=True)
    
    territory_code: constr(min_length=1, max_length=50) = Field(
        ...,
        description="Territory code"
    )
    territory_name: constr(min_length=1, max_length=200) = Field(
        ...,
        description="Territory name"
    )
    territory_name_ar: Optional[str] = None
    territory_type: str = Field(
        'country',
        description="Type of territory"
    )
    
    # Pricing
    rate_adjustment: condecimal(ge=-100, le=1000, decimal_places=2) = Field(
        0,
        description="Rate adjustment percentage"
    )
    minimum_premium: Optional[condecimal(ge=0, decimal_places=2)] = None
    maximum_premium: Optional[condecimal(ge=0, decimal_places=2)] = None
    
    # Dates
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    # Status
    is_active: bool = True
    
    # Regulatory
    regulatory_requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PlanTerritoryResponse(BaseModel):
    """Response schema for plan territory"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    plan_id: UUID
    territory_code: str
    territory_name: str
    territory_type: str
    rate_adjustment: Decimal
    is_active: bool
    effective_date: Optional[date]
    expiry_date: Optional[date]


# ================================================================
# VERSION SCHEMAS
# ================================================================

class PlanVersionResponse(BaseModel):
    """Response schema for plan version"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    plan_id: UUID
    version_number: int
    version_label: Optional[str]
    version_description: Optional[str]
    change_type: str
    status: str
    is_current_version: bool
    effective_date: datetime
    expiry_date: Optional[datetime]
    created_at: datetime
    created_by: Optional[UUID]


# ================================================================
# BULK OPERATION SCHEMAS
# ================================================================

class PlanBulkUpdate(BaseModel):
    """Schema for bulk plan updates"""
    
    plan_ids: List[UUID] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="Plans to update"
    )
    update_data: PlanUpdate = Field(
        ...,
        description="Update data to apply"
    )


class PlanBulkResponse(BaseModel):
    """Response for bulk operations"""
    
    success_count: int
    failure_count: int
    results: List[Dict[str, Any]]


# ================================================================
# STATISTICS SCHEMAS
# ================================================================

class PlanStatistics(BaseModel):
    """Schema for plan statistics"""
    
    model_config = ConfigDict(from_attributes=True)
    
    total_plans: int
    active_plans: int
    inactive_plans: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    premium_statistics: Dict[str, float]
    
    # Period metrics
    created_this_month: Optional[int] = 0
    activated_this_month: Optional[int] = 0
    discontinued_this_month: Optional[int] = 0