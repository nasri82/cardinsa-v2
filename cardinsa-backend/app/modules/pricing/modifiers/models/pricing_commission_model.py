from sqlalchemy import Column, String, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4

from app.core.database import Base

class PricingCommission(Base):
    __tablename__ = "pricing_commissions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    channel = Column(String, nullable=False)  # e.g., "broker", "agent"
    commission_type = Column(String, nullable=False)  # fixed, percentage
    value = Column(Numeric, nullable=False)
    currency = Column(String, default="USD")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
