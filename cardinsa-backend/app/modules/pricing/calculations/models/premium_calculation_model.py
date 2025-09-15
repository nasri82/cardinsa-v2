from sqlalchemy import Column, ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import enum
from datetime import datetime

class ApprovalStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class PremiumCalculation(Base):
    __tablename__ = "premium_calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quotation_id = Column(UUID(as_uuid=True), ForeignKey("quotations.id"))
    profile_id = Column(UUID(as_uuid=True), ForeignKey("quotation_pricing_profiles.id"))

    base_premium = Column(Numeric)
    age_loading = Column(Numeric)
    region_loading = Column(Numeric)
    deductible_amount = Column(Numeric)
    discount_amount = Column(Numeric)
    surcharge_amount = Column(Numeric)
    tax_amount = Column(Numeric)
    final_premium = Column(Numeric)

    approval_status = Column(Enum(ApprovalStatusEnum), default=ApprovalStatusEnum.pending)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    quotation = relationship("Quotation", back_populates="calculations")
    profile = relationship("QuotationPricingProfile")
    approver = relationship("User")
