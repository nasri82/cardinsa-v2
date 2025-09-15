import uuid
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime


class ActuarialTable(Base):
    __tablename__ = "actuarial_tables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    gender = Column(String(10), nullable=False)  # male, female, other
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    risk_factor = Column(Float, nullable=False)  # e.g. 1.0 = neutral, >1 = riskier

    region = Column(String(100))  # Optional region-specific adjustment
    year = Column(Integer)        # Optional: to version actuarial data over time

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
