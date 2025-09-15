from app.modules.benefits.models.benefit_calculation_rule_model import BenefitCalculationRule
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional


class BenefitCalculationRuleRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_all(self) -> List[BenefitCalculationRule]:
        return self.db.query(BenefitCalculationRule).all()


    def get_by_id(self, id: UUID) -> Optional[BenefitCalculationRule]:
        return self.db.query(BenefitCalculationRule).filter(BenefitCalculationRule.id == id).first()


    def create(self, obj_in: dict) -> BenefitCalculationRule:
        db_obj = BenefitCalculationRule(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def update(self, db_obj: BenefitCalculationRule, obj_in: dict) -> BenefitCalculationRule:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj


    def delete(self, id: UUID) -> None:
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()