from sqlalchemy.orm import Session
from uuid import UUID

from app.modules.pricing.product.repositories.plan_type_repository import PlanTypeRepository
from app.modules.pricing.product.schemas.plan_type_schema import PlanTypeCreate, PlanTypeUpdate


class PlanTypeService:
    def __init__(self, db: Session):
        self.repo = PlanTypeRepository(db)

    def list(self):
        return self.repo.list()

    def create(self, data: PlanTypeCreate):
        return self.repo.create(data)

    def update(self, id: UUID, data: PlanTypeUpdate):
        obj = self.repo.db.query(self.repo.model).filter_by(id=id).first()
        if not obj:
            return None
        return self.repo.update(obj, data)

    def delete(self, id: UUID):
        obj = self.repo.db.query(self.repo.model).filter_by(id=id).first()
        if obj:
            self.repo.delete(obj)
            return True
        return False
