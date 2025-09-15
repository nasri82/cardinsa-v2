# app/modules/benefits/schemas/benefit_condition_schema.py

from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID

class BenefitConditionBase(BaseModel):
    condition_type: str
    operator: str
    value: Any
    priority: Optional[int]
    group_id: Optional[UUID]

class BenefitConditionCreate(BenefitConditionBase):
    pass

class BenefitConditionUpdate(BenefitConditionBase):
    pass

class BenefitConditionOut(BenefitConditionBase):
    id: UUID
    schedule_id: UUID

    class Config:
        orm_mode = True
