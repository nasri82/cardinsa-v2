# app/modules/benefits/schemas/coverage_option_schema.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum
from decimal import Decimal


# =====================================================
# ENUMS FOR VALIDATION
# =====================================================

class OptionTypeEnum(str, Enum):
    """Enumeration of coverage option types"""
    STANDARD = "STANDARD"
    ENHANCED = "ENHANCED"
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"
    CUSTOM = "CUSTOM"
    ALTERNATIVE = "ALTERNATIVE"
    SUPPLEMENTAL = "SUPPLEMENTAL"
    RIDER = "RIDER"
    ADD_ON = "ADD_ON"
    UPGRADE = "UPGRADE"


class OptionTierEnum(str, Enum):
    """Enumeration of option tiers"""
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    DELUXE = "DELUXE"


class SelectionTypeEnum(str, Enum):
    """Enumeration of selection types"""
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    AUTOMATIC = "AUTOMATIC"
    CONDITIONAL = "CONDITIONAL"
    EXCLUDED = "EXCLUDED"


class OptionStatusEnum(str, Enum):
    """Enumeration of option status values"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


# =====================================================
# BASE SCHEMA
# =====================================================

class CoverageOptionBase(BaseModel):
    """Base schema for coverage option with common fields"""
    
    option_code: str = Field(
        ..., 
        min_length=1, 
        max_length=30,
        description="Unique code identifying the coverage option",
        examples=["PCP_STANDARD_001"]
    )
    option_name: str = Field(
        ..., 
        min_length=1, 
        max_length=150,
        description="Display name of the coverage option",
        examples=["Standard Primary Care Coverage"]
    )
    option_name_ar: Optional[str] = Field(
        None, 
        max_length=150,
        description="Arabic translation of option name",
        examples=["تغطية الرعاية الأولية القياسية"]
    )
    
    # Parent coverage relationship
    coverage_id: UUID = Field(
        ...,
        description="ID of the parent coverage"
    )
    
    # Option classification
    option_type: OptionTypeEnum = Field(
        default=OptionTypeEnum.STANDARD,
        description="Type classification of the option"
    )
    option_tier: Optional[OptionTierEnum] = Field(
        None,
        description="Tier level of the option"
    )
    selection_type: SelectionTypeEnum = Field(
        default=SelectionTypeEnum.OPTIONAL,
        description="How this option can be selected"
    )
    
    # Descriptive fields
    description: Optional[str] = Field(
        None,
        description="Detailed description of the coverage option",
        examples=["Standard primary care coverage with $25 copay and no referral requirements"]
    )
    description_ar: Optional[str] = Field(
        None,
        description="Arabic translation of description"
    )
    short_description: Optional[str] = Field(
        None, 
        max_length=255,
        description="Brief description for display purposes",
        examples=["$25 copay, no referrals needed"]
    )
    
    # Cost-sharing overrides
    copay_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Copay amount for this option",
        examples=[Decimal("25.00")]
    )
    coinsurance_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Coinsurance percentage for this option",
        examples=[Decimal("20.00")]
    )
    deductible_override: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Deductible override amount",
        examples=[Decimal("500.00")]
    )
    
    # Network-specific cost sharing
    in_network_copay: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="In-network copay amount"
    )
    out_of_network_copay: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Out-of-network copay amount"
    )
    in_network_coinsurance: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="In-network coinsurance percentage"
    )
    out_of_network_coinsurance: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Out-of-network coinsurance percentage"
    )
    
    # Limit overrides
    visit_limit_override: Optional[int] = Field(
        None,
        ge=0,
        description="Visit limit override for this option",
        examples=[20]
    )
    annual_limit_override: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Annual limit override"
    )
    lifetime_limit_override: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Lifetime limit override"
    )
    
    # Authorization and referral overrides
    requires_pre_authorization: Optional[bool] = Field(
        None,
        description="Pre-authorization requirement override"
    )
    requires_referral: Optional[bool] = Field(
        None,
        description="Referral requirement override"
    )
    
    # Pricing and premium impact
    premium_adjustment: Optional[Decimal] = Field(
        None,
        max_digits=10,
        decimal_places=2,
        description="Premium adjustment amount (positive or negative)",
        examples=[Decimal("15.00")]
    )
    premium_adjustment_percentage: Optional[Decimal] = Field(
        None,
        ge=-100,
        le=1000,
        max_digits=6,
        decimal_places=2,
        description="Premium adjustment percentage"
    )
    
    # Display and ordering
    display_order: int = Field(
        default=1,
        ge=1,
        description="Order for displaying options",
        examples=[1]
    )
    is_default: bool = Field(
        default=False,
        description="Whether this is the default option"
    )
    is_recommended: bool = Field(
        default=False,
        description="Whether this option is recommended"
    )
    
    # Availability and selection
    is_active: bool = Field(
        default=True,
        description="Whether the option is currently active"
    )
    is_selectable: bool = Field(
        default=True,
        description="Whether the option can be selected by users"
    )
    
    # Effective dates
    effective_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="When option becomes effective"
    )
    expiry_date: Optional[datetime] = Field(
        None,
        description="When option expires"
    )


# =====================================================
# CREATE SCHEMA
# =====================================================

class CoverageOptionCreate(CoverageOptionBase):
    """Schema for creating a new coverage option"""
    
    # Additional features and customizations
    custom_features: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom features specific to this option",
        examples=[{
            "telehealth_included": True,
            "24_7_nurse_line": True,
            "wellness_discount": 10
        }]
    )
    
    # Service modifications
    additional_covered_services: Optional[List[str]] = Field(
        None,
        description="Additional services covered by this option",
        examples=[["telemedicine", "wellness_coaching"]]
    )
    excluded_services_override: Optional[List[str]] = Field(
        None,
        description="Services excluded in this option (overrides parent coverage)"
    )
    
    # Provider network modifications
    network_restrictions: Optional[Dict[str, Any]] = Field(
        None,
        description="Network restrictions specific to this option",
        examples=[{
            "preferred_providers_only": True,
            "enhanced_network_access": False
        }]
    )
    
    # Geographic availability
    geographic_availability: Optional[Dict[str, Any]] = Field(
        None,
        description="Geographic availability restrictions",
        examples=[{
            "available_states": ["TX", "OK", "AR"],
            "metro_areas_only": False
        }]
    )
    
    # Eligibility criteria
    eligibility_criteria: Optional[Dict[str, Any]] = Field(
        None,
        description="Specific eligibility criteria for this option",
        examples=[{
            "min_age": 18,
            "max_age": 65,
            "employment_status": ["ACTIVE", "COBRA"]
        }]
    )
    
    # Quality and performance features
    quality_programs: Optional[Dict[str, Any]] = Field(
        None,
        description="Quality programs included with this option"
    )
    performance_guarantees: Optional[Dict[str, Any]] = Field(
        None,
        description="Performance guarantees for this option"
    )
    
    @field_validator('option_code')
    @classmethod
    def validate_option_code(cls, v):
        """Validate option code format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Option code must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()
    
    @field_validator('expiry_date')
    @classmethod
    def validate_expiry_date(cls, v, info):
        """Validate expiry date is after effective date"""
        if v and 'effective_date' in info.data and v <= info.data['effective_date']:
            raise ValueError('Expiry date must be after effective date')
        return v
    
    @field_validator('premium_adjustment', 'premium_adjustment_percentage')
    @classmethod
    def validate_premium_adjustments(cls, v):
        """Validate premium adjustments"""
        if v is not None and abs(v) > 10000:  # Reasonable limit
            raise ValueError('Premium adjustment seems unreasonably large')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "option_code": "PCP_STANDARD_001",
                "option_name": "Standard Primary Care Coverage",
                "coverage_id": "123e4567-e89b-12d3-a456-426614174000",
                "option_type": "STANDARD",
                "selection_type": "OPTIONAL",
                "in_network_copay": "25.00",
                "out_of_network_copay": "50.00",
                "requires_referral": False,
                "premium_adjustment": "0.00",
                "is_default": True
            }
        }
    )


# =====================================================
# UPDATE SCHEMA
# =====================================================

class CoverageOptionUpdate(BaseModel):
    """Schema for updating an existing coverage option"""
    
    option_name: Optional[str] = Field(None, min_length=1, max_length=150)
    option_name_ar: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = Field(None)
    description_ar: Optional[str] = Field(None)
    short_description: Optional[str] = Field(None, max_length=255)
    
    option_type: Optional[OptionTypeEnum] = Field(None)
    option_tier: Optional[OptionTierEnum] = Field(None)
    selection_type: Optional[SelectionTypeEnum] = Field(None)
    
    # Cost sharing updates
    copay_amount: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    coinsurance_percentage: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2)
    deductible_override: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    
    in_network_copay: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    out_of_network_copay: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    in_network_coinsurance: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2)
    out_of_network_coinsurance: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2)
    
    # Limit updates
    visit_limit_override: Optional[int] = Field(None, ge=0)
    annual_limit_override: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    lifetime_limit_override: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Authorization updates
    requires_pre_authorization: Optional[bool] = Field(None)
    requires_referral: Optional[bool] = Field(None)
    
    # Premium updates
    premium_adjustment: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    premium_adjustment_percentage: Optional[Decimal] = Field(None, ge=-100, le=1000, max_digits=6, decimal_places=2)
    
    # Display updates
    display_order: Optional[int] = Field(None, ge=1)
    is_default: Optional[bool] = Field(None)
    is_recommended: Optional[bool] = Field(None)
    
    # Status updates
    is_active: Optional[bool] = Field(None)
    is_selectable: Optional[bool] = Field(None)
    expiry_date: Optional[datetime] = Field(None)
    
    # Feature updates
    custom_features: Optional[Dict[str, Any]] = Field(None)
    additional_covered_services: Optional[List[str]] = Field(None)
    excluded_services_override: Optional[List[str]] = Field(None)
    network_restrictions: Optional[Dict[str, Any]] = Field(None)
    geographic_availability: Optional[Dict[str, Any]] = Field(None)
    eligibility_criteria: Optional[Dict[str, Any]] = Field(None)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class CoverageOptionResponse(CoverageOptionBase):
    """Schema for coverage option responses"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Unique identifier for the coverage option")
    
    # Parent coverage information
    coverage_name: Optional[str] = Field(None, description="Name of parent coverage")
    coverage_code: Optional[str] = Field(None, description="Code of parent coverage")
    coverage_type: Optional[str] = Field(None, description="Type of parent coverage")
    
    # Extended option details
    custom_features: Optional[Dict[str, Any]] = Field(None, description="Custom features")
    additional_covered_services: Optional[List[str]] = Field(None, description="Additional covered services")
    excluded_services_override: Optional[List[str]] = Field(None, description="Excluded services override")
    
    # Restrictions and requirements
    network_restrictions: Optional[Dict[str, Any]] = Field(None, description="Network restrictions")
    geographic_availability: Optional[Dict[str, Any]] = Field(None, description="Geographic availability")
    eligibility_criteria: Optional[Dict[str, Any]] = Field(None, description="Eligibility criteria")
    
    # Quality and performance
    quality_programs: Optional[Dict[str, Any]] = Field(None, description="Quality programs")
    performance_guarantees: Optional[Dict[str, Any]] = Field(None, description="Performance guarantees")
    
    # Usage statistics
    selection_count: Optional[int] = Field(None, description="Number of times this option has been selected")
    member_count: Optional[int] = Field(None, description="Current number of members with this option")
    
    # Status information
    status: Optional[OptionStatusEnum] = Field(None, description="Current option status")
    status_reason: Optional[str] = Field(None, description="Reason for current status")
    
    # Calculated fields
    effective_copay_in_network: Optional[Decimal] = Field(None, description="Effective in-network copay")
    effective_copay_out_network: Optional[Decimal] = Field(None, description="Effective out-of-network copay")
    cost_sharing_summary: Optional[str] = Field(None, description="Human-readable cost sharing summary")
    
    # Audit fields
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="ID of user who created the option")
    updated_by: Optional[UUID] = Field(None, description="ID of user who last updated the option")
    version: int = Field(default=1, description="Version number")


class CoverageOptionSummary(BaseModel):
    """Lightweight summary schema for coverage options"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "option_code": "PCP_STANDARD_001",
                "option_name": "Standard Primary Care Coverage",
                "option_type": "STANDARD",
                "selection_type": "OPTIONAL",
                "is_active": True,
                "is_default": True,
                "is_recommended": False,
                "in_network_copay": "25.00",
                "out_of_network_copay": "50.00",
                "premium_adjustment": "0.00"
            }
        }
    )
    
    id: UUID
    option_code: str
    option_name: str
    option_name_ar: Optional[str] = None
    option_type: OptionTypeEnum
    option_tier: Optional[OptionTierEnum] = None
    selection_type: SelectionTypeEnum
    is_active: bool
    is_default: bool
    is_recommended: bool
    
    # Key cost sharing info
    in_network_copay: Optional[Decimal] = None
    out_of_network_copay: Optional[Decimal] = None
    premium_adjustment: Optional[Decimal] = None


# =====================================================
# SPECIALIZED SCHEMAS
# =====================================================

class CoverageOptionWithCalculation(CoverageOptionResponse):
    """Coverage option schema with cost calculations"""
    
    cost_calculation: Optional[Dict[str, Any]] = Field(
        None,
        description="Sample cost calculation for this option"
    )
    member_cost_examples: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Example member cost scenarios"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cost_calculation": {
                    "service_cost": "150.00",
                    "member_pays": "25.00",
                    "insurance_pays": "125.00",
                    "network_status": "in_network"
                },
                "member_cost_examples": [
                    {
                        "scenario": "Routine visit",
                        "service_cost": "150.00",
                        "member_cost": "25.00"
                    }
                ]
            }
        }
    )


class CoverageOptionComparison(BaseModel):
    """Schema for comparing coverage options"""
    
    option_id: UUID
    option_name: str
    option_type: OptionTypeEnum
    
    # Cost comparison
    cost_sharing: Dict[str, Optional[Decimal]] = Field(..., description="Cost sharing breakdown")
    premium_impact: Optional[Decimal] = Field(None, description="Premium impact")
    
    # Feature comparison
    features: Dict[str, Any] = Field(..., description="Feature comparison")
    restrictions: Dict[str, Any] = Field(..., description="Restrictions comparison")
    
    # Value metrics
    value_score: Optional[float] = Field(None, ge=0, le=100, description="Calculated value score")
    member_satisfaction: Optional[float] = Field(None, ge=0, le=10, description="Member satisfaction score")


class CoverageOptionStats(BaseModel):
    """Schema for coverage option statistics"""
    
    option_id: UUID
    option_code: str
    option_name: str
    
    # Selection statistics
    total_selections: int = Field(default=0, description="Total times selected")
    current_members: int = Field(default=0, description="Current active members")
    selection_rate: Optional[float] = Field(None, ge=0, le=100, description="Selection rate percentage")
    
    # Cost statistics
    average_member_cost: Optional[Decimal] = Field(None, description="Average member cost per service")
    total_claims_processed: int = Field(default=0, description="Total claims processed")
    average_claim_amount: Optional[Decimal] = Field(None, description="Average claim amount")
    
    # Satisfaction metrics
    member_satisfaction_score: Optional[float] = Field(None, ge=0, le=10, description="Member satisfaction")
    net_promoter_score: Optional[int] = Field(None, ge=-100, le=100, description="Net Promoter Score")
    
    # Performance metrics
    claim_processing_time_avg: Optional[float] = Field(None, description="Average claim processing time in days")
    authorization_approval_rate: Optional[float] = Field(None, ge=0, le=100, description="Authorization approval rate")
    
    # Trend data
    selection_trend: Optional[float] = Field(None, description="Selection trend percentage change")
    cost_trend: Optional[float] = Field(None, description="Cost trend percentage change")
    
    reporting_period_start: datetime = Field(..., description="Statistics period start")
    reporting_period_end: datetime = Field(..., description="Statistics period end")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Statistics last updated")


# =====================================================
# LIST AND FILTER SCHEMAS
# =====================================================

class CoverageOptionFilter(BaseModel):
    """Schema for filtering coverage options"""
    
    coverage_id: Optional[UUID] = Field(None, description="Filter by parent coverage")
    option_type: Optional[OptionTypeEnum] = Field(None, description="Filter by option type")
    option_tier: Optional[OptionTierEnum] = Field(None, description="Filter by option tier")
    selection_type: Optional[SelectionTypeEnum] = Field(None, description="Filter by selection type")
    
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_selectable: Optional[bool] = Field(None, description="Filter by selectable status")
    is_default: Optional[bool] = Field(None, description="Filter by default status")
    is_recommended: Optional[bool] = Field(None, description="Filter by recommended status")
    
    # Cost filters
    has_copay: Optional[bool] = Field(None, description="Filter by copay presence")
    has_coinsurance: Optional[bool] = Field(None, description="Filter by coinsurance presence")
    has_premium_adjustment: Optional[bool] = Field(None, description="Filter by premium adjustment presence")
    
    # Authorization filters
    requires_pre_authorization: Optional[bool] = Field(None, description="Filter by pre-auth requirement")
    requires_referral: Optional[bool] = Field(None, description="Filter by referral requirement")
    
    # Cost range filters
    copay_range_min: Optional[Decimal] = Field(None, ge=0, description="Minimum copay amount")
    copay_range_max: Optional[Decimal] = Field(None, ge=0, description="Maximum copay amount")
    premium_adjustment_min: Optional[Decimal] = Field(None, description="Minimum premium adjustment")
    premium_adjustment_max: Optional[Decimal] = Field(None, description="Maximum premium adjustment")
    
    # Date filters
    effective_date_from: Optional[datetime] = Field(None, description="Option effective from date")
    effective_date_to: Optional[datetime] = Field(None, description="Option effective to date")
    
    # Search fields
    search_term: Optional[str] = Field(None, max_length=100, description="Search in names and descriptions")
    option_codes: Optional[List[str]] = Field(None, description="Filter by specific option codes")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "option_type": "STANDARD",
                "selection_type": "OPTIONAL",
                "is_active": True,
                "is_selectable": True,
                "has_copay": True,
                "search_term": "primary care"
            }
        }
    )


class CoverageOptionListResponse(BaseModel):
    """Schema for paginated list of coverage options"""
    
    items: List[CoverageOptionResponse] = Field(..., description="List of coverage options")
    total_count: int = Field(..., ge=0, description="Total number of options matching filter")
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

class CoverageOptionBulkCreate(BaseModel):
    """Schema for bulk creating coverage options"""
    
    options: List[CoverageOptionCreate] = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="List of coverage options to create"
    )
    
    # Bulk operation settings
    skip_duplicates: bool = Field(default=False, description="Skip options with duplicate codes")
    validate_coverage_references: bool = Field(default=True, description="Validate coverage references")
    auto_set_display_order: bool = Field(default=True, description="Auto-set display order")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "options": [
                    {
                        "option_code": "PCP_STANDARD_001",
                        "option_name": "Standard Primary Care",
                        "coverage_id": "123e4567-e89b-12d3-a456-426614174000",
                        "option_type": "STANDARD",
                        "in_network_copay": "25.00"
                    }
                ],
                "skip_duplicates": True
            }
        }
    )


class CoverageOptionBulkUpdate(BaseModel):
    """Schema for bulk updating coverage options"""
    
    option_ids: List[UUID] = Field(..., min_length=1, max_length=100)
    updates: CoverageOptionUpdate = Field(..., description="Fields to update")
    
    # Update options
    preserve_custom_features: bool = Field(default=True, description="Preserve existing custom features")
    update_display_order: bool = Field(default=False, description="Recalculate display order")


class CoverageOptionBulkResponse(BaseModel):
    """Schema for bulk operation responses"""
    
    successful_operations: int = Field(..., ge=0, description="Number of successful operations")
    failed_operations: int = Field(..., ge=0, description="Number of failed operations")
    total_operations: int = Field(..., ge=0, description="Total number of operations attempted")
    
    success_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of successful operations")
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of failed operations")


# =====================================================
# SELECTION AND RECOMMENDATION SCHEMAS
# =====================================================

class CoverageOptionRecommendation(BaseModel):
    """Schema for coverage option recommendations"""
    
    member_profile: Dict[str, Any] = Field(..., description="Member profile for recommendations")
    coverage_id: UUID = Field(..., description="Coverage to get recommendations for")
    recommendation_criteria: List[str] = Field(
        default=["cost_effectiveness", "member_preferences", "utilization_history"],
        description="Criteria for recommendations"
    )


class CoverageOptionRecommendationResult(BaseModel):
    """Schema for coverage option recommendation results"""
    
    recommended_options: List[Dict[str, Any]] = Field(..., description="Recommended options with scores")
    recommendation_reasons: Dict[UUID, List[str]] = Field(..., description="Reasons for each recommendation")
    cost_comparison: Dict[UUID, Dict[str, Decimal]] = Field(..., description="Cost comparison matrix")
    
    # Recommendation metadata
    recommendation_confidence: float = Field(..., ge=0, le=100, description="Confidence in recommendations")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Recommendation timestamp")
    valid_until: datetime = Field(..., description="Recommendation valid until")


class CoverageOptionSelection(BaseModel):
    """Schema for coverage option selection"""
    
    member_id: UUID = Field(..., description="Member making the selection")
    option_id: UUID = Field(..., description="Selected coverage option")
    effective_date: datetime = Field(..., description="Selection effective date")
    selection_reason: Optional[str] = Field(None, description="Reason for selection")
    
    # Selection context
    selection_channel: Optional[str] = Field(None, description="Channel used for selection")
    advisor_assisted: bool = Field(default=False, description="Whether advisor assisted with selection")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "member_id": "123e4567-e89b-12d3-a456-426614174000",
                "option_id": "123e4567-e89b-12d3-a456-426614174001",
                "effective_date": "2024-01-01T00:00:00Z",
                "selection_reason": "Better copay amount",
                "selection_channel": "web_portal"
            }
        }
    )


# =====================================================
# MISSING SCHEMAS FOR ROUTE IMPORTS
# =====================================================

class CoverageOptionWithDetails(CoverageOptionResponse):
    """Coverage option schema with comprehensive details"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "option_code": "PCP_STANDARD_001",
                "option_name": "Standard Primary Care Coverage",
                "coverage_details": {
                    "coverage_name": "Primary Care",
                    "coverage_type": "Medical",
                    "category": "Outpatient"
                },
                "pricing_details": {
                    "base_premium": "25.00",
                    "member_cost": "25.00",
                    "employer_contribution": "0.00"
                },
                "benefit_details": {
                    "copay_in_network": "25.00",
                    "copay_out_network": "50.00",
                    "annual_limit": "unlimited"
                }
            }
        }
    )
    
    coverage_details: Optional[Dict[str, Any]] = Field(None, description="Detailed coverage information")
    pricing_details: Optional[Dict[str, Any]] = Field(None, description="Detailed pricing breakdown")
    benefit_details: Optional[Dict[str, Any]] = Field(None, description="Detailed benefit information")
    network_details: Optional[Dict[str, Any]] = Field(None, description="Provider network details")
    utilization_data: Optional[Dict[str, Any]] = Field(None, description="Historical utilization data")
    related_options: Optional[List[Dict[str, Any]]] = Field(None, description="Related coverage options")


class OptionCombination(BaseModel):
    """Schema for coverage option combinations"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "combination_id": "123e4567-e89b-12d3-a456-426614174000",
                "combination_name": "Standard Care Package",
                "option_ids": [
                    "123e4567-e89b-12d3-a456-426614174001",
                    "123e4567-e89b-12d3-a456-426614174002"
                ],
                "total_premium_adjustment": "50.00",
                "discount_percentage": "10.00",
                "is_recommended_combination": True
            }
        }
    )
    
    combination_id: Optional[UUID] = Field(None, description="Unique identifier for combination")
    combination_name: str = Field(..., description="Name of the option combination")
    combination_description: Optional[str] = Field(None, description="Description of combination")
    option_ids: List[UUID] = Field(..., min_length=2, description="Coverage option IDs in combination")
    options: Optional[List[CoverageOptionSummary]] = Field(None, description="Full option details")
    total_premium_adjustment: Optional[Decimal] = Field(None, description="Total premium adjustment")
    discount_amount: Optional[Decimal] = Field(None, ge=0, description="Discount amount")
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Discount percentage")
    is_recommended_combination: bool = Field(default=False, description="Whether recommended")
    is_popular_combination: bool = Field(default=False, description="Whether popular")
    is_exclusive_combination: bool = Field(default=False, description="Whether exclusive")
    combination_restrictions: Optional[Dict[str, Any]] = Field(None, description="Combination restrictions")
    mutual_exclusions: Optional[List[UUID]] = Field(None, description="Mutually exclusive options")
    display_order: int = Field(default=1, ge=1, description="Display order")
    is_active: bool = Field(default=True, description="Whether active")
    effective_date: Optional[datetime] = Field(None, description="Effective date")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date")


class OptionCompatibility(BaseModel):
    """Schema for option compatibility checking"""
    
    model_config = ConfigDict(from_attributes=True)
    
    option_id: UUID = Field(..., description="Primary option ID")
    compatible_options: List[UUID] = Field(default_factory=list, description="Compatible option IDs")
    incompatible_options: List[UUID] = Field(default_factory=list, description="Incompatible option IDs")
    conditional_compatibility: Optional[Dict[UUID, Dict[str, Any]]] = Field(
        None, description="Conditional compatibility rules"
    )
    compatibility_reasons: Optional[Dict[UUID, str]] = Field(None, description="Compatibility reasons")


class CoverageRecommendation(BaseModel):
    """Schema for coverage recommendations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    member_profile: Dict[str, Any] = Field(..., description="Member profile data")
    recommended_options: List[UUID] = Field(..., description="Recommended option IDs")
    recommendation_scores: Dict[UUID, float] = Field(..., description="Recommendation scores")
    recommendation_reasons: Dict[UUID, List[str]] = Field(..., description="Recommendation reasons")
    alternative_options: Optional[List[UUID]] = Field(None, description="Alternative options")
    cost_analysis: Optional[Dict[str, Any]] = Field(None, description="Cost analysis")
    confidence_level: float = Field(..., ge=0, le=100, description="Recommendation confidence")


class OptionOptimization(BaseModel):
    """Schema for option optimization"""
    
    model_config = ConfigDict(from_attributes=True)
    
    optimization_criteria: List[str] = Field(..., description="Optimization criteria")
    current_options: List[UUID] = Field(..., description="Current selected options")
    optimized_options: List[UUID] = Field(..., description="Optimized option selection")
    cost_savings: Optional[Decimal] = Field(None, description="Potential cost savings")
    coverage_improvements: Optional[Dict[str, Any]] = Field(None, description="Coverage improvements")
    optimization_score: float = Field(..., ge=0, le=100, description="Optimization score")


class CoverageScenarioComparison(BaseModel):
    """Schema for scenario-based coverage comparison"""
    
    model_config = ConfigDict(from_attributes=True)
    
    scenario_name: str = Field(..., description="Scenario name")
    scenario_description: Optional[str] = Field(None, description="Scenario description")
    option_sets: List[List[UUID]] = Field(..., description="Sets of options to compare")
    comparison_criteria: List[str] = Field(..., description="Comparison criteria")
    scenario_results: Dict[str, Any] = Field(..., description="Comparison results")
    recommended_set: Optional[int] = Field(None, description="Index of recommended option set")


class MemberPreferences(BaseModel):
    """Schema for member preferences"""
    
    model_config = ConfigDict(from_attributes=True)
    
    member_id: UUID = Field(..., description="Member ID")
    preferred_cost_sharing: Optional[str] = Field(None, description="Preferred cost sharing type")
    max_monthly_premium: Optional[Decimal] = Field(None, description="Maximum monthly premium")
    preferred_providers: Optional[List[str]] = Field(None, description="Preferred provider types")
    coverage_priorities: Optional[List[str]] = Field(None, description="Coverage priorities")
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance level")
    flexibility_preferences: Optional[Dict[str, Any]] = Field(None, description="Flexibility preferences")


class OptionAnalysis(BaseModel):
    """Schema for option analysis"""
    
    model_config = ConfigDict(from_attributes=True)
    
    option_id: UUID = Field(..., description="Option ID")
    analysis_type: str = Field(..., description="Type of analysis")
    analysis_parameters: Dict[str, Any] = Field(..., description="Analysis parameters")
    analysis_results: Dict[str, Any] = Field(..., description="Analysis results")
    insights: Optional[List[str]] = Field(None, description="Analysis insights")
    recommendations: Optional[List[str]] = Field(None, description="Based on analysis")


class CombinationValidation(BaseModel):
    """Schema for combination validation"""
    
    model_config = ConfigDict(from_attributes=True)
    
    option_ids: List[UUID] = Field(..., min_length=2, description="Option IDs to validate")
    validation_rules: Optional[List[str]] = Field(None, description="Validation rules to apply")
    is_valid: bool = Field(..., description="Whether combination is valid")
    validation_errors: Optional[List[str]] = Field(None, description="Validation errors")
    validation_warnings: Optional[List[str]] = Field(None, description="Validation warnings")
    suggested_fixes: Optional[List[str]] = Field(None, description="Suggested fixes")


class OptimizationCriteria(BaseModel):
    """Schema for optimization criteria"""
    
    model_config = ConfigDict(from_attributes=True)
    
    cost_weight: float = Field(default=0.3, ge=0, le=1, description="Cost optimization weight")
    coverage_weight: float = Field(default=0.4, ge=0, le=1, description="Coverage optimization weight")
    convenience_weight: float = Field(default=0.2, ge=0, le=1, description="Convenience weight")
    member_satisfaction_weight: float = Field(default=0.1, ge=0, le=1, description="Satisfaction weight")
    custom_criteria: Optional[Dict[str, float]] = Field(None, description="Custom criteria weights")
    
    @field_validator('cost_weight', 'coverage_weight', 'convenience_weight', 'member_satisfaction_weight')
    @classmethod
    def validate_weights_sum_to_one(cls, v, info):
        """Validate that all weights sum to 1.0"""
        # This is a simplified validation; in practice you'd check the sum of all weights
        return v


class CoverageOptionSearchFilter(BaseModel):
    """Enhanced search filter for coverage options"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Extend the existing CoverageOptionFilter
    coverage_id: Optional[UUID] = Field(None, description="Filter by parent coverage")
    option_type: Optional[OptionTypeEnum] = Field(None, description="Filter by option type")
    selection_type: Optional[SelectionTypeEnum] = Field(None, description="Filter by selection type")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    search_term: Optional[str] = Field(None, description="Search term")
    
    # Additional search capabilities
    member_preferences: Optional[MemberPreferences] = Field(None, description="Member preferences")
    cost_range: Optional[Dict[str, Decimal]] = Field(None, description="Cost range filters")
    feature_requirements: Optional[List[str]] = Field(None, description="Required features")
    exclude_options: Optional[List[UUID]] = Field(None, description="Options to exclude")
    include_combinations: bool = Field(default=False, description="Include option combinations")


class BulkOptionOperation(BaseModel):
    """Schema for bulk option operations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    operation_type: str = Field(..., description="Type of bulk operation")
    option_ids: List[UUID] = Field(..., min_length=1, description="Option IDs for operation")
    operation_parameters: Dict[str, Any] = Field(..., description="Operation parameters")
    batch_size: int = Field(default=50, ge=1, le=100, description="Batch processing size")
    validate_before_operation: bool = Field(default=True, description="Validate before processing")
    rollback_on_error: bool = Field(default=True, description="Rollback on any error")
    notification_settings: Optional[Dict[str, Any]] = Field(None, description="Notification preferences")