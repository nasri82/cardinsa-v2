# app/modules/benefits/schemas/plan_benefit_schedule_schema.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum
from decimal import Decimal


# =====================================================
# ENUMS FOR VALIDATION
# =====================================================

class ScheduleTypeEnum(str, Enum):
    """Enumeration of benefit schedule types"""
    COMPREHENSIVE = "COMPREHENSIVE"
    SUMMARY = "SUMMARY"
    DETAILED = "DETAILED"
    COMPARISON = "COMPARISON"
    REGULATORY = "REGULATORY"


class CoverageLevelEnum(str, Enum):
    """Enumeration of coverage levels"""
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    PLATINUM = "PLATINUM"
    CATASTROPHIC = "CATASTROPHIC"


class MetalTierEnum(str, Enum):
    """Enumeration of ACA metal tiers"""
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class PlanTypeEnum(str, Enum):
    """Enumeration of plan types"""
    HMO = "HMO"
    PPO = "PPO"
    EPO = "EPO"
    POS = "POS"
    HDHP = "HDHP"
    INDEMNITY = "INDEMNITY"


class MarketSegmentEnum(str, Enum):
    """Enumeration of market segments"""
    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"
    LARGE_GROUP = "LARGE_GROUP"
    GOVERNMENT = "GOVERNMENT"
    MEDICARE = "MEDICARE"
    MEDICAID = "MEDICAID"


class ApprovalStatusEnum(str, Enum):
    """Enumeration of approval status values"""
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"
    WITHDRAWN = "WITHDRAWN"


class ScheduleStatusEnum(str, Enum):
    """Enumeration of schedule status values"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


class VersionStatusEnum(str, Enum):
    """Enumeration of version status values"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


# =====================================================
# BASE SCHEMA
# =====================================================

class PlanBenefitScheduleBase(BaseModel):
    """Base schema for plan benefit schedule with common fields"""
    
    model_config = ConfigDict(from_attributes=True)
    
    schedule_code: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Unique code identifying the benefit schedule",
        examples=["SCHED_PPO_2024_001"]
    )
    schedule_name: str = Field(
        ..., 
        min_length=1, 
        max_length=150,
        description="Display name of the benefit schedule",
        examples=["PPO Standard Plan 2024 - Comprehensive Benefits"]
    )
    schedule_name_ar: Optional[str] = Field(
        None, 
        max_length=150,
        description="Arabic translation of schedule name",
        examples=["خطة PPO القياسية 2024 - الفوائد الشاملة"]
    )
    
    # Plan associations
    plan_id: UUID = Field(
        ...,
        description="ID of the associated insurance plan"
    )
    plan_code: str = Field(
        ...,
        max_length=50,
        description="Code of the associated plan"
    )
    plan_name: str = Field(
        ...,
        max_length=150,
        description="Name of the associated plan"
    )
    
    # Product hierarchy
    product_id: Optional[UUID] = Field(
        None,
        description="ID of the parent product"
    )
    product_line: Optional[str] = Field(
        None,
        max_length=50,
        description="Product line classification"
    )
    
    # Market and demographic info
    market_segment: MarketSegmentEnum = Field(
        default=MarketSegmentEnum.GROUP,
        description="Target market segment"
    )
    target_demographic: Optional[str] = Field(
        None,
        max_length=50,
        description="Target demographic group"
    )
    
    # Schedule classification
    schedule_type: ScheduleTypeEnum = Field(
        default=ScheduleTypeEnum.COMPREHENSIVE,
        description="Type of benefit schedule"
    )
    coverage_level: CoverageLevelEnum = Field(
        default=CoverageLevelEnum.STANDARD,
        description="Level of coverage provided"
    )
    metal_tier: Optional[MetalTierEnum] = Field(
        None,
        description="ACA metal tier classification"
    )
    plan_type: PlanTypeEnum = Field(
        default=PlanTypeEnum.PPO,
        description="Type of insurance plan"
    )
    
    # Financial overview
    annual_deductible_individual: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Individual annual deductible",
        examples=["1500.00"]
    )
    annual_deductible_family: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Family annual deductible",
        examples=["3000.00"]
    )
    out_of_pocket_max_individual: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Individual out-of-pocket maximum",
        examples=["6000.00"]
    )
    out_of_pocket_max_family: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Family out-of-pocket maximum",
        examples=["12000.00"]
    )
    
    # Network differentials
    in_network_deductible: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="In-network deductible amount"
    )
    out_of_network_deductible: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Out-of-network deductible amount"
    )
    in_network_oop_max: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="In-network out-of-pocket maximum"
    )
    out_of_network_oop_max: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Out-of-network out-of-pocket maximum"
    )
    
    # Lifetime and annual limits
    lifetime_maximum: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Lifetime maximum benefit"
    )
    currency_code: str = Field(
        default="USD",
        max_length=3,
        description="Currency code for monetary amounts"
    )
    
    # Plan year and effective periods
    plan_year: int = Field(
        ...,
        ge=2020,
        le=2050,
        description="Plan year this schedule applies to",
        examples=[2024]
    )
    effective_date: datetime = Field(
        ...,
        description="When schedule becomes effective"
    )
    termination_date: Optional[datetime] = Field(
        None,
        description="When schedule terminates"
    )
    
    # Enrollment periods
    open_enrollment_start: Optional[datetime] = Field(
        None,
        description="Open enrollment start date"
    )
    open_enrollment_end: Optional[datetime] = Field(
        None,
        description="Open enrollment end date"
    )
    allows_mid_year_changes: bool = Field(
        default=False,
        description="Whether mid-year changes are allowed"
    )
    
    # Regulatory and compliance
    essential_health_benefits: bool = Field(
        default=True,
        description="Whether plan includes Essential Health Benefits"
    )
    aca_compliant: bool = Field(
        default=True,
        description="Whether plan is ACA compliant"
    )
    star_rating: Optional[Decimal] = Field(
        None,
        ge=1.0,
        le=5.0,
        max_digits=2,
        decimal_places=1,
        description="Plan quality star rating"
    )
    
    # Availability flags
    is_active: bool = Field(
        default=True,
        description="Whether the schedule is currently active"
    )
    is_published: bool = Field(
        default=False,
        description="Whether the schedule is published"
    )
    is_enrollable: bool = Field(
        default=True,
        description="Whether the plan is currently enrollable"
    )
    available_individual: bool = Field(
        default=True,
        description="Available for individual enrollment"
    )
    available_group: bool = Field(
        default=True,
        description="Available for group enrollment"
    )
    available_online: bool = Field(
        default=True,
        description="Available for online enrollment"
    )


# =====================================================
# CREATE SCHEMA
# =====================================================

class PlanBenefitScheduleCreate(PlanBenefitScheduleBase):
    """Schema for creating a new plan benefit schedule"""
    
    # Comprehensive benefit structure (JSON format for flexibility)
    medical_benefits: Optional[Dict[str, Any]] = Field(
        None,
        description="Medical benefits structure",
        examples=[{
            "preventive_care": {
                "in_network": "100%",
                "out_network": "70%",
                "deductible_applies": False
            },
            "primary_care": {
                "in_network": "$25 copay",
                "out_network": "70% after deductible"
            },
            "specialist": {
                "in_network": "$50 copay",
                "out_network": "70% after deductible"
            }
        }]
    )
    
    prescription_benefits: Optional[Dict[str, Any]] = Field(
        None,
        description="Prescription drug benefits",
        examples=[{
            "generic": {"copay": "$10", "mail_order": "$25"},
            "brand_preferred": {"copay": "$35", "mail_order": "$87.50"},
            "brand_non_preferred": {"copay": "$70", "mail_order": "$175"},
            "specialty": {"coinsurance": "25%", "max_copay": "$150"}
        }]
    )
    
    dental_benefits: Optional[Dict[str, Any]] = Field(
        None,
        description="Dental benefits structure"
    )
    vision_benefits: Optional[Dict[str, Any]] = Field(
        None,
        description="Vision benefits structure"
    )
    mental_health_benefits: Optional[Dict[str, Any]] = Field(
        None,
        description="Mental health and substance abuse benefits"
    )
    wellness_benefits: Optional[Dict[str, Any]] = Field(
        None,
        description="Wellness and preventive benefits"
    )
    
    # Detailed service categories
    physician_services: Optional[Dict[str, Any]] = Field(
        None,
        description="Physician services benefits"
    )
    hospital_inpatient: Optional[Dict[str, Any]] = Field(
        None,
        description="Inpatient hospital benefits"
    )
    hospital_outpatient: Optional[Dict[str, Any]] = Field(
        None,
        description="Outpatient hospital benefits"
    )
    emergency_services: Optional[Dict[str, Any]] = Field(
        None,
        description="Emergency services benefits"
    )
    urgent_care: Optional[Dict[str, Any]] = Field(
        None,
        description="Urgent care benefits"
    )
    
    # Diagnostic and therapeutic services
    lab_services: Optional[Dict[str, Any]] = Field(
        None,
        description="Laboratory services benefits"
    )
    radiology_services: Optional[Dict[str, Any]] = Field(
        None,
        description="Radiology and imaging benefits"
    )
    physical_therapy: Optional[Dict[str, Any]] = Field(
        None,
        description="Physical therapy benefits"
    )
    
    # Specialized care
    maternity_services: Optional[Dict[str, Any]] = Field(
        None,
        description="Maternity and childbirth benefits"
    )
    pediatric_services: Optional[Dict[str, Any]] = Field(
        None,
        description="Pediatric care benefits"
    )
    
    # Advanced treatments
    transplant_services: Optional[Dict[str, Any]] = Field(
        None,
        description="Organ transplant benefits"
    )
    oncology_services: Optional[Dict[str, Any]] = Field(
        None,
        description="Cancer treatment benefits"
    )
    
    # Home and extended care
    home_health_care: Optional[Dict[str, Any]] = Field(
        None,
        description="Home health care benefits"
    )
    skilled_nursing: Optional[Dict[str, Any]] = Field(
        None,
        description="Skilled nursing facility benefits"
    )
    hospice_care: Optional[Dict[str, Any]] = Field(
        None,
        description="Hospice care benefits"
    )
    
    # Network and provider information
    network_tiers: Optional[Dict[str, Any]] = Field(
        None,
        description="Network tier structure",
        examples=[{
            "tier_1": {"description": "Preferred providers", "cost_share": "lowest"},
            "tier_2": {"description": "Standard network", "cost_share": "moderate"},
            "out_of_network": {"description": "Non-contracted", "cost_share": "highest"}
        }]
    )
    
    provider_access: Optional[Dict[str, Any]] = Field(
        None,
        description="Provider access requirements",
        examples=[{
            "primary_care_required": False,
            "referrals_required": True,
            "prior_auth_services": ["MRI", "CT", "surgery"]
        }]
    )
    
    geographic_coverage: Optional[Dict[str, Any]] = Field(
        None,
        description="Geographic coverage area",
        examples=[{
            "service_area": ["TX", "OK", "AR"],
            "international_coverage": "emergency_only"
        }]
    )
    
    # Exclusions and limitations
    general_exclusions: Optional[List[str]] = Field(
        None,
        description="General plan exclusions",
        examples=[["cosmetic surgery", "experimental treatments"]]
    )
    coverage_limitations: Optional[Dict[str, Any]] = Field(
        None,
        description="Coverage limitations",
        examples=[{
            "chiropractic": {"visits_per_year": 20},
            "acupuncture": {"visits_per_year": 12, "requires_referral": True}
        }]
    )
    
    # Special features and programs
    wellness_programs: Optional[Dict[str, Any]] = Field(
        None,
        description="Wellness programs included"
    )
    disease_management: Optional[Dict[str, Any]] = Field(
        None,
        description="Disease management programs"
    )
    telemedicine: Optional[Dict[str, Any]] = Field(
        None,
        description="Telemedicine benefits"
    )
    
    # Member resources
    member_services: Optional[Dict[str, Any]] = Field(
        None,
        description="Member services and support"
    )
    
    # Regulatory compliance
    state_requirements: Optional[Dict[str, Any]] = Field(
        None,
        description="State-specific requirements"
    )
    mandated_benefits: Optional[Dict[str, Any]] = Field(
        None,
        description="Mandated benefits compliance"
    )
    
    # Document and communication
    plan_summary: Optional[str] = Field(
        None,
        description="Executive summary of the plan"
    )
    plan_highlights: Optional[List[str]] = Field(
        None,
        description="Key plan highlights"
    )
    marketing_description: Optional[str] = Field(
        None,
        description="Marketing description"
    )
    
    # Multi-language support
    available_languages: Optional[List[str]] = Field(
        default=["en", "ar"],
        description="Available languages for plan materials"
    )
    primary_language: str = Field(
        default="en",
        description="Primary language for plan materials"
    )
    
    @field_validator('schedule_code')
    @classmethod
    def validate_schedule_code(cls, v):
        """Validate schedule code format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Schedule code must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()
    
    @field_validator('termination_date')
    @classmethod
    def validate_termination_date(cls, v, info):
        """Validate termination date is after effective date"""
        if v and 'effective_date' in info.data and v <= info.data['effective_date']:
            raise ValueError('Termination date must be after effective date')
        return v
    
    @field_validator('open_enrollment_end')
    @classmethod
    def validate_enrollment_period(cls, v, info):
        """Validate enrollment period"""
        if v and 'open_enrollment_start' in info.data and info.data['open_enrollment_start'] and v <= info.data['open_enrollment_start']:
            raise ValueError('Open enrollment end must be after start date')
        return v


# =====================================================
# UPDATE SCHEMA
# =====================================================

class PlanBenefitScheduleUpdate(BaseModel):
    """Schema for updating an existing plan benefit schedule"""
    
    model_config = ConfigDict(from_attributes=True)
    
    schedule_name: Optional[str] = Field(None, min_length=1, max_length=150)
    schedule_name_ar: Optional[str] = Field(None, max_length=150)
    
    # Plan associations
    plan_name: Optional[str] = Field(None, max_length=150)
    product_line: Optional[str] = Field(None, max_length=50)
    target_demographic: Optional[str] = Field(None, max_length=50)
    
    # Classification updates
    schedule_type: Optional[ScheduleTypeEnum] = Field(None)
    coverage_level: Optional[CoverageLevelEnum] = Field(None)
    metal_tier: Optional[MetalTierEnum] = Field(None)
    plan_type: Optional[PlanTypeEnum] = Field(None)
    market_segment: Optional[MarketSegmentEnum] = Field(None)
    
    # Financial updates
    annual_deductible_individual: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    annual_deductible_family: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    out_of_pocket_max_individual: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    out_of_pocket_max_family: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    
    # Network differential updates
    in_network_deductible: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    out_of_network_deductible: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    in_network_oop_max: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    out_of_network_oop_max: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    
    # Limit updates
    lifetime_maximum: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Date updates
    termination_date: Optional[datetime] = Field(None)
    open_enrollment_start: Optional[datetime] = Field(None)
    open_enrollment_end: Optional[datetime] = Field(None)
    allows_mid_year_changes: Optional[bool] = Field(None)
    
    # Compliance updates
    essential_health_benefits: Optional[bool] = Field(None)
    aca_compliant: Optional[bool] = Field(None)
    star_rating: Optional[Decimal] = Field(None, ge=1.0, le=5.0, max_digits=2, decimal_places=1)
    
    # Availability updates
    is_active: Optional[bool] = Field(None)
    is_published: Optional[bool] = Field(None)
    is_enrollable: Optional[bool] = Field(None)
    available_individual: Optional[bool] = Field(None)
    available_group: Optional[bool] = Field(None)
    available_online: Optional[bool] = Field(None)
    
    # Benefit structure updates
    medical_benefits: Optional[Dict[str, Any]] = Field(None)
    prescription_benefits: Optional[Dict[str, Any]] = Field(None)
    dental_benefits: Optional[Dict[str, Any]] = Field(None)
    vision_benefits: Optional[Dict[str, Any]] = Field(None)
    wellness_programs: Optional[Dict[str, Any]] = Field(None)
    
    # Network updates
    network_tiers: Optional[Dict[str, Any]] = Field(None)
    provider_access: Optional[Dict[str, Any]] = Field(None)
    geographic_coverage: Optional[Dict[str, Any]] = Field(None)
    
    # Exclusion updates
    general_exclusions: Optional[List[str]] = Field(None)
    coverage_limitations: Optional[Dict[str, Any]] = Field(None)
    
    # Communication updates
    plan_summary: Optional[str] = Field(None)
    plan_highlights: Optional[List[str]] = Field(None)
    marketing_description: Optional[str] = Field(None)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class PlanBenefitScheduleResponse(PlanBenefitScheduleBase):
    """Schema for plan benefit schedule responses"""
    
    id: UUID = Field(..., description="Unique identifier for the benefit schedule")
    
    # Extended benefit details
    medical_benefits: Optional[Dict[str, Any]] = Field(None, description="Medical benefits structure")
    prescription_benefits: Optional[Dict[str, Any]] = Field(None, description="Prescription benefits")
    dental_benefits: Optional[Dict[str, Any]] = Field(None, description="Dental benefits")
    vision_benefits: Optional[Dict[str, Any]] = Field(None, description="Vision benefits")
    mental_health_benefits: Optional[Dict[str, Any]] = Field(None, description="Mental health benefits")
    wellness_benefits: Optional[Dict[str, Any]] = Field(None, description="Wellness benefits")
    
    # Detailed service categories
    physician_services: Optional[Dict[str, Any]] = Field(None, description="Physician services")
    hospital_inpatient: Optional[Dict[str, Any]] = Field(None, description="Inpatient benefits")
    hospital_outpatient: Optional[Dict[str, Any]] = Field(None, description="Outpatient benefits")
    emergency_services: Optional[Dict[str, Any]] = Field(None, description="Emergency benefits")
    lab_services: Optional[Dict[str, Any]] = Field(None, description="Lab services")
    radiology_services: Optional[Dict[str, Any]] = Field(None, description="Radiology services")
    
    # Specialized services
    maternity_services: Optional[Dict[str, Any]] = Field(None, description="Maternity benefits")
    pediatric_services: Optional[Dict[str, Any]] = Field(None, description="Pediatric benefits")
    transplant_services: Optional[Dict[str, Any]] = Field(None, description="Transplant benefits")
    home_health_care: Optional[Dict[str, Any]] = Field(None, description="Home health benefits")
    
    # Network and access
    network_tiers: Optional[Dict[str, Any]] = Field(None, description="Network tiers")
    provider_access: Optional[Dict[str, Any]] = Field(None, description="Provider access rules")
    geographic_coverage: Optional[Dict[str, Any]] = Field(None, description="Geographic coverage")
    
    # Limitations and exclusions
    general_exclusions: Optional[List[str]] = Field(None, description="General exclusions")
    coverage_limitations: Optional[Dict[str, Any]] = Field(None, description="Coverage limitations")
    
    # Special programs
    wellness_programs: Optional[Dict[str, Any]] = Field(None, description="Wellness programs")
    disease_management: Optional[Dict[str, Any]] = Field(None, description="Disease management")
    telemedicine: Optional[Dict[str, Any]] = Field(None, description="Telemedicine benefits")
    member_services: Optional[Dict[str, Any]] = Field(None, description="Member services")
    
    # Regulatory and compliance
    state_requirements: Optional[Dict[str, Any]] = Field(None, description="State requirements")
    mandated_benefits: Optional[Dict[str, Any]] = Field(None, description="Mandated benefits")
    quality_metrics: Optional[Dict[str, Any]] = Field(None, description="Quality metrics")
    
    # Version and document control
    version: str = Field(..., description="Schedule version")
    version_effective_date: datetime = Field(..., description="Version effective date")
    supersedes_schedule_id: Optional[UUID] = Field(None, description="Previous schedule ID")
    
    # Approval workflow
    approval_status: ApprovalStatusEnum = Field(..., description="Current approval status")
    approved_by: Optional[UUID] = Field(None, description="ID of approver")
    approved_date: Optional[datetime] = Field(None, description="Approval date")
    published_date: Optional[datetime] = Field(None, description="Publication date")
    
    # Communication and materials
    plan_summary: Optional[str] = Field(None, description="Plan summary")
    plan_highlights: Optional[List[str]] = Field(None, description="Key highlights")
    marketing_description: Optional[str] = Field(None, description="Marketing description")
    
    # Document URLs
    member_handbook_url: Optional[str] = Field(None, description="Member handbook URL")
    provider_directory_url: Optional[str] = Field(None, description="Provider directory URL")
    formulary_url: Optional[str] = Field(None, description="Drug formulary URL")
    
    # Multi-language support
    available_languages: Optional[List[str]] = Field(None, description="Available languages")
    primary_language: str = Field(default="en", description="Primary language")
    
    # Statistics
    enrollment_count: Optional[int] = Field(None, description="Current enrollment count")
    utilization_rate: Optional[float] = Field(None, description="Overall utilization rate")
    member_satisfaction_score: Optional[float] = Field(None, description="Member satisfaction score")
    
    # Status information
    status: Optional[ScheduleStatusEnum] = Field(None, description="Current schedule status")
    status_reason: Optional[str] = Field(None, description="Reason for current status")
    
    # Audit fields
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="ID of user who created the schedule")
    updated_by: Optional[UUID] = Field(None, description="ID of user who last updated the schedule")


# =====================================================
# VERSION MANAGEMENT SCHEMAS
# =====================================================

class ScheduleVersion(BaseModel):
    """Schema for schedule version information"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Version ID")
    schedule_id: UUID = Field(..., description="Schedule ID")
    version_number: str = Field(..., description="Version number")
    effective_date: datetime = Field(..., description="Version effective date")
    status: VersionStatusEnum = Field(..., description="Version status")
    changes_summary: Optional[str] = Field(None, description="Summary of changes")
    created_by: Optional[UUID] = Field(None, description="Created by user ID")
    created_at: datetime = Field(..., description="Creation timestamp")


class ScheduleComparison(BaseModel):
    """Schema for schedule comparison results"""
    
    model_config = ConfigDict(from_attributes=True)
    
    schedule_a_id: UUID = Field(..., description="First schedule ID")
    schedule_b_id: UUID = Field(..., description="Second schedule ID")
    comparison_date: datetime = Field(..., description="Comparison timestamp")
    differences: List[Dict[str, Any]] = Field(..., description="List of differences")
    difference_count: int = Field(..., description="Total number of differences")
    similarity_score: Optional[float] = Field(None, description="Similarity score percentage")


class ScheduleDifference(BaseModel):
    """Schema for individual schedule differences"""
    
    model_config = ConfigDict(from_attributes=True)
    
    field_name: str = Field(..., description="Name of the differing field")
    schedule_a_value: Optional[Any] = Field(None, description="Value in first schedule")
    schedule_b_value: Optional[Any] = Field(None, description="Value in second schedule")
    difference_type: str = Field(..., description="Type of difference")
    impact_level: str = Field(..., description="Impact level of difference")


class ScheduleValidation(BaseModel):
    """Schema for schedule validation results"""
    
    model_config = ConfigDict(from_attributes=True)
    
    schedule_id: UUID = Field(..., description="Validated schedule ID")
    is_valid: bool = Field(..., description="Whether schedule is valid")
    validation_date: datetime = Field(..., description="Validation timestamp")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    compliance_score: Optional[float] = Field(None, description="Compliance score")


class ScheduleTemplate(BaseModel):
    """Schema for schedule templates"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Template ID")
    template_name: str = Field(..., description="Template name")
    template_type: ScheduleTypeEnum = Field(..., description="Template type")
    template_data: Dict[str, Any] = Field(..., description="Template configuration")
    is_active: bool = Field(..., description="Whether template is active")
    created_at: datetime = Field(..., description="Creation timestamp")


class ScheduleTimeline(BaseModel):
    """Schema for schedule timeline information"""
    
    model_config = ConfigDict(from_attributes=True)
    
    schedule_id: UUID = Field(..., description="Schedule ID")
    timeline_events: List[Dict[str, Any]] = Field(..., description="Timeline events")
    current_version: str = Field(..., description="Current version")
    future_changes: Optional[List[Dict[str, Any]]] = Field(None, description="Scheduled future changes")


class PlanScheduleAssociation(BaseModel):
    """Schema for plan-schedule associations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Association ID")
    plan_id: UUID = Field(..., description="Plan ID")
    schedule_id: UUID = Field(..., description="Schedule ID")
    effective_date: date = Field(..., description="Association effective date")
    termination_date: Optional[date] = Field(None, description="Association termination date")
    is_active: bool = Field(..., description="Whether association is active")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Association metadata")


class ScheduleMerge(BaseModel):
    """Schema for schedule merge operations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    source_schedule_ids: List[UUID] = Field(..., description="Source schedule IDs to merge")
    target_schedule_name: str = Field(..., description="Name for merged schedule")
    merge_strategy: str = Field(..., description="Merge strategy to use")
    conflict_resolution: Dict[str, str] = Field(..., description="Conflict resolution rules")


class ScheduleSearchFilter(BaseModel):
    """Schema for schedule search filters"""
    
    model_config = ConfigDict(from_attributes=True)
    
    search: Optional[str] = Field(None, description="Search term")
    schedule_type: Optional[ScheduleTypeEnum] = Field(None, description="Schedule type filter")
    status: Optional[ScheduleStatusEnum] = Field(None, description="Status filter")
    effective_after: Optional[date] = Field(None, description="Effective after date")
    effective_before: Optional[date] = Field(None, description="Effective before date")
    plan_id: Optional[UUID] = Field(None, description="Plan ID filter")
    created_by: Optional[UUID] = Field(None, description="Created by filter")
    has_active_version: Optional[bool] = Field(None, description="Has active version filter")


class BulkScheduleOperation(BaseModel):
    """Schema for bulk schedule operations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    operation_type: str = Field(..., description="Type of bulk operation")
    schedule_ids: List[UUID] = Field(..., description="Schedule IDs to operate on")
    operation_data: Optional[Dict[str, Any]] = Field(None, description="Operation-specific data")
    dry_run: bool = Field(default=True, description="Whether to perform dry run")


# =====================================================
# SUMMARY SCHEMAS
# =====================================================

class PlanBenefitScheduleWithDetails(PlanBenefitScheduleResponse):
    """Extended schema with additional details for comprehensive view"""
    
    # Additional computed fields
    total_benefits_count: Optional[int] = Field(None, description="Total number of benefits")
    coverage_completeness_score: Optional[float] = Field(None, description="Coverage completeness score")
    complexity_score: Optional[float] = Field(None, description="Schedule complexity score")
    
    # Related entities
    associated_plans: Optional[List[Dict[str, Any]]] = Field(None, description="Associated plans")
    version_history: Optional[List[ScheduleVersion]] = Field(None, description="Version history")
    
    # Analytics
    utilization_stats: Optional[Dict[str, Any]] = Field(None, description="Utilization statistics")
    cost_analysis: Optional[Dict[str, Any]] = Field(None, description="Cost analysis")
    member_feedback: Optional[Dict[str, Any]] = Field(None, description="Member feedback summary")


class PlanBenefitScheduleSummary(BaseModel):
    """Lightweight summary schema for plan benefit schedules"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    schedule_code: str
    schedule_name: str
    schedule_name_ar: Optional[str] = None
    plan_name: str
    plan_year: int
    coverage_level: CoverageLevelEnum
    metal_tier: Optional[MetalTierEnum] = None
    plan_type: PlanTypeEnum
    is_active: bool
    is_published: bool
    is_enrollable: bool
    
    # Key financial info
    annual_deductible_individual: Optional[Decimal] = None
    out_of_pocket_max_individual: Optional[Decimal] = None
    star_rating: Optional[Decimal] = None