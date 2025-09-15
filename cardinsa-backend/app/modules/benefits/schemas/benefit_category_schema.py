from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class BenefitCategoryBase(BaseModel):
    name: str
    name_ar: Optional[str]
    name_fr: Optional[str]
    category_code: Optional[str]
    parent_id: Optional[UUID]
    order_index: Optional[str]
    is_active: Optional[bool] = True
    calculation_basis: Optional[str]
    regulatory_tag: Optional[str]


class BenefitCategoryCreate(BenefitCategoryBase):
    pass


class BenefitCategoryUpdate(BenefitCategoryBase):
    pass


class BenefitCategoryOut(BenefitCategoryBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


    class Config:
        orm_mode = True