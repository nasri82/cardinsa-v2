# app/modules/pricing/plans/routes/plan_exclusion_link_routes.py
"""
Plan Exclusion Link Routes

FastAPI routes for Plan Exclusion Link management.
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
from app.modules.pricing.plans.repositories.plan_exclusion_link_repository import PlanExclusionLinkRepository
from app.modules.pricing.plans.services.plan_exclusion_link_service import PlanExclusionLinkService
from app.modules.pricing.plans.schemas.plan_exclusion_link_schema import (
    PlanExclusionLinkCreate,
    PlanExclusionLinkUpdate,
    PlanExclusionLinkResponse,
    BulkExclusionLinkCreate,
    ExclusionLinkSummary,
    ExclusionLinkSearchFilters,
    CoverageApplicationCheck,
    ExclusionLinkEffectivenessCheck,
    LinkStatus,
    ApplicationScope,
    OverrideType
)
from app.core.responses import create_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/plans/{plan_id}/exclusion-links",
    tags=["Plan Exclusion Links"],
    responses={404: {"description": "Not found"}}
)

def get_exclusion_link_service(db: Session = Depends(get_db)) -> PlanExclusionLinkService:
    """Get exclusion link service instance"""
    repository = PlanExclusionLinkRepository(db)
    return PlanExclusionLinkService(repository)

# ======================================================================
# CRUD Operations
# ======================================================================

@router.post(
    "/",
    response_model=PlanExclusionLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link exclusion to plan",
    description="Create a new exclusion link for a plan from the exclusion library"
)
async def create_exclusion_link(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_data: PlanExclusionLinkCreate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    """Create new exclusion link"""
    try:
        exclusion_link = service.create_exclusion_link(
            plan_id=plan_id,
            link_data=link_data,
            created_by=current_user.id
        )
        
        logger.info(f"Created exclusion link {exclusion_link.id} for plan {plan_id}")
        return exclusion_link
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating exclusion link: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create exclusion link")

@router.post(
    "/bulk",
    response_model=List[PlanExclusionLinkResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk link exclusions to plan",
    description="Create multiple exclusion links for a plan at once"
)
async def bulk_create_exclusion_links(
    plan_id: UUID = Path(..., description="Plan ID"),
    bulk_data: BulkExclusionLinkCreate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    """Bulk create exclusion links"""
    try:
        exclusion_links = service.bulk_create_exclusion_links(
            plan_id=plan_id,
            bulk_data=bulk_data,
            created_by=current_user.id
        )
        
        logger.info(f"Bulk created {len(exclusion_links)} exclusion links for plan {plan_id}")
        return exclusion_links
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error bulk creating exclusion links: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to bulk create exclusion links")

@router.get(
    "/",
    response_model=List[PlanExclusionLinkResponse],
    summary="List plan exclusion links",
    description="Get all exclusion links for a plan with optional filters"
)
async def list_exclusion_links(
    plan_id: UUID = Path(..., description="Plan ID"),
    status: Optional[LinkStatus] = Query(None, description="Filter by link status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_mandatory: Optional[bool] = Query(None, description="Filter by mandatory status"),
    application_scope: Optional[ApplicationScope] = Query(None, description="Filter by application scope"),
    override_type: Optional[OverrideType] = Query(None, description="Filter by override type"),
    is_highlighted: Optional[bool] = Query(None, description="Filter by highlighted status"),
    effective_date: Optional[date] = Query(None, description="Filter by effective date"),
    display_category: Optional[str] = Query(None, description="Filter by display category"),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get exclusion links for a plan"""
    try:
        filters = ExclusionLinkSearchFilters(
            status=status,
            is_active=is_active,
            is_mandatory=is_mandatory,
            application_scope=application_scope,
            override_type=override_type,
            is_highlighted=is_highlighted,
            effective_date=effective_date,
            display_category=display_category
        )
        
        exclusion_links = service.get_plan_exclusion_links(plan_id, filters)
        return exclusion_links
        
    except Exception as e:
        logger.error(f"Error listing exclusion links for plan {plan_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve exclusion links")

@router.get(
    "/effective",
    response_model=List[PlanExclusionLinkResponse],
    summary="Get effective exclusion links",
    description="Get all currently effective exclusion links for a plan"
)
async def get_effective_exclusion_links(
    plan_id: UUID = Path(..., description="Plan ID"),
    check_date: Optional[date] = Query(None, description="Date to check (default: today)"),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get effective exclusion links"""
    try:
        return service.get_effective_exclusion_links(plan_id, check_date)
    except Exception as e:
        logger.error(f"Error getting effective exclusion links: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve effective exclusion links")

@router.get(
    "/mandatory",
    response_model=List[PlanExclusionLinkResponse],
    summary="Get mandatory exclusion links",
    description="Get all mandatory exclusion links for a plan"
)
async def get_mandatory_exclusion_links(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get mandatory exclusion links"""
    try:
        return service.get_mandatory_exclusion_links(plan_id)
    except Exception as e:
        logger.error(f"Error getting mandatory exclusion links: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve mandatory exclusion links")

@router.get(
    "/highlighted",
    response_model=List[PlanExclusionLinkResponse],
    summary="Get highlighted exclusion links",
    description="Get all highlighted exclusion links for a plan"
)
async def get_highlighted_exclusion_links(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get highlighted exclusion links"""
    try:
        return service.get_highlighted_exclusion_links(plan_id)
    except Exception as e:
        logger.error(f"Error getting highlighted exclusion links: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve highlighted exclusion links")

@router.get(
    "/coverage/{coverage_id}",
    response_model=List[PlanExclusionLinkResponse],
    summary="Get exclusion links for coverage",
    description="Get exclusion links that apply to a specific coverage"
)
async def get_coverage_exclusion_links(
    plan_id: UUID = Path(..., description="Plan ID"),
    coverage_id: UUID = Path(..., description="Coverage ID"),
    check_date: Optional[date] = Query(None, description="Date to check (default: today)"),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get exclusion links for a coverage"""
    try:
        return service.get_coverage_exclusion_links(plan_id, coverage_id, check_date)
    except Exception as e:
        logger.error(f"Error getting coverage exclusion links: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve coverage exclusion links")

@router.get(
    "/{link_id}",
    response_model=PlanExclusionLinkResponse,
    summary="Get exclusion link details",
    description="Get detailed information about a specific exclusion link"
)
async def get_exclusion_link(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_id: UUID = Path(..., description="Exclusion Link ID"),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get exclusion link by ID"""
    try:
        exclusion_link = service.get_exclusion_link(link_id)
        
        # Verify link belongs to the plan
        if exclusion_link.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion link not found for this plan")
        
        return exclusion_link
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion link not found")
    except Exception as e:
        logger.error(f"Error getting exclusion link {link_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve exclusion link")

@router.put(
    "/{link_id}",
    response_model=PlanExclusionLinkResponse,
    summary="Update exclusion link",
    description="Update exclusion link configuration and overrides"
)
async def update_exclusion_link(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_id: UUID = Path(..., description="Exclusion Link ID"),
    update_data: PlanExclusionLinkUpdate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "edit"))
):
    """Update exclusion link"""
    try:
        # Verify link belongs to the plan
        exclusion_link = service.get_exclusion_link(link_id)
        if exclusion_link.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion link not found for this plan")
        
        updated_link = service.update_exclusion_link(
            link_id=link_id,
            update_data=update_data,
            updated_by=current_user.id
        )
        
        logger.info(f"Updated exclusion link {link_id}")
        return updated_link
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion link not found")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating exclusion link {link_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update exclusion link")

@router.delete(
    "/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete exclusion link",
    description="Remove an exclusion link from a plan"
)
async def delete_exclusion_link(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_id: UUID = Path(..., description="Exclusion Link ID"),
    current_user: User = Depends(get_current_user),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "delete"))
):
    """Delete exclusion link"""
    try:
        # Verify link belongs to the plan
        exclusion_link = service.get_exclusion_link(link_id)
        if exclusion_link.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion link not found for this plan")
        
        success = service.delete_exclusion_link(link_id)
        if success:
            logger.info(f"Deleted exclusion link {link_id}")
            return None
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion link not found")
    except Exception as e:
        logger.error(f"Error deleting exclusion link {link_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete exclusion link")

# ======================================================================
# Application Checking
# ======================================================================

@router.post(
    "/{link_id}/check-coverage",
    response_model=Dict[str, Any],
    summary="Check coverage application",
    description="Check if exclusion link applies to a specific coverage"
)
async def check_coverage_application(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_id: UUID = Path(..., description="Exclusion Link ID"),
    coverage_check: CoverageApplicationCheck = ...,
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Check coverage application"""
    try:
        # Verify link belongs to the plan
        exclusion_link = service.get_exclusion_link(link_id)
        if exclusion_link.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion link not found for this plan")
        
        result = service.check_coverage_application(link_id, coverage_check)
        
        return create_response(
            data=result,
            message="Coverage application checked successfully"
        )
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion link not found")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error checking coverage application: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check coverage application")

@router.post(
    "/{link_id}/check-effectiveness",
    response_model=Dict[str, Any],
    summary="Check link effectiveness",
    description="Check if exclusion link is effective for a given date"
)
async def check_link_effectiveness(
    plan_id: UUID = Path(..., description="Plan ID"),
    link_id: UUID = Path(..., description="Exclusion Link ID"),
    effectiveness_check: ExclusionLinkEffectivenessCheck = ...,
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Check link effectiveness"""
    try:
        # Verify link belongs to the plan
        exclusion_link = service.get_exclusion_link(link_id)
        if exclusion_link.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion link not found for this plan")
        
        result = service.check_link_effectiveness(link_id, effectiveness_check)
        
        return create_response(
            data=result,
            message="Link effectiveness checked successfully"
        )
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion link not found")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error checking link effectiveness: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check link effectiveness")

# ======================================================================
# Analytics and Summary
# ======================================================================

@router.get(
    "/summary",
    response_model=ExclusionLinkSummary,
    summary="Get exclusion links summary",
    description="Get summary statistics for exclusion links in a plan"
)
async def get_exclusion_link_summary(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get exclusion link summary"""
    try:
        return service.get_exclusion_link_summary(plan_id)
    except Exception as e:
        logger.error(f"Error getting exclusion link summary: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve exclusion link summary")

# ======================================================================
# Validation
# ======================================================================

@router.post(
    "/validate-compatibility",
    response_model=Dict[str, Any],
    summary="Validate exclusion compatibility",
    description="Validate if exclusions are compatible with the plan"
)
async def validate_exclusion_compatibility(
    plan_id: UUID = Path(..., description="Plan ID"),
    exclusion_ids: List[UUID] = Query(..., description="Exclusion IDs to validate"),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Validate exclusion compatibility"""
    try:
        validation_result = service.validate_exclusion_compatibility(plan_id, exclusion_ids)
        
        return create_response(
            data=validation_result,
            message="Exclusion compatibility validation completed"
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error validating exclusion compatibility: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to validate exclusion compatibility")

# ======================================================================
# Export and Documentation
# ======================================================================

@router.get(
    "/export",
    response_model=Dict[str, Any],
    summary="Export exclusion links",
    description="Export exclusion links for documentation or reporting"
)
async def export_exclusion_links(
    plan_id: UUID = Path(..., description="Plan ID"),
    format: str = Query("json", regex="^(json|summary)$", description="Export format"),
    include_overrides: bool = Query(True, description="Include override details"),
    service: PlanExclusionLinkService = Depends(get_exclusion_link_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Export exclusion links"""
    try:
        exclusion_links = service.get_plan_exclusion_links(plan_id)
        
        export_data = {
            'plan_id': str(plan_id),
            'export_timestamp': date.today().isoformat(),
            'total_links': len(exclusion_links),
            'exclusion_links': []
        }
        
        for link in exclusion_links:
            link_data = {
                'id': str(link.id),
                'exclusion_id': str(link.exclusion_id),
                'status': link.status,
                'is_active': link.is_active,
                'is_mandatory': link.is_mandatory,
                'is_highlighted': link.is_highlighted,
                'application_scope': link.application_scope,
                'display_order': link.display_order,
                'is_effective': link.is_effective,
                'effective_date': link.effective_date.isoformat() if link.effective_date else None,
                'expiry_date': link.expiry_date.isoformat() if link.expiry_date else None
            }
            
            if include_overrides:
                link_data.update({
                    'override_type': link.override_type,
                    'override_text': link.override_text,
                    'override_parameters': link.override_parameters,
                    'applicable_coverages': [str(c) for c in (link.applicable_coverages or [])],
                    'display_category': link.display_category
                })
            
            export_data['exclusion_links'].append(link_data)
        
        return create_response(
            data=export_data,
            message=f"Exclusion links exported successfully ({format} format)"
        )
        
    except Exception as e:
        logger.error(f"Error exporting exclusion links: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export exclusion links")
