# app/modules/pricing/product/repositories/product_catalog_repository.py

"""
Product Catalog Repository

Data access layer for Product Catalog entities.
Handles all database operations for product management.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select, update, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.modules.pricing.product.models.product_catalog_model import ProductCatalog
from app.modules.pricing.product.schemas.product_catalog_schema import (
    ProductCatalogCreate,
    ProductCatalogUpdate,
    ProductCatalogFilter,
    ProductStatusEnum as ProductStatus
)
from app.core.database import get_db
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Define custom exceptions or use HTTPException
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

def create_product_catalog(
    db: Session,
    product_data: ProductCatalogCreate,
    created_by: Optional[UUID] = None
) -> ProductCatalog:
    """
    Create a new product catalog entry
    
    Args:
        db: Database session
        product_data: Product catalog creation data
        created_by: ID of the user creating the product
        
    Returns:
        Created ProductCatalog instance
        
    Raises:
        ConflictException: If product code already exists
        BadRequestException: If data validation fails
    """
    try:
        # Check for duplicate product code
        existing = db.query(ProductCatalog).filter(
            and_(
                ProductCatalog.product_code == product_data.product_code,
                ProductCatalog.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ConflictException(
                f"Product with code '{product_data.product_code}' already exists"
            )
        
        # Create new product
        product = ProductCatalog(
            **product_data.model_dump(exclude={'tags'}),
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        
        # Handle tags if provided
        if product_data.tags:
            product.tags = product_data.tags
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        logger.info(f"Created product catalog: {product.id}")
        return product
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        raise ConflictException("Product creation failed due to data conflict")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product catalog: {str(e)}")
        raise BadRequestException(f"Failed to create product: {str(e)}")


def bulk_create_products(
    db: Session,
    products_data: List[ProductCatalogCreate],
    created_by: Optional[UUID] = None
) -> List[ProductCatalog]:
    """
    Create multiple product catalogs in bulk
    
    Args:
        db: Database session
        products_data: List of product creation data
        created_by: ID of the user creating the products
        
    Returns:
        List of created ProductCatalog instances
    """
    created_products = []
    
    try:
        for product_data in products_data:
            product = create_product_catalog(db, product_data, created_by)
            created_products.append(product)
        
        logger.info(f"Bulk created {len(created_products)} products")
        return created_products
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk product creation: {str(e)}")
        raise BadRequestException(f"Bulk creation failed: {str(e)}")


# ================================================================
# READ OPERATIONS
# ================================================================

def get_product_catalog_by_id(
    db: Session,
    product_id: UUID,
    include_deleted: bool = False
) -> Optional[ProductCatalog]:
    """
    Get product catalog by ID
    
    Args:
        db: Database session
        product_id: Product UUID
        include_deleted: Include soft-deleted records
        
    Returns:
        ProductCatalog instance or None
    """
    query = db.query(ProductCatalog).filter(ProductCatalog.id == product_id)
    
    if not include_deleted:
        query = query.filter(ProductCatalog.is_deleted == False)
    
    return query.first()


def get_product_by_code(
    db: Session,
    product_code: str,
    include_deleted: bool = False
) -> Optional[ProductCatalog]:
    """
    Get product catalog by product code
    
    Args:
        db: Database session
        product_code: Unique product code
        include_deleted: Include soft-deleted records
        
    Returns:
        ProductCatalog instance or None
    """
    query = db.query(ProductCatalog).filter(
        ProductCatalog.product_code == product_code.upper()
    )
    
    if not include_deleted:
        query = query.filter(ProductCatalog.is_deleted == False)
    
    return query.first()


def get_products_list(
    db: Session,
    filters: Optional[ProductCatalogFilter] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Get paginated list of products with filters
    
    Args:
        db: Database session
        filters: Filter criteria
        skip: Number of records to skip
        limit: Maximum number of records to return
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        Dictionary containing products list and pagination info
    """
    query = db.query(ProductCatalog).filter(ProductCatalog.is_deleted == False)
    
    # Apply filters
    if filters:
        if filters.product_type:
            query = query.filter(ProductCatalog.product_type == filters.product_type)
        
        if filters.product_category:
            query = query.filter(ProductCatalog.product_category == filters.product_category)
        
        if filters.status:
            query = query.filter(ProductCatalog.status == filters.status)
        
        if filters.is_active is not None:
            query = query.filter(ProductCatalog.is_active == filters.is_active)
        
        if filters.requires_underwriting is not None:
            query = query.filter(
                ProductCatalog.requires_underwriting == filters.requires_underwriting
            )
        
        if filters.search_term:
            search_pattern = f"%{filters.search_term}%"
            query = query.filter(
                or_(
                    ProductCatalog.product_code.ilike(search_pattern),
                    ProductCatalog.product_name.ilike(search_pattern),
                    ProductCatalog.description.ilike(search_pattern)
                )
            )
        
        if filters.tags:
            query = query.filter(
                ProductCatalog.tags.contains(filters.tags)
            )
        
        if filters.min_age_limit is not None:
            query = query.filter(ProductCatalog.min_age_limit >= filters.min_age_limit)
        
        if filters.max_age_limit is not None:
            query = query.filter(ProductCatalog.max_age_limit <= filters.max_age_limit)
        
        if filters.effective_date_from:
            query = query.filter(ProductCatalog.effective_date >= filters.effective_date_from)
        
        if filters.effective_date_to:
            query = query.filter(ProductCatalog.effective_date <= filters.effective_date_to)
    
    # Get total count
    total_count = query.count()
    
    # Apply sorting
    if hasattr(ProductCatalog, sort_by):
        order_column = getattr(ProductCatalog, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    
    # Apply pagination
    products = query.offset(skip).limit(limit).all()
    
    return {
        "products": products,
        "total_count": total_count,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "total_pages": (total_count + limit - 1) // limit
    }


def get_active_products(
    db: Session,
    product_category: Optional[str] = None
) -> List[ProductCatalog]:
    """
    Get all active products, optionally filtered by category
    
    Args:
        db: Database session
        product_category: Optional category filter
        
    Returns:
        List of active ProductCatalog instances
    """
    query = db.query(ProductCatalog).filter(
        and_(
            ProductCatalog.is_active == True,
            ProductCatalog.is_deleted == False,
            ProductCatalog.status == ProductStatus.ACTIVE
        )
    )
    
    if product_category:
        query = query.filter(ProductCatalog.product_category == product_category)
    
    # Check effective dates
    current_date = date.today()
    query = query.filter(
        and_(
            or_(
                ProductCatalog.effective_date == None,
                ProductCatalog.effective_date <= current_date
            ),
            or_(
                ProductCatalog.expiry_date == None,
                ProductCatalog.expiry_date >= current_date
            )
        )
    )
    
    return query.all()


# ================================================================
# UPDATE OPERATIONS
# ================================================================

def update_product_catalog(
    db: Session,
    product_id: UUID,
    update_data: ProductCatalogUpdate,
    updated_by: Optional[UUID] = None
) -> ProductCatalog:
    """
    Update product catalog
    
    Args:
        db: Database session
        product_id: Product UUID
        update_data: Update data
        updated_by: ID of the user updating the product
        
    Returns:
        Updated ProductCatalog instance
        
    Raises:
        NotFoundException: If product not found
        BadRequestException: If update fails
    """
    product = get_product_catalog_by_id(db, product_id)
    
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    try:
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(product, field, value)
        
        product.updated_at = datetime.utcnow()
        product.updated_by = updated_by
        
        db.commit()
        db.refresh(product)
        
        logger.info(f"Updated product catalog: {product_id}")
        return product
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating product: {str(e)}")
        raise BadRequestException(f"Failed to update product: {str(e)}")


def bulk_update_products(
    db: Session,
    product_ids: List[UUID],
    update_data: ProductCatalogUpdate,
    updated_by: Optional[UUID] = None
) -> List[ProductCatalog]:
    """
    Update multiple products in bulk
    
    Args:
        db: Database session
        product_ids: List of product UUIDs
        update_data: Update data to apply
        updated_by: ID of the user updating the products
        
    Returns:
        List of updated ProductCatalog instances
    """
    updated_products = []
    
    try:
        for product_id in product_ids:
            product = update_product_catalog(db, product_id, update_data, updated_by)
            updated_products.append(product)
        
        logger.info(f"Bulk updated {len(updated_products)} products")
        return updated_products
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk update: {str(e)}")
        raise BadRequestException(f"Bulk update failed: {str(e)}")


# ================================================================
# DELETE OPERATIONS
# ================================================================

def delete_product_catalog(
    db: Session,
    product_id: UUID,
    soft_delete: bool = True,
    deleted_by: Optional[UUID] = None
) -> bool:
    """
    Delete product catalog (soft or hard delete)
    
    Args:
        db: Database session
        product_id: Product UUID
        soft_delete: If True, perform soft delete
        deleted_by: ID of the user deleting the product
        
    Returns:
        True if deleted successfully
        
    Raises:
        NotFoundException: If product not found
    """
    product = get_product_catalog_by_id(db, product_id, include_deleted=False)
    
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    
    try:
        if soft_delete:
            product.is_deleted = True
            product.deleted_at = datetime.utcnow()
            product.deleted_by = deleted_by
            product.status = ProductStatus.DISCONTINUED
        else:
            db.delete(product)
        
        db.commit()
        
        logger.info(f"{'Soft' if soft_delete else 'Hard'} deleted product: {product_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting product: {str(e)}")
        raise BadRequestException(f"Failed to delete product: {str(e)}")


def bulk_delete_products(
    db: Session,
    product_ids: List[UUID],
    soft_delete: bool = True,
    deleted_by: Optional[UUID] = None
) -> int:
    """
    Delete multiple products in bulk
    
    Args:
        db: Database session
        product_ids: List of product UUIDs
        soft_delete: If True, perform soft delete
        deleted_by: ID of the user deleting the products
        
    Returns:
        Number of products deleted
    """
    deleted_count = 0
    
    try:
        for product_id in product_ids:
            if delete_product_catalog(db, product_id, soft_delete, deleted_by):
                deleted_count += 1
        
        logger.info(f"Bulk deleted {deleted_count} products")
        return deleted_count
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk delete: {str(e)}")
        raise BadRequestException(f"Bulk delete failed: {str(e)}")


# ================================================================
# SPECIAL OPERATIONS
# ================================================================

def clone_product_catalog(
    db: Session,
    source_product_id: UUID,
    new_product_code: str,
    new_product_name: str,
    created_by: Optional[UUID] = None
) -> ProductCatalog:
    """
    Clone an existing product catalog with a new code and name
    
    Args:
        db: Database session
        source_product_id: Source product UUID
        new_product_code: New unique product code
        new_product_name: New product name
        created_by: ID of the user creating the clone
        
    Returns:
        Cloned ProductCatalog instance
        
    Raises:
        NotFoundException: If source product not found
        ConflictException: If new product code already exists
    """
    source_product = get_product_catalog_by_id(db, source_product_id)
    
    if not source_product:
        raise NotFoundException(f"Source product with ID {source_product_id} not found")
    
    # Check if new code already exists
    existing = get_product_by_code(db, new_product_code)
    if existing:
        raise ConflictException(f"Product with code '{new_product_code}' already exists")
    
    try:
        # Create clone
        clone_data = {
            key: value for key, value in source_product.__dict__.items()
            if not key.startswith('_') and key not in [
                'id', 'product_code', 'product_name', 
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ]
        }
        
        clone = ProductCatalog(
            **clone_data,
            product_code=new_product_code.upper(),
            product_name=new_product_name,
            created_by=created_by,
            created_at=datetime.utcnow(),
            status=ProductStatus.DRAFT  # Set clone as draft initially
        )
        
        db.add(clone)
        db.commit()
        db.refresh(clone)
        
        logger.info(f"Cloned product {source_product_id} to {clone.id}")
        return clone
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error cloning product: {str(e)}")
        raise BadRequestException(f"Failed to clone product: {str(e)}")


def get_product_statistics(db: Session) -> Dict[str, Any]:
    """
    Get product catalog statistics
    
    Args:
        db: Database session
        
    Returns:
        Dictionary containing product statistics
    """
    try:
        total_products = db.query(func.count(ProductCatalog.id)).filter(
            ProductCatalog.is_deleted == False
        ).scalar()
        
        active_products = db.query(func.count(ProductCatalog.id)).filter(
            and_(
                ProductCatalog.is_deleted == False,
                ProductCatalog.is_active == True,
                ProductCatalog.status == ProductStatus.ACTIVE
            )
        ).scalar()
        
        products_by_type = db.query(
            ProductCatalog.product_type,
            func.count(ProductCatalog.id)
        ).filter(
            ProductCatalog.is_deleted == False
        ).group_by(ProductCatalog.product_type).all()
        
        products_by_category = db.query(
            ProductCatalog.product_category,
            func.count(ProductCatalog.id)
        ).filter(
            ProductCatalog.is_deleted == False
        ).group_by(ProductCatalog.product_category).all()
        
        return {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": total_products - active_products,
            "by_type": dict(products_by_type),
            "by_category": dict(products_by_category)
        }
        
    except Exception as e:
        logger.error(f"Error getting product statistics: {str(e)}")
        raise BadRequestException(f"Failed to get statistics: {str(e)}")


# ================================================================
# END OF REPOSITORY
# ================================================================