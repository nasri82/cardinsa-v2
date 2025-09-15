from sqlalchemy import Column, ForeignKey, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class PremiumOverrideLog(Base):
    __tablename__ = "premium_override_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id = Column(UUID(as_uuid=True), ForeignKey("premium_calculations.id"))
    original_value = Column(Numeric)
    overridden_value = Column(Numeric)
    reason = Column(String)
    overridden_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    overridden_at = Column(DateTime, default=datetime.utcnow)

    calculation = relationship("PremiumCalculation", back_populates="override_logs")
    overrider = relationship("User")
