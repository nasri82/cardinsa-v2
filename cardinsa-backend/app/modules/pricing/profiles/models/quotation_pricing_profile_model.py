# app/modules/pricing/profiles/models/quotation_pricing_profile_model.py
from sqlalchemy import Column, String, Text, Boolean, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class QuotationPricingProfile(Base):
    """
    Pricing Profile model for managing insurance pricing configurations.
    """
    __tablename__ = "quotation_pricing_profiles"
    __table_args__ = {'extend_existing': True}  # Allow table redefinition

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Profile Identity
    name = Column(String(255), nullable=False)
    description = Column(Text)
    code = Column(String(50), unique=True)
    
    # Profile Configuration
    insurance_type = Column(String(50))  # Medical, Motor, Life, etc.
    currency = Column(String(3))  # 3-letter currency code
    
    # Premium Boundaries
    min_premium = Column(Numeric(15, 2))
    max_premium = Column(Numeric(15, 2))
    
    # Risk Formula
    risk_formula = Column(Text)
    
    # Benefit Exposure Settings
    enable_benefit_exposure = Column(Boolean, default=False)
    benefit_exposure_factor = Column(Numeric(10, 4))
    
    # Network Cost Settings
    enable_network_costs = Column(Boolean, default=False)
    network_cost_factor = Column(Numeric(10, 4))
    
    # Status and Configuration
    is_active = Column(Boolean, default=True)
    profile_metadata = Column(JSONB)  # Renamed from 'metadata' to avoid conflict
    
    # Audit Fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    archived_at = Column(DateTime)
    
    def __repr__(self):
        return f"<QuotationPricingProfile(id={self.id}, name={self.name}, insurance_type={self.insurance_type})>"