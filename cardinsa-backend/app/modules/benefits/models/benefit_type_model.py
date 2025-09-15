from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class BenefitType(Base):
    __tablename__ = "benefit_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    type_code = Column(String(50), unique=True, nullable=False)
    type_name = Column(String(200), nullable=False)
    type_name_ar = Column(String(200))
    type_name_fr = Column(String(200))

    calculation_method = Column(String(50))   # e.g., "percentage", "fixed_amount", "per_unit"
    unit_of_measure = Column(String(50))      # e.g., "per_year", "per_visit", "per_day"
    is_active = Column(Boolean, default=True)

    # 🔁 Relationship to coverages
    coverages = relationship("Coverage", back_populates="benefit_type")
