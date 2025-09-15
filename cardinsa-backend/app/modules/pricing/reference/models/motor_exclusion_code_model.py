from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class MotorExclusionCode(Base):
    __tablename__ = "motor_exclusion_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    reason_en = Column(String(255), nullable=False)
    reason_ar = Column(String(255), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("motor_exclusion_categories.id"))

    category = relationship("MotorExclusionCategory", back_populates="exclusions")
