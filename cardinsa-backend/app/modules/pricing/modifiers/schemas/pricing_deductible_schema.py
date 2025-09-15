from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class PricingDeductibleBase(BaseModel):
    code: str
    label: str
    amount: Decimal
    currency: Optional[str] = "USD"
    is_active: Optional[bool] = True

class PricingDeductibleCreate(PricingDeductibleBase):
    pass

class PricingDeductibleUpdate(PricingDeductibleBase):
    pass

class PricingDeductible(PricingDeductibleBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        orm_mode = True
