# app/modules/pricing/profiles/routes/advanced_rules_route.py
"""
Advanced Rules Route - Production Ready Implementation
Handles multi-condition logic and advanced rule evaluation
"""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.responses import create_response, create_error_response
from app.modules.pricing.profiles.services.advanced_rule_engine import (
    MultiConditionLogicEngine, 
    AdvancedRule, 
    ConditionNode, 
    RuleImpact,
    LogicalOperator,
    ComparisonOperator
)
from app.modules.auth.models.user_model import User
from app.core.exceptions import ValidationError, BusinessLogicError
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/pricing/advanced-rules", tags=["Advanced Rules Engine"])

# =============================================================================
# SCHEMAS FOR API REQUESTS/RESPONSES
# =============================================================================

class ConditionNodeSchema(BaseModel):
    """Schema for condition node in rule structure."""
    operator: str = Field(..., description="Logical or comparison operator")
    field: Optional[str] = Field(None, description="Field name for comparison")
    value: Any = Field(None, description="Value for comparison")
    conditions: Optional[List['ConditionNodeSchema']] = Field(None, description="Sub-conditions for logical operators")

class RuleImpactSchema(BaseModel):
    """Schema for rule impact definition."""
    type: str = Field(..., description="Impact type: PERCENTAGE, FIXED_AMOUNT, MULTIPLIER, FORMULA")
    value: Any = Field(..., description="Impact value")
    formula: Optional[str] = Field(None, description="Formula for complex calculations")
    description: Optional[str] = Field(None, description="Human-readable description")

class AdvancedRuleSchema(BaseModel):
    """Schema for advanced rule definition."""
    rule_id: UUID
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    conditions: ConditionNodeSchema
    impact: RuleImpactSchema
    priority: int = Field(0, description="Rule priority for execution order")
    dependencies: List[UUID] = Field(default_factory=list, description="Rule dependencies")
    conflicts_with: List[UUID] = Field(default_factory=list, description="Conflicting rules")
    is_active: bool = Field(True, description="Whether rule is active")

class RuleEvaluationRequest(BaseModel):
    """Request schema for rule evaluation."""
    conditions: ConditionNodeSchema
    input_data: Dict[str, Any] = Field(..., description="Input data for evaluation")

class RuleEvaluationResponse(BaseModel):
    """Response schema for rule evaluation."""
    success: bool
    result: bool = Field(..., description="Whether conditions were met")
    execution_time: float = Field(..., description="Execution time in seconds")
    details: Dict[str, Any] = Field(default_factory=dict, description="Evaluation details")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")

class ValidationRequest(BaseModel):
    """Request schema for condition validation."""
    conditions: ConditionNodeSchema

class ValidationResponse(BaseModel):
    """Response schema for condition validation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    complexity_score: Optional[int] = Field(None, description="Complexity score (1-10)")

class SupportedOperatorsResponse(BaseModel):
    """Response schema for supported operators."""
    logical_operators: List[str]
    comparison_operators: List[str]
    operator_descriptions: Dict[str, str]

# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

def get_logic_engine(db: Session = Depends(get_db)) -> MultiConditionLogicEngine:
    """Dependency to get multi-condition logic engine."""
    return MultiConditionLogicEngine(db)

# =============================================================================
# CORE ENDPOINTS
# =============================================================================

@router.post("/evaluate", response_model=RuleEvaluationResponse)
async def evaluate_advanced_rule(
    request: RuleEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    logic_engine: MultiConditionLogicEngine = Depends(get_logic_engine)
):
    """
    Evaluate complex multi-condition rules against input data.
    
    This endpoint allows you to test complex rule conditions with nested
    AND/OR/NOT logic against provided input data.
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"Evaluating advanced rule for user {current_user.id}")
        
        # Convert schema to internal condition node
        condition_node = _convert_schema_to_condition_node(request.conditions)
        
        # Evaluate the conditions
        result = logic_engine.evaluate_conditions(condition_node, request.input_data)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return RuleEvaluationResponse(
            success=True,
            result=result,
            execution_time=execution_time,
            details={
                "input_fields_used": list(request.input_data.keys()),
                "condition_complexity": _calculate_condition_complexity(condition_node),
                "evaluation_path": "multi_condition_logic_engine"
            }
        )
        
    except ValidationError as e:
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        return RuleEvaluationResponse(
            success=False,
            result=False,
            execution_time=execution_time,
            errors=[str(e)]
        )
    
    except Exception as e:
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"Error evaluating advanced rule: {str(e)}")
        return RuleEvaluationResponse(
            success=False,
            result=False,
            execution_time=execution_time,
            errors=[f"Evaluation error: {str(e)}"]
        )

@router.post("/validate-conditions", response_model=ValidationResponse)
async def validate_rule_conditions(
    request: ValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    logic_engine: MultiConditionLogicEngine = Depends(get_logic_engine)
):
    """
    Validate the structure and syntax of complex rule conditions.
    
    This endpoint checks rule conditions for:
    - Correct operator usage
    - Proper nesting structure
    - Field name requirements
    - Value type validation
    """
    try:
        logger.info(f"Validating rule conditions for user {current_user.id}")
        
        # Convert schema to internal condition node
        condition_node = _convert_schema_to_condition_node(request.conditions)
        
        # Validate condition structure
        validation_errors = logic_engine.validate_condition_structure(condition_node)
        
        # Calculate complexity score
        complexity_score = _calculate_condition_complexity(condition_node)
        
        # Generate warnings for complex conditions
        warnings = []
        if complexity_score > 7:
            warnings.append("Condition is very complex and may impact performance")
        if complexity_score > 5:
            warnings.append("Consider breaking down into simpler rules for better maintainability")
        
        return ValidationResponse(
            is_valid=len(validation_errors) == 0,
            errors=validation_errors,
            warnings=warnings,
            complexity_score=complexity_score
        )
        
    except Exception as e:
        logger.error(f"Error validating conditions: {str(e)}")
        return ValidationResponse(
            is_valid=False,
            errors=[f"Validation error: {str(e)}"]
        )

@router.get("/operators", response_model=SupportedOperatorsResponse)
async def get_supported_operators():
    """
    Get list of all supported logical and comparison operators.
    
    Returns comprehensive information about operators that can be used
    in advanced rule conditions.
    """
    try:
        return SupportedOperatorsResponse(
            logical_operators=[op.value for op in LogicalOperator],
            comparison_operators=[op.value for op in ComparisonOperator],
            operator_descriptions={
                # Logical operators
                "AND": "All sub-conditions must be true",
                "OR": "At least one sub-condition must be true", 
                "NOT": "Negate the result of sub-condition",
                
                # Comparison operators
                "=": "Equal to",
                ">": "Greater than",
                ">=": "Greater than or equal to",
                "<": "Less than",
                "<=": "Less than or equal to",
                "IN": "Value is in the provided list",
                "BETWEEN": "Value is between two values (inclusive)",
                "CONTAINS": "Field contains the specified value",
                "STARTS_WITH": "Field starts with the specified value",
                "ENDS_WITH": "Field ends with the specified value"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting supported operators: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supported operators"
        )

@router.post("/parse-condition", response_model=Dict[str, Any])
async def parse_condition_json(
    condition_json: Dict[str, Any] = Body(..., description="JSON condition structure"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    logic_engine: MultiConditionLogicEngine = Depends(get_logic_engine)
):
    """
    Parse and analyze a JSON condition structure.
    
    This endpoint takes a raw JSON condition structure and parses it
    into the internal format, providing analysis and validation.
    """
    try:
        logger.info(f"Parsing condition JSON for user {current_user.id}")
        
        # Parse JSON condition
        condition_node = logic_engine.parse_condition_json(condition_json)
        
        # Validate the parsed condition
        validation_errors = logic_engine.validate_condition_structure(condition_node)
        
        # Analyze the condition
        analysis = {
            "structure_valid": len(validation_errors) == 0,
            "validation_errors": validation_errors,
            "complexity_score": _calculate_condition_complexity(condition_node),
            "operator_count": _count_operators(condition_node),
            "max_nesting_depth": _calculate_nesting_depth(condition_node),
            "field_references": _extract_field_references(condition_node)
        }
        
        return create_response(
            data=analysis,
            message="Condition parsed and analyzed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error parsing condition JSON: {str(e)}")
        return create_error_response(
            message="Failed to parse condition JSON",
            errors=[str(e)],
            status_code=status.HTTP_400_BAD_REQUEST
        )

@router.post("/test-scenarios", response_model=Dict[str, Any])
async def test_rule_scenarios(
    conditions: ConditionNodeSchema,
    test_scenarios: List[Dict[str, Any]] = Body(..., description="List of test data scenarios"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    logic_engine: MultiConditionLogicEngine = Depends(get_logic_engine)
):
    """
    Test rule conditions against multiple scenarios.
    
    This endpoint allows bulk testing of rule conditions against
    multiple input data scenarios to verify rule behavior.
    """
    try:
        logger.info(f"Testing rule scenarios for user {current_user.id}")
        
        # Convert schema to internal condition node
        condition_node = _convert_schema_to_condition_node(conditions)
        
        # Test against each scenario
        results = []
        for i, scenario in enumerate(test_scenarios):
            try:
                start_time = datetime.utcnow()
                result = logic_engine.evaluate_conditions(condition_node, scenario)
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                results.append({
                    "scenario_index": i,
                    "input_data": scenario,
                    "result": result,
                    "success": True,
                    "execution_time": execution_time,
                    "error": None
                })
                
            except Exception as e:
                results.append({
                    "scenario_index": i,
                    "input_data": scenario,
                    "result": False,
                    "success": False,
                    "execution_time": 0,
                    "error": str(e)
                })
        
        # Generate summary statistics
        successful_tests = [r for r in results if r["success"]]
        true_results = [r for r in successful_tests if r["result"]]
        
        summary = {
            "total_scenarios": len(test_scenarios),
            "successful_evaluations": len(successful_tests),
            "failed_evaluations": len(test_scenarios) - len(successful_tests),
            "conditions_met": len(true_results),
            "conditions_not_met": len(successful_tests) - len(true_results),
            "average_execution_time": sum(r["execution_time"] for r in successful_tests) / len(successful_tests) if successful_tests else 0,
            "success_rate": len(successful_tests) / len(test_scenarios) * 100 if test_scenarios else 0
        }
        
        return create_response(
            data={
                "summary": summary,
                "detailed_results": results
            },
            message=f"Tested rule against {len(test_scenarios)} scenarios"
        )
        
    except Exception as e:
        logger.error(f"Error testing rule scenarios: {str(e)}")
        return create_error_response(
            message="Failed to test rule scenarios",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _convert_schema_to_condition_node(schema: ConditionNodeSchema) -> ConditionNode:
    """Convert API schema to internal ConditionNode structure."""
    sub_conditions = None
    if schema.conditions:
        sub_conditions = [_convert_schema_to_condition_node(sub) for sub in schema.conditions]
    
    return ConditionNode(
        operator=schema.operator,
        field=schema.field,
        value=schema.value,
        conditions=sub_conditions
    )

def _calculate_condition_complexity(condition: ConditionNode) -> int:
    """Calculate complexity score for a condition (1-10 scale)."""
    if not condition:
        return 0
    
    complexity = 1
    
    # Add complexity for logical operators
    if condition.is_logical():
        complexity += 1
        if condition.conditions:
            # Add complexity for each sub-condition
            complexity += sum(_calculate_condition_complexity(sub) for sub in condition.conditions)
    
    # Add complexity for comparison operators
    elif condition.is_comparison():
        if condition.operator in ["BETWEEN", "IN"]:
            complexity += 1
        if condition.operator in ["CONTAINS", "STARTS_WITH", "ENDS_WITH"]:
            complexity += 1
    
    return min(complexity, 10)  # Cap at 10

def _count_operators(condition: ConditionNode) -> Dict[str, int]:
    """Count different types of operators in condition tree."""
    counts = {"logical": 0, "comparison": 0}
    
    if not condition:
        return counts
    
    if condition.is_logical():
        counts["logical"] += 1
        if condition.conditions:
            for sub_condition in condition.conditions:
                sub_counts = _count_operators(sub_condition)
                counts["logical"] += sub_counts["logical"]
                counts["comparison"] += sub_counts["comparison"]
    
    elif condition.is_comparison():
        counts["comparison"] += 1
    
    return counts

def _calculate_nesting_depth(condition: ConditionNode, current_depth: int = 0) -> int:
    """Calculate maximum nesting depth of condition tree."""
    if not condition or not condition.conditions:
        return current_depth
    
    max_depth = current_depth
    for sub_condition in condition.conditions:
        depth = _calculate_nesting_depth(sub_condition, current_depth + 1)
        max_depth = max(max_depth, depth)
    
    return max_depth

def _extract_field_references(condition: ConditionNode) -> List[str]:
    """Extract all field references from condition tree."""
    fields = []
    
    if not condition:
        return fields
    
    if condition.field:
        fields.append(condition.field)
    
    if condition.conditions:
        for sub_condition in condition.conditions:
            fields.extend(_extract_field_references(sub_condition))
    
    return list(set(fields))  # Return unique fields

# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@router.get("/health", response_model=Dict[str, Any])
async def advanced_rules_health_check(
    db: Session = Depends(get_db),
    logic_engine: MultiConditionLogicEngine = Depends(get_logic_engine)
):
    """
    Health check for the advanced rules engine.
    
    Verifies that all components are working correctly.
    """
    try:
        # Test basic functionality
        test_condition = ConditionNode(
            operator=ComparisonOperator.EQUALS,
            field="test_field",
            value="test_value"
        )
        
        test_data = {"test_field": "test_value"}
        result = logic_engine.evaluate_conditions(test_condition, test_data)
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "multi_condition_logic_engine": "operational",
                "condition_evaluation": "operational",
                "validation": "operational"
            },
            "test_results": {
                "basic_evaluation": "passed" if result else "failed",
                "supported_operators": len(LogicalOperator) + len(ComparisonOperator)
            }
        }
        
        return create_response(
            data=health_status,
            message="Advanced rules engine is healthy"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return create_error_response(
            message="Advanced rules engine health check failed",
            errors=[str(e)],
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )