from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class PricingCopaymentBase(BaseModel):
    code: str
    label: str
    percentage: Decimal
    description: Optional[str] = None
    is_active: Optional[bool] = True

class PricingCopaymentCreate(PricingCopaymentBase):
    pass

class PricingCopaymentUpdate(PricingCopaymentBase):
    pass

class PricingCopayment(PricingCopaymentBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        orm_mode = True
