# app/modules/pricing/product/routes/plan_type_routes.py

"""
Plan Type Routes

API endpoints for plan type management.
"""

from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.pricing.product.services import plan_type_service as service
from app.modules.pricing.product.schemas.plan_type_schema import (
    PlanTypeCreate,
    PlanTypeUpdate,
    PlanTypeResponse,
    PlanTypeListResponse,
    PlanTypeFilter,
    PlanComparison,
    PlanComparisonResponse,
    PlanEligibilityRequest,
    PlanEligibilityResponse,
    PlanStatus,
    PlanTier,
    PlanCategory,
    NetworkType
)

router = APIRouter(
    prefix="/plans",
    tags=["Plan Types"]
)


# ================================================================
# CREATE ENDPOINTS
# ================================================================

@router.post(
    "/",
    response_model=PlanTypeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new plan"
)
async def create_plan(
    plan_data: PlanTypeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new insurance plan type.
    
    - **plan_code**: Unique plan identifier
    - **plan_name**: Display name of the plan
    - **plan_tier**: Tier level (bronze, silver, gold, platinum)
    - **plan_category**: Category (individual, family, group, etc.)
    - **base_premium**: Base premium amount
    - **deductibles**: Individual and family deductibles
    - **coverage_limits**: Annual and lifetime limits
    """
    try:
        return service.create_plan_with_validation(
            db, 
            plan_data, 
            created_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/tier-structure",
    response_model=List[PlanTypeResponse],
    summary="Create tier structure"
)
async def create_tier_structure(
    product_id: UUID = Body(..., description="Product UUID"),
    base_premium: float = Body(..., ge=0, description="Base premium for bronze tier"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a standard tier structure for a product.
    
    Creates Bronze, Silver, Gold, and Platinum plans with:
    - Progressive pricing (1x, 1.3x, 1.6x, 2x)
    - Decreasing deductibles
    - Increasing coverage limits
    """
    try:
        return service.create_plan_tier_structure(
            db,
            product_id,
            Decimal(str(base_premium)),
            created_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# READ ENDPOINTS
# ================================================================

@router.get(
    "/",
    response_model=PlanTypeListResponse,
    summary="List all plans"
)
async def list_plans(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    product_id: Optional[UUID] = Query(None, description="Filter by product"),
    plan_tier: Optional[PlanTier] = Query(None, description="Filter by tier"),
    plan_category: Optional[PlanCategory] = Query(None, description="Filter by category"),
    network_type: Optional[NetworkType] = Query(None, description="Filter by network"),
    status: Optional[PlanStatus] = Query(None, description="Filter by status"),
    is_renewable: Optional[bool] = Query(None, description="Filter by renewable flag"),
    allows_dependents: Optional[bool] = Query(None, description="Filter by dependents flag"),
    min_premium: Optional[float] = Query(None, ge=0, description="Minimum premium"),
    max_premium: Optional[float] = Query(None, ge=0, description="Maximum premium"),
    search_term: Optional[str] = Query(None, description="Search in name/code/description"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of plans with optional filtering.
    """
    filters = PlanTypeFilter(
        product_id=product_id,
        plan_tier=plan_tier,
        plan_category=plan_category,
        network_type=network_type,
        status=status,
        is_renewable=is_renewable,
        allows_dependents=allows_dependents,
        min_premium=Decimal(str(min_premium)) if min_premium else None,
        max_premium=Decimal(str(max_premium)) if max_premium else None,
        search_term=search_term,
        tags=tags
    )
    
    return service.search_plans(db, filters, page, page_size)


@router.get(
    "/product/{product_id}",
    response_model=List[PlanTypeResponse],
    summary="Get plans for a product"
)
async def get_product_plans(
    product_id: UUID,
    active_only: bool = Query(True, description="Only active plans"),
    db: Session = Depends(get_db)
):
    """
    Get all plans for a specific product.
    
    Plans are ordered by tier hierarchy (Bronze → Platinum).
    """
    return service.get_plans_by_product(db, product_id, active_only)


@router.get(
    "/{plan_id}",
    response_model=dict,
    summary="Get plan details"
)
async def get_plan(
    plan_id: UUID,
    include_features: bool = Query(True, description="Include applicable features"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive plan details.
    
    Includes:
    - Coverage limits and deductibles
    - Enrollment requirements
    - Applicable features (if requested)
    """
    try:
        return service.get_plan_details(db, plan_id, include_features)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# COMPARISON ENDPOINTS
# ================================================================

@router.post(
    "/compare",
    response_model=PlanComparisonResponse,
    summary="Compare multiple plans"
)
async def compare_plans(
    comparison_request: PlanComparison,
    db: Session = Depends(get_db)
):
    """
    Compare multiple plans side by side.
    
    - Minimum 2 plans, maximum 5 plans
    - Includes premium comparison
    - Coverage comparison
    - Feature comparison (optional)
    - Intelligent recommendations
    """
    try:
        return service.compare_plans(db, comparison_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# ELIGIBILITY ENDPOINTS
# ================================================================

@router.post(
    "/eligibility",
    response_model=PlanEligibilityResponse,
    summary="Check plan eligibility"
)
async def check_eligibility(
    eligibility_request: PlanEligibilityRequest,
    product_id: Optional[UUID] = Query(None, description="Filter by product"),
    db: Session = Depends(get_db)
):
    """
    Check eligibility for plans based on criteria.
    
    Considers:
    - Age requirements
    - Member count limits
    - Dependent allowances
    - Pre-existing conditions
    - Geographic location
    """
    try:
        return service.check_plan_eligibility(
            db, eligibility_request, product_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# PREMIUM CALCULATION ENDPOINTS
# ================================================================

@router.post(
    "/{plan_id}/calculate-premium",
    response_model=dict,
    summary="Calculate plan premium"
)
async def calculate_premium(
    plan_id: UUID,
    member_count: int = Query(1, ge=1, description="Number of primary members"),
    dependent_count: int = Query(0, ge=0, description="Number of dependents"),
    ages: Optional[List[int]] = Query(None, description="Ages of all members"),
    db: Session = Depends(get_db)
):
    """
    Calculate detailed premium for a plan.
    
    Includes:
    - Age-based adjustments
    - Group discounts (5+ members)
    - Payment schedule
    - All applicable factors
    """
    try:
        return service.calculate_plan_premium(
            db, plan_id, member_count, dependent_count, ages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/product/{product_id}/price-range",
    response_model=dict,
    summary="Get price range for product plans"
)
async def get_price_range(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get price range for all plans in a product.
    
    Returns:
    - Minimum premium
    - Maximum premium
    - Average premium
    - Premium by tier
    """
    from app.modules.pricing.product.repositories import plan_type_repository as repo
    
    return repo.get_plan_price_range(db, product_id)


# ================================================================
# UPDATE ENDPOINTS
# ================================================================

@router.put(
    "/{plan_id}",
    response_model=PlanTypeResponse,
    summary="Update plan"
)
async def update_plan(
    plan_id: UUID,
    update_data: PlanTypeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update plan configuration.
    
    Validates:
    - Age limits consistency
    - Deductible relationships
    - Coverage limit logic
    - Member count limits
    """
    try:
        return service.update_plan_with_validation(
            db,
            plan_id,
            update_data,
            updated_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/bulk-update",
    response_model=List[PlanTypeResponse],
    summary="Bulk update plans"
)
async def bulk_update_plans(
    plan_ids: List[UUID],
    update_data: PlanTypeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update multiple plans with the same changes.
    """
    from app.modules.pricing.product.repositories import plan_type_repository as repo
    
    return repo.bulk_update_plans(
        db,
        plan_ids,
        update_data,
        updated_by=current_user.get("user_id")
    )


# ================================================================
# ANALYTICS ENDPOINTS
# ================================================================

@router.get(
    "/product/{product_id}/analytics",
    response_model=dict,
    summary="Get plan analytics"
)
async def get_plan_analytics(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get analytics for plans in a product.
    
    Includes:
    - Plan statistics
    - Pricing analysis
    - Tier distribution
    - Network analysis
    - Enrollment capacity
    """
    return service.get_plan_analytics(db, product_id)


@router.get(
    "/{plan_id}/performance",
    response_model=dict,
    summary="Get plan performance metrics"
)
async def get_performance_metrics(
    plan_id: UUID,
    period_days: int = Query(30, ge=1, description="Analysis period in days"),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for a plan.
    
    Includes (mock data):
    - Enrollment rate
    - Retention rate
    - Satisfaction score
    - Financial metrics
    """
    return service.get_plan_performance_metrics(db, plan_id, period_days)


@router.get(
    "/statistics",
    response_model=dict,
    summary="Get plan statistics"
)
async def get_plan_statistics(
    product_id: Optional[UUID] = Query(None, description="Filter by product"),
    db: Session = Depends(get_db)
):
    """
    Get overall plan statistics.
    """
    from app.modules.pricing.product.repositories import plan_type_repository as repo
    
    return repo.get_plan_statistics(db, product_id)


@router.get(
    "/renewable",
    response_model=List[PlanTypeResponse],
    summary="Get renewable plans"
)
async def get_renewable_plans(
    days_until_expiry: int = Query(30, ge=1, description="Days threshold"),
    product_id: Optional[UUID] = Query(None, description="Filter by product"),
    db: Session = Depends(get_db)
):
    """
    Get plans that are due for renewal.
    """
    from datetime import date, timedelta
    from app.modules.pricing.product.repositories import plan_type_repository as repo
    
    expiry_threshold = date.today() + timedelta(days=days_until_expiry)
    plans = repo.get_renewable_plans(db, expiry_threshold, product_id)
    
    return [PlanTypeResponse.model_validate(p) for p in plans]


# ================================================================
# DELETE ENDPOINTS
# ================================================================

@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete plan"
)
async def delete_plan(
    plan_id: UUID,
    soft_delete: bool = Query(True, description="Soft delete (can be recovered)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a plan (soft or hard delete).
    """
    from app.modules.pricing.product.repositories import plan_type_repository as repo
    
    try:
        repo.delete_plan_type(
            db,
            plan_id,
            soft_delete,
            deleted_by=current_user.get("user_id")
        )
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/product/{product_id}/all",
    response_model=dict,
    summary="Delete all plans for a product"
)
async def delete_product_plans(
    product_id: UUID,
    soft_delete: bool = Query(True, description="Soft delete (can be recovered)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete all plans for a product.
    """
    from app.modules.pricing.product.repositories import plan_type_repository as repo
    
    try:
        count = repo.delete_plans_by_product(
            db,
            product_id,
            soft_delete,
            deleted_by=current_user.get("user_id")
        )
        return {"deleted_count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# END OF ROUTES
# ================================================================