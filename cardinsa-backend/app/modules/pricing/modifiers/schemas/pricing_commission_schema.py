from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class PricingCommissionBase(BaseModel):
    channel: str
    commission_type: str  # e.g. 'fixed' or 'percentage'
    value: Decimal
    currency: Optional[str] = "USD"
    is_active: Optional[bool] = True

class PricingCommissionCreate(PricingCommissionBase):
    pass

class PricingCommissionUpdate(PricingCommissionBase):
    pass

class PricingCommission(PricingCommissionBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        orm_mode = True
