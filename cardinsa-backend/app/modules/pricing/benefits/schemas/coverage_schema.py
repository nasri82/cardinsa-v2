# app/modules/benefits/schemas/coverage_schema.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum
from decimal import Decimal


# =====================================================
# ENUMS FOR VALIDATION
# =====================================================

class CoverageTypeEnum(str, Enum):
    """Enumeration of coverage types"""
    MEDICAL = "MEDICAL"
    DENTAL = "DENTAL"
    VISION = "VISION"
    PRESCRIPTION = "PRESCRIPTION"
    MENTAL_HEALTH = "MENTAL_HEALTH"
    MATERNITY = "MATERNITY"
    EMERGENCY = "EMERGENCY"
    PREVENTIVE = "PREVENTIVE"
    DIAGNOSTIC = "DIAGNOSTIC"
    THERAPEUTIC = "THERAPEUTIC"
    REHABILITATIVE = "REHABILITATIVE"
    HABILITATIVE = "HABILITATIVE"
    PEDIATRIC = "PEDIATRIC"
    HOSPICE = "HOSPICE"
    HOME_HEALTH = "HOME_HEALTH"
    DURABLE_MEDICAL_EQUIPMENT = "DURABLE_MEDICAL_EQUIPMENT"


class CoverageLevelEnum(str, Enum):
    """Enumeration of coverage levels"""
    NOT_COVERED = "NOT_COVERED"
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    ENHANCED = "ENHANCED"
    COMPREHENSIVE = "COMPREHENSIVE"
    UNLIMITED = "UNLIMITED"


class NetworkTypeEnum(str, Enum):
    """Enumeration of network types"""
    IN_NETWORK_ONLY = "IN_NETWORK_ONLY"
    OUT_OF_NETWORK_ONLY = "OUT_OF_NETWORK_ONLY"
    BOTH_NETWORKS = "BOTH_NETWORKS"
    PREFERRED_NETWORK = "PREFERRED_NETWORK"
    NO_NETWORK = "NO_NETWORK"


class CoverageStatusEnum(str, Enum):
    """Enumeration of coverage status values"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class UtilizationTrackingEnum(str, Enum):
    """Enumeration of utilization tracking types"""
    VISITS = "VISITS"
    DAYS = "DAYS"
    UNITS = "UNITS"
    PROCEDURES = "PROCEDURES"
    EPISODES = "EPISODES"
    DOLLARS = "DOLLARS"


# =====================================================
# BASE SCHEMA
# =====================================================

class CoverageBase(BaseModel):
    """Base schema for coverage with common fields"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "coverage_code": "MED_PCP_001",
                "coverage_name": "Primary Care Office Visits",
                "coverage_type": "MEDICAL",
                "benefit_type_id": "123e4567-e89b-12d3-a456-426614174000",
                "coverage_level": "COMPREHENSIVE",
                "in_network_copay": "25.00",
                "out_of_network_copay": "50.00",
                "visit_limit_per_year": 12,
                "requires_referral": False,
                "deductible_applies": False
            }
        }
    )
    
    coverage_code: str = Field(
        ..., 
        min_length=1, 
        max_length=30,
        description="Unique code identifying the coverage",
        examples=["MED_PCP_001"]
    )
    coverage_name: str = Field(
        ..., 
        min_length=1, 
        max_length=150,
        description="Display name of the coverage",
        examples=["Primary Care Physician Office Visits"]
    )
    coverage_name_ar: Optional[str] = Field(
        None, 
        max_length=150,
        description="Arabic translation of coverage name"
    )
    
    # Classification
    coverage_type: CoverageTypeEnum = Field(
        ...,
        description="Type classification of the coverage"
    )
    benefit_type_id: UUID = Field(
        ...,
        description="ID of the parent benefit type"
    )
    
    # Coverage level and network
    coverage_level: CoverageLevelEnum = Field(
        default=CoverageLevelEnum.STANDARD,
        description="Level of coverage provided"
    )
    network_type: NetworkTypeEnum = Field(
        default=NetworkTypeEnum.BOTH_NETWORKS,
        description="Network requirements for this coverage"
    )
    
    # Descriptive fields
    description: Optional[str] = Field(
        None,
        description="Detailed description of what is covered"
    )
    description_ar: Optional[str] = Field(
        None,
        description="Arabic translation of description"
    )
    coverage_summary: Optional[str] = Field(
        None,
        max_length=500,
        description="Summary of coverage for member materials"
    )
    
    # Cost-sharing structure
    in_network_copay: Optional[Decimal] = Field(
        None,
        ge=0,
        description="In-network copay amount"
    )
    out_of_network_copay: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Out-of-network copay amount"
    )
    in_network_coinsurance: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="In-network coinsurance percentage"
    )
    out_of_network_coinsurance: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Out-of-network coinsurance percentage"
    )
    
    # Deductible application
    deductible_applies: bool = Field(
        default=True,
        description="Whether deductible applies to this coverage"
    )
    separate_deductible: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Separate deductible specific to this coverage"
    )
    
    # Coverage limits
    annual_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Annual coverage limit in currency"
    )
    lifetime_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Lifetime coverage limit in currency"
    )
    
    # Visit and utilization limits
    visit_limit_per_year: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum visits allowed per year"
    )
    visit_limit_per_condition: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum visits per condition/episode"
    )
    utilization_tracking: Optional[UtilizationTrackingEnum] = Field(
        None,
        description="How utilization is tracked for this coverage"
    )
    
    # Authorization and referral requirements
    requires_pre_authorization: bool = Field(
        default=False,
        description="Whether pre-authorization is required"
    )
    requires_referral: bool = Field(
        default=False,
        description="Whether referral is required"
    )
    
    # Status and availability
    is_active: bool = Field(
        default=True,
        description="Whether the coverage is currently active"
    )
    is_available: bool = Field(
        default=True,
        description="Whether the coverage is available for selection"
    )
    
    # Effective dates
    effective_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="When coverage becomes effective"
    )
    expiry_date: Optional[datetime] = Field(
        None,
        description="When coverage expires"
    )

    @field_validator('coverage_code')
    @classmethod
    def validate_coverage_code(cls, v: str) -> str:
        """Validate coverage code format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Coverage code must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()

    @field_validator('expiry_date')
    @classmethod
    def validate_expiry_date(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate expiry date is after effective date"""
        if v and hasattr(info, 'data') and 'effective_date' in info.data:
            effective_date = info.data['effective_date']
            if v <= effective_date:
                raise ValueError('Expiry date must be after effective date')
        return v


# =====================================================
# CREATE SCHEMA
# =====================================================

class CoverageCreate(CoverageBase):
    """Schema for creating a new coverage"""
    
    # Service specifications
    covered_services: Optional[List[str]] = Field(
        None,
        description="List of covered services"
    )
    excluded_services: Optional[List[str]] = Field(
        None,
        description="List of excluded services"
    )
    
    # Provider and facility requirements
    provider_requirements: Optional[Dict[str, Any]] = Field(
        None,
        description="Provider qualification requirements"
    )
    facility_requirements: Optional[Dict[str, Any]] = Field(
        None,
        description="Facility requirements"
    )
    
    # Age and demographic restrictions
    age_restrictions: Optional[Dict[str, Any]] = Field(
        None,
        description="Age-based coverage restrictions"
    )
    gender_restrictions: Optional[List[str]] = Field(
        None,
        description="Gender restrictions if any"
    )
    
    # Geographic limitations
    geographic_limitations: Optional[Dict[str, Any]] = Field(
        None,
        description="Geographic coverage limitations"
    )
    
    # Waiting periods and limitations
    waiting_period_days: Optional[int] = Field(
        None,
        ge=0,
        description="Waiting period before coverage begins"
    )
    pre_existing_condition_exclusion: Optional[int] = Field(
        None,
        ge=0,
        description="Pre-existing condition exclusion period in months"
    )
    
    # Quality and outcome measures
    quality_measures: Optional[Dict[str, Any]] = Field(
        None,
        description="Quality measures and requirements"
    )
    outcome_tracking: Optional[Dict[str, Any]] = Field(
        None,
        description="Outcome tracking requirements"
    )


# =====================================================
# UPDATE SCHEMA
# =====================================================

class CoverageUpdate(BaseModel):
    """Schema for updating an existing coverage"""
    
    model_config = ConfigDict(from_attributes=True)
    
    coverage_name: Optional[str] = Field(None, min_length=1, max_length=150)
    coverage_name_ar: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = Field(None)
    description_ar: Optional[str] = Field(None)
    coverage_summary: Optional[str] = Field(None, max_length=500)
    
    coverage_type: Optional[CoverageTypeEnum] = Field(None)
    coverage_level: Optional[CoverageLevelEnum] = Field(None)
    network_type: Optional[NetworkTypeEnum] = Field(None)
    
    # Cost sharing updates
    in_network_copay: Optional[Decimal] = Field(None, ge=0)
    out_of_network_copay: Optional[Decimal] = Field(None, ge=0)
    in_network_coinsurance: Optional[Decimal] = Field(None, ge=0, le=100)
    out_of_network_coinsurance: Optional[Decimal] = Field(None, ge=0, le=100)
    
    deductible_applies: Optional[bool] = Field(None)
    separate_deductible: Optional[Decimal] = Field(None, ge=0)
    
    # Limit updates
    annual_limit: Optional[Decimal] = Field(None, ge=0)
    lifetime_limit: Optional[Decimal] = Field(None, ge=0)
    visit_limit_per_year: Optional[int] = Field(None, ge=0)
    visit_limit_per_condition: Optional[int] = Field(None, ge=0)
    utilization_tracking: Optional[UtilizationTrackingEnum] = Field(None)
    
    # Authorization updates
    requires_pre_authorization: Optional[bool] = Field(None)
    requires_referral: Optional[bool] = Field(None)
    
    # Status updates
    is_active: Optional[bool] = Field(None)
    is_available: Optional[bool] = Field(None)
    expiry_date: Optional[datetime] = Field(None)
    
    # Service and requirement updates
    covered_services: Optional[List[str]] = Field(None)
    excluded_services: Optional[List[str]] = Field(None)
    provider_requirements: Optional[Dict[str, Any]] = Field(None)
    facility_requirements: Optional[Dict[str, Any]] = Field(None)
    age_restrictions: Optional[Dict[str, Any]] = Field(None)
    gender_restrictions: Optional[List[str]] = Field(None)
    geographic_limitations: Optional[Dict[str, Any]] = Field(None)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class CoverageResponse(CoverageBase):
    """Schema for coverage responses"""
    
    id: UUID = Field(..., description="Unique identifier for the coverage")
    
    # Related entity information
    benefit_type_name: Optional[str] = Field(None, description="Name of parent benefit type")
    benefit_type_code: Optional[str] = Field(None, description="Code of parent benefit type")
    category_name: Optional[str] = Field(None, description="Name of benefit category")
    
    # Extended coverage details
    covered_services: Optional[List[str]] = Field(None, description="List of covered services")
    excluded_services: Optional[List[str]] = Field(None, description="List of excluded services")
    
    # Requirements and restrictions
    provider_requirements: Optional[Dict[str, Any]] = Field(None, description="Provider requirements")
    facility_requirements: Optional[Dict[str, Any]] = Field(None, description="Facility requirements")
    age_restrictions: Optional[Dict[str, Any]] = Field(None, description="Age restrictions")
    gender_restrictions: Optional[List[str]] = Field(None, description="Gender restrictions")
    geographic_limitations: Optional[Dict[str, Any]] = Field(None, description="Geographic limitations")
    
    # Waiting periods and exclusions
    waiting_period_days: Optional[int] = Field(None, description="Waiting period in days")
    pre_existing_condition_exclusion: Optional[int] = Field(None, description="Pre-existing condition exclusion period")
    
    # Quality and tracking
    quality_measures: Optional[Dict[str, Any]] = Field(None, description="Quality measures")
    outcome_tracking: Optional[Dict[str, Any]] = Field(None, description="Outcome tracking")
    
    # Statistics
    coverage_options_count: Optional[int] = Field(None, description="Number of coverage options")
    active_plans_count: Optional[int] = Field(None, description="Number of plans using this coverage")
    
    # Status information
    status: Optional[CoverageStatusEnum] = Field(None, description="Current coverage status")
    status_reason: Optional[str] = Field(None, description="Reason for current status")
    
    # Audit fields
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="ID of user who created the coverage")
    updated_by: Optional[UUID] = Field(None, description="ID of user who last updated the coverage")
    version: int = Field(default=1, description="Version number")


class CoverageSummary(BaseModel):
    """Lightweight summary schema for coverages"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "coverage_code": "MED_PCP_001",
                "coverage_name": "Primary Care Office Visits",
                "coverage_type": "MEDICAL",
                "coverage_level": "COMPREHENSIVE",
                "network_type": "BOTH_NETWORKS",
                "is_active": True,
                "in_network_copay": "25.00",
                "out_of_network_copay": "50.00",
                "deductible_applies": False,
                "requires_pre_authorization": False,
                "requires_referral": False
            }
        }
    )
    
    id: UUID
    coverage_code: str
    coverage_name: str
    coverage_name_ar: Optional[str] = None
    coverage_type: CoverageTypeEnum
    coverage_level: CoverageLevelEnum
    network_type: NetworkTypeEnum
    is_active: bool
    
    # Key cost sharing info
    in_network_copay: Optional[Decimal] = None
    out_of_network_copay: Optional[Decimal] = None
    deductible_applies: bool = True
    requires_pre_authorization: bool = False
    requires_referral: bool = False


# =====================================================
# SPECIALIZED SCHEMAS
# =====================================================

class CoverageWithOptions(CoverageResponse):
    """Coverage schema including related coverage options"""
    
    coverage_options: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of coverage options/variants"
    )
    default_option_id: Optional[UUID] = Field(None, description="Default coverage option ID")
    option_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of coverage options"
    )


class CoverageCostCalculation(BaseModel):
    """Schema for coverage cost calculation results"""
    
    model_config = ConfigDict(from_attributes=True)
    
    coverage_id: UUID
    coverage_name: str
    service_cost: Decimal = Field(..., description="Original service cost")
    
    # Cost breakdown
    member_deductible: Decimal = Field(default=Decimal('0'), description="Deductible amount member pays")
    member_copay: Decimal = Field(default=Decimal('0'), description="Copay amount member pays")
    member_coinsurance: Decimal = Field(default=Decimal('0'), description="Coinsurance amount member pays")
    total_member_pays: Decimal = Field(..., description="Total amount member pays")
    insurance_pays: Decimal = Field(..., description="Amount insurance pays")
    
    # Calculation details
    network_status: str = Field(..., description="In-network or out-of-network")
    deductible_applied: bool = Field(..., description="Whether deductible was applied")
    coverage_applies: bool = Field(..., description="Whether coverage applies to this service")
    
    # Utilization tracking
    visits_used: Optional[int] = Field(None, description="Visits used this period")
    visits_remaining: Optional[int] = Field(None, description="Visits remaining this period")
    
    calculation_date: datetime = Field(default_factory=datetime.utcnow, description="When calculation was performed")


# =====================================================
# LIST AND FILTER SCHEMAS
# =====================================================

class CoverageFilter(BaseModel):
    """Schema for filtering coverages"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "coverage_type": "MEDICAL",
                "coverage_level": "COMPREHENSIVE",
                "network_type": "BOTH_NETWORKS",
                "is_active": True,
                "requires_pre_authorization": False,
                "has_copay": True,
                "search_term": "primary care"
            }
        }
    )
    
    coverage_type: Optional[CoverageTypeEnum] = Field(None, description="Filter by coverage type")
    benefit_type_id: Optional[UUID] = Field(None, description="Filter by parent benefit type")
    coverage_level: Optional[CoverageLevelEnum] = Field(None, description="Filter by coverage level")
    network_type: Optional[NetworkTypeEnum] = Field(None, description="Filter by network type")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_available: Optional[bool] = Field(None, description="Filter by available status")
    
    # Authorization filters
    requires_pre_authorization: Optional[bool] = Field(None, description="Filter by pre-auth requirement")
    requires_referral: Optional[bool] = Field(None, description="Filter by referral requirement")
    
    # Cost sharing filters
    has_copay: Optional[bool] = Field(None, description="Filter by copay presence")
    has_coinsurance: Optional[bool] = Field(None, description="Filter by coinsurance presence")
    deductible_applies: Optional[bool] = Field(None, description="Filter by deductible applicability")
    
    # Limit filters
    has_visit_limits: Optional[bool] = Field(None, description="Filter by visit limit presence")
    has_annual_limit: Optional[bool] = Field(None, description="Filter by annual limit presence")
    has_lifetime_limit: Optional[bool] = Field(None, description="Filter by lifetime limit presence")
    
    # Cost range filters
    copay_range_min: Optional[Decimal] = Field(None, ge=0, description="Minimum copay amount")
    copay_range_max: Optional[Decimal] = Field(None, ge=0, description="Maximum copay amount")
    
    # Date filters
    effective_date_from: Optional[datetime] = Field(None, description="Coverage effective from date")
    effective_date_to: Optional[datetime] = Field(None, description="Coverage effective to date")
    
    # Search fields
    search_term: Optional[str] = Field(None, max_length=100, description="Search in names and descriptions")
    coverage_codes: Optional[List[str]] = Field(None, description="Filter by specific coverage codes")


class CoverageListResponse(BaseModel):
    """Schema for paginated list of coverages"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[CoverageResponse] = Field(..., description="List of coverages")
    total_count: int = Field(..., ge=0, description="Total number of coverages matching filter")
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

class CoverageBulkCreate(BaseModel):
    """Schema for bulk creating coverages"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "coverages": [
                    {
                        "coverage_code": "MED_PCP_001",
                        "coverage_name": "Primary Care Visits",
                        "coverage_type": "MEDICAL",
                        "benefit_type_id": "123e4567-e89b-12d3-a456-426614174000",
                        "in_network_copay": "25.00"
                    }
                ],
                "skip_duplicates": True
            }
        }
    )
    
    coverages: List[CoverageCreate] = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="List of coverages to create"
    )
    
    # Bulk operation settings
    skip_duplicates: bool = Field(default=False, description="Skip coverages with duplicate codes")
    validate_benefit_types: bool = Field(default=True, description="Validate benefit type references")
    create_missing_options: bool = Field(default=False, description="Auto-create basic coverage options")


class CoverageBulkUpdate(BaseModel):
    """Schema for bulk updating coverages"""
    
    model_config = ConfigDict(from_attributes=True)
    
    coverage_ids: List[UUID] = Field(..., min_length=1, max_length=100)
    updates: CoverageUpdate = Field(..., description="Fields to update")
    
    # Update options
    update_related_options: bool = Field(default=False, description="Also update related coverage options")
    preserve_customizations: bool = Field(default=True, description="Preserve existing customizations")


class CoverageBulkResponse(BaseModel):
    """Schema for bulk operation responses"""
    
    model_config = ConfigDict(from_attributes=True)
    
    successful_operations: int = Field(..., ge=0, description="Number of successful operations")
    failed_operations: int = Field(..., ge=0, description="Number of failed operations")
    total_operations: int = Field(..., ge=0, description="Total number of operations attempted")
    
    success_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of successful operations")
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of failed operations")
    
    # Additional bulk operation results
    created_coverage_options: Optional[int] = Field(None, description="Number of coverage options auto-created")
    updated_related_entities: Optional[int] = Field(None, description="Number of related entities updated")


# =====================================================
# SCHEMA REGISTRY
# =====================================================

COVERAGE_SCHEMAS = {
    'base': CoverageBase,
    'create': CoverageCreate,
    'update': CoverageUpdate,
    'response': CoverageResponse,
    'summary': CoverageSummary,
    'with_options': CoverageWithOptions,
    'cost_calculation': CoverageCostCalculation,
    'filter': CoverageFilter,
    'list_response': CoverageListResponse,
    'bulk_create': CoverageBulkCreate,
    'bulk_update': CoverageBulkUpdate,
    'bulk_response': CoverageBulkResponse,
}

# Export all schemas for easy importing
__all__ = list(COVERAGE_SCHEMAS.keys()) + [
    'CoverageTypeEnum', 'CoverageLevelEnum', 'NetworkTypeEnum',
    'CoverageStatusEnum', 'UtilizationTrackingEnum', 'COVERAGE_SCHEMAS'
]