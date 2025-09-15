from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class PricingIndustryAdjustmentBase(BaseModel):
    industry_code: str
    adjustment_factor: Decimal
    description: Optional[str] = None
    is_active: Optional[bool] = True

class PricingIndustryAdjustmentCreate(PricingIndustryAdjustmentBase):
    pass

class PricingIndustryAdjustmentUpdate(PricingIndustryAdjustmentBase):
    pass

class PricingIndustryAdjustment(PricingIndustryAdjustmentBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        orm_mode = True
