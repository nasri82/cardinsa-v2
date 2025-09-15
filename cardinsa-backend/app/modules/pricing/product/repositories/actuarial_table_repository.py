from sqlalchemy.orm import Session
from uuid import UUID
from app.modules.pricing.product.models.actuarial_table_model import ActuarialTable
from app.modules.pricing.product.schemas.actuarial_table_schema import ActuarialTableCreate, ActuarialTableUpdate


class ActuarialTableRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ActuarialTableCreate) -> ActuarialTable:
        obj = ActuarialTable(**data.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list(self, region: str = None, year: int = None):
        query = self.db.query(ActuarialTable)
        if region:
            query = query.filter(ActuarialTable.region == region)
        if year:
            query = query.filter(ActuarialTable.year == year)
        return query.all()

    def update(self, obj: ActuarialTable, data: ActuarialTableUpdate) -> ActuarialTable:
        for field, value in data.dict(exclude_unset=True).items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ActuarialTable):
        self.db.delete(obj)
        self.db.commit()
