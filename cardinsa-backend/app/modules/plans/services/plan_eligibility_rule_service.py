# app/modules/plans/services/plan_eligibility_rule_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.plans.models.plan_eligibility_rule_model import PlanEligibilityRule
from app.modules.plans.schemas.plan_eligibility_rule_schema import PlanEligibilityRuleCreate
from app.modules.plans.repositories import plan_eligibility_rule_repository

async def list_eligibility_rules_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanEligibilityRule]:
    return await plan_eligibility_rule_repository.get_eligibility_rules_by_plan(session, plan_id)

async def create_eligibility_rule(session: AsyncSession, payload: PlanEligibilityRuleCreate, plan_id: UUID) -> PlanEligibilityRule:
    rule = PlanEligibilityRule(**payload.dict(), plan_id=plan_id)
    return await plan_eligibility_rule_repository.create_eligibility_rule(session, rule)
