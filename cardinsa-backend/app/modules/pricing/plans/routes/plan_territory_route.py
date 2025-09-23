# ======================================================================
# Plan Territory Routes - Complete FastAPI Implementation
# app/modules/plans/routes/plan_territory_routes.py
# ======================================================================

"""
Plan Territory Routes

FastAPI routes for Plan Territory management including CRUD operations,
premium calculations, analytics, and coverage validation.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_permission,
    require_permission_scoped
)
from app.core.exceptions import (
    EntityNotFoundError,
    ValidationError,
    BusinessLogicError,
    DatabaseOperationError
)
from app.modules.auth.models.user_model import User
from app.modules.pricing.plans.repositories.plan_territory_repository import PlanTerritoryRepository
from app.modules.pricing.plans.services.plan_territory_service import PlanTerritoryService
from app.modules.pricing.plans.schemas.plan_territory_schema import (
    PlanTerritoryCreate,
    PlanTerritoryUpdate,
    PlanTerritoryResponse,
    TerritoryPremiumCalculation,
    TerritoryAnalytics
)
from app.modules.pricing.plans.models.plan_territory_model import TerritoryType, TerritoryStatus
from app.core.responses import create_response
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/plans/{plan_id}/territories",
    tags=["Plan Territories"],
    responses={404: {"description": "Not found"}}
)

# Dependency to get service
def get_territory_service(db: Session = Depends(get_db)) -> PlanTerritoryService:
    """Get territory service instance"""
    repository = PlanTerritoryRepository(db)
    return PlanTerritoryService(repository)

# ======================================================================
# CRUD Operations
# ======================================================================

@router.post(
    "/",
    response_model=PlanTerritoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new territory",
    description="Create a new territory for a plan with pricing and geographic definitions"
)
async def create_territory(
    plan_id: UUID = Path(..., description="Plan ID"),
    territory_data: PlanTerritoryCreate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    """Create new territory for a plan"""
    try:
        territory = service.create_territory(
            plan_id=plan_id,
            territory_data=territory_data,
            created_by=current_user.id
        )
        
        logger.info(f"Created territory {territory.territory_code} for plan {plan_id} by user {current_user.id}")
        return territory
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating territory: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create territory"
        )

@router.get(
    "/",
    response_model=List[PlanTerritoryResponse],
    summary="List plan territories",
    description="Get all territories for a plan with optional filters"
)
async def list_territories(
    plan_id: UUID = Path(..., description="Plan ID"),
    territory_type: Optional[TerritoryType] = Query(None, description="Filter by territory type"),
    status: Optional[TerritoryStatus] = Query(None, description="Filter by territory status"),
    effective_date: Optional[date] = Query(None, description="Filter by effective date"),
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get territories for a plan"""
    try:
        territories = service.get_territories_by_plan(
            plan_id=plan_id,
            territory_type=territory_type,
            status=status,
            effective_date=effective_date
        )
        
        return territories
        
    except Exception as e:
        logger.error(f"Error listing territories for plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve territories"
        )

@router.get(
    "/{territory_id}",
    response_model=PlanTerritoryResponse,
    summary="Get territory details",
    description="Get detailed information about a specific territory"
)
async def get_territory(
    plan_id: UUID = Path(..., description="Plan ID"),
    territory_id: UUID = Path(..., description="Territory ID"),
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get territory by ID"""
    try:
        territory = service.get_territory(territory_id)
        
        # Verify territory belongs to the plan
        if territory.plan_id != plan_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Territory not found for this plan"
            )
        
        return territory
        
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territory not found"
        )
    except Exception as e:
        logger.error(f"Error getting territory {territory_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve territory"
        )

@router.put(
    "/{territory_id}",
    response_model=PlanTerritoryResponse,
    summary="Update territory",
    description="Update territory information including pricing and geographic data"
)
async def update_territory(
    plan_id: UUID = Path(..., description="Plan ID"),
    territory_id: UUID = Path(..., description="Territory ID"),
    update_data: PlanTerritoryUpdate = ...,
    current_user: User = Depends(get_current_user),
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "edit"))
):
    """Update territory"""
    try:
        # Verify territory belongs to the plan
        territory = service.get_territory(territory_id)
        if territory.plan_id != plan_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Territory not found for this plan"
            )
        
        updated_territory = service.update_territory(
            territory_id=territory_id,
            update_data=update_data,
            updated_by=current_user.id
        )
        
        logger.info(f"Updated territory {territory_id} by user {current_user.id}")
        return updated_territory
        
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territory not found"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating territory {territory_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update territory"
        )

@router.delete(
    "/{territory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete territory",
    description="Soft delete a territory (marks as inactive)"
)
async def delete_territory(
    plan_id: UUID = Path(..., description="Plan ID"),
    territory_id: UUID = Path(..., description="Territory ID"),
    current_user: User = Depends(get_current_user),
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "delete"))
):
    """Delete territory"""
    try:
        # Verify territory belongs to the plan
        territory = service.get_territory(territory_id)
        if territory.plan_id != plan_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Territory not found for this plan"
            )
        
        success = service.delete_territory(territory_id)
        if success:
            logger.info(f"Deleted territory {territory_id} by user {current_user.id}")
            return None
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete territory"
            )
        
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territory not found"
        )
    except Exception as e:
        logger.error(f"Error deleting territory {territory_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete territory"
        )

# ======================================================================
# Premium Calculations
# ======================================================================

@router.post(
    "/calculate-premium",
    response_model=Dict[str, Any],
    summary="Calculate territory-adjusted premium",
    description="Calculate premium adjustments based on territory factors and risk characteristics"
)
async def calculate_territory_premium(
    plan_id: UUID = Path(..., description="Plan ID"),
    calculation_request: TerritoryPremiumCalculation = ...,
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Calculate territory-adjusted premium"""
    try:
        calculation_result = service.calculate_premium(
            plan_id=plan_id,
            calculation_request=calculation_request
        )
        
        return create_response(
            data=calculation_result,
            message="Premium calculated successfully"
        )
        
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error calculating premium for plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate premium"
        )

@router.post(
    "/bulk-calculate",
    response_model=Dict[str, Any],
    summary="Bulk premium calculations",
    description="Calculate premiums for multiple territories and coverage combinations"
)
async def bulk_calculate_premiums(
    plan_id: UUID = Path(..., description="Plan ID"),
    calculations: List[TerritoryPremiumCalculation] = ...,
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Bulk calculate territory premiums"""
    try:
        results = []
        errors = []
        
        for i, calc_request in enumerate(calculations):
            try:
                result = service.calculate_premium(
                    plan_id=plan_id,
                    calculation_request=calc_request
                )
                results.append({
                    'index': i,
                    'territory_code': calc_request.territory_code,
                    'calculation': result
                })
            except Exception as e:
                errors.append({
                    'index': i,
                    'territory_code': calc_request.territory_code,
                    'error': str(e)
                })
        
        return create_response(
            data={
                'successful_calculations': len(results),
                'failed_calculations': len(errors),
                'results': results,
                'errors': errors
            },
            message=f"Bulk calculation completed: {len(results)} successful, {len(errors)} failed"
        )
        
    except Exception as e:
        logger.error(f"Error in bulk calculation for plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform bulk calculations"
        )

# ======================================================================
# Analytics and Reporting
# ======================================================================

@router.get(
    "/{territory_id}/analytics",
    response_model=TerritoryAnalytics,
    summary="Get territory analytics",
    description="Get detailed analytics and performance metrics for a territory"
)
async def get_territory_analytics(
    plan_id: UUID = Path(..., description="Plan ID"),
    territory_id: UUID = Path(..., description="Territory ID"),
    date_from: Optional[date] = Query(None, description="Analytics start date"),
    date_to: Optional[date] = Query(None, description="Analytics end date"),
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get territory analytics"""
    try:
        # Verify territory belongs to the plan
        territory = service.get_territory(territory_id)
        if territory.plan_id != plan_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Territory not found for this plan"
            )
        
        analytics = service.get_territory_analytics(
            territory_id=territory_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return analytics
        
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territory not found"
        )
    except Exception as e:
        logger.error(f"Error getting analytics for territory {territory_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )

@router.get(
    "/analytics/summary",
    response_model=Dict[str, Any],
    summary="Get plan territory analytics summary",
    description="Get aggregated analytics for all territories in a plan"
)
async def get_plan_territory_analytics_summary(
    plan_id: UUID = Path(..., description="Plan ID"),
    date_from: Optional[date] = Query(None, description="Analytics start date"),
    date_to: Optional[date] = Query(None, description="Analytics end date"),
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get aggregated territory analytics for a plan"""
    try:
        territories = service.get_territories_by_plan(plan_id)
        
        total_territories = len(territories)
        active_territories = len([t for t in territories if t.status == TerritoryStatus.ACTIVE])
        
        # Aggregate analytics (simplified version)
        summary = {
            'plan_id': str(plan_id),
            'total_territories': total_territories,
            'active_territories': active_territories,
            'inactive_territories': total_territories - active_territories,
            'territory_types': {},
            'risk_distribution': {},
            'regulatory_jurisdictions': {},
            'date_range': {
                'from': date_from.isoformat() if date_from else None,
                'to': date_to.isoformat() if date_to else None
            }
        }
        
        # Count by territory type
        for territory in territories:
            territory_type = territory.territory_type.value
            summary['territory_types'][territory_type] = summary['territory_types'].get(territory_type, 0) + 1
            
            # Count by risk level
            risk_level = territory.risk_level
            summary['risk_distribution'][risk_level] = summary['risk_distribution'].get(risk_level, 0) + 1
            
            # Count by regulatory jurisdiction
            if territory.regulatory_jurisdiction:
                jurisdiction = territory.regulatory_jurisdiction
                summary['regulatory_jurisdictions'][jurisdiction] = summary['regulatory_jurisdictions'].get(jurisdiction, 0) + 1
        
        return create_response(
            data=summary,
            message="Territory analytics summary retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting territory analytics summary for plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics summary"
        )

# ======================================================================
# Coverage Validation
# ======================================================================

@router.post(
    "/validate-coverage",
    response_model=Dict[str, Any],
    summary="Validate territory coverage",
    description="Validate if postal codes or geographic areas are covered by plan territories"
)
async def validate_territory_coverage(
    plan_id: UUID = Path(..., description="Plan ID"),
    postal_codes: List[str] = Query(..., description="List of postal codes to validate"),
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Validate territory coverage for postal codes"""
    try:
        if not postal_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one postal code must be provided"
            )
        
        if len(postal_codes) > 1000:  # Limit for performance
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 1000 postal codes can be validated at once"
            )
        
        coverage_result = service.validate_territory_coverage(
            plan_id=plan_id,
            postal_codes=postal_codes
        )
        
        return create_response(
            data=coverage_result,
            message="Coverage validation completed successfully"
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error validating coverage for plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate coverage"
        )

# ======================================================================
# Utility Endpoints
# ======================================================================

@router.get(
    "/by-jurisdiction/{jurisdiction}",
    response_model=List[PlanTerritoryResponse],
    summary="Get territories by jurisdiction",
    description="Get all active territories for a specific regulatory jurisdiction"
)
async def get_territories_by_jurisdiction(
    plan_id: UUID = Path(..., description="Plan ID"),
    jurisdiction: str = Path(..., description="Regulatory jurisdiction"),
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Get territories by regulatory jurisdiction"""
    try:
        territories = service.get_active_territories_by_jurisdiction(jurisdiction)
        
        # Filter by plan_id
        plan_territories = [t for t in territories if t.plan_id == plan_id]
        
        return plan_territories
        
    except Exception as e:
        logger.error(f"Error getting territories by jurisdiction {jurisdiction}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve territories"
        )

@router.get(
    "/export",
    response_model=Dict[str, Any],
    summary="Export territory data",
    description="Export territory configuration and analytics data for reporting"
)
async def export_territory_data(
    plan_id: UUID = Path(..., description="Plan ID"),
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    include_analytics: bool = Query(False, description="Include analytics data"),
    service: PlanTerritoryService = Depends(get_territory_service),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    """Export territory data"""
    try:
        territories = service.get_territories_by_plan(plan_id)
        
        export_data = {
            'plan_id': str(plan_id),
            'export_timestamp': date.today().isoformat(),
            'territory_count': len(territories),
            'territories': []
        }
        
        for territory in territories:
            territory_data = territory.dict()
            
            if include_analytics:
                try:
                    analytics = service.get_territory_analytics(territory.id)
                    territory_data['analytics'] = analytics.dict()
                except:
                    territory_data['analytics'] = None
            
            export_data['territories'].append(territory_data)
        
        return create_response(
            data=export_data,
            message=f"Territory data exported successfully ({format} format)"
        )
        
    except Exception as e:
        logger.error(f"Error exporting territory data for plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export territory data"
        )



# ======================================================================
# End of Plan Territory Routes
# ======================================================================