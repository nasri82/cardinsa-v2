"""
Benefit Type Routes - Advanced Cost-Sharing & Member Cost Modeling API
======================================================================

Enterprise-grade REST API for benefit type management with sophisticated
cost-sharing calculations, member cost modeling, and benefit analysis.

Author: Assistant
Created: 2024
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from decimal import Decimal
from functools import wraps
import hashlib
import asyncio

# Core imports - FIXED
from app.core.database import get_db
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.core.dependencies import get_current_user, require_role
from app.core.logging import get_logger
from app.core.responses import success_response, error_response
from app.utils.pagination import PaginatedResponse, PaginationParams
from app.core.cache import cache_set, cache_get

# Service imports
from app.modules.pricing.benefits.services.benefit_type_service import BenefitTypeService
from app.modules.pricing.benefits.models.benefit_type_model import BenefitType, CostSharingType, NetworkTier

# Schema imports
from app.modules.pricing.benefits.schemas.benefit_type_schema import (
    BenefitTypeCreate,
    BenefitTypeUpdate,
    BenefitTypeResponse,
    BenefitTypeWithDetails,
    CostSharingCalculation,
    MemberCostEstimate,
    BenefitComparison,
    AnnualCostProjection,
    CostOptimizationRecommendation,
    BenefitUsageScenario,
    CostSharingConfiguration,
    NetworkCostAnalysis,
    BenefitSearchFilter,
    BulkBenefitTypeOperation
)

logger = get_logger(__name__)

# =====================================================================
# CACHE DECORATOR AND HELPERS
# =====================================================================

def cache_response(ttl: int = 3600, key_prefix: str = "route_cache"):
    """
    Decorator to cache FastAPI route responses.
    
    Args:
        ttl: Time to live in seconds (default 1 hour)
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and first relevant argument
            first_arg = str(args[1]) if len(args) > 1 else "no_args"
            cache_key = f"{key_prefix}:{func.__name__}:{first_arg}"
            
            # Try to get from cache
            cached_result = await cache_get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            # Convert Pydantic models to dict for caching
            if hasattr(result, 'dict'):
                cache_data = result.dict()
            elif hasattr(result, 'model_dump'):
                cache_data = result.model_dump() 
            else:
                cache_data = result
                
            await cache_set(cache_key, cache_data, ttl)
            return result
            
        return wrapper
    return decorator


def require_permissions(user, required_permissions: List[str]):
    """Check if user has required permissions"""
    if not hasattr(user, 'has_any') or not user.has_any(required_permissions):
        raise HTTPException(status_code=403, detail="Insufficient permissions")


# Initialize router
router = APIRouter(
    prefix="/api/v1/benefit-types",
    tags=["Benefit Types"],
    responses={
        404: {"description": "Benefit type not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# =====================================================================
# CORE CRUD OPERATIONS
# =====================================================================

@router.post(
    "/",
    response_model=BenefitTypeResponse,
    status_code=201,
    summary="Create Benefit Type",
    description="Create a new benefit type with cost-sharing configuration"
)
async def create_benefit_type(
    benefit_type_data: BenefitTypeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new benefit type"""
    try:
        if not current_user.has_any(["admin", "benefit_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitTypeService(db)
        benefit_type = await service.create_benefit_type(benefit_type_data.dict())
        
        logger.info(
            f"Benefit type created by {current_user.id}: {benefit_type.type_name}",
            extra={"benefit_type_id": str(benefit_type.id), "user_id": str(current_user.id)}
        )
        
        return BenefitTypeResponse.model_validate(benefit_type)
        
    except ValidationError as e:
        logger.error(f"Benefit type creation validation failed: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Benefit type creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create benefit type")


@router.get(
    "/{benefit_type_id}",
    response_model=BenefitTypeResponse,
    summary="Get Benefit Type",
    description="Retrieve a specific benefit type by ID"
)
async def get_benefit_type(
    benefit_type_id: str = Path(..., description="Benefit type ID"),
    include_details: bool = Query(False, description="Include detailed configuration"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific benefit type"""
    try:
        service = BenefitTypeService(db)
        
        if include_details:
            benefit_type = await service.get_benefit_type_with_details(benefit_type_id)
            if not benefit_type:
                raise HTTPException(status_code=404, detail="Benefit type not found")
            return BenefitTypeWithDetails.model_validate(benefit_type)
        else:
            benefit_type = await service.get_by_id(benefit_type_id)
            if not benefit_type:
                raise HTTPException(status_code=404, detail="Benefit type not found")
            return BenefitTypeResponse.model_validate(benefit_type)
            
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit type not found")
    except Exception as e:
        logger.error(f"Failed to retrieve benefit type {benefit_type_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve benefit type")


@router.put(
    "/{benefit_type_id}",
    response_model=BenefitTypeResponse,
    summary="Update Benefit Type",
    description="Update an existing benefit type"
)
async def update_benefit_type(
    benefit_type_id: str = Path(..., description="Benefit type ID"),
    benefit_type_data: BenefitTypeUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing benefit type"""
    try:
        if not current_user.has_any(["admin", "benefit_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitTypeService(db)
        benefit_type = await service.update_benefit_type(
            benefit_type_id, 
            benefit_type_data.dict(exclude_unset=True)
        )
        
        logger.info(
            f"Benefit type updated by {current_user.id}: {benefit_type.type_name}",
            extra={"benefit_type_id": str(benefit_type.id), "user_id": str(current_user.id)}
        )
        
        return BenefitTypeResponse.model_validate(benefit_type)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit type not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Benefit type update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update benefit type")


@router.delete(
    "/{benefit_type_id}",
    status_code=204,
    summary="Delete Benefit Type",
    description="Delete a benefit type and handle dependencies"
)
async def delete_benefit_type(
    benefit_type_id: str = Path(..., description="Benefit type ID"),
    force: bool = Query(False, description="Force delete with dependencies"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a benefit type"""
    try:
        if not current_user.has_any(["admin"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitTypeService(db)
        await service.delete_benefit_type(benefit_type_id, force=force)
        
        logger.info(
            f"Benefit type deleted by {current_user.id}: {benefit_type_id}",
            extra={"benefit_type_id": benefit_type_id, "user_id": str(current_user.id)}
        )
        
        return JSONResponse(status_code=204, content=None)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit type not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Benefit type deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete benefit type")

# =====================================================================
# COST-SHARING CALCULATIONS
# =====================================================================

@router.post(
    "/{benefit_type_id}/calculate-cost-sharing",
    response_model=CostSharingCalculation,
    summary="Calculate Cost-Sharing",
    description="Calculate member cost-sharing for a specific benefit type and service"
)
async def calculate_cost_sharing(
    benefit_type_id: str = Path(..., description="Benefit type ID"),
    service_amount: Decimal = Body(..., description="Service amount"),
    network_tier: NetworkTier = Body(..., description="Provider network tier"),
    member_id: Optional[str] = Body(None, description="Member ID for personalized calculation"),
    service_date: Optional[date] = Body(None, description="Service date"),
    accumulator_amounts: Optional[Dict[str, Decimal]] = Body(None, description="Current accumulator amounts"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate cost-sharing for a service"""
    try:
        service = BenefitTypeService(db)
        calculation = await service.calculate_cost_sharing(
            benefit_type_id=benefit_type_id,
            service_amount=service_amount,
            network_tier=network_tier,
            member_id=member_id,
            service_date=service_date or date.today(),
            accumulator_amounts=accumulator_amounts or {}
        )
        
        logger.info(
            f"Cost-sharing calculated for benefit type {benefit_type_id}: ${calculation.member_cost}",
            extra={
                "benefit_type_id": benefit_type_id,
                "service_amount": float(service_amount),
                "member_cost": float(calculation.member_cost)
            }
        )
        
        return calculation
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit type not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Cost-sharing calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Cost-sharing calculation failed")


@router.post(
    "/{benefit_type_id}/estimate-member-cost",
    response_model=MemberCostEstimate,
    summary="Estimate Member Cost",
    description="Estimate total member cost for multiple services"
)
async def estimate_member_cost(
    benefit_type_id: str = Path(..., description="Benefit type ID"),
    services: List[Dict[str, Any]] = Body(..., description="List of services to estimate"),
    member_id: Optional[str] = Body(None, description="Member ID for personalized estimate"),
    plan_year: Optional[int] = Body(None, description="Plan year for calculations"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Estimate member cost for multiple services"""
    try:
        service = BenefitTypeService(db)
        estimate = await service.estimate_member_cost(
            benefit_type_id=benefit_type_id,
            services=services,
            member_id=member_id,
            plan_year=plan_year or datetime.now().year
        )
        
        logger.info(
            f"Member cost estimated for benefit type {benefit_type_id}: ${estimate.total_estimated_cost}",
            extra={
                "benefit_type_id": benefit_type_id,
                "service_count": len(services),
                "total_cost": float(estimate.total_estimated_cost)
            }
        )
        
        return estimate
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit type not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Member cost estimation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Member cost estimation failed")


@router.get(
    "/{benefit_type_id}/cost-sharing-configuration",
    response_model=CostSharingConfiguration,
    summary="Get Cost-Sharing Configuration",
    description="Get detailed cost-sharing configuration for a benefit type"
)
@cache_response(ttl=600)
async def get_cost_sharing_configuration(
    benefit_type_id: str = Path(..., description="Benefit type ID"),
    network_tier: Optional[NetworkTier] = Query(None, description="Specific network tier"),
    effective_date: Optional[date] = Query(None, description="Configuration effective date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get cost-sharing configuration"""
    try:
        service = BenefitTypeService(db)
        configuration = await service.get_cost_sharing_configuration(
            benefit_type_id=benefit_type_id,
            network_tier=network_tier,
            effective_date=effective_date or date.today()
        )
        
        return configuration
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit type not found")
    except Exception as e:
        logger.error(f"Failed to get cost-sharing configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")


# =====================================================================
# BENEFIT ANALYSIS & COMPARISON
# =====================================================================

@router.post(
    "/compare",
    response_model=BenefitComparison,
    summary="Compare Benefit Types",
    description="Compare multiple benefit types for cost and coverage analysis"
)
async def compare_benefit_types(
    benefit_type_ids: List[str] = Body(..., description="List of benefit type IDs to compare"),
    comparison_scenarios: List[BenefitUsageScenario] = Body(..., description="Usage scenarios for comparison"),
    member_id: Optional[str] = Body(None, description="Member ID for personalized comparison"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Compare multiple benefit types"""
    try:
        service = BenefitTypeService(db)
        comparison = await service.compare_benefit_types(
            benefit_type_ids=benefit_type_ids,
            scenarios=comparison_scenarios,
            member_id=member_id
        )
        
        logger.info(
            f"Benefit types compared: {len(benefit_type_ids)} types, {len(comparison_scenarios)} scenarios",
            extra={"benefit_type_count": len(benefit_type_ids), "scenario_count": len(comparison_scenarios)}
        )
        
        return comparison
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Benefit type comparison failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Benefit comparison failed")


@router.post(
    "/{benefit_type_id}/project-annual-cost",
    response_model=AnnualCostProjection,
    summary="Project Annual Cost",
    description="Project annual member cost based on usage patterns"
)
async def project_annual_cost(
    benefit_type_id: str = Path(..., description="Benefit type ID"),
    usage_patterns: Dict[str, Any] = Body(..., description="Historical or projected usage patterns"),
    member_profile: Optional[Dict[str, Any]] = Body(None, description="Member demographic profile"),
    plan_year: Optional[int] = Body(None, description="Plan year for projections"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Project annual cost for a member"""
    try:
        service = BenefitTypeService(db)
        projection = await service.project_annual_cost(
            benefit_type_id=benefit_type_id,
            usage_patterns=usage_patterns,
            member_profile=member_profile,
            plan_year=plan_year or datetime.now().year
        )
        
        logger.info(
            f"Annual cost projected for benefit type {benefit_type_id}: ${projection.projected_annual_cost}",
            extra={
                "benefit_type_id": benefit_type_id,
                "projected_cost": float(projection.projected_annual_cost)
            }
        )
        
        return projection
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit type not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Annual cost projection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Annual cost projection failed")


@router.post(
    "/{benefit_type_id}/optimization-recommendations",
    response_model=List[CostOptimizationRecommendation],
    summary="Get Cost Optimization Recommendations",
    description="Get recommendations for optimizing member costs"
)
async def get_cost_optimization_recommendations(
    benefit_type_id: str = Path(..., description="Benefit type ID"),
    member_id: Optional[str] = Body(None, description="Member ID for personalized recommendations"),
    current_usage: Optional[Dict[str, Any]] = Body(None, description="Current usage patterns"),
    optimization_goals: List[str] = Body(default=["minimize_cost"], description="Optimization objectives"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get cost optimization recommendations"""
    try:
        service = BenefitTypeService(db)
        recommendations = await service.get_cost_optimization_recommendations(
            benefit_type_id=benefit_type_id,
            member_id=member_id,
            current_usage=current_usage,
            optimization_goals=optimization_goals
        )
        
        logger.info(
            f"Cost optimization recommendations generated for benefit type {benefit_type_id}: {len(recommendations)} recommendations",
            extra={"benefit_type_id": benefit_type_id, "recommendation_count": len(recommendations)}
        )
        
        return recommendations
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit type not found")
    except Exception as e:
        logger.error(f"Cost optimization recommendations failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


# =====================================================================
# NETWORK ANALYSIS
# =====================================================================

@router.get(
    "/{benefit_type_id}/network-cost-analysis",
    response_model=NetworkCostAnalysis,
    summary="Network Cost Analysis",
    description="Analyze cost differences across provider network tiers"
)
@cache_response(ttl=1800)
async def get_network_cost_analysis(
    benefit_type_id: str = Path(..., description="Benefit type ID"),
    service_types: Optional[List[str]] = Query(None, description="Specific service types to analyze"),
    geographic_area: Optional[str] = Query(None, description="Geographic area for analysis"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get network cost analysis"""
    try:
        service = BenefitTypeService(db)
        analysis = await service.get_network_cost_analysis(
            benefit_type_id=benefit_type_id,
            service_types=service_types,
            geographic_area=geographic_area
        )
        
        return analysis
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit type not found")
    except Exception as e:
        logger.error(f"Network cost analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Network cost analysis failed")


# =====================================================================
# SEARCH AND FILTERING
# =====================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[BenefitTypeResponse],
    summary="List Benefit Types",
    description="List and search benefit types with advanced filtering"
)
async def list_benefit_types(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    
    # Basic filters
    search: Optional[str] = Query(None, description="Search term"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    cost_sharing_type: Optional[CostSharingType] = Query(None, description="Cost-sharing type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    
    # Advanced filters
    min_deductible: Optional[Decimal] = Query(None, description="Minimum deductible amount"),
    max_deductible: Optional[Decimal] = Query(None, description="Maximum deductible amount"),
    has_copay: Optional[bool] = Query(None, description="Filter by copay presence"),
    has_coinsurance: Optional[bool] = Query(None, description="Filter by coinsurance presence"),
    network_tiers: Optional[List[NetworkTier]] = Query(None, description="Filter by network tiers"),
    
    # Sorting
    sort_by: str = Query("type_name", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List benefit types with advanced filtering"""
    try:
        service = BenefitTypeService(db)
        
        # Build filter dictionary
        filters = BenefitSearchFilter(
            search=search,
            category_id=category_id,
            cost_sharing_type=cost_sharing_type,
            is_active=is_active,
            min_deductible=min_deductible,
            max_deductible=max_deductible,
            has_copay=has_copay,
            has_coinsurance=has_coinsurance,
            network_tiers=network_tiers
        )
        
        # Get paginated results
        result = await service.search_benefit_types(
            filters=filters.dict(exclude_unset=True),
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return PaginatedResponse(
            items=[BenefitTypeResponse.model_validate(bt) for bt in result.items],
            total=result.total,
            page=page,
            size=size,
            pages=result.pages
        )
        
    except Exception as e:
        logger.error(f"Benefit type search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search benefit types")


# =====================================================================
# BULK OPERATIONS
# =====================================================================

@router.post(
    "/bulk/operations",
    response_model=Dict[str, Any],
    summary="Bulk Benefit Type Operations",
    description="Perform bulk operations on multiple benefit types"
)
async def bulk_benefit_type_operations(
    operation: BulkBenefitTypeOperation = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Perform bulk operations on benefit types"""
    try:
        require_permissions(current_user, ["admin", "benefit_manager"])
        
        service = BenefitTypeService(db)
        result = await service.bulk_operations(operation.dict())
        
        logger.info(
            f"Bulk benefit type operation performed by {current_user.get('user_id')}: {operation.operation_type}",
            extra={
                "operation_type": operation.operation_type,
                "benefit_type_count": len(operation.benefit_type_ids),
                "user_id": current_user.get('user_id')
            }
        )
        
        return result
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Bulk benefit type operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Bulk operation failed")


# =====================================================================
# ANALYTICS AND REPORTING
# =====================================================================

@router.get(
    "/analytics/cost-trends",
    response_model=Dict[str, Any],
    summary="Cost Trend Analytics",
    description="Get cost trend analytics across benefit types"
)
@cache_response(ttl=3600)
async def get_cost_trend_analytics(
    period: str = Query("90d", description="Analysis period"),
    benefit_type_ids: Optional[List[str]] = Query(None, description="Specific benefit types"),
    network_tier: Optional[NetworkTier] = Query(None, description="Specific network tier"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get cost trend analytics"""
    try:
        service = BenefitTypeService(db)
        analytics = await service.get_cost_trend_analytics(
            period=period,
            benefit_type_ids=benefit_type_ids,
            network_tier=network_tier
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Cost trend analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cost trends")


@router.get(
    "/analytics/utilization-patterns",
    response_model=Dict[str, Any],
    summary="Utilization Pattern Analytics",
    description="Get benefit type utilization pattern analytics"
)
@cache_response(ttl=3600)
async def get_utilization_pattern_analytics(
    period: str = Query("90d", description="Analysis period"),
    demographic_breakdown: bool = Query(False, description="Include demographic breakdown"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get utilization pattern analytics"""
    try:
        service = BenefitTypeService(db)
        analytics = await service.get_utilization_pattern_analytics(
            period=period,
            demographic_breakdown=demographic_breakdown
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Utilization pattern analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get utilization patterns")


# =====================================================================
# HEALTH CHECK
# =====================================================================

@router.get(
    "/health",
    response_model=Dict[str, str],
    summary="Benefit Type Service Health Check",
    description="Check the health status of the benefit type service"
)
async def benefit_type_service_health(
    db: Session = Depends(get_db)
):
    """Health check for benefit type service"""
    try:
        service = BenefitTypeService(db)
        health_status = await service.health_check()
        
        return {
            "status": "healthy" if health_status else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "BenefitTypeService"
        }
        
    except Exception as e:
        logger.error(f"Benefit type service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "BenefitTypeService",
            "error": str(e)
        }