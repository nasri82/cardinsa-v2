# app/modules/pricing/plans/schemas/plan_eligibility_rule_schema.py
"""
Plan Eligibility Rule Schemas

Pydantic models for API serialization and validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from enum import Enum

# Enums from the model
class RuleCategory(str, Enum):
    AGE = "age"
    GENDER = "gender"
    LOCATION = "location"
    OCCUPATION = "occupation"
    INCOME = "income"
    HEALTH = "health"
    FAMILY = "family"
    EMPLOYMENT = "employment"
    LIFESTYLE = "lifestyle"
    EXISTING_COVERAGE = "existing_coverage"
    CUSTOM = "custom"

class RuleType(str, Enum):
    INCLUSION = "inclusion"
    EXCLUSION = "exclusion"
    PREFERENCE = "preference"
    WARNING = "warning"

class RuleOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_EQUAL = "greater_equal"
    LESS_THAN = "less_than"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"

class RuleLogic(str, Enum):
    AND = "and"
    OR = "or"
    NOT = "not"
    XOR = "xor"

class RuleSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class EligibilityEvaluationRequest(BaseModel):
    """Request to evaluate eligibility rules"""
    applicant_data: Dict[str, Any] = Field(..., description="Applicant data to evaluate")
    check_date: Optional[date] = Field(None, description="Date for rule effectiveness check")
    override_codes: Optional[List[str]] = Field([], description="Override authorization codes")

class RuleEvaluationResult(BaseModel):
    """Result of rule evaluation"""
    rule_id: UUID
    rule_name: str
    rule_category: RuleCategory
    rule_type: RuleType
    rule_severity: RuleSeverity
    passed: bool
    message: Optional[str] = None
    recommendation: Optional[str] = None
    exception_applied: bool = False
    can_override: bool = False
    error: Optional[str] = None

class EligibilityEvaluationResponse(BaseModel):
    """Response for eligibility evaluation"""
    plan_id: UUID
    overall_eligible: bool
    evaluation_date: datetime
    total_rules_evaluated: int
    passed_rules: int
    failed_rules: int
    override_count: int
    rule_results: List[RuleEvaluationResult]
    blocking_issues: List[RuleEvaluationResult]
    warnings: List[RuleEvaluationResult]

class PlanEligibilityRuleBase(BaseModel):
    """Base schema for Plan Eligibility Rule"""
    rule_name: str = Field(..., min_length=1, max_length=100)
    rule_description: Optional[str] = None
    rule_code: Optional[str] = Field(None, max_length=50)
    
    # Configuration
    rule_category: RuleCategory = RuleCategory.CUSTOM
    rule_type: RuleType = RuleType.INCLUSION
    rule_severity: RuleSeverity = RuleSeverity.CRITICAL
    
    # Parent rule reference
    parent_rule_id: Optional[UUID] = None
    
    # Criteria
    field_name: Optional[str] = Field(None, max_length=100)
    operator: Optional[RuleOperator] = None
    value: Optional[Any] = None
    eligibility_criteria: Optional[Dict[str, Any]] = {}
    
    # Logic
    logic_operator: RuleLogic = RuleLogic.AND
    rule_group: Optional[str] = Field(None, max_length=50)
    priority: int = Field(0, ge=0)
    
    # Conditions
    is_mandatory: bool = True
    is_active: bool = True
    can_override: bool = False
    requires_documentation: bool = False
    
    # Age-specific
    min_age: Optional[int] = Field(None, ge=0, le=150)
    max_age: Optional[int] = Field(None, ge=0, le=150)
    age_calculation_date: Optional[str] = Field(None, max_length=50)
    
    # Messages
    success_message: Optional[str] = None
    failure_message: Optional[str] = None
    failure_message_ar: Optional[str] = None
    recommendation: Optional[str] = None
    
    # Dates
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    # Exceptions
    exception_conditions: Optional[Dict[str, Any]] = {}
    override_codes: Optional[List[str]] = []
    
    # Metadata
    validation_script: Optional[str] = None
    external_system_ref: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('max_age')
    def max_age_greater_than_min(cls, v, values):
        if v and 'min_age' in values and values['min_age']:
            if v <= values['min_age']:
                raise ValueError('Maximum age must be greater than minimum age')
        return v
    
    @validator('expiry_date')
    def expiry_after_effective(cls, v, values):
        if v and 'effective_date' in values and values['effective_date']:
            if v <= values['effective_date']:
                raise ValueError('Expiry date must be after effective date')
        return v
    
    @validator('rule_name')
    def rule_name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Rule name cannot be empty')
        return v.strip()

class PlanEligibilityRuleCreate(PlanEligibilityRuleBase):
    """Create schema for Plan Eligibility Rule"""
    pass

class PlanEligibilityRuleUpdate(BaseModel):
    """Update schema for Plan Eligibility Rule"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=100)
    rule_description: Optional[str] = None
    rule_code: Optional[str] = Field(None, max_length=50)
    
    rule_category: Optional[RuleCategory] = None
    rule_type: Optional[RuleType] = None
    rule_severity: Optional[RuleSeverity] = None
    
    parent_rule_id: Optional[UUID] = None
    
    field_name: Optional[str] = Field(None, max_length=100)
    operator: Optional[RuleOperator] = None
    value: Optional[Any] = None
    eligibility_criteria: Optional[Dict[str, Any]] = None
    
    logic_operator: Optional[RuleLogic] = None
    rule_group: Optional[str] = Field(None, max_length=50)
    priority: Optional[int] = Field(None, ge=0)
    
    is_mandatory: Optional[bool] = None
    is_active: Optional[bool] = None
    can_override: Optional[bool] = None
    requires_documentation: Optional[bool] = None
    
    min_age: Optional[int] = Field(None, ge=0, le=150)
    max_age: Optional[int] = Field(None, ge=0, le=150)
    age_calculation_date: Optional[str] = Field(None, max_length=50)
    
    success_message: Optional[str] = None
    failure_message: Optional[str] = None
    failure_message_ar: Optional[str] = None
    recommendation: Optional[str] = None
    
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    exception_conditions: Optional[Dict[str, Any]] = None
    override_codes: Optional[List[str]] = None
    
    validation_script: Optional[str] = None
    external_system_ref: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class PlanEligibilityRuleResponse(PlanEligibilityRuleBase):
    """Response schema for Plan Eligibility Rule"""
    id: UUID
    plan_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    # Computed fields
    is_effective: bool = True
    has_child_rules: bool = False
    
    class Config:
        from_attributes = True

class BulkEligibilityRuleCreate(BaseModel):
    """Bulk create eligibility rules"""
    rules: List[PlanEligibilityRuleCreate] = Field(..., min_items=1, max_items=50)

class EligibilityRuleSummary(BaseModel):
    """Summary of eligibility rules for a plan"""
    plan_id: UUID
    total_rules: int
    active_rules: int
    mandatory_rules: int
    by_category: Dict[str, int]
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    overridable_rules: int

class EligibilityRuleSearchFilters(BaseModel):
    """Search filters for eligibility rules"""
    rule_category: Optional[RuleCategory] = None
    rule_type: Optional[RuleType] = None
    rule_severity: Optional[RuleSeverity] = None
    is_mandatory: Optional[bool] = None
    is_active: Optional[bool] = None
    can_override: Optional[bool] = None
    rule_group: Optional[str] = None
    effective_date: Optional[date] = None
    text_search: Optional[str] = None
    tags: Optional[List[str]] = None
