# app/modules/pricing/product/routes/product_feature_routes.py

"""
Product Feature Routes

API endpoints for product feature management.
"""

from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.pricing.product.services import product_feature_service as service
from app.modules.pricing.product.schemas.product_feature_schema import (
    ProductFeatureCreate,
    ProductFeatureUpdate,
    ProductFeatureResponse,
    ProductFeatureListResponse,
    ProductFeatureFilter,
    ProductFeatureBulkCreate,
    ProductFeatureBulkUpdate,
    FeaturePricingRequest,
    FeaturePricingResponse,
    FeatureStatus,
    FeatureType,
    FeatureCategory
)

router = APIRouter(
    prefix="/features",
    tags=["Product Features"]
)


# ================================================================
# CREATE ENDPOINTS
# ================================================================

@router.post(
    "/",
    response_model=ProductFeatureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new feature"
)
async def create_feature(
    feature_data: ProductFeatureCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new product feature.
    
    - **feature_code**: Unique feature identifier
    - **feature_name**: Display name of the feature
    - **feature_type**: Type (basic, optional, rider, addon, mandatory)
    - **feature_category**: Category (medical, dental, vision, etc.)
    - **coverage_amount**: Coverage amount provided
    - **waiting_period_days**: Waiting period before coverage
    """
    try:
        return service.create_feature_with_validation(
            db, 
            feature_data, 
            created_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/bulk",
    response_model=List[ProductFeatureResponse],
    summary="Create multiple features"
)
async def create_features_bulk(
    product_id: UUID,
    features_data: List[ProductFeatureCreate],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create multiple features for a product in bulk.
    
    Maximum 50 features per request.
    """
    if len(features_data) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 features can be created at once"
        )
    
    try:
        return service.create_features_bulk(
            db,
            product_id,
            features_data,
            created_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/copy",
    response_model=List[ProductFeatureResponse],
    summary="Copy features between products"
)
async def copy_features(
    source_product_id: UUID = Query(..., description="Source product UUID"),
    target_product_id: UUID = Query(..., description="Target product UUID"),
    feature_codes: Optional[List[str]] = Query(None, description="Specific features to copy"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Copy features from one product to another.
    
    If feature_codes is not specified, all features are copied.
    """
    try:
        return service.copy_features_to_product(
            db,
            source_product_id,
            target_product_id,
            feature_codes,
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
    response_model=ProductFeatureListResponse,
    summary="List all features"
)
async def list_features(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    product_id: Optional[UUID] = Query(None, description="Filter by product"),
    feature_type: Optional[FeatureType] = Query(None, description="Filter by type"),
    feature_category: Optional[FeatureCategory] = Query(None, description="Filter by category"),
    status: Optional[FeatureStatus] = Query(None, description="Filter by status"),
    is_mandatory: Optional[bool] = Query(None, description="Filter by mandatory flag"),
    is_taxable: Optional[bool] = Query(None, description="Filter by taxable flag"),
    search_term: Optional[str] = Query(None, description="Search in name/code/description"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of features with optional filtering.
    """
    filters = ProductFeatureFilter(
        product_id=product_id,
        feature_type=feature_type,
        feature_category=feature_category,
        status=status,
        is_mandatory=is_mandatory,
        is_taxable=is_taxable,
        search_term=search_term,
        tags=tags
    )
    
    return service.search_features(db, filters, page, page_size)


@router.get(
    "/product/{product_id}",
    response_model=List[ProductFeatureResponse],
    summary="Get features for a product"
)
async def get_product_features(
    product_id: UUID,
    feature_type: Optional[FeatureType] = Query(None, description="Filter by type"),
    mandatory_only: bool = Query(False, description="Only mandatory features"),
    db: Session = Depends(get_db)
):
    """
    Get all features for a specific product.
    """
    return service.get_features_by_product(
        db, product_id, feature_type, mandatory_only
    )


@router.get(
    "/product/{product_id}/by-category",
    response_model=dict,
    summary="Get features grouped by category"
)
async def get_features_by_category(
    product_id: UUID,
    category: FeatureCategory,
    db: Session = Depends(get_db)
):
    """
    Get features grouped by type within a category.
    
    Returns features organized as:
    - mandatory
    - optional
    - rider
    - addon
    """
    return service.get_features_by_category(db, product_id, category)


@router.get(
    "/product/{product_id}/combinations",
    response_model=List[dict],
    summary="Get popular feature combinations"
)
async def get_popular_combinations(
    product_id: UUID,
    limit: int = Query(5, ge=1, le=10, description="Number of combinations"),
    db: Session = Depends(get_db)
):
    """
    Get popular feature combinations for a product.
    
    Returns pre-configured packages with estimated pricing.
    """
    return service.get_popular_feature_combinations(db, product_id, limit)


@router.get(
    "/{feature_id}",
    response_model=dict,
    summary="Get feature details"
)
async def get_feature(
    feature_id: UUID,
    include_pricing: bool = Query(True, description="Include pricing information"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive feature details.
    """
    try:
        return service.get_feature_details(db, feature_id, include_pricing)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# UPDATE ENDPOINTS
# ================================================================

@router.put(
    "/{feature_id}",
    response_model=ProductFeatureResponse,
    summary="Update feature"
)
async def update_feature(
    feature_id: UUID,
    update_data: ProductFeatureUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update feature configuration.
    
    Status transitions are validated:
    - ACTIVE → INACTIVE/SUSPENDED/DEPRECATED
    - INACTIVE → ACTIVE/DEPRECATED
    - PENDING → ACTIVE/INACTIVE
    """
    try:
        return service.update_feature_with_validation(
            db,
            feature_id,
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
    response_model=dict,
    summary="Bulk update features"
)
async def bulk_update_features(
    feature_ids: List[UUID],
    update_data: ProductFeatureUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update multiple features with the same changes.
    
    Returns summary of updated and failed updates.
    """
    return service.bulk_update_features(
        db,
        feature_ids,
        update_data,
        updated_by=current_user.get("user_id")
    )


# ================================================================
# STATUS MANAGEMENT ENDPOINTS
# ================================================================

@router.post(
    "/{feature_id}/activate",
    response_model=ProductFeatureResponse,
    summary="Activate feature"
)
async def activate_feature(
    feature_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Activate a feature for use.
    """
    try:
        return service.activate_feature(
            db,
            feature_id,
            activated_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{feature_id}/deactivate",
    response_model=ProductFeatureResponse,
    summary="Deactivate feature"
)
async def deactivate_feature(
    feature_id: UUID,
    reason: str = Query(..., min_length=1, description="Deactivation reason"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deactivate a feature.
    """
    try:
        return service.deactivate_feature(
            db,
            feature_id,
            reason,
            deactivated_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# PRICING ENDPOINTS
# ================================================================

@router.post(
    "/pricing/calculate",
    response_model=FeaturePricingResponse,
    summary="Calculate feature pricing"
)
async def calculate_feature_pricing(
    pricing_request: FeaturePricingRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate price for a feature with all factors.
    
    Considers:
    - Age-based pricing
    - Coverage amount adjustments
    - Discounts
    - Taxes
    """
    try:
        return service.calculate_feature_price(db, pricing_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/pricing/bundle",
    response_model=dict,
    summary="Calculate bundle pricing"
)
async def calculate_bundle_pricing(
    product_id: UUID,
    feature_ids: List[UUID],
    age: Optional[int] = Query(None, ge=0, le=150, description="Insured age"),
    apply_bundle_discount: bool = Query(True, description="Apply bundling discount"),
    db: Session = Depends(get_db)
):
    """
    Calculate price for a bundle of features.
    
    Includes:
    - Mandatory features automatically
    - Selected optional features
    - Bundle discounts for 3+ features
    - Tax calculation
    """
    try:
        return service.calculate_bundle_price(
            db,
            product_id,
            feature_ids,
            age,
            apply_bundle_discount
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# ELIGIBILITY ENDPOINTS
# ================================================================

@router.get(
    "/{feature_id}/eligibility",
    response_model=dict,
    summary="Check feature eligibility"
)
async def check_eligibility(
    feature_id: UUID,
    age: int = Query(..., ge=0, le=150, description="Person's age"),
    has_pre_existing: bool = Query(False, description="Has pre-existing conditions"),
    db: Session = Depends(get_db)
):
    """
    Check if a person is eligible for a feature.
    
    Returns:
    - Eligibility status
    - Restrictions
    - Requirements
    - Waiting periods
    """
    try:
        return service.check_feature_eligibility(
            db, feature_id, age, has_pre_existing
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# VALIDATION ENDPOINTS
# ================================================================

@router.get(
    "/product/{product_id}/validate",
    response_model=dict,
    summary="Validate feature configuration"
)
async def validate_features(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Validate feature configuration for a product.
    
    Checks:
    - Mandatory features exist
    - Feature diversity
    - Pricing completeness
    - Age range consistency
    """
    return service.validate_feature_configuration(db, product_id)


# ================================================================
# ANALYTICS ENDPOINTS
# ================================================================

@router.get(
    "/product/{product_id}/analytics",
    response_model=dict,
    summary="Get feature analytics"
)
async def get_feature_analytics(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get analytics for product features.
    
    Includes:
    - Feature statistics
    - Pricing analysis
    - Coverage analysis
    - Distribution by type/category
    """
    return service.get_feature_analytics(db, product_id)


@router.get(
    "/statistics",
    response_model=dict,
    summary="Get feature statistics"
)
async def get_feature_statistics(
    product_id: Optional[UUID] = Query(None, description="Filter by product"),
    db: Session = Depends(get_db)
):
    """
    Get overall feature statistics.
    """
    from app.modules.pricing.product.repositories import product_feature_repository as repo
    
    return repo.get_feature_statistics(db, product_id)


# ================================================================
# DELETE ENDPOINTS
# ================================================================

@router.delete(
    "/{feature_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete feature"
)
async def delete_feature(
    feature_id: UUID,
    soft_delete: bool = Query(True, description="Soft delete (can be recovered)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a feature (soft or hard delete).
    """
    from app.modules.pricing.product.repositories import product_feature_repository as repo
    
    try:
        repo.delete_product_feature(
            db,
            feature_id,
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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all features for a product"
)
async def delete_product_features(
    product_id: UUID,
    soft_delete: bool = Query(True, description="Soft delete (can be recovered)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete all features for a product.
    """
    from app.modules.pricing.product.repositories import product_feature_repository as repo
    
    try:
        count = repo.delete_features_by_product(
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