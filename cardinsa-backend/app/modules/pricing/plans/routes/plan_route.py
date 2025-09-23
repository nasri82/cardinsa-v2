# app/modules/pricing/plans/routes/plan_route.py

"""
Plan Route - Production Ready

RESTful API endpoints for Plan management.
Implements comprehensive CRUD operations and business workflows.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime  # Added datetime import
from fastapi import (
    APIRouter, Depends, HTTPException, Query, 
    status, Body, Path, BackgroundTasks
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.pricing.plans.services.plan_service import PlanService
from app.modules.pricing.plans.schemas.plan_schema import (
    PlanCreate,
    PlanUpdate,
    PlanResponse,
    PlanDetailResponse,
    PlanSearchFilters,
    PlanComparisonRequest,
    PlanComparisonResponse,
    PlanEligibilityCheck,
    PlanEligibilityResponse,
    PlanPricingRequest,
    PlanPricingResponse,
    PlanTerritoryCreate,
    PlanTerritoryResponse,
    PlanVersionResponse,
    PlanBulkUpdate,
    PlanBulkResponse,
    PlanStatistics
)

from app.core.exceptions import (
    EntityNotFoundError,
    ValidationError,
    BusinessLogicError
)
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/plans",
    tags=["Plans"]
)


# ================================================================
# DEPENDENCIES
# ================================================================

def get_plan_service(db: Session = Depends(get_db)) -> PlanService:
    """Get plan service instance"""
    return PlanService(db)


# ================================================================
# PLAN CRUD ENDPOINTS
# ================================================================

@router.post(
    "/",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new plan",
    description="Create a new insurance plan with validation"
)
async def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Create a new plan.
    
    - **plan_code**: Unique code within company
    - **product_id**: Reference to product catalog
    - **company_id**: Company offering this plan
    - **premium_amount**: Base premium amount
    
    Returns created plan with generated ID.
    """
    try:
        user_id = current_user.get("user_id")
        plan = service.create_plan(plan_data, user_id)
        return plan
    except (ValidationError, BusinessLogicError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create plan"
        )


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Get plan by ID",
    description="Retrieve a plan by its ID"
)
async def get_plan(
    plan_id: UUID = Path(..., description="Plan UUID"),
    include_details: bool = Query(False, description="Include related data"),
    db: Session = Depends(get_db),
    service: PlanService = Depends(get_plan_service)
):
    """
    Get plan details.
    
    - **plan_id**: Plan UUID
    - **include_details**: Include territories, coverages, benefits, etc.
    
    Returns plan information.
    """
    try:
        if include_details:
            return service.get_plan(plan_id, include_details=True)
        return service.get_plan(plan_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Update plan",
    description="Update an existing plan"
)
async def update_plan(
    plan_id: UUID = Path(..., description="Plan UUID"),
    update_data: PlanUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Update plan information.
    
    All fields are optional for partial updates.
    Version will be incremented for significant changes.
    """
    try:
        user_id = current_user.get("user_id")
        plan = service.update_plan(plan_id, update_data, user_id)
        return plan
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ValidationError, BusinessLogicError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete plan",
    description="Soft delete a plan"
)
async def delete_plan(
    plan_id: UUID = Path(..., description="Plan UUID"),
    hard_delete: bool = Query(False, description="Permanently delete"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Delete a plan.
    
    - **hard_delete**: If true, permanently delete. Otherwise soft delete.
    
    Plans with active policies cannot be deleted.
    """
    try:
        user_id = current_user.get("user_id")
        success = service.delete_plan(plan_id, user_id, not hard_delete)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete plan"
            )
        return None
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# SEARCH & LIST ENDPOINTS
# ================================================================

@router.post(
    "/search",
    response_model=Dict[str, Any],
    summary="Search plans",
    description="Search plans with advanced filters"
)
async def search_plans(
    filters: PlanSearchFilters = Body(...),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    service: PlanService = Depends(get_plan_service)
):
    """
    Search plans with filters.
    
    Supports filtering by:
    - Product, company
    - Plan type, tier, status
    - Premium range
    - Date ranges
    - Text search
    
    Returns paginated results.
    """
    return service.search_plans(filters, page, page_size)


@router.get(
    "/",
    response_model=List[PlanResponse],
    summary="List active plans",
    description="Get list of active plans"
)
async def list_active_plans(
    product_id: Optional[UUID] = Query(None, description="Filter by product"),
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
    db: Session = Depends(get_db),
    service: PlanService = Depends(get_plan_service)
):
    """
    List active plans.
    
    Returns only currently active and available plans.
    """
    return service.get_active_plans(product_id, company_id)


# ================================================================
# PLAN LIFECYCLE ENDPOINTS
# ================================================================

@router.post(
    "/{plan_id}/activate",
    response_model=PlanResponse,
    summary="Activate plan",
    description="Activate a draft or approved plan"
)
async def activate_plan(
    plan_id: UUID = Path(..., description="Plan UUID"),
    effective_date: Optional[date] = Body(None, description="Activation date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Activate a plan for sale.
    
    Plan must be in DRAFT or APPROVED status.
    All required fields must be configured.
    """
    try:
        user_id = current_user.get("user_id")
        plan = service.activate_plan(plan_id, user_id, effective_date)
        return plan
    except (EntityNotFoundError, BusinessLogicError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{plan_id}/suspend",
    response_model=PlanResponse,
    summary="Suspend plan",
    description="Temporarily suspend an active plan"
)
async def suspend_plan(
    plan_id: UUID = Path(..., description="Plan UUID"),
    reason: str = Body(..., min_length=10, description="Suspension reason"),
    effective_date: Optional[date] = Body(None, description="Suspension date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Suspend an active plan.
    
    Suspended plans cannot be sold but existing policies remain valid.
    """
    try:
        user_id = current_user.get("user_id")
        plan = service.suspend_plan(plan_id, user_id, reason, effective_date)
        return plan
    except (EntityNotFoundError, BusinessLogicError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{plan_id}/discontinue",
    response_model=PlanResponse,
    summary="Discontinue plan",
    description="Permanently discontinue a plan"
)
async def discontinue_plan(
    plan_id: UUID = Path(..., description="Plan UUID"),
    reason: str = Body(..., min_length=10, description="Discontinuation reason"),
    end_date: Optional[date] = Body(None, description="End date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Discontinue a plan permanently.
    
    Discontinued plans cannot be reactivated.
    Existing policies may continue until expiry.
    """
    try:
        user_id = current_user.get("user_id")
        plan = service.discontinue_plan(plan_id, user_id, reason, end_date)
        return plan
    except (EntityNotFoundError, BusinessLogicError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# COMPARISON & ELIGIBILITY ENDPOINTS
# ================================================================

@router.post(
    "/compare",
    response_model=Dict[str, Any],
    summary="Compare plans",
    description="Compare multiple plans side by side"
)
async def compare_plans(
    comparison_request: PlanComparisonRequest = Body(...),
    db: Session = Depends(get_db),
    service: PlanService = Depends(get_plan_service)
):
    """
    Compare 2-5 plans.
    
    Returns:
    - Side-by-side comparison
    - Value scores
    - Recommendation
    """
    try:
        return service.compare_plans(comparison_request)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{plan_id}/check-eligibility",
    response_model=PlanEligibilityResponse,
    summary="Check eligibility",
    description="Check if applicant is eligible for plan"
)
async def check_eligibility(
    plan_id: UUID = Path(..., description="Plan UUID"),
    eligibility_data: PlanEligibilityCheck = Body(...),
    db: Session = Depends(get_db),
    service: PlanService = Depends(get_plan_service)
):
    """
    Check eligibility for a plan.
    
    Validates:
    - Age requirements
    - Group size (for group plans)
    - Location coverage
    - Pre-existing conditions
    
    Returns eligibility status with reasons.
    """
    try:
        result = service.check_eligibility(plan_id, eligibility_data)
        return PlanEligibilityResponse(**result)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# PRICING ENDPOINTS
# ================================================================

@router.post(
    "/{plan_id}/calculate-premium",
    response_model=PlanPricingResponse,
    summary="Calculate premium",
    description="Calculate premium with adjustments"
)
async def calculate_premium(
    plan_id: UUID = Path(..., description="Plan UUID"),
    pricing_request: PlanPricingRequest = Body(...),
    db: Session = Depends(get_db),
    service: PlanService = Depends(get_plan_service)
):
    """
    Calculate premium for a plan.
    
    Applies adjustments for:
    - Age factors
    - Group discounts
    - Territory adjustments
    - Risk factors
    
    Returns detailed premium breakdown.
    """
    try:
        result = service.calculate_premium(plan_id, pricing_request)
        return PlanPricingResponse(**result)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# TERRITORY MANAGEMENT ENDPOINTS
# ================================================================

@router.post(
    "/{plan_id}/territories",
    response_model=PlanTerritoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add territory",
    description="Add territory coverage to plan"
)
async def add_territory(
    plan_id: UUID = Path(..., description="Plan UUID"),
    territory_data: PlanTerritoryCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Add territory coverage to plan.
    
    Territories define:
    - Geographic coverage areas
    - Rate adjustments
    - Regulatory requirements
    """
    try:
        user_id = current_user.get("user_id")
        territory = service.repository.add_territory(
            plan_id,
            territory_data.dict(),
            user_id
        )
        return PlanTerritoryResponse.from_orm(territory)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{plan_id}/territories",
    response_model=List[PlanTerritoryResponse],
    summary="List territories",
    description="Get plan territories"
)
async def list_territories(
    plan_id: UUID = Path(..., description="Plan UUID"),
    active_only: bool = Query(True, description="Only active territories"),
    db: Session = Depends(get_db),
    service: PlanService = Depends(get_plan_service)
):
    """
    List territories for a plan.
    
    Returns all geographic coverage areas.
    """
    plan = service.repository.get_by_id(plan_id, load_relationships=True)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found"
        )
    
    territories = plan.territories
    if active_only:
        territories = [t for t in territories if t.is_active]
    
    return [PlanTerritoryResponse.from_orm(t) for t in territories]


# ================================================================
# VERSION MANAGEMENT ENDPOINTS
# ================================================================

@router.get(
    "/{plan_id}/versions",
    response_model=List[PlanVersionResponse],
    summary="List plan versions",
    description="Get version history for plan"
)
async def list_versions(
    plan_id: UUID = Path(..., description="Plan UUID"),
    db: Session = Depends(get_db),
    service: PlanService = Depends(get_plan_service)
):
    """
    Get version history for a plan.
    
    Returns all versions with change tracking.
    """
    # TODO: Implement version listing
    return []


# ================================================================
# BULK OPERATIONS ENDPOINTS
# ================================================================

@router.post(
    "/bulk/update",
    response_model=PlanBulkResponse,
    summary="Bulk update plans",
    description="Update multiple plans at once"
)
async def bulk_update_plans(
    bulk_data: PlanBulkUpdate = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """
    Update multiple plans in bulk.
    
    Useful for:
    - Mass status changes
    - Bulk price adjustments
    - Group configuration updates
    
    Large updates are processed in background.
    """
    try:
        user_id = current_user.get("user_id")
        
        # For large batches, process in background
        if len(bulk_data.plan_ids) > 10:
            background_tasks.add_task(
                service.repository.bulk_update,
                bulk_data.plan_ids,
                bulk_data.update_data.dict(exclude_unset=True),
                user_id
            )
            return PlanBulkResponse(
                success_count=0,
                failure_count=0,
                results=[{"status": "processing", "message": "Bulk update in progress"}]
            )
        
        # Small batch - process immediately
        count = service.repository.bulk_update(
            bulk_data.plan_ids,
            bulk_data.update_data.dict(exclude_unset=True),
            user_id
        )
        
        return PlanBulkResponse(
            success_count=count,
            failure_count=len(bulk_data.plan_ids) - count,
            results=[]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ================================================================
# STATISTICS & ANALYTICS ENDPOINTS
# ================================================================

@router.get(
    "/statistics",
    response_model=PlanStatistics,
    summary="Get plan statistics",
    description="Get statistical overview of plans"
)
async def get_statistics(
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    product_id: Optional[UUID] = Query(None, description="Filter by product"),
    db: Session = Depends(get_db),
    service: PlanService = Depends(get_plan_service)
):
    """
    Get plan statistics.
    
    Returns:
    - Total counts by status and type
    - Premium statistics
    - Trend data
    """
    stats = service.get_plan_statistics(company_id, product_id)
    return PlanStatistics(**stats)


# ================================================================
# HEALTH CHECK
# ================================================================

@router.get(
    "/health",
    summary="Health check",
    description="Check plan module health"
)
async def health_check():
    """
    Health check endpoint for plan module.
    """
    return {
        "status": "healthy",
        "module": "plans",
        "timestamp": datetime.utcnow().isoformat()
    }