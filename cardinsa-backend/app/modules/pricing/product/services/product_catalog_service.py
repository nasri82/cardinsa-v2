# app/modules/pricing/product/services/product_catalog_service.py

"""
Product Catalog Service

Business logic layer for Product Catalog management.
Handles complex operations, validations, and orchestration.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.modules.pricing.product.repositories import product_catalog_repository as repo
from app.modules.pricing.product.repositories import product_feature_repository as feature_repo
from app.modules.pricing.product.repositories import plan_type_repository as plan_repo
from app.modules.pricing.product.schemas.product_catalog_schema import (
    ProductCatalogCreate,
    ProductCatalogUpdate,
    ProductCatalogFilter,
    ProductCatalogResponse,
    ProductCatalogListResponse,
    ProductCatalogClone,
    ProductStatusEnum as ProductStatus,
    ProductTypeEnum as ProductType
)
from app.core.database import get_db
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Define custom exceptions
class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class ConflictException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ================================================================
# PRODUCT CREATION & MANAGEMENT
# ================================================================

def create_product_with_validation(
    db: Session,
    product_data: ProductCatalogCreate,
    created_by: Optional[UUID] = None
) -> ProductCatalogResponse:
    """
    Create a new product with comprehensive validation
    
    Args:
        db: Database session
        product_data: Product creation data
        created_by: User ID creating the product
        
    Returns:
        Created product response
        
    Raises:
        ValidationException: If validation fails
        ConflictException: If product code exists
    """
    try:
        # Validate product data
        _validate_product_data(product_data)
        
        # Check for code uniqueness
        existing = repo.get_product_by_code(db, product_data.product_code)
        if existing:
            raise ConflictException(
                f"Product with code '{product_data.product_code}' already exists"
            )
        
        # Validate date ranges
        if product_data.effective_date and product_data.expiry_date:
            if product_data.expiry_date <= product_data.effective_date:
                raise ValidationException(
                    "Expiry date must be after effective date"
                )
        
        # Create the product
        product = repo.create_product_catalog(db, product_data, created_by)
        
        # Log the creation
        logger.info(
            f"Product created: {product.id} - {product.product_name} "
            f"by user {created_by}"
        )
        
        # Convert to response schema
        return ProductCatalogResponse.model_validate(product)
        
    except (ConflictException, ValidationException) as e:
        logger.warning(f"Product creation validation failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating product: {str(e)}")
        raise BadRequestException(f"Failed to create product: {str(e)}")


def _validate_product_data(product_data: ProductCatalogCreate) -> None:
    """
    Validate product data before creation
    
    Args:
        product_data: Product data to validate
        
    Raises:
        ValidationException: If validation fails
    """
    # Validate age limits
    if product_data.min_age_limit and product_data.max_age_limit:
        if product_data.min_age_limit > product_data.max_age_limit:
            raise ValidationException(
                "Minimum age limit cannot be greater than maximum age limit"
            )
    
    # Validate renewal settings
    if product_data.max_renewal_age and product_data.min_age_limit:
        if product_data.max_renewal_age < product_data.min_age_limit:
            raise ValidationException(
                "Maximum renewal age cannot be less than minimum age limit"
            )
    
    # Validate product type specific rules
    if product_data.product_type == ProductType.LIFE:
        if not product_data.requires_underwriting:
            logger.warning(
                "Life insurance product typically requires underwriting"
            )
    
    # Validate waiting periods
    if product_data.product_type == ProductType.HEALTH:
        if not hasattr(product_data, 'waiting_period_days'):
            logger.warning(
                "Health insurance product should define waiting periods"
            )


# ================================================================
# PRODUCT RETRIEVAL & SEARCH
# ================================================================

def get_product_details(
    db: Session,
    product_id: UUID,
    include_features: bool = True,
    include_plans: bool = True
) -> Dict[str, Any]:
    """
    Get comprehensive product details with related entities
    
    Args:
        db: Database session
        product_id: Product UUID
        include_features: Include product features
        include_plans: Include plan types
        
    Returns:
        Product details with related data
        
    Raises:
        NotFoundException: If product not found
    """
    # Get base product
    product = repo.get_product_catalog_by_id(db, product_id)
    
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    result = {
        "product": ProductCatalogResponse.model_validate(product),
        "statistics": {}
    }
    
    # Add features if requested
    if include_features:
        features = feature_repo.get_features_by_product(db, product_id)
        result["features"] = features
        result["statistics"]["total_features"] = len(features)
        result["statistics"]["mandatory_features"] = sum(
            1 for f in features if f.is_mandatory
        )
    
    # Add plans if requested
    if include_plans:
        plans = plan_repo.get_plans_by_product(db, product_id)
        result["plans"] = plans
        result["statistics"]["total_plans"] = len(plans)
        result["statistics"]["active_plans"] = sum(
            1 for p in plans if p.status == 'active'
        )
    
    # Add pricing range
    if include_plans and plans:
        price_range = plan_repo.get_plan_price_range(db, product_id)
        result["pricing"] = price_range
    
    return result


def search_products(
    db: Session,
    filters: Optional[ProductCatalogFilter] = None,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> ProductCatalogListResponse:
    """
    Search products with advanced filtering
    
    Args:
        db: Database session
        filters: Search filters
        page: Page number (1-based)
        page_size: Items per page
        sort_by: Sort field
        sort_order: Sort direction
        
    Returns:
        Paginated product list response
    """
    # Calculate offset
    skip = (page - 1) * page_size
    
    # Get products from repository
    result = repo.get_products_list(
        db, filters, skip, page_size, sort_by, sort_order
    )
    
    # Convert to response schema
    products = [
        ProductCatalogResponse.model_validate(p) 
        for p in result["products"]
    ]
    
    return ProductCatalogListResponse(
        products=products,
        total_count=result["total_count"],
        page=page,
        page_size=page_size,
        total_pages=result["total_pages"]
    )


def get_products_by_category(
    db: Session,
    category: str,
    active_only: bool = True
) -> List[ProductCatalogResponse]:
    """
    Get products by category
    
    Args:
        db: Database session
        category: Product category
        active_only: Only return active products
        
    Returns:
        List of products in the category
    """
    if active_only:
        products = repo.get_active_products(db, category)
    else:
        filters = ProductCatalogFilter(product_category=category)
        result = repo.get_products_list(db, filters)
        products = result["products"]
    
    return [
        ProductCatalogResponse.model_validate(p) 
        for p in products
    ]


# ================================================================
# PRODUCT UPDATE & LIFECYCLE
# ================================================================

def update_product_with_validation(
    db: Session,
    product_id: UUID,
    update_data: ProductCatalogUpdate,
    updated_by: Optional[UUID] = None
) -> ProductCatalogResponse:
    """
    Update product with validation and change tracking
    
    Args:
        db: Database session
        product_id: Product UUID
        update_data: Update data
        updated_by: User ID updating the product
        
    Returns:
        Updated product response
    """
    # Get existing product
    product = repo.get_product_catalog_by_id(db, product_id)
    
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    # Validate status transitions
    if update_data.status:
        _validate_status_transition(product.status, update_data.status)
    
    # Validate dates if being updated
    if update_data.effective_date or update_data.expiry_date:
        effective = update_data.effective_date or product.effective_date
        expiry = update_data.expiry_date or product.expiry_date
        
        if effective and expiry and expiry <= effective:
            raise ValidationException("Expiry date must be after effective date")
    
    # Update the product
    updated_product = repo.update_product_catalog(
        db, product_id, update_data, updated_by
    )
    
    logger.info(
        f"Product updated: {product_id} by user {updated_by}"
    )
    
    return ProductCatalogResponse.model_validate(updated_product)


def _validate_status_transition(
    current_status: ProductStatus,
    new_status: ProductStatus
) -> None:
    """
    Validate product status transitions
    
    Args:
        current_status: Current product status
        new_status: New status to transition to
        
    Raises:
        ValidationException: If transition is invalid
    """
    valid_transitions = {
        ProductStatus.DRAFT: [
            ProductStatus.PENDING_APPROVAL,
            ProductStatus.ACTIVE
        ],
        ProductStatus.PENDING_APPROVAL: [
            ProductStatus.ACTIVE,
            ProductStatus.DRAFT,
            ProductStatus.SUSPENDED
        ],
        ProductStatus.ACTIVE: [
            ProductStatus.SUSPENDED,
            ProductStatus.DISCONTINUED
        ],
        ProductStatus.SUSPENDED: [
            ProductStatus.ACTIVE,
            ProductStatus.DISCONTINUED
        ],
        ProductStatus.DISCONTINUED: []  # No transitions from discontinued
    }
    
    allowed = valid_transitions.get(current_status, [])
    
    if new_status not in allowed:
        raise ValidationException(
            f"Invalid status transition from {current_status} to {new_status}"
        )


def activate_product(
    db: Session,
    product_id: UUID,
    effective_date: Optional[date] = None,
    activated_by: Optional[UUID] = None
) -> ProductCatalogResponse:
    """
    Activate a product for sale
    
    Args:
        db: Database session
        product_id: Product UUID
        effective_date: Activation date (default: today)
        activated_by: User ID activating the product
        
    Returns:
        Activated product response
    """
    product = repo.get_product_catalog_by_id(db, product_id)
    
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    # Check if product can be activated
    if product.status not in [ProductStatus.DRAFT, ProductStatus.PENDING_APPROVAL, ProductStatus.SUSPENDED]:
        raise ValidationException(
            f"Product cannot be activated from status {product.status}"
        )
    
    # Check if product has required components
    features = feature_repo.get_features_by_product(db, product_id)
    if not features:
        raise ValidationException(
            "Product must have at least one feature before activation"
        )
    
    plans = plan_repo.get_plans_by_product(db, product_id)
    if not plans:
        raise ValidationException(
            "Product must have at least one plan before activation"
        )
    
    # Update product status
    update_data = ProductCatalogUpdate(
        status=ProductStatus.ACTIVE,
        is_active=True,
        effective_date=effective_date or date.today()
    )
    
    updated_product = repo.update_product_catalog(
        db, product_id, update_data, activated_by
    )
    
    logger.info(
        f"Product activated: {product_id} by user {activated_by}"
    )
    
    return ProductCatalogResponse.model_validate(updated_product)


def suspend_product(
    db: Session,
    product_id: UUID,
    reason: str,
    suspended_by: Optional[UUID] = None
) -> ProductCatalogResponse:
    """
    Suspend a product temporarily
    
    Args:
        db: Database session
        product_id: Product UUID
        reason: Suspension reason
        suspended_by: User ID suspending the product
        
    Returns:
        Suspended product response
    """
    product = repo.get_product_catalog_by_id(db, product_id)
    
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    if product.status != ProductStatus.ACTIVE:
        raise ValidationException(
            f"Only active products can be suspended"
        )
    
    # Update product
    update_data = ProductCatalogUpdate(
        status=ProductStatus.SUSPENDED,
        is_active=False,
        notes=f"Suspended: {reason}"
    )
    
    updated_product = repo.update_product_catalog(
        db, product_id, update_data, suspended_by
    )
    
    logger.warning(
        f"Product suspended: {product_id} - Reason: {reason} "
        f"by user {suspended_by}"
    )
    
    return ProductCatalogResponse.model_validate(updated_product)


def discontinue_product(
    db: Session,
    product_id: UUID,
    discontinuation_date: Optional[date] = None,
    discontinued_by: Optional[UUID] = None
) -> ProductCatalogResponse:
    """
    Discontinue a product permanently
    
    Args:
        db: Database session
        product_id: Product UUID
        discontinuation_date: Date of discontinuation
        discontinued_by: User ID discontinuing the product
        
    Returns:
        Discontinued product response
    """
    product = repo.get_product_catalog_by_id(db, product_id)
    
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    if product.status == ProductStatus.DISCONTINUED:
        raise ValidationException("Product is already discontinued")
    
    # Update product
    update_data = ProductCatalogUpdate(
        status=ProductStatus.DISCONTINUED,
        is_active=False,
        expiry_date=discontinuation_date or date.today()
    )
    
    updated_product = repo.update_product_catalog(
        db, product_id, update_data, discontinued_by
    )
    
    # Also discontinue all plans
    plan_repo.delete_plans_by_product(
        db, product_id, soft_delete=True, deleted_by=discontinued_by
    )
    
    logger.warning(
        f"Product discontinued: {product_id} by user {discontinued_by}"
    )
    
    return ProductCatalogResponse.model_validate(updated_product)


# ================================================================
# PRODUCT CLONING & DUPLICATION
# ================================================================

def clone_product_with_components(
    db: Session,
    clone_request: ProductCatalogClone,
    created_by: Optional[UUID] = None
) -> ProductCatalogResponse:
    """
    Clone a product with optional features and plans
    
    Args:
        db: Database session
        clone_request: Clone configuration
        created_by: User ID creating the clone
        
    Returns:
        Cloned product response
    """
    # Get source product
    source = repo.get_product_catalog_by_id(db, clone_request.source_product_id)
    
    if not source:
        raise NotFoundException(
            f"Source product {clone_request.source_product_id} not found"
        )
    
    # Clone the base product
    cloned_product = repo.clone_product_catalog(
        db,
        clone_request.source_product_id,
        clone_request.new_product_code,
        clone_request.new_product_name,
        created_by
    )
    
    # Clone features if requested
    if clone_request.include_features:
        source_features = feature_repo.get_features_by_product(
            db, clone_request.source_product_id
        )
        
        for feature in source_features:
            # Create feature data for clone
            feature_data = {
                'product_id': cloned_product.id,
                'feature_code': feature.feature_code,
                'feature_name': feature.feature_name,
                'description': feature.description,
                'feature_type': feature.feature_type,
                'feature_category': feature.feature_category,
                'coverage_amount': feature.coverage_amount,
                'coverage_limit': feature.coverage_limit,
                'deductible_amount': feature.deductible_amount,
                'copay_percentage': feature.copay_percentage,
                'waiting_period_days': feature.waiting_period_days,
                'benefit_period_days': feature.benefit_period_days,
                'min_age': feature.min_age,
                'max_age': feature.max_age,
                'is_mandatory': feature.is_mandatory,
                'is_taxable': feature.is_taxable,
                'requires_underwriting': feature.requires_underwriting,
                'base_price': feature.base_price
            }
            
            # Note: Would need to import and use feature service/repo here
            # feature_repo.create_product_feature(db, feature_data, created_by)
    
    logger.info(
        f"Product cloned: {source.id} -> {cloned_product.id} "
        f"by user {created_by}"
    )
    
    return ProductCatalogResponse.model_validate(cloned_product)


# ================================================================
# BULK OPERATIONS
# ================================================================

def bulk_update_products(
    db: Session,
    product_ids: List[UUID],
    update_data: ProductCatalogUpdate,
    updated_by: Optional[UUID] = None
) -> List[ProductCatalogResponse]:
    """
    Update multiple products in bulk
    
    Args:
        db: Database session
        product_ids: List of product UUIDs
        update_data: Update data to apply
        updated_by: User ID performing update
        
    Returns:
        List of updated products
    """
    updated_products = []
    errors = []
    
    for product_id in product_ids:
        try:
            updated = update_product_with_validation(
                db, product_id, update_data, updated_by
            )
            updated_products.append(updated)
        except Exception as e:
            errors.append({
                "product_id": str(product_id),
                "error": str(e)
            })
            logger.error(f"Failed to update product {product_id}: {str(e)}")
    
    if errors:
        logger.warning(
            f"Bulk update completed with {len(errors)} errors out of "
            f"{len(product_ids)} products"
        )
    
    return updated_products


def bulk_activate_products(
    db: Session,
    product_ids: List[UUID],
    activated_by: Optional[UUID] = None
) -> Dict[str, Any]:
    """
    Activate multiple products
    
    Args:
        db: Database session
        product_ids: List of product UUIDs
        activated_by: User ID activating products
        
    Returns:
        Summary of activation results
    """
    results = {
        "activated": [],
        "failed": [],
        "total": len(product_ids)
    }
    
    for product_id in product_ids:
        try:
            activated = activate_product(
                db, product_id, activated_by=activated_by
            )
            results["activated"].append(str(product_id))
        except Exception as e:
            results["failed"].append({
                "product_id": str(product_id),
                "error": str(e)
            })
    
    results["activated_count"] = len(results["activated"])
    results["failed_count"] = len(results["failed"])
    
    return results


# ================================================================
# ANALYTICS & REPORTING
# ================================================================

def get_product_analytics(
    db: Session,
    product_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Get comprehensive analytics for a product
    
    Args:
        db: Database session
        product_id: Product UUID
        start_date: Analytics start date
        end_date: Analytics end date
        
    Returns:
        Product analytics data
    """
    product = repo.get_product_catalog_by_id(db, product_id)
    
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    # Get basic statistics
    stats = repo.get_product_statistics(db)
    
    # Get feature statistics
    feature_stats = feature_repo.get_feature_statistics(db, product_id)
    
    # Get plan statistics
    plan_stats = plan_repo.get_plan_statistics(db, product_id)
    
    # Get pricing range
    pricing = plan_repo.get_plan_price_range(db, product_id)
    
    analytics = {
        "product": {
            "id": str(product.id),
            "name": product.product_name,
            "code": product.product_code,
            "type": product.product_type,
            "category": product.product_category,
            "status": product.status,
            "created_at": product.created_at.isoformat(),
            "days_active": (datetime.now().date() - product.created_at.date()).days
        },
        "features": feature_stats,
        "plans": plan_stats,
        "pricing": pricing,
        "overall_statistics": stats
    }
    
    # Add time-based analytics if dates provided
    if start_date and end_date:
        analytics["period"] = {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": (end_date - start_date).days
        }
    
    return analytics


def get_portfolio_summary(
    db: Session,
    include_inactive: bool = False
) -> Dict[str, Any]:
    """
    Get summary of entire product portfolio
    
    Args:
        db: Database session
        include_inactive: Include inactive products
        
    Returns:
        Portfolio summary statistics
    """
    stats = repo.get_product_statistics(db)
    
    # Get products by status
    all_products = repo.get_products_list(db)["products"]
    
    status_breakdown = {}
    for product in all_products:
        status = product.status
        if status not in status_breakdown:
            status_breakdown[status] = 0
        status_breakdown[status] += 1
    
    return {
        "total_products": stats["total_products"],
        "active_products": stats["active_products"],
        "inactive_products": stats["inactive_products"],
        "by_type": stats["by_type"],
        "by_category": stats["by_category"],
        "by_status": status_breakdown,
        "summary": {
            "activation_rate": (
                stats["active_products"] / stats["total_products"] * 100
                if stats["total_products"] > 0 else 0
            )
        }
    }


def get_products_requiring_review(
    db: Session,
    days_until_expiry: int = 30
) -> List[Dict[str, Any]]:
    """
    Get products that need review or action
    
    Args:
        db: Database session
        days_until_expiry: Days threshold for expiry warning
        
    Returns:
        List of products requiring attention
    """
    products_needing_review = []
    
    # Get all active products
    active_products = repo.get_active_products(db)
    
    expiry_threshold = date.today() + timedelta(days=days_until_expiry)
    
    for product in active_products:
        review_reasons = []
        
        # Check expiry date
        if product.expiry_date and product.expiry_date <= expiry_threshold:
            review_reasons.append(
                f"Expires in {(product.expiry_date - date.today()).days} days"
            )
        
        # Check if product has no features
        features = feature_repo.get_features_by_product(db, product.id)
        if not features:
            review_reasons.append("No features configured")
        
        # Check if product has no plans
        plans = plan_repo.get_plans_by_product(db, product.id)
        if not plans:
            review_reasons.append("No plans configured")
        
        # Check if pending approval for too long
        if product.status == ProductStatus.PENDING_APPROVAL:
            days_pending = (datetime.now().date() - product.updated_at.date()).days
            if days_pending > 7:
                review_reasons.append(f"Pending approval for {days_pending} days")
        
        if review_reasons:
            products_needing_review.append({
                "product_id": str(product.id),
                "product_name": product.product_name,
                "product_code": product.product_code,
                "status": product.status,
                "review_reasons": review_reasons
            })
    
    return products_needing_review


# ================================================================
# VALIDATION & COMPLIANCE
# ================================================================

def validate_product_completeness(
    db: Session,
    product_id: UUID
) -> Dict[str, Any]:
    """
    Validate if a product is complete and ready for sale
    
    Args:
        db: Database session
        product_id: Product UUID
        
    Returns:
        Validation results with missing components
    """
    product = repo.get_product_catalog_by_id(db, product_id)
    
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    validation_results = {
        "product_id": str(product_id),
        "is_complete": True,
        "missing_components": [],
        "warnings": [],
        "validation_timestamp": datetime.utcnow().isoformat()
    }
    
    # Check basic product information
    if not product.description:
        validation_results["warnings"].append("Product description is missing")
    
    # Check features
    features = feature_repo.get_features_by_product(db, product_id)
    if not features:
        validation_results["is_complete"] = False
        validation_results["missing_components"].append("No features configured")
    else:
        mandatory_features = [f for f in features if f.is_mandatory]
        if not mandatory_features:
            validation_results["warnings"].append(
                "No mandatory features defined"
            )
    
    # Check plans
    plans = plan_repo.get_plans_by_product(db, product_id)
    if not plans:
        validation_results["is_complete"] = False
        validation_results["missing_components"].append("No plans configured")
    else:
        active_plans = [p for p in plans if p.status == 'active']
        if not active_plans:
            validation_results["warnings"].append("No active plans available")
    
    # Check dates
    if product.expiry_date and product.expiry_date < date.today():
        validation_results["is_complete"] = False
        validation_results["missing_components"].append("Product has expired")
    
    # Check underwriting requirements
    if product.requires_underwriting:
        validation_results["warnings"].append(
            "Product requires underwriting process"
        )
    
    return validation_results


def check_regulatory_compliance(
    db: Session,
    product_id: UUID,
    region: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check if product meets regulatory requirements
    
    Args:
        db: Database session
        product_id: Product UUID
        region: Regulatory region to check
        
    Returns:
        Compliance check results
    """
    product = repo.get_product_catalog_by_id(db, product_id)
    
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    compliance_results = {
        "product_id": str(product_id),
        "is_compliant": True,
        "compliance_issues": [],
        "recommendations": [],
        "check_timestamp": datetime.utcnow().isoformat()
    }
    
    # Basic compliance checks
    if product.product_type in [ProductType.HEALTH, ProductType.LIFE]:
        # Check waiting periods
        features = feature_repo.get_features_by_product(db, product_id)
        has_waiting_period = any(
            f.waiting_period_days and f.waiting_period_days > 0 
            for f in features
        )
        
        if not has_waiting_period:
            compliance_results["recommendations"].append(
                "Consider adding waiting periods for pre-existing conditions"
            )
    
    # Check age limits
    if not product.min_age_limit or not product.max_age_limit:
        compliance_results["compliance_issues"].append(
            "Age limits not defined"
        )
        compliance_results["is_compliant"] = False
    
    # Region-specific checks
    if region:
        compliance_results["region"] = region
        # Add region-specific validation logic here
    
    return compliance_results


# ================================================================
# END OF SERVICE
# ================================================================