# app/modules/benefits/schemas/benefit_calculation_rule_schema.py
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from uuid import UUID
from decimal import Decimal

# Import enums from the correct location
from app.modules.pricing.benefits.models.benefit_calculation_rule_enums import (
    RuleType as RuleTypeEnum,
    CalculationMethod as CalculationMethodEnum,
    RuleCategory as RuleCategoryEnum,
    ResetFrequency as ResetFrequencyEnum,
    DeploymentStage as DeploymentStageEnum,
    RuleStatus as RuleStatusEnum,
    AuthorizationLevel,
    FormulaComplexity,
    CurrencyCode
)


# =====================================================
# BASE SCHEMA
# =====================================================

class BenefitCalculationRuleBase(BaseModel):
    """Base schema for benefit calculation rule with common fields"""
    
    rule_code: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Unique code identifying the calculation rule",
        example="CALC_DEDUCT_001"
    )
    rule_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Display name of the calculation rule",
        example="Individual Deductible Calculation"
    )
    rule_name_ar: Optional[str] = Field(
        None, 
        max_length=100,
        description="Arabic translation of rule name",
        example="حساب الخصم الفردي"
    )
    
    # Rule classification
    rule_type: RuleTypeEnum = Field(
        ...,
        description="Type classification of the rule"
    )
    calculation_method: CalculationMethodEnum = Field(
        default=CalculationMethodEnum.FORMULA,
        description="Method used for calculation"
    )
    rule_category: RuleCategoryEnum = Field(
        default=RuleCategoryEnum.FINANCIAL,
        description="Category classification of the rule"
    )
    
    # Rule hierarchy and execution
    priority_order: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Priority order for rule execution",
        example=1
    )
    execution_sequence: int = Field(
        default=1,
        ge=1,
        description="Execution sequence within priority group"
    )
    
    # Basic calculation parameters
    base_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Base amount for calculations",
        example="1000.00"
    )
    minimum_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Minimum calculation result",
        example="25.00"
    )
    maximum_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Maximum calculation result",
        example="5000.00"
    )
    
    # Percentage-based calculations
    percentage_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=4,
        description="Percentage rate for calculations",
        example="20.0000"
    )
    discount_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=4,
        description="Discount rate to apply"
    )
    
    # Network-based parameters
    in_network_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="In-network specific amount"
    )
    out_of_network_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=15,
        decimal_places=2,
        description="Out-of-network specific amount"
    )
    in_network_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=4,
        description="In-network percentage"
    )
    out_of_network_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=4,
        description="Out-of-network percentage"
    )
    
    # Currency and precision
    currency_code: str = Field(
        default="USD",
        max_length=3,
        description="Currency code for monetary calculations"
    )
    decimal_precision: int = Field(
        default=2,
        ge=0,
        le=4,
        description="Decimal precision for results"
    )
    
    # Accumulation behavior
    contributes_to_deductible: bool = Field(
        default=False,
        description="Whether result contributes to deductible"
    )
    contributes_to_oop_max: bool = Field(
        default=False,
        description="Whether result contributes to out-of-pocket maximum"
    )
    contributes_to_benefit_max: bool = Field(
        default=False,
        description="Whether result contributes to benefit maximum"
    )
    
    # Reset behavior
    reset_frequency: ResetFrequencyEnum = Field(
        default=ResetFrequencyEnum.ANNUAL,
        description="How often accumulations reset"
    )
    
    # Authorization requirements
    requires_authorization: bool = Field(
        default=False,
        description="Whether rule requires authorization to execute"
    )
    authorization_level: Optional[str] = Field(
        None,
        max_length=30,
        description="Level of authorization required"
    )
    
    # Status and availability
    is_active: bool = Field(
        default=True,
        description="Whether the rule is currently active"
    )
    is_system_rule: bool = Field(
        default=False,
        description="Whether this is a system-generated rule"
    )
    is_mandatory: bool = Field(
        default=False,
        description="Whether this rule is mandatory"
    )
    
    # Testing and deployment
    is_test_rule: bool = Field(
        default=False,
        description="Whether this is a test rule"
    )
    deployment_stage: DeploymentStageEnum = Field(
        default=DeploymentStageEnum.PRODUCTION,
        description="Deployment stage of the rule"
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


# =====================================================
# CREATE SCHEMA
# =====================================================

class BenefitCalculationRuleCreate(BenefitCalculationRuleBase):
    """Schema for creating a new benefit calculation rule"""
    
    # Related entity references
    benefit_type_id: Optional[UUID] = Field(
        None,
        description="ID of the benefit type this rule applies to"
    )
    coverage_id: Optional[UUID] = Field(
        None,
        description="ID of the coverage this rule applies to"
    )
    limit_id: Optional[UUID] = Field(
        None,
        description="ID of the benefit limit this rule applies to"
    )
    
    # Rule dependencies
    parent_rule_id: Optional[UUID] = Field(
        None,
        description="Parent rule ID for hierarchical rules"
    )
    depends_on_rules: Optional[List[UUID]] = Field(
        None,
        description="List of rule IDs this rule depends on"
    )
    
    # Calculation formulas and logic
    calculation_formula: Optional[str] = Field(
        None,
        description="Primary calculation formula",
        example="IF(service_cost > deductible_remaining, (service_cost - deductible_remaining) * coinsurance_rate, 0)"
    )
    in_network_formula: Optional[str] = Field(
        None,
        description="Formula specific to in-network services"
    )
    out_of_network_formula: Optional[str] = Field(
        None,
        description="Formula specific to out-of-network services"
    )
    emergency_formula: Optional[str] = Field(
        None,
        description="Formula for emergency services"
    )
    
    # Formula variables and parameters
    formula_variables: Optional[Dict[str, Union[str, int, float]]] = Field(
        None,
        description="Variables used in formulas",
        example={
            "deductible_rate": 0.2,
            "max_benefit": 5000,
            "frequency_limit": 12
        }
    )
    calculation_parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Calculation parameters and settings",
        example={
            "rounding_method": "up",
            "minimum_payment": 10.00,
            "precision": 2
        }
    )
    
    # Conditions and triggers
    trigger_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Conditions that trigger this rule",
        example={
            "age": {"min": 18, "max": 65},
            "coverage_type": "MEDICAL",
            "service_category": "OUTPATIENT"
        }
    )
    exclusion_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Conditions that exclude this rule",
        example={
            "pre_existing": True,
            "experimental_treatment": True
        }
    )
    
    # Lookup tables for lookup-based calculations
    lookup_table_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Lookup table data for calculations",
        example={
            "age_brackets": [
                {"min_age": 0, "max_age": 17, "rate": 0.1},
                {"min_age": 18, "max_age": 64, "rate": 0.2}
            ]
        }
    )
    
    # Validation and business rules
    validation_rules: Optional[Dict[str, Any]] = Field(
        None,
        description="Validation rules for inputs and outputs",
        example={
            "required_fields": ["age", "gender"],
            "min_service_cost": 0.01
        }
    )
    error_handling: Optional[Dict[str, str]] = Field(
        None,
        description="Error handling configuration",
        example={
            "on_missing_data": "use_default",
            "on_calculation_error": "deny_claim"
        }
    )
    
    # Performance and reporting
    track_utilization: bool = Field(
        default=False,
        description="Whether to track utilization of this rule"
    )
    performance_metrics: Optional[Dict[str, float]] = Field(
        None,
        description="Performance metrics and targets"
    )
    
    # Documentation
    description: Optional[str] = Field(
        None,
        description="Detailed description of the rule"
    )
    description_ar: Optional[str] = Field(
        None,
        description="Arabic description of the rule"
    )
    technical_notes: Optional[str] = Field(
        None,
        description="Technical implementation notes"
    )
    business_rationale: Optional[str] = Field(
        None,
        description="Business rationale for this rule"
    )
    
    # Examples and test cases
    example_scenarios: Optional[Dict[str, Any]] = Field(
        None,
        description="Example calculation scenarios"
    )
    test_cases: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Test cases for validation"
    )
    
    @validator('rule_code')
    def validate_rule_code(cls, v):
        """Validate rule code format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Rule code must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()
    
    @validator('effective_to')
    def validate_effective_to(cls, v, values):
        """Validate effective_to is after effective_from"""
        if v and 'effective_from' in values and v <= values['effective_from']:
            raise ValueError('Effective to date must be after effective from date')
        return v
    
    @validator('priority_order', 'execution_sequence')
    def validate_positive_integers(cls, v):
        """Validate positive integers"""
        if v <= 0:
            raise ValueError('Priority order and execution sequence must be positive integers')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_code": "CALC_DEDUCT_001",
                "rule_name": "Individual Deductible Calculation",
                "rule_type": "DEDUCTIBLE",
                "calculation_method": "PERCENTAGE",
                "priority_order": 1,
                "percentage_rate": "100.0000",
                "base_amount": "1000.00",
                "contributes_to_oop_max": True,
                "is_mandatory": True,
                "trigger_conditions": {
                    "deductible_applies": True,
                    "service_type": "MEDICAL"
                }
            }
        }
    )


# =====================================================
# UPDATE SCHEMA
# =====================================================

class BenefitCalculationRuleUpdate(BaseModel):
    """Schema for updating an existing benefit calculation rule"""
    
    rule_name: Optional[str] = Field(None, min_length=1, max_length=100)
    rule_name_ar: Optional[str] = Field(None, max_length=100)
    
    rule_type: Optional[RuleTypeEnum] = Field(None)
    calculation_method: Optional[CalculationMethodEnum] = Field(None)
    rule_category: Optional[RuleCategoryEnum] = Field(None)
    
    # Priority and execution updates
    priority_order: Optional[int] = Field(None, ge=1, le=1000)
    execution_sequence: Optional[int] = Field(None, ge=1)
    
    # Amount updates
    base_amount: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    minimum_amount: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    maximum_amount: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Percentage updates
    percentage_rate: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=4)
    discount_rate: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=4)
    
    # Network-specific updates
    in_network_amount: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    out_of_network_amount: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    in_network_percentage: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=4)
    out_of_network_percentage: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=4)
    
    # Precision updates
    decimal_precision: Optional[int] = Field(None, ge=0, le=4)
    
    # Accumulation updates
    contributes_to_deductible: Optional[bool] = Field(None)
    contributes_to_oop_max: Optional[bool] = Field(None)
    contributes_to_benefit_max: Optional[bool] = Field(None)
    
    # Reset updates
    reset_frequency: Optional[ResetFrequencyEnum] = Field(None)
    
    # Authorization updates
    requires_authorization: Optional[bool] = Field(None)
    authorization_level: Optional[str] = Field(None, max_length=30)
    
    # Status updates
    is_active: Optional[bool] = Field(None)
    is_mandatory: Optional[bool] = Field(None)
    is_test_rule: Optional[bool] = Field(None)
    deployment_stage: Optional[DeploymentStageEnum] = Field(None)
    effective_to: Optional[datetime] = Field(None)
    
    # Formula updates
    calculation_formula: Optional[str] = Field(None)
    in_network_formula: Optional[str] = Field(None)
    out_of_network_formula: Optional[str] = Field(None)
    formula_variables: Optional[Dict[str, Union[str, int, float]]] = Field(None)
    calculation_parameters: Optional[Dict[str, Any]] = Field(None)
    
    # Condition updates
    trigger_conditions: Optional[Dict[str, Any]] = Field(None)
    exclusion_conditions: Optional[Dict[str, Any]] = Field(None)
    lookup_table_data: Optional[Dict[str, Any]] = Field(None)
    
    # Validation updates
    validation_rules: Optional[Dict[str, Any]] = Field(None)
    error_handling: Optional[Dict[str, str]] = Field(None)
    
    # Documentation updates
    description: Optional[str] = Field(None)
    description_ar: Optional[str] = Field(None)
    technical_notes: Optional[str] = Field(None)
    business_rationale: Optional[str] = Field(None)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class BenefitCalculationRuleResponse(BenefitCalculationRuleBase):
    """Schema for benefit calculation rule responses"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Unique identifier for the calculation rule")
    
    # Related entity information
    benefit_type_id: Optional[UUID] = Field(None, description="Associated benefit type ID")
    coverage_id: Optional[UUID] = Field(None, description="Associated coverage ID")
    limit_id: Optional[UUID] = Field(None, description="Associated limit ID")
    benefit_type_name: Optional[str] = Field(None, description="Associated benefit type name")
    coverage_name: Optional[str] = Field(None, description="Associated coverage name")
    
    # Rule hierarchy
    parent_rule_id: Optional[UUID] = Field(None, description="Parent rule ID")
    depends_on_rules: Optional[List[UUID]] = Field(None, description="Dependencies")
    
    # Calculation logic
    calculation_formula: Optional[str] = Field(None, description="Primary calculation formula")
    in_network_formula: Optional[str] = Field(None, description="In-network formula")
    out_of_network_formula: Optional[str] = Field(None, description="Out-of-network formula")
    emergency_formula: Optional[str] = Field(None, description="Emergency services formula")
    
    # Variables and parameters
    formula_variables: Optional[Dict[str, Union[str, int, float]]] = Field(None, description="Formula variables")
    calculation_parameters: Optional[Dict[str, Any]] = Field(None, description="Calculation parameters")
    
    # Conditions
    trigger_conditions: Optional[Dict[str, Any]] = Field(None, description="Trigger conditions")
    exclusion_conditions: Optional[Dict[str, Any]] = Field(None, description="Exclusion conditions")
    
    # Lookup data
    lookup_table_data: Optional[Dict[str, Any]] = Field(None, description="Lookup table data")
    
    # Validation and error handling
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    error_handling: Optional[Dict[str, str]] = Field(None, description="Error handling configuration")
    
    # Performance metrics
    track_utilization: bool = Field(default=False, description="Utilization tracking enabled")
    performance_metrics: Optional[Dict[str, float]] = Field(None, description="Performance metrics")
    
    # Usage statistics
    execution_count: Optional[int] = Field(None, description="Number of times rule has been executed")
    success_rate: Optional[float] = Field(None, ge=0, le=100, description="Success rate percentage")
    average_execution_time: Optional[float] = Field(None, description="Average execution time in milliseconds")
    
    # Documentation
    description: Optional[str] = Field(None, description="Rule description")
    description_ar: Optional[str] = Field(None, description="Arabic description")
    technical_notes: Optional[str] = Field(None, description="Technical notes")
    business_rationale: Optional[str] = Field(None, description="Business rationale")
    
    # Examples and testing
    example_scenarios: Optional[Dict[str, Any]] = Field(None, description="Example scenarios")
    test_cases: Optional[List[Dict[str, Any]]] = Field(None, description="Test cases")
    
    # Status information
    status: Optional[RuleStatusEnum] = Field(None, description="Current rule status")
    status_reason: Optional[str] = Field(None, description="Reason for current status")
    
    # Audit fields
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="ID of user who created the rule")
    updated_by: Optional[UUID] = Field(None, description="ID of user who last updated the rule")
    version: int = Field(default=1, description="Version number")


class BenefitCalculationRuleSummary(BaseModel):
    """Lightweight summary schema for benefit calculation rules"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    rule_code: str
    rule_name: str
    rule_name_ar: Optional[str] = None
    rule_type: RuleTypeEnum
    calculation_method: CalculationMethodEnum
    rule_category: RuleCategoryEnum
    priority_order: int
    is_active: bool
    is_mandatory: bool
    deployment_stage: DeploymentStageEnum

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "rule_code": "CALC_DEDUCT_001",
                "rule_name": "Individual Deductible Calculation",
                "rule_type": "DEDUCTIBLE",
                "calculation_method": "PERCENTAGE",
                "rule_category": "FINANCIAL",
                "priority_order": 1,
                "is_active": True,
                "is_mandatory": True,
                "deployment_stage": "PRODUCTION"
            }
        }
    )


# =====================================================
# SPECIALIZED SCHEMAS
# =====================================================

class RuleEvaluationRequest(BaseModel):
    """Schema for rule evaluation requests"""
    
    rule_id: UUID = Field(..., description="Rule to evaluate")
    input_data: Dict[str, Any] = Field(..., description="Input data for evaluation")
    evaluation_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for evaluation"
    )
    debug_mode: bool = Field(default=False, description="Enable debug information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_id": "123e4567-e89b-12d3-a456-426614174000",
                "input_data": {
                    "service_cost": 500.00,
                    "member_age": 35,
                    "network_status": "in_network",
                    "deductible_met": 200.00
                },
                "evaluation_context": {
                    "plan_year": "2024",
                    "member_id": "member_123"
                },
                "debug_mode": True
            }
        }
    )


class RuleEvaluationResult(BaseModel):
    """Schema for rule evaluation results"""
    
    rule_id: UUID
    rule_code: str
    rule_name: str
    
    # Evaluation results
    applies: bool = Field(..., description="Whether rule applies to input")
    result: Optional[Decimal] = Field(None, description="Calculation result")
    result_details: Dict[str, Any] = Field(..., description="Detailed calculation breakdown")
    
    # Execution information
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    success: bool = Field(..., description="Whether evaluation was successful")
    error_message: Optional[str] = Field(None, description="Error message if evaluation failed")
    
    # Debug information (if requested)
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information")
    applied_conditions: List[str] = Field(default_factory=list, description="Conditions that were applied")
    
    evaluated_at: datetime = Field(default_factory=datetime.utcnow, description="Evaluation timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_id": "123e4567-e89b-12d3-a456-426614174000",
                "rule_code": "CALC_DEDUCT_001",
                "rule_name": "Individual Deductible Calculation",
                "applies": True,
                "result": "300.00",
                "result_details": {
                    "service_cost": "500.00",
                    "deductible_remaining": "300.00",
                    "member_pays": "300.00",
                    "insurance_pays": "200.00"
                },
                "execution_time_ms": 2.5,
                "success": True,
                "applied_conditions": ["deductible_applies", "in_network"]
            }
        }
    )


class BatchEvaluationRequest(BaseModel):
    """Schema for batch rule evaluation requests"""
    
    rule_ids: List[UUID] = Field(..., min_items=1, max_items=50, description="Rules to evaluate")
    input_data: Dict[str, Any] = Field(..., description="Common input data")
    individual_contexts: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Individual contexts per rule (rule_id as key)"
    )
    execution_order: Optional[List[UUID]] = Field(None, description="Specific execution order")
    stop_on_error: bool = Field(default=False, description="Stop batch on first error")


class BatchEvaluationResult(BaseModel):
    """Schema for batch rule evaluation results"""
    
    total_rules: int = Field(..., description="Total rules evaluated")
    successful_evaluations: int = Field(..., description="Successful evaluations")
    failed_evaluations: int = Field(..., description="Failed evaluations")
    
    # Individual results
    results: List[RuleEvaluationResult] = Field(..., description="Individual evaluation results")
    
    # Batch summary
    total_execution_time_ms: float = Field(..., description="Total execution time")
    batch_success: bool = Field(..., description="Whether entire batch was successful")
    
    # Aggregated results
    aggregated_result: Optional[Dict[str, Any]] = Field(None, description="Aggregated calculation results")
    
class RulePerformanceStats(BaseModel):
    """Schema for rule performance statistics"""
    
    rule_id: UUID
    rule_code: str
    rule_name: str
    
    # Execution statistics
    total_executions: int = Field(default=0, description="Total number of executions")
    successful_executions: int = Field(default=0, description="Successful executions")
    failed_executions: int = Field(default=0, description="Failed executions")
    success_rate: float = Field(default=0.0, ge=0, le=100, description="Success rate percentage")
    
    # Performance metrics
    average_execution_time_ms: float = Field(default=0.0, description="Average execution time")
    min_execution_time_ms: float = Field(default=0.0, description="Minimum execution time")
    max_execution_time_ms: float = Field(default=0.0, description="Maximum execution time")
    
    # Usage patterns
    most_common_inputs: Dict[str, int] = Field(default_factory=dict, description="Most common input patterns")
    error_patterns: Dict[str, int] = Field(default_factory=dict, description="Common error patterns")
    
    # Business impact
    total_amount_calculated: Decimal = Field(default=Decimal('0'), description="Total amount calculated by this rule")
    average_result_amount: Optional[Decimal] = Field(None, description="Average calculation result")
    
    # Time period
    reporting_period_start: datetime = Field(..., description="Reporting period start")
    reporting_period_end: datetime = Field(..., description="Reporting period end")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Statistics last updated")


# =====================================================
# LIST AND FILTER SCHEMAS
# =====================================================

class BenefitCalculationRuleFilter(BaseModel):
    """Schema for filtering benefit calculation rules"""
    
    rule_type: Optional[RuleTypeEnum] = Field(None, description="Filter by rule type")
    calculation_method: Optional[CalculationMethodEnum] = Field(None, description="Filter by calculation method")
    rule_category: Optional[RuleCategoryEnum] = Field(None, description="Filter by rule category")
    deployment_stage: Optional[DeploymentStageEnum] = Field(None, description="Filter by deployment stage")
    
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_mandatory: Optional[bool] = Field(None, description="Filter by mandatory status")
    is_system_rule: Optional[bool] = Field(None, description="Filter by system rule status")
    is_test_rule: Optional[bool] = Field(None, description="Filter by test rule status")
    
    # Related entity filters
    benefit_type_id: Optional[UUID] = Field(None, description="Filter by benefit type")
    coverage_id: Optional[UUID] = Field(None, description="Filter by coverage")
    limit_id: Optional[UUID] = Field(None, description="Filter by limit")
    
    # Priority filters
    priority_order_min: Optional[int] = Field(None, ge=1, description="Minimum priority order")
    priority_order_max: Optional[int] = Field(None, ge=1, description="Maximum priority order")
    
    # Authorization filters
    requires_authorization: Optional[bool] = Field(None, description="Filter by authorization requirement")
    authorization_level: Optional[str] = Field(None, description="Filter by authorization level")
    
    # Effective date filters
    effective_date_from: Optional[datetime] = Field(None, description="Effective from date")
    effective_date_to: Optional[datetime] = Field(None, description="Effective to date")
    
    # Search fields
    search_term: Optional[str] = Field(None, max_length=100, description="Search in names and descriptions")
    rule_codes: Optional[List[str]] = Field(None, description="Filter by specific rule codes")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_type": "DEDUCTIBLE",
                "calculation_method": "PERCENTAGE",
                "rule_category": "FINANCIAL",
                "is_active": True,
                "is_mandatory": True,
                "deployment_stage": "PRODUCTION",
                "search_term": "deductible"
            }
        }
    )


class BenefitCalculationRuleListResponse(BaseModel):
    """Schema for paginated list of benefit calculation rules"""
    
    items: List[BenefitCalculationRuleResponse] = Field(..., description="List of calculation rules")
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

class BenefitCalculationRuleBulkCreate(BaseModel):
    """Schema for bulk creating benefit calculation rules"""
    
    rules: List[BenefitCalculationRuleCreate] = Field(
        ..., 
        min_items=1, 
        max_items=50,
        description="List of calculation rules to create"
    )
    
    # Bulk operation settings
    skip_duplicates: bool = Field(default=False, description="Skip rules with duplicate codes")
    validate_formulas: bool = Field(default=True, description="Validate calculation formulas")
    auto_assign_priority: bool = Field(default=False, description="Auto-assign priority order")

    class Config:
        json_schema_extra = {
            "example": {
                "rules": [
                    {
                        "rule_code": "CALC_DEDUCT_001",
                        "rule_name": "Individual Deductible",
                        "rule_type": "DEDUCTIBLE",
                        "calculation_method": "PERCENTAGE",
                        "percentage_rate": "100.0000"
                    }
                ],
                "skip_duplicates": True,
                "validate_formulas": True
            }
        }


class BenefitCalculationRuleBulkUpdate(BaseModel):
    """Schema for bulk updating benefit calculation rules"""
    
    rule_ids: List[UUID] = Field(..., min_items=1, max_items=100)
    updates: BenefitCalculationRuleUpdate = Field(..., description="Fields to update")
    
    # Update options
    preserve_custom_formulas: bool = Field(default=True, description="Preserve custom formulas")
    recalculate_dependencies: bool = Field(default=False, description="Recalculate rule dependencies")


class BenefitCalculationRuleBulkResponse(BaseModel):
    """Schema for bulk operation responses"""
    
    successful_operations: int = Field(..., ge=0, description="Number of successful operations")
    failed_operations: int = Field(..., ge=0, description="Number of failed operations")
    total_operations: int = Field(..., ge=0, description="Total number of operations attempted")
    
    success_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of successful operations")
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of failed operations")
    
    # Additional results
    dependencies_updated: Optional[int] = Field(None, description="Number of dependencies updated")
    formulas_validated: Optional[int] = Field(None, description="Number of formulas validated")


# =====================================================
# ADDITIONAL SPECIALIZED SCHEMAS
# =====================================================

class FormulaValidation(BaseModel):
    """Schema for formula validation results"""
    
    formula: str = Field(..., description="The formula that was validated")
    is_valid: bool = Field(..., description="Whether the formula is valid")
    syntax_errors: List[str] = Field(default_factory=list, description="Syntax error messages")
    security_warnings: List[str] = Field(default_factory=list, description="Security warnings")
    complexity_score: int = Field(default=0, ge=0, description="Complexity score (0-100)")
    estimated_performance: str = Field(default="UNKNOWN", description="Estimated performance rating")
    variables_identified: List[str] = Field(default_factory=list, description="Variables found in formula")
    functions_used: List[str] = Field(default_factory=list, description="Functions used in formula")
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow)


class CalculationExecution(BaseModel):
    """Schema for calculation execution results"""
    
    rule_id: UUID = Field(..., description="ID of the executed rule")
    rule_code: str = Field(..., description="Code of the executed rule")
    execution_id: str = Field(..., description="Unique execution identifier")
    
    # Input data
    input_context: Dict[str, Any] = Field(..., description="Input data used for calculation")
    
    # Results
    result: Optional[Decimal] = Field(None, description="Calculation result")
    intermediate_steps: List[Dict[str, Any]] = Field(default_factory=list, description="Step-by-step calculation")
    
    # Execution metadata
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    success: bool = Field(..., description="Whether execution was successful")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error details if failed")
    
    # Tracing (if enabled)
    execution_trace: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed execution trace")
    
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class RuleTestCase(BaseModel):
    """Schema for individual rule test case"""
    
    test_id: str = Field(..., description="Test case identifier")
    test_name: str = Field(..., description="Test case name")
    input_data: Dict[str, Any] = Field(..., description="Test input data")
    expected_result: Optional[Decimal] = Field(None, description="Expected calculation result")
    expected_applies: bool = Field(default=True, description="Whether rule should apply")
    
    # Test execution results
    actual_result: Optional[Decimal] = Field(None, description="Actual calculation result")
    actual_applies: Optional[bool] = Field(None, description="Whether rule actually applied")
    test_passed: Optional[bool] = Field(None, description="Whether test passed")
    error_message: Optional[str] = Field(None, description="Error message if test failed")
    execution_time_ms: Optional[float] = Field(None, description="Test execution time")
    
    test_executed_at: Optional[datetime] = Field(None, description="When test was executed")


class RulePerformanceMetrics(BaseModel):
    """Schema for rule performance metrics"""
    
    rule_id: UUID
    rule_code: str
    
    # Performance data
    avg_execution_time_ms: float = Field(default=0.0, description="Average execution time")
    p95_execution_time_ms: float = Field(default=0.0, description="95th percentile execution time")
    p99_execution_time_ms: float = Field(default=0.0, description="99th percentile execution time")
    
    # Usage statistics
    total_executions: int = Field(default=0, description="Total number of executions")
    executions_per_day: float = Field(default=0.0, description="Average executions per day")
    peak_executions_per_hour: int = Field(default=0, description="Peak executions per hour")
    
    # Success rates
    success_rate_percentage: float = Field(default=0.0, ge=0, le=100, description="Success rate percentage")
    error_rate_percentage: float = Field(default=0.0, ge=0, le=100, description="Error rate percentage")
    
    # Resource usage
    cpu_usage_ms: float = Field(default=0.0, description="CPU time usage in milliseconds")
    memory_usage_kb: float = Field(default=0.0, description="Memory usage in kilobytes")
    
    # Business impact
    total_amount_processed: Decimal = Field(default=Decimal('0'), description="Total amount processed")
    cost_savings_generated: Decimal = Field(default=Decimal('0'), description="Cost savings generated")
    
    metrics_period_start: datetime = Field(..., description="Metrics period start")
    metrics_period_end: datetime = Field(..., description="Metrics period end")


# Make commonly used schemas easily accessible
__all__ = [
    'BenefitCalculationRuleCreate',
    'BenefitCalculationRuleUpdate', 
    'BenefitCalculationRuleResponse',
    'BenefitCalculationRuleSummary',
    'RuleEvaluationRequest',
    'RuleEvaluationResult',
    'BatchEvaluationRequest',
    'BatchEvaluationResult',
    'FormulaValidation',
    'CalculationExecution',
    'RuleTestCase',
    'RulePerformanceStats',
    'BenefitCalculationRuleFilter',
    'BenefitCalculationRuleListResponse',
    'BenefitCalculationRuleBulkCreate',
    'BenefitCalculationRuleBulkUpdate',
    'BenefitCalculationRuleBulkResponse'
]


# =====================================================
# MISSING SCHEMAS FOR ADVANCED FUNCTIONALITY
# =====================================================

class BenefitCalculationRuleWithDetails(BenefitCalculationRuleResponse):
    """Extended schema with detailed rule information"""
    
    # Dependencies and relationships
    dependency_graph: Optional[Dict[str, Any]] = Field(None, description="Rule dependency graph")
    dependent_rules: List[UUID] = Field(default_factory=list, description="Rules that depend on this one")
    child_rules: List[UUID] = Field(default_factory=list, description="Child rules")
    
    # Performance data
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    usage_statistics: Optional[Dict[str, Any]] = Field(None, description="Usage statistics")
    
    # Formula analysis
    formula_complexity: Optional[str] = Field(None, description="Formula complexity rating")
    formula_variables_used: List[str] = Field(default_factory=list, description="Variables used in formula")
    formula_functions_used: List[str] = Field(default_factory=list, description="Functions used in formula")
    
    # Validation history
    last_validation_date: Optional[datetime] = Field(None, description="Last validation date")
    validation_status: Optional[str] = Field(None, description="Current validation status")
    
    model_config = ConfigDict(from_attributes=True)


class RulePerformanceMetrics(BaseModel):
    """Schema for detailed rule performance metrics"""
    
    rule_id: UUID
    rule_code: str
    rule_name: str
    
    # Execution performance
    avg_execution_time_ms: float = Field(default=0.0, description="Average execution time")
    p50_execution_time_ms: float = Field(default=0.0, description="50th percentile execution time")
    p95_execution_time_ms: float = Field(default=0.0, description="95th percentile execution time")
    p99_execution_time_ms: float = Field(default=0.0, description="99th percentile execution time")
    max_execution_time_ms: float = Field(default=0.0, description="Maximum execution time")
    
    # Usage statistics
    total_executions: int = Field(default=0, description="Total executions")
    executions_per_hour: float = Field(default=0.0, description="Average executions per hour")
    executions_per_day: float = Field(default=0.0, description="Average executions per day")
    peak_executions_per_hour: int = Field(default=0, description="Peak executions per hour")
    
    # Success rates
    success_rate: float = Field(default=100.0, ge=0, le=100, description="Success rate percentage")
    error_rate: float = Field(default=0.0, ge=0, le=100, description="Error rate percentage")
    timeout_rate: float = Field(default=0.0, ge=0, le=100, description="Timeout rate percentage")
    
    # Resource usage
    avg_cpu_usage_ms: float = Field(default=0.0, description="Average CPU usage")
    avg_memory_usage_kb: float = Field(default=0.0, description="Average memory usage")
    peak_memory_usage_kb: float = Field(default=0.0, description="Peak memory usage")
    
    # Business impact
    total_amount_processed: Decimal = Field(default=Decimal('0'), description="Total amount processed")
    avg_amount_per_execution: Decimal = Field(default=Decimal('0'), description="Average amount per execution")
    total_savings_generated: Decimal = Field(default=Decimal('0'), description="Total savings generated")
    
    # Trends
    performance_trend: str = Field(default="stable", description="Performance trend (improving/stable/degrading)")
    usage_trend: str = Field(default="stable", description="Usage trend")
    
    # Time period
    metrics_start_date: datetime = Field(..., description="Metrics collection start date")
    metrics_end_date: datetime = Field(..., description="Metrics collection end date")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last metrics update")


class RuleDependencyGraph(BaseModel):
    """Schema for rule dependency graphs"""
    
    root_rule_id: UUID = Field(..., description="Root rule ID")
    root_rule_code: str = Field(..., description="Root rule code")
    root_rule_name: str = Field(..., description="Root rule name")
    
    # Dependency information
    dependencies: List[Dict[str, Any]] = Field(default_factory=list, description="Direct dependencies")
    dependents: List[Dict[str, Any]] = Field(default_factory=list, description="Rules that depend on this one")
    
    # Graph structure
    dependency_tree: Dict[str, Any] = Field(default_factory=dict, description="Complete dependency tree")
    circular_dependencies: List[Dict[str, Any]] = Field(default_factory=list, description="Circular dependencies found")
    orphaned_rules: List[UUID] = Field(default_factory=list, description="Rules with missing dependencies")
    
    # Metrics
    max_depth: int = Field(default=0, description="Maximum dependency depth")
    total_dependencies: int = Field(default=0, description="Total number of dependencies")
    total_dependents: int = Field(default=0, description="Total number of dependents")
    
    # Analysis results
    has_circular_dependencies: bool = Field(default=False, description="Whether circular dependencies exist")
    has_missing_dependencies: bool = Field(default=False, description="Whether missing dependencies exist")
    dependency_health_score: float = Field(default=100.0, ge=0, le=100, description="Dependency health score")
    
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Graph generation timestamp")


class FormulaOptimization(BaseModel):
    """Schema for formula optimization results"""
    
    rule_id: UUID = Field(..., description="Rule ID that was optimized")
    original_formula: str = Field(..., description="Original formula")
    optimized_formula: str = Field(..., description="Optimized formula")
    
    # Optimization results
    optimization_applied: bool = Field(..., description="Whether optimization was applied")
    optimization_type: str = Field(..., description="Type of optimization performed")
    optimization_goals: List[str] = Field(..., description="Optimization goals achieved")
    
    # Performance improvements
    performance_improvement: float = Field(default=0.0, description="Performance improvement percentage")
    execution_time_reduction: float = Field(default=0.0, description="Execution time reduction in ms")
    complexity_reduction: float = Field(default=0.0, description="Formula complexity reduction")
    memory_usage_reduction: float = Field(default=0.0, description="Memory usage reduction")
    
    # Validation results
    semantics_preserved: bool = Field(..., description="Whether original semantics were preserved")
    test_results_identical: bool = Field(..., description="Whether test results are identical")
    validation_passed: bool = Field(..., description="Whether validation passed")
    
    # Optimization details
    optimizations_performed: List[Dict[str, Any]] = Field(default_factory=list, description="Specific optimizations")
    warnings: List[str] = Field(default_factory=list, description="Optimization warnings")
    recommendations: List[str] = Field(default_factory=list, description="Additional recommendations")
    
    optimized_at: datetime = Field(default_factory=datetime.utcnow, description="Optimization timestamp")


class RuleVersion(BaseModel):
    """Schema for rule versions"""
    
    version_id: UUID = Field(..., description="Version ID")
    rule_id: UUID = Field(..., description="Parent rule ID")
    version_number: int = Field(..., description="Version number")
    version_name: Optional[str] = Field(None, description="Version name")
    
    # Version data
    rule_data: Dict[str, Any] = Field(..., description="Rule data for this version")
    change_summary: str = Field(..., description="Summary of changes")
    change_details: Optional[Dict[str, Any]] = Field(None, description="Detailed change information")
    
    # Version status
    is_active: bool = Field(default=False, description="Whether this version is active")
    is_archived: bool = Field(default=False, description="Whether this version is archived")
    
    # Metadata
    created_by: Optional[UUID] = Field(None, description="User who created this version")
    created_at: datetime = Field(..., description="Version creation timestamp")
    activated_at: Optional[datetime] = Field(None, description="When this version was activated")
    activated_by: Optional[UUID] = Field(None, description="User who activated this version")
    
    # Comparison with previous version
    previous_version_id: Optional[UUID] = Field(None, description="Previous version ID")
    changes_from_previous: Optional[Dict[str, Any]] = Field(None, description="Changes from previous version")


class CalculationContext(BaseModel):
    """Schema for calculation execution context"""
    
    # Core calculation inputs
    benefit_type_id: str = Field(..., description="Benefit type ID")
    service_amount: Decimal = Field(..., ge=0, description="Service amount")
    
    # Member context
    member_context: Dict[str, Any] = Field(..., description="Member-specific context")
    
    # Claim context (optional)
    claim_context: Optional[Dict[str, Any]] = Field(None, description="Claim-specific context")
    
    # Execution options
    include_intermediate_steps: bool = Field(default=False, description="Include intermediate calculation steps")
    validate_inputs: bool = Field(default=True, description="Validate input data")
    trace_execution: bool = Field(default=False, description="Enable execution tracing")
    
    # Override options
    rule_overrides: Optional[Dict[str, Any]] = Field(None, description="Rule-specific overrides")
    context_overrides: Optional[Dict[str, Any]] = Field(None, description="Context overrides")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "benefit_type_id": "medical_outpatient",
                "service_amount": "500.00",
                "member_context": {
                    "member_id": "M123456",
                    "age": 35,
                    "deductible_met": "200.00",
                    "oop_spent": "150.00",
                    "plan_year": "2024"
                },
                "claim_context": {
                    "claim_id": "CLM789",
                    "provider_network": "in_network",
                    "service_date": "2024-09-15"
                },
                "include_intermediate_steps": True,
                "validate_inputs": True
            }
        }
    )


class RuleSearchFilter(BaseModel):
    """Advanced search filters for rules"""
    
    # Text search
    search: Optional[str] = Field(None, description="Text search across name, code, description")
    
    # Basic filters
    rule_type: Optional[RuleTypeEnum] = Field(None, description="Filter by rule type")
    calculation_method: Optional[CalculationMethodEnum] = Field(None, description="Filter by calculation method")
    rule_category: Optional[RuleCategoryEnum] = Field(None, description="Filter by rule category")
    deployment_stage: Optional[DeploymentStageEnum] = Field(None, description="Filter by deployment stage")
    
    # Status filters
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_mandatory: Optional[bool] = Field(None, description="Filter by mandatory status")
    is_system_rule: Optional[bool] = Field(None, description="Filter by system rule status")
    is_test_rule: Optional[bool] = Field(None, description="Filter by test rule status")
    
    # Relationship filters
    benefit_type_id: Optional[str] = Field(None, description="Filter by benefit type")
    coverage_id: Optional[str] = Field(None, description="Filter by coverage")
    has_dependencies: Optional[bool] = Field(None, description="Filter by dependency existence")
    has_formula: Optional[bool] = Field(None, description="Filter by formula existence")
    
    # Performance filters
    performance_threshold: Optional[float] = Field(None, description="Filter by performance threshold")
    complexity: Optional[str] = Field(None, description="Filter by complexity level")
    
    # Date filters
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    modified_after: Optional[datetime] = Field(None, description="Modified after date")
    modified_before: Optional[datetime] = Field(None, description="Modified before date")
    
    # Priority filters
    min_priority: Optional[int] = Field(None, ge=1, description="Minimum priority")
    max_priority: Optional[int] = Field(None, ge=1, description="Maximum priority")


class BulkRuleOperation(BaseModel):
    """Schema for bulk rule operations"""
    
    operation_type: str = Field(..., description="Type of bulk operation")
    rule_ids: List[UUID] = Field(..., min_items=1, max_items=1000, description="Rule IDs to operate on")
    
    # Operation parameters
    operation_parameters: Optional[Dict[str, Any]] = Field(None, description="Operation-specific parameters")
    
    # Execution options
    execute_async: bool = Field(default=True, description="Execute operation asynchronously")
    batch_size: int = Field(default=50, ge=1, le=100, description="Batch size for processing")
    fail_fast: bool = Field(default=False, description="Stop on first failure")
    
    # Validation options
    validate_before_execute: bool = Field(default=True, description="Validate before execution")
    dry_run: bool = Field(default=False, description="Perform dry run without actual changes")
    
    # Notification options
    notify_on_completion: bool = Field(default=False, description="Send notification on completion")
    notification_recipients: Optional[List[str]] = Field(None, description="Notification recipients")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "operation_type": "bulk_activate",
                "rule_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "234e5678-e89b-12d3-a456-426614174001"
                ],
                "operation_parameters": {
                    "effective_date": "2024-10-01",
                    "reason": "Monthly activation cycle"
                },
                "execute_async": True,
                "batch_size": 25,
                "validate_before_execute": True,
                "dry_run": False
            }
        }
    )