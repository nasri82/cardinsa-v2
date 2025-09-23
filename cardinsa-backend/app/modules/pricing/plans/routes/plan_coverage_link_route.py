# app/modules/pricing/plans/routes/plan_coverage_link_routes.py
"""
Plan Coverage Link Routes

FastAPI routes for Plan Coverage Link management.
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
from app.modules.pricing.plans.repositories.plan_coverage_link_repository import PlanCoverageLinkRepository
from app.modules.pricing.plans.services.plan_coverage_link_service import PlanCoverageLinkService
from app.modules.pricing.plans.schemas.plan_coverage_link_schema import (
    PlanCoverageLinkCreate,
    PlanCoverageLinkUpdate,
    PlanCoverageLinkResponse,
    BulkCoverageLinkCreate,
    CoverageLinkSummary,
    CostCalculationRequest,
    CostCalculationResponse,
    CoverageTier
)
from app.core.responses import create_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/plans/{plan_id}/coverage-links",
    tags=["Plan Coverage Links"],
    responses={404: {"description": "Not found"}}
)

def get_coverage_link_service(db: Session = Depends(get_db)) -> PlanCoverageLinkService:
    """Get coverage link service instance"""
    repository = PlanCoverageLinkRepository(db)
    return PlanCoverageLinkService(repository)

# ======================================================================
# CRUD Operations
# ======================================================================

@router.post(
    "/",
    response_model=PlanCoverageLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link coverage to plan",
    description="Create a new coverage link for a plan with specific terms and conditions"
)
async def create_coverage_link(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_data: PlanCoverageLinkCreate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    """Create new coverage link"""
    try:
        coverage_link = service.create_coverage_link(
            plan_id=plan_id,
            link_data=link_data,
            created_by=current_user.id
        )
        
        logger.info(f"Created coverage link {coverage_link.id} for plan {plan_id}")
        return coverage_link
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating coverage link: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create coverage link")

@router.post(
    "/bulk",
    response_model=List[PlanCoverageLinkResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk link coverages to plan",
    description="Create multiple coverage links for a plan at once"
)
async def bulk_create_coverage_links(
    plan_id: UUID = Path(..., description="Plan ID"),
    bulk_data: BulkCoverageLinkCreate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    """Bulk create coverage links"""
    try:
        coverage_links = service.bulk_create_coverage_links(
            plan_id=plan_id,
            bulk_data=bulk_data,
            created_by=current_user.id
        )
        
        logger.info(f"Bulk created {len(coverage_links)} coverage links for plan {plan_id}")
        return coverage_links
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error bulk creating coverage links: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to bulk create coverage links")

@router.get(
    "/",
    response_model=List[PlanCoverageLinkResponse],
    summary="List plan coverage links",
    description="Get all coverage links for a plan with optional filters"
)
async def list_coverage_links(
    plan_id: UUID = Path(..., description="Plan ID"),
    is_mandatory: Optional[bool] = Query(None, description="Filter by mandatory status"),
    is_excluded: Optional[bool] = Query(None, description="Filter by excluded status"),
    coverage_tier: Optional[CoverageTier] = Query(None, description="Filter by coverage tier"),
    effective_date: Optional[date] = Query(None, description="Filter by effective date"),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get coverage links for a plan"""
    try:
        coverage_links = service.get_plan_coverage_links(
            plan_id=plan_id,
            is_mandatory=is_mandatory,
            is_excluded=is_excluded,
            coverage_tier=coverage_tier,
            effective_date=effective_date
        )
        return coverage_links
        
    except Exception as e:
        logger.error(f"Error listing coverage links for plan {plan_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve coverage links")

@router.get(
    "/mandatory",
    response_model=List[PlanCoverageLinkResponse],
    summary="Get mandatory coverages",
    description="Get all mandatory coverages for a plan"
)
async def get_mandatory_coverages(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get mandatory coverages"""
    try:
        return service.get_mandatory_coverages(plan_id)
    except Exception as e:
        logger.error(f"Error getting mandatory coverages: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve mandatory coverages")

@router.get(
    "/optional",
    response_model=List[PlanCoverageLinkResponse],
    summary="Get optional coverages",
    description="Get all optional coverages for a plan"
)
async def get_optional_coverages(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get optional coverages"""
    try:
        return service.get_optional_coverages(plan_id)
    except Exception as e:
        logger.error(f"Error getting optional coverages: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve optional coverages")

@router.get(
    "/{link_id}",
    response_model=PlanCoverageLinkResponse,
    summary="Get coverage link details",
    description="Get detailed information about a specific coverage link"
)
async def get_coverage_link(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_id: UUID = Path(..., description="Coverage Link ID"),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get coverage link by ID"""
    try:
        coverage_link = service.get_coverage_link(link_id)
        
        # Verify link belongs to the plan
        if coverage_link.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coverage link not found for this plan")
        
        return coverage_link
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coverage link not found")
    except Exception as e:
        logger.error(f"Error getting coverage link {link_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve coverage link")

@router.put(
    "/{link_id}",
    response_model=PlanCoverageLinkResponse,
    summary="Update coverage link",
    description="Update coverage link terms and conditions"
)
async def update_coverage_link(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_id: UUID = Path(..., description="Coverage Link ID"),
    update_data: PlanCoverageLinkUpdate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "edit"))
):
    """Update coverage link"""
    try:
        # Verify link belongs to the plan
        coverage_link = service.get_coverage_link(link_id)
        if coverage_link.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coverage link not found for this plan")
        
        updated_link = service.update_coverage_link(
            link_id=link_id,
            update_data=update_data,
            updated_by=current_user.id
        )
        
        logger.info(f"Updated coverage link {link_id}")
        return updated_link
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coverage link not found")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating coverage link {link_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update coverage link")

@router.delete(
    "/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete coverage link",
    description="Remove a coverage link from a plan"
)
async def delete_coverage_link(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_id: UUID = Path(..., description="Coverage Link ID"),
    current_user: User = Depends(get_current_user),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "delete"))
):
    """Delete coverage link"""
    try:
        # Verify link belongs to the plan
        coverage_link = service.get_coverage_link(link_id)
        if coverage_link.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coverage link not found for this plan")
        
        success = service.delete_coverage_link(link_id)
        if success:
            logger.info(f"Deleted coverage link {link_id}")
            return None
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coverage link not found")
    except Exception as e:
        logger.error(f"Error deleting coverage link {link_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete coverage link")

# ======================================================================
# Cost Calculations
# ======================================================================

@router.post(
    "/{link_id}/calculate-cost",
    response_model=CostCalculationResponse,
    summary="Calculate member cost",
    description="Calculate member cost for a service under this coverage link"
)
async def calculate_member_cost(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_id: UUID = Path(..., description="Coverage Link ID"),
    calculation_request: CostCalculationRequest = ...,
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Calculate member cost"""
    try:
        # Verify link belongs to the plan
        coverage_link = service.get_coverage_link(link_id)
        if coverage_link.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coverage link not found for this plan")
        
        cost_calculation = service.calculate_member_cost(link_id, calculation_request)
        return cost_calculation
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coverage link not found")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating cost: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate cost")

# ======================================================================
# Analytics and Summary
# ======================================================================

@router.get(
    "/summary",
    response_model=CoverageLinkSummary,
    summary="Get coverage links summary",
    description="Get summary statistics for coverage links in a plan"
)
async def get_coverage_summary(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get coverage summary"""
    try:
        return service.get_coverage_summary(plan_id)
    except Exception as e:
        logger.error(f"Error getting coverage summary: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve coverage summary")

@router.get(
    "/total-value",
    response_model=Dict[str, Any],
    summary="Get total coverage value",
    description="Calculate total coverage value for all linked coverages"
)
async def get_total_coverage_value(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get total coverage value"""
    try:
        total_value = service.calculate_plan_coverage_value(plan_id)
        
        return create_response(
            data={
                'plan_id': str(plan_id),
                'total_coverage_value': float(total_value),
                'currency': 'USD'  # This should come from plan or system settings
            },
            message="Total coverage value calculated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error calculating total coverage value: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate total coverage value")

# ======================================================================
# Validation
# ======================================================================

@router.post(
    "/validate-compatibility",
    response_model=Dict[str, Any],
    summary="Validate coverage compatibility",
    description="Validate if coverages are compatible with the plan"
)
async def validate_coverage_compatibility(
    plan_id: UUID = Path(..., description="Plan ID"),
    coverage_ids: List[UUID] = Query(..., description="Coverage IDs to validate"),
    service: PlanCoverageLinkService = Depends(get_coverage_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Validate coverage compatibility"""
    try:
        validation_result = service.validate_coverage_compatibility(plan_id, coverage_ids)
        
        return create_response(
            data=validation_result,
            message="Coverage compatibility validation completed"
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error validating coverage compatibility: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to validate coverage compatibility")
