from sqlalchemy.orm import Session
from app.modules.pricing.reference.repositories.motor_exclusion_code_repository import MotorExclusionCodeRepository
from app.modules.pricing.reference.schemas.motor_exclusion_code_schema import MotorExclusionCodeCreate, MotorExclusionCodeUpdate


class MotorExclusionCodeService:
    def __init__(self, db: Session):
        self.repo = MotorExclusionCodeRepository(db)

    def list(self, skip=0, limit=100):
        return self.repo.get_all(skip, limit)

    def get(self, id):
        return self.repo.get_by_id(id)

    def create(self, obj_in: MotorExclusionCodeCreate):
        return self.repo.create(obj_in)

    def update(self, id, obj_in: MotorExclusionCodeUpdate):
        db_obj = self.repo.get_by_id(id)
        return self.repo.update(db_obj, obj_in)

    def delete(self, id):
        return self.repo.delete(id)
