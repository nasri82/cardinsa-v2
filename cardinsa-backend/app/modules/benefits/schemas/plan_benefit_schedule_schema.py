# app/modules/benefits/schemas/plan_benefit_schedule_schema.py

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date
from .benefit_condition_schema import BenefitConditionOut
from .benefit_translation_schema import BenefitTranslationOut
from .benefit_preapproval_rule_schema import BenefitPreapprovalRuleOut

class PlanBenefitScheduleBase(BaseModel):
    name: str
    name_ar: Optional[str]
    description: Optional[str]
    description_ar: Optional[str]
    benefit_type_id: Optional[UUID]
    limit: Optional[float]
    deductible: Optional[float]
    copay: Optional[float]
    coinsurance: Optional[float]
    frequency_limit: Optional[int]
    waiting_period_days: Optional[int]
    requires_preapproval: Optional[bool] = False
    network_tier: Optional[str]
    display_order: Optional[int]
    is_active: Optional[bool] = True
    effective_date: Optional[date]
    expiry_date: Optional[date]
    metadata: Optional[dict]

class PlanBenefitScheduleCreate(PlanBenefitScheduleBase):
    pass

class PlanBenefitScheduleUpdate(PlanBenefitScheduleBase):
    pass

class PlanBenefitScheduleOut(PlanBenefitScheduleBase):
    id: UUID
    plan_id: UUID
    conditions: Optional[List[BenefitConditionOut]] = []
    translations: Optional[List[BenefitTranslationOut]] = []
    preapproval_rules: Optional[List[BenefitPreapprovalRuleOut]] = []

    class Config:
        orm_mode = True
