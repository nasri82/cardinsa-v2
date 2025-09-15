from sqlalchemy.orm import Session
from uuid import UUID
from app.modules.pricing.product.models.product_feature_model import ProductFeature
from app.modules.pricing.product.schemas.product_feature_schema import ProductFeatureCreate, ProductFeatureUpdate


class ProductFeatureRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ProductFeatureCreate) -> ProductFeature:
        obj = ProductFeature(**data.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_by_product(self, product_id: UUID):
        return self.db.query(ProductFeature).filter(ProductFeature.product_id == product_id).all()

    def update(self, obj: ProductFeature, data: ProductFeatureUpdate) -> ProductFeature:
        for field, value in data.dict(exclude_unset=True).items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ProductFeature):
        self.db.delete(obj)
        self.db.commit()
