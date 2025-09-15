from sqlalchemy import Column, String, Numeric, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4

from app.core.database import Base

class PricingDeductible(Base):
    __tablename__ = "pricing_deductibles"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    code = Column(String, unique=True, nullable=False)
    label = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    currency = Column(String, default="USD")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
