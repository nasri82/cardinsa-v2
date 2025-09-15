from sqlalchemy.orm import Session
from app.modules.pricing.reference.repositories.icd10_code_repository import ICD10CodeRepository
from app.modules.pricing.reference.schemas.icd10_code_schema import ICD10CodeCreate, ICD10CodeUpdate


class ICD10CodeService:
    def __init__(self, db: Session):
        self.repo = ICD10CodeRepository(db)

    def list(self, skip=0, limit=100):
        return self.repo.get_all(skip, limit)

    def get(self, id):
        return self.repo.get_by_id(id)

    def create(self, obj_in: ICD10CodeCreate):
        return self.repo.create(obj_in)

    def update(self, id, obj_in: ICD10CodeUpdate):
        db_obj = self.repo.get_by_id(id)
        return self.repo.update(db_obj, obj_in)

    def delete(self, id):
        return self.repo.delete(id)
