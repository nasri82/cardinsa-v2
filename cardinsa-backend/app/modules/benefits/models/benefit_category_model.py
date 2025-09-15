from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class BenefitCategory(Base):
    __tablename__ = "benefit_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    name_ar = Column(String)
    name_fr = Column(String)
    category_code = Column(String, unique=True)

    parent_id = Column(UUID(as_uuid=True), ForeignKey("benefit_categories.id"), nullable=True)
    order_index = Column(String)
    is_active = Column(Boolean, default=True)

    # 🆕 Phase 2+3 enhancements
    calculation_basis = Column(String)  # e.g. "percentage", "fixed_amount", "per_unit"
    regulatory_tag = Column(String)     # optional: used for compliance filtering

    # Relationships
    parent = relationship("BenefitCategory", remote_side=[id], backref="subcategories")
    coverages = relationship("Coverage", back_populates="category")
    calculation_rules = relationship("BenefitCalculationRule", back_populates="category")
