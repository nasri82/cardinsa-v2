from sqlalchemy.orm import Session
from app.modules.benefits.repositories.benefit_calculation_rule_repository import BenefitCalculationRuleRepository
from app.modules.benefits.schemas.benefit_calculation_rule_schema import (
BenefitCalculationRuleCreate, BenefitCalculationRuleUpdate
)


class BenefitCalculationRuleService:
    def __init__(self, db: Session):
        self.repo = BenefitCalculationRuleRepository(db)


    def get_all(self):
        return self.repo.get_all()


    def get_by_id(self, id):
        return self.repo.get_by_id(id)


    def create(self, data: BenefitCalculationRuleCreate):
        return self.repo.create(data.dict())


    def update(self, id, data: BenefitCalculationRuleUpdate):
        obj = self.repo.get_by_id(id)
        return self.repo.update(obj, data.dict())


    def delete(self, id):
        return self.repo.delete(id)