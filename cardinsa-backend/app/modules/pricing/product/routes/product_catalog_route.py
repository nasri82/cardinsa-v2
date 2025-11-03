# app/modules/pricing/product/routes/product_catalog_routes.py

"""
Product Catalog Routes

API endpoints for product catalog management.
"""

from typing import Optional, List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.pricing.product.services import product_catalog_service as service
from app.modules.pricing.product.schemas.product_catalog_schema import (
    ProductCatalogCreate,
    ProductCatalogUpdate,
    ProductCatalogResponse,
    ProductCatalogListResponse,
    ProductCatalogFilter,
    ProductCatalogClone,
    ProductStatusEnum as ProductStatus,
    ProductTypeEnum as ProductType,
    ProductCategoryEnum as ProductCategory
)

router = APIRouter(
    prefix="/products",
    tags=["Product Catalog"]
)


# ================================================================
# CREATE ENDPOINTS
# ================================================================

@router.post(
    "/",
    response_model=ProductCatalogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product"
)
async def create_product(
    product_data: ProductCatalogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new insurance product.
    
    - **product_code**: Unique product identifier
    - **product_name**: Display name of the product
    - **product_type**: Type of insurance (health, life, etc.)
    - **product_category**: Category classification
    - **base_premium_range**: Premium range configuration
    - **coverage_limits**: Coverage limit settings
    """
    try:
        return service.create_product_with_validation(
            db, 
            product_data, 
            created_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/bulk",
    response_model=List[ProductCatalogResponse],
    summary="Create multiple products"
)
async def create_products_bulk(
    products_data: List[ProductCatalogCreate],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create multiple products in bulk.
    
    Maximum 50 products per request.
    """
    if len(products_data) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 products can be created at once"
        )
    
    try:
        created_products = []
        for product_data in products_data:
            product = service.create_product_with_validation(
                db, 
                product_data, 
                created_by=current_user.get("user_id")
            )
            created_products.append(product)
        return created_products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/clone",
    response_model=ProductCatalogResponse,
    summary="Clone an existing product"
)
async def clone_product(
    clone_request: ProductCatalogClone,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Clone an existing product with optional components.
    
    - **source_product_id**: Product to clone from
    - **new_product_code**: Unique code for cloned product
    - **new_product_name**: Name for cloned product
    - **include_features**: Clone features as well
    - **include_commission**: Clone commission structure
    - **include_underwriting**: Clone underwriting rules
    """
    try:
        return service.clone_product_with_components(
            db,
            clone_request,
            created_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/tier-structure",
    response_model=List[ProductCatalogResponse],
    summary="Create standard tier structure"
)
async def create_tier_structure(
    product_id: UUID,
    base_premium: float = Query(..., ge=0, description="Base premium for bronze tier"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a standard tier structure (Bronze, Silver, Gold, Platinum) for a product.
    """
    # Note: This would typically call plan_type_service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="This endpoint should call plan_type_service.create_plan_tier_structure"
    )


# ================================================================
# READ ENDPOINTS
# ================================================================

@router.get(
    "/",
    response_model=ProductCatalogListResponse,
    summary="List all products"
)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    product_type: Optional[ProductType] = Query(None, description="Filter by product type"),
    product_category: Optional[ProductCategory] = Query(None, description="Filter by category"),
    status: Optional[ProductStatus] = Query(None, description="Filter by status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search_term: Optional[str] = Query(None, description="Search in name/code/description"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of products with optional filtering.
    """
    filters = ProductCatalogFilter(
        product_type=product_type,
        product_category=product_category,
        status=status,
        is_active=is_active,
        search_term=search_term,
        tags=tags
    )
    
    return service.search_products(
        db, filters, page, page_size, sort_by, sort_order
    )


@router.get(
    "/active",
    response_model=List[ProductCatalogResponse],
    summary="List active products"
)
async def list_active_products(
    category: Optional[ProductCategory] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Get all active products available for sale.
    """
    return service.get_products_by_category(
        db, category, active_only=True
    )


@router.get(
    "/requiring-review",
    response_model=List[dict],
    summary="Get products requiring review"
)
async def get_products_requiring_review(
    days_until_expiry: int = Query(30, ge=1, description="Days threshold for expiry warning"),
    db: Session = Depends(get_db)
):
    """
    Get products that need review or action.
    
    Returns products that are:
    - Expiring soon
    - Missing configuration
    - Pending approval for too long
    """
    return service.get_products_requiring_review(db, days_until_expiry)


@router.get(
    "/{product_id}",
    response_model=dict,
    summary="Get product details"
)
async def get_product(
    product_id: UUID,
    include_features: bool = Query(True, description="Include product features"),
    include_plans: bool = Query(True, description="Include plan types"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive product details with related entities.
    """
    try:
        return service.get_product_details(
            db, product_id, include_features, include_plans
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# UPDATE ENDPOINTS
# ================================================================

@router.put(
    "/{product_id}",
    response_model=ProductCatalogResponse,
    summary="Update product"
)
async def update_product(
    product_id: UUID,
    update_data: ProductCatalogUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update product configuration.
    
    Status transitions are validated:
    - DRAFT → PENDING_APPROVAL → ACTIVE
    - ACTIVE → SUSPENDED → ACTIVE
    - ACTIVE → DISCONTINUED
    """
    try:
        return service.update_product_with_validation(
            db,
            product_id,
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
    response_model=List[ProductCatalogResponse],
    summary="Bulk update products"
)
async def bulk_update_products(
    product_ids: List[UUID],
    update_data: ProductCatalogUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update multiple products with the same changes.
    """
    return service.bulk_update_products(
        db,
        product_ids,
        update_data,
        updated_by=current_user.get("user_id")
    )


# ================================================================
# STATUS MANAGEMENT ENDPOINTS
# ================================================================

@router.post(
    "/{product_id}/activate",
    response_model=ProductCatalogResponse,
    summary="Activate product"
)
async def activate_product(
    product_id: UUID,
    effective_date: Optional[date] = Query(None, description="Activation date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Activate a product for sale.
    
    Requirements:
    - Product must have at least one feature
    - Product must have at least one plan
    """
    try:
        return service.activate_product(
            db,
            product_id,
            effective_date,
            activated_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/bulk-activate",
    response_model=dict,
    summary="Bulk activate products"
)
async def bulk_activate_products(
    product_ids: List[UUID],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Activate multiple products at once.
    """
    return service.bulk_activate_products(
        db,
        product_ids,
        activated_by=current_user.get("user_id")
    )


@router.post(
    "/{product_id}/suspend",
    response_model=ProductCatalogResponse,
    summary="Suspend product"
)
async def suspend_product(
    product_id: UUID,
    reason: str = Query(..., min_length=1, description="Suspension reason"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Suspend a product temporarily.
    
    Only active products can be suspended.
    """
    try:
        return service.suspend_product(
            db,
            product_id,
            reason,
            suspended_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{product_id}/discontinue",
    response_model=ProductCatalogResponse,
    summary="Discontinue product"
)
async def discontinue_product(
    product_id: UUID,
    discontinuation_date: Optional[date] = Query(None, description="Discontinuation date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Discontinue a product permanently.
    
    This action cannot be reversed.
    """
    try:
        return service.discontinue_product(
            db,
            product_id,
            discontinuation_date,
            discontinued_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# DELETE ENDPOINTS
# ================================================================

@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product"
)
async def delete_product(
    product_id: UUID,
    soft_delete: bool = Query(True, description="Soft delete (can be recovered)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a product (soft or hard delete).
    
    Soft delete marks the product as deleted but retains data.
    Hard delete permanently removes the product.
    """
    from app.modules.pricing.product.repositories import product_catalog_repository as repo
    
    try:
        repo.delete_product_catalog(
            db,
            product_id,
            soft_delete,
            deleted_by=current_user.get("user_id")
        )
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# VALIDATION & COMPLIANCE ENDPOINTS
# ================================================================

@router.get(
    "/{product_id}/validate",
    response_model=dict,
    summary="Validate product completeness"
)
async def validate_product(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Validate if a product is complete and ready for sale.
    
    Checks:
    - Required information is present
    - Features are configured
    - Plans are available
    - Dates are valid
    """
    try:
        return service.validate_product_completeness(db, product_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/{product_id}/compliance",
    response_model=dict,
    summary="Check regulatory compliance"
)
async def check_compliance(
    product_id: UUID,
    region: Optional[str] = Query(None, description="Regulatory region"),
    db: Session = Depends(get_db)
):
    """
    Check if product meets regulatory requirements.
    """
    try:
        return service.check_regulatory_compliance(db, product_id, region)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# ANALYTICS ENDPOINTS
# ================================================================

@router.get(
    "/{product_id}/analytics",
    response_model=dict,
    summary="Get product analytics"
)
async def get_product_analytics(
    product_id: UUID,
    start_date: Optional[date] = Query(None, description="Analytics start date"),
    end_date: Optional[date] = Query(None, description="Analytics end date"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for a product.
    
    Includes:
    - Feature statistics
    - Plan statistics
    - Pricing analysis
    - Performance metrics
    """
    try:
        return service.get_product_analytics(
            db, product_id, start_date, end_date
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/analytics/portfolio",
    response_model=dict,
    summary="Get portfolio summary"
)
async def get_portfolio_summary(
    include_inactive: bool = Query(False, description="Include inactive products"),
    db: Session = Depends(get_db)
):
    """
    Get summary of entire product portfolio.
    
    Includes:
    - Total product count
    - Status distribution
    - Category breakdown
    - Activation rates
    """
    return service.get_portfolio_summary(db, include_inactive)


@router.get(
    "/statistics",
    response_model=dict,
    summary="Get product statistics"
)
async def get_product_statistics(
    db: Session = Depends(get_db)
):
    """
    Get overall product statistics.
    """
    from app.modules.pricing.product.repositories import product_catalog_repository as repo
    
    return repo.get_product_statistics(db)


# ================================================================
# END OF ROUTES
# ================================================================