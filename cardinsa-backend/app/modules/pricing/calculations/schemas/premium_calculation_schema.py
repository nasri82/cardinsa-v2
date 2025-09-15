from pydantic import BaseModel

from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from decimal import Decimal


class ApprovalStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class PremiumCalculationBase(BaseModel):
    quotation_id: UUID
    profile_id: UUID
    base_premium: Optional[float] = 0
    age_loading: Optional[float] = 0
    region_loading: Optional[float] = 0
    deductible_amount: Optional[float] = 0
    discount_amount: Optional[float] = 0
    surcharge_amount: Optional[float] = 0
    tax_amount: Optional[float] = 0
    final_premium: Optional[float] = 0


class PremiumCalculationCreate(PremiumCalculationBase):
    pass


class PremiumCalculationUpdate(BaseModel):
    approval_status: Optional[ApprovalStatusEnum]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]


class PremiumCalculationOut(PremiumCalculationBase):
    id: UUID
    approval_status: ApprovalStatusEnum
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True

# In premium_calculation_schema.py


class PremiumOverrideCreate(BaseModel):
    override_reason: str
    new_premium: Decimal
    justification: str

class CalculationBreakdownOut(BaseModel):
    calculation_id: UUID
    base_premium: Decimal
    risk_adjustments: Dict[str, Any]
    component_breakdown: Dict[str, Decimal]
    age_adjustments: Optional[Dict[str, Decimal]]
    industry_loadings: Optional[Dict[str, Decimal]]
    final_premium: Decimal
    
class CalculationPerformanceMetrics(BaseModel):
    calculation_time_ms: float
    rules_evaluated: int
    components_processed: int
    engine_version: str