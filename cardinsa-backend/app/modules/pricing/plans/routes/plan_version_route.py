# app/modules/pricing/plans/routes/plan_version_route.py

"""
Plan Version Route

RESTful API endpoints for Plan Version management.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import (
    APIRouter, Depends, HTTPException, Query, 
    status, Body, Path
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.pricing.plans.services.plan_version_service import PlanVersionService
from app.modules.pricing.plans.schemas.plan_version_schema import (
    PlanVersionCreate,
    PlanVersionUpdate,
    PlanVersionResponse,
    PlanVersionDetailResponse,
    VersionComparisonRequest,
    VersionComparisonResponse,
    VersionRollbackRequest,
    VersionApprovalRequest,
    VersionRejectionRequest,
    VersionHistoryFilters,
    VersionStatistics
)

from app.core.exceptions import (
    EntityNotFoundError,
    ValidationError,
    BusinessLogicError,
    UnauthorizedError
)
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/plans/{plan_id}/versions",
    tags=["Plan Versions"]
)


# ================================================================
# DEPENDENCIES
# ================================================================

def get_version_service(db: Session = Depends(get_db)) -> PlanVersionService:
    """Get version service instance"""
    return PlanVersionService(db)


# ================================================================
# VERSION CRUD ENDPOINTS
# ================================================================

@router.post(
    "/",
    response_model=PlanVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new version",
    description="Create a new version of a plan"
)
async def create_version(
    plan_id: UUID = Path(..., description="Plan UUID"),
    version_data: PlanVersionCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanVersionService = Depends(get_version_service)
):
    """
    Create a new plan version.
    
    - Captures current plan state
    - Tracks changes from previous version
    - Sets approval requirements based on change type
    """
    try:
        user_id = current_user.get("user_id")
        version = service.create_version(plan_id, version_data, user_id)
        return version
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


@router.get(
    "/current",
    response_model=PlanVersionResponse,
    summary="Get current version",
    description="Get the current active version of a plan"
)
async def get_current_version(
    plan_id: UUID = Path(..., description="Plan UUID"),
    db: Session = Depends(get_db),
    service: PlanVersionService = Depends(get_version_service)
):
    """Get the current active version."""
    try:
        return service.get_current_version(plan_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=List[PlanVersionResponse],
    summary="Get version history",
    description="Get version history for a plan"
)
async def get_version_history(
    plan_id: UUID = Path(..., description="Plan UUID"),
    include_draft: bool = Query(False, description="Include draft versions"),
    limit: int = Query(10, ge=1, le=50, description="Maximum versions"),
    db: Session = Depends(get_db),
    service: PlanVersionService = Depends(get_version_service)
):
    """Get version history with optional filters."""
    return service.get_version_history(plan_id, include_draft, limit)


@router.get(
    "/{version_id}",
    response_model=PlanVersionDetailResponse,
    summary="Get specific version",
    description="Get details of a specific version"
)
async def get_version(
    plan_id: UUID = Path(..., description="Plan UUID"),
    version_id: UUID = Path(..., description="Version UUID"),
    db: Session = Depends(get_db),
    service: PlanVersionService = Depends(get_version_service)
):
    """Get detailed version information including snapshots."""
    try:
        return service.get_version(version_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{version_id}",
    response_model=PlanVersionResponse,
    summary="Update draft version",
    description="Update a draft version"
)
async def update_version(
    plan_id: UUID = Path(..., description="Plan UUID"),
    version_id: UUID = Path(..., description="Version UUID"),
    update_data: PlanVersionUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanVersionService = Depends(get_version_service)
):
    """
    Update a draft version.
    
    Only versions in DRAFT status can be updated.
    """
    try:
        user_id = current_user.get("user_id")
        version = service.update_version(version_id, update_data, user_id)
        return version
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


# ================================================================
# APPROVAL WORKFLOW ENDPOINTS
# ================================================================

@router.post(
    "/{version_id}/submit",
    response_model=PlanVersionResponse,
    summary="Submit for approval",
    description="Submit version for approval"
)
async def submit_for_approval(
    plan_id: UUID = Path(..., description="Plan UUID"),
    version_id: UUID = Path(..., description="Version UUID"),
    notes: Optional[str] = Body(None, description="Submission notes"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanVersionService = Depends(get_version_service)
):
    """Submit a draft version for approval."""
    try:
        user_id = current_user.get("user_id")
        version = service.submit_for_approval(version_id, user_id, notes)
        return version
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/{version_id}/approve",
    response_model=PlanVersionResponse,
    summary="Approve version",
    description="Approve a pending version"
)
async def approve_version(
    plan_id: UUID = Path(..., description="Plan UUID"),
    version_id: UUID = Path(..., description="Version UUID"),
    approval_request: VersionApprovalRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanVersionService = Depends(get_version_service)
):
    """
    Approve a pending version.
    
    - Optionally make it the current version
    - Add approval notes
    """
    try:
        user_id = current_user.get("user_id")
        version = service.approve_version(
            version_id,
            user_id,
            approval_request.notes,
            approval_request.make_current
        )
        return version
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/{version_id}/reject",
    response_model=PlanVersionResponse,
    summary="Reject version",
    description="Reject a pending version"
)
async def reject_version(
    plan_id: UUID = Path(..., description="Plan UUID"),
    version_id: UUID = Path(..., description="Version UUID"),
    rejection_request: VersionRejectionRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanVersionService = Depends(get_version_service)
):
    """Reject a pending version with reason."""
    try:
        user_id = current_user.get("user_id")
        version = service.reject_version(
            version_id,
            user_id,
            rejection_request.reason
        )
        return version
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# VERSION MANAGEMENT ENDPOINTS
# ================================================================

@router.post(
    "/{version_id}/activate",
    response_model=PlanVersionResponse,
    summary="Activate version",
    description="Make version the current active version"
)
async def activate_version(
    plan_id: UUID = Path(..., description="Plan UUID"),
    version_id: UUID = Path(..., description="Version UUID"),
    effective_date: Optional[datetime] = Body(None, description="Effective date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanVersionService = Depends(get_version_service)
):
    """
    Activate a version as current.
    
    Version must be approved before activation.
    """
    try:
        user_id = current_user.get("user_id")
        version = service.activate_version(version_id, user_id, effective_date)
        return version
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/rollback",
    response_model=PlanVersionResponse,
    summary="Rollback to version",
    description="Rollback to a previous version"
)
async def rollback_to_version(
    plan_id: UUID = Path(..., description="Plan UUID"),
    rollback_request: VersionRollbackRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    service: PlanVersionService = Depends(get_version_service)
):
    """
    Rollback to a previous version.
    
    Creates a new version with the old version's data.
    """
    try:
        user_id = current_user.get("user_id")
        version = service.rollback_to_version(plan_id, rollback_request, user_id)
        return version
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


# ================================================================
# COMPARISON ENDPOINTS
# ================================================================

@router.post(
    "/compare",
    response_model=Dict[str, Any],
    summary="Compare versions",
    description="Compare two versions"
)
async def compare_versions(
    plan_id: UUID = Path(..., description="Plan UUID"),
    comparison_request: VersionComparisonRequest = Body(...),
    db: Session = Depends(get_db),
    service: PlanVersionService = Depends(get_version_service)
):
    """
    Compare two versions.
    
    Returns detailed differences between versions.
    """
    try:
        return service.compare_versions(comparison_request)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# STATISTICS ENDPOINTS
# ================================================================

@router.get(
    "/statistics",
    response_model=VersionStatistics,
    summary="Get version statistics",
    description="Get statistics about plan versions"
)
async def get_version_statistics(
    plan_id: UUID = Path(..., description="Plan UUID"),
    db: Session = Depends(get_db),
    service: PlanVersionService = Depends(get_version_service)
):
    """Get version statistics for a plan."""
    stats = service.get_version_statistics(plan_id)
    return VersionStatistics(**stats)


# ================================================================
# PENDING APPROVALS ENDPOINT
# ================================================================

@router.get(
    "/pending-approvals",
    response_model=List[PlanVersionResponse],
    summary="Get pending approvals",
    description="Get all versions pending approval"
)
async def get_pending_approvals(
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    db: Session = Depends(get_db),
    service: PlanVersionService = Depends(get_version_service)
):
    """Get all versions pending approval."""
    return service.get_pending_approvals(company_id)