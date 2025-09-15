from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class ProductFeatureBase(BaseModel):
    name_en: str
    name_ar: Optional[str]
    description: Optional[str]
    is_optional: Optional[bool] = True


class ProductFeatureCreate(ProductFeatureBase):
    product_id: UUID


class ProductFeatureUpdate(ProductFeatureBase):
    pass


class ProductFeatureRead(ProductFeatureBase):
    id: UUID
    product_id: UUID

    class Config:
        orm_mode = True
