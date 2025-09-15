# app/modules/pricing/profiles/schemas/quotation_pricing_rule_schema.py

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from enum import Enum

# Import insurance type from profile schema to avoid duplication
from .quotation_pricing_profile_schema import InsuranceType

# Enums for rule validation
class RuleType(str, Enum):
    """Types of pricing rules available"""
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    MULTIPLIER = "MULTIPLIER"
    FORMULA = "FORMULA"
    AGE_BASED = "AGE_BASED"
    INDUSTRY_BASED = "INDUSTRY_BASED"
    RISK_BASED = "RISK_BASED"
    DISCOUNT = "DISCOUNT"
    LOADING = "LOADING"
    COMMISSION = "COMMISSION"

class ComparisonOperator(str, Enum):
    """Comparison operators for rule conditions"""
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    IN = "IN"
    NOT_IN = "NOT IN"
    BETWEEN = "BETWEEN"

class AdjustmentType(str, Enum):
    """Types of premium adjustments"""
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    MULTIPLIER = "MULTIPLIER"
    FORMULA = "FORMULA"

# Base schema for pricing rules
class QuotationPricingRuleBase(BaseModel):
    """Base schema for quotation pricing rules"""
    
    insurance_type: InsuranceType = Field(..., description="Type of insurance this rule applies to")
    rule_name: str = Field(..., min_length=1, max_length=255, description="Name of the pricing rule")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the rule")
    base_premium: Optional[Decimal] = Field(None, ge=0, description="Base premium amount")
    min_premium: Optional[Decimal] = Field(None, ge=0, description="Minimum premium amount")
    max_premium: Optional[Decimal] = Field(None, ge=0, description="Maximum premium amount")
    currency_code: str = Field(default="SAR", min_length=3, max_length=3, description="Currency code")
    applies_to: Optional[str] = Field(None, max_length=50, description="What the rule applies to")
    comparison_operator: Optional[ComparisonOperator] = Field(None, description="Comparison operator")
    value: Optional[str] = Field(None, description="Value to compare against")
    adjustment_type: Optional[AdjustmentType] = Field(None, description="Type of adjustment")
    adjustment_value: Optional[Decimal] = Field(None, description="Adjustment value")
    formula_expression: Optional[str] = Field(None, description="Formula expression")
    formula_variables: Optional[Dict[str, Any]] = Field(None, description="Formula variables")
    is_active: bool = Field(default=True, description="Whether the rule is active")
    effective_from: datetime = Field(default_factory=datetime.utcnow, description="When the rule becomes effective")
    effective_to: Optional[datetime] = Field(None, description="When the rule expires")
    priority: int = Field(default=0, description="Rule priority (higher = more important)")
    version: int = Field(default=1, description="Rule version")
    rule_type: Optional[RuleType] = Field(None, description="Type of rule")
    copayment_id: Optional[UUID] = Field(None, description="Related copayment ID")
    deductible_id: Optional[UUID] = Field(None, description="Related deductible ID")
    discount_id: Optional[UUID] = Field(None, description="Related discount ID")
    commission_id: Optional[UUID] = Field(None, description="Related commission ID")

    @field_validator('effective_to')
    @classmethod
    def validate_effective_dates(cls, v, info):
        """Ensure effective_to is after effective_from"""
        effective_from = info.data.get('effective_from')
        if v and effective_from and v <= effective_from:
            raise ValueError('effective_to must be after effective_from')
        return v

# Create schema
class QuotationPricingRuleCreate(QuotationPricingRuleBase):
    """Schema for creating a new pricing rule"""
    
    created_by: Optional[str] = Field(None, max_length=100, description="Created by user")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "insurance_type": "Motor",
                "rule_name": "Age Loading Rule",
                "description": "Applies loading based on driver age",
                "rule_type": "AGE_BASED",
                "adjustment_type": "PERCENTAGE",
                "adjustment_value": 15.0,
                "priority": 10,
                "currency_code": "SAR"
            }
        }
    )

# Update schema
class QuotationPricingRuleUpdate(BaseModel):
    """Schema for updating an existing pricing rule"""
    
    insurance_type: Optional[InsuranceType] = None
    rule_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    base_premium: Optional[Decimal] = Field(None, ge=0)
    min_premium: Optional[Decimal] = Field(None, ge=0)
    max_premium: Optional[Decimal] = Field(None, ge=0)
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3)
    applies_to: Optional[str] = Field(None, max_length=50)
    comparison_operator: Optional[ComparisonOperator] = None
    value: Optional[str] = None
    adjustment_type: Optional[AdjustmentType] = None
    adjustment_value: Optional[Decimal] = None
    formula_expression: Optional[str] = None
    formula_variables: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    priority: Optional[int] = None
    version: Optional[int] = None
    rule_type: Optional[RuleType] = None
    copayment_id: Optional[UUID] = None
    deductible_id: Optional[UUID] = None
    discount_id: Optional[UUID] = None
    commission_id: Optional[UUID] = None
    updated_by: Optional[str] = Field(None, max_length=100)

# Response schema
class QuotationPricingRuleResponse(QuotationPricingRuleBase):
    """Schema for pricing rule responses"""
    
    id: UUID = Field(..., description="Rule unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    archived_at: Optional[datetime] = Field(None, description="Archive timestamp")
    created_by: Optional[str] = Field(None, description="Creator user")
    updated_by: Optional[str] = Field(None, description="Last updater user")

    model_config = ConfigDict(from_attributes=True)

# Rule evaluation schemas
class QuotationPricingRuleEvaluation(BaseModel):
    """Schema for evaluating a pricing rule"""
    
    rule_id: UUID = Field(..., description="Rule to evaluate")
    input_data: Dict[str, Any] = Field(..., description="Input data for evaluation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_id": "123e4567-e89b-12d3-a456-426614174000",
                "input_data": {
                    "age": 25,
                    "vehicle_value": 50000,
                    "location": "Riyadh"
                }
            }
        }
    )

class QuotationPricingRuleEvaluationResult(BaseModel):
    """Schema for rule evaluation results"""
    
    rule_id: UUID = Field(..., description="Evaluated rule ID")
    rule_name: str = Field(..., description="Rule name")
    applied: bool = Field(..., description="Whether rule was applied")
    original_value: Decimal = Field(..., description="Original value")
    adjusted_value: Decimal = Field(..., description="Value after rule application")
    adjustment_amount: Decimal = Field(..., description="Amount of adjustment")
    adjustment_percentage: Optional[Decimal] = Field(None, description="Percentage adjustment")
    reason: str = Field(..., description="Reason for application/non-application")

class RuleEvaluationRequest(BaseModel):
    """Schema for requesting rule evaluation"""
    
    rule_id: UUID = Field(..., description="Rule ID to evaluate")
    input_data: Dict[str, Any] = Field(..., description="Input data for evaluation")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for evaluation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_id": "123e4567-e89b-12d3-a456-426614174000",
                "input_data": {
                    "age": 25,
                    "vehicle_value": 50000,
                    "location": "Riyadh"
                },
                "context": {
                    "profile_id": "987fcdeb-51a2-43d1-9f12-345678901234"
                }
            }
        }
    )

class RuleEvaluationResult(BaseModel):
    """Schema for rule evaluation results"""
    
    rule_id: UUID = Field(..., description="Evaluated rule ID")
    rule_name: str = Field(..., description="Rule name")
    condition_met: bool = Field(..., description="Whether rule condition was met")
    impact_applied: bool = Field(..., description="Whether rule impact was applied")
    result_value: Optional[Decimal] = Field(None, description="Calculated result value")
    evaluation_details: Dict[str, Any] = Field(..., description="Detailed evaluation information")
    evaluation_timestamp: Optional[datetime] = Field(None, description="When evaluation was performed")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_id": "123e4567-e89b-12d3-a456-426614174000",
                "rule_name": "Age Factor Rule",
                "condition_met": True,
                "impact_applied": True,
                "result_value": 150.0,
                "evaluation_details": {
                    "field_name": "age",
                    "field_value": 25,
                    "operator": "<=",
                    "condition_value": 30,
                    "impact_type": "percentage",
                    "impact_value": 15.0
                },
                "evaluation_timestamp": "2024-09-15T10:30:00Z"
            }
        }
    )

# Batch evaluation schemas
class BatchEvaluationProfileRequest(BaseModel):
    """Schema for a single profile evaluation in a batch"""
    
    profile_id: UUID = Field(..., description="Profile ID to evaluate")
    input_data: Dict[str, Any] = Field(..., description="Input data for this profile")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class BatchEvaluationRequest(BaseModel):
    """Schema for batch evaluation request"""
    
    batch_id: Optional[str] = Field(None, description="Optional batch identifier")
    profile_evaluations: List[BatchEvaluationProfileRequest] = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="List of profile evaluations to perform"
    )
    evaluation_strategy: Optional[str] = Field("sequential", description="Evaluation strategy")
    use_cache: Optional[bool] = Field(True, description="Whether to use caching")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "batch_id": "batch_2024_09_15_001",
                "profile_evaluations": [
                    {
                        "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                        "input_data": {
                            "age": 25,
                            "vehicle_value": 50000
                        }
                    },
                    {
                        "profile_id": "987fcdeb-51a2-43d1-9f12-345678901234",
                        "input_data": {
                            "age": 35,
                            "vehicle_value": 75000
                        }
                    }
                ],
                "evaluation_strategy": "parallel",
                "use_cache": True
            }
        }
    )

class BatchEvaluationProfileResult(BaseModel):
    """Schema for a single profile result in batch evaluation"""
    
    profile_id: UUID = Field(..., description="Profile ID")
    success: bool = Field(..., description="Whether evaluation was successful")
    result: Optional[Dict[str, Any]] = Field(None, description="Evaluation result if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class BatchEvaluationResult(BaseModel):
    """Schema for batch evaluation results"""
    
    batch_id: Optional[str] = Field(None, description="Batch identifier")
    total_profiles: int = Field(..., description="Total number of profiles evaluated")
    successful_evaluations: int = Field(..., description="Number of successful evaluations")
    failed_evaluations: int = Field(..., description="Number of failed evaluations")
    total_processing_time: float = Field(..., description="Total processing time in seconds")
    total_elapsed_time: float = Field(..., description="Total elapsed time in seconds")
    average_processing_time: float = Field(..., description="Average processing time per profile")
    results: List[BatchEvaluationProfileResult] = Field(..., description="Individual profile results")
    batch_timestamp: datetime = Field(..., description="Batch completion timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "batch_id": "batch_2024_09_15_001",
                "total_profiles": 2,
                "successful_evaluations": 2,
                "failed_evaluations": 0,
                "total_processing_time": 0.245,
                "total_elapsed_time": 0.312,
                "average_processing_time": 0.1225,
                "results": [
                    {
                        "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                        "success": True,
                        "result": {"total_impact": 150.0, "rules_applied": 3},
                        "processing_time": 0.120
                    }
                ],
                "batch_timestamp": "2024-09-15T10:35:00Z"
            }
        }
    )

# Bulk operations
class QuotationPricingRuleBulkCreate(BaseModel):
    """Schema for creating multiple pricing rules"""
    
    rules: List[QuotationPricingRuleCreate] = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="List of rules to create"
    )

# Priority update schema
class QuotationPricingRulePriorityUpdate(BaseModel):
    """Schema for updating rule priorities"""
    
    rule_priorities: List[Dict[str, Union[UUID, int]]] = Field(
        ...,
        description="List of rule IDs and their new priorities"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_priorities": [
                    {"rule_id": "123e4567-e89b-12d3-a456-426614174000", "priority": 10},
                    {"rule_id": "987fcdeb-51a2-43d1-9f12-345678901234", "priority": 5}
                ]
            }
        }
    )

# Profile-Rule relationship schemas
class QuotationPricingProfileRuleBase(BaseModel):
    """Base schema for profile-rule relationships"""
    
    profile_id: UUID = Field(..., description="Pricing profile ID")
    rule_id: UUID = Field(..., description="Pricing rule ID")
    order_index: int = Field(default=0, description="Order of rule execution")
    is_active: bool = Field(default=True, description="Whether relationship is active")

class QuotationPricingProfileRuleCreate(QuotationPricingProfileRuleBase):
    """Schema for creating profile-rule relationships"""
    
    created_by: Optional[UUID] = Field(None, description="Created by user ID")

class QuotationPricingProfileRuleResponse(QuotationPricingProfileRuleBase):
    """Schema for profile-rule relationship responses"""
    
    id: UUID = Field(..., description="Relationship unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    archived_at: Optional[datetime] = Field(None, description="Archive timestamp")
    created_by: Optional[UUID] = Field(None, description="Creator user ID")
    updated_by: Optional[UUID] = Field(None, description="Last updater user ID")

    model_config = ConfigDict(from_attributes=True)

# Age bracket schemas
class QuotationPricingRuleAgeBracketBase(BaseModel):
    """Base schema for rule age brackets"""
    
    rule_id: UUID = Field(..., description="Related pricing rule ID")
    age_bracket_id: UUID = Field(..., description="Related age bracket ID")
    multiplier: Decimal = Field(default=Decimal("1.0"), ge=0, description="Age bracket multiplier")

class QuotationPricingRuleAgeBracketCreate(QuotationPricingRuleAgeBracketBase):
    """Schema for creating rule age brackets"""
    
    created_by: Optional[UUID] = Field(None, description="Created by user ID")

class QuotationPricingRuleAgeBracketResponse(QuotationPricingRuleAgeBracketBase):
    """Schema for rule age bracket responses"""
    
    id: UUID = Field(..., description="Age bracket rule unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    archived_at: Optional[datetime] = Field(None, description="Archive timestamp")
    created_by: Optional[UUID] = Field(None, description="Creator user ID")
    updated_by: Optional[UUID] = Field(None, description="Last updater user ID")

    model_config = ConfigDict(from_attributes=True)

# Convenience aliases for backward compatibility
PricingRuleBase = QuotationPricingRuleBase
PricingRuleCreate = QuotationPricingRuleCreate
PricingRuleUpdate = QuotationPricingRuleUpdate
PricingRuleResponse = QuotationPricingRuleResponse
PricingRuleEvaluation = QuotationPricingRuleEvaluation
PricingRuleEvaluationResult = QuotationPricingRuleEvaluationResult
PricingRuleBulkCreate = QuotationPricingRuleBulkCreate
PricingRulePriorityUpdate = QuotationPricingRulePriorityUpdate
RuleEvaluationRequest = RuleEvaluationRequest
RuleEvaluationResult = RuleEvaluationResult
BatchEvaluationRequest = BatchEvaluationRequest
BatchEvaluationResult = BatchEvaluationResult