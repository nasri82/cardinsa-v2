from sqlalchemy.orm import Session
from app.modules.pricing.reference.repositories.medical_exclusion_code_repository import MedicalExclusionCodeRepository
from app.modules.pricing.reference.schemas.medical_exclusion_code_schema import MedicalExclusionCodeCreate, MedicalExclusionCodeUpdate


class MedicalExclusionCodeService:
    def __init__(self, db: Session):
        self.repo = MedicalExclusionCodeRepository(db)

    def list(self, skip=0, limit=100):
        return self.repo.get_all(skip, limit)

    def get(self, id):
        return self.repo.get_by_id(id)

    def create(self, obj_in: MedicalExclusionCodeCreate):
        return self.repo.create(obj_in)

    def update(self, id, obj_in: MedicalExclusionCodeUpdate):
        db_obj = self.repo.get_by_id(id)
        return self.repo.update(db_obj, obj_in)

    def delete(self, id):
        return self.repo.delete(id)
