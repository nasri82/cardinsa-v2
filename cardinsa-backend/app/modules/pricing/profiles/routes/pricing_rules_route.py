# app/modules/pricing/profiles/routes/pricing_rules_route.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.responses import create_response, create_error_response, success_response
from app.modules.pricing.profiles.services.pricing_rules_service import PricingRulesService
from app.modules.pricing.profiles.services.rule_evaluation_service import RuleEvaluationService
from app.modules.pricing.profiles.schemas.pricing_rule_schema import (
    PricingRuleCreate,
    PricingRuleUpdate,
    PricingRuleResponse,
    RuleEvaluationRequest,
    RuleEvaluationResult,
    BatchEvaluationRequest,
    BatchEvaluationResult
)
from app.modules.auth.models.user_model import User
from app.core.exceptions import EntityNotFoundError, BusinessLogicError, ValidationError


router = APIRouter(prefix="/pricing/rules", tags=["Pricing Rules"])


def get_pricing_rules_service(db: Session = Depends(get_db)) -> PricingRulesService:
    """Dependency to get pricing rules service."""
    return PricingRulesService(db)


def get_rule_evaluation_service(db: Session = Depends(get_db)) -> RuleEvaluationService:
    """Dependency to get rule evaluation service."""
    return RuleEvaluationService(db)


# ============================================================================
# RULE CRUD ENDPOINTS
# ============================================================================

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_pricing_rule(
    rule_data: PricingRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Create a new pricing rule.
    
    - **name**: Required rule name
    - **description**: Optional rule description
    - **field_name**: Field name the rule operates on
    - **operator**: Comparison operator (=, >, >=, <, <=, IN, BETWEEN)
    - **condition_value**: Value(s) to compare against
    - **impact_type**: Type of impact (PERCENTAGE, FIXED_AMOUNT, MULTIPLIER)
    - **impact_value**: Impact value to apply
    - **formula**: Optional formula for complex calculations
    - **insurance_type**: Type of insurance this rule applies to
    - **is_active**: Whether the rule is active (default: true)
    """
    try:
        created_rule = rules_service.create_pricing_rule(
            rule_data=rule_data,
            created_by=current_user.id
        )
        
        return create_response(
            data=created_rule.model_dump(),
            message="Pricing rule created successfully",
            status_code=status.HTTP_201_CREATED,
            meta={
                "created_by": str(current_user.id)
            }
        )
        
    except ValidationError as e:
        return create_error_response(
            message="Validation error",
            errors=[str(e)],
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except BusinessLogicError as e:
        return create_error_response(
            message="Business logic error",
            errors=[str(e)],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return create_error_response(
            message="Failed to create pricing rule",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{rule_id}", response_model=Dict[str, Any])
async def get_pricing_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Get a pricing rule by ID.
    
    - **rule_id**: UUID of the pricing rule
    """
    try:
        rule = rules_service.get_pricing_rule(rule_id)
        
        if not rule:
            return create_error_response(
                message=f"Pricing rule {rule_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return create_response(
            data=rule.model_dump(),
            message="Pricing rule retrieved successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to retrieve pricing rule",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{rule_id}", response_model=Dict[str, Any])
async def update_pricing_rule(
    rule_id: UUID,
    rule_data: PricingRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Update an existing pricing rule.
    
    - **rule_id**: UUID of the pricing rule to update
    - All fields are optional and only provided fields will be updated
    """
    try:
        updated_rule = rules_service.update_pricing_rule(
            rule_id=rule_id,
            rule_data=rule_data,
            updated_by=current_user.id
        )
        
        if not updated_rule:
            return create_error_response(
                message=f"Pricing rule {rule_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return create_response(
            data=updated_rule.model_dump(),
            message="Pricing rule updated successfully",
            meta={
                "updated_by": str(current_user.id)
            }
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except ValidationError as e:
        return create_error_response(
            message="Validation error",
            errors=[str(e)],
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except BusinessLogicError as e:
        return create_error_response(
            message="Business logic error",
            errors=[str(e)],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return create_error_response(
            message="Failed to update pricing rule",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{rule_id}", response_model=Dict[str, Any])
async def delete_pricing_rule(
    rule_id: UUID,
    hard_delete: bool = Query(False, description="Permanently delete the rule"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Delete a pricing rule.
    
    - **rule_id**: UUID of the pricing rule to delete
    - **hard_delete**: Whether to permanently delete (default: soft delete)
    """
    try:
        success = rules_service.delete_pricing_rule(
            rule_id=rule_id,
            updated_by=current_user.id,
            hard_delete=hard_delete
        )
        
        if not success:
            return create_error_response(
                message=f"Pricing rule {rule_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return create_response(
            data={"rule_id": str(rule_id), "deleted": True},
            message="Pricing rule deleted successfully",
            meta={
                "deletion_type": "hard" if hard_delete else "soft",
                "deleted_by": str(current_user.id)
            }
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except BusinessLogicError as e:
        return create_error_response(
            message="Business logic error",
            errors=[str(e)],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return create_error_response(
            message="Failed to delete pricing rule",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# RULE SEARCH AND FILTERING ENDPOINTS
# ============================================================================

@router.get("/", response_model=Dict[str, Any])
async def search_pricing_rules(
    name: Optional[str] = Query(None, description="Filter by rule name (partial match)"),
    field_name: Optional[str] = Query(None, description="Filter by field name"),
    insurance_type: Optional[str] = Query(None, description="Filter by insurance type"),
    impact_type: Optional[str] = Query(None, description="Filter by impact type"),
    operator: Optional[str] = Query(None, description="Filter by operator"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Search and filter pricing rules.
    
    - **name**: Partial match on rule name
    - **field_name**: Filter by field name
    - **insurance_type**: Filter by insurance type
    - **impact_type**: Filter by impact type (PERCENTAGE, FIXED_AMOUNT, MULTIPLIER)
    - **operator**: Filter by operator (=, >, >=, <, <=, IN, BETWEEN)
    - **is_active**: Filter by active status
    - **page**: Page number for pagination
    - **page_size**: Number of items per page (max 100)
    """
    try:
        offset = (page - 1) * page_size
        
        results = rules_service.search_pricing_rules(
            name=name,
            field_name=field_name,
            insurance_type=insurance_type,
            impact_type=impact_type,
            operator=operator,
            is_active=is_active,
            limit=page_size,
            offset=offset
        )
        
        return create_response(
            data={
                "rules": [rule.model_dump() for rule in results['rules']],
                "pagination": {
                    **results['pagination'],
                    "page": page,
                    "page_size": page_size
                }
            },
            message="Pricing rules retrieved successfully",
            meta={
                "filters_applied": results['filters_applied']
            }
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to search pricing rules",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/by-field/{field_name}", response_model=Dict[str, Any])
async def get_rules_by_field(
    field_name: str,
    active_only: bool = Query(True, description="Return only active rules"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Get all rules that operate on a specific field.
    
    - **field_name**: Name of the field
    - **active_only**: Whether to return only active rules
    """
    try:
        rules = rules_service.get_rules_by_field(
            field_name=field_name,
            active_only=active_only
        )
        
        return create_response(
            data={
                "rules": [rule.model_dump() for rule in rules],
                "field_name": field_name,
                "total_count": len(rules)
            },
            message=f"Rules for field '{field_name}' retrieved successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message=f"Failed to retrieve rules for field '{field_name}'",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/by-insurance-type/{insurance_type}", response_model=Dict[str, Any])
async def get_rules_by_insurance_type(
    insurance_type: str,
    active_only: bool = Query(True, description="Return only active rules"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Get all rules for a specific insurance type.
    
    - **insurance_type**: Type of insurance
    - **active_only**: Whether to return only active rules
    """
    try:
        rules = rules_service.get_rules_by_insurance_type(
            insurance_type=insurance_type,
            active_only=active_only
        )
        
        return create_response(
            data={
                "rules": [rule.model_dump() for rule in rules],
                "insurance_type": insurance_type,
                "total_count": len(rules)
            },
            message=f"Rules for {insurance_type} insurance retrieved successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message=f"Failed to retrieve rules for {insurance_type} insurance",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# RULE EVALUATION ENDPOINTS
# ============================================================================

@router.post("/{rule_id}/evaluate", response_model=Dict[str, Any])
async def evaluate_single_rule(
    rule_id: UUID,
    input_data: Dict[str, Any] = Body(..., description="Input data for rule evaluation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Evaluate a single pricing rule against input data.
    
    - **rule_id**: UUID of the rule to evaluate
    - **input_data**: Dictionary containing field values for evaluation
    
    Example request body:
    ```json
    {
        "age": 35,
        "base_premium": 1000.0,
        "sum_insured": 50000.0,
        "deductible": 500.0
    }
    ```
    """
    try:
        result = rules_service.evaluate_single_rule(
            rule_id=rule_id,
            input_data=input_data
        )
        
        return create_response(
            data=result.model_dump() if hasattr(result, 'model_dump') else result.__dict__,
            message="Rule evaluation completed successfully"
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return create_error_response(
            message="Failed to evaluate pricing rule",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/evaluate-set", response_model=Dict[str, Any])
async def evaluate_rule_set(
    rule_ids: List[UUID] = Body(..., description="List of rule IDs to evaluate"),
    input_data: Dict[str, Any] = Body(..., description="Input data for rule evaluation"),
    evaluation_order: str = Body("sequential", description="Evaluation order: sequential, parallel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Evaluate a set of pricing rules against input data.
    
    - **rule_ids**: List of rule UUIDs to evaluate
    - **input_data**: Dictionary containing field values for evaluation
    - **evaluation_order**: Order of evaluation (sequential, parallel)
    
    Example request body:
    ```json
    {
        "rule_ids": [
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
        ],
        "input_data": {
            "age": 35,
            "base_premium": 1000.0,
            "sum_insured": 50000.0
        },
        "evaluation_order": "sequential"
    }
    ```
    """
    try:
        result = rules_service.evaluate_rule_set(
            rule_ids=rule_ids,
            input_data=input_data,
            evaluation_order=evaluation_order
        )
        
        return create_response(
            data=result,
            message="Rule set evaluation completed successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to evaluate rule set",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/evaluate-profile/{profile_id}", response_model=Dict[str, Any])
async def evaluate_profile_rules(
    profile_id: UUID,
    input_data: Dict[str, Any] = Body(..., description="Input data for rule evaluation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Evaluate all rules associated with a pricing profile.
    
    - **profile_id**: UUID of the pricing profile
    - **input_data**: Dictionary containing field values for evaluation
    
    Rules will be evaluated in their configured order within the profile.
    """
    try:
        result = rules_service.evaluate_profile_rules(
            profile_id=profile_id,
            input_data=input_data
        )
        
        return create_response(
            data=result,
            message="Profile rule evaluation completed successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to evaluate profile rules",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# ADVANCED EVALUATION ENDPOINTS
# ============================================================================

@router.post("/evaluate-async/{profile_id}", response_model=Dict[str, Any])
async def evaluate_profile_async(
    profile_id: UUID,
    input_data: Dict[str, Any] = Body(..., description="Input data for rule evaluation"),
    evaluation_strategy: str = Body("sequential", description="Evaluation strategy: sequential, parallel, optimized"),
    use_cache: bool = Body(True, description="Whether to use cached results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evaluation_service: RuleEvaluationService = Depends(get_rule_evaluation_service)
):
    """
    Asynchronously evaluate all rules for a pricing profile with advanced strategies.
    
    - **profile_id**: UUID of the pricing profile
    - **input_data**: Dictionary containing field values for evaluation
    - **evaluation_strategy**: Strategy for evaluation (sequential, parallel, optimized)
    - **use_cache**: Whether to use cached results for performance
    
    Advanced evaluation with performance optimization and caching.
    """
    try:
        result = await evaluation_service.evaluate_profile_async(
            profile_id=profile_id,
            input_data=input_data,
            evaluation_strategy=evaluation_strategy,
            use_cache=use_cache
        )
        
        return create_response(
            data=result,
            message="Async profile evaluation completed successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to evaluate profile asynchronously",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/evaluate-batch", response_model=Dict[str, Any])
async def evaluate_batch_profiles(
    batch_request: BatchEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evaluation_service: RuleEvaluationService = Depends(get_rule_evaluation_service)
):
    """
    Evaluate multiple profiles in batch with optimized processing.
    
    - **batch_request**: Batch evaluation request containing multiple profile evaluations
    
    Efficiently processes multiple profile evaluations with performance tracking.
    """
    try:
        result = evaluation_service.evaluate_batch_profiles(batch_request)
        
        return create_response(
            data=result.model_dump() if hasattr(result, 'model_dump') else result.__dict__,
            message="Batch evaluation completed successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to evaluate batch profiles",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/simulate/{profile_id}", response_model=Dict[str, Any])
async def evaluate_with_simulation(
    profile_id: UUID,
    base_input_data: Dict[str, Any] = Body(..., description="Base input data"),
    simulation_parameters: Dict[str, List[Any]] = Body(..., description="Parameters to vary in simulation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evaluation_service: RuleEvaluationService = Depends(get_rule_evaluation_service)
):
    """
    Evaluate a profile with multiple simulation scenarios.
    
    - **profile_id**: UUID of the pricing profile
    - **base_input_data**: Base input data for simulation
    - **simulation_parameters**: Parameters to vary across scenarios
    
    Example request body:
    ```json
    {
        "base_input_data": {
            "base_premium": 1000.0,
            "sum_insured": 50000.0
        },
        "simulation_parameters": {
            "age": [25, 35, 45, 55],
            "deductible": [500, 1000, 2000]
        }
    }
    ```
    
    Generates and evaluates all combinations of simulation parameters.
    """
    try:
        result = evaluation_service.evaluate_with_simulation(
            profile_id=profile_id,
            base_input_data=base_input_data,
            simulation_parameters=simulation_parameters
        )
        
        return create_response(
            data=result,
            message="Simulation evaluation completed successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to evaluate simulation scenarios",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# RULE ANALYSIS AND VALIDATION ENDPOINTS
# ============================================================================

@router.get("/{rule_id}/validate", response_model=Dict[str, Any])
async def validate_rule_configuration(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Validate the configuration of a pricing rule.
    
    - **rule_id**: UUID of the pricing rule to validate
    
    Returns comprehensive validation results including configuration analysis.
    """
    try:
        validation_result = rules_service.validate_rule_configuration(rule_id)
        
        return create_response(
            data=validation_result,
            message="Rule validation completed"
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return create_error_response(
            message="Failed to validate rule configuration",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{rule_id}/usage", response_model=Dict[str, Any])
async def check_rule_usage(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Check how a rule is being used across profiles.
    
    - **rule_id**: UUID of the pricing rule
    
    Returns usage information including profile associations.
    """
    try:
        usage_info = rules_service.check_rule_usage(rule_id)
        
        return create_response(
            data=usage_info,
            message="Rule usage information retrieved successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to check rule usage",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/analyze-conflicts", response_model=Dict[str, Any])
async def analyze_rule_conflicts(
    profile_id: Optional[UUID] = Body(None, description="Profile ID to analyze"),
    rule_ids: Optional[List[UUID]] = Body(None, description="Specific rule IDs to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rules_service: PricingRulesService = Depends(get_pricing_rules_service)
):
    """
    Analyze potential conflicts between rules.
    
    - **profile_id**: Profile ID to analyze (optional)
    - **rule_ids**: Specific rule IDs to analyze (optional)
    
    Either profile_id or rule_ids must be provided.
    Returns analysis of potential rule conflicts and overlaps.
    """
    try:
        if not profile_id and not rule_ids:
            return create_error_response(
                message="Either profile_id or rule_ids must be provided",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        conflict_analysis = rules_service.analyze_rule_conflicts(
            profile_id=profile_id,
            rule_ids=rule_ids
        )
        
        return create_response(
            data=conflict_analysis,
            message="Rule conflict analysis completed"
        )
        
    except ValidationError as e:
        return create_error_response(
            message="Validation error",
            errors=[str(e)],
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return create_error_response(
            message="Failed to analyze rule conflicts",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# PERFORMANCE OPTIMIZATION ENDPOINTS
# ============================================================================

@router.post("/optimize-execution-order/{profile_id}", response_model=Dict[str, Any])
async def optimize_rule_execution_order(
    profile_id: UUID,
    sample_data: Optional[List[Dict[str, Any]]] = Body(None, description="Sample data for performance testing"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evaluation_service: RuleEvaluationService = Depends(get_rule_evaluation_service)
):
    """
    Optimize the execution order of rules based on performance analysis.
    
    - **profile_id**: UUID of the pricing profile
    - **sample_data**: Optional sample data for performance testing
    
    Analyzes rule performance and provides optimization recommendations.
    """
    try:
        optimization_result = evaluation_service.optimize_rule_execution_order(
            profile_id=profile_id,
            sample_data=sample_data
        )
        
        return create_response(
            data=optimization_result,
            message="Rule execution order optimization completed"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to optimize rule execution order",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/evaluation-statistics", response_model=Dict[str, Any])
async def get_evaluation_statistics(
    profile_id: Optional[UUID] = Query(None, description="Profile ID for specific stats"),
    time_period_days: int = Query(30, ge=1, le=365, description="Time period for statistics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evaluation_service: RuleEvaluationService = Depends(get_rule_evaluation_service)
):
    """
    Get evaluation statistics and performance metrics.
    
    - **profile_id**: Optional profile ID for specific statistics
    - **time_period_days**: Time period for statistics (1-365 days)
    
    Returns comprehensive evaluation performance metrics.
    """
    try:
        statistics = evaluation_service.get_evaluation_statistics(
            profile_id=profile_id,
            time_period_days=time_period_days
        )
        
        return create_response(
            data=statistics,
            message="Evaluation statistics retrieved successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to retrieve evaluation statistics",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )