

from sqlalchemy.orm import Session
from app.modules.benefits.repositories.coverage_option_repository import CoverageOptionRepository
from app.modules.benefits.schemas.coverage_option_schema import CoverageOptionCreate, CoverageOptionUpdate


class CoverageOptionService:
    def __init__(self, db: Session):
        self.repo = CoverageOptionRepository(db)


    def get_all(self):
        return self.repo.get_all()


    def get_by_id(self, id):
        return self.repo.get_by_id(id)


    def create(self, data: CoverageOptionCreate):
        return self.repo.create(data.dict())


    def update(self, id, data: CoverageOptionUpdate):
        obj = self.repo.get_by_id(id)
        return self.repo.update(obj, data.dict())


    def delete(self, id):
        return self.repo.delete(id)