# app/modules/benefits/routes/benefit_preapproval_rule_route.py

from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.benefits.schemas.benefit_preapproval_rule_schema import BenefitPreapprovalRuleCreate, BenefitPreapprovalRuleOut
from app.modules.benefits.services import benefit_preapproval_rule_service

router = APIRouter(prefix="/benefit-schedules/{schedule_id}/preapproval-rules", tags=["Benefit Preapproval Rules"])

@router.get("/", response_model=list[BenefitPreapprovalRuleOut])
async def list_preapproval_rules(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "view"))
):
    return await benefit_preapproval_rule_service.list_preapproval_rules_by_schedule(session, schedule_id)

@router.post("/", response_model=BenefitPreapprovalRuleOut)
async def create_preapproval_rule(
    schedule_id: UUID,
    payload: BenefitPreapprovalRuleCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "create"))
):
    return await benefit_preapproval_rule_service.create_preapproval_rule(session, payload, schedule_id)
