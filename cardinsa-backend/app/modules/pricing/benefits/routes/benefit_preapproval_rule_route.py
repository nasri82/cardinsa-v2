"""
Benefit Preapproval Rule Routes - Prior Authorization Workflow API
=================================================================

Enterprise-grade REST API for benefit preapproval rule management with comprehensive
prior authorization workflows, approval decision tracking, and compliance monitoring.

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
from app.modules.pricing.benefits.services.benefit_preapproval_rule_service import BenefitPreapprovalRuleService

# Model imports - Import the model only, enums don't exist in your current model
from app.modules.pricing.benefits.models.benefit_preapproval_rule_model import BenefitPreapprovalRule

# Define enums locally since they don't exist in your model file
from enum import Enum

class ApprovalType(str, Enum):
    """Approval types for API compatibility"""
    PRIOR_AUTH = "PRIOR_AUTH"
    PRE_CERTIFICATION = "PRE_CERTIFICATION"
    REFERRAL = "REFERRAL"
    STEP_THERAPY = "STEP_THERAPY"

class ApprovalStatus(str, Enum):
    """Approval status for API compatibility"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"

class RuleCategory(str, Enum):
    """Rule categories for API compatibility"""
    MEDICAL = "MEDICAL"
    SURGICAL = "SURGICAL"
    DIAGNOSTIC = "DIAGNOSTIC"
    THERAPEUTIC = "THERAPEUTIC"

class UrgencyLevel(str, Enum):
    """Urgency levels for API compatibility"""
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    STANDARD = "STANDARD"
    ELECTIVE = "ELECTIVE"

class ReviewLevel(str, Enum):
    """Review levels for API compatibility"""
    AUTO_APPROVED = "AUTO_APPROVED"
    NURSE_REVIEWER = "NURSE_REVIEWER"
    MEDICAL_DIRECTOR = "MEDICAL_DIRECTOR"

# Schema classes for API requests/responses
class BenefitPreapprovalRuleCreate(BaseModel):
    rule_code: str = Field(..., description="Unique rule code")
    rule_name: str = Field(..., description="Rule display name")
    rule_name_ar: Optional[str] = Field(None, description="Arabic rule name")
    approval_type: str = Field(..., description="Type of approval required")
    rule_category: str = Field(default="MEDICAL", description="Rule category")
    urgency_level: str = Field(default="STANDARD", description="Urgency level")
    review_level: str = Field(default="MEDICAL_DIRECTOR", description="Review level required")
    cost_threshold: Optional[Decimal] = Field(None, description="Cost threshold for approval")
    requires_approval: bool = Field(default=True, description="Whether approval is required")
    priority: int = Field(default=100, description="Rule priority")
    auto_approval_enabled: bool = Field(default=False, description="Enable auto-approval")
    max_processing_days: int = Field(default=3, description="Maximum processing days")
    approval_conditions: Optional[Dict[str, Any]] = Field(None, description="Approval conditions")
    medical_criteria: Optional[Dict[str, Any]] = Field(None, description="Medical criteria")
    documentation_requirements: Optional[Dict[str, Any]] = Field(None, description="Required documentation")
    is_active: bool = Field(default=True, description="Whether rule is active")
    description: Optional[str] = Field(None, description="Rule description")
    clinical_rationale: Optional[str] = Field(None, description="Clinical rationale")
    coverage_id: Optional[str] = Field(None, description="Associated coverage ID")
    benefit_type_id: Optional[str] = Field(None, description="Associated benefit type ID")

class BenefitPreapprovalRuleUpdate(BaseModel):
    rule_name: Optional[str] = Field(None, description="Rule display name")
    rule_name_ar: Optional[str] = Field(None, description="Arabic rule name")
    approval_type: Optional[str] = Field(None, description="Type of approval required")
    rule_category: Optional[str] = Field(None, description="Rule category")
    urgency_level: Optional[str] = Field(None, description="Urgency level")
    review_level: Optional[str] = Field(None, description="Review level required")
    cost_threshold: Optional[Decimal] = Field(None, description="Cost threshold for approval")
    requires_approval: Optional[bool] = Field(None, description="Whether approval is required")
    priority: Optional[int] = Field(None, description="Rule priority")
    auto_approval_enabled: Optional[bool] = Field(None, description="Enable auto-approval")
    max_processing_days: Optional[int] = Field(None, description="Maximum processing days")
    approval_conditions: Optional[Dict[str, Any]] = Field(None, description="Approval conditions")
    medical_criteria: Optional[Dict[str, Any]] = Field(None, description="Medical criteria")
    documentation_requirements: Optional[Dict[str, Any]] = Field(None, description="Required documentation")
    is_active: Optional[bool] = Field(None, description="Whether rule is active")
    description: Optional[str] = Field(None, description="Rule description")
    clinical_rationale: Optional[str] = Field(None, description="Clinical rationale")
    effective_to: Optional[datetime] = Field(None, description="Rule expiry date")

class BenefitPreapprovalRuleResponse(BaseModel):
    id: str = Field(..., description="Rule ID")
    rule_code: str = Field(..., description="Rule code")
    rule_name: str = Field(..., description="Rule name")
    rule_name_ar: Optional[str] = Field(None, description="Arabic rule name")
    approval_type: str = Field(..., description="Approval type")
    rule_category: str = Field(..., description="Rule category")
    urgency_level: str = Field(..., description="Urgency level")
    review_level: str = Field(..., description="Review level")
    cost_threshold: Optional[Decimal] = Field(None, description="Cost threshold")
    requires_approval: bool = Field(..., description="Requires approval")
    priority: int = Field(..., description="Priority")
    auto_approval_enabled: bool = Field(..., description="Auto-approval enabled")
    max_processing_days: int = Field(..., description="Max processing days")
    is_active: bool = Field(..., description="Is active")
    description: Optional[str] = Field(None, description="Description")
    clinical_rationale: Optional[str] = Field(None, description="Clinical rationale")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    
    class Config:
        from_attributes = True

class BenefitPreapprovalRuleWithDetails(BenefitPreapprovalRuleResponse):
    approval_conditions: Optional[Dict[str, Any]] = Field(None, description="Approval conditions")
    medical_criteria: Optional[Dict[str, Any]] = Field(None, description="Medical criteria")
    documentation_requirements: Optional[Dict[str, Any]] = Field(None, description="Documentation requirements")
    workflow_info: Optional[Dict[str, Any]] = Field(None, description="Workflow information")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")

class AuthorizationRequest(BaseModel):
    member_id: str = Field(..., description="Member ID")
    service_type: str = Field(..., description="Service type")
    provider_id: str = Field(..., description="Provider ID")
    procedure_code: Optional[str] = Field(None, description="Procedure code")
    diagnosis_codes: List[str] = Field(default_factory=list, description="Diagnosis codes")
    estimated_cost: Optional[Decimal] = Field(None, description="Estimated cost")
    is_emergency: bool = Field(default=False, description="Emergency case")
    clinical_info: Dict[str, Any] = Field(default_factory=dict, description="Clinical information")
    supporting_documents: List[str] = Field(default_factory=list, description="Supporting document IDs")

class AuthorizationResponse(BaseModel):
    request_id: str = Field(..., description="Authorization request ID")
    decision: str = Field(..., description="Authorization decision")
    rationale: str = Field(..., description="Decision rationale")
    conditions: List[str] = Field(default_factory=list, description="Approval conditions")
    valid_until: Optional[datetime] = Field(None, description="Authorization validity")
    authorization_number: Optional[str] = Field(None, description="Authorization number")
    appeal_deadline: Optional[datetime] = Field(None, description="Appeal deadline")

class PreapprovalWorkflow(BaseModel):
    rule_id: str = Field(..., description="Rule ID")
    workflow_type: str = Field(..., description="Workflow type")
    stages: List[Dict[str, Any]] = Field(..., description="Workflow stages")
    current_stage: str = Field(..., description="Current stage")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion")

class ClinicalCriteria(BaseModel):
    id: str = Field(..., description="Criteria ID")
    rule_id: str = Field(..., description="Associated rule ID")
    criteria_type: str = Field(..., description="Type of criteria")
    conditions: Dict[str, Any] = Field(..., description="Criteria conditions")
    is_active: bool = Field(default=True, description="Is active")
    description: Optional[str] = Field(None, description="Criteria description")

class ApprovalDecision(BaseModel):
    decision_id: str = Field(..., description="Decision ID")
    request_id: str = Field(..., description="Authorization request ID")
    decision: str = Field(..., description="Decision value")
    rationale: str = Field(..., description="Decision rationale")
    decided_by: str = Field(..., description="Decision maker")
    decision_date: datetime = Field(..., description="Decision timestamp")
    clinical_notes: Optional[str] = Field(None, description="Clinical notes")

class AuthorizationAppeal(BaseModel):
    id: str = Field(..., description="Appeal ID")
    request_id: str = Field(..., description="Original request ID")
    appeal_reason: str = Field(..., description="Reason for appeal")
    status: str = Field(..., description="Appeal status")
    submitted_by: str = Field(..., description="Appeal submitter")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    clinical_justification: Optional[str] = Field(None, description="Clinical justification")

class RuleCompliance(BaseModel):
    rule_id: str = Field(..., description="Rule ID")
    compliance_score: float = Field(..., description="Compliance score")
    violations: List[str] = Field(default_factory=list, description="Compliance violations")
    assessment_period: str = Field(..., description="Assessment period")
    last_assessed: datetime = Field(..., description="Last assessment date")

class WorkflowMetrics(BaseModel):
    period: str = Field(..., description="Metrics period")
    total_requests: int = Field(..., description="Total requests")
    approval_rate: float = Field(..., description="Approval rate")
    denial_rate: float = Field(..., description="Denial rate")
    average_processing_time: float = Field(..., description="Average processing time in hours")
    sla_compliance_rate: float = Field(..., description="SLA compliance rate")

class PreapprovalSearchFilter(BaseModel):
    search: Optional[str] = Field(None, description="Search term")
    rule_type: Optional[str] = Field(None, description="Rule type filter")
    status: Optional[str] = Field(None, description="Status filter")
    service_type: Optional[str] = Field(None, description="Service type filter")
    benefit_type_id: Optional[str] = Field(None, description="Benefit type filter")
    requires_clinical_review: Optional[bool] = Field(None, description="Requires clinical review")
    auto_approval_enabled: Optional[bool] = Field(None, description="Auto-approval enabled")
    effective_after: Optional[date] = Field(None, description="Effective after date")
    effective_before: Optional[date] = Field(None, description="Effective before date")

class BulkPreapprovalOperation(BaseModel):
    operation_type: str = Field(..., description="Type of bulk operation")
    rule_ids: List[str] = Field(..., description="Rule IDs to operate on")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")

logger = get_logger(__name__)

# Helper functions
def get_db_session():
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

# Initialize router
router = APIRouter(
    prefix="/api/v1/benefit-preapproval-rules",
    tags=["Benefit Preapproval Rules"],
    responses={
        404: {"description": "Preapproval rule not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# =====================================================================
# CORE CRUD OPERATIONS
# =====================================================================

@router.post(
    "/",
    response_model=BenefitPreapprovalRuleResponse,
    status_code=201,
    summary="Create Preapproval Rule",
    description="Create a new benefit preapproval rule with workflow configuration"
)
async def create_preapproval_rule(
    rule_data: BenefitPreapprovalRuleCreate,
    validate_criteria: bool = Query(True, description="Validate clinical criteria"),
    initialize_workflow: bool = Query(True, description="Initialize authorization workflow"),
    test_rule: bool = Query(False, description="Test rule with sample data"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new benefit preapproval rule"""
    try:
        # Check permissions
        require_permissions(current_user, ["admin", "medical_director", "authorization_manager"])
        
        service = BenefitPreapprovalRuleService(db)
        rule = await service.create_preapproval_rule(rule_data.dict())
        
        logger.info(
            f"Preapproval rule created by {current_user.get('user_id', 'unknown')}: {rule.rule_name}",
            extra={"rule_id": str(rule.id), "user_id": current_user.get('user_id')}
        )
        
        return BenefitPreapprovalRuleResponse.from_orm(rule)
        
    except ValidationError as e:
        logger.error(f"Preapproval rule creation validation failed: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Preapproval rule creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create preapproval rule")


@router.get(
    "/{rule_id}",
    response_model=Union[BenefitPreapprovalRuleResponse, BenefitPreapprovalRuleWithDetails],
    summary="Get Preapproval Rule",
    description="Retrieve a specific preapproval rule by ID"
)
async def get_preapproval_rule(
    rule_id: str = Path(..., description="Preapproval rule ID"),
    include_criteria: bool = Query(False, description="Include clinical criteria"),
    include_workflow: bool = Query(False, description="Include workflow configuration"),
    include_metrics: bool = Query(False, description="Include performance metrics"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific preapproval rule"""
    try:
        service = BenefitPreapprovalRuleService(db)
        rule = await service.get_by_id(rule_id)
        
        if not rule:
            raise HTTPException(status_code=404, detail="Preapproval rule not found")
        
        if include_criteria or include_workflow or include_metrics:
            # Return detailed response with additional information
            additional_data = {}
            if include_criteria:
                additional_data['medical_criteria'] = rule.medical_criteria
                additional_data['documentation_requirements'] = rule.documentation_requirements
                additional_data['approval_conditions'] = rule.approval_conditions
            
            response_data = BenefitPreapprovalRuleResponse.from_orm(rule).dict()
            response_data.update(additional_data)
            return BenefitPreapprovalRuleWithDetails(**response_data)
        else:
            return BenefitPreapprovalRuleResponse.from_orm(rule)
            
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Preapproval rule not found")
    except Exception as e:
        logger.error(f"Failed to retrieve preapproval rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve preapproval rule")


@router.put(
    "/{rule_id}",
    response_model=BenefitPreapprovalRuleResponse,
    summary="Update Preapproval Rule",
    description="Update an existing preapproval rule"
)
async def update_preapproval_rule(
    rule_id: str = Path(..., description="Preapproval rule ID"),
    rule_data: BenefitPreapprovalRuleUpdate = Body(...),
    validate_changes: bool = Query(True, description="Validate rule changes"),
    effective_date: Optional[date] = Body(None, description="Changes effective date"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing preapproval rule"""
    try:
        require_permissions(current_user, ["admin", "medical_director", "authorization_manager"])
        
        service = BenefitPreapprovalRuleService(db)
        rule = await service.update_by_id(
            rule_id,
            rule_data.dict(exclude_unset=True)
        )
        
        logger.info(
            f"Preapproval rule updated by {current_user.get('user_id', 'unknown')}: {rule.rule_name}",
            extra={"rule_id": str(rule.id), "user_id": current_user.get('user_id')}
        )
        
        return BenefitPreapprovalRuleResponse.from_orm(rule)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Preapproval rule not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Preapproval rule update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update preapproval rule")


@router.delete(
    "/{rule_id}",
    status_code=204,
    summary="Delete Preapproval Rule",
    description="Delete a preapproval rule"
)
async def delete_preapproval_rule(
    rule_id: str = Path(..., description="Preapproval rule ID"),
    force: bool = Query(False, description="Force delete with active authorizations"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a preapproval rule"""
    try:
        require_permissions(current_user, ["admin"])
        
        service = BenefitPreapprovalRuleService(db)
        await service.delete_by_id(rule_id)
        
        logger.info(
            f"Preapproval rule deleted by {current_user.get('user_id', 'unknown')}: {rule_id}",
            extra={"rule_id": rule_id, "user_id": current_user.get('user_id')}
        )
        
        return JSONResponse(status_code=204, content=None)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Preapproval rule not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Preapproval rule deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete preapproval rule")

# =====================================================================
# AUTHORIZATION PROCESSING
# =====================================================================

@router.post(
    "/authorize",
    response_model=AuthorizationResponse,
    summary="Process Authorization Request",
    description="Process a new authorization request through preapproval rules"
)
async def process_authorization_request(
    authorization_request: AuthorizationRequest = Body(...),
    auto_decide: bool = Query(True, description="Enable automatic decision making"),
    priority: str = Query("normal", description="Request priority level"),
    override_rules: Optional[List[str]] = Body(None, description="Rules to override for this request"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Process authorization request through preapproval rules"""
    try:
        service = BenefitPreapprovalRuleService(db)
        result = await service.evaluate_preapproval_request(authorization_request.dict())
        
        # Convert service result to API response format
        authorization_response = AuthorizationResponse(
            request_id=result.get('request_id', str(uuid.uuid4())),
            decision=result.get('decision', 'PENDING'),
            rationale='; '.join(result.get('decision_rationale', ['Processing request'])),
            conditions=result.get('next_steps', []),
            valid_until=None,  # Would be calculated based on approval validity
            authorization_number=None,  # Would be generated for approved requests
            appeal_deadline=None  # Would be calculated based on decision date
        )
        
        logger.info(
            f"Authorization processed: {authorization_response.request_id}, decision: {authorization_response.decision}",
            extra={
                "request_id": authorization_response.request_id,
                "decision": authorization_response.decision,
                "member_id": authorization_request.member_id,
                "service_type": authorization_request.service_type
            }
        )
        
        return authorization_response
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Authorization processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Authorization processing failed")


@router.get(
    "/authorizations/{request_id}",
    response_model=AuthorizationResponse,
    summary="Get Authorization Status",
    description="Get status and details of an authorization request"
)
@cache_response(ttl=60)
async def get_authorization_status(
    request_id: str = Path(..., description="Authorization request ID"),
    include_history: bool = Query(True, description="Include decision history"),
    include_clinical_notes: bool = Query(False, description="Include clinical review notes"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get authorization request status and details"""
    try:
        service = BenefitPreapprovalRuleService(db)
        status = await service.get_approval_status(request_id)
        
        # Convert service result to API response format
        authorization_response = AuthorizationResponse(
            request_id=request_id,
            decision=status.get('current_status', 'PENDING'),
            rationale="Status retrieved",
            conditions=[],
            valid_until=status.get('estimated_completion'),
            authorization_number=None,
            appeal_deadline=None
        )
        
        return authorization_response
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Authorization request not found")
    except Exception as e:
        logger.error(f"Failed to get authorization status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get authorization status")


# =====================================================================
# LIST AND SEARCH
# =====================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[BenefitPreapprovalRuleResponse],
    summary="List Preapproval Rules",
    description="List and search preapproval rules with advanced filtering"
)
async def list_preapproval_rules(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    
    # Basic filters
    search: Optional[str] = Query(None, description="Search term"),
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    
    # Advanced filters
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    benefit_type_id: Optional[str] = Query(None, description="Filter by benefit type"),
    requires_clinical_review: Optional[bool] = Query(None, description="Filter by clinical review requirement"),
    auto_approval_enabled: Optional[bool] = Query(None, description="Filter by auto-approval capability"),
    
    # Date filters
    effective_after: Optional[date] = Query(None, description="Effective after date"),
    effective_before: Optional[date] = Query(None, description="Effective before date"),
    
    # Sorting
    sort_by: str = Query("rule_name", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List preapproval rules with advanced filtering"""
    try:
        service = BenefitPreapprovalRuleService(db)
        
        # Build filter dictionary
        filters = PreapprovalSearchFilter(
            search=search,
            rule_type=rule_type,
            status=status,
            service_type=service_type,
            benefit_type_id=benefit_type_id,
            requires_clinical_review=requires_clinical_review,
            auto_approval_enabled=auto_approval_enabled,
            effective_after=effective_after,
            effective_before=effective_before
        )
        
        # Get rules from service
        rules = await service.get_all()  # This would need pagination support in service
        
        # For now, return a simple paginated response
        total_count = len(rules)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        page_rules = rules[start_idx:end_idx]
        
        return PaginatedResponse(
            items=[BenefitPreapprovalRuleResponse.from_orm(rule) for rule in page_rules],
            total=total_count,
            page=page,
            size=size,
            pages=(total_count + size - 1) // size  # Calculate total pages
        )
        
    except Exception as e:
        logger.error(f"Preapproval rule search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search preapproval rules")


# =====================================================================
# HEALTH CHECK
# =====================================================================

@router.get(
    "/health",
    response_model=Dict[str, str],
    summary="Preapproval Service Health Check",
    description="Check the health status of the preapproval service"
)
async def preapproval_service_health(
    db: Session = Depends(get_db)
):
    """Health check for preapproval service"""
    try:
        # Simple database connectivity check
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "BenefitPreapprovalRuleService"
        }
        
    except Exception as e:
        logger.error(f"Preapproval service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "BenefitPreapprovalRuleService",
            "error": str(e)
        }