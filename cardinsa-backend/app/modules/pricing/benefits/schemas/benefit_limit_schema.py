# app/modules/benefits/schemas/benefit_limit_schema.py
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum
from decimal import Decimal


# =====================================================
# ENUMS FOR VALIDATION
# =====================================================

class LimitTypeEnum(str, Enum):
    """Enumeration of benefit limit types"""
    MONETARY = "MONETARY"
    FREQUENCY = "FREQUENCY" 
    QUANTITY = "QUANTITY"
    VISIT = "VISIT"
    TIME_BASED = "TIME_BASED"
    AGGREGATE = "AGGREGATE"
    LIFETIME = "LIFETIME"


class LimitCategoryEnum(str, Enum):
    """Enumeration of limit categories"""
    COVERAGE = "COVERAGE"
    DEDUCTIBLE = "DEDUCTIBLE"
    COPAY = "COPAY"
    COINSURANCE = "COINSURANCE"
    OUT_OF_POCKET = "OUT_OF_POCKET"
    BENEFIT_MAX = "BENEFIT_MAX"


class LimitScopeEnum(str, Enum):
    """Enumeration of limit scopes"""
    INDIVIDUAL = "INDIVIDUAL"
    FAMILY = "FAMILY"
    PER_INCIDENT = "PER_INCIDENT"
    PER_CONDITION = "PER_CONDITION"
    AGGREGATE = "AGGREGATE"
    LIFETIME = "LIFETIME"


class NetworkTypeEnum(str, Enum):
    """Enumeration of network types"""
    IN_NETWORK = "IN_NETWORK"
    OUT_OF_NETWORK = "OUT_OF_NETWORK"
    BOTH = "BOTH"
    PREFERRED = "PREFERRED"
    NON_PREFERRED = "NON_PREFERRED"


class ResetPeriodEnum(str, Enum):
    """Enumeration of reset periods"""
    NEVER = "NEVER"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"
    PLAN_YEAR = "PLAN_YEAR"
    LIFETIME = "LIFETIME"


class FrequencyPeriodEnum(str, Enum):
    """Enumeration of frequency periods"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"
    LIFETIME = "LIFETIME"
    PER_INCIDENT = "PER_INCIDENT"


class LimitStatusEnum(str, Enum):
    """Enumeration of limit status values"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


# =====================================================
# BASE SCHEMA
# =====================================================

class BenefitLimitBase(BaseModel):
    """Base schema for benefit limit with common fields"""
    
    limit_code: str = Field(
        ..., 
        min_length=1, 
        max_length=30,
        description="Unique code identifying the benefit limit",
        example="DEDUCT_IND_001"
    )
    limit_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Display name of the benefit limit",
        example="Individual Annual Deductible"
    )
    limit_name_ar: Optional[str] = Field(
        None, 
        max_length=100,
        description="Arabic translation of limit name",
        example="الخصم السنوي الفردي"
    )
    
    # Classification
    limit_type: LimitTypeEnum = Field(
        ...,
        description="Type classification of the limit"
    )
    limit_category: LimitCategoryEnum = Field(
        default=LimitCategoryEnum.COVERAGE,
        description="Category classification of the limit"
    )
    limit_scope: LimitScopeEnum = Field(
        default=LimitScopeEnum.INDIVIDUAL,
        description="Scope of the limit application"
    )
    
    # Monetary limits
    monetary_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Monetary limit amount",
        example="1000.00"
    )
    currency_code: str = Field(
        default="USD",
        max_length=3,
        description="Currency code for monetary limits"
    )
    
    # Deductible specific fields
    deductible_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Deductible amount"
    )
    deductible_type: Optional[str] = Field(
        None,
        max_length=20,
        description="Type of deductible (INDIVIDUAL, FAMILY, EMBEDDED, etc.)"
    )
    
    # Out-of-pocket limits
    out_of_pocket_max: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Out-of-pocket maximum amount"
    )
    out_of_pocket_individual: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Individual out-of-pocket maximum"
    )
    out_of_pocket_family: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Family out-of-pocket maximum"
    )
    
    # Copay limits
    copay_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Copay amount"
    )
    copay_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Copay percentage"
    )
    
    # Coinsurance limits
    coinsurance_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Coinsurance percentage"
    )
    coinsurance_max: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Maximum coinsurance amount"
    )
    
    # Coverage limits
    coverage_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Coverage limit amount"
    )
    lifetime_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Lifetime limit amount"
    )
    annual_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Annual limit amount"
    )
    
    # Frequency and quantity limits
    frequency_limit: Optional[int] = Field(
        None,
        ge=0,
        description="Frequency limit number"
    )
    frequency_period: Optional[FrequencyPeriodEnum] = Field(
        None,
        description="Frequency period"
    )
    max_visits: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum visits allowed"
    )
    max_days: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum days allowed"
    )
    max_units: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum units allowed"
    )
    
    # Visit-specific limits
    visits_per_year: Optional[int] = Field(
        None,
        ge=0,
        description="Visits allowed per year"
    )
    visits_per_month: Optional[int] = Field(
        None,
        ge=0,
        description="Visits allowed per month"
    )
    visits_per_condition: Optional[int] = Field(
        None,
        ge=0,
        description="Visits allowed per condition"
    )
    
    # Time-based limits
    waiting_period_days: Optional[int] = Field(
        None,
        ge=0,
        description="Waiting period in days"
    )
    elimination_period_days: Optional[int] = Field(
        None,
        ge=0,
        description="Elimination period in days"
    )
    benefit_period_days: Optional[int] = Field(
        None,
        ge=0,
        description="Benefit period in days"
    )
    
    # Network-based limits
    network_type: Optional[NetworkTypeEnum] = Field(
        None,
        description="Network type this limit applies to"
    )
    in_network_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="In-network limit amount"
    )
    out_of_network_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Out-of-network limit amount"
    )
    in_network_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="In-network percentage"
    )
    out_of_network_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Out-of-network percentage"
    )
    
    # Age-based limits
    age_limit_min: Optional[int] = Field(
        None,
        ge=0,
        le=150,
        description="Minimum age for limit application"
    )
    age_limit_max: Optional[int] = Field(
        None,
        ge=0,
        le=150,
        description="Maximum age for limit application"
    )
    
    # Accumulator settings
    accumulates_to_deductible: bool = Field(
        default=True,
        description="Whether this accumulates to deductible"
    )
    accumulates_to_oop: bool = Field(
        default=True,
        description="Whether this accumulates to out-of-pocket maximum"
    )
    accumulates_to_benefit_max: bool = Field(
        default=True,
        description="Whether this accumulates to benefit maximum"
    )
    
    # Reset settings
    reset_period: ResetPeriodEnum = Field(
        default=ResetPeriodEnum.ANNUAL,
        description="How often the limit resets"
    )
    reset_date: Optional[datetime] = Field(
        None,
        description="Specific reset date if applicable"
    )
    
    # Override settings
    can_override: bool = Field(
        default=False,
        description="Whether this limit can be overridden"
    )
    override_level: Optional[str] = Field(
        None,
        max_length=20,
        description="Level of authorization required for override"
    )
    
    # Status and effective dates
    is_active: bool = Field(
        default=True,
        description="Whether the limit is currently active"
    )
    is_mandatory: bool = Field(
        default=False,
        description="Whether this limit is mandatory"
    )
    effective_from: datetime = Field(
        default_factory=datetime.utcnow,
        description="When limit becomes effective"
    )
    effective_to: Optional[datetime] = Field(
        None,
        description="When limit expires"
    )


# =====================================================
# CREATE SCHEMA
# =====================================================

class BenefitLimitCreate(BenefitLimitBase):
    """Schema for creating a new benefit limit"""
    
    # Related entity references
    coverage_id: Optional[UUID] = Field(
        None,
        description="ID of the coverage this limit applies to"
    )
    benefit_type_id: Optional[UUID] = Field(
        None,
        description="ID of the benefit type this limit applies to"
    )
    
    # Business rules and conditions
    conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Conditions for limit application",
        example={
            "age_range": {"min": 18, "max": 65},
            "gender": "F",
            "state": "TX"
        }
    )
    exceptions: Optional[Dict[str, Any]] = Field(
        None,
        description="Exception rules for this limit",
        example={
            "emergency_override": True,
            "life_threatening": "no_limit"
        }
    )
    calculation_rules: Optional[Dict[str, Any]] = Field(
        None,
        description="Calculation rules for this limit",
        example={
            "rounding": "up",
            "minimum_charge": "50.00"
        }
    )
    
    # Geographic and temporal restrictions
    geographic_scope: Optional[str] = Field(
        None,
        max_length=30,
        description="Geographic scope of the limit"
    )
    coverage_territory: Optional[str] = Field(
        None,
        max_length=100,
        description="Coverage territory"
    )
    excluded_territories: Optional[List[str]] = Field(
        None,
        description="Excluded territories"
    )
    
    # Provider-specific limits
    specialist_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Specialist-specific limit"
    )
    referral_required: bool = Field(
        default=False,
        description="Whether referral is required"
    )
    prior_auth_required: bool = Field(
        default=False,
        description="Whether prior authorization is required"
    )
    
    # Display and formatting
    display_format: Optional[str] = Field(
        None,
        max_length=50,
        description="Display format for this limit"
    )
    display_order: int = Field(
        default=1,
        ge=1,
        description="Display order for this limit"
    )
    is_highlighted: bool = Field(
        default=False,
        description="Whether this limit should be highlighted"
    )
    
    # Member communication
    member_description: Optional[str] = Field(
        None,
        description="Member-friendly description"
    )
    member_description_ar: Optional[str] = Field(
        None,
        description="Arabic member-friendly description"
    )
    
    # Regulatory information
    regulatory_code: Optional[str] = Field(
        None,
        max_length=50,
        description="Regulatory code"
    )
    compliance_notes: Optional[str] = Field(
        None,
        description="Compliance notes"
    )
    
    @validator('limit_code')
    def validate_limit_code(cls, v):
        """Validate limit code format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Limit code must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()
    
    @validator('effective_to')
    def validate_effective_to(cls, v, values):
        """Validate effective_to is after effective_from"""
        if v and 'effective_from' in values and v <= values['effective_from']:
            raise ValueError('Effective to date must be after effective from date')
        return v
    
    @validator('age_limit_max')
    def validate_age_limits(cls, v, values):
        """Validate age limit consistency"""
        if v and 'age_limit_min' in values and values['age_limit_min'] and v <= values['age_limit_min']:
            raise ValueError('Maximum age must be greater than minimum age')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "limit_code": "DEDUCT_IND_001",
                "limit_name": "Individual Annual Deductible",
                "limit_type": "MONETARY",
                "limit_category": "DEDUCTIBLE",
                "limit_scope": "INDIVIDUAL",
                "deductible_amount": "1000.00",
                "reset_period": "ANNUAL",
                "accumulates_to_oop": True,
                "is_mandatory": True
            }
        }


# =====================================================
# UPDATE SCHEMA
# =====================================================

class BenefitLimitUpdate(BaseModel):
    """Schema for updating an existing benefit limit"""
    
    limit_name: Optional[str] = Field(None, min_length=1, max_length=100)
    limit_name_ar: Optional[str] = Field(None, max_length=100)
    
    limit_type: Optional[LimitTypeEnum] = Field(None)
    limit_category: Optional[LimitCategoryEnum] = Field(None)
    limit_scope: Optional[LimitScopeEnum] = Field(None)
    
    # Monetary limit updates
    monetary_limit: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    deductible_amount: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    out_of_pocket_max: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    out_of_pocket_individual: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    out_of_pocket_family: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Copay and coinsurance updates
    copay_amount: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    copay_percentage: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2)
    coinsurance_percentage: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2)
    coinsurance_max: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Coverage limit updates
    coverage_limit: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    lifetime_limit: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    annual_limit: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Frequency and quantity updates
    frequency_limit: Optional[int] = Field(None, ge=0)
    frequency_period: Optional[FrequencyPeriodEnum] = Field(None)
    max_visits: Optional[int] = Field(None, ge=0)
    max_days: Optional[int] = Field(None, ge=0)
    max_units: Optional[int] = Field(None, ge=0)
    
    # Time-based updates
    waiting_period_days: Optional[int] = Field(None, ge=0)
    elimination_period_days: Optional[int] = Field(None, ge=0)
    benefit_period_days: Optional[int] = Field(None, ge=0)
    
    # Network updates
    network_type: Optional[NetworkTypeEnum] = Field(None)
    in_network_limit: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    out_of_network_limit: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Age limit updates
    age_limit_min: Optional[int] = Field(None, ge=0, le=150)
    age_limit_max: Optional[int] = Field(None, ge=0, le=150)
    
    # Accumulator updates
    accumulates_to_deductible: Optional[bool] = Field(None)
    accumulates_to_oop: Optional[bool] = Field(None)
    accumulates_to_benefit_max: Optional[bool] = Field(None)
    
    # Reset updates
    reset_period: Optional[ResetPeriodEnum] = Field(None)
    reset_date: Optional[datetime] = Field(None)
    
    # Override updates
    can_override: Optional[bool] = Field(None)
    override_level: Optional[str] = Field(None, max_length=20)
    
    # Status updates
    is_active: Optional[bool] = Field(None)
    is_mandatory: Optional[bool] = Field(None)
    effective_to: Optional[datetime] = Field(None)
    
    # Business rule updates
    conditions: Optional[Dict[str, Any]] = Field(None)
    exceptions: Optional[Dict[str, Any]] = Field(None)
    calculation_rules: Optional[Dict[str, Any]] = Field(None)
    
    # Display updates
    display_format: Optional[str] = Field(None, max_length=50)
    display_order: Optional[int] = Field(None, ge=1)
    is_highlighted: Optional[bool] = Field(None)
    
    # Communication updates
    member_description: Optional[str] = Field(None)
    member_description_ar: Optional[str] = Field(None)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class BenefitLimitResponse(BenefitLimitBase):
    """Schema for benefit limit responses"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Unique identifier for the benefit limit")
    
    # Related entity information
    coverage_id: Optional[UUID] = Field(None, description="Associated coverage ID")
    benefit_type_id: Optional[UUID] = Field(None, description="Associated benefit type ID")
    coverage_name: Optional[str] = Field(None, description="Associated coverage name")
    benefit_type_name: Optional[str] = Field(None, description="Associated benefit type name")
    
    # Extended limit details
    conditions: Optional[Dict[str, Any]] = Field(None, description="Application conditions")
    exceptions: Optional[Dict[str, Any]] = Field(None, description="Exception rules")
    calculation_rules: Optional[Dict[str, Any]] = Field(None, description="Calculation rules")
    
    # Geographic and restrictions
    geographic_scope: Optional[str] = Field(None, description="Geographic scope")
    coverage_territory: Optional[str] = Field(None, description="Coverage territory")
    excluded_territories: Optional[List[str]] = Field(None, description="Excluded territories")
    
    # Provider requirements
    specialist_limit: Optional[Decimal] = Field(None, description="Specialist limit")
    referral_required: bool = Field(default=False, description="Referral required")
    prior_auth_required: bool = Field(default=False, description="Prior auth required")
    
    # Display information
    display_format: Optional[str] = Field(None, description="Display format")
    display_order: int = Field(default=1, description="Display order")
    is_highlighted: bool = Field(default=False, description="Is highlighted")
    
    # Member communication
    member_description: Optional[str] = Field(None, description="Member description")
    member_description_ar: Optional[str] = Field(None, description="Arabic member description")
    
    # Regulatory information
    regulatory_code: Optional[str] = Field(None, description="Regulatory code")
    compliance_notes: Optional[str] = Field(None, description="Compliance notes")
    
    # Usage statistics
    usage_count: Optional[int] = Field(None, description="Number of times this limit is used")
    active_plans_count: Optional[int] = Field(None, description="Number of active plans using this limit")
    
    # Status information
    status: Optional[LimitStatusEnum] = Field(None, description="Current limit status")
    status_reason: Optional[str] = Field(None, description="Reason for current status")
    
    # Calculated fields
    formatted_display: Optional[str] = Field(None, description="Formatted display string")
    limit_summary: Optional[str] = Field(None, description="Human-readable summary")
    
    # Audit fields
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="ID of user who created the limit")
    updated_by: Optional[UUID] = Field(None, description="ID of user who last updated the limit")
    version: int = Field(default=1, description="Version number")


class BenefitLimitSummary(BaseModel):
    """Lightweight summary schema for benefit limits"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    limit_code: str
    limit_name: str
    limit_name_ar: Optional[str] = None
    limit_type: LimitTypeEnum
    limit_category: LimitCategoryEnum
    limit_scope: LimitScopeEnum
    is_active: bool
    is_mandatory: bool
    
    # Key limit values
    monetary_limit: Optional[Decimal] = None
    frequency_limit: Optional[int] = None
    max_visits: Optional[int] = None
    formatted_display: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "limit_code": "DEDUCT_IND_001",
                "limit_name": "Individual Annual Deductible",
                "limit_type": "MONETARY",
                "limit_category": "DEDUCTIBLE",
                "limit_scope": "INDIVIDUAL",
                "is_active": True,
                "is_mandatory": True,
                "monetary_limit": "1000.00",
                "formatted_display": "$1,000 annual deductible"
            }
        }


# =====================================================
# SPECIALIZED SCHEMAS
# =====================================================

class BenefitLimitCalculation(BaseModel):
    """Schema for benefit limit calculation results"""
    
    limit_id: UUID
    limit_name: str
    service_cost: Decimal = Field(..., description="Original service cost")
    
    # Calculation inputs
    current_usage: Dict[str, Any] = Field(..., description="Current usage amounts")
    member_context: Dict[str, Any] = Field(..., description="Member context for calculation")
    
    # Calculation results
    limit_applies: bool = Field(..., description="Whether limit applies to this service")
    remaining_benefit: Optional[Decimal] = Field(None, description="Remaining benefit amount")
    member_responsibility: Decimal = Field(..., description="Member's financial responsibility")
    insurance_pays: Decimal = Field(..., description="Amount insurance will pay")
    
    # Limit status
    limit_reached: bool = Field(default=False, description="Whether limit has been reached")
    limit_exceeded: bool = Field(default=False, description="Whether limit has been exceeded")
    
    # Detailed breakdown
    calculation_details: Dict[str, Any] = Field(..., description="Detailed calculation breakdown")
    applied_rules: List[str] = Field(default_factory=list, description="Rules applied in calculation")
    
    calculation_date: datetime = Field(default_factory=datetime.utcnow, description="When calculation was performed")

    class Config:
        json_schema_extra = {
            "example": {
                "limit_id": "123e4567-e89b-12d3-a456-426614174000",
                "limit_name": "Individual Annual Deductible",
                "service_cost": "500.00",
                "current_usage": {"deductible_met": "200.00"},
                "member_context": {"plan_year_start": "2024-01-01"},
                "limit_applies": True,
                "remaining_benefit": "800.00",
                "member_responsibility": "300.00",
                "insurance_pays": "200.00",
                "limit_reached": False
            }
        }


class BenefitLimitUtilization(BaseModel):
    """Schema for benefit limit utilization tracking"""
    
    limit_id: UUID
    limit_name: str
    member_id: Optional[UUID] = Field(None, description="Specific member (if applicable)")
    
    # Current utilization
    current_amount_used: Decimal = Field(default=Decimal('0'), description="Current amount used")
    current_visits_used: int = Field(default=0, description="Current visits used")
    current_units_used: int = Field(default=0, description="Current units used")
    
    # Limits and remaining
    total_limit_amount: Optional[Decimal] = Field(None, description="Total limit amount")
    remaining_amount: Optional[Decimal] = Field(None, description="Remaining amount")
    total_visits_allowed: Optional[int] = Field(None, description="Total visits allowed")
    remaining_visits: Optional[int] = Field(None, description="Remaining visits")
    
    # Utilization percentages
    amount_utilization_percentage: Optional[float] = Field(None, ge=0, le=100, description="Amount utilization percentage")
    visit_utilization_percentage: Optional[float] = Field(None, ge=0, le=100, description="Visit utilization percentage")
    
    # Period information
    tracking_period: str = Field(..., description="Current tracking period")
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    next_reset_date: Optional[date] = Field(None, description="Next reset date")
    
    # Status
    utilization_status: str = Field(..., description="Current utilization status")
    # Options: AVAILABLE, APPROACHING_LIMIT, AT_LIMIT, EXCEEDED
    
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last updated timestamp")


class BenefitLimitStats(BaseModel):
    """Schema for benefit limit statistics and analytics"""
    
    limit_id: UUID
    limit_code: str
    limit_name: str
    
    # Usage statistics
    total_members_subject: int = Field(default=0, description="Total members subject to this limit")
    members_at_limit: int = Field(default=0, description="Members who have reached the limit")
    members_exceeded_limit: int = Field(default=0, description="Members who have exceeded the limit")
    
    # Financial statistics
    total_amount_limited: Decimal = Field(default=Decimal('0'), description="Total amount limited by this rule")
    average_member_usage: Optional[Decimal] = Field(None, description="Average member usage")
    median_member_usage: Optional[Decimal] = Field(None, description="Median member usage")
    
    # Utilization statistics
    average_utilization_rate: Optional[float] = Field(None, ge=0, le=100, description="Average utilization rate")
    limit_hit_frequency: Optional[float] = Field(None, description="Frequency of limit being hit")
    
    # Cost impact
    estimated_cost_savings: Optional[Decimal] = Field(None, description="Estimated cost savings from this limit")
    member_cost_impact: Optional[Decimal] = Field(None, description="Average member cost impact")
    
    # Trends
    usage_trend_percentage: Optional[float] = Field(None, description="Usage trend year-over-year")
    cost_trend_percentage: Optional[float] = Field(None, description="Cost trend year-over-year")
    
    # Reporting period
    reporting_period_start: date = Field(..., description="Reporting period start")
    reporting_period_end: date = Field(..., description="Reporting period end")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Statistics last updated")


# =====================================================
# LIST AND FILTER SCHEMAS
# =====================================================

class BenefitLimitFilter(BaseModel):
    """Schema for filtering benefit limits"""
    
    limit_type: Optional[LimitTypeEnum] = Field(None, description="Filter by limit type")
    limit_category: Optional[LimitCategoryEnum] = Field(None, description="Filter by limit category")
    limit_scope: Optional[LimitScopeEnum] = Field(None, description="Filter by limit scope")
    network_type: Optional[NetworkTypeEnum] = Field(None, description="Filter by network type")
    reset_period: Optional[ResetPeriodEnum] = Field(None, description="Filter by reset period")
    
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_mandatory: Optional[bool] = Field(None, description="Filter by mandatory status")
    can_override: Optional[bool] = Field(None, description="Filter by override capability")
    
    # Related entity filters
    coverage_id: Optional[UUID] = Field(None, description="Filter by coverage")
    benefit_type_id: Optional[UUID] = Field(None, description="Filter by benefit type")
    
    # Amount range filters
    monetary_limit_min: Optional[Decimal] = Field(None, ge=0, description="Minimum monetary limit")
    monetary_limit_max: Optional[Decimal] = Field(None, ge=0, description="Maximum monetary limit")
    
    # Visit range filters
    max_visits_min: Optional[int] = Field(None, ge=0, description="Minimum visit limit")
    max_visits_max: Optional[int] = Field(None, ge=0, description="Maximum visit limit")
    
    # Age range filters
    applies_to_age: Optional[int] = Field(None, ge=0, le=150, description="Age the limit applies to")
    
    # Date filters
    effective_date_from: Optional[datetime] = Field(None, description="Effective from date")
    effective_date_to: Optional[datetime] = Field(None, description="Effective to date")
    
    # Search fields
    search_term: Optional[str] = Field(None, max_length=100, description="Search in names and descriptions")
    limit_codes: Optional[List[str]] = Field(None, description="Filter by specific limit codes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "limit_type": "MONETARY",
                "limit_category": "DEDUCTIBLE",
                "limit_scope": "INDIVIDUAL",
                "is_active": True,
                "is_mandatory": True,
                "search_term": "deductible"
            }
        }


class BenefitLimitListResponse(BaseModel):
    """Schema for paginated list of benefit limits"""
    
    items: List[BenefitLimitResponse] = Field(..., description="List of benefit limits")
    total_count: int = Field(..., ge=0, description="Total number of limits matching filter")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")
    
    # Summary statistics
    summary: Optional[Dict[str, Any]] = Field(None, description="Summary statistics for filtered results")


# =====================================================
# BULK OPERATION SCHEMAS
# =====================================================

class BenefitLimitBulkCreate(BaseModel):
    """Schema for bulk creating benefit limits"""
    
    limits: List[BenefitLimitCreate] = Field(
        ..., 
        min_items=1, 
        max_items=100,
        description="List of benefit limits to create"
    )
    
    # Bulk operation settings
    skip_duplicates: bool = Field(default=False, description="Skip limits with duplicate codes")
    validate_references: bool = Field(default=True, description="Validate coverage and benefit type references")
    auto_generate_display_order: bool = Field(default=True, description="Auto-generate display order")

    class Config:
        json_schema_extra = {
            "example": {
                "limits": [
                    {
                        "limit_code": "DEDUCT_IND_001",
                        "limit_name": "Individual Deductible",
                        "limit_type": "MONETARY",
                        "limit_category": "DEDUCTIBLE",
                        "deductible_amount": "1000.00"
                    }
                ],
                "skip_duplicates": True
            }
        }


class BenefitLimitBulkUpdate(BaseModel):
    """Schema for bulk updating benefit limits"""
    
    limit_ids: List[UUID] = Field(..., min_items=1, max_items=100)
    updates: BenefitLimitUpdate = Field(..., description="Fields to update")
    
    # Update options
    preserve_custom_rules: bool = Field(default=True, description="Preserve custom calculation rules")
    recalculate_utilization: bool = Field(default=False, description="Recalculate utilization after update")


class BenefitLimitBulkResponse(BaseModel):
    """Schema for bulk operation responses"""
    
    successful_operations: int = Field(..., ge=0, description="Number of successful operations")
    failed_operations: int = Field(..., ge=0, description="Number of failed operations")
    total_operations: int = Field(..., ge=0, description="Total number of operations attempted")
    
    success_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of successful operations")
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of failed operations")
    
    # Additional results
    utilization_recalculated: Optional[int] = Field(None, description="Number of utilization records recalculated")


# =====================================================
# VALIDATION AND COMPLIANCE SCHEMAS
# =====================================================

class BenefitLimitValidation(BaseModel):
    """Schema for benefit limit validation requests"""
    
    limit_id: UUID = Field(..., description="Limit ID to validate")
    validation_rules: List[str] = Field(
        default=["consistency_check", "regulatory_compliance", "calculation_accuracy"],
        description="Validation rules to apply"
    )
    member_scenarios: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Member scenarios to test against"
    )


class BenefitLimitValidationResult(BaseModel):
    """Schema for benefit limit validation results"""
    
    limit_id: UUID
    limit_code: str
    is_valid: bool = Field(..., description="Overall validation status")
    
    # Validation details
    validation_errors: List[Dict[str, str]] = Field(default_factory=list, description="Validation errors found")
    validation_warnings: List[Dict[str, str]] = Field(default_factory=list, description="Validation warnings found")
    
    # Compliance status
    regulatory_compliance: bool = Field(default=True, description="Regulatory compliance status")
    compliance_issues: List[str] = Field(default_factory=list, description="Compliance issues identified")
    
    # Test results
    scenario_test_results: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Results of scenario testing"
    )
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    
    validated_at: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")


# =====================================================
# MEMBER IMPACT AND CALCULATION SCHEMAS
# =====================================================

class MemberLimitImpactRequest(BaseModel):
    """Schema for calculating member impact of limits"""
    
    member_id: UUID = Field(..., description="Member ID")
    limit_ids: List[UUID] = Field(..., description="Limits to analyze")
    scenario: Dict[str, Any] = Field(..., description="Usage scenario to analyze")
    calculation_date: Optional[datetime] = Field(None, description="Date for calculation")


class MemberLimitImpactResult(BaseModel):
    """Schema for member limit impact results"""
    
    member_id: UUID
    total_member_cost: Decimal = Field(..., description="Total estimated member cost")
    total_insurance_cost: Decimal = Field(..., description="Total estimated insurance cost")
    
    # Limit-specific impacts
    limit_impacts: List[Dict[str, Any]] = Field(..., description="Impact of each limit")
    
    # Summary
    most_restrictive_limit: Optional[UUID] = Field(None, description="Most restrictive limit ID")
    cost_saving_opportunities: List[str] = Field(default_factory=list, description="Cost saving opportunities")
    
    # Projections
    annual_projection: Optional[Dict[str, Decimal]] = Field(None, description="Annual cost projection")
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="Calculation timestamp")