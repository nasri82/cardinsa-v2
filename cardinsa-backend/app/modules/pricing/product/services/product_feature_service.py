# app/modules/pricing/product/services/product_feature_service.py

"""
Product Feature Service

Business logic layer for Product Feature management.
Handles feature configuration, pricing, and eligibility.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.modules.pricing.product.repositories import product_feature_repository as repo
from app.modules.pricing.product.repositories import product_catalog_repository as product_repo
from app.modules.pricing.product.schemas.product_feature_schema import (
    ProductFeatureCreate,
    ProductFeatureUpdate,
    ProductFeatureFilter,
    ProductFeatureResponse,
    ProductFeatureListResponse,
    FeaturePricingRequest,
    FeaturePricingResponse,
    FeatureStatus,
    FeatureType,
    FeatureCategory
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
# FEATURE CREATION & MANAGEMENT
# ================================================================

def create_feature_with_validation(
    db: Session,
    feature_data: ProductFeatureCreate,
    created_by: Optional[UUID] = None
) -> ProductFeatureResponse:
    """
    Create a new product feature with validation
    
    Args:
        db: Database session
        feature_data: Feature creation data
        created_by: User ID creating the feature
        
    Returns:
        Created feature response
        
    Raises:
        ValidationException: If validation fails
        ConflictException: If feature code exists
    """
    try:
        # Verify product exists
        product = product_repo.get_product_catalog_by_id(db, feature_data.product_id)
        if not product:
            raise NotFoundException(
                f"Product with ID {feature_data.product_id} not found"
            )
        
        # Validate feature data
        _validate_feature_data(feature_data, product)
        
        # Check for duplicate feature code
        existing = repo.get_feature_by_code(
            db, feature_data.product_id, feature_data.feature_code
        )
        if existing:
            raise ConflictException(
                f"Feature with code '{feature_data.feature_code}' "
                f"already exists for this product"
            )
        
        # Create the feature
        feature = repo.create_product_feature(db, feature_data, created_by)
        
        logger.info(
            f"Feature created: {feature.id} - {feature.feature_name} "
            f"for product {feature_data.product_id} by user {created_by}"
        )
        
        return ProductFeatureResponse.model_validate(feature)
        
    except (ConflictException, ValidationException, NotFoundException) as e:
        logger.warning(f"Feature creation validation failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating feature: {str(e)}")
        raise BadRequestException(f"Failed to create feature: {str(e)}")


def _validate_feature_data(
    feature_data: ProductFeatureCreate,
    product: Any
) -> None:
    """
    Validate feature data against product configuration
    
    Args:
        feature_data: Feature data to validate
        product: Parent product
        
    Raises:
        ValidationException: If validation fails
    """
    # Validate age limits against product limits
    if product.min_age_limit and feature_data.min_age:
        if feature_data.min_age < product.min_age_limit:
            raise ValidationException(
                f"Feature minimum age {feature_data.min_age} is below "
                f"product minimum {product.min_age_limit}"
            )
    
    if product.max_age_limit and feature_data.max_age:
        if feature_data.max_age > product.max_age_limit:
            raise ValidationException(
                f"Feature maximum age {feature_data.max_age} exceeds "
                f"product maximum {product.max_age_limit}"
            )
    
    # Validate coverage limits
    if feature_data.coverage_amount and feature_data.coverage_limit:
        if feature_data.coverage_amount > feature_data.coverage_limit:
            raise ValidationException(
                "Coverage amount cannot exceed coverage limit"
            )
    
    # Validate deductible and copay
    if feature_data.copay_percentage:
        if feature_data.copay_percentage < 0 or feature_data.copay_percentage > 100:
            raise ValidationException(
                "Copay percentage must be between 0 and 100"
            )
    
    # Validate waiting and benefit periods
    if feature_data.waiting_period_days and feature_data.benefit_period_days:
        if feature_data.waiting_period_days >= feature_data.benefit_period_days:
            raise ValidationException(
                "Waiting period must be less than benefit period"
            )
    
    # Type-specific validations
    if feature_data.feature_type == FeatureType.MANDATORY:
        if not feature_data.is_mandatory:
            logger.warning(
                "Feature type is MANDATORY but is_mandatory flag is False"
            )
            feature_data.is_mandatory = True


def create_features_bulk(
    db: Session,
    product_id: UUID,
    features_data: List[ProductFeatureCreate],
    created_by: Optional[UUID] = None
) -> List[ProductFeatureResponse]:
    """
    Create multiple features for a product
    
    Args:
        db: Database session
        product_id: Product UUID
        features_data: List of feature creation data
        created_by: User ID creating features
        
    Returns:
        List of created features
    """
    # Verify product exists
    product = product_repo.get_product_catalog_by_id(db, product_id)
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    created_features = []
    errors = []
    
    for feature_data in features_data:
        try:
            # Ensure product_id is set
            feature_data.product_id = product_id
            
            feature = create_feature_with_validation(
                db, feature_data, created_by
            )
            created_features.append(feature)
        except Exception as e:
            errors.append({
                "feature_code": feature_data.feature_code,
                "error": str(e)
            })
            logger.error(
                f"Failed to create feature {feature_data.feature_code}: {str(e)}"
            )
    
    if errors:
        logger.warning(
            f"Bulk feature creation completed with {len(errors)} errors "
            f"out of {len(features_data)} features"
        )
    
    return created_features


# ================================================================
# FEATURE RETRIEVAL & SEARCH
# ================================================================

def get_feature_details(
    db: Session,
    feature_id: UUID,
    include_pricing: bool = True
) -> Dict[str, Any]:
    """
    Get comprehensive feature details
    
    Args:
        db: Database session
        feature_id: Feature UUID
        include_pricing: Include pricing information
        
    Returns:
        Feature details with additional information
    """
    feature = repo.get_product_feature_by_id(db, feature_id)
    
    if not feature:
        raise NotFoundException(f"Feature with ID {feature_id} not found")
    
    result = {
        "feature": ProductFeatureResponse.model_validate(feature),
        "configuration": {
            "is_mandatory": feature.is_mandatory,
            "requires_underwriting": feature.requires_underwriting,
            "is_taxable": feature.is_taxable,
            "waiting_period_days": feature.waiting_period_days,
            "benefit_period_days": feature.benefit_period_days
        }
    }
    
    # Add pricing information if requested
    if include_pricing and feature.base_price:
        pricing_info = {
            "base_price": float(feature.base_price),
            "currency": "USD",  # Could be from product configuration
            "tax_applicable": feature.is_taxable,
            "pricing_factors": []
        }
        
        if feature.min_age and feature.max_age:
            pricing_info["pricing_factors"].append({
                "factor": "age_based",
                "min_age": feature.min_age,
                "max_age": feature.max_age
            })
        
        if feature.coverage_limit:
            pricing_info["pricing_factors"].append({
                "factor": "coverage_based",
                "max_coverage": float(feature.coverage_limit)
            })
        
        result["pricing"] = pricing_info
    
    # Add coverage details
    coverage = {
        "coverage_amount": float(feature.coverage_amount) if feature.coverage_amount else None,
        "coverage_limit": float(feature.coverage_limit) if feature.coverage_limit else None,
        "deductible": float(feature.deductible_amount) if feature.deductible_amount else None,
        "copay_percentage": float(feature.copay_percentage) if feature.copay_percentage else None
    }
    result["coverage"] = coverage
    
    return result


def get_features_by_product(
    db: Session,
    product_id: UUID,
    feature_type: Optional[FeatureType] = None,
    mandatory_only: bool = False
) -> List[ProductFeatureResponse]:
    """
    Get all features for a product
    
    Args:
        db: Database session
        product_id: Product UUID
        feature_type: Optional filter by type
        mandatory_only: Only return mandatory features
        
    Returns:
        List of product features
    """
    if mandatory_only:
        features = repo.get_mandatory_features(db, product_id)
    else:
        features = repo.get_features_by_product(
            db, product_id, feature_type
        )
    
    return [
        ProductFeatureResponse.model_validate(f) 
        for f in features
    ]


def search_features(
    db: Session,
    filters: Optional[ProductFeatureFilter] = None,
    page: int = 1,
    page_size: int = 50
) -> ProductFeatureListResponse:
    """
    Search features with filtering and pagination
    
    Args:
        db: Database session
        filters: Search filters
        page: Page number
        page_size: Items per page
        
    Returns:
        Paginated feature list
    """
    skip = (page - 1) * page_size
    
    result = repo.get_features_list(
        db, filters, skip, page_size
    )
    
    features = [
        ProductFeatureResponse.model_validate(f)
        for f in result["features"]
    ]
    
    return ProductFeatureListResponse(
        features=features,
        total_count=result["total_count"],
        page=page,
        page_size=page_size,
        total_pages=result["total_pages"]
    )


def get_features_by_category(
    db: Session,
    product_id: UUID,
    category: FeatureCategory
) -> Dict[str, List[ProductFeatureResponse]]:
    """
    Get features grouped by type within a category
    
    Args:
        db: Database session
        product_id: Product UUID
        category: Feature category
        
    Returns:
        Features grouped by type
    """
    filters = ProductFeatureFilter(
        product_id=product_id,
        feature_category=category
    )
    
    result = repo.get_features_list(db, filters, limit=1000)
    features = result["features"]
    
    grouped = {
        "mandatory": [],
        "optional": [],
        "rider": [],
        "addon": []
    }
    
    for feature in features:
        response = ProductFeatureResponse.model_validate(feature)
        
        if feature.is_mandatory:
            grouped["mandatory"].append(response)
        elif feature.feature_type == FeatureType.RIDER:
            grouped["rider"].append(response)
        elif feature.feature_type == FeatureType.ADDON:
            grouped["addon"].append(response)
        else:
            grouped["optional"].append(response)
    
    return grouped


# ================================================================
# FEATURE UPDATE & LIFECYCLE
# ================================================================

def update_feature_with_validation(
    db: Session,
    feature_id: UUID,
    update_data: ProductFeatureUpdate,
    updated_by: Optional[UUID] = None
) -> ProductFeatureResponse:
    """
    Update feature with validation
    
    Args:
        db: Database session
        feature_id: Feature UUID
        update_data: Update data
        updated_by: User ID updating feature
        
    Returns:
        Updated feature response
    """
    feature = repo.get_product_feature_by_id(db, feature_id)
    
    if not feature:
        raise NotFoundException(f"Feature with ID {feature_id} not found")
    
    # Validate status transitions
    if update_data.status:
        _validate_feature_status_transition(feature.status, update_data.status)
    
    # Validate age limits
    if update_data.min_age and update_data.max_age:
        if update_data.min_age > update_data.max_age:
            raise ValidationException(
                "Minimum age cannot be greater than maximum age"
            )
    
    # Validate dates
    if update_data.effective_date and update_data.expiry_date:
        if update_data.expiry_date <= update_data.effective_date:
            raise ValidationException(
                "Expiry date must be after effective date"
            )
    
    # Update the feature
    updated_feature = repo.update_product_feature(
        db, feature_id, update_data, updated_by
    )
    
    logger.info(f"Feature updated: {feature_id} by user {updated_by}")
    
    return ProductFeatureResponse.model_validate(updated_feature)


def _validate_feature_status_transition(
    current_status: FeatureStatus,
    new_status: FeatureStatus
) -> None:
    """
    Validate feature status transitions
    
    Args:
        current_status: Current status
        new_status: New status
        
    Raises:
        ValidationException: If transition invalid
    """
    valid_transitions = {
        FeatureStatus.ACTIVE: [
            FeatureStatus.INACTIVE,
            FeatureStatus.SUSPENDED,
            FeatureStatus.DEPRECATED
        ],
        FeatureStatus.INACTIVE: [
            FeatureStatus.ACTIVE,
            FeatureStatus.DEPRECATED
        ],
        FeatureStatus.PENDING: [
            FeatureStatus.ACTIVE,
            FeatureStatus.INACTIVE
        ],
        FeatureStatus.SUSPENDED: [
            FeatureStatus.ACTIVE,
            FeatureStatus.INACTIVE,
            FeatureStatus.DEPRECATED
        ],
        FeatureStatus.DEPRECATED: []  # No transitions from deprecated
    }
    
    allowed = valid_transitions.get(current_status, [])
    
    if new_status not in allowed:
        raise ValidationException(
            f"Invalid status transition from {current_status} to {new_status}"
        )


def activate_feature(
    db: Session,
    feature_id: UUID,
    activated_by: Optional[UUID] = None
) -> ProductFeatureResponse:
    """
    Activate a feature
    
    Args:
        db: Database session
        feature_id: Feature UUID
        activated_by: User ID activating
        
    Returns:
        Activated feature
    """
    update_data = ProductFeatureUpdate(
        status=FeatureStatus.ACTIVE,
        effective_date=date.today()
    )
    
    return update_feature_with_validation(
        db, feature_id, update_data, activated_by
    )


def deactivate_feature(
    db: Session,
    feature_id: UUID,
    reason: str,
    deactivated_by: Optional[UUID] = None
) -> ProductFeatureResponse:
    """
    Deactivate a feature
    
    Args:
        db: Database session
        feature_id: Feature UUID
        reason: Deactivation reason
        deactivated_by: User ID deactivating
        
    Returns:
        Deactivated feature
    """
    update_data = ProductFeatureUpdate(
        status=FeatureStatus.INACTIVE,
        feature_metadata={"deactivation_reason": reason}
    )
    
    updated = update_feature_with_validation(
        db, feature_id, update_data, deactivated_by
    )
    
    logger.warning(
        f"Feature deactivated: {feature_id} - Reason: {reason} "
        f"by user {deactivated_by}"
    )
    
    return updated


# ================================================================
# PRICING CALCULATIONS
# ================================================================

def calculate_feature_price(
    db: Session,
    pricing_request: FeaturePricingRequest
) -> FeaturePricingResponse:
    """
    Calculate price for a feature with all factors
    
    Args:
        db: Database session
        pricing_request: Pricing calculation request
        
    Returns:
        Detailed pricing response
    """
    feature = repo.get_product_feature_by_id(db, pricing_request.feature_id)
    
    if not feature:
        raise NotFoundException(
            f"Feature with ID {pricing_request.feature_id} not found"
        )
    
    # Get base price
    base_price = feature.base_price or Decimal('0')
    adjusted_price = base_price
    calculation_details = {
        "base_price": float(base_price),
        "factors_applied": []
    }
    
    # Apply age-based pricing
    if pricing_request.age:
        age_factor = _calculate_age_factor(
            pricing_request.age,
            feature.min_age,
            feature.max_age
        )
        adjusted_price *= age_factor
        calculation_details["factors_applied"].append({
            "type": "age",
            "value": pricing_request.age,
            "factor": float(age_factor)
        })
    
    # Apply coverage-based pricing
    if pricing_request.coverage_amount and feature.coverage_limit:
        coverage_factor = _calculate_coverage_factor(
            pricing_request.coverage_amount,
            feature.coverage_limit
        )
        adjusted_price *= coverage_factor
        calculation_details["factors_applied"].append({
            "type": "coverage",
            "amount": float(pricing_request.coverage_amount),
            "factor": float(coverage_factor)
        })
    
    # Apply discounts if requested
    discount_amount = Decimal('0')
    if pricing_request.apply_discounts:
        # Could integrate with discount service
        discount_rate = Decimal('0.1')  # 10% discount example
        discount_amount = adjusted_price * discount_rate
        calculation_details["discount"] = {
            "rate": float(discount_rate),
            "amount": float(discount_amount)
        }
    
    # Apply taxes if requested
    tax_amount = Decimal('0')
    if pricing_request.apply_taxes and feature.is_taxable:
        tax_rate = Decimal('0.15')  # 15% tax example
        tax_amount = (adjusted_price - discount_amount) * tax_rate
        calculation_details["tax"] = {
            "rate": float(tax_rate),
            "amount": float(tax_amount)
        }
    
    final_price = adjusted_price - discount_amount + tax_amount
    
    return FeaturePricingResponse(
        feature_id=pricing_request.feature_id,
        base_price=base_price,
        adjusted_price=adjusted_price,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        final_price=final_price,
        currency="USD",
        calculation_details=calculation_details
    )


def _calculate_age_factor(
    age: int,
    min_age: Optional[int],
    max_age: Optional[int]
) -> Decimal:
    """
    Calculate age-based pricing factor
    
    Args:
        age: Insured age
        min_age: Minimum allowed age
        max_age: Maximum allowed age
        
    Returns:
        Age factor multiplier
    """
    # Validate age range
    if min_age and age < min_age:
        raise ValidationException(f"Age {age} is below minimum {min_age}")
    if max_age and age > max_age:
        raise ValidationException(f"Age {age} exceeds maximum {max_age}")
    
    # Age-based factor calculation
    if age <= 30:
        return Decimal('1.0')
    elif age <= 40:
        return Decimal('1.1')
    elif age <= 50:
        return Decimal('1.3')
    elif age <= 60:
        return Decimal('1.6')
    else:
        return Decimal('2.0')


def _calculate_coverage_factor(
    coverage_amount: Decimal,
    coverage_limit: Decimal
) -> Decimal:
    """
    Calculate coverage-based pricing factor
    
    Args:
        coverage_amount: Requested coverage
        coverage_limit: Maximum coverage
        
    Returns:
        Coverage factor multiplier
    """
    if coverage_amount > coverage_limit:
        raise ValidationException(
            f"Coverage {coverage_amount} exceeds limit {coverage_limit}"
        )
    
    coverage_ratio = coverage_amount / coverage_limit
    
    # Progressive factor based on coverage ratio
    if coverage_ratio <= Decimal('0.5'):
        return Decimal('1.0')
    elif coverage_ratio <= Decimal('0.75'):
        return Decimal('1.2')
    else:
        return Decimal('1.5')


def calculate_bundle_price(
    db: Session,
    product_id: UUID,
    feature_ids: List[UUID],
    age: Optional[int] = None,
    apply_bundle_discount: bool = True
) -> Dict[str, Any]:
    """
    Calculate price for a bundle of features
    
    Args:
        db: Database session
        product_id: Product UUID
        feature_ids: List of feature UUIDs
        age: Insured age
        apply_bundle_discount: Apply bundling discount
        
    Returns:
        Bundle pricing details
    """
    # Get mandatory features
    mandatory_features = repo.get_mandatory_features(db, product_id)
    mandatory_ids = [f.id for f in mandatory_features]
    
    # Combine with selected features
    all_feature_ids = list(set(mandatory_ids + feature_ids))
    
    total_price = Decimal('0')
    feature_prices = []
    
    for feature_id in all_feature_ids:
        try:
            pricing_request = FeaturePricingRequest(
                feature_id=feature_id,
                age=age,
                apply_discounts=False,  # Apply bundle discount later
                apply_taxes=False  # Apply tax on total
            )
            
            price_response = calculate_feature_price(db, pricing_request)
            
            feature = repo.get_product_feature_by_id(db, feature_id)
            
            feature_prices.append({
                "feature_id": str(feature_id),
                "feature_name": feature.feature_name,
                "is_mandatory": feature_id in mandatory_ids,
                "base_price": float(price_response.base_price),
                "adjusted_price": float(price_response.adjusted_price)
            })
            
            total_price += price_response.adjusted_price
            
        except Exception as e:
            logger.error(f"Error calculating price for feature {feature_id}: {e}")
    
    # Apply bundle discount
    bundle_discount = Decimal('0')
    if apply_bundle_discount and len(all_feature_ids) > 3:
        # Progressive discount based on bundle size
        discount_rate = min(Decimal('0.05') * (len(all_feature_ids) - 3), Decimal('0.25'))
        bundle_discount = total_price * discount_rate
    
    # Apply tax on discounted total
    tax_rate = Decimal('0.15')
    tax_amount = (total_price - bundle_discount) * tax_rate
    
    final_total = total_price - bundle_discount + tax_amount
    
    return {
        "product_id": str(product_id),
        "feature_count": len(all_feature_ids),
        "mandatory_count": len(mandatory_ids),
        "optional_count": len(all_feature_ids) - len(mandatory_ids),
        "features": feature_prices,
        "subtotal": float(total_price),
        "bundle_discount": float(bundle_discount),
        "tax_amount": float(tax_amount),
        "total": float(final_total),
        "currency": "USD"
    }


# ================================================================
# ELIGIBILITY & VALIDATION
# ================================================================

def check_feature_eligibility(
    db: Session,
    feature_id: UUID,
    age: int,
    has_pre_existing: bool = False
) -> Dict[str, Any]:
    """
    Check if a person is eligible for a feature
    
    Args:
        db: Database session
        feature_id: Feature UUID
        age: Person's age
        has_pre_existing: Has pre-existing conditions
        
    Returns:
        Eligibility results
    """
    feature = repo.get_product_feature_by_id(db, feature_id)
    
    if not feature:
        raise NotFoundException(f"Feature with ID {feature_id} not found")
    
    eligibility = {
        "feature_id": str(feature_id),
        "feature_name": feature.feature_name,
        "is_eligible": True,
        "restrictions": [],
        "requirements": [],
        "waiting_periods": []
    }
    
    # Check age eligibility
    if feature.min_age and age < feature.min_age:
        eligibility["is_eligible"] = False
        eligibility["restrictions"].append(
            f"Minimum age requirement: {feature.min_age} years"
        )
    
    if feature.max_age and age > feature.max_age:
        eligibility["is_eligible"] = False
        eligibility["restrictions"].append(
            f"Maximum age limit: {feature.max_age} years"
        )
    
    # Check underwriting requirements
    if feature.requires_underwriting:
        eligibility["requirements"].append("Medical underwriting required")
        
        if has_pre_existing:
            eligibility["requirements"].append(
                "Pre-existing conditions must be declared"
            )
    
    # Add waiting periods
    if feature.waiting_period_days:
        eligibility["waiting_periods"].append({
            "type": "general",
            "days": feature.waiting_period_days,
            "description": f"General waiting period of {feature.waiting_period_days} days"
        })
    
    if has_pre_existing and feature.feature_category == FeatureCategory.MEDICAL:
        # Additional waiting for pre-existing conditions
        eligibility["waiting_periods"].append({
            "type": "pre_existing",
            "days": 365,  # Example: 1 year for pre-existing
            "description": "Pre-existing condition waiting period"
        })
    
    return eligibility


def validate_feature_configuration(
    db: Session,
    product_id: UUID
) -> Dict[str, Any]:
    """
    Validate feature configuration for a product
    
    Args:
        db: Database session
        product_id: Product UUID
        
    Returns:
        Validation results
    """
    features = repo.get_features_by_product(db, product_id)
    
    validation = {
        "product_id": str(product_id),
        "is_valid": True,
        "total_features": len(features),
        "issues": [],
        "warnings": [],
        "statistics": {}
    }
    
    if not features:
        validation["is_valid"] = False
        validation["issues"].append("No features configured")
        return validation
    
    # Check for mandatory features
    mandatory_features = [f for f in features if f.is_mandatory]
    validation["statistics"]["mandatory_features"] = len(mandatory_features)
    
    if not mandatory_features:
        validation["warnings"].append("No mandatory features defined")
    
    # Check for feature diversity
    categories = set(f.feature_category for f in features)
    validation["statistics"]["categories_covered"] = len(categories)
    
    if len(categories) < 3:
        validation["warnings"].append(
            f"Limited feature diversity: only {len(categories)} categories"
        )
    
    # Check for pricing
    priced_features = [f for f in features if f.base_price and f.base_price > 0]
    validation["statistics"]["priced_features"] = len(priced_features)
    
    if len(priced_features) < len(features):
        validation["warnings"].append(
            f"{len(features) - len(priced_features)} features have no pricing"
        )
    
    # Check for conflicts
    for feature in features:
        # Check age range consistency
        if feature.min_age and feature.max_age:
            if feature.min_age > feature.max_age:
                validation["issues"].append(
                    f"Feature {feature.feature_code}: Invalid age range"
                )
                validation["is_valid"] = False
    
    return validation


# ================================================================
# ANALYTICS & REPORTING
# ================================================================

def get_feature_analytics(
    db: Session,
    product_id: UUID
) -> Dict[str, Any]:
    """
    Get analytics for product features
    
    Args:
        db: Database session
        product_id: Product UUID
        
    Returns:
        Feature analytics
    """
    features = repo.get_features_by_product(db, product_id)
    stats = repo.get_feature_statistics(db, product_id)
    
    # Calculate pricing analytics
    prices = [float(f.base_price) for f in features if f.base_price]
    
    analytics = {
        "product_id": str(product_id),
        "statistics": stats,
        "pricing": {
            "average_price": sum(prices) / len(prices) if prices else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "total_value": sum(prices)
        },
        "coverage": {},
        "distribution": {}
    }
    
    # Analyze coverage
    coverage_amounts = [
        float(f.coverage_amount) 
        for f in features 
        if f.coverage_amount
    ]
    
    if coverage_amounts:
        analytics["coverage"] = {
            "average_coverage": sum(coverage_amounts) / len(coverage_amounts),
            "max_coverage": max(coverage_amounts),
            "total_coverage": sum(coverage_amounts)
        }
    
    # Analyze distribution
    analytics["distribution"] = {
        "by_type": {},
        "by_category": {},
        "by_requirement": {
            "mandatory": len([f for f in features if f.is_mandatory]),
            "optional": len([f for f in features if not f.is_mandatory]),
            "underwriting_required": len(
                [f for f in features if f.requires_underwriting]
            )
        }
    }
    
    # Group by type
    for feature in features:
        feat_type = feature.feature_type
        if feat_type not in analytics["distribution"]["by_type"]:
            analytics["distribution"]["by_type"][feat_type] = 0
        analytics["distribution"]["by_type"][feat_type] += 1
    
    # Group by category
    for feature in features:
        category = feature.feature_category
        if category not in analytics["distribution"]["by_category"]:
            analytics["distribution"]["by_category"][category] = 0
        analytics["distribution"]["by_category"][category] += 1
    
    return analytics


def get_popular_feature_combinations(
    db: Session,
    product_id: UUID,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Get popular feature combinations (mock implementation)
    
    Args:
        db: Database session
        product_id: Product UUID
        limit: Number of combinations to return
        
    Returns:
        Popular feature combinations
    """
    # Get all features
    features = repo.get_features_by_product(db, product_id)
    mandatory_features = [f for f in features if f.is_mandatory]
    optional_features = [f for f in features if not f.is_mandatory]
    
    # Create sample combinations
    combinations = []
    
    # Basic package - mandatory only
    if mandatory_features:
        basic_price = sum(
            float(f.base_price) for f in mandatory_features 
            if f.base_price
        )
        combinations.append({
            "name": "Basic Package",
            "description": "Essential coverage only",
            "features": [f.feature_name for f in mandatory_features],
            "feature_count": len(mandatory_features),
            "estimated_price": basic_price,
            "popularity_score": 85
        })
    
    # Standard package - mandatory + popular optionals
    if optional_features:
        popular_optionals = optional_features[:2]
        standard_features = mandatory_features + popular_optionals
        standard_price = sum(
            float(f.base_price) for f in standard_features 
            if f.base_price
        )
        combinations.append({
            "name": "Standard Package",
            "description": "Balanced coverage with popular add-ons",
            "features": [f.feature_name for f in standard_features],
            "feature_count": len(standard_features),
            "estimated_price": standard_price,
            "popularity_score": 95
        })
    
    # Premium package - all features
    if len(features) > len(mandatory_features):
        premium_price = sum(
            float(f.base_price) for f in features 
            if f.base_price
        )
        combinations.append({
            "name": "Premium Package",
            "description": "Comprehensive coverage with all features",
            "features": [f.feature_name for f in features],
            "feature_count": len(features),
            "estimated_price": premium_price,
            "popularity_score": 70
        })
    
    # Sort by popularity and limit
    combinations.sort(key=lambda x: x["popularity_score"], reverse=True)
    
    return combinations[:limit]


# ================================================================
# BULK OPERATIONS
# ================================================================

def bulk_update_features(
    db: Session,
    feature_ids: List[UUID],
    update_data: ProductFeatureUpdate,
    updated_by: Optional[UUID] = None
) -> Dict[str, Any]:
    """
    Bulk update multiple features
    
    Args:
        db: Database session
        feature_ids: List of feature UUIDs
        update_data: Update data to apply
        updated_by: User performing update
        
    Returns:
        Update results summary
    """
    results = {
        "updated": [],
        "failed": [],
        "total": len(feature_ids)
    }
    
    for feature_id in feature_ids:
        try:
            updated = update_feature_with_validation(
                db, feature_id, update_data, updated_by
            )
            results["updated"].append(str(feature_id))
        except Exception as e:
            results["failed"].append({
                "feature_id": str(feature_id),
                "error": str(e)
            })
            logger.error(f"Failed to update feature {feature_id}: {e}")
    
    results["updated_count"] = len(results["updated"])
    results["failed_count"] = len(results["failed"])
    
    return results


def copy_features_to_product(
    db: Session,
    source_product_id: UUID,
    target_product_id: UUID,
    feature_codes: Optional[List[str]] = None,
    created_by: Optional[UUID] = None
) -> List[ProductFeatureResponse]:
    """
    Copy features from one product to another
    
    Args:
        db: Database session
        source_product_id: Source product UUID
        target_product_id: Target product UUID
        feature_codes: Specific features to copy (None = all)
        created_by: User performing copy
        
    Returns:
        List of copied features
    """
    # Verify both products exist
    source_product = product_repo.get_product_catalog_by_id(db, source_product_id)
    if not source_product:
        raise NotFoundException(f"Source product {source_product_id} not found")
    
    target_product = product_repo.get_product_catalog_by_id(db, target_product_id)
    if not target_product:
        raise NotFoundException(f"Target product {target_product_id} not found")
    
    # Get source features
    source_features = repo.get_features_by_product(db, source_product_id)
    
    # Filter by codes if specified
    if feature_codes:
        source_features = [
            f for f in source_features 
            if f.feature_code in feature_codes
        ]
    
    copied_features = []
    
    for feature in source_features:
        try:
            # Check if feature already exists in target
            existing = repo.get_feature_by_code(
                db, target_product_id, feature.feature_code
            )
            
            if existing:
                logger.warning(
                    f"Feature {feature.feature_code} already exists in target"
                )
                continue
            
            # Create feature data for copy
            feature_data = ProductFeatureCreate(
                product_id=target_product_id,
                feature_code=feature.feature_code,
                feature_name=feature.feature_name,
                description=feature.description,
                feature_type=feature.feature_type,
                feature_category=feature.feature_category,
                coverage_amount=feature.coverage_amount,
                coverage_limit=feature.coverage_limit,
                deductible_amount=feature.deductible_amount,
                copay_percentage=feature.copay_percentage,
                waiting_period_days=feature.waiting_period_days,
                benefit_period_days=feature.benefit_period_days,
                min_age=feature.min_age,
                max_age=feature.max_age,
                is_mandatory=feature.is_mandatory,
                is_taxable=feature.is_taxable,
                requires_underwriting=feature.requires_underwriting,
                base_price=feature.base_price,
                feature_metadata=feature.feature_metadata,
                tags=feature.tags
            )
            
            copied = create_feature_with_validation(
                db, feature_data, created_by
            )
            copied_features.append(copied)
            
        except Exception as e:
            logger.error(
                f"Failed to copy feature {feature.feature_code}: {e}"
            )
    
    logger.info(
        f"Copied {len(copied_features)} features from product "
        f"{source_product_id} to {target_product_id}"
    )
    
    return copied_features


# ================================================================
# END OF SERVICE
# ================================================================