# app/modules/benefits/models/benefit_condition_model.py

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class BenefitCondition(Base):
    __tablename__ = "benefit_conditions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("plan_benefit_schedules.id", ondelete="CASCADE"), nullable=False)

    condition_type = Column(String, nullable=False)  # e.g. age, occupation, gender
    operator = Column(String, nullable=False)        # e.g. >, <, =, IN
    value = Column(JSONB, nullable=False)            # flexible JSON storage
    priority = Column(Integer, nullable=True)
    group_id = Column(UUID(as_uuid=True), nullable=True)  # for AND/OR grouping

    # Relationships
    schedule = relationship("PlanBenefitSchedule", back_populates="conditions")
