from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.modules.pricing.product.repositories.actuarial_table_repository import ActuarialTableRepository
from app.modules.pricing.product.schemas.actuarial_table_schema import ActuarialTableCreate, ActuarialTableUpdate


class ActuarialTableService:
    def __init__(self, db: Session):
        self.repo = ActuarialTableRepository(db)

    def list(self, region: Optional[str] = None, year: Optional[int] = None):
        return self.repo.list(region=region, year=year)

    def create(self, data: ActuarialTableCreate):
        return self.repo.create(data)

    def update(self, id: UUID, data: ActuarialTableUpdate):
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
