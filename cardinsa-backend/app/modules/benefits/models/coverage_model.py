from sqlalchemy import Column, String, Boolean, Integer, Float, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class Coverage(Base):
    __tablename__ = "coverages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    name_ar = Column(String)
    name_fr = Column(String)
    description = Column(String)
    coverage_code = Column(String, unique=True)

    # 🔗 Relationships
    category_id = Column(UUID(as_uuid=True), ForeignKey("benefit_categories.id"))
    parent_coverage_id = Column(UUID(as_uuid=True), ForeignKey("coverages.id"), nullable=True)
    benefit_type_id = Column(UUID(as_uuid=True), ForeignKey("benefit_types.id"), nullable=True)

    # 💰 Benefit Logic Fields
    limit_amount = Column(Float)
    co_payment = Column(Float)
    deductible = Column(Float)
    frequency_limit = Column(Integer)
    max_visits = Column(Integer)
    unit_type = Column(String)  # e.g. "per_visit", "per_day"
    waiting_period_days = Column(Integer)

    # 📅 Lifecycle
    effective_date = Column(Date)
    expiry_date = Column(Date)
    authorization_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # 🧾 Compliance
    regulatory_code = Column(String)

    # 🔗 Relationships
    parent_coverage = relationship("Coverage", remote_side=[id], backref="sub_coverages")
    category = relationship("BenefitCategory", back_populates="coverages")
    benefit_type = relationship("BenefitType", back_populates="coverages")
    options = relationship("CoverageOption", back_populates="coverage", cascade="all, delete")
