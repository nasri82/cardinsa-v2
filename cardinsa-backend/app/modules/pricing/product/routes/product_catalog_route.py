from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.modules.pricing.product.schemas.product_catalog_schema import (
    ProductCatalogCreate, ProductCatalogRead, ProductCatalogUpdate
)
from app.modules.pricing.product.services.product_catalog_service import ProductCatalogService
from app.core.dependencies import get_db, require_permission_scoped

router = APIRouter(prefix="/product-catalog", tags=["Product Catalog"])
RESOURCE = "pricing.product_catalog"

@router.get("/", response_model=List[ProductCatalogRead])
def list_products(
    skip: int = 0,
    limit: int = Query(100, le=200),
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="read"))
):
    return ProductCatalogService(db).list(skip=skip, limit=limit)

@router.post("/", response_model=ProductCatalogRead)
def create_product(
    data: ProductCatalogCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="create"))
):
    return ProductCatalogService(db).create(data)

@router.get("/{id}", response_model=ProductCatalogRead)
def get_product(
    id: UUID,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="read"))
):
    service = ProductCatalogService(db)
    product = service.get(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{id}", response_model=ProductCatalogRead)
def update_product(
    id: UUID,
    data: ProductCatalogUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="update"))
):
    service = ProductCatalogService(db)
    updated = service.update(id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/{id}")
def delete_product(
    id: UUID,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="delete"))
):
    service = ProductCatalogService(db)
    service.delete(id)
    return {"message": "Deleted"}
