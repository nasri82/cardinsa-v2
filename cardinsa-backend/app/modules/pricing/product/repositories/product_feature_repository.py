# app/modules/pricing/product/repositories/product_feature_repository.py

"""
Product Feature Repository

Data access layer for Product Feature entities.
Handles all database operations for feature management.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.modules.pricing.product.models.product_feature_model import ProductFeature
from app.modules.pricing.product.schemas.product_feature_schema import (
    ProductFeatureCreate,
    ProductFeatureUpdate,
    ProductFeatureFilter,
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

class ConflictException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ================================================================
# CREATE OPERATIONS
# ================================================================

def create_product_feature(
    db: Session,
    feature_data: ProductFeatureCreate,
    created_by: Optional[UUID] = None
) -> ProductFeature:
    """
    Create a new product feature
    
    Args:
        db: Database session
        feature_data: Product feature creation data
        created_by: ID of the user creating the feature
        
    Returns:
        Created ProductFeature instance
        
    Raises:
        ConflictException: If feature code already exists for product
        BadRequestException: If data validation fails
    """
    try:
        # Check for duplicate feature code within the same product
        existing = db.query(ProductFeature).filter(
            and_(
                ProductFeature.product_id == feature_data.product_id,
                ProductFeature.feature_code == feature_data.feature_code,
                ProductFeature.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ConflictException(
                f"Feature with code '{feature_data.feature_code}' already exists for this product"
            )
        
        # Create new feature
        feature = ProductFeature(
            **feature_data.model_dump(exclude={'tags'}),
            created_by=created_by,
            created_at=datetime.utcnow(),
            status=FeatureStatus.ACTIVE
        )
        
        # Handle tags if provided
        if feature_data.tags:
            feature.tags = feature_data.tags
        
        db.add(feature)
        db.commit()
        db.refresh(feature)
        
        logger.info(f"Created product feature: {feature.id}")
        return feature
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        raise ConflictException("Feature creation failed due to data conflict")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product feature: {str(e)}")
        raise BadRequestException(f"Failed to create feature: {str(e)}")


def bulk_create_features(
    db: Session,
    features_data: List[ProductFeatureCreate],
    created_by: Optional[UUID] = None
) -> List[ProductFeature]:
    """
    Create multiple product features in bulk
    
    Args:
        db: Database session
        features_data: List of feature creation data
        created_by: ID of the user creating the features
        
    Returns:
        List of created ProductFeature instances
    """
    created_features = []
    
    try:
        for feature_data in features_data:
            feature = create_product_feature(db, feature_data, created_by)
            created_features.append(feature)
        
        logger.info(f"Bulk created {len(created_features)} features")
        return created_features
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk feature creation: {str(e)}")
        raise BadRequestException(f"Bulk creation failed: {str(e)}")


# ================================================================
# READ OPERATIONS
# ================================================================

def get_product_feature_by_id(
    db: Session,
    feature_id: UUID,
    include_deleted: bool = False
) -> Optional[ProductFeature]:
    """
    Get product feature by ID
    
    Args:
        db: Database session
        feature_id: Feature UUID
        include_deleted: Include soft-deleted records
        
    Returns:
        ProductFeature instance or None
    """
    query = db.query(ProductFeature).filter(ProductFeature.id == feature_id)
    
    if not include_deleted:
        query = query.filter(ProductFeature.is_deleted == False)
    
    return query.first()


def get_features_by_product(
    db: Session,
    product_id: UUID,
    feature_type: Optional[FeatureType] = None,
    include_inactive: bool = False
) -> List[ProductFeature]:
    """
    Get all features for a specific product
    
    Args:
        db: Database session
        product_id: Product UUID
        feature_type: Optional feature type filter
        include_inactive: Include inactive features
        
    Returns:
        List of ProductFeature instances
    """
    query = db.query(ProductFeature).filter(
        and_(
            ProductFeature.product_id == product_id,
            ProductFeature.is_deleted == False
        )
    )
    
    if not include_inactive:
        query = query.filter(ProductFeature.status == FeatureStatus.ACTIVE)
    
    if feature_type:
        query = query.filter(ProductFeature.feature_type == feature_type)
    
    return query.order_by(ProductFeature.feature_code).all()


def get_mandatory_features(
    db: Session,
    product_id: UUID
) -> List[ProductFeature]:
    """
    Get all mandatory features for a product
    
    Args:
        db: Database session
        product_id: Product UUID
        
    Returns:
        List of mandatory ProductFeature instances
    """
    return db.query(ProductFeature).filter(
        and_(
            ProductFeature.product_id == product_id,
            ProductFeature.is_mandatory == True,
            ProductFeature.status == FeatureStatus.ACTIVE,
            ProductFeature.is_deleted == False
        )
    ).all()


def get_features_list(
    db: Session,
    filters: Optional[ProductFeatureFilter] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Get paginated list of features with filters
    
    Args:
        db: Database session
        filters: Filter criteria
        skip: Number of records to skip
        limit: Maximum number of records to return
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        Dictionary containing features list and pagination info
    """
    query = db.query(ProductFeature).filter(ProductFeature.is_deleted == False)
    
    # Apply filters
    if filters:
        if filters.product_id:
            query = query.filter(ProductFeature.product_id == filters.product_id)
        
        if filters.feature_type:
            query = query.filter(ProductFeature.feature_type == filters.feature_type)
        
        if filters.feature_category:
            query = query.filter(ProductFeature.feature_category == filters.feature_category)
        
        if filters.status:
            query = query.filter(ProductFeature.status == filters.status)
        
        if filters.is_mandatory is not None:
            query = query.filter(ProductFeature.is_mandatory == filters.is_mandatory)
        
        if filters.is_taxable is not None:
            query = query.filter(ProductFeature.is_taxable == filters.is_taxable)
        
        if filters.requires_underwriting is not None:
            query = query.filter(
                ProductFeature.requires_underwriting == filters.requires_underwriting
            )
        
        if filters.min_coverage_amount is not None:
            query = query.filter(
                ProductFeature.coverage_amount >= filters.min_coverage_amount
            )
        
        if filters.max_coverage_amount is not None:
            query = query.filter(
                ProductFeature.coverage_amount <= filters.max_coverage_amount
            )
        
        if filters.search_term:
            search_pattern = f"%{filters.search_term}%"
            query = query.filter(
                or_(
                    ProductFeature.feature_code.ilike(search_pattern),
                    ProductFeature.feature_name.ilike(search_pattern),
                    ProductFeature.description.ilike(search_pattern)
                )
            )
        
        if filters.tags:
            query = query.filter(
                ProductFeature.tags.contains(filters.tags)
            )
        
        if filters.effective_date_from:
            query = query.filter(ProductFeature.effective_date >= filters.effective_date_from)
        
        if filters.effective_date_to:
            query = query.filter(ProductFeature.effective_date <= filters.effective_date_to)
    
    # Get total count
    total_count = query.count()
    
    # Apply sorting
    if hasattr(ProductFeature, sort_by):
        order_column = getattr(ProductFeature, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    
    # Apply pagination
    features = query.offset(skip).limit(limit).all()
    
    return {
        "features": features,
        "total_count": total_count,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "total_pages": (total_count + limit - 1) // limit
    }


def get_feature_by_code(
    db: Session,
    product_id: UUID,
    feature_code: str
) -> Optional[ProductFeature]:
    """
    Get feature by product ID and feature code
    
    Args:
        db: Database session
        product_id: Product UUID
        feature_code: Feature code
        
    Returns:
        ProductFeature instance or None
    """
    return db.query(ProductFeature).filter(
        and_(
            ProductFeature.product_id == product_id,
            ProductFeature.feature_code == feature_code.upper(),
            ProductFeature.is_deleted == False
        )
    ).first()


# ================================================================
# UPDATE OPERATIONS
# ================================================================

def update_product_feature(
    db: Session,
    feature_id: UUID,
    update_data: ProductFeatureUpdate,
    updated_by: Optional[UUID] = None
) -> ProductFeature:
    """
    Update product feature
    
    Args:
        db: Database session
        feature_id: Feature UUID
        update_data: Update data
        updated_by: ID of the user updating the feature
        
    Returns:
        Updated ProductFeature instance
        
    Raises:
        NotFoundException: If feature not found
        BadRequestException: If update fails
    """
    feature = get_product_feature_by_id(db, feature_id)
    
    if not feature:
        raise NotFoundException(f"Feature with ID {feature_id} not found")
    
    try:
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(feature, field, value)
        
        feature.updated_at = datetime.utcnow()
        feature.updated_by = updated_by
        
        db.commit()
        db.refresh(feature)
        
        logger.info(f"Updated product feature: {feature_id}")
        return feature
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating feature: {str(e)}")
        raise BadRequestException(f"Failed to update feature: {str(e)}")


def bulk_update_features(
    db: Session,
    feature_ids: List[UUID],
    update_data: ProductFeatureUpdate,
    updated_by: Optional[UUID] = None
) -> List[ProductFeature]:
    """
    Update multiple features in bulk
    
    Args:
        db: Database session
        feature_ids: List of feature UUIDs
        update_data: Update data to apply
        updated_by: ID of the user updating the features
        
    Returns:
        List of updated ProductFeature instances
    """
    updated_features = []
    
    try:
        for feature_id in feature_ids:
            feature = update_product_feature(db, feature_id, update_data, updated_by)
            updated_features.append(feature)
        
        logger.info(f"Bulk updated {len(updated_features)} features")
        return updated_features
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk update: {str(e)}")
        raise BadRequestException(f"Bulk update failed: {str(e)}")


# ================================================================
# DELETE OPERATIONS
# ================================================================

def delete_product_feature(
    db: Session,
    feature_id: UUID,
    soft_delete: bool = True,
    deleted_by: Optional[UUID] = None
) -> bool:
    """
    Delete product feature (soft or hard delete)
    
    Args:
        db: Database session
        feature_id: Feature UUID
        soft_delete: If True, perform soft delete
        deleted_by: ID of the user deleting the feature
        
    Returns:
        True if deleted successfully
        
    Raises:
        NotFoundException: If feature not found
    """
    feature = get_product_feature_by_id(db, feature_id, include_deleted=False)
    
    if not feature:
        raise NotFoundException(f"Feature with ID {feature_id} not found")
    
    try:
        if soft_delete:
            feature.is_deleted = True
            feature.deleted_at = datetime.utcnow()
            feature.deleted_by = deleted_by
            feature.status = FeatureStatus.INACTIVE
        else:
            db.delete(feature)
        
        db.commit()
        
        logger.info(f"{'Soft' if soft_delete else 'Hard'} deleted feature: {feature_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting feature: {str(e)}")
        raise BadRequestException(f"Failed to delete feature: {str(e)}")


def delete_features_by_product(
    db: Session,
    product_id: UUID,
    soft_delete: bool = True,
    deleted_by: Optional[UUID] = None
) -> int:
    """
    Delete all features for a product
    
    Args:
        db: Database session
        product_id: Product UUID
        soft_delete: If True, perform soft delete
        deleted_by: ID of the user deleting the features
        
    Returns:
        Number of features deleted
    """
    try:
        if soft_delete:
            result = db.query(ProductFeature).filter(
                and_(
                    ProductFeature.product_id == product_id,
                    ProductFeature.is_deleted == False
                )
            ).update({
                'is_deleted': True,
                'deleted_at': datetime.utcnow(),
                'deleted_by': deleted_by,
                'status': FeatureStatus.INACTIVE
            })
        else:
            result = db.query(ProductFeature).filter(
                ProductFeature.product_id == product_id
            ).delete()
        
        db.commit()
        
        logger.info(f"Deleted {result} features for product {product_id}")
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting features: {str(e)}")
        raise BadRequestException(f"Failed to delete features: {str(e)}")


# ================================================================
# PRICING OPERATIONS
# ================================================================

def calculate_feature_price(
    db: Session,
    feature_id: UUID,
    age: Optional[int] = None,
    coverage_amount: Optional[Decimal] = None
) -> Dict[str, Any]:
    """
    Calculate price for a feature based on parameters
    
    Args:
        db: Database session
        feature_id: Feature UUID
        age: Age of insured
        coverage_amount: Coverage amount requested
        
    Returns:
        Dictionary containing pricing details
        
    Raises:
        NotFoundException: If feature not found
    """
    feature = get_product_feature_by_id(db, feature_id)
    
    if not feature:
        raise NotFoundException(f"Feature with ID {feature_id} not found")
    
    # Basic pricing calculation
    base_price = feature.base_price or Decimal('0')
    adjusted_price = base_price
    
    # Age adjustment
    age_factor = Decimal('1.0')
    if age and feature.min_age and feature.max_age:
        if age < feature.min_age or age > feature.max_age:
            raise BadRequestException(
                f"Age {age} is outside the allowed range ({feature.min_age}-{feature.max_age})"
            )
        # Simple age factor calculation (can be enhanced)
        if age > 50:
            age_factor = Decimal('1.2')
        elif age > 40:
            age_factor = Decimal('1.1')
    
    adjusted_price *= age_factor
    
    # Coverage amount adjustment
    coverage_factor = Decimal('1.0')
    if coverage_amount and feature.coverage_limit:
        if coverage_amount > feature.coverage_limit:
            raise BadRequestException(
                f"Coverage amount {coverage_amount} exceeds limit {feature.coverage_limit}"
            )
        # Simple coverage factor (can be enhanced)
        coverage_ratio = coverage_amount / feature.coverage_limit
        coverage_factor = Decimal('1') + (coverage_ratio * Decimal('0.1'))
    
    adjusted_price *= coverage_factor
    
    # Tax calculation
    tax_amount = Decimal('0')
    if feature.is_taxable:
        tax_rate = Decimal('0.1')  # 10% tax (configurable)
        tax_amount = adjusted_price * tax_rate
    
    final_price = adjusted_price + tax_amount
    
    return {
        "feature_id": feature_id,
        "base_price": float(base_price),
        "adjusted_price": float(adjusted_price),
        "tax_amount": float(tax_amount),
        "final_price": float(final_price),
        "factors": {
            "age_factor": float(age_factor),
            "coverage_factor": float(coverage_factor)
        }
    }


def get_total_features_price(
    db: Session,
    product_id: UUID,
    selected_feature_ids: Optional[List[UUID]] = None,
    age: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate total price for product features
    
    Args:
        db: Database session
        product_id: Product UUID
        selected_feature_ids: List of selected optional feature IDs
        age: Age of insured
        
    Returns:
        Dictionary containing total pricing details
    """
    # Get mandatory features
    mandatory_features = get_mandatory_features(db, product_id)
    
    total_price = Decimal('0')
    feature_prices = []
    
    # Calculate mandatory features price
    for feature in mandatory_features:
        price_info = calculate_feature_price(db, feature.id, age)
        total_price += Decimal(str(price_info['final_price']))
        feature_prices.append({
            "feature_id": feature.id,
            "feature_name": feature.feature_name,
            "is_mandatory": True,
            "price": price_info['final_price']
        })
    
    # Calculate selected optional features price
    if selected_feature_ids:
        for feature_id in selected_feature_ids:
            feature = get_product_feature_by_id(db, feature_id)
            if feature and feature.product_id == product_id:
                price_info = calculate_feature_price(db, feature_id, age)
                total_price += Decimal(str(price_info['final_price']))
                feature_prices.append({
                    "feature_id": feature.id,
                    "feature_name": feature.feature_name,
                    "is_mandatory": False,
                    "price": price_info['final_price']
                })
    
    return {
        "product_id": product_id,
        "total_price": float(total_price),
        "feature_breakdown": feature_prices,
        "mandatory_count": len(mandatory_features),
        "optional_count": len(selected_feature_ids) if selected_feature_ids else 0
    }


# ================================================================
# STATISTICS OPERATIONS
# ================================================================

def get_feature_statistics(
    db: Session,
    product_id: Optional[UUID] = None
) -> Dict[str, Any]:
    """
    Get feature statistics
    
    Args:
        db: Database session
        product_id: Optional product filter
        
    Returns:
        Dictionary containing feature statistics
    """
    try:
        query = db.query(ProductFeature).filter(ProductFeature.is_deleted == False)
        
        if product_id:
            query = query.filter(ProductFeature.product_id == product_id)
        
        total_features = query.count()
        
        active_features = query.filter(
            ProductFeature.status == FeatureStatus.ACTIVE
        ).count()
        
        mandatory_features = query.filter(
            ProductFeature.is_mandatory == True
        ).count()
        
        features_by_type = db.query(
            ProductFeature.feature_type,
            func.count(ProductFeature.id)
        ).filter(
            ProductFeature.is_deleted == False
        )
        
        if product_id:
            features_by_type = features_by_type.filter(
                ProductFeature.product_id == product_id
            )
        
        features_by_type = features_by_type.group_by(ProductFeature.feature_type).all()
        
        features_by_category = db.query(
            ProductFeature.feature_category,
            func.count(ProductFeature.id)
        ).filter(
            ProductFeature.is_deleted == False
        )
        
        if product_id:
            features_by_category = features_by_category.filter(
                ProductFeature.product_id == product_id
            )
        
        features_by_category = features_by_category.group_by(
            ProductFeature.feature_category
        ).all()
        
        return {
            "total_features": total_features,
            "active_features": active_features,
            "inactive_features": total_features - active_features,
            "mandatory_features": mandatory_features,
            "optional_features": total_features - mandatory_features,
            "by_type": dict(features_by_type),
            "by_category": dict(features_by_category)
        }
        
    except Exception as e:
        logger.error(f"Error getting feature statistics: {str(e)}")
        raise BadRequestException(f"Failed to get statistics: {str(e)}")


# ================================================================
# END OF REPOSITORY
# ================================================================