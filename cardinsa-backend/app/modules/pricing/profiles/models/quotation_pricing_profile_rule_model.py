# app/modules/pricing/profiles/models/quotation_pricing_profile_rule_model.py
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class QuotationPricingProfileRule(Base):
    """
    Association model for many-to-many relationship between pricing profiles and rules.
    """
    __tablename__ = "quotation_pricing_profile_rules"
    __table_args__ = {'extend_existing': True}  # Allow table redefinition

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    profile_id = Column(UUID(as_uuid=True), ForeignKey('quotation_pricing_profiles.id', ondelete='CASCADE'), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey('quotation_pricing_rules.id', ondelete='CASCADE'), nullable=False)
    
    # Relationship Configuration
    order_index = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    archived_at = Column(DateTime)
    
    def __repr__(self):
        return f"<QuotationPricingProfileRule(profile_id={self.profile_id}, rule_id={self.rule_id})>"