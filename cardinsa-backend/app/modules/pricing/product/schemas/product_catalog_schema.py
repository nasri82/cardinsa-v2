from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
from .product_feature_schema import ProductFeatureRead


class ProductCatalogBase(BaseModel):
    name_en: str
    name_ar: Optional[str]
    description: Optional[str]
    product_type: str  # e.g. medical, motor, life
    is_active: Optional[bool] = True


class ProductCatalogCreate(ProductCatalogBase):
    pass


class ProductCatalogUpdate(ProductCatalogBase):
    pass


class ProductCatalogRead(ProductCatalogBase):
    id: UUID
    features: Optional[List[ProductFeatureRead]] = []

    class Config:
        orm_mode = True
