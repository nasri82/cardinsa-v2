# app/modules/plans/models/plan_model.py

from sqlalchemy import Column, String, Date, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)

    plan_type_id = Column(UUID(as_uuid=True), ForeignKey("plan_types.id"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    version = Column(String, nullable=True)
    regulatory_approval_status = Column(String, nullable=True)
    policy_terms_url = Column(String, nullable=True)
    commission_structure = Column(String, nullable=True)
    target_market_segment = Column(String, nullable=True)
    distribution_channels = Column(String, nullable=True)
    underwriting_guidelines = Column(Text, nullable=True)

    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    coverages = relationship("PlanCoverageLink", back_populates="plan", cascade="all, delete-orphan")
    exclusions = relationship("PlanExclusionLink", back_populates="plan", cascade="all, delete-orphan")
    versions = relationship("PlanVersion", back_populates="plan", cascade="all, delete-orphan")
    territories = relationship("PlanTerritory", back_populates="plan", cascade="all, delete-orphan")
    eligibility_rules = relationship("PlanEligibilityRule", back_populates="plan", cascade="all, delete-orphan")
