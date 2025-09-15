# app/modules/plans/models/plan_eligibility_rule_model.py

from sqlalchemy import Column, String, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class PlanEligibilityRule(Base):
    __tablename__ = "plan_eligibility_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)

    rule_name = Column(String, nullable=False)
    rule_category = Column(String, nullable=False)  # e.g. age, occupation, medical, financial
    eligibility_criteria = Column(JSONB, nullable=False)

    is_mandatory = Column(Boolean, default=True)
    effective_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(Date, nullable=True)

    # Relationships
    plan = relationship("Plan", back_populates="eligibility_rules")
