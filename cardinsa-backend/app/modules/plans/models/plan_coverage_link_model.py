# app/modules/plans/models/plan_coverage_link_model.py

from sqlalchemy import Column, String, Numeric, Integer, Boolean, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class PlanCoverageLink(Base):
    __tablename__ = "plan_coverage_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    coverage_id = Column(UUID(as_uuid=True), ForeignKey("coverages.id", ondelete="CASCADE"), nullable=False)

    limit = Column(Numeric(15, 2), nullable=True)
    deductible = Column(Numeric(15, 2), nullable=True)
    copay = Column(Numeric(5, 2), nullable=True)
    coinsurance = Column(Numeric(5, 2), nullable=True)

    coverage_tier = Column(String, nullable=True)
    network_restrictions = Column(JSONB, nullable=True)
    prior_authorization_required = Column(Boolean, default=False)

    annual_maximum = Column(Numeric(15, 2), nullable=True)
    lifetime_maximum = Column(Numeric(15, 2), nullable=True)

    waiting_period_days = Column(Integer, nullable=True)
    effective_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    geographic_restrictions = Column(JSONB, nullable=True)

    is_mandatory = Column(Boolean, default=False)

    # Relationships
    plan = relationship("Plan", back_populates="coverages")
