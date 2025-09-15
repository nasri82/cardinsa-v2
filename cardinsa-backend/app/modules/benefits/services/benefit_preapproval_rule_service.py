# app/modules/benefits/services/benefit_preapproval_rule_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.benefits.models.benefit_preapproval_rule_model import BenefitPreapprovalRule
from app.modules.benefits.schemas.benefit_preapproval_rule_schema import BenefitPreapprovalRuleCreate
from app.modules.benefits.repositories import benefit_preapproval_rule_repository

async def list_preapproval_rules_by_schedule(session: AsyncSession, schedule_id: UUID) -> list[BenefitPreapprovalRule]:
    return await benefit_preapproval_rule_repository.get_preapproval_rules_by_schedule(session, schedule_id)

async def create_preapproval_rule(session: AsyncSession, payload: BenefitPreapprovalRuleCreate, schedule_id: UUID) -> BenefitPreapprovalRule:
    rule = BenefitPreapprovalRule(**payload.dict(), schedule_id=schedule_id)
    return await benefit_preapproval_rule_repository.create_preapproval_rule(session, rule)

async def delete_preapproval_rule(session: AsyncSession, rule: BenefitPreapprovalRule) -> None:
    return await benefit_preapproval_rule_repository.delete_preapproval_rule(session, rule)
