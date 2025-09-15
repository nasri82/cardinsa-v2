# app/modules/benefits/schemas/benefit_preapproval_rule_schema.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class BenefitPreapprovalRuleBase(BaseModel):
    rule_name: str
    description: Optional[str]
    criteria: Optional[dict]
    is_mandatory: Optional[bool] = True

class BenefitPreapprovalRuleCreate(BenefitPreapprovalRuleBase):
    pass

class BenefitPreapprovalRuleUpdate(BenefitPreapprovalRuleBase):
    pass

class BenefitPreapprovalRuleOut(BenefitPreapprovalRuleBase):
    id: UUID
    schedule_id: UUID

    class Config:
        orm_mode = True
