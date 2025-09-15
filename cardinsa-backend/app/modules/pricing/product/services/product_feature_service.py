from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.modules.pricing.product.repositories.product_feature_repository import ProductFeatureRepository
from app.modules.pricing.product.schemas.product_feature_schema import ProductFeatureCreate, ProductFeatureUpdate


class ProductFeatureService:
    def __init__(self, db: Session):
        self.repo = ProductFeatureRepository(db)

    def create(self, data: ProductFeatureCreate):
        return self.repo.create(data)

    def list_by_product(self, product_id: UUID):
        return self.repo.list_by_product(product_id)

    def update(self, id: UUID, data: ProductFeatureUpdate):
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
