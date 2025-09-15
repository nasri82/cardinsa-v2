from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.modules.pricing.product.schemas.product_feature_schema import (
    ProductFeatureCreate, ProductFeatureRead, ProductFeatureUpdate
)
from app.modules.pricing.product.services.product_feature_service import ProductFeatureService
from app.core.dependencies import get_db, require_permission_scoped

router = APIRouter(prefix="/product-features", tags=["Product Features"])
RESOURCE = "pricing.product_feature"

@router.post("/", response_model=ProductFeatureRead)
def create_feature(
    data: ProductFeatureCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="create"))
):
    return ProductFeatureService(db).create(data)

@router.get("/by-product/{product_id}", response_model=List[ProductFeatureRead])
def list_features_by_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="read"))
):
    return ProductFeatureService(db).list_by_product(product_id)

@router.put("/{id}", response_model=ProductFeatureRead)
def update_feature(
    id: UUID,
    data: ProductFeatureUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="update"))
):
    service = ProductFeatureService(db)
    updated = service.update(id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Feature not found")
    return updated

@router.delete("/{id}")
def delete_feature(
    id: UUID,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="delete"))
):
    service = ProductFeatureService(db)
    success = service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"message": "Deleted"}
