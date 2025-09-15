# app/modules/plans/repositories/plan_version_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.plans.models.plan_version_model import PlanVersion
from uuid import UUID

async def get_versions_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanVersion]:
    result = await session.execute(select(PlanVersion).where(PlanVersion.plan_id == plan_id))
    return result.scalars().all()

async def create_version(session: AsyncSession, version: PlanVersion) -> PlanVersion:
    session.add(version)
    await session.commit()
    await session.refresh(version)
    return version

async def set_current_version(session: AsyncSession, plan_id: UUID, version_id: UUID) -> None:
    await session.execute(
        f"UPDATE plan_versions SET is_current_version = false WHERE plan_id = :pid", {"pid": str(plan_id)}
    )
    await session.execute(
        f"UPDATE plan_versions SET is_current_version = true WHERE id = :vid", {"vid": str(version_id)}
    )
    await session.commit()
