# app/modules/benefits/models/benefit_translation_model.py

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class BenefitTranslation(Base):
    __tablename__ = "benefit_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("plan_benefit_schedules.id", ondelete="CASCADE"), nullable=False)

    language_code = Column(String, nullable=False)  # e.g. 'en', 'ar', 'fr'
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    schedule = relationship("PlanBenefitSchedule", back_populates="translations")
