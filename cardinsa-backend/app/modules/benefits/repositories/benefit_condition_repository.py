# app/modules/benefits/repositories/benefit_condition_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.benefits.models.benefit_condition_model import BenefitCondition
from uuid import UUID

async def get_conditions_by_schedule(session: AsyncSession, schedule_id: UUID) -> list[BenefitCondition]:
    result = await session.execute(
        select(BenefitCondition).where(BenefitCondition.schedule_id == schedule_id)
    )
    return result.scalars().all()

async def create_condition(session: AsyncSession, condition: BenefitCondition) -> BenefitCondition:
    session.add(condition)
    await session.commit()
    await session.refresh(condition)
    return condition

async def delete_condition(session: AsyncSession, condition: BenefitCondition) -> None:
    await session.delete(condition)
    await session.commit()
