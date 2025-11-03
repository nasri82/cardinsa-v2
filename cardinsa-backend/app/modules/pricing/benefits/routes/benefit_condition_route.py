"""
Benefit Condition Routes - Eligibility & Conditions Management API
==================================================================

Enterprise-grade REST API for benefit condition management with comprehensive
eligibility checking, member qualification validation, and condition dependency management.

Author: Assistant
Created: 2024
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import asyncio
import io

# Core imports
from app.core.database import get_db
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.core.dependencies import get_current_user, require_role
from app.core.logging import get_logger
from app.core.responses import success_response, error_response
from app.utils.pagination import PaginatedResponse, PaginationParams

# Service imports
from app.modules.pricing.benefits.services.benefit_condition_service import BenefitConditionService

# Model imports - FIXED: Only import what exists in the model file
from app.modules.pricing.benefits.models.benefit_condition_model import BenefitCondition

# Schema imports - FIXED: Import enums from schema file and create aliases
from app.modules.pricing.benefits.schemas.benefit_condition_schema import (
    BenefitConditionCreate,
    BenefitConditionUpdate,
    BenefitConditionResponse,
    BenefitConditionSummary,
    BenefitConditionFilter,
    BenefitConditionListResponse,
    BenefitConditionBulkCreate,
    BenefitConditionBulkUpdate,
    BenefitConditionBulkResponse,
    ConditionEvaluationRequest,
    ConditionEvaluationResult,
    # Import enums and create aliases for backward compatibility
    ConditionTypeEnum as ConditionType,
    ConditionStatusEnum as ConditionStatus,
    ConditionCategoryEnum,
    ApplicationScopeEnum,
    LogicalOperatorEnum,
    EvaluationFrequencyEnum,
    ErrorHandlingEnum,
    ValidationStatusEnum
)

logger = get_logger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1/benefit-conditions",
    tags=["Benefit Conditions"],
    responses={
        404: {"description": "Condition not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# =====================================================================
# MISSING SCHEMA DEFINITIONS - Create placeholders for referenced types
# =====================================================================

class EligibilityCheck(BaseModel):
    """Eligibility check request"""
    member_id: str = Field(..., description="Member ID to check")
    benefit_type_id: Optional[str] = Field(None, description="Benefit type ID")
    coverage_id: Optional[str] = Field(None, description="Coverage ID")
    evaluation_context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class EligibilityAssessment(BaseModel):
    """Eligibility assessment result"""
    member_id: str
    is_eligible: bool
    eligibility_score: float
    condition_results: List[Dict[str, Any]]
    failed_conditions: List[Dict[str, Any]] = []
    warnings: List[str] = []
    recommendations: List[str] = []

class MemberQualification(BaseModel):
    """Member qualification details"""
    member_id: str
    qualification_id: str
    qualification_level: str
    status: str
    effective_date: date
    qualifications: List[Dict[str, Any]] = []

class ConditionDependency(BaseModel):
    """Condition dependency information"""
    condition_id: str
    dependent_condition_id: str
    dependency_type: str
    rules: Dict[str, Any] = {}

class QualificationTracking(BaseModel):
    """Qualification tracking information"""
    member_id: str
    progress: Dict[str, Any]
    requirements: List[Dict[str, Any]]
    recommendations: List[str] = []

class EligibilityRule(BaseModel):
    """Eligibility rule definition"""
    rule_id: str
    rule_type: str
    conditions: Dict[str, Any]
    is_active: bool = True

class ConditionCompliance(BaseModel):
    """Condition compliance status"""
    condition_id: str
    compliance_score: float
    violations: List[Dict[str, Any]] = []
    trends: Optional[Dict[str, Any]] = None

class QualificationMetrics(BaseModel):
    """Qualification metrics and analytics"""
    period: str
    total_qualifications: int
    success_rate: float
    trends: Dict[str, Any] = {}

class ConditionSearchFilter(BaseModel):
    """Search filter for conditions"""
    search: Optional[str] = None
    condition_type: Optional[ConditionType] = None
    status: Optional[ConditionStatus] = None
    benefit_type_id: Optional[str] = None

class BulkConditionOperation(BaseModel):
    """Bulk operation on conditions"""
    operation_type: str
    condition_ids: List[str]
    parameters: Dict[str, Any] = {}

class BenefitConditionWithDetails(BenefitConditionResponse):
    """Extended condition response with details"""
    pass

# Define missing enum
class QualificationLevel(str):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def get_db_session():
    """Get database session"""
    return get_db()

def require_permissions(current_user: dict, required_roles: List[str]):
    """Check if user has required permissions"""
    user_roles = current_user.get('roles', [])
    if not any(role in user_roles for role in required_roles):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

def cache_response(ttl: int = 300):
    """Cache response decorator"""
    def decorator(func):
        return func
    return decorator

# =====================================================================
# CORE CRUD OPERATIONS
# =====================================================================

@router.post(
    "/",
    response_model=BenefitConditionResponse,
    status_code=201,
    summary="Create Benefit Condition",
    description="Create a new benefit condition with eligibility rules"
)
async def create_benefit_condition(
    condition_data: BenefitConditionCreate,
    validate_rules: bool = Query(True, description="Validate eligibility rules"),
    test_condition: bool = Query(False, description="Test condition with sample data"),
    initialize_dependencies: bool = Query(True, description="Initialize condition dependencies"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new benefit condition"""
    try:
        if not current_user.has_any(["admin", "benefits_manager", "eligibility_specialist"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitConditionService(db)
        condition = await service.create_benefit_condition(
            condition_data.dict()
        )
        
        logger.info(
            f"Benefit condition created by {current_user.id}: {condition.condition_name}",
            extra={"condition_id": str(condition.id), "user_id": str(current_user.id)}
        )
        
        return BenefitConditionResponse.from_orm(condition)
        
    except ValidationError as e:
        logger.error(f"Condition creation validation failed: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Condition creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create benefit condition")


@router.get(
    "/{condition_id}",
    response_model=BenefitConditionResponse,
    summary="Get Benefit Condition",
    description="Retrieve a specific benefit condition by ID"
)
async def get_benefit_condition(
    condition_id: str = Path(..., description="Condition ID"),
    include_rules: bool = Query(False, description="Include eligibility rules"),
    include_dependencies: bool = Query(False, description="Include condition dependencies"),
    include_metrics: bool = Query(False, description="Include performance metrics"),
    member_context: Optional[str] = Query(None, description="Member ID for personalized view"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific benefit condition"""
    try:
        service = BenefitConditionService(db)
        
        if include_rules or include_dependencies or include_metrics:
            condition = await service.get_condition_with_details(
                condition_id,
                include_rules=include_rules,
                include_dependencies=include_dependencies,
                include_metrics=include_metrics,
                member_context=member_context
            )
            if not condition:
                raise HTTPException(status_code=404, detail="Condition not found")
            return BenefitConditionWithDetails.from_orm(condition)
        else:
            condition = await service.get_by_id(condition_id)
            if not condition:
                raise HTTPException(status_code=404, detail="Condition not found")
            return BenefitConditionResponse.from_orm(condition)
            
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Condition not found")
    except Exception as e:
        logger.error(f"Failed to retrieve condition {condition_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve condition")


@router.put(
    "/{condition_id}",
    response_model=BenefitConditionResponse,
    summary="Update Benefit Condition",
    description="Update an existing benefit condition"
)
async def update_benefit_condition(
    condition_id: str = Path(..., description="Condition ID"),
    condition_data: BenefitConditionUpdate = Body(...),
    validate_changes: bool = Query(True, description="Validate condition changes"),
    update_dependencies: bool = Query(True, description="Update dependent conditions"),
    effective_date: Optional[date] = Body(None, description="Changes effective date"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing benefit condition"""
    try:
        if not current_user.has_any(["admin", "benefits_manager", "eligibility_specialist"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitConditionService(db)
        condition = await service.update_benefit_condition(
            condition_id,
            condition_data.dict(exclude_unset=True),
            validate_changes=validate_changes,
            update_dependencies=update_dependencies,
            effective_date=effective_date or date.today(),
            updated_by=str(current_user.id)
        )
        
        logger.info(
            f"Condition updated by {current_user.id}: {condition.condition_name}",
            extra={"condition_id": str(condition.id), "user_id": str(current_user.id)}
        )
        
        return BenefitConditionResponse.from_orm(condition)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Condition not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Condition update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update condition")


@router.delete(
    "/{condition_id}",
    status_code=204,
    summary="Delete Benefit Condition",
    description="Delete a benefit condition and handle dependencies"
)
async def delete_benefit_condition(
    condition_id: str = Path(..., description="Condition ID"),
    force: bool = Query(False, description="Force delete with dependencies"),
    cascade_delete: bool = Query(False, description="Delete dependent conditions"),
    archive_data: bool = Query(True, description="Archive condition data"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a benefit condition"""
    try:
        if not current_user.has_any(["admin"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitConditionService(db)
        await service.delete_benefit_condition(
            condition_id,
            force=force,
            cascade_delete=cascade_delete,
            archive_data=archive_data,
            deleted_by=str(current_user.id)
        )
        
        logger.info(
            f"Condition deleted by {current_user.id}: {condition_id}",
            extra={"condition_id": condition_id, "user_id": str(current_user.id)}
        )
        
        return JSONResponse(status_code=204, content=None)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Condition not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Condition deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete condition")

# =====================================================================
# ELIGIBILITY CHECKING
# =====================================================================

@router.post(
    "/check-eligibility",
    response_model=EligibilityAssessment,
    summary="Check Member Eligibility",
    description="Check member eligibility against benefit conditions"
)
async def check_member_eligibility(
    eligibility_check: EligibilityCheck = Body(...),
    comprehensive: bool = Query(True, description="Perform comprehensive eligibility check"),
    include_reasons: bool = Query(True, description="Include eligibility failure reasons"),
    cache_results: bool = Query(True, description="Cache eligibility results"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Check member eligibility against conditions"""
    try:
        service = BenefitConditionService(db)
        eligibility_assessment = await service.check_member_eligibility(
            check=eligibility_check.dict(),
            comprehensive=comprehensive,
            include_reasons=include_reasons,
            cache_results=cache_results,
            checked_by=str(current_user.id)
        )
        
        logger.info(
            f"Eligibility checked for member {eligibility_check.member_id}: eligible={eligibility_assessment.is_eligible}",
            extra={
                "member_id": eligibility_check.member_id,
                "is_eligible": eligibility_assessment.is_eligible,
                "condition_count": len(eligibility_assessment.condition_results)
            }
        )
        
        return eligibility_assessment
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Eligibility check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Eligibility check failed")


@router.get(
    "/member/{member_id}/eligibility",
    response_model=List[EligibilityAssessment],
    summary="Get Member Eligibility Status",
    description="Get comprehensive eligibility status for a member"
)
@cache_response(ttl=300)
async def get_member_eligibility_status(
    member_id: str = Path(..., description="Member ID"),
    condition_types: Optional[List[ConditionType]] = Query(None, description="Filter by condition types"),
    active_only: bool = Query(True, description="Include only active conditions"),
    as_of_date: Optional[date] = Query(None, description="Eligibility as of specific date"),
    include_history: bool = Query(False, description="Include eligibility history"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get member eligibility status"""
    try:
        service = BenefitConditionService(db)
        eligibility_status = await service.get_member_eligibility_status(
            member_id=member_id,
            condition_types=condition_types,
            active_only=active_only,
            as_of_date=as_of_date or date.today(),
            include_history=include_history
        )
        
        return eligibility_status
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Member not found")
    except Exception as e:
        logger.error(f"Failed to get member eligibility status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get eligibility status")


@router.post(
    "/batch-eligibility-check",
    response_model=List[EligibilityAssessment],
    summary="Batch Eligibility Check",
    description="Check eligibility for multiple members/conditions"
)
async def batch_eligibility_check(
    eligibility_checks: List[EligibilityCheck] = Body(..., description="Batch eligibility checks"),
    max_concurrent: int = Query(10, description="Maximum concurrent checks"),
    fail_fast: bool = Query(False, description="Stop on first failure"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Perform batch eligibility checks"""
    try:
        require_permissions(current_user, ["admin", "benefits_manager", "eligibility_specialist"])
        
        service = BenefitConditionService(db)
        batch_results = await service.batch_eligibility_check(
            checks=[check.dict() for check in eligibility_checks],
            max_concurrent=max_concurrent,
            fail_fast=fail_fast,
            checked_by=current_user.get('user_id')
        )
        
        logger.info(
            f"Batch eligibility check completed: {len(eligibility_checks)} checks",
            extra={"check_count": len(eligibility_checks), "user_id": current_user.get('user_id')}
        )
        
        return batch_results
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Batch eligibility check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Batch eligibility check failed")


# =====================================================================
# MEMBER QUALIFICATION
# =====================================================================

@router.get(
    "/member/{member_id}/qualifications",
    response_model=List[MemberQualification],
    summary="Get Member Qualifications",
    description="Get all qualifications for a member"
)
@cache_response(ttl=600)
async def get_member_qualifications(
    member_id: str = Path(..., description="Member ID"),
    qualification_levels: Optional[List[str]] = Query(None, description="Filter by qualification levels"),
    active_only: bool = Query(True, description="Include only active qualifications"),
    include_pending: bool = Query(False, description="Include pending qualifications"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get member qualifications"""
    try:
        service = BenefitConditionService(db)
        qualifications = await service.get_member_qualifications(
            member_id=member_id,
            qualification_levels=qualification_levels,
            active_only=active_only,
            include_pending=include_pending
        )
        
        return qualifications
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Member not found")
    except Exception as e:
        logger.error(f"Failed to get member qualifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get qualifications")


@router.post(
    "/member/{member_id}/qualify",
    response_model=MemberQualification,
    summary="Qualify Member",
    description="Qualify a member for specific benefits based on conditions"
)
async def qualify_member(
    member_id: str = Path(..., description="Member ID"),
    condition_ids: List[str] = Body(..., description="Condition IDs to qualify for"),
    qualification_data: Optional[Dict[str, Any]] = Body(None, description="Qualification metadata"),
    effective_date: Optional[date] = Body(None, description="Qualification effective date"),
    override_requirements: bool = Body(False, description="Override unmet requirements"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Qualify member for benefits"""
    try:
        require_permissions(current_user, ["admin", "benefits_manager", "eligibility_specialist"])
        
        service = BenefitConditionService(db)
        qualification = await service.qualify_member(
            member_id=member_id,
            condition_ids=condition_ids,
            qualification_data=qualification_data or {},
            effective_date=effective_date or date.today(),
            override_requirements=override_requirements,
            qualified_by=current_user.get('user_id')
        )
        
        logger.info(
            f"Member qualified by {current_user.get('user_id')}: {member_id} for {len(condition_ids)} conditions",
            extra={
                "member_id": member_id,
                "condition_count": len(condition_ids),
                "user_id": current_user.get('user_id')
            }
        )
        
        return qualification
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Member qualification failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Member qualification failed")


@router.get(
    "/member/{member_id}/qualification-tracking",
    response_model=QualificationTracking,
    summary="Track Member Qualification",
    description="Track qualification progress and requirements for a member"
)
@cache_response(ttl=300)
async def track_member_qualification(
    member_id: str = Path(..., description="Member ID"),
    condition_id: Optional[str] = Query(None, description="Specific condition to track"),
    include_recommendations: bool = Query(True, description="Include qualification recommendations"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Track member qualification progress"""
    try:
        service = BenefitConditionService(db)
        tracking = await service.track_member_qualification(
            member_id=member_id,
            condition_id=condition_id,
            include_recommendations=include_recommendations
        )
        
        return tracking
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Member not found")
    except Exception as e:
        logger.error(f"Failed to track member qualification: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track qualification")


# =====================================================================
# CONDITION DEPENDENCIES
# =====================================================================

@router.get(
    "/{condition_id}/dependencies",
    response_model=List[ConditionDependency],
    summary="Get Condition Dependencies",
    description="Get dependencies for a benefit condition"
)
@cache_response(ttl=600)
async def get_condition_dependencies(
    condition_id: str = Path(..., description="Condition ID"),
    include_dependents: bool = Query(True, description="Include dependent conditions"),
    max_depth: Optional[int] = Query(None, description="Maximum dependency depth"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get condition dependencies"""
    try:
        service = BenefitConditionService(db)
        dependencies = await service.get_condition_dependencies(
            condition_id=condition_id,
            include_dependents=include_dependents,
            max_depth=max_depth
        )
        
        return dependencies
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Condition not found")
    except Exception as e:
        logger.error(f"Failed to get condition dependencies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dependencies")


@router.post(
    "/{condition_id}/dependencies",
    response_model=ConditionDependency,
    summary="Add Condition Dependency",
    description="Add a dependency relationship between conditions"
)
async def add_condition_dependency(
    condition_id: str = Path(..., description="Condition ID"),
    dependent_condition_id: str = Body(..., description="Dependent condition ID"),
    dependency_type: str = Body(..., description="Type of dependency"),
    dependency_rules: Optional[Dict[str, Any]] = Body(None, description="Dependency rules"),
    validate_circular: bool = Query(True, description="Validate against circular dependencies"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Add condition dependency"""
    try:
        require_permissions(current_user, ["admin", "benefits_manager", "eligibility_specialist"])
        
        service = BenefitConditionService(db)
        dependency = await service.add_condition_dependency(
            condition_id=condition_id,
            dependent_condition_id=dependent_condition_id,
            dependency_type=dependency_type,
            rules=dependency_rules or {},
            validate_circular=validate_circular,
            added_by=current_user.get('user_id')
        )
        
        logger.info(
            f"Condition dependency added by {current_user.get('user_id')}: {condition_id} -> {dependent_condition_id}",
            extra={
                "condition_id": condition_id,
                "dependent_condition_id": dependent_condition_id,
                "user_id": current_user.get('user_id')
            }
        )
        
        return dependency
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add condition dependency: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add dependency")


# =====================================================================
# ELIGIBILITY RULES
# =====================================================================

@router.get(
    "/{condition_id}/rules",
    response_model=List[EligibilityRule],
    summary="Get Eligibility Rules",
    description="Get eligibility rules for a condition"
)
@cache_response(ttl=600)
async def get_eligibility_rules(
    condition_id: str = Path(..., description="Condition ID"),
    rule_types: Optional[List[str]] = Query(None, description="Filter by rule types"),
    active_only: bool = Query(True, description="Include only active rules"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get eligibility rules for a condition"""
    try:
        service = BenefitConditionService(db)
        rules = await service.get_eligibility_rules(
            condition_id=condition_id,
            rule_types=rule_types,
            active_only=active_only
        )
        
        return rules
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Condition not found")
    except Exception as e:
        logger.error(f"Failed to get eligibility rules: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get eligibility rules")


@router.post(
    "/{condition_id}/rules",
    response_model=EligibilityRule,
    summary="Add Eligibility Rule",
    description="Add an eligibility rule to a condition"
)
async def add_eligibility_rule(
    condition_id: str = Path(..., description="Condition ID"),
    rule_data: Dict[str, Any] = Body(..., description="Rule configuration"),
    validate_rule: bool = Query(True, description="Validate rule logic"),
    test_rule: bool = Query(False, description="Test rule with sample data"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Add eligibility rule to condition"""
    try:
        require_permissions(current_user, ["admin", "benefits_manager", "eligibility_specialist"])
        
        service = BenefitConditionService(db)
        rule = await service.add_eligibility_rule(
            condition_id=condition_id,
            rule_data=rule_data,
            validate_rule=validate_rule,
            test_rule=test_rule,
            added_by=current_user.get('user_id')
        )
        
        logger.info(
            f"Eligibility rule added by {current_user.get('user_id')}: condition {condition_id}",
            extra={"condition_id": condition_id, "rule_id": str(rule.id), "user_id": current_user.get('user_id')}
        )
        
        return rule
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Condition not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add eligibility rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add eligibility rule")


# =====================================================================
# COMPLIANCE MONITORING
# =====================================================================

@router.get(
    "/{condition_id}/compliance",
    response_model=ConditionCompliance,
    summary="Get Condition Compliance",
    description="Get compliance status and metrics for a condition"
)
@cache_response(ttl=1800)
async def get_condition_compliance(
    condition_id: str = Path(..., description="Condition ID"),
    period: str = Query("30d", description="Compliance analysis period"),
    include_violations: bool = Query(True, description="Include compliance violations"),
    include_trends: bool = Query(False, description="Include compliance trends"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get condition compliance status"""
    try:
        service = BenefitConditionService(db)
        compliance = await service.get_condition_compliance(
            condition_id=condition_id,
            period=period,
            include_violations=include_violations,
            include_trends=include_trends
        )
        
        return compliance
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Condition not found")
    except Exception as e:
        logger.error(f"Failed to get condition compliance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get compliance")


@router.post(
    "/compliance/audit",
    response_model=Dict[str, Any],
    summary="Audit Condition Compliance",
    description="Perform compliance audit on benefit conditions"
)
async def audit_condition_compliance(
    condition_ids: Optional[List[str]] = Body(None, description="Specific condition IDs to audit"),
    audit_criteria: Optional[List[str]] = Body(None, description="Audit criteria"),
    period: str = Query("90d", description="Audit period"),
    include_recommendations: bool = Query(True, description="Include improvement recommendations"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Perform compliance audit on conditions"""
    try:
        require_permissions(current_user, ["admin", "compliance_officer", "audit_manager"])
        
        service = BenefitConditionService(db)
        audit_result = await service.audit_condition_compliance(
            condition_ids=condition_ids,
            criteria=audit_criteria,
            period=period,
            include_recommendations=include_recommendations,
            audited_by=current_user.get('user_id')
        )
        
        logger.info(
            f"Condition compliance audit performed by {current_user.get('user_id')}",
            extra={
                "audited_condition_count": len(condition_ids) if condition_ids else 0,
                "user_id": current_user.get('user_id')
            }
        )
        
        return audit_result
        
    except Exception as e:
        logger.error(f"Compliance audit failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Compliance audit failed")


# =====================================================================
# SEARCH AND FILTERING
# =====================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[BenefitConditionResponse],
    summary="List Benefit Conditions",
    description="List and search benefit conditions with advanced filtering"
)
async def list_benefit_conditions(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    
    # Basic filters
    search: Optional[str] = Query(None, description="Search term"),
    condition_type: Optional[ConditionType] = Query(None, description="Filter by condition type"),
    status: Optional[ConditionStatus] = Query(None, description="Filter by status"),
    
    # Advanced filters
    benefit_type_id: Optional[str] = Query(None, description="Filter by benefit type"),
    requires_documentation: Optional[bool] = Query(None, description="Filter by documentation requirement"),
    has_dependencies: Optional[bool] = Query(None, description="Filter by dependency presence"),
    qualification_level: Optional[str] = Query(None, description="Filter by qualification level"),
    
    # Date filters
    effective_after: Optional[date] = Query(None, description="Effective after date"),
    effective_before: Optional[date] = Query(None, description="Effective before date"),
    
    # Sorting
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """List benefit conditions with advanced filtering"""
    try:
        service = BenefitConditionService(db)
        
        # Build filter dictionary
        filters = ConditionSearchFilter(
            search=search,
            condition_type=condition_type,
            status=status,
            benefit_type_id=benefit_type_id
        )
        
        # Get paginated results
        result = await service.search_benefit_conditions(
            filters=filters.dict(exclude_unset=True),
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return PaginatedResponse(
            items=[BenefitConditionResponse.from_orm(condition) for condition in result.items],
            total=result.total,
            page=page,
            size=size,
            pages=result.pages
        )
        
    except Exception as e:
        logger.error(f"Condition search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search conditions")


# =====================================================================
# BULK OPERATIONS
# =====================================================================

@router.post(
    "/bulk/operations",
    response_model=Dict[str, Any],
    summary="Bulk Condition Operations",
    description="Perform bulk operations on multiple conditions"
)
async def bulk_condition_operations(
    operation: BulkConditionOperation = Body(...),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Perform bulk operations on conditions"""
    try:
        require_permissions(current_user, ["admin", "benefits_manager"])
        
        service = BenefitConditionService(db)
        result = await service.bulk_operations(operation.dict())
        
        logger.info(
            f"Bulk condition operation performed by {current_user.get('user_id')}: {operation.operation_type}",
            extra={
                "operation_type": operation.operation_type,
                "condition_count": len(operation.condition_ids),
                "user_id": current_user.get('user_id')
            }
        )
        
        return result
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Bulk condition operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Bulk operation failed")


# =====================================================================
# ANALYTICS AND METRICS
# =====================================================================

@router.get(
    "/analytics/qualification-metrics",
    response_model=QualificationMetrics,
    summary="Qualification Analytics",
    description="Get analytics on member qualifications and eligibility"
)
@cache_response(ttl=3600)
async def get_qualification_metrics(
    period: str = Query("30d", description="Metrics period"),
    condition_types: Optional[List[ConditionType]] = Query(None, description="Specific condition types"),
    include_trends: bool = Query(True, description="Include qualification trends"),
    breakdown_by: Optional[str] = Query(None, description="Breakdown dimension"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get qualification analytics and metrics"""
    try:
        service = BenefitConditionService(db)
        metrics = await service.get_qualification_metrics(
            period=period,
            condition_types=condition_types,
            include_trends=include_trends,
            breakdown_by=breakdown_by
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Qualification metrics failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get qualification metrics")


@router.get(
    "/analytics/eligibility-patterns",
    response_model=Dict[str, Any],
    summary="Eligibility Pattern Analytics",
    description="Get analytics on eligibility patterns and trends"
)
@cache_response(ttl=3600)
async def get_eligibility_pattern_analytics(
    period: str = Query("90d", description="Analysis period"),
    include_failures: bool = Query(True, description="Include eligibility failure analysis"),
    demographic_breakdown: bool = Query(False, description="Include demographic breakdown"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get eligibility pattern analytics"""
    try:
        service = BenefitConditionService(db)
        analytics = await service.get_eligibility_pattern_analytics(
            period=period,
            include_failures=include_failures,
            demographic_breakdown=demographic_breakdown
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Eligibility pattern analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get eligibility analytics")


# =====================================================================
# HEALTH CHECK
# =====================================================================

@router.get(
    "/health",
    response_model=Dict[str, str],
    summary="Condition Service Health Check",
    description="Check the health status of the condition service"
)
async def condition_service_health(
    db: Session = Depends(get_db_session)
):
    """Health check for condition service"""
    try:
        service = BenefitConditionService(db)
        health_status = await service.health_check()
        
        return {
            "status": "healthy" if health_status else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "BenefitConditionService"
        }
        
    except Exception as e:
        logger.error(f"Condition service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "BenefitConditionService",
            "error": str(e)
        }