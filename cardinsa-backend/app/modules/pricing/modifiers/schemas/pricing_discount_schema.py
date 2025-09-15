from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class PricingDiscountBase(BaseModel):
    code: str
    label: str
    percentage: Decimal
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True

class PricingDiscountCreate(PricingDiscountBase):
    pass

class PricingDiscountUpdate(PricingDiscountBase):
    pass

class PricingDiscount(PricingDiscountBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        orm_mode = True
