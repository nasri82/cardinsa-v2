from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.core.database import Base
import uuid

class BenefitCalculationRule(Base):
    __tablename__ = "benefit_calculation_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    benefit_category_id = Column(UUID(as_uuid=True), ForeignKey("benefit_categories.id"))
    rule_name = Column(String(200), nullable=False)
    rule_description = Column(String)

    calculation_formula = Column(String)  # e.g., "amount = invoice * 0.1 + deductible"
    parameters = Column(JSON)             # JSONB object to store dynamic values
    effective_date = Column(Date)
    expiry_date = Column(Date)

    # 🔁 Relationship
    category = relationship("BenefitCategory", back_populates="calculation_rules")
