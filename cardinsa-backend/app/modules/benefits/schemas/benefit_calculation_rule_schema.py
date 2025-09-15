from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from datetime import date, datetime


class BenefitCalculationRuleBase(BaseModel):
    benefit_category_id: Optional[UUID]
    rule_name: str
    rule_description: Optional[str]
    calculation_formula: Optional[str]
    parameters: Optional[Dict[str, float]]
    effective_date: Optional[date]
    expiry_date: Optional[date]


class BenefitCalculationRuleCreate(BenefitCalculationRuleBase):
    pass


class BenefitCalculationRuleUpdate(BenefitCalculationRuleBase):
    pass


class BenefitCalculationRuleOut(BenefitCalculationRuleBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


    class Config:
        orm_mode = True