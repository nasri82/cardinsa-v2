

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.dependencies import get_db
from app.modules.benefits.schemas.benefit_calculation_rule_schema import (
BenefitCalculationRuleCreate, BenefitCalculationRuleUpdate, BenefitCalculationRuleOut
)
from app.modules.benefits.services.benefit_calculation_rule_service import BenefitCalculationRuleService


router = APIRouter(prefix="/benefit-rules", tags=["Benefit Rules"])


@router.get("/", response_model=list[BenefitCalculationRuleOut])
def list_benefit_rules(db: Session = Depends(get_db)):
    return BenefitCalculationRuleService(db).get_all()


@router.get("/{id}", response_model=BenefitCalculationRuleOut)
def get_benefit_rule(id: UUID, db: Session = Depends(get_db)):
    obj = BenefitCalculationRuleService(db).get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Benefit rule not found")
    return obj


@router.post("/", response_model=BenefitCalculationRuleOut)
def create_benefit_rule(data: BenefitCalculationRuleCreate, db: Session = Depends(get_db)):
    return BenefitCalculationRuleService(db).create(data)


@router.put("/{id}", response_model=BenefitCalculationRuleOut)
def update_benefit_rule(id: UUID, data: BenefitCalculationRuleUpdate, db: Session = Depends(get_db)):
    return BenefitCalculationRuleService(db).update(id, data)


@router.delete("/{id}")
def delete_benefit_rule(id: UUID, db: Session = Depends(get_db)):
    BenefitCalculationRuleService(db).delete(id)
    return {"message": "Deleted successfully"}