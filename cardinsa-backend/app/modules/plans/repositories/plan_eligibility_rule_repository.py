# app/modules/plans/repositories/plan_eligibility_rule_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.plans.models.plan_eligibility_rule_model import PlanEligibilityRule
from uuid import UUID

async def get_eligibility_rules_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanEligibilityRule]:
    result = await session.execute(select(PlanEligibilityRule).where(PlanEligibilityRule.plan_id == plan_id))
    return result.scalars().all()

async def create_eligibility_rule(session: AsyncSession, rule: PlanEligibilityRule) -> PlanEligibilityRule:
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule

async def delete_eligibility_rule(session: AsyncSession, rule: PlanEligibilityRule) -> None:
    await session.delete(rule)
    await session.commit()
