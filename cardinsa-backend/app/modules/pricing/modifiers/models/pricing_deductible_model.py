# app/modules/pricing/modifiers/models/pricing_deductible_model.py

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin

class PricingDeductible(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Pricing Deductible Model for Step 5 - Advanced Pricing Components
    
    This model handles both service-specific and global deductible configurations
    that integrate with pricing profiles from Step 4.
    
    Key Features:
    - Service-specific deductibles (medical, dental, vision, etc.)
    - Global deductible pools (family vs individual)
    - Currency support with validation
    - Integration with pricing profiles
    - Audit trail and version control
    - Active/inactive status management
    """
    __tablename__ = "premium_deductible"

    # =====================================================
    # CORE FIELDS
    # =====================================================
    
    code = Column(String(50), unique=True, nullable=False, index=True,
                 comment="Unique identifier code for the deductible (e.g., 'MED_IND_1000')")
    
    label = Column(String(200), nullable=False,
                  comment="Human-readable label (e.g., 'Medical Individual Deductible')")
    
    description = Column(Text,
                        comment="Detailed description of the deductible terms and conditions")

    # =====================================================
    # DEDUCTIBLE CONFIGURATION
    # =====================================================
    
    amount = Column(Numeric(15, 2), nullable=False,
                   comment="Deductible amount in the specified currency")
    
    currency = Column(String(3), default="USD", nullable=False,
                     comment="ISO 3-letter currency code (USD, EUR, etc.)")
    
    deductible_type = Column(String(50), nullable=False, default="individual",
                            comment="Type: individual, family, service_specific, global")
    
    service_category = Column(String(100),
                             comment="Service category: medical, dental, vision, pharmacy, etc.")
    
    frequency = Column(String(50), default="annual",
                      comment="Reset frequency: annual, lifetime, per_incident")
    
    # =====================================================
    # BUSINESS RULES
    # =====================================================
    
    min_amount = Column(Numeric(15, 2),
                       comment="Minimum deductible amount allowed")
    
    max_amount = Column(Numeric(15, 2), 
                       comment="Maximum deductible amount allowed")
    
    applies_to_coinsurance = Column(Boolean, default=True,
                                   comment="Whether deductible applies before coinsurance kicks in")
    
    applies_to_copay = Column(Boolean, default=False,
                             comment="Whether copays count toward deductible")
    
    carryover_allowed = Column(Boolean, default=False,
                              comment="Whether unused deductible carries over to next period")
    
    # =====================================================
    # INTEGRATION WITH STEP 4 (PRICING PROFILES)
    # =====================================================
    
    profile_id = Column(UUID(as_uuid=True), ForeignKey('quotation_pricing_profiles.id'),
                       comment="Link to pricing profile from Step 4")
    
    priority = Column(String(20), default="medium",
                     comment="Processing priority: low, medium, high, critical")
    
    calculation_order = Column(String(20), default="before_copay",
                              comment="When to apply: before_copay, after_copay, before_coinsurance")
    
    # =====================================================
    # VALIDITY AND STATUS
    # =====================================================
    
    effective_date = Column(DateTime, default=datetime.utcnow,
                           comment="Date when this deductible becomes effective")
    
    expiration_date = Column(DateTime,
                            comment="Date when this deductible expires")
    
    is_active = Column(Boolean, default=True, nullable=False, index=True,
                      comment="Whether this deductible is currently active")
    
    is_default = Column(Boolean, default=False,
                       comment="Whether this is the default deductible for its category")
    
    # =====================================================
    # AUDIT AND COMPLIANCE
    # =====================================================
    
    created_by = Column(UUID(as_uuid=True),
                       comment="User ID who created this deductible")
    
    updated_by = Column(UUID(as_uuid=True),
                       comment="User ID who last updated this deductible")
    
    version = Column(String(20), default="1.0",
                    comment="Version number for change tracking")
    
    approval_status = Column(String(50), default="draft",
                            comment="Approval status: draft, pending, approved, rejected")
    
    approved_by = Column(UUID(as_uuid=True),
                        comment="User ID who approved this deductible")
    
    approved_at = Column(DateTime,
                        comment="Timestamp of approval")

    # =====================================================
    # RELATIONSHIPS
    # =====================================================
    
    # Relationship to pricing profile (Step 4 integration)
    profile = relationship("QuotationPricingProfile", back_populates="deductibles")
    
    # Self-referential relationship for deductible hierarchies
    parent_id = Column(UUID(as_uuid=True), ForeignKey('premium_deductible.id'),
                      comment="Parent deductible for hierarchical structures")
    
    children = relationship("PricingDeductible", 
                           backref="parent",
                           remote_side="PricingDeductible.id")

    # =====================================================
    # TABLE CONFIGURATION
    # =====================================================
    
    __table_args__ = (
        # Indexes for performance
        {"comment": "Pricing deductibles for Step 5 advanced pricing components"}
    )

    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def is_applicable_to_service(self, service_type: str) -> bool:
        """
        Check if this deductible applies to a specific service type.
        
        Args:
            service_type: The type of service to check
            
        Returns:
            True if deductible applies to the service
        """
        if self.service_category is None:
            return True  # Global deductible applies to all services
        return self.service_category.lower() == service_type.lower()
    
    def calculate_remaining_deductible(self, amount_used: float) -> float:
        """
        Calculate the remaining deductible amount.
        
        Args:
            amount_used: Amount already applied toward deductible
            
        Returns:
            Remaining deductible amount
        """
        remaining = float(self.amount) - amount_used
        return max(0, remaining)
    
    def is_satisfied(self, amount_used: float) -> bool:
        """
        Check if the deductible has been fully satisfied.
        
        Args:
            amount_used: Amount already applied toward deductible
            
        Returns:
            True if deductible is fully satisfied
        """
        return amount_used >= float(self.amount)
    
    def validate_amount(self) -> bool:
        """
        Validate that the deductible amount is within acceptable bounds.
        
        Returns:
            True if amount is valid
        """
        amount = float(self.amount)
        
        if self.min_amount and amount < float(self.min_amount):
            return False
            
        if self.max_amount and amount > float(self.max_amount):
            return False
            
        return amount > 0
    
    def to_dict(self) -> dict:
        """
        Convert model to dictionary for API responses.
        
        Returns:
            Dictionary representation of the model
        """
        return {
            'id': str(self.id),
            'code': self.code,
            'label': self.label,
            'description': self.description,
            'amount': float(self.amount),
            'currency': self.currency,
            'deductible_type': self.deductible_type,
            'service_category': self.service_category,
            'frequency': self.frequency,
            'is_active': self.is_active,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return f"<PricingDeductible(code='{self.code}', amount={self.amount} {self.currency}, type='{self.deductible_type}')>"

    def __str__(self) -> str:
        return f"{self.label}: {self.amount} {self.currency}"