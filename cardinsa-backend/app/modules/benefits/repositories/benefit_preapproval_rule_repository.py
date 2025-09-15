# app/modules/benefits/repositories/benefit_preapproval_rule_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.benefits.models.benefit_preapproval_rule_model import BenefitPreapprovalRule
from uuid import UUID

async def get_preapproval_rules_by_schedule(session: AsyncSession, schedule_id: UUID) -> list[BenefitPreapprovalRule]:
    result = await session.execute(
        select(BenefitPreapprovalRule).where(BenefitPreapprovalRule.schedule_id == schedule_id)
    )
    return result.scalars().all()

async def create_preapproval_rule(session: AsyncSession, rule: BenefitPreapprovalRule) -> BenefitPreapprovalRule:
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule

async def delete_preapproval_rule(session: AsyncSession, rule: BenefitPreapprovalRule) -> None:
    await session.delete(rule)
    await session.commit()
