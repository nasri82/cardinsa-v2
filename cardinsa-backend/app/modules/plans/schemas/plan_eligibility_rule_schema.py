# app/modules/plans/schemas/plan_eligibility_rule_schema.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date

class PlanEligibilityRuleBase(BaseModel):
    rule_name: str
    rule_category: str  # age, occupation, medical, financial, etc.
    eligibility_criteria: dict
    is_mandatory: Optional[bool] = True
    effective_date: Optional[date]
    expiry_date: Optional[date]

class PlanEligibilityRuleCreate(PlanEligibilityRuleBase):
    pass

class PlanEligibilityRuleUpdate(PlanEligibilityRuleBase):
    pass

class PlanEligibilityRuleOut(PlanEligibilityRuleBase):
    id: UUID
    plan_id: UUID

    class Config:
        orm_mode = True
