# app/modules/benefits/schemas/benefit_preapproval_rule_schema.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
from enum import Enum
from decimal import Decimal


# =====================================================
# ENUMS FOR VALIDATION
# =====================================================

class ApprovalTypeEnum(str, Enum):
    """Enumeration of approval types"""
    PRIOR_AUTH = "PRIOR_AUTH"
    PRE_CERTIFICATION = "PRE_CERTIFICATION"
    REFERRAL = "REFERRAL"
    STEP_THERAPY = "STEP_THERAPY"
    QUANTITY_LIMIT = "QUANTITY_LIMIT"
    MEDICAL_NECESSITY = "MEDICAL_NECESSITY"
    EXPERIMENTAL_REVIEW = "EXPERIMENTAL_REVIEW"
    CONCURRENT_REVIEW = "CONCURRENT_REVIEW"


class RuleCategoryEnum(str, Enum):
    """Enumeration of rule categories"""
    MEDICAL = "MEDICAL"
    SURGICAL = "SURGICAL"
    DIAGNOSTIC = "DIAGNOSTIC"
    THERAPEUTIC = "THERAPEUTIC"
    PHARMACEUTICAL = "PHARMACEUTICAL"
    DURABLE_MEDICAL_EQUIPMENT = "DURABLE_MEDICAL_EQUIPMENT"
    HOME_HEALTH = "HOME_HEALTH"
    MENTAL_HEALTH = "MENTAL_HEALTH"


class UrgencyLevelEnum(str, Enum):
    """Enumeration of urgency levels"""
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    STANDARD = "STANDARD"
    ELECTIVE = "ELECTIVE"


class ReviewLevelEnum(str, Enum):
    """Enumeration of review levels"""
    AUTO_APPROVED = "AUTO_APPROVED"
    NURSE_REVIEWER = "NURSE_REVIEWER"
    MEDICAL_DIRECTOR = "MEDICAL_DIRECTOR"
    SPECIALIST_CONSULTANT = "SPECIALIST_CONSULTANT"
    EXTERNAL_REVIEW = "EXTERNAL_REVIEW"
    COMMITTEE_REVIEW = "COMMITTEE_REVIEW"


class RuleStatusEnum(str, Enum):
    """Enumeration of rule status values"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"
    UNDER_REVIEW = "UNDER_REVIEW"


# =====================================================
# BASE SCHEMA
# =====================================================

class BenefitPreapprovalRuleBase(BaseModel):
    """Base schema for benefit preapproval rule with common fields"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "rule_code": "PA_MRI_001",
                "rule_name": "MRI Prior Authorization for Non-Emergency Cases",
                "approval_type": "PRIOR_AUTH",
                "rule_category": "DIAGNOSTIC",
                "urgency_level": "STANDARD",
                "review_level": "MEDICAL_DIRECTOR",
                "max_approval_days": 14,
                "is_active": True
            }
        }
    )
    
    rule_code: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Unique code identifying the preapproval rule"
    )
    rule_name: str = Field(
        ..., 
        min_length=1, 
        max_length=150,
        description="Display name of the preapproval rule"
    )
    rule_name_ar: Optional[str] = Field(
        None, 
        max_length=150,
        description="Arabic translation of rule name"
    )
    
    # Rule classification
    approval_type: ApprovalTypeEnum = Field(
        ...,
        description="Type of approval required"
    )
    rule_category: RuleCategoryEnum = Field(
        default=RuleCategoryEnum.MEDICAL,
        description="Medical category of the rule"
    )
    urgency_level: UrgencyLevelEnum = Field(
        default=UrgencyLevelEnum.STANDARD,
        description="Urgency level for processing"
    )
    review_level: ReviewLevelEnum = Field(
        default=ReviewLevelEnum.NURSE_REVIEWER,
        description="Level of review required"
    )
    
    # Timing and deadlines
    max_approval_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Maximum days for approval decision"
    )
    expedited_review_hours: Optional[int] = Field(
        None,
        ge=1,
        le=72,
        description="Hours for expedited review"
    )
    emergency_override: bool = Field(
        default=True,
        description="Whether emergency override is allowed"
    )
    
    # Service and diagnosis criteria
    applicable_services: Optional[List[str]] = Field(
        None,
        description="CPT/HCPCS codes requiring approval"
    )
    applicable_diagnoses: Optional[List[str]] = Field(
        None,
        description="ICD-10 codes triggering this rule"
    )
    excluded_services: Optional[List[str]] = Field(
        None,
        description="Services excluded from this rule"
    )
    excluded_diagnoses: Optional[List[str]] = Field(
        None,
        description="Diagnoses excluded from this rule"
    )
    
    # Cost thresholds
    cost_threshold_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Cost threshold for approval requirement"
    )
    cumulative_cost_period_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Period for cumulative cost calculation"
    )
    
    # Network and provider requirements
    network_restrictions: Optional[Dict[str, Any]] = Field(
        None,
        description="Network-specific requirements"
    )
    provider_specialty_required: Optional[List[str]] = Field(
        None,
        description="Required provider specialties"
    )
    facility_type_required: Optional[List[str]] = Field(
        None,
        description="Required facility types"
    )
    
    # Member criteria
    age_criteria: Optional[Dict[str, Any]] = Field(
        None,
        description="Age-based criteria for the rule"
    )
    gender_restrictions: Optional[List[str]] = Field(
        None,
        description="Gender restrictions if applicable"
    )
    medical_history_requirements: Optional[Dict[str, Any]] = Field(
        None,
        description="Medical history requirements"
    )
    
    # Documentation requirements
    required_documentation: Optional[List[str]] = Field(
        None,
        description="Required documentation for approval"
    )
    clinical_notes_required: bool = Field(
        default=True,
        description="Whether clinical notes are required"
    )
    lab_results_required: bool = Field(
        default=False,
        description="Whether lab results are required"
    )
    imaging_required: bool = Field(
        default=False,
        description="Whether imaging is required"
    )
    
    # Decision criteria
    medical_necessity_criteria: Optional[Dict[str, Any]] = Field(
        None,
        description="Medical necessity evaluation criteria"
    )
    evidence_based_guidelines: Optional[List[str]] = Field(
        None,
        description="Guidelines used for decision making"
    )
    contraindication_checks: Optional[List[str]] = Field(
        None,
        description="Contraindications to check"
    )
    
    # Alternative treatments
    step_therapy_required: bool = Field(
        default=False,
        description="Whether step therapy is required"
    )
    alternative_treatments: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Alternative treatments to consider"
    )
    conservative_treatment_duration: Optional[int] = Field(
        None,
        ge=0,
        description="Required conservative treatment duration in days"
    )
    
    # Approval parameters
    max_approval_quantity: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum quantity that can be approved"
    )
    max_approval_duration_days: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum duration of approval in days"
    )
    renewable: bool = Field(
        default=True,
        description="Whether approval can be renewed"
    )
    max_renewals: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum number of renewals allowed"
    )
    
    # Appeals process
    appeals_allowed: bool = Field(
        default=True,
        description="Whether appeals are allowed"
    )
    external_review_available: bool = Field(
        default=True,
        description="Whether external review is available"
    )
    peer_review_required: bool = Field(
        default=False,
        description="Whether peer review is required for denials"
    )
    
    # Status and availability
    is_active: bool = Field(
        default=True,
        description="Whether the rule is currently active"
    )
    is_system_generated: bool = Field(
        default=False,
        description="Whether this is a system-generated rule"
    )
    requires_manual_review: bool = Field(
        default=True,
        description="Whether manual review is always required"
    )
    
    # Effective dates
    effective_from: datetime = Field(
        default_factory=datetime.utcnow,
        description="When rule becomes effective"
    )
    effective_to: Optional[datetime] = Field(
        None,
        description="When rule expires"
    )

    @field_validator('rule_code')
    @classmethod
    def validate_rule_code(cls, v: str) -> str:
        """Validate rule code format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Rule code must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()

    @field_validator('effective_to')
    @classmethod
    def validate_effective_to(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate effective_to is after effective_from"""
        if v and hasattr(info, 'data') and 'effective_from' in info.data:
            effective_from = info.data['effective_from']
            if v <= effective_from:
                raise ValueError('Effective to date must be after effective from date')
        return v


# =====================================================
# CREATE SCHEMA
# =====================================================

class BenefitPreapprovalRuleCreate(BenefitPreapprovalRuleBase):
    """Schema for creating a new benefit preapproval rule"""
    
    # Related entity references
    coverage_id: Optional[UUID] = Field(
        None,
        description="ID of the coverage this rule applies to"
    )
    benefit_type_id: Optional[UUID] = Field(
        None,
        description="ID of the benefit type this rule applies to"
    )
    
    # Extended rule configuration
    auto_approval_criteria: Optional[Dict[str, Any]] = Field(
        None,
        description="Criteria for automatic approval"
    )
    auto_denial_criteria: Optional[Dict[str, Any]] = Field(
        None,
        description="Criteria for automatic denial"
    )
    
    # Integration settings
    external_system_integration: Optional[Dict[str, Any]] = Field(
        None,
        description="External system integration settings"
    )
    notification_settings: Optional[Dict[str, Any]] = Field(
        None,
        description="Notification configuration"
    )
    
    # Performance tracking
    track_performance: bool = Field(
        default=True,
        description="Whether to track performance metrics"
    )
    quality_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Quality metrics to track"
    )
    
    # Documentation and help
    description: Optional[str] = Field(
        None,
        description="Detailed description of the rule"
    )
    description_ar: Optional[str] = Field(
        None,
        description="Arabic description of the rule"
    )
    clinical_rationale: Optional[str] = Field(
        None,
        description="Clinical rationale for the rule"
    )
    implementation_notes: Optional[str] = Field(
        None,
        description="Implementation notes and guidelines"
    )
    
    # Communication templates
    approval_message_template: Optional[str] = Field(
        None,
        description="Template for approval notifications"
    )
    denial_message_template: Optional[str] = Field(
        None,
        description="Template for denial notifications"
    )
    pending_message_template: Optional[str] = Field(
        None,
        description="Template for pending notifications"
    )


# =====================================================
# UPDATE SCHEMA
# =====================================================

class BenefitPreapprovalRuleUpdate(BaseModel):
    """Schema for updating an existing benefit preapproval rule"""
    
    model_config = ConfigDict(from_attributes=True)
    
    rule_name: Optional[str] = Field(None, min_length=1, max_length=150)
    rule_name_ar: Optional[str] = Field(None, max_length=150)
    
    approval_type: Optional[ApprovalTypeEnum] = Field(None)
    rule_category: Optional[RuleCategoryEnum] = Field(None)
    urgency_level: Optional[UrgencyLevelEnum] = Field(None)
    review_level: Optional[ReviewLevelEnum] = Field(None)
    
    # Timing updates
    max_approval_days: Optional[int] = Field(None, ge=1, le=365)
    expedited_review_hours: Optional[int] = Field(None, ge=1, le=72)
    emergency_override: Optional[bool] = Field(None)
    
    # Service criteria updates
    applicable_services: Optional[List[str]] = Field(None)
    applicable_diagnoses: Optional[List[str]] = Field(None)
    excluded_services: Optional[List[str]] = Field(None)
    excluded_diagnoses: Optional[List[str]] = Field(None)
    
    # Cost threshold updates
    cost_threshold_amount: Optional[Decimal] = Field(None, ge=0)
    cumulative_cost_period_days: Optional[int] = Field(None, ge=1, le=365)
    
    # Requirements updates
    network_restrictions: Optional[Dict[str, Any]] = Field(None)
    provider_specialty_required: Optional[List[str]] = Field(None)
    facility_type_required: Optional[List[str]] = Field(None)
    
    # Member criteria updates
    age_criteria: Optional[Dict[str, Any]] = Field(None)
    gender_restrictions: Optional[List[str]] = Field(None)
    medical_history_requirements: Optional[Dict[str, Any]] = Field(None)
    
    # Documentation updates
    required_documentation: Optional[List[str]] = Field(None)
    clinical_notes_required: Optional[bool] = Field(None)
    lab_results_required: Optional[bool] = Field(None)
    imaging_required: Optional[bool] = Field(None)
    
    # Decision criteria updates
    medical_necessity_criteria: Optional[Dict[str, Any]] = Field(None)
    evidence_based_guidelines: Optional[List[str]] = Field(None)
    contraindication_checks: Optional[List[str]] = Field(None)
    
    # Alternative treatment updates
    step_therapy_required: Optional[bool] = Field(None)
    alternative_treatments: Optional[List[Dict[str, Any]]] = Field(None)
    conservative_treatment_duration: Optional[int] = Field(None, ge=0)
    
    # Approval parameter updates
    max_approval_quantity: Optional[int] = Field(None, ge=1)
    max_approval_duration_days: Optional[int] = Field(None, ge=1)
    renewable: Optional[bool] = Field(None)
    max_renewals: Optional[int] = Field(None, ge=0)
    
    # Appeals updates
    appeals_allowed: Optional[bool] = Field(None)
    external_review_available: Optional[bool] = Field(None)
    peer_review_required: Optional[bool] = Field(None)
    
    # Status updates
    is_active: Optional[bool] = Field(None)
    requires_manual_review: Optional[bool] = Field(None)
    effective_to: Optional[datetime] = Field(None)
    
    # Extended configuration updates
    auto_approval_criteria: Optional[Dict[str, Any]] = Field(None)
    auto_denial_criteria: Optional[Dict[str, Any]] = Field(None)
    external_system_integration: Optional[Dict[str, Any]] = Field(None)
    notification_settings: Optional[Dict[str, Any]] = Field(None)
    
    # Documentation updates
    description: Optional[str] = Field(None)
    description_ar: Optional[str] = Field(None)
    clinical_rationale: Optional[str] = Field(None)
    implementation_notes: Optional[str] = Field(None)
    
    # Template updates
    approval_message_template: Optional[str] = Field(None)
    denial_message_template: Optional[str] = Field(None)
    pending_message_template: Optional[str] = Field(None)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class BenefitPreapprovalRuleResponse(BenefitPreapprovalRuleBase):
    """Schema for benefit preapproval rule responses"""
    
    id: UUID = Field(..., description="Unique identifier for the preapproval rule")
    
    # Related entity information
    coverage_id: Optional[UUID] = Field(None, description="Associated coverage ID")
    benefit_type_id: Optional[UUID] = Field(None, description="Associated benefit type ID")
    coverage_name: Optional[str] = Field(None, description="Associated coverage name")
    benefit_type_name: Optional[str] = Field(None, description="Associated benefit type name")
    
    # Extended configuration
    auto_approval_criteria: Optional[Dict[str, Any]] = Field(None, description="Auto-approval criteria")
    auto_denial_criteria: Optional[Dict[str, Any]] = Field(None, description="Auto-denial criteria")
    external_system_integration: Optional[Dict[str, Any]] = Field(None, description="External system integration")
    notification_settings: Optional[Dict[str, Any]] = Field(None, description="Notification settings")
    
    # Performance tracking
    track_performance: bool = Field(default=True, description="Performance tracking enabled")
    quality_metrics: Optional[Dict[str, Any]] = Field(None, description="Quality metrics")
    
    # Documentation
    description: Optional[str] = Field(None, description="Rule description")
    description_ar: Optional[str] = Field(None, description="Arabic description")
    clinical_rationale: Optional[str] = Field(None, description="Clinical rationale")
    implementation_notes: Optional[str] = Field(None, description="Implementation notes")
    
    # Communication templates
    approval_message_template: Optional[str] = Field(None, description="Approval message template")
    denial_message_template: Optional[str] = Field(None, description="Denial message template")
    pending_message_template: Optional[str] = Field(None, description="Pending message template")
    
    # Usage statistics
    total_requests: Optional[int] = Field(None, description="Total approval requests")
    approved_requests: Optional[int] = Field(None, description="Number of approved requests")
    denied_requests: Optional[int] = Field(None, description="Number of denied requests")
    pending_requests: Optional[int] = Field(None, description="Number of pending requests")
    approval_rate: Optional[float] = Field(None, ge=0, le=100, description="Approval rate percentage")
    
    # Performance metrics
    average_decision_time_hours: Optional[float] = Field(None, description="Average decision time in hours")
    sla_compliance_rate: Optional[float] = Field(None, ge=0, le=100, description="SLA compliance rate")
    appeals_rate: Optional[float] = Field(None, ge=0, le=100, description="Appeals rate percentage")
    
    # Status information
    status: Optional[RuleStatusEnum] = Field(None, description="Current rule status")
    status_reason: Optional[str] = Field(None, description="Reason for current status")
    
    # Audit fields
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="ID of user who created the rule")
    updated_by: Optional[UUID] = Field(None, description="ID of user who last updated the rule")
    version: int = Field(default=1, description="Version number")


class BenefitPreapprovalRuleSummary(BaseModel):
    """Lightweight summary schema for benefit preapproval rules"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "rule_code": "PA_MRI_001",
                "rule_name": "MRI Prior Authorization",
                "approval_type": "PRIOR_AUTH",
                "rule_category": "DIAGNOSTIC",
                "urgency_level": "STANDARD",
                "review_level": "MEDICAL_DIRECTOR",
                "is_active": True,
                "max_approval_days": 14,
                "emergency_override": True
            }
        }
    )
    
    id: UUID
    rule_code: str
    rule_name: str
    rule_name_ar: Optional[str] = None
    approval_type: ApprovalTypeEnum
    rule_category: RuleCategoryEnum
    urgency_level: UrgencyLevelEnum
    review_level: ReviewLevelEnum
    is_active: bool
    max_approval_days: Optional[int] = None
    emergency_override: bool = True


# =====================================================
# SPECIALIZED SCHEMAS
# =====================================================

class PreapprovalRequest(BaseModel):
    """Schema for preapproval requests"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_id": "123e4567-e89b-12d3-a456-426614174000",
                "member_id": "456e7890-e89b-12d3-a456-426614174001",
                "requested_service": "99213",
                "diagnosis_codes": ["M79.3"],
                "provider_id": "789e0123-e89b-12d3-a456-426614174002",
                "urgency_level": "STANDARD",
                "clinical_information": {
                    "symptoms": "Lower back pain for 6 weeks",
                    "previous_treatments": ["Physical therapy", "NSAIDs"],
                    "treatment_duration": "4 weeks"
                }
            }
        }
    )
    
    rule_id: UUID = Field(..., description="Preapproval rule ID")
    member_id: UUID = Field(..., description="Member requesting approval")
    requested_service: str = Field(..., description="Requested service code")
    diagnosis_codes: List[str] = Field(..., description="Diagnosis codes")
    provider_id: UUID = Field(..., description="Requesting provider ID")
    facility_id: Optional[UUID] = Field(None, description="Facility ID if applicable")
    
    urgency_level: UrgencyLevelEnum = Field(
        default=UrgencyLevelEnum.STANDARD,
        description="Urgency level of request"
    )
    
    clinical_information: Dict[str, Any] = Field(..., description="Clinical information supporting request")
    supporting_documentation: Optional[List[str]] = Field(None, description="Supporting document IDs")
    
    requested_quantity: Optional[int] = Field(None, ge=1, description="Requested quantity")
    requested_duration_days: Optional[int] = Field(None, ge=1, description="Requested duration")
    
    service_date: Optional[datetime] = Field(None, description="Planned service date")
    estimated_cost: Optional[Decimal] = Field(None, ge=0, description="Estimated cost")


class PreapprovalDecision(BaseModel):
    """Schema for preapproval decisions"""
    
    model_config = ConfigDict(from_attributes=True)
    
    request_id: UUID = Field(..., description="Preapproval request ID")
    rule_id: UUID = Field(..., description="Rule that processed the request")
    decision: str = Field(..., description="Decision (APPROVED, DENIED, PENDING)")
    
    # Decision details
    decision_reason: str = Field(..., description="Reason for decision")
    decision_notes: Optional[str] = Field(None, description="Additional decision notes")
    reviewer_id: Optional[UUID] = Field(None, description="ID of reviewer who made decision")
    review_level_used: ReviewLevelEnum = Field(..., description="Review level that made decision")
    
    # Approval details (if approved)
    approved_quantity: Optional[int] = Field(None, description="Approved quantity")
    approved_duration_days: Optional[int] = Field(None, description="Approved duration")
    approval_conditions: Optional[List[str]] = Field(None, description="Conditions of approval")
    authorization_number: Optional[str] = Field(None, description="Authorization number")
    
    # Validity
    valid_from: Optional[datetime] = Field(None, description="Authorization valid from")
    valid_until: Optional[datetime] = Field(None, description="Authorization valid until")
    
    # Appeals information
    appeals_deadline: Optional[datetime] = Field(None, description="Deadline for appeals")
    external_review_available: bool = Field(default=True, description="Whether external review is available")
    
    decision_date: datetime = Field(default_factory=datetime.utcnow, description="Decision timestamp")


# =====================================================
# LIST AND FILTER SCHEMAS
# =====================================================

class BenefitPreapprovalRuleFilter(BaseModel):
    """Schema for filtering benefit preapproval rules"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "approval_type": "PRIOR_AUTH",
                "rule_category": "DIAGNOSTIC",
                "urgency_level": "STANDARD",
                "is_active": True,
                "emergency_override": True,
                "search_term": "MRI"
            }
        }
    )
    
    approval_type: Optional[ApprovalTypeEnum] = Field(None, description="Filter by approval type")
    rule_category: Optional[RuleCategoryEnum] = Field(None, description="Filter by rule category")
    urgency_level: Optional[UrgencyLevelEnum] = Field(None, description="Filter by urgency level")
    review_level: Optional[ReviewLevelEnum] = Field(None, description="Filter by review level")
    
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_system_generated: Optional[bool] = Field(None, description="Filter by system generated status")
    requires_manual_review: Optional[bool] = Field(None, description="Filter by manual review requirement")
    emergency_override: Optional[bool] = Field(None, description="Filter by emergency override availability")
    
    # Related entity filters
    coverage_id: Optional[UUID] = Field(None, description="Filter by coverage")
    benefit_type_id: Optional[UUID] = Field(None, description="Filter by benefit type")
    
    # Service filters
    service_code: Optional[str] = Field(None, description="Filter by specific service code")
    diagnosis_code: Optional[str] = Field(None, description="Filter by specific diagnosis code")
    
    # Performance filters
    approval_rate_min: Optional[float] = Field(None, ge=0, le=100, description="Minimum approval rate")
    decision_time_max: Optional[float] = Field(None, ge=0, description="Maximum decision time in hours")
    
    # Date filters
    effective_date_from: Optional[datetime] = Field(None, description="Effective from date")
    effective_date_to: Optional[datetime] = Field(None, description="Effective to date")
    
    # Search fields
    search_term: Optional[str] = Field(None, max_length=100, description="Search in names and descriptions")
    rule_codes: Optional[List[str]] = Field(None, description="Filter by specific rule codes")


class BenefitPreapprovalRuleListResponse(BaseModel):
    """Schema for paginated list of benefit preapproval rules"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[BenefitPreapprovalRuleResponse] = Field(..., description="List of preapproval rules")
    total_count: int = Field(..., ge=0, description="Total number of rules matching filter")
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

class BenefitPreapprovalRuleBulkCreate(BaseModel):
    """Schema for bulk creating benefit preapproval rules"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rules": [
                    {
                        "rule_code": "PA_MRI_001",
                        "rule_name": "MRI Prior Authorization",
                        "approval_type": "PRIOR_AUTH",
                        "rule_category": "DIAGNOSTIC",
                        "max_approval_days": 14
                    }
                ],
                "skip_duplicates": True,
                "validate_services": True
            }
        }
    )
    
    rules: List[BenefitPreapprovalRuleCreate] = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="List of preapproval rules to create"
    )
    
    # Bulk operation settings
    skip_duplicates: bool = Field(default=False, description="Skip rules with duplicate codes")
    validate_services: bool = Field(default=True, description="Validate service and diagnosis codes")
    auto_activate: bool = Field(default=False, description="Auto-activate created rules")


class BenefitPreapprovalRuleBulkUpdate(BaseModel):
    """Schema for bulk updating benefit preapproval rules"""
    
    model_config = ConfigDict(from_attributes=True)
    
    rule_ids: List[UUID] = Field(..., min_length=1, max_length=100)
    updates: BenefitPreapprovalRuleUpdate = Field(..., description="Fields to update")
    
    # Update options
    preserve_custom_criteria: bool = Field(default=True, description="Preserve custom criteria")
    recalculate_dependencies: bool = Field(default=False, description="Recalculate rule dependencies")


class BenefitPreapprovalRuleBulkResponse(BaseModel):
    """Schema for bulk operation responses"""
    
    model_config = ConfigDict(from_attributes=True)
    
    successful_operations: int = Field(..., ge=0, description="Number of successful operations")
    failed_operations: int = Field(..., ge=0, description="Number of failed operations")
    total_operations: int = Field(..., ge=0, description="Total number of operations attempted")
    
    success_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of successful operations")
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of failed operations")
    
    # Additional results
    rules_activated: Optional[int] = Field(None, description="Number of rules activated")
    dependencies_updated: Optional[int] = Field(None, description="Number of dependencies updated")