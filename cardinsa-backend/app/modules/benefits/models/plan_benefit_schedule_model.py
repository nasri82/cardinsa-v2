# app/modules/benefits/models/plan_benefit_schedule_model.py

from sqlalchemy import Column, String, Numeric, Integer, Boolean, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class PlanBenefitSchedule(Base):
    __tablename__ = "plan_benefit_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)

    benefit_type_id = Column(UUID(as_uuid=True), ForeignKey("benefit_types.id"), nullable=True)
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)

    limit = Column(Numeric(15, 2), nullable=True)
    deductible = Column(Numeric(15, 2), nullable=True)
    copay = Column(Numeric(5, 2), nullable=True)
    coinsurance = Column(Numeric(5, 2), nullable=True)
    frequency_limit = Column(Integer, nullable=True)
    waiting_period_days = Column(Integer, nullable=True)

    requires_preapproval = Column(Boolean, default=False)
    network_tier = Column(String, nullable=True)

    display_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    effective_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)

    extra_metadata = Column(JSONB, nullable=True)

    # Relationships
    conditions = relationship("BenefitCondition", back_populates="schedule", cascade="all, delete-orphan")
    translations = relationship("BenefitTranslation", back_populates="schedule", cascade="all, delete-orphan")
    preapproval_rules = relationship("BenefitPreapprovalRule", back_populates="schedule", cascade="all, delete-orphan")
