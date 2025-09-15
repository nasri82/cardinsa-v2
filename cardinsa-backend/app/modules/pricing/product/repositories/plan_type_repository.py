from sqlalchemy.orm import Session
from uuid import UUID
from app.modules.pricing.product.models.plan_type_model import PlanType
from app.modules.pricing.product.schemas.plan_type_schema import PlanTypeCreate, PlanTypeUpdate


class PlanTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: PlanTypeCreate) -> PlanType:
        obj = PlanType(**data.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list(self):
        return self.db.query(PlanType).filter(PlanType.is_active == True).all()

    def update(self, obj: PlanType, data: PlanTypeUpdate) -> PlanType:
        for field, value in data.dict(exclude_unset=True).items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: PlanType):
        self.db.delete(obj)
        self.db.commit()
