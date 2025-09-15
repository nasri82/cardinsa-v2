from sqlalchemy.orm import Session
from app.modules.benefits.repositories.benefit_type_repository import BenefitTypeRepository
from app.modules.benefits.schemas.benefit_type_schema import BenefitTypeCreate, BenefitTypeUpdate


class BenefitTypeService:
    def __init__(self, db: Session):
        self.repo = BenefitTypeRepository(db)


    def get_all(self):
        return self.repo.get_all()


    def get_by_id(self, id):
        return self.repo.get_by_id(id)


    def create(self, data: BenefitTypeCreate):
        return self.repo.create(data.dict())


    def update(self, id, data: BenefitTypeUpdate):
        obj = self.repo.get_by_id(id)
        return self.repo.update(obj, data.dict())


    def delete(self, id):
        return self.repo.delete(id)