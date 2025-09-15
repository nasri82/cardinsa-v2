from sqlalchemy.orm import Session
from uuid import UUID
from app.modules.pricing.product.models.product_catalog_model import ProductCatalog
from app.modules.pricing.product.schemas.product_catalog_schema import ProductCatalogCreate, ProductCatalogUpdate


class ProductCatalogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ProductCatalogCreate) -> ProductCatalog:
        obj = ProductCatalog(**data.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, id: UUID) -> ProductCatalog:
        return self.db.query(ProductCatalog).filter(ProductCatalog.id == id).first()

    def list(self, skip: int = 0, limit: int = 100):
        return self.db.query(ProductCatalog).offset(skip).limit(limit).all()

    def update(self, db_obj: ProductCatalog, data: ProductCatalogUpdate) -> ProductCatalog:
        for field, value in data.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: UUID):
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
