from sqlalchemy.orm import Session
from app.modules.benefits.repositories.coverage_repository import CoverageRepository
from app.modules.benefits.schemas.coverage_schema import CoverageCreate, CoverageUpdate


class CoverageService:
    def __init__(self, db: Session):
        self.repo = CoverageRepository(db)


def get_all(self):
    return self.repo.get_all()


def get_by_id(self, id):
    return self.repo.get_by_id(id)


def create(self, data: CoverageCreate):
    return self.repo.create(data.dict())


def update(self, id, data: CoverageUpdate):
    obj = self.repo.get_by_id(id)
    return self.repo.update(obj, data.dict())


def delete(self, id):
    return self.repo.delete(id)