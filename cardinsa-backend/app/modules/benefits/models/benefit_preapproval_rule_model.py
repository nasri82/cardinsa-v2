# app/modules/benefits/models/benefit_preapproval_rule_model.py

from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class BenefitPreapprovalRule(Base):
    __tablename__ = "benefit_preapproval_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("plan_benefit_schedules.id", ondelete="CASCADE"), nullable=False)

    rule_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    criteria = Column(JSONB, nullable=True)   # flexible logic
    is_mandatory = Column(Boolean, default=True)

    # Relationships
    schedule = relationship("PlanBenefitSchedule", back_populates="preapproval_rules")
