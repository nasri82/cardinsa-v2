# app/modules/pricing/plans/routes/plan_exclusion_routes.py
"""
Plan Exclusion Routes

FastAPI routes for Plan Exclusion management.
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
from app.modules.pricing.plans.repositories.plan_exclusion_repository import PlanExclusionRepository
from app.modules.pricing.plans.services.plan_exclusion_service import PlanExclusionService
from app.modules.pricing.plans.schemas.plan_exclusion_schema import (
    PlanExclusionCreate,
    PlanExclusionUpdate,
    PlanExclusionResponse,
    BulkExclusionCreate,
    ExclusionSummary,
    ExclusionCheckRequest,
    ExclusionCheckResponse,
    ExclusionSearchFilters,
    ExclusionType,
    ExclusionCategory,
    ExclusionSeverity
)
from app.core.responses import create_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/plans/{plan_id}/exclusions",
    tags=["Plan Exclusions"],
    responses={404: {"description": "Not found"}}
)

def get_exclusion_service(db: Session = Depends(get_db)) -> PlanExclusionService:
    """Get exclusion service instance"""
    repository = PlanExclusionRepository(db)
    return PlanExclusionService(repository)

# ======================================================================
# CRUD Operations
# ======================================================================

@router.post(
    "/",
    response_model=PlanExclusionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create plan exclusion",
    description="Create a new exclusion for a plan"
)
async def create_exclusion(
    plan_id: UUID = Path(..., description="Plan ID"),
    exclusion_data: PlanExclusionCreate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    """Create new exclusion"""
    try:
        exclusion = service.create_exclusion(
            plan_id=plan_id,
            exclusion_data=exclusion_data,
            created_by=current_user.id
        )
        
        logger.info(f"Created exclusion {exclusion.id} for plan {plan_id}")
        return exclusion
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating exclusion: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create exclusion")

@router.post(
    "/bulk",
    response_model=List[PlanExclusionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create exclusions",
    description="Create multiple exclusions for a plan at once"
)
async def bulk_create_exclusions(
    plan_id: UUID = Path(..., description="Plan ID"),
    bulk_data: BulkExclusionCreate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    """Bulk create exclusions"""
    try:
        exclusions = service.bulk_create_exclusions(
            plan_id=plan_id,
            bulk_data=bulk_data,
            created_by=current_user.id
        )
        
        logger.info(f"Bulk created {len(exclusions)} exclusions for plan {plan_id}")
        return exclusions
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error bulk creating exclusions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to bulk create exclusions")

@router.get(
    "/",
    response_model=List[PlanExclusionResponse],
    summary="List plan exclusions",
    description="Get all exclusions for a plan with optional filters"
)
async def list_exclusions(
    plan_id: UUID = Path(..., description="Plan ID"),
    exclusion_type: Optional[ExclusionType] = Query(None, description="Filter by exclusion type"),
    exclusion_category: Optional[ExclusionCategory] = Query(None, description="Filter by category"),
    exclusion_severity: Optional[ExclusionSeverity] = Query(None, description="Filter by severity"),
    is_highlighted: Optional[bool] = Query(None, description="Filter by highlighted status"),
    effective_date: Optional[date] = Query(None, description="Filter by effective date"),
    text_search: Optional[str] = Query(None, description="Search in exclusion text"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get exclusions for a plan"""
    try:
        filters = ExclusionSearchFilters(
            exclusion_type=exclusion_type,
            exclusion_category=exclusion_category,
            exclusion_severity=exclusion_severity,
            is_highlighted=is_highlighted,
            effective_date=effective_date,
            text_search=text_search,
            tags=tags.split(',') if tags else None
        )
        
        exclusions = service.get_plan_exclusions(plan_id, filters)
        return exclusions
        
    except Exception as e:
        logger.error(f"Error listing exclusions for plan {plan_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve exclusions")

@router.get(
    "/active",
    response_model=List[PlanExclusionResponse],
    summary="Get active exclusions",
    description="Get all currently active exclusions for a plan"
)
async def get_active_exclusions(
    plan_id: UUID = Path(..., description="Plan ID"),
    check_date: Optional[date] = Query(None, description="Date to check (default: today)"),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get active exclusions"""
    try:
        return service.get_active_exclusions(plan_id, check_date)
    except Exception as e:
        logger.error(f"Error getting active exclusions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve active exclusions")

@router.get(
    "/highlighted",
    response_model=List[PlanExclusionResponse],
    summary="Get highlighted exclusions",
    description="Get all highlighted exclusions for a plan"
)
async def get_highlighted_exclusions(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get highlighted exclusions"""
    try:
        return service.get_highlighted_exclusions(plan_id)
    except Exception as e:
        logger.error(f"Error getting highlighted exclusions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve highlighted exclusions")

@router.get(
    "/waiverable",
    response_model=List[PlanExclusionResponse],
    summary="Get waiverable exclusions",
    description="Get all exclusions that can be waived"
)
async def get_waiverable_exclusions(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get waiverable exclusions"""
    try:
        return service.get_waiverable_exclusions(plan_id)
    except Exception as e:
        logger.error(f"Error getting waiverable exclusions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve waiverable exclusions")

@router.get(
    "/{exclusion_id}",
    response_model=PlanExclusionResponse,
    summary="Get exclusion details",
    description="Get detailed information about a specific exclusion"
)
async def get_exclusion(
    plan_id: UUID = Path(..., description="Plan ID"),
    exclusion_id: UUID = Path(..., description="Exclusion ID"),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get exclusion by ID"""
    try:
        exclusion = service.get_exclusion(exclusion_id)
        
        # Verify exclusion belongs to the plan
        if exclusion.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion not found for this plan")
        
        return exclusion
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion not found")
    except Exception as e:
        logger.error(f"Error getting exclusion {exclusion_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve exclusion")

@router.put(
    "/{exclusion_id}",
    response_model=PlanExclusionResponse,
    summary="Update exclusion",
    description="Update exclusion details"
)
async def update_exclusion(
    plan_id: UUID = Path(..., description="Plan ID"),
    exclusion_id: UUID = Path(..., description="Exclusion ID"),
    update_data: PlanExclusionUpdate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "edit"))
):
    """Update exclusion"""
    try:
        # Verify exclusion belongs to the plan
        exclusion = service.get_exclusion(exclusion_id)
        if exclusion.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion not found for this plan")
        
        updated_exclusion = service.update_exclusion(
            exclusion_id=exclusion_id,
            update_data=update_data,
            updated_by=current_user.id
        )
        
        logger.info(f"Updated exclusion {exclusion_id}")
        return updated_exclusion
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion not found")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating exclusion {exclusion_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update exclusion")

@router.delete(
    "/{exclusion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete exclusion",
    description="Remove an exclusion from a plan"
)
async def delete_exclusion(
    plan_id: UUID = Path(..., description="Plan ID"),
    exclusion_id: UUID = Path(..., description="Exclusion ID"),
    current_user: User = Depends(get_current_user),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "delete"))
):
    """Delete exclusion"""
    try:
        # Verify exclusion belongs to the plan
        exclusion = service.get_exclusion(exclusion_id)
        if exclusion.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion not found for this plan")
        
        success = service.delete_exclusion(exclusion_id)
        if success:
            logger.info(f"Deleted exclusion {exclusion_id}")
            return None
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion not found")
    except Exception as e:
        logger.error(f"Error deleting exclusion {exclusion_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete exclusion")

# ======================================================================
# Exclusion Checking
# ======================================================================

@router.post(
    "/{exclusion_id}/check",
    response_model=ExclusionCheckResponse,
    summary="Check if exclusion applies",
    description="Check if an exclusion applies to a given context"
)
async def check_exclusion(
    plan_id: UUID = Path(..., description="Plan ID"),
    exclusion_id: UUID = Path(..., description="Exclusion ID"),
    check_request: ExclusionCheckRequest = ...,
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Check if exclusion applies"""
    try:
        # Verify exclusion belongs to the plan
        exclusion = service.get_exclusion(exclusion_id)
        if exclusion.plan_id != plan_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion not found for this plan")
        
        result = service.check_exclusion_applies(exclusion_id, check_request)
        return result
        
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion not found")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error checking exclusion: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check exclusion")

@router.post(
    "/check-medical-codes",
    response_model=Dict[str, Any],
    summary="Check exclusions for medical codes",
    description="Check exclusions for specific CPT or ICD-10 codes"
)
async def check_medical_code_exclusions(
    plan_id: UUID = Path(..., description="Plan ID"),
    cpt_codes: Optional[List[UUID]] = Query(None, description="CPT code IDs"),
    icd10_codes: Optional[List[UUID]] = Query(None, description="ICD-10 code IDs"),
    context: Optional[Dict[str, Any]] = None,
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Check medical code exclusions"""
    try:
        if not cpt_codes and not icd10_codes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one CPT or ICD-10 code must be provided")
        
        result = service.check_medical_code_exclusions(
            plan_id=plan_id,
            cpt_codes=cpt_codes,
            icd10_codes=icd10_codes,
            context=context or {}
        )
        
        return create_response(
            data=result,
            message="Medical code exclusions checked successfully"
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error checking medical code exclusions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check medical code exclusions")

# ======================================================================
# Search and Analytics
# ======================================================================

@router.get(
    "/search",
    response_model=List[PlanExclusionResponse],
    summary="Search exclusions",
    description="Search exclusions by text"
)
async def search_exclusions(
    plan_id: UUID = Path(..., description="Plan ID"),
    q: str = Query(..., description="Search term", min_length=3),
    limit: int = Query(50, description="Maximum results", ge=1, le=100),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Search exclusions"""
    try:
        exclusions = service.search_exclusions(plan_id, q, limit)
        return exclusions
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching exclusions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search exclusions")

@router.get(
    "/summary",
    response_model=ExclusionSummary,
    summary="Get exclusions summary",
    description="Get summary statistics for exclusions in a plan"
)
async def get_exclusion_summary(
    plan_id: UUID = Path(..., description="Plan ID"),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get exclusion summary"""
    try:
        return service.get_exclusion_summary(plan_id)
    except Exception as e:
        logger.error(f"Error getting exclusion summary: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve exclusion summary")

# ======================================================================
# Export and Documentation
# ======================================================================

@router.get(
    "/export",
    response_model=Dict[str, Any],
    summary="Export exclusions",
    description="Export exclusions for documentation or reporting"
)
async def export_exclusions(
    plan_id: UUID = Path(..., description="Plan ID"),
    format: str = Query("json", regex="^(json|text)$", description="Export format"),
    language: str = Query("en", regex="^(en|ar)$", description="Language preference"),
    service: PlanExclusionService = Depends(get_exclusion_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Export exclusions"""
    try:
        exclusions = service.get_plan_exclusions(plan_id)
        
        export_data = {
            'plan_id': str(plan_id),
            'export_timestamp': date.today().isoformat(),
            'language': language,
            'total_exclusions': len(exclusions),
            'exclusions': []
        }
        
        for exclusion in exclusions:
            exclusion_data = {
                'id': str(exclusion.id),
                'type': exclusion.exclusion_type,
                'category': exclusion.exclusion_category,
                'severity': exclusion.exclusion_severity,
                'text': exclusion.exclusion_text_ar if language == 'ar' and exclusion.exclusion_text_ar else exclusion.exclusion_text,
                'member_text': exclusion.member_facing_text_ar if language == 'ar' and exclusion.member_facing_text_ar else exclusion.member_facing_text,
                'is_highlighted': exclusion.is_highlighted,
                'is_waiverable': exclusion.is_waiverable,
                'is_temporary': exclusion.is_temporary,
                'effective_date': exclusion.effective_date.isoformat() if exclusion.effective_date else None,
                'expiry_date': exclusion.expiry_date.isoformat() if exclusion.expiry_date else None
            }
            export_data['exclusions'].append(exclusion_data)
        
        return create_response(
            data=export_data,
            message=f"Exclusions exported successfully ({format} format, {language} language)"
        )
        
    except Exception as e:
        logger.error(f"Error exporting exclusions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export exclusions")
