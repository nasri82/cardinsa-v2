# app/modules/plans/models/plan_territory_model.py

from sqlalchemy import Column, String, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class PlanTerritory(Base):
    __tablename__ = "plan_territories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)

    territory_type = Column(String, nullable=False)  # e.g. country, region, city
    territory_code = Column(String, nullable=True)
    territory_name = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    effective_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)

    rate_adjustments = Column(JSONB, nullable=True)
    regulatory_requirements = Column(JSONB, nullable=True)

    created_at = Column(Date, nullable=True)

    # Relationships
    plan = relationship("Plan", back_populates="territories")
