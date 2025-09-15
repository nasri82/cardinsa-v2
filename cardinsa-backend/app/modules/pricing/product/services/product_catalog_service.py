from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.product.repositories.product_catalog_repository import ProductCatalogRepository
from app.modules.pricing.product.schemas.product_catalog_schema import ProductCatalogCreate, ProductCatalogUpdate


class ProductCatalogService:
    def __init__(self, db: Session):
        self.repo = ProductCatalogRepository(db)

    def list(self, skip: int = 0, limit: int = 100):
        return self.repo.list(skip=skip, limit=limit)

    def get(self, id: UUID):
        return self.repo.get(id)

    def create(self, data: ProductCatalogCreate):
        return self.repo.create(data)

    def update(self, id: UUID, data: ProductCatalogUpdate):
        obj = self.repo.get(id)
        if not obj:
            return None
        return self.repo.update(obj, data)

    def delete(self, id: UUID):
        return self.repo.delete(id)
