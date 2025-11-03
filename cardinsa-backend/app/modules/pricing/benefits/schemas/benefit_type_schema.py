# app/modules/benefits/schemas/benefit_type_schema.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum
from decimal import Decimal


# =====================================================
# ENUMS FOR VALIDATION
# =====================================================

class BenefitTypeEnum(str, Enum):
    """Enumeration of benefit type classifications"""
    PREVENTIVE = "PREVENTIVE"
    PRIMARY_CARE = "PRIMARY_CARE"
    SPECIALIST_CARE = "SPECIALIST_CARE"
    INPATIENT = "INPATIENT"
    OUTPATIENT = "OUTPATIENT"
    EMERGENCY = "EMERGENCY"
    URGENT_CARE = "URGENT_CARE"
    DIAGNOSTIC = "DIAGNOSTIC"
    THERAPEUTIC = "THERAPEUTIC"
    PRESCRIPTION = "PRESCRIPTION"
    DENTAL = "DENTAL"
    VISION = "VISION"
    MENTAL_HEALTH = "MENTAL_HEALTH"
    MATERNITY = "MATERNITY"
    REHABILITATION = "REHABILITATION"
    HOME_HEALTH = "HOME_HEALTH"
    SKILLED_NURSING = "SKILLED_NURSING"
    DURABLE_MEDICAL_EQUIPMENT = "DURABLE_MEDICAL_EQUIPMENT"
    WELLNESS = "WELLNESS"
    SUPPLEMENTAL = "SUPPLEMENTAL"


class CoverageLevelEnum(str, Enum):
    """Enumeration of coverage levels"""
    NONE = "NONE"
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    COMPREHENSIVE = "COMPREHENSIVE"
    UNLIMITED = "UNLIMITED"


class BenefitStatusEnum(str, Enum):
    """Enumeration of benefit status values"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    SUSPENDED = "SUSPENDED"


# =====================================================
# BASE SCHEMA
# =====================================================

class BenefitTypeBase(BaseModel):
    """Base schema for benefit type with common fields"""
    
    type_code: str = Field(
        ..., 
        min_length=1, 
        max_length=30,
        description="Unique code identifying the benefit type",
        examples=["PRIM_CARE_001"]
    )
    type_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Display name of the benefit type",
        examples=["Primary Care Physician Visits"]
    )
    type_name_ar: Optional[str] = Field(
        None, 
        max_length=100,
        description="Arabic translation of type name",
        examples=["زيارات طبيب الرعاية الأولية"]
    )
    
    # Classification
    benefit_type: BenefitTypeEnum = Field(
        ...,
        description="Classification of the benefit type"
    )
    benefit_category_id: UUID = Field(
        ...,
        description="ID of the parent benefit category"
    )
    
    # Descriptive fields
    description: Optional[str] = Field(
        None,
        description="Detailed description of the benefit type",
        examples=["Coverage for routine visits to primary care physicians including annual physicals and sick visits"]
    )
    description_ar: Optional[str] = Field(
        None,
        description="Arabic translation of description"
    )
    short_description: Optional[str] = Field(
        None, 
        max_length=255,
        description="Brief description for display purposes",
        examples=["Primary care visits with your family doctor"]
    )
    
    # Coverage details
    coverage_level: CoverageLevelEnum = Field(
        default=CoverageLevelEnum.STANDARD,
        description="Level of coverage provided"
    )
    is_essential_health_benefit: bool = Field(
        default=False,
        description="Whether this is an ACA Essential Health Benefit"
    )
    
    # Service specifications
    service_category: Optional[str] = Field(
        None,
        max_length=50,
        description="Category of medical service",
        examples=["PROFESSIONAL_SERVICES"]
    )
    procedure_codes: Optional[List[str]] = Field(
        None,
        description="Associated CPT/HCPCS procedure codes",
        examples=[["99201", "99213", "99395"]]
    )
    diagnosis_codes: Optional[List[str]] = Field(
        None,
        description="Associated ICD-10 diagnosis codes",
        examples=[["Z00.00", "Z00.01"]]
    )
    
    # Network and provider requirements
    network_requirements: Optional[Dict[str, Any]] = Field(
        None,
        description="Network and provider requirements",
        examples=[{
            "in_network_required": False,
            "referral_required": False,
            "prior_auth_required": False
        }]
    )
    
    # Display and ordering
    display_order: int = Field(
        default=1,
        ge=1,
        description="Order for displaying benefit types",
        examples=[1]
    )
    is_user_selectable: bool = Field(
        default=True,
        description="Whether users can select this benefit type"
    )
    
    # Status and availability
    is_active: bool = Field(
        default=True,
        description="Whether the benefit type is currently active"
    )
    is_available: bool = Field(
        default=True,
        description="Whether the benefit type is available for use"
    )


# =====================================================
# CREATE SCHEMA
# =====================================================

class BenefitTypeCreate(BenefitTypeBase):
    """Schema for creating a new benefit type"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type_code": "PRIM_CARE_001",
                "type_name": "Primary Care Physician Visits",
                "type_name_ar": "زيارات طبيب الرعاية الأولية",
                "benefit_type": "PRIMARY_CARE",
                "benefit_category_id": "123e4567-e89b-12d3-a456-426614174000",
                "description": "Routine visits to primary care physicians",
                "coverage_level": "COMPREHENSIVE",
                "default_copay_amount": "25.00",
                "requires_referral": False,
                "is_essential_health_benefit": True
            }
        }
    )
    
    # Additional creation fields
    default_copay_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Default copay amount for this benefit type",
        examples=[Decimal("25.00")]
    )
    default_coinsurance_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Default coinsurance percentage",
        examples=[Decimal("20.00")]
    )
    default_deductible_applies: bool = Field(
        default=True,
        description="Whether deductible applies by default"
    )
    
    # Service configuration
    requires_pre_authorization: bool = Field(
        default=False,
        description="Whether pre-authorization is required"
    )
    requires_referral: bool = Field(
        default=False,
        description="Whether referral is required"
    )
    
    # Age and demographic restrictions
    age_restrictions: Optional[Dict[str, Any]] = Field(
        None,
        description="Age-based restrictions",
        examples=[{
            "min_age": 0,
            "max_age": 120,
            "pediatric_age_limit": 18
        }]
    )
    gender_restrictions: Optional[List[str]] = Field(
        None,
        description="Gender restrictions if any",
        examples=[["F"]]  # For maternity benefits
    )
    
    # Regulatory and compliance
    regulatory_codes: Optional[List[str]] = Field(
        None,
        description="Regulatory classification codes"
    )
    compliance_requirements: Optional[Dict[str, Any]] = Field(
        None,
        description="Compliance requirements and notes"
    )
    
    @field_validator('type_code')
    @classmethod
    def validate_type_code(cls, v):
        """Validate benefit type code format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Type code must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()
    
    @field_validator('procedure_codes')
    @classmethod
    def validate_procedure_codes(cls, v):
        """Validate procedure codes format"""
        if v:
            for code in v:
                if not code.isalnum():
                    raise ValueError(f'Procedure code {code} must be alphanumeric')
        return v
    
    @field_validator('diagnosis_codes')
    @classmethod
    def validate_diagnosis_codes(cls, v):
        """Validate diagnosis codes format"""
        if v:
            for code in v:
                if not code.replace('.', '').isalnum():
                    raise ValueError(f'Diagnosis code {code} must be alphanumeric with optional dots')
        return v


# =====================================================
# UPDATE SCHEMA
# =====================================================

class BenefitTypeUpdate(BaseModel):
    """Schema for updating an existing benefit type"""
    
    type_name: Optional[str] = Field(None, min_length=1, max_length=100)
    type_name_ar: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None)
    description_ar: Optional[str] = Field(None)
    short_description: Optional[str] = Field(None, max_length=255)
    
    benefit_type: Optional[BenefitTypeEnum] = Field(None)
    coverage_level: Optional[CoverageLevelEnum] = Field(None)
    is_essential_health_benefit: Optional[bool] = Field(None)
    
    service_category: Optional[str] = Field(None, max_length=50)
    procedure_codes: Optional[List[str]] = Field(None)
    diagnosis_codes: Optional[List[str]] = Field(None)
    
    network_requirements: Optional[Dict[str, Any]] = Field(None)
    
    default_copay_amount: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    default_coinsurance_percentage: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2)
    default_deductible_applies: Optional[bool] = Field(None)
    
    requires_pre_authorization: Optional[bool] = Field(None)
    requires_referral: Optional[bool] = Field(None)
    
    age_restrictions: Optional[Dict[str, Any]] = Field(None)
    gender_restrictions: Optional[List[str]] = Field(None)
    
    display_order: Optional[int] = Field(None, ge=1)
    is_user_selectable: Optional[bool] = Field(None)
    is_active: Optional[bool] = Field(None)
    is_available: Optional[bool] = Field(None)
    
    regulatory_codes: Optional[List[str]] = Field(None)
    compliance_requirements: Optional[Dict[str, Any]] = Field(None)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class BenefitTypeResponse(BenefitTypeBase):
    """Schema for benefit type responses"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Unique identifier for the benefit type")
    
    # Related entity information
    category_name: Optional[str] = Field(None, description="Name of parent benefit category")
    category_code: Optional[str] = Field(None, description="Code of parent benefit category")
    
    # Cost-sharing defaults
    default_copay_amount: Optional[Decimal] = Field(None, description="Default copay amount")
    default_coinsurance_percentage: Optional[Decimal] = Field(None, description="Default coinsurance percentage")
    default_deductible_applies: bool = Field(default=True, description="Whether deductible applies by default")
    
    # Authorization requirements
    requires_pre_authorization: bool = Field(default=False, description="Pre-authorization requirement")
    requires_referral: bool = Field(default=False, description="Referral requirement")
    
    # Restrictions
    age_restrictions: Optional[Dict[str, Any]] = Field(None, description="Age-based restrictions")
    gender_restrictions: Optional[List[str]] = Field(None, description="Gender restrictions")
    
    # Regulatory information
    regulatory_codes: Optional[List[str]] = Field(None, description="Regulatory codes")
    compliance_requirements: Optional[Dict[str, Any]] = Field(None, description="Compliance requirements")
    
    # Statistics
    coverage_count: Optional[int] = Field(None, description="Number of coverages using this benefit type")
    active_coverage_count: Optional[int] = Field(None, description="Number of active coverages")
    
    # Status
    status: Optional[BenefitStatusEnum] = Field(None, description="Current benefit type status")
    status_reason: Optional[str] = Field(None, description="Reason for current status")
    
    # Audit fields
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="ID of user who created the benefit type")
    updated_by: Optional[UUID] = Field(None, description="ID of user who last updated the benefit type")
    version: int = Field(default=1, description="Version number")


class BenefitTypeSummary(BaseModel):
    """Lightweight summary schema for benefit types"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type_code": "PRIM_CARE_001",
                "type_name": "Primary Care Visits",
                "benefit_type": "PRIMARY_CARE",
                "coverage_level": "COMPREHENSIVE",
                "is_active": True,
                "is_essential_health_benefit": True,
                "default_copay_amount": "25.00",
                "requires_pre_authorization": False,
                "requires_referral": False
            }
        }
    )
    
    id: UUID
    type_code: str
    type_name: str
    type_name_ar: Optional[str] = None
    benefit_type: BenefitTypeEnum
    coverage_level: CoverageLevelEnum
    is_active: bool
    is_essential_health_benefit: bool
    default_copay_amount: Optional[Decimal] = None
    requires_pre_authorization: bool = False
    requires_referral: bool = False


# =====================================================
# SPECIALIZED SCHEMAS
# =====================================================

class BenefitTypeWithCoverages(BenefitTypeResponse):
    """Benefit type schema including related coverage information"""
    
    coverages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of coverages using this benefit type"
    )
    coverage_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of coverage statistics"
    )


class BenefitTypeCostSharing(BaseModel):
    """Schema for benefit type cost-sharing information"""
    
    benefit_type_id: UUID
    type_name: str
    
    # In-network cost sharing
    in_network_copay: Optional[Decimal] = Field(None, description="In-network copay amount")
    in_network_coinsurance: Optional[Decimal] = Field(None, description="In-network coinsurance percentage")
    in_network_deductible_applies: bool = Field(default=True, description="Whether in-network deductible applies")
    
    # Out-of-network cost sharing
    out_of_network_copay: Optional[Decimal] = Field(None, description="Out-of-network copay amount")
    out_of_network_coinsurance: Optional[Decimal] = Field(None, description="Out-of-network coinsurance percentage")
    out_of_network_deductible_applies: bool = Field(default=True, description="Whether out-of-network deductible applies")
    
    # Additional cost sharing
    specialty_tier_copay: Optional[Decimal] = Field(None, description="Specialty tier copay")
    emergency_copay: Optional[Decimal] = Field(None, description="Emergency services copay")


class BenefitTypeStats(BaseModel):
    """Schema for benefit type statistics and analytics"""
    
    benefit_type_id: UUID
    type_code: str
    type_name: str
    
    # Usage statistics
    total_coverages: int = Field(default=0, description="Total coverages using this benefit type")
    active_coverages: int = Field(default=0, description="Active coverages")
    plan_usage_count: int = Field(default=0, description="Number of plans using this benefit type")
    
    # Utilization metrics
    average_copay: Optional[Decimal] = Field(None, description="Average copay across all coverages")
    most_common_coinsurance: Optional[Decimal] = Field(None, description="Most commonly used coinsurance rate")
    authorization_rate: Optional[float] = Field(None, ge=0, le=100, description="Percentage requiring pre-authorization")
    
    # Cost metrics
    estimated_annual_cost: Optional[Decimal] = Field(None, description="Estimated annual cost for this benefit type")
    cost_trend: Optional[float] = Field(None, description="Cost trend percentage year-over-year")
    
    # Compliance metrics
    compliance_score: Optional[float] = Field(None, ge=0, le=100, description="Regulatory compliance score")
    ehb_compliance: bool = Field(default=True, description="Essential Health Benefit compliance")
    
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Statistics last updated")


# =====================================================
# LIST AND FILTER SCHEMAS
# =====================================================

class BenefitTypeFilter(BaseModel):
    """Schema for filtering benefit types"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "benefit_type": "PRIMARY_CARE",
                "is_active": True,
                "is_essential_health_benefit": True,
                "requires_pre_authorization": False,
                "search_term": "primary care"
            }
        }
    )
    
    benefit_type: Optional[BenefitTypeEnum] = Field(None, description="Filter by benefit type")
    benefit_category_id: Optional[UUID] = Field(None, description="Filter by parent category")
    coverage_level: Optional[CoverageLevelEnum] = Field(None, description="Filter by coverage level")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_available: Optional[bool] = Field(None, description="Filter by available status")
    is_essential_health_benefit: Optional[bool] = Field(None, description="Filter by EHB status")
    requires_pre_authorization: Optional[bool] = Field(None, description="Filter by pre-auth requirement")
    requires_referral: Optional[bool] = Field(None, description="Filter by referral requirement")
    
    # Cost sharing filters
    has_copay: Optional[bool] = Field(None, description="Filter by copay presence")
    has_coinsurance: Optional[bool] = Field(None, description="Filter by coinsurance presence")
    copay_range_min: Optional[Decimal] = Field(None, ge=0, description="Minimum copay amount")
    copay_range_max: Optional[Decimal] = Field(None, ge=0, description="Maximum copay amount")
    
    # Service filters
    service_category: Optional[str] = Field(None, description="Filter by service category")
    procedure_code: Optional[str] = Field(None, description="Filter by specific procedure code")
    
    # Search fields
    search_term: Optional[str] = Field(None, max_length=100, description="Search in names and descriptions")
    type_codes: Optional[List[str]] = Field(None, description="Filter by specific type codes")


class BenefitTypeListResponse(BaseModel):
    """Schema for paginated list of benefit types"""
    
    items: List[BenefitTypeResponse] = Field(..., description="List of benefit types")
    total_count: int = Field(..., ge=0, description="Total number of benefit types matching filter")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


# =====================================================
# BULK OPERATION SCHEMAS
# =====================================================

class BenefitTypeBulkCreate(BaseModel):
    """Schema for bulk creating benefit types"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "benefit_types": [
                    {
                        "type_code": "PRIM_CARE_001",
                        "type_name": "Primary Care Visits",
                        "benefit_type": "PRIMARY_CARE",
                        "benefit_category_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                ],
                "skip_duplicates": True
            }
        }
    )
    
    benefit_types: List[BenefitTypeCreate] = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="List of benefit types to create"
    )
    
    # Bulk operation settings
    skip_duplicates: bool = Field(default=False, description="Skip benefit types with duplicate codes")
    validate_categories: bool = Field(default=True, description="Validate benefit category references")


class BenefitTypeBulkUpdate(BaseModel):
    """Schema for bulk updating benefit types"""
    
    benefit_type_ids: List[UUID] = Field(..., min_length=1, max_length=100)
    updates: BenefitTypeUpdate = Field(..., description="Fields to update")


class BenefitTypeBulkResponse(BaseModel):
    """Schema for bulk operation responses"""
    
    successful_operations: int = Field(..., ge=0, description="Number of successful operations")
    failed_operations: int = Field(..., ge=0, description="Number of failed operations")
    total_operations: int = Field(..., ge=0, description="Total number of operations attempted")
    
    success_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of successful operations")
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of failed operations")


# =====================================================
# COMPARISON AND ANALYSIS SCHEMAS
# =====================================================

class BenefitTypeComparison(BaseModel):
    """Schema for comparing benefit types"""
    
    benefit_type_ids: List[UUID] = Field(..., min_length=2, max_length=5, description="Benefit types to compare")
    comparison_fields: List[str] = Field(
        default=[
            "coverage_level", "default_copay_amount", "default_coinsurance_percentage",
            "requires_pre_authorization", "requires_referral", "is_essential_health_benefit"
        ],
        description="Fields to include in comparison"
    )


class BenefitTypeComparisonResult(BaseModel):
    """Schema for benefit type comparison results"""
    
    comparison_matrix: Dict[str, Dict[str, Any]] = Field(..., description="Comparison matrix")
    differences: List[Dict[str, Any]] = Field(..., description="Key differences identified")
    recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Comparison generated timestamp")


# =====================================================
# MISSING SCHEMAS FOR ROUTE IMPORTS  
# =====================================================

class BenefitTypeWithDetails(BenefitTypeResponse):
    """Extended benefit type schema with comprehensive details"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Extended details
    utilization_data: Optional[Dict[str, Any]] = Field(None, description="Historical utilization data")
    cost_analysis: Optional[Dict[str, Any]] = Field(None, description="Cost analysis data")
    provider_network_data: Optional[Dict[str, Any]] = Field(None, description="Provider network information")
    regulatory_compliance_details: Optional[Dict[str, Any]] = Field(None, description="Detailed compliance info")


class CostSharingCalculation(BaseModel):
    """Schema for cost-sharing calculation results"""
    
    model_config = ConfigDict(from_attributes=True)
    
    service_amount: Decimal = Field(..., description="Original service amount")
    member_cost: Decimal = Field(..., description="Amount member pays")
    insurance_cost: Decimal = Field(..., description="Amount insurance pays")
    deductible_applied: Decimal = Field(default=Decimal('0'), description="Deductible amount applied")
    copay_applied: Decimal = Field(default=Decimal('0'), description="Copay amount applied")
    coinsurance_applied: Decimal = Field(default=Decimal('0'), description="Coinsurance amount applied")
    calculation_breakdown: List[Dict[str, Any]] = Field(default_factory=list, description="Step-by-step breakdown")


class MemberCostEstimate(BaseModel):
    """Schema for member cost estimates"""
    
    model_config = ConfigDict(from_attributes=True)
    
    total_estimated_cost: Decimal = Field(..., description="Total estimated member cost")
    service_estimates: List[Dict[str, Any]] = Field(..., description="Individual service estimates")
    annual_projection: Optional[Decimal] = Field(None, description="Annual cost projection")
    confidence_level: Optional[float] = Field(None, ge=0, le=100, description="Estimate confidence level")


class BenefitComparison(BaseModel):
    """Schema for benefit comparison results"""
    
    model_config = ConfigDict(from_attributes=True)
    
    compared_benefits: List[UUID] = Field(..., description="List of compared benefit type IDs")
    comparison_matrix: Dict[str, Dict[str, Any]] = Field(..., description="Detailed comparison matrix")
    recommendations: List[str] = Field(default_factory=list, description="Comparison-based recommendations")
    best_value_option: Optional[UUID] = Field(None, description="Best value benefit type ID")


class AnnualCostProjection(BaseModel):
    """Schema for annual cost projections"""
    
    model_config = ConfigDict(from_attributes=True)
    
    projected_annual_cost: Decimal = Field(..., description="Projected annual member cost")
    monthly_breakdown: List[Decimal] = Field(..., description="Month-by-month projection")
    scenario_analysis: Dict[str, Decimal] = Field(..., description="Different usage scenarios")
    confidence_intervals: Dict[str, Decimal] = Field(..., description="Statistical confidence intervals")


class CostOptimizationRecommendation(BaseModel):
    """Schema for cost optimization recommendations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    recommendation_type: str = Field(..., description="Type of recommendation")
    current_cost: Decimal = Field(..., description="Current estimated cost")
    optimized_cost: Decimal = Field(..., description="Optimized estimated cost")
    potential_savings: Decimal = Field(..., description="Potential cost savings")
    implementation_steps: List[str] = Field(..., description="Steps to implement recommendation")
    priority_level: str = Field(..., description="Priority level (high, medium, low)")


class BenefitUsageScenario(BaseModel):
    """Schema for benefit usage scenarios"""
    
    model_config = ConfigDict(from_attributes=True)
    
    scenario_name: str = Field(..., description="Name of the usage scenario")
    service_frequency: int = Field(..., ge=0, description="Expected service frequency per year")
    service_cost: Decimal = Field(..., ge=0, description="Average cost per service")
    member_demographics: Optional[Dict[str, Any]] = Field(None, description="Member demographic assumptions")


class CostSharingConfiguration(BaseModel):
    """Schema for cost-sharing configuration"""
    
    model_config = ConfigDict(from_attributes=True)
    
    benefit_type_id: UUID = Field(..., description="Benefit type ID")
    in_network_config: Dict[str, Any] = Field(..., description="In-network cost sharing configuration")
    out_of_network_config: Dict[str, Any] = Field(..., description="Out-of-network cost sharing configuration")
    special_conditions: Optional[Dict[str, Any]] = Field(None, description="Special cost sharing conditions")
    effective_dates: Dict[str, datetime] = Field(..., description="Configuration effective dates")


class NetworkCostAnalysis(BaseModel):
    """Schema for network cost analysis"""
    
    model_config = ConfigDict(from_attributes=True)
    
    benefit_type_id: UUID = Field(..., description="Benefit type ID")
    network_tiers: Dict[str, Dict[str, Any]] = Field(..., description="Cost analysis by network tier")
    cost_differentials: Dict[str, Decimal] = Field(..., description="Cost differences between tiers")
    member_impact_analysis: Dict[str, Any] = Field(..., description="Analysis of member cost impact")
    recommendations: List[str] = Field(default_factory=list, description="Network optimization recommendations")


class BenefitSearchFilter(BaseModel):
    """Enhanced search filter for benefit types"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Extend the existing BenefitTypeFilter
    benefit_type: Optional[BenefitTypeEnum] = Field(None, description="Filter by benefit type")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    search_term: Optional[str] = Field(None, description="Search term")
    
    # Additional search capabilities
    cost_range: Optional[Dict[str, Decimal]] = Field(None, description="Cost range filters")
    authorization_requirements: Optional[List[str]] = Field(None, description="Authorization requirements")
    network_preferences: Optional[List[str]] = Field(None, description="Network preferences")


class BulkBenefitTypeOperation(BaseModel):
    """Schema for bulk benefit type operations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    operation_type: str = Field(..., description="Type of bulk operation")
    benefit_type_ids: List[UUID] = Field(..., min_length=1, description="Benefit type IDs for operation")
    operation_parameters: Dict[str, Any] = Field(..., description="Operation parameters")
    batch_size: int = Field(default=50, ge=1, le=100, description="Batch processing size")
    validate_before_operation: bool = Field(default=True, description="Validate before processing")