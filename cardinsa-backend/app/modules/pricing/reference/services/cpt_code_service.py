from sqlalchemy.orm import Session
from app.modules.pricing.reference.repositories.cpt_code_repository import CPTCodeRepository
from app.modules.pricing.reference.schemas.cpt_code_schema import CPTCodeCreate, CPTCodeUpdate


class CPTCodeService:
    def __init__(self, db: Session):
        self.repo = CPTCodeRepository(db)

    def list(self, skip=0, limit=100):
        return self.repo.get_all(skip, limit)

    def get(self, id):
        return self.repo.get_by_id(id)

    def create(self, obj_in: CPTCodeCreate):
        return self.repo.create(obj_in)

    def update(self, id, obj_in: CPTCodeUpdate):
        db_obj = self.repo.get_by_id(id)
        return self.repo.update(db_obj, obj_in)

    def delete(self, id):
        return self.repo.delete(id)
