# app/modules/pricing/profiles/schemas/pricing_rule_schema.py

"""
Simplified pricing rule schemas that import from quotation_pricing_rule_schema
and provide convenient aliases for services that expect this naming convention.
"""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

# Import all the classes from the main schema file
from .quotation_pricing_rule_schema import (
    # Enums
    RuleType,
    ComparisonOperator,
    AdjustmentType,
    
    # Base rule schemas
    QuotationPricingRuleBase as PricingRuleBase,
    QuotationPricingRuleCreate as PricingRuleCreate,
    QuotationPricingRuleUpdate as PricingRuleUpdate,
    QuotationPricingRuleResponse as PricingRuleResponse,
    QuotationPricingRuleEvaluation as PricingRuleEvaluation,
    QuotationPricingRuleEvaluationResult as PricingRuleEvaluationResult,
    QuotationPricingRuleBulkCreate as PricingRuleBulkCreate,
    QuotationPricingRulePriorityUpdate as PricingRulePriorityUpdate,
    
    # Profile-rule relationship schemas
    QuotationPricingProfileRuleBase,
    QuotationPricingProfileRuleCreate,
    QuotationPricingProfileRuleResponse,
    
    # Age bracket schemas
    QuotationPricingRuleAgeBracketBase,
    QuotationPricingRuleAgeBracketCreate,
    QuotationPricingRuleAgeBracketResponse,
)

# Define the evaluation schemas that are missing
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

# Export all classes for easy import
__all__ = [
    # Enums
    "RuleType",
    "ComparisonOperator", 
    "AdjustmentType",
    
    # Core rule schemas
    "PricingRuleBase",
    "PricingRuleCreate",
    "PricingRuleUpdate", 
    "PricingRuleResponse",
    "PricingRuleEvaluation",
    "PricingRuleEvaluationResult",
    "PricingRuleBulkCreate",
    "PricingRulePriorityUpdate",
    
    # Evaluation schemas
    "RuleEvaluationRequest",
    "RuleEvaluationResult",
    "BatchEvaluationRequest",
    "BatchEvaluationResult",
    "BatchEvaluationProfileRequest",
    "BatchEvaluationProfileResult",
    
    # Profile-rule relationship schemas
    "QuotationPricingProfileRuleBase",
    "QuotationPricingProfileRuleCreate",
    "QuotationPricingProfileRuleResponse",
    
    # Age bracket schemas
    "QuotationPricingRuleAgeBracketBase",
    "QuotationPricingRuleAgeBracketCreate",
    "QuotationPricingRuleAgeBracketResponse",
]