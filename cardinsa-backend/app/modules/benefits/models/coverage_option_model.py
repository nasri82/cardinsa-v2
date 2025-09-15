from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class CoverageOption(Base):
    __tablename__ = "coverage_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    coverage_id = Column(UUID(as_uuid=True), ForeignKey("coverages.id"), nullable=False)
    name = Column(String, nullable=False)
    name_ar = Column(String)
    name_fr = Column(String)

    value = Column(String)  # e.g., "Private", "VIP", "Yes", "No"
    display_order = Column(Integer)
    is_default = Column(Boolean, default=False)
    is_mandatory = Column(Boolean, default=False)
    option_group_code = Column(String)

    # 🧠 Phase 2 Enhancements
    eligibility_criteria = Column(String)         # e.g., "age > 18"
    geographic_restrictions = Column(String)      # e.g., "LEBANON_ONLY"
    exclusion_tags = Column(String)               # comma-separated tags

    coverage = relationship("Coverage", back_populates="options")
