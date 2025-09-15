# app/modules/plans/routes/plan_eligibility_rule_route.py

from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.plans.schemas.plan_eligibility_rule_schema import PlanEligibilityRuleCreate, PlanEligibilityRuleOut
from app.modules.plans.services import plan_eligibility_rule_service

router = APIRouter(prefix="/plans/{plan_id}/eligibility", tags=["Plan Eligibility Rules"])

@router.get("/", response_model=list[PlanEligibilityRuleOut])
async def list_eligibility_rules(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    return await plan_eligibility_rule_service.list_eligibility_rules_by_plan(session, plan_id)

@router.post("/", response_model=PlanEligibilityRuleOut)
async def create_eligibility_rule(
    plan_id: UUID,
    payload: PlanEligibilityRuleCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    return await plan_eligibility_rule_service.create_eligibility_rule(session, payload, plan_id)
