from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class MotorExclusionCategory(Base):
    __tablename__ = "motor_exclusion_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    exclusions = relationship("MotorExclusionCode", back_populates="category", cascade="all, delete")
