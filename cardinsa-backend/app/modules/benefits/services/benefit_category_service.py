

from sqlalchemy.orm import Session
from app.modules.benefits.repositories.benefit_category_repository import BenefitCategoryRepository
from app.modules.benefits.schemas.benefit_category_schema import (
BenefitCategoryCreate, BenefitCategoryUpdate
)


class BenefitCategoryService:
    def __init__(self, db: Session):
        self.repo = BenefitCategoryRepository(db)


def get_all(self):
    return self.repo.get_all()


def get_by_id(self, id):
    return self.repo.get_by_id(id)


def create(self, data: BenefitCategoryCreate):
    return self.repo.create(data.dict())


def update(self, id, data: BenefitCategoryUpdate):
    obj = self.repo.get_by_id(id)
    return self.repo.update(obj, data.dict())


def delete(self, id):
    return self.repo.delete(id)