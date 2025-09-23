# =============================================================================
# FILE: app/modules/underwriting/schemas/underwriting_schema.py
# WORLD-CLASS UNDERWRITING SCHEMAS - ENTERPRISE GRADE
# =============================================================================

"""
Underwriting Schemas - Enterprise Data Validation Layer

Comprehensive Pydantic schemas providing:
- Input validation and serialization
- Output formatting and transformation
- Type safety and data integrity
- API documentation support
- Business rule validation
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# Core imports
from app.core.schemas import BaseSchema, TimestampSchema, PaginationSchema
from app.core.validators import validate_uuid, validate_percentage, validate_currency


# =============================================================================
# ENUMS FOR VALIDATION
# =============================================================================

class DecisionEnum(str, Enum):
    """Underwriting decision outcomes"""
    APPROVED = "approved"
    REFERRED = "referred"
    REJECTED = "rejected"
    PENDING = "pending"
    CONDITIONAL = "conditional"
    DEFERRED = "deferred"


class RiskLevelEnum(str, Enum):
    """Risk level classification"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    UNACCEPTABLE = "unacceptable"


class StatusEnum(str, Enum):
    """Application/Profile status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PriorityEnum(str, Enum):
    """Priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class RuleCategoryEnum(str, Enum):
    """Rule categories"""
    MEDICAL = "medical"
    FINANCIAL = "financial"
    OCCUPATIONAL = "occupational"
    LIFESTYLE = "lifestyle"
    GEOGRAPHICAL = "geographical"
    LEGAL = "legal"
    ELIGIBILITY = "eligibility"
    COVERAGE_LIMITS = "coverage_limits"


class RuleTypeEnum(str, Enum):
    """Rule types"""
    AUTOMATIC = "automatic"
    MANUAL_REVIEW = "manual_review"
    CONDITIONAL = "conditional"
    EXCEPTION = "exception"


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class UnderwritingBaseSchema(BaseSchema):
    """Base schema for all underwriting entities"""
    pass


class RiskFactorSchema(BaseModel):
    """Risk factor representation"""
    category: str = Field(..., description="Risk factor category")
    factor: str = Field(..., description="Specific risk factor")
    severity: str = Field(default="medium", description="Risk factor severity")
    impact: Optional[Decimal] = Field(None, ge=0, le=100, description="Impact score")
    description: Optional[str] = Field(None, description="Factor description")
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return v


class MitigationFactorSchema(BaseModel):
    """Mitigation factor representation"""
    category: str = Field(..., description="Mitigation category")
    factor: str = Field(..., description="Specific mitigation factor")
    benefit: str = Field(default="medium", description="Mitigation benefit level")
    impact: Optional[Decimal] = Field(None, ge=0, le=100, description="Benefit impact score")
    description: Optional[str] = Field(None, description="Factor description")


class ConditionSchema(BaseModel):
    """Rule condition schema"""
    field: Optional[str] = Field(None, description="Field to evaluate")
    operator: str = Field(..., description="Comparison operator")
    value: Optional[Any] = Field(None, description="Expected value")
    conditions: Optional[List['ConditionSchema']] = Field(None, description="Sub-conditions")
    
    @field_validator('operator')
    @classmethod
    def validate_operator(cls, v):
        valid_operators = [
            'equals', 'not_equals', 'greater_than', 'less_than', 'greater_equal', 
            'less_equal', 'in', 'not_in', 'contains', 'not_contains', 'between',
            'regex_match', 'is_null', 'is_not_null', 'and', 'or', 'not'
        ]
        if v not in valid_operators:
            raise ValueError(f"Operator must be one of: {valid_operators}")
        return v
    
    @model_validator(mode='after')
    def validate_condition_structure(self):
        field = self.field
        operator = self.operator
        sub_conditions = self.conditions
        
        if operator in ['and', 'or', 'not']:
            if not sub_conditions:
                raise ValueError(f"Logical operator '{operator}' requires sub-conditions")
        else:
            if not field:
                raise ValueError(f"Field operator '{operator}' requires a field")
        
        return self


class ActionSchema(BaseModel):
    """Rule action schema"""
    type: str = Field(..., description="Action type")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action parameters")
    description: Optional[str] = Field(None, description="Action description")
    
    @field_validator('type')
    @classmethod
    def validate_action_type(cls, v):
        valid_types = [
            'premium_adjustment', 'coverage_modification', 'exclusion', 
            'requirement', 'escalation', 'assignment', 'notification'
        ]
        if v not in valid_types:
            raise ValueError(f"Action type must be one of: {valid_types}")
        return v


# =============================================================================
# UNDERWRITING RULE SCHEMAS
# =============================================================================

class UnderwritingRuleCreateSchema(UnderwritingBaseSchema):
    """Schema for creating underwriting rules"""
    rule_name: str = Field(..., min_length=1, max_length=100, description="Rule name")
    description: Optional[str] = Field(None, max_length=1000, description="Rule description")
    product_type: str = Field(..., max_length=50, description="Product type")
    rule_category: Optional[RuleCategoryEnum] = Field(None, description="Rule category")
    rule_type: RuleTypeEnum = Field(default=RuleTypeEnum.AUTOMATIC, description="Rule type")
    applies_to: Optional[str] = Field(None, max_length=50, description="What the rule applies to")
    
    conditions: ConditionSchema = Field(..., description="Rule conditions")
    actions: ActionSchema = Field(..., description="Rule actions")
    
    decision_outcome: Optional[DecisionEnum] = Field(None, description="Decision outcome")
    target_score: Optional[Decimal] = Field(None, ge=0, le=100, description="Target risk score")
    risk_score_impact: Decimal = Field(default=0, ge=-100, le=100, description="Risk score impact")
    premium_adjustment_percentage: Decimal = Field(default=0, ge=-100, le=500, description="Premium adjustment %")
    coverage_modifications: Optional[Dict[str, Any]] = Field(None, description="Coverage modifications")
    
    priority: int = Field(default=100, ge=0, le=1000, description="Rule priority")
    is_active: bool = Field(default=True, description="Rule is active")
    effective_from: date = Field(default_factory=date.today, description="Effective from date")
    effective_to: Optional[date] = Field(None, description="Effective to date")
    
    @field_validator('rule_name')
    @classmethod
    def validate_rule_name(cls, v):
        if not v.strip():
            raise ValueError("Rule name cannot be empty")
        return v.strip()
    
    @field_validator('product_type')
    @classmethod
    def validate_product_type(cls, v):
        valid_types = ['medical', 'motor', 'life', 'property', 'travel', 'general']
        if v.lower() not in valid_types:
            raise ValueError(f"Product type must be one of: {valid_types}")
        return v.lower()
    
    @model_validator(mode='after')
    def validate_effective_dates(self):
        effective_from = self.effective_from
        effective_to = self.effective_to
        
        if effective_from and effective_to and effective_from > effective_to:
            raise ValueError("Effective from date must be before effective to date")
        
        return self


class UnderwritingRuleUpdateSchema(UnderwritingBaseSchema):
    """Schema for updating underwriting rules"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Rule name")
    description: Optional[str] = Field(None, max_length=1000, description="Rule description")
    rule_category: Optional[RuleCategoryEnum] = Field(None, description="Rule category")
    rule_type: Optional[RuleTypeEnum] = Field(None, description="Rule type")
    applies_to: Optional[str] = Field(None, max_length=50, description="What the rule applies to")
    
    conditions: Optional[ConditionSchema] = Field(None, description="Rule conditions")
    actions: Optional[ActionSchema] = Field(None, description="Rule actions")
    
    decision_outcome: Optional[DecisionEnum] = Field(None, description="Decision outcome")
    target_score: Optional[Decimal] = Field(None, ge=0, le=100, description="Target risk score")
    risk_score_impact: Optional[Decimal] = Field(None, ge=-100, le=100, description="Risk score impact")
    premium_adjustment_percentage: Optional[Decimal] = Field(None, ge=-100, le=500, description="Premium adjustment %")
    coverage_modifications: Optional[Dict[str, Any]] = Field(None, description="Coverage modifications")
    
    priority: Optional[int] = Field(None, ge=0, le=1000, description="Rule priority")
    is_active: Optional[bool] = Field(None, description="Rule is active")
    effective_from: Optional[date] = Field(None, description="Effective from date")
    effective_to: Optional[date] = Field(None, description="Effective to date")


class UnderwritingRuleResponseSchema(TimestampSchema):
    """Schema for underwriting rule responses"""
    id: UUID = Field(..., description="Rule ID")
    rule_name: str = Field(..., description="Rule name")
    name: Optional[str] = Field(None, description="Alternative rule name")
    description: Optional[str] = Field(None, description="Rule description")
    
    product_type: str = Field(..., description="Product type")
    rule_category: Optional[str] = Field(None, description="Rule category")
    rule_type: str = Field(..., description="Rule type")
    applies_to: Optional[str] = Field(None, description="What the rule applies to")
    
    conditions: Dict[str, Any] = Field(..., description="Rule conditions")
    actions: Dict[str, Any] = Field(..., description="Rule actions")
    
    decision_outcome: Optional[str] = Field(None, description="Decision outcome")
    target_score: Optional[Decimal] = Field(None, description="Target risk score")
    risk_score_impact: Optional[Decimal] = Field(None, description="Risk score impact")
    premium_adjustment_percentage: Optional[Decimal] = Field(None, description="Premium adjustment %")
    coverage_modifications: Optional[Dict[str, Any]] = Field(None, description="Coverage modifications")
    
    priority: int = Field(..., description="Rule priority")
    is_active: bool = Field(..., description="Rule is active")
    effective_from: Optional[date] = Field(None, description="Effective from date")
    effective_to: Optional[date] = Field(None, description="Effective to date")
    
    created_by: Optional[UUID] = Field(None, description="Created by user ID")
    updated_by: Optional[UUID] = Field(None, description="Updated by user ID")
    approved_by: Optional[UUID] = Field(None, description="Approved by user ID")
    
    # Computed fields
    is_effective: bool = Field(..., description="Rule is currently effective")
    condition_summary: str = Field(..., description="Human-readable condition summary")
    impact_summary: str = Field(..., description="Impact summary")
    has_child_rules: bool = Field(default=False, description="Has child rules")
    
    model_config = {"from_attributes": True}


# =============================================================================
# UNDERWRITING PROFILE SCHEMAS
# =============================================================================

class UnderwritingProfileCreateSchema(UnderwritingBaseSchema):
    """Schema for creating underwriting profiles"""
    member_id: Optional[UUID] = Field(None, description="Member ID")
    policy_id: Optional[UUID] = Field(None, description="Policy ID")
    plan_id: Optional[UUID] = Field(None, description="Plan ID")
    quote_id: Optional[UUID] = Field(None, description="Quote ID")
    application_id: Optional[UUID] = Field(None, description="Application ID")
    
    profile_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Profile data")
    risk_data: Optional[Dict[str, Any]] = Field(None, description="Risk assessment data")
    medical_data: Optional[Dict[str, Any]] = Field(None, description="Medical information")
    financial_data: Optional[Dict[str, Any]] = Field(None, description="Financial information")
    
    priority: int = Field(default=5, ge=1, le=10, description="Processing priority")
    notes: Optional[str] = Field(None, max_length=2000, description="General notes")
    
    @field_validator('profile_data')
    @classmethod
    def validate_profile_data(cls, v):
        if v and not isinstance(v, dict):
            raise ValueError("Profile data must be a valid dictionary")
        return v


class UnderwritingProfileUpdateSchema(UnderwritingBaseSchema):
    """Schema for updating underwriting profiles"""
    risk_score: Optional[Decimal] = Field(None, ge=0, le=100, description="Risk score")
    risk_level: Optional[RiskLevelEnum] = Field(None, description="Risk level")
    decision: Optional[DecisionEnum] = Field(None, description="Underwriting decision")
    status: Optional[StatusEnum] = Field(None, description="Profile status")
    
    profile_data: Optional[Dict[str, Any]] = Field(None, description="Profile data")
    risk_factors: Optional[List[RiskFactorSchema]] = Field(None, description="Risk factors")
    mitigation_factors: Optional[List[MitigationFactorSchema]] = Field(None, description="Mitigation factors")
    
    premium_loading: Optional[Decimal] = Field(None, ge=-100, le=500, description="Premium loading %")
    premium_discount: Optional[Decimal] = Field(None, ge=0, le=100, description="Premium discount %")
    
    exclusions: Optional[List[str]] = Field(None, description="Coverage exclusions")
    conditions: Optional[List[str]] = Field(None, description="Special conditions")
    
    notes: Optional[str] = Field(None, max_length=2000, description="General notes")
    underwriter_notes: Optional[str] = Field(None, max_length=2000, description="Underwriter notes")
    
    assigned_to: Optional[UUID] = Field(None, description="Assigned to user ID")
    priority: Optional[int] = Field(None, ge=1, le=10, description="Processing priority")


class UnderwritingProfileResponseSchema(TimestampSchema):
    """Schema for underwriting profile responses"""
    id: UUID = Field(..., description="Profile ID")
    
    member_id: Optional[UUID] = Field(None, description="Member ID")
    policy_id: Optional[UUID] = Field(None, description="Policy ID")
    plan_id: Optional[UUID] = Field(None, description="Plan ID")
    quote_id: Optional[UUID] = Field(None, description="Quote ID")
    application_id: Optional[UUID] = Field(None, description="Application ID")
    
    risk_score: Optional[Decimal] = Field(None, description="Risk score")
    risk_level: Optional[str] = Field(None, description="Risk level")
    base_risk_score: Optional[Decimal] = Field(None, description="Base risk score")
    adjusted_risk_score: Optional[Decimal] = Field(None, description="Adjusted risk score")
    
    decision: Optional[str] = Field(None, description="Underwriting decision")
    status: str = Field(..., description="Profile status")
    evaluation_method: str = Field(..., description="Evaluation method")
    
    premium_loading: Optional[Decimal] = Field(None, description="Premium loading %")
    premium_discount: Optional[Decimal] = Field(None, description="Premium discount %")
    net_premium_adjustment: Optional[Decimal] = Field(None, description="Net premium adjustment %")
    
    priority: int = Field(..., description="Processing priority")
    assigned_to: Optional[UUID] = Field(None, description="Assigned to user ID")
    sla_due_date: Optional[datetime] = Field(None, description="SLA due date")
    
    evaluation_started_at: Optional[datetime] = Field(None, description="Evaluation start time")
    evaluation_completed_at: Optional[datetime] = Field(None, description="Evaluation completion time")
    
    created_by: Optional[UUID] = Field(None, description="Created by user ID")
    updated_by: Optional[UUID] = Field(None, description="Updated by user ID")
    evaluated_by: Optional[UUID] = Field(None, description="Evaluated by user ID")
    
    # Computed fields
    is_overdue: bool = Field(..., description="Profile is overdue")
    is_high_priority: bool = Field(..., description="Profile is high priority")
    evaluation_duration_minutes: Optional[int] = Field(None, description="Evaluation duration in minutes")
    
    model_config = {"from_attributes": True}


class UnderwritingProfileDetailSchema(UnderwritingProfileResponseSchema):
    """Detailed profile schema with sensitive data"""
    profile_data: Optional[Dict[str, Any]] = Field(None, description="Complete profile data")
    risk_factors: Optional[Dict[str, Any]] = Field(None, description="Risk factors")
    mitigation_factors: Optional[Dict[str, Any]] = Field(None, description="Mitigation factors")
    exclusions: Optional[Dict[str, Any]] = Field(None, description="Coverage exclusions")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Special conditions")
    coverage_limits: Optional[Dict[str, Any]] = Field(None, description="Coverage limits")
    waiting_periods: Optional[Dict[str, Any]] = Field(None, description="Waiting periods")
    deductible_adjustments: Optional[Dict[str, Any]] = Field(None, description="Deductible adjustments")
    
    notes: Optional[str] = Field(None, description="General notes")
    underwriter_notes: Optional[str] = Field(None, description="Underwriter notes")
    medical_notes: Optional[str] = Field(None, description="Medical notes")
    financial_notes: Optional[str] = Field(None, description="Financial notes")


# =============================================================================
# UNDERWRITING APPLICATION SCHEMAS
# =============================================================================

class UnderwritingApplicationCreateSchema(UnderwritingBaseSchema):
    """Schema for creating underwriting applications"""
    member_id: Optional[UUID] = Field(None, description="Member ID")
    product_type: str = Field(..., description="Product type")
    product_id: Optional[UUID] = Field(None, description="Product ID")
    plan_id: Optional[UUID] = Field(None, description="Plan ID")
    coverage_amount: Optional[Decimal] = Field(None, ge=0, description="Coverage amount")
    
    application_data: Dict[str, Any] = Field(..., description="Complete application data")
    applicant_data: Optional[Dict[str, Any]] = Field(None, description="Primary applicant data")
    beneficiary_data: Optional[Dict[str, Any]] = Field(None, description="Beneficiary data")
    medical_data: Optional[Dict[str, Any]] = Field(None, description="Medical information")
    financial_data: Optional[Dict[str, Any]] = Field(None, description="Financial information")
    risk_data: Optional[Dict[str, Any]] = Field(None, description="Risk assessment data")
    
    submission_channel: Optional[str] = Field(None, description="Submission channel")
    source: Optional[str] = Field(None, description="Application source")
    priority: PriorityEnum = Field(default=PriorityEnum.NORMAL, description="Processing priority")
    
    estimated_premium: Optional[Decimal] = Field(None, ge=0, description="Estimated premium")
    notes: Optional[str] = Field(None, max_length=2000, description="General notes")
    
    @field_validator('product_type')
    @classmethod
    def validate_product_type(cls, v):
        valid_types = ['medical', 'motor', 'life', 'property', 'travel', 'general', 'disability', 'critical_illness']
        if v.lower() not in valid_types:
            raise ValueError(f"Product type must be one of: {valid_types}")
        return v.lower()
    
    @field_validator('application_data')
    @classmethod
    def validate_application_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Application data must be a valid dictionary")
        
        required_fields = ['applicant_info', 'contact_info']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Application data must contain '{field}' section")
        
        return v
    
    @field_validator('submission_channel')
    @classmethod
    def validate_submission_channel(cls, v):
        if v:
            valid_channels = ['online', 'agent', 'broker', 'phone', 'email', 'mail', 'walk_in', 'partner', 'api']
            if v.lower() not in valid_channels:
                raise ValueError(f"Submission channel must be one of: {valid_channels}")
            return v.lower()
        return v


class UnderwritingApplicationUpdateSchema(UnderwritingBaseSchema):
    """Schema for updating underwriting applications"""
    status: Optional[StatusEnum] = Field(None, description="Application status")
    priority: Optional[PriorityEnum] = Field(None, description="Processing priority")
    
    application_data: Optional[Dict[str, Any]] = Field(None, description="Updated application data")
    medical_data: Optional[Dict[str, Any]] = Field(None, description="Updated medical information")
    financial_data: Optional[Dict[str, Any]] = Field(None, description="Updated financial information")
    risk_data: Optional[Dict[str, Any]] = Field(None, description="Updated risk assessment data")
    
    assigned_underwriter: Optional[UUID] = Field(None, description="Assigned underwriter ID")
    assigned_to: Optional[UUID] = Field(None, description="Assigned to user ID")
    
    estimated_premium: Optional[Decimal] = Field(None, ge=0, description="Updated estimated premium")
    quoted_premium: Optional[Decimal] = Field(None, ge=0, description="Quoted premium")
    final_premium: Optional[Decimal] = Field(None, ge=0, description="Final premium")
    
    notes: Optional[str] = Field(None, max_length=2000, description="Updated notes")
    internal_notes: Optional[str] = Field(None, max_length=2000, description="Internal notes")
    underwriter_notes: Optional[str] = Field(None, max_length=2000, description="Underwriter notes")


class UnderwritingApplicationResponseSchema(TimestampSchema):
    """Schema for underwriting application responses"""
    id: UUID = Field(..., description="Application ID")
    application_number: str = Field(..., description="Application number")
    reference_number: Optional[str] = Field(None, description="Reference number")
    
    member_id: Optional[UUID] = Field(None, description="Member ID")
    policy_id: Optional[UUID] = Field(None, description="Policy ID")
    quote_id: Optional[UUID] = Field(None, description="Quote ID")
    profile_id: Optional[UUID] = Field(None, description="Profile ID")
    
    product_type: str = Field(..., description="Product type")
    product_id: Optional[UUID] = Field(None, description="Product ID")
    plan_id: Optional[UUID] = Field(None, description="Plan ID")
    coverage_amount: Optional[Decimal] = Field(None, description="Coverage amount")
    
    submission_channel: Optional[str] = Field(None, description="Submission channel")
    source: Optional[str] = Field(None, description="Application source")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    submitted_by: Optional[UUID] = Field(None, description="Submitted by user ID")
    
    status: str = Field(..., description="Application status")
    priority: str = Field(..., description="Processing priority")
    
    assigned_underwriter: Optional[UUID] = Field(None, description="Assigned underwriter ID")
    assigned_to: Optional[UUID] = Field(None, description="Assigned to user ID")
    assigned_at: Optional[datetime] = Field(None, description="Assignment timestamp")
    
    sla_due_date: Optional[datetime] = Field(None, description="SLA due date")
    processing_started_at: Optional[datetime] = Field(None, description="Processing start time")
    actual_completion_date: Optional[datetime] = Field(None, description="Actual completion time")
    
    decision_at: Optional[datetime] = Field(None, description="Decision timestamp")
    decision_by: Optional[UUID] = Field(None, description="Decision by user ID")
    
    estimated_premium: Optional[Decimal] = Field(None, description="Estimated premium")
    quoted_premium: Optional[Decimal] = Field(None, description="Quoted premium")
    final_premium: Optional[Decimal] = Field(None, description="Final premium")
    premium_score: Optional[Decimal] = Field(None, description="Premium score")
    
    quality_score: Optional[Decimal] = Field(None, description="Quality score")
    compliance_checked: bool = Field(..., description="Compliance checked")
    
    created_by: Optional[UUID] = Field(None, description="Created by user ID")
    updated_by: Optional[UUID] = Field(None, description="Updated by user ID")
    
    # Computed fields
    is_overdue: bool = Field(..., description="Application is overdue")
    is_high_priority: bool = Field(..., description="Application is high priority")
    is_complete: bool = Field(..., description="Application is complete")
    processing_duration_hours: Optional[int] = Field(None, description="Processing duration in hours")
    missing_requirements: List[str] = Field(default_factory=list, description="Missing requirements")
    
    model_config = {"from_attributes": True}


# =============================================================================
# WORKFLOW SCHEMAS
# =============================================================================

class WorkflowStepCreateSchema(UnderwritingBaseSchema):
    """Schema for creating workflow steps"""
    name: str = Field(..., min_length=1, max_length=100, description="Step name")
    description: Optional[str] = Field(None, max_length=1000, description="Step description")
    code: Optional[str] = Field(None, max_length=50, description="Step code")
    
    step_type: str = Field(..., description="Step type")
    order_index: int = Field(..., ge=0, description="Step order")
    is_required: bool = Field(default=True, description="Step is required")
    is_parallel: bool = Field(default=False, description="Step runs in parallel")
    
    conditions: Optional[Dict[str, Any]] = Field(None, description="Step conditions")
    actions: Optional[Dict[str, Any]] = Field(None, description="Step actions")
    rules: Optional[Dict[str, Any]] = Field(None, description="Business rules")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Step configuration")
    
    sla_hours: Optional[int] = Field(None, ge=0, description="SLA in hours")
    timeout_hours: Optional[int] = Field(None, ge=0, description="Timeout in hours")
    
    @field_validator('step_type')
    @classmethod
    def validate_step_type(cls, v):
        valid_types = ['auto', 'manual', 'conditional', 'approval', 'notification', 'integration', 'decision']
        if v not in valid_types:
            raise ValueError(f"Step type must be one of: {valid_types}")
        return v


class WorkflowCreateSchema(UnderwritingBaseSchema):
    """Schema for creating workflows"""
    name: str = Field(..., min_length=1, max_length=100, description="Workflow name")
    description: Optional[str] = Field(None, max_length=1000, description="Workflow description")
    code: Optional[str] = Field(None, max_length=50, description="Workflow code")
    version: str = Field(default="1.0", description="Workflow version")
    
    product_types: Optional[List[str]] = Field(None, description="Applicable product types")
    triggers: Dict[str, Any] = Field(..., description="Workflow triggers")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Execution conditions")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Workflow configuration")
    
    is_active: bool = Field(default=True, description="Workflow is active")
    is_default: bool = Field(default=False, description="Default workflow")
    
    default_sla_hours: Optional[int] = Field(None, ge=0, description="Default SLA hours")
    max_duration_hours: Optional[int] = Field(None, ge=0, description="Maximum duration hours")
    
    steps: Optional[List[WorkflowStepCreateSchema]] = Field(None, description="Workflow steps")


# =============================================================================
# REQUEST/RESPONSE SCHEMAS
# =============================================================================

class UnderwritingEvaluationRequest(UnderwritingBaseSchema):
    """Schema for underwriting evaluation requests"""
    application_id: UUID = Field(..., description="Application to evaluate")
    force_manual_review: bool = Field(default=False, description="Force manual review")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    evaluation_options: Optional[Dict[str, Any]] = Field(None, description="Evaluation options")


class RiskAssessmentResult(BaseModel):
    """Risk assessment result schema"""
    overall_score: Decimal = Field(..., ge=0, le=100, description="Overall risk score")
    risk_level: RiskLevelEnum = Field(..., description="Risk level")
    category_scores: Dict[str, Decimal] = Field(..., description="Category-wise risk scores")
    risk_factors: List[RiskFactorSchema] = Field(default_factory=list, description="Risk factors")
    mitigation_factors: List[MitigationFactorSchema] = Field(default_factory=list, description="Mitigation factors")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    confidence_level: Decimal = Field(..., ge=0, le=100, description="Confidence level")


class RuleEvaluationResult(BaseModel):
    """Rule evaluation result schema"""
    rule_id: UUID = Field(..., description="Rule ID")
    rule_name: str = Field(..., description="Rule name")
    matched: bool = Field(..., description="Rule matched")
    decision: Optional[DecisionEnum] = Field(None, description="Rule decision")
    risk_score_impact: Optional[Decimal] = Field(None, description="Risk score impact")
    premium_adjustment: Optional[Decimal] = Field(None, description="Premium adjustment")
    conditions_met: List[str] = Field(default_factory=list, description="Conditions met")
    actions_taken: List[str] = Field(default_factory=list, description="Actions taken")
    notes: Optional[str] = Field(None, description="Evaluation notes")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")


class UnderwritingDecisionResult(BaseModel):
    """Complete underwriting decision result schema"""
    decision: DecisionEnum = Field(..., description="Final decision")
    risk_score: Decimal = Field(..., ge=0, le=100, description="Final risk score")
    premium_adjustment: Decimal = Field(..., description="Premium adjustment percentage")
    conditions: List[str] = Field(default_factory=list, description="Approval conditions")
    exclusions: List[str] = Field(default_factory=list, description="Coverage exclusions")
    rule_results: List[RuleEvaluationResult] = Field(default_factory=list, description="Rule evaluation results")
    risk_assessment: Optional[RiskAssessmentResult] = Field(None, description="Risk assessment details")
    workflow_id: Optional[UUID] = Field(None, description="Started workflow ID")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    confidence_score: Optional[Decimal] = Field(None, ge=0, le=100, description="Decision confidence")
    next_actions: List[str] = Field(default_factory=list, description="Recommended next actions")
    requires_manual_review: bool = Field(default=False, description="Requires manual review")
    escalation_required: bool = Field(default=False, description="Escalation required")


# =============================================================================
# SEARCH AND FILTER SCHEMAS
# =============================================================================

class UnderwritingRuleSearchFilters(BaseModel):
    """Search filters for underwriting rules"""
    product_type: Optional[str] = Field(None, description="Filter by product type")
    rule_category: Optional[RuleCategoryEnum] = Field(None, description="Filter by category")
    rule_type: Optional[RuleTypeEnum] = Field(None, description="Filter by type")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    decision_outcome: Optional[DecisionEnum] = Field(None, description="Filter by decision")
    priority_min: Optional[int] = Field(None, ge=0, le=1000, description="Minimum priority")
    priority_max: Optional[int] = Field(None, ge=0, le=1000, description="Maximum priority")
    effective_date: Optional[date] = Field(None, description="Effective on date")
    search_text: Optional[str] = Field(None, min_length=1, max_length=100, description="Search in name/description")


class UnderwritingProfileSearchFilters(BaseModel):
    """Search filters for underwriting profiles"""
    member_id: Optional[UUID] = Field(None, description="Filter by member ID")
    status: Optional[StatusEnum] = Field(None, description="Filter by status")
    decision: Optional[DecisionEnum] = Field(None, description="Filter by decision")
    risk_level: Optional[RiskLevelEnum] = Field(None, description="Filter by risk level")
    assigned_to: Optional[UUID] = Field(None, description="Filter by assigned user")
    priority_min: Optional[int] = Field(None, ge=1, le=10, description="Minimum priority")
    priority_max: Optional[int] = Field(None, ge=1, le=10, description="Maximum priority")
    is_overdue: Optional[bool] = Field(None, description="Filter overdue profiles")
    evaluation_method: Optional[str] = Field(None, description="Filter by evaluation method")
    created_date_from: Optional[date] = Field(None, description="Created from date")
    created_date_to: Optional[date] = Field(None, description="Created to date")


class UnderwritingApplicationSearchFilters(BaseModel):
    """Search filters for underwriting applications"""
    application_number: Optional[str] = Field(None, min_length=1, max_length=30, description="Application number")
    member_id: Optional[UUID] = Field(None, description="Filter by member ID")
    product_type: Optional[str] = Field(None, description="Filter by product type")
    status: Optional[StatusEnum] = Field(None, description="Filter by status")
    priority: Optional[PriorityEnum] = Field(None, description="Filter by priority")
    submission_channel: Optional[str] = Field(None, description="Filter by submission channel")
    source: Optional[str] = Field(None, description="Filter by source")
    assigned_to: Optional[UUID] = Field(None, description="Filter by assigned user")
    is_overdue: Optional[bool] = Field(None, description="Filter overdue applications")
    is_complete: Optional[bool] = Field(None, description="Filter complete applications")
    submitted_date_from: Optional[date] = Field(None, description="Submitted from date")
    submitted_date_to: Optional[date] = Field(None, description="Submitted to date")
    coverage_amount_min: Optional[Decimal] = Field(None, ge=0, description="Minimum coverage amount")
    coverage_amount_max: Optional[Decimal] = Field(None, ge=0, description="Maximum coverage amount")


# =============================================================================
# BULK OPERATION SCHEMAS
# =============================================================================

class BulkRuleCreateSchema(UnderwritingBaseSchema):
    """Schema for bulk rule creation"""
    rules: List[UnderwritingRuleCreateSchema] = Field(..., min_length=1, max_length=100, description="Rules to create")
    validate_only: bool = Field(default=False, description="Only validate, don't create")
    skip_duplicates: bool = Field(default=True, description="Skip duplicate rule names")


class BulkOperationResult(BaseModel):
    """Result of bulk operations"""
    total_requested: int = Field(..., description="Total items requested")
    successful: int = Field(..., description="Successfully processed")
    failed: int = Field(..., description="Failed to process")
    skipped: int = Field(default=0, description="Skipped items")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    created_ids: List[UUID] = Field(default_factory=list, description="Created item IDs")


# =============================================================================
# ANALYTICS SCHEMAS
# =============================================================================

class UnderwritingAnalytics(BaseModel):
    """Underwriting analytics schema"""
    period_start: date = Field(..., description="Analytics period start")
    period_end: date = Field(..., description="Analytics period end")
    
    total_applications: int = Field(..., description="Total applications")
    approved_applications: int = Field(..., description="Approved applications")
    rejected_applications: int = Field(..., description="Rejected applications")
    referred_applications: int = Field(..., description="Referred applications")
    
    approval_rate: Decimal = Field(..., ge=0, le=100, description="Approval rate %")
    rejection_rate: Decimal = Field(..., ge=0, le=100, description="Rejection rate %")
    referral_rate: Decimal = Field(..., ge=0, le=100, description="Referral rate %")
    
    average_risk_score: Decimal = Field(..., ge=0, le=100, description="Average risk score")
    average_processing_time_hours: Decimal = Field(..., ge=0, description="Average processing time")
    sla_compliance_rate: Decimal = Field(..., ge=0, le=100, description="SLA compliance rate %")
    
    risk_distribution: Dict[str, int] = Field(..., description="Risk level distribution")
    product_distribution: Dict[str, int] = Field(..., description="Product type distribution")
    channel_distribution: Dict[str, int] = Field(..., description="Channel distribution")


# =============================================================================
# UPDATE SCHEMAS TO HANDLE RECURSIVE REFERENCES
# =============================================================================

# Update recursive models
ConditionSchema.model_rebuild()


# =============================================================================
# EXPORT ALL SCHEMAS
# =============================================================================

__all__ = [
    # Base schemas
    'UnderwritingBaseSchema',
    'RiskFactorSchema',
    'MitigationFactorSchema',
    'ConditionSchema',
    'ActionSchema',
    
    # Rule schemas
    'UnderwritingRuleCreateSchema',
    'UnderwritingRuleUpdateSchema',
    'UnderwritingRuleResponseSchema',
    
    # Profile schemas
    'UnderwritingProfileCreateSchema',
    'UnderwritingProfileUpdateSchema',
    'UnderwritingProfileResponseSchema',
    'UnderwritingProfileDetailSchema',
    
    # Application schemas
    'UnderwritingApplicationCreateSchema',
    'UnderwritingApplicationUpdateSchema',
    'UnderwritingApplicationResponseSchema',
    
    # Workflow schemas
    'WorkflowStepCreateSchema',
    'WorkflowCreateSchema',
    
    # Request/Response schemas
    'UnderwritingEvaluationRequest',
    'RiskAssessmentResult',
    'RuleEvaluationResult',
    'UnderwritingDecisionResult',
    
    # Search schemas
    'UnderwritingRuleSearchFilters',
    'UnderwritingProfileSearchFilters',
    'UnderwritingApplicationSearchFilters',
    
    # Bulk operation schemas
    'BulkRuleCreateSchema',
    'BulkOperationResult',
    
    # Analytics schemas
    'UnderwritingAnalytics',
    
    # Enums
    'DecisionEnum',
    'RiskLevelEnum',
    'StatusEnum',
    'PriorityEnum',
    'RuleCategoryEnum',
    'RuleTypeEnum'
]