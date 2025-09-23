# app/modules/benefits/schemas/benefit_condition_schema.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, date
from uuid import UUID
from enum import Enum
from decimal import Decimal


# =====================================================
# ENUMS FOR VALIDATION
# =====================================================

class ConditionTypeEnum(str, Enum):
    """Enumeration of condition types"""
    ELIGIBILITY = "ELIGIBILITY"
    COVERAGE = "COVERAGE"
    EXCLUSION = "EXCLUSION"
    LIMITATION = "LIMITATION"
    REQUIREMENT = "REQUIREMENT"
    QUALIFICATION = "QUALIFICATION"
    PRE_EXISTING = "PRE_EXISTING"
    WAITING_PERIOD = "WAITING_PERIOD"
    BENEFIT_TRIGGER = "BENEFIT_TRIGGER"


class ConditionCategoryEnum(str, Enum):
    """Enumeration of condition categories"""
    MEMBER = "MEMBER"
    SERVICE = "SERVICE"
    PROVIDER = "PROVIDER"
    TEMPORAL = "TEMPORAL"
    FINANCIAL = "FINANCIAL"
    CLINICAL = "CLINICAL"
    GEOGRAPHIC = "GEOGRAPHIC"
    REGULATORY = "REGULATORY"
    ADMINISTRATIVE = "ADMINISTRATIVE"


class ApplicationScopeEnum(str, Enum):
    """Enumeration of application scopes"""
    BENEFIT = "BENEFIT"
    COVERAGE = "COVERAGE"
    PLAN = "PLAN"
    MEMBER = "MEMBER"
    SERVICE = "SERVICE"
    PROVIDER = "PROVIDER"
    CLAIM = "CLAIM"


class LogicalOperatorEnum(str, Enum):
    """Enumeration of logical operators"""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    XOR = "XOR"


class EvaluationFrequencyEnum(str, Enum):
    """Enumeration of evaluation frequencies"""
    ON_DEMAND = "ON_DEMAND"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    ANNUALLY = "ANNUALLY"
    AT_ENROLLMENT = "AT_ENROLLMENT"
    AT_RENEWAL = "AT_RENEWAL"


class ErrorHandlingEnum(str, Enum):
    """Enumeration of error handling strategies"""
    FAIL_SAFE = "FAIL_SAFE"
    FAIL_SECURE = "FAIL_SECURE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    USE_DEFAULT = "USE_DEFAULT"


class ValidationStatusEnum(str, Enum):
    """Enumeration of validation status values"""
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"
    APPROVED = "APPROVED"


class ConditionStatusEnum(str, Enum):
    """Enumeration of condition status values"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


# =====================================================
# BASE SCHEMA
# =====================================================

class BenefitConditionBase(BaseModel):
    """Base schema for benefit condition with common fields"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "condition_code": "COND_AGE_001",
                "condition_name": "Age Eligibility Requirement",
                "condition_type": "ELIGIBILITY",
                "condition_category": "MEMBER",
                "application_scope": "BENEFIT",
                "age_conditions": {
                    "min_age": 18,
                    "max_age": 65
                },
                "member_explanation": "You must be between 18 and 65 years old to be eligible for this benefit",
                "is_mandatory": True
            }
        }
    )
    
    condition_code: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Unique code identifying the condition"
    )
    condition_name: str = Field(
        ..., 
        min_length=1, 
        max_length=150,
        description="Display name of the condition"
    )
    condition_name_ar: Optional[str] = Field(
        None, 
        max_length=150,
        description="Arabic translation of condition name"
    )
    
    # Classification
    condition_type: ConditionTypeEnum = Field(
        ...,
        description="Type of condition"
    )
    condition_category: ConditionCategoryEnum = Field(
        default=ConditionCategoryEnum.MEMBER,
        description="Category of condition"
    )
    application_scope: ApplicationScopeEnum = Field(
        default=ApplicationScopeEnum.BENEFIT,
        description="Scope where condition applies"
    )
    
    # Logical evaluation
    logical_operator: LogicalOperatorEnum = Field(
        default=LogicalOperatorEnum.AND,
        description="Logical operator for complex conditions"
    )
    condition_expression: Optional[str] = Field(
        None,
        description="Complex logical condition expression"
    )
    evaluation_order: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Order of evaluation for this condition"
    )
    is_mandatory: bool = Field(
        default=False,
        description="Whether this condition is mandatory"
    )
    
    # Evaluation settings
    evaluation_frequency: EvaluationFrequencyEnum = Field(
        default=EvaluationFrequencyEnum.ON_DEMAND,
        description="How often condition should be evaluated"
    )
    auto_evaluation: bool = Field(
        default=True,
        description="Whether condition is evaluated automatically"
    )
    requires_manual_review: bool = Field(
        default=False,
        description="Whether manual review is required"
    )
    
    # Caching and performance
    cache_result: bool = Field(
        default=True,
        description="Whether to cache evaluation results"
    )
    cache_duration_hours: int = Field(
        default=24,
        ge=1,
        le=8760,
        description="Cache duration in hours"
    )
    
    # Error handling
    error_handling: ErrorHandlingEnum = Field(
        default=ErrorHandlingEnum.FAIL_SAFE,
        description="Error handling strategy"
    )
    default_result: Optional[bool] = Field(
        None,
        description="Default result when evaluation fails"
    )
    
    # Notifications
    notify_on_failure: bool = Field(
        default=False,
        description="Whether to notify on evaluation failure"
    )
    notify_on_success: bool = Field(
        default=False,
        description="Whether to notify on evaluation success"
    )
    
    # Member communication
    member_visible: bool = Field(
        default=True,
        description="Whether condition is visible to members"
    )
    member_explanation: Optional[str] = Field(
        None,
        description="Member-friendly explanation of the condition"
    )
    member_explanation_ar: Optional[str] = Field(
        None,
        description="Arabic member-friendly explanation"
    )
    
    # Status and control
    is_active: bool = Field(
        default=True,
        description="Whether the condition is currently active"
    )
    is_system_generated: bool = Field(
        default=False,
        description="Whether condition is system-generated"
    )
    is_test_condition: bool = Field(
        default=False,
        description="Whether this is a test condition"
    )
    validation_status: ValidationStatusEnum = Field(
        default=ValidationStatusEnum.PENDING,
        description="Validation status of the condition"
    )
    
    # Effective dates
    effective_from: datetime = Field(
        default_factory=datetime.utcnow,
        description="When condition becomes effective"
    )
    effective_to: Optional[datetime] = Field(
        None,
        description="When condition expires"
    )

    @field_validator('condition_code')
    @classmethod
    def validate_condition_code(cls, v: str) -> str:
        """Validate condition code format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Condition code must contain only alphanumeric characters, hyphens, and underscores')
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

    @field_validator('evaluation_order')
    @classmethod
    def validate_evaluation_order(cls, v: int) -> int:
        """Validate evaluation order is positive"""
        if v <= 0:
            raise ValueError('Evaluation order must be a positive integer')
        return v


# =====================================================
# CREATE SCHEMA
# =====================================================

class BenefitConditionCreate(BenefitConditionBase):
    """Schema for creating a new benefit condition"""
    
    # Related entity references
    coverage_id: Optional[UUID] = Field(
        None,
        description="ID of the coverage this condition applies to"
    )
    benefit_type_id: Optional[UUID] = Field(
        None,
        description="ID of the benefit type this condition applies to"
    )
    limit_id: Optional[UUID] = Field(
        None,
        description="ID of the benefit limit this condition applies to"
    )
    
    # Condition dependencies
    parent_condition_id: Optional[UUID] = Field(
        None,
        description="Parent condition ID for hierarchical conditions"
    )
    prerequisite_conditions: Optional[List[UUID]] = Field(
        None,
        description="List of prerequisite condition IDs"
    )
    exclusive_with_conditions: Optional[List[UUID]] = Field(
        None,
        description="List of mutually exclusive condition IDs"
    )
    
    # Member conditions
    age_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Age-based conditions"
    )
    gender_conditions: Optional[List[str]] = Field(
        None,
        description="Gender-based conditions"
    )
    marital_status_conditions: Optional[List[str]] = Field(
        None,
        description="Marital status conditions"
    )
    
    # Employment conditions
    employment_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Employment-based conditions"
    )
    
    # Dependent conditions
    dependent_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Dependent-related conditions"
    )
    
    # Health and medical conditions
    pre_existing_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Pre-existing condition rules"
    )
    health_status_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Health status requirements"
    )
    disability_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Disability-related conditions"
    )
    
    # Service and treatment conditions
    service_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Service-specific conditions"
    )
    diagnosis_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Diagnosis-based conditions"
    )
    treatment_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Treatment-specific conditions"
    )
    
    # Provider and facility conditions
    provider_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Provider requirements"
    )
    facility_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Facility requirements"
    )
    referral_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Referral requirements"
    )
    
    # Temporal conditions
    temporal_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Time-based conditions"
    )
    frequency_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Frequency-based conditions"
    )
    seasonal_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Seasonal conditions"
    )
    
    # Financial conditions
    cost_sharing_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Cost-sharing conditions"
    )
    income_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Income-based conditions"
    )
    premium_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Premium payment conditions"
    )
    
    # Geographic conditions
    geographic_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Geographic restrictions"
    )
    network_geographic_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Network geographic conditions"
    )
    
    # Regulatory and compliance conditions
    regulatory_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Regulatory requirements"
    )
    legal_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Legal conditions"
    )
    
    # Communication templates
    failure_message_template: Optional[str] = Field(
        None,
        max_length=100,
        description="Template for failure notifications"
    )
    success_message_template: Optional[str] = Field(
        None,
        max_length=100,
        description="Template for success notifications"
    )
    
    # Documentation
    description: Optional[str] = Field(
        None,
        description="Detailed description of the condition"
    )
    business_purpose: Optional[str] = Field(
        None,
        description="Business purpose of the condition"
    )
    implementation_notes: Optional[str] = Field(
        None,
        description="Implementation guidance"
    )
    example_scenarios: Optional[Dict[str, str]] = Field(
        None,
        description="Example scenarios"
    )
    
    # Regulatory documentation
    regulatory_reference: Optional[str] = Field(
        None,
        max_length=200,
        description="Regulatory reference"
    )
    compliance_notes: Optional[str] = Field(
        None,
        description="Compliance notes"
    )


# =====================================================
# UPDATE SCHEMA
# =====================================================

class BenefitConditionUpdate(BaseModel):
    """Schema for updating an existing benefit condition"""
    
    model_config = ConfigDict(from_attributes=True)
    
    condition_name: Optional[str] = Field(None, min_length=1, max_length=150)
    condition_name_ar: Optional[str] = Field(None, max_length=150)
    
    # Classification updates
    condition_type: Optional[ConditionTypeEnum] = Field(None)
    condition_category: Optional[ConditionCategoryEnum] = Field(None)
    application_scope: Optional[ApplicationScopeEnum] = Field(None)
    
    # Logic updates
    logical_operator: Optional[LogicalOperatorEnum] = Field(None)
    condition_expression: Optional[str] = Field(None)
    evaluation_order: Optional[int] = Field(None, ge=1, le=1000)
    is_mandatory: Optional[bool] = Field(None)
    
    # Evaluation updates
    evaluation_frequency: Optional[EvaluationFrequencyEnum] = Field(None)
    auto_evaluation: Optional[bool] = Field(None)
    requires_manual_review: Optional[bool] = Field(None)
    
    # Caching updates
    cache_result: Optional[bool] = Field(None)
    cache_duration_hours: Optional[int] = Field(None, ge=1, le=8760)
    
    # Error handling updates
    error_handling: Optional[ErrorHandlingEnum] = Field(None)
    default_result: Optional[bool] = Field(None)
    
    # Notification updates
    notify_on_failure: Optional[bool] = Field(None)
    notify_on_success: Optional[bool] = Field(None)
    
    # Member communication updates
    member_visible: Optional[bool] = Field(None)
    member_explanation: Optional[str] = Field(None)
    member_explanation_ar: Optional[str] = Field(None)
    
    # Status updates
    is_active: Optional[bool] = Field(None)
    is_test_condition: Optional[bool] = Field(None)
    validation_status: Optional[ValidationStatusEnum] = Field(None)
    effective_to: Optional[datetime] = Field(None)
    
    # Condition criteria updates
    age_conditions: Optional[Dict[str, Any]] = Field(None)
    gender_conditions: Optional[List[str]] = Field(None)
    employment_conditions: Optional[Dict[str, Any]] = Field(None)
    service_conditions: Optional[Dict[str, Any]] = Field(None)
    provider_conditions: Optional[Dict[str, Any]] = Field(None)
    geographic_conditions: Optional[Dict[str, Any]] = Field(None)
    
    # Template updates
    failure_message_template: Optional[str] = Field(None, max_length=100)
    success_message_template: Optional[str] = Field(None, max_length=100)
    
    # Documentation updates
    description: Optional[str] = Field(None)
    business_purpose: Optional[str] = Field(None)
    implementation_notes: Optional[str] = Field(None)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class BenefitConditionResponse(BenefitConditionBase):
    """Schema for benefit condition responses"""
    
    id: UUID = Field(..., description="Unique identifier for the condition")
    
    # Related entity information
    coverage_id: Optional[UUID] = Field(None, description="Associated coverage ID")
    benefit_type_id: Optional[UUID] = Field(None, description="Associated benefit type ID")
    limit_id: Optional[UUID] = Field(None, description="Associated limit ID")
    coverage_name: Optional[str] = Field(None, description="Associated coverage name")
    benefit_type_name: Optional[str] = Field(None, description="Associated benefit type name")
    
    # Condition dependencies
    parent_condition_id: Optional[UUID] = Field(None, description="Parent condition ID")
    prerequisite_conditions: Optional[List[UUID]] = Field(None, description="Prerequisite conditions")
    exclusive_with_conditions: Optional[List[UUID]] = Field(None, description="Mutually exclusive conditions")
    
    # All condition criteria
    age_conditions: Optional[Dict[str, Any]] = Field(None, description="Age-based conditions")
    gender_conditions: Optional[List[str]] = Field(None, description="Gender conditions")
    marital_status_conditions: Optional[List[str]] = Field(None, description="Marital status conditions")
    employment_conditions: Optional[Dict[str, Any]] = Field(None, description="Employment conditions")
    dependent_conditions: Optional[Dict[str, Any]] = Field(None, description="Dependent conditions")
    
    # Health conditions
    pre_existing_conditions: Optional[Dict[str, Any]] = Field(None, description="Pre-existing condition rules")
    health_status_conditions: Optional[Dict[str, Any]] = Field(None, description="Health status conditions")
    disability_conditions: Optional[Dict[str, Any]] = Field(None, description="Disability conditions")
    
    # Service conditions
    service_conditions: Optional[Dict[str, Any]] = Field(None, description="Service conditions")
    diagnosis_conditions: Optional[Dict[str, Any]] = Field(None, description="Diagnosis conditions")
    treatment_conditions: Optional[Dict[str, Any]] = Field(None, description="Treatment conditions")
    
    # Provider conditions
    provider_conditions: Optional[Dict[str, Any]] = Field(None, description="Provider conditions")
    facility_conditions: Optional[Dict[str, Any]] = Field(None, description="Facility conditions")
    referral_conditions: Optional[Dict[str, Any]] = Field(None, description="Referral conditions")
    
    # Temporal conditions
    temporal_conditions: Optional[Dict[str, Any]] = Field(None, description="Temporal conditions")
    frequency_conditions: Optional[Dict[str, Any]] = Field(None, description="Frequency conditions")
    seasonal_conditions: Optional[Dict[str, Any]] = Field(None, description="Seasonal conditions")
    
    # Financial conditions
    cost_sharing_conditions: Optional[Dict[str, Any]] = Field(None, description="Cost sharing conditions")
    income_conditions: Optional[Dict[str, Any]] = Field(None, description="Income conditions")
    premium_conditions: Optional[Dict[str, Any]] = Field(None, description="Premium conditions")
    
    # Geographic conditions
    geographic_conditions: Optional[Dict[str, Any]] = Field(None, description="Geographic conditions")
    network_geographic_conditions: Optional[Dict[str, Any]] = Field(None, description="Network geographic conditions")
    
    # Regulatory conditions
    regulatory_conditions: Optional[Dict[str, Any]] = Field(None, description="Regulatory conditions")
    legal_conditions: Optional[Dict[str, Any]] = Field(None, description="Legal conditions")
    
    # Communication templates
    failure_message_template: Optional[str] = Field(None, description="Failure message template")
    success_message_template: Optional[str] = Field(None, description="Success message template")
    
    # Documentation
    description: Optional[str] = Field(None, description="Condition description")
    business_purpose: Optional[str] = Field(None, description="Business purpose")
    implementation_notes: Optional[str] = Field(None, description="Implementation notes")
    example_scenarios: Optional[Dict[str, str]] = Field(None, description="Example scenarios")
    regulatory_reference: Optional[str] = Field(None, description="Regulatory reference")
    compliance_notes: Optional[str] = Field(None, description="Compliance notes")
    
    # Usage statistics
    evaluation_count: Optional[int] = Field(None, description="Number of evaluations performed")
    success_rate: Optional[float] = Field(None, ge=0, le=100, description="Success rate percentage")
    failure_rate: Optional[float] = Field(None, ge=0, le=100, description="Failure rate percentage")
    average_evaluation_time: Optional[float] = Field(None, description="Average evaluation time in milliseconds")
    
    # Hierarchy information
    child_condition_count: Optional[int] = Field(None, description="Number of child conditions")
    dependency_count: Optional[int] = Field(None, description="Number of dependencies")
    
    # Status information
    status: Optional[ConditionStatusEnum] = Field(None, description="Current condition status")
    status_reason: Optional[str] = Field(None, description="Reason for current status")
    
    # Audit fields
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="ID of user who created the condition")
    updated_by: Optional[UUID] = Field(None, description="ID of user who last updated the condition")
    version: str = Field(default="1.0", description="Condition version")


class BenefitConditionSummary(BaseModel):
    """Lightweight summary schema for benefit conditions"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "condition_code": "COND_AGE_001",
                "condition_name": "Age Eligibility Requirement",
                "condition_type": "ELIGIBILITY",
                "condition_category": "MEMBER",
                "application_scope": "BENEFIT",
                "is_active": True,
                "is_mandatory": True,
                "evaluation_frequency": "ON_DEMAND",
                "member_visible": True
            }
        }
    )
    
    id: UUID
    condition_code: str
    condition_name: str
    condition_name_ar: Optional[str] = None
    condition_type: ConditionTypeEnum
    condition_category: ConditionCategoryEnum
    application_scope: ApplicationScopeEnum
    is_active: bool
    is_mandatory: bool
    evaluation_frequency: EvaluationFrequencyEnum
    member_visible: bool


# =====================================================
# SPECIALIZED SCHEMAS
# =====================================================

class ConditionEvaluationRequest(BaseModel):
    """Schema for condition evaluation requests"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "condition_id": "123e4567-e89b-12d3-a456-426614174000",
                "evaluation_context": {
                    "member_age": 35,
                    "member_gender": "M",
                    "employment_status": "ACTIVE",
                    "member_state": "TX",
                    "service_type": "MEDICAL"
                },
                "debug_mode": True,
                "force_evaluation": False
            }
        }
    )
    
    condition_id: UUID = Field(..., description="Condition to evaluate")
    evaluation_context: Dict[str, Any] = Field(..., description="Context data for evaluation")
    debug_mode: bool = Field(default=False, description="Enable debug information")
    force_evaluation: bool = Field(default=False, description="Force evaluation even if cached")


class ConditionEvaluationResult(BaseModel):
    """Schema for condition evaluation results"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "condition_id": "123e4567-e89b-12d3-a456-426614174000",
                "condition_code": "COND_AGE_001",
                "condition_name": "Age Eligibility Requirement",
                "satisfied": True,
                "result_details": {
                    "member_age": 35,
                    "min_age_required": 18,
                    "max_age_allowed": 65,
                    "age_check_passed": True
                },
                "evaluation_time_ms": 1.2,
                "from_cache": False,
                "satisfaction_reason": "Member age 35 is within required range 18-65",
                "member_explanation": "Your age meets the eligibility requirements"
            }
        }
    )
    
    condition_id: UUID
    condition_code: str
    condition_name: str
    
    # Evaluation results
    satisfied: bool = Field(..., description="Whether condition is satisfied")
    result_details: Dict[str, Any] = Field(..., description="Detailed evaluation results")
    
    # Execution information
    evaluation_time_ms: float = Field(..., description="Evaluation time in milliseconds")
    from_cache: bool = Field(default=False, description="Whether result came from cache")
    
    # Condition chain evaluation
    prerequisite_results: Optional[List[Dict[str, Any]]] = Field(None, description="Results of prerequisite conditions")
    child_condition_results: Optional[List[Dict[str, Any]]] = Field(None, description="Results of child conditions")
    
    # Debug information
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information if requested")
    evaluation_path: List[str] = Field(default_factory=list, description="Evaluation path taken")
    
    # Reasons and explanations
    satisfaction_reason: str = Field(..., description="Reason for satisfaction/failure")
    member_explanation: Optional[str] = Field(None, description="Member-friendly explanation")
    
    evaluated_at: datetime = Field(default_factory=datetime.utcnow, description="Evaluation timestamp")


# =====================================================
# LIST AND FILTER SCHEMAS
# =====================================================

class BenefitConditionFilter(BaseModel):
    """Schema for filtering benefit conditions"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "condition_type": "ELIGIBILITY",
                "condition_category": "MEMBER",
                "application_scope": "BENEFIT",
                "is_active": True,
                "is_mandatory": True,
                "member_visible": True,
                "search_term": "age eligibility"
            }
        }
    )
    
    condition_type: Optional[ConditionTypeEnum] = Field(None, description="Filter by condition type")
    condition_category: Optional[ConditionCategoryEnum] = Field(None, description="Filter by condition category")
    application_scope: Optional[ApplicationScopeEnum] = Field(None, description="Filter by application scope")
    logical_operator: Optional[LogicalOperatorEnum] = Field(None, description="Filter by logical operator")
    
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_mandatory: Optional[bool] = Field(None, description="Filter by mandatory status")
    is_system_generated: Optional[bool] = Field(None, description="Filter by system generated status")
    is_test_condition: Optional[bool] = Field(None, description="Filter by test condition status")
    member_visible: Optional[bool] = Field(None, description="Filter by member visibility")
    
    # Related entity filters
    coverage_id: Optional[UUID] = Field(None, description="Filter by coverage")
    benefit_type_id: Optional[UUID] = Field(None, description="Filter by benefit type")
    limit_id: Optional[UUID] = Field(None, description="Filter by limit")
    
    # Evaluation filters
    evaluation_frequency: Optional[EvaluationFrequencyEnum] = Field(None, description="Filter by evaluation frequency")
    auto_evaluation: Optional[bool] = Field(None, description="Filter by auto evaluation")
    requires_manual_review: Optional[bool] = Field(None, description="Filter by manual review requirement")
    
    # Performance filters
    success_rate_min: Optional[float] = Field(None, ge=0, le=100, description="Minimum success rate")
    evaluation_time_max: Optional[float] = Field(None, ge=0, description="Maximum evaluation time")
    
    # Hierarchy filters
    parent_condition_id: Optional[UUID] = Field(None, description="Filter by parent condition")
    has_child_conditions: Optional[bool] = Field(None, description="Filter by presence of child conditions")
    has_prerequisites: Optional[bool] = Field(None, description="Filter by presence of prerequisites")
    
    # Date filters
    effective_date_from: Optional[datetime] = Field(None, description="Effective from date")
    effective_date_to: Optional[datetime] = Field(None, description="Effective to date")
    
    # Search fields
    search_term: Optional[str] = Field(None, max_length=100, description="Search in names and descriptions")
    condition_codes: Optional[List[str]] = Field(None, description="Filter by specific condition codes")


class BenefitConditionListResponse(BaseModel):
    """Schema for paginated list of benefit conditions"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[BenefitConditionResponse] = Field(..., description="List of benefit conditions")
    total_count: int = Field(..., ge=0, description="Total number of conditions matching filter")
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

class BenefitConditionBulkCreate(BaseModel):
    """Schema for bulk creating benefit conditions"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conditions": [
                    {
                        "condition_code": "COND_AGE_001",
                        "condition_name": "Age Eligibility",
                        "condition_type": "ELIGIBILITY",
                        "condition_category": "MEMBER",
                        "age_conditions": {"min_age": 18, "max_age": 65}
                    }
                ],
                "skip_duplicates": True,
                "validate_dependencies": True
            }
        }
    )
    
    conditions: List[BenefitConditionCreate] = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="List of benefit conditions to create"
    )
    
    # Bulk operation settings
    skip_duplicates: bool = Field(default=False, description="Skip conditions with duplicate codes")
    validate_dependencies: bool = Field(default=True, description="Validate condition dependencies")
    auto_assign_evaluation_order: bool = Field(default=True, description="Auto-assign evaluation order")


class BenefitConditionBulkUpdate(BaseModel):
    """Schema for bulk updating benefit conditions"""
    
    model_config = ConfigDict(from_attributes=True)
    
    condition_ids: List[UUID] = Field(..., min_length=1, max_length=100)
    updates: BenefitConditionUpdate = Field(..., description="Fields to update")
    
    # Update options
    preserve_custom_conditions: bool = Field(default=True, description="Preserve custom condition criteria")
    recalculate_dependencies: bool = Field(default=False, description="Recalculate condition dependencies")
    clear_cache: bool = Field(default=False, description="Clear cached results after update")


class BenefitConditionBulkResponse(BaseModel):
    """Schema for bulk operation responses"""
    
    model_config = ConfigDict(from_attributes=True)
    
    successful_operations: int = Field(..., ge=0, description="Number of successful operations")
    failed_operations: int = Field(..., ge=0, description="Number of failed operations")
    total_operations: int = Field(..., ge=0, description="Total number of operations attempted")
    
    success_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of successful operations")
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of failed operations")
    
    # Additional results
    dependencies_updated: Optional[int] = Field(None, description="Number of dependencies updated")
    caches_cleared: Optional[int] = Field(None, description="Number of caches cleared")