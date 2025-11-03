# app/modules/pricing/plans/routes/plan_eligibility_rule_routes.py
"""
Plan Eligibility Rule Routes

FastAPI routes for Plan Eligibility Rule management.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permission_scoped
from app.core.exceptions import EntityNotFoundError, ValidationError, BusinessLogicError
from app.modules.auth.models.user_model import User
from app.modules.pricing.plans.repositories.plan_eligibility_rule_repository import PlanEligibilityRuleRepository
from app.modules.pricing.plans.services.plan_eligibility_rule_service import PlanEligibilityRuleService
from app.modules.pricing.plans.schemas.plan_eligibility_rule_schema import (
    PlanEligibilityRuleCreate,
    PlanEligibilityRuleUpdate,
    PlanEligibilityRuleResponse,
    BulkEligibilityRuleCreate,
    EligibilityRuleSummary,
    EligibilityRuleSearchFilters,
    EligibilityEvaluationRequest,
    EligibilityEvaluationResponse,
    RuleCategory,
    RuleType,
    RuleSeverity
)
from app.core.responses import create_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/plans/{plan_id}/eligibility-rules",
    tags=["Plan Eligibility Rules"],
    responses={404: {"description": "Not found"}}
)

def get_eligibility_rule_service(db: Session = Depends(get_db)) -> PlanEligibilityRuleService:
    """Get eligibility rule service instance"""
    repository = PlanEligibilityRuleRepository(db)
    return PlanEligibilityRuleService(repository)

# ======================================================================
# CRUD Operations
# ======================================================================

@router.post(
    "/",
    response_model=PlanEligibilityRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create eligibility rule",
    description="Create a new eligibility rule for a plan"
)
async def create_eligibility_rule(
    plan_id: UUID = Path(..., description="Plan ID"),
    rule_data: PlanEligibilityRuleCreate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    """Create new eligibility rule"""
    try:
        eligibility_rule = service.create_eligibility_rule(
            plan_id=plan_id,
            rule_data=rule_data,
            created_by=current_user.id
        )
        
        logger.info(f"Created eligibility rule {eligibility_rule.id} for plan {plan_id}")
        return eligibility_rule
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating eligibility rule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create eligibility rule")

@router.post(
    "/bulk",
    response_model=List[PlanEligibilityRuleResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create eligibility rules",
    description="Create multiple eligibility rules for a plan at once"
)
async def bulk_create_eligibility_rules(
    plan_id: UUID = Path(..., description="Plan ID"),
    bulk_data: BulkEligibilityRuleCreate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    """Bulk create eligibility rules"""
    try:
        eligibility_rules = service.bulk_create_eligibility_rules(
            plan_id=plan_id,
            bulk_data=bulk_data,
            created_by=current_user.id
        )
        
        logger.info(f"Bulk created {len(eligibility_rules)} eligibility rules for plan {plan_id}")
        return eligibility_rules
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error bulk creating eligibility rules: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to bulk create eligibility rules")

@router.get(
    "/",
    response_model=List[PlanEligibilityRuleResponse],
    summary="List plan eligibility rules",
    description="Get all eligibility rules for a plan with optional filters"
)
async def list_eligibility_rules(
    plan_id: UUID = Path(..., description="Plan ID"),
    rule_category: Optional[RuleCategory] = Query(None, description="Filter by rule category"),
    rule_type: Optional[RuleType] = Query(None, description="Filter by rule type"),
    rule_severity: Optional[RuleSeverity] = Query(None, description="Filter by rule severity"),
    is_mandatory: Optional[bool] = Query(None, description="Filter by mandatory status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    can_override: Optional[bool] = Query(None, description="Filter by override capability"),
    rule_group: Optional[str] = Query(None, description="Filter by rule group"),
    effective_date: Optional[date] = Query(None, description="Filter by effective date"),
    text_search: Optional[str] = Query(None, description="Search in rule text"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get eligibility rules for a plan"""
    try:
        filters = EligibilityRuleSearchFilters(
            rule_category=rule_category,
            rule_type=rule_type,
            rule_severity=rule_severity,
            is_mandatory=is_mandatory,
            is_active=is_active,
            can_override=can_override,
            rule_group=rule_group,
            effective_date=effective_date,
            text_search=text_search,
            tags=tags.split(',') if tags else None
        )
        
        eligibility_rules = service.get_plan_eligibility_rules(plan_id, filters)
        return eligibility_rules
        
    except Exception as e:
        logger.error(f"Error listing eligibility rules for plan {plan_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve eligibility rules")

@router.get(
    "/effective",
    response_model=List[PlanEligibilityRuleResponse],
    summary="Get effective eligibility rules",
    description="Get all currently effective eligibility rules for a plan"
)
async def get_effective_eligibility_rules(
    plan_id: UUID = Path(..., description="Plan ID"),
    check_date: Optional[date] = Query(None, description="Date to check (default: today)"),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get effective eligibility rules"""
    try:
        return service.get_effective_eligibility_rules(plan_id, check_date)
    except Exception as e:
        logger.error(f"Error getting effective eligibility rules: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve effective eligibility rules")

@router.get(
    "/mandatory",
    response_model=List[PlanEligibilityRuleResponse],
    summary="Get mandatory eligibility rules",
    description="Get all mandatory eligibility rules for a plan"
)
async def get_mandatory_eligibility_rules(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get mandatory eligibility rules"""
    try:
        return service.get_mandatory_eligibility_rules(plan_id)
    except Exception as e:
        logger.error(f"Error getting mandatory eligibility rules: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve mandatory eligibility rules")

@router.get(
    "/category/{category}",
    response_model=List[PlanEligibilityRuleResponse],
    summary="Get eligibility rules by category",
    description="Get eligibility rules for a specific category"
)
async def get_eligibility_rules_by_category(
    plan_id: UUID = Path(..., description="Plan ID"),
    category: RuleCategory = Path(..., description="Rule category"),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get eligibility rules by category"""
    try:
        return service.get_rules_by_category(plan_id, category)
    except Exception as e:
        logger.error(f"Error getting eligibility rules by category: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve eligibility rules by category")

@router.get(
    "/{rule_id}",
    response_model=PlanEligibilityRuleResponse,
    summary="Get eligibility rule details",
    description="Get detailed information about a specific eligibility rule"
)
async def get_eligibility_rule(
    plan_id: UUID = Path(..., description="Plan ID"),
    rule_id: UUID = Path(..., description="Eligibility Rule ID"),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get eligibility rule by ID"""
    try:
        eligibility_rule = service.get_eligibility_rule(rule_id)
        
        # Verify rule belongs to the plan
        if eligibility_rule.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eligibility rule not found for this plan")
        
        return eligibility_rule
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eligibility rule not found")
    except Exception as e:
        logger.error(f"Error getting eligibility rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve eligibility rule")

@router.put(
    "/{rule_id}",
    response_model=PlanEligibilityRuleResponse,
    summary="Update eligibility rule",
    description="Update eligibility rule configuration"
)
async def update_eligibility_rule(
    plan_id: UUID = Path(..., description="Plan ID"),
    rule_id: UUID = Path(..., description="Eligibility Rule ID"),
    update_data: PlanEligibilityRuleUpdate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "edit"))
):
    """Update eligibility rule"""
    try:
        # Verify rule belongs to the plan
        eligibility_rule = service.get_eligibility_rule(rule_id)
        if eligibility_rule.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eligibility rule not found for this plan")
        
        updated_rule = service.update_eligibility_rule(
            rule_id=rule_id,
            update_data=update_data,
            updated_by=current_user.id
        )
        
        logger.info(f"Updated eligibility rule {rule_id}")
        return updated_rule
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eligibility rule not found")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating eligibility rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update eligibility rule")

@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete eligibility rule",
    description="Remove an eligibility rule from a plan"
)
async def delete_eligibility_rule(
    plan_id: UUID = Path(..., description="Plan ID"),
    rule_id: UUID = Path(..., description="Eligibility Rule ID"),
    current_user: User = Depends(get_current_user),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "delete"))
):
    """Delete eligibility rule"""
    try:
        # Verify rule belongs to the plan
        eligibility_rule = service.get_eligibility_rule(rule_id)
        if eligibility_rule.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eligibility rule not found for this plan")
        
        success = service.delete_eligibility_rule(rule_id)
        if success:
            logger.info(f"Deleted eligibility rule {rule_id}")
            return None
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eligibility rule not found")
    except Exception as e:
        logger.error(f"Error deleting eligibility rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete eligibility rule")

# ======================================================================
# Eligibility Evaluation
# ======================================================================

@router.post(
    "/evaluate",
    response_model=EligibilityEvaluationResponse,
    summary="Evaluate plan eligibility",
    description="Evaluate if an applicant meets plan eligibility requirements"
)
async def evaluate_plan_eligibility(
    plan_id: UUID = Path(..., description="Plan ID"),
    evaluation_request: EligibilityEvaluationRequest = ...,
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Evaluate plan eligibility"""
    try:
        evaluation_result = service.evaluate_eligibility(plan_id, evaluation_request)
        return evaluation_result
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error evaluating plan eligibility: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to evaluate plan eligibility")

# ======================================================================
# Analytics and Summary
# ======================================================================

@router.get(
    "/summary",
    response_model=EligibilityRuleSummary,
    summary="Get eligibility rules summary",
    description="Get summary statistics for eligibility rules in a plan"
)
async def get_eligibility_rule_summary(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get eligibility rule summary"""
    try:
        return service.get_eligibility_rule_summary(plan_id)
    except Exception as e:
        logger.error(f"Error getting eligibility rule summary: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve eligibility rule summary")

@router.get(
    "/validate-hierarchy",
    response_model=Dict[str, Any],
    summary="Validate rule hierarchy",
    description="Validate rule hierarchy and check for circular dependencies"
)
async def validate_rule_hierarchy(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Validate rule hierarchy"""
    try:
        validation_result = service.validate_rule_hierarchy(plan_id)
        
        return create_response(
            data=validation_result,
            message="Rule hierarchy validation completed"
        )
        
    except Exception as e:
        logger.error(f"Error validating rule hierarchy: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to validate rule hierarchy")

# ======================================================================
# Export and Documentation
# ======================================================================

@router.get(
    "/export",
    response_model=Dict[str, Any],
    summary="Export eligibility rules",
    description="Export eligibility rules for documentation or reporting"
)
async def export_eligibility_rules(
    plan_id: UUID = Path(..., description="Plan ID"),
    format: str = Query("json", regex="^(json|summary)$", description="Export format"),
    include_inactive: bool = Query(False, description="Include inactive rules"),
    language: str = Query("en", regex="^(en|ar)$", description="Language preference"),
    service: PlanEligibilityRuleService = Depends(get_eligibility_rule_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Export eligibility rules"""
    try:
        filters = EligibilityRuleSearchFilters()
        if not include_inactive:
            filters.is_active = True
        
        eligibility_rules = service.get_plan_eligibility_rules(plan_id, filters)
        
        export_data = {
            'plan_id': str(plan_id),
            'export_timestamp': date.today().isoformat(),
            'language': language,
            'total_rules': len(eligibility_rules),
            'eligibility_rules': []
        }
        
        for rule in eligibility_rules:
            rule_data = {
                'id': str(rule.id),
                'rule_name': rule.rule_name,
                'rule_category': rule.rule_category,
                'rule_type': rule.rule_type,
                'rule_severity': rule.rule_severity,
                'is_mandatory': rule.is_mandatory,
                'is_active': rule.is_active,
                'can_override': rule.can_override,
                'priority': rule.priority,
                'failure_message': rule.failure_message_ar if language == 'ar' and rule.failure_message_ar else rule.failure_message,
                'recommendation': rule.recommendation,
                'min_age': rule.min_age,
                'max_age': rule.max_age,
                'effective_date': rule.effective_date.isoformat() if rule.effective_date else None,
                'expiry_date': rule.expiry_date.isoformat() if rule.expiry_date else None
            }
            export_data['eligibility_rules'].append(rule_data)
        
        return create_response(
            data=export_data,
            message=f"Eligibility rules exported successfully ({format} format, {language} language)"
        )
        
    except Exception as e:
        logger.error(f"Error exporting eligibility rules: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export eligibility rules")
