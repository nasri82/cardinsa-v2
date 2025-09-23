# app/modules/pricing/modifiers/models/pricing_copayment_model.py

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
import enum

from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin

class CopaymentType(enum.Enum):
    """Copayment calculation types"""
    FIXED_AMOUNT = "fixed_amount"
    PERCENTAGE = "percentage"
    TIERED = "tiered"
    HYBRID = "hybrid"

class ServiceTier(enum.Enum):
    """Service tier levels for tiered copayments"""
    TIER_1 = "tier_1"  # Preferred/Generic
    TIER_2 = "tier_2"  # Non-preferred/Brand
    TIER_3 = "tier_3"  # Specialty
    TIER_4 = "tier_4"  # Premium

class PricingCopayment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Pricing Copayment Model for Step 5 - Advanced Pricing Components
    
    This model handles both fixed amount and percentage-based copayments
    with support for tiered structures and service-specific configurations.
    
    Key Features:
    - Fixed amount and percentage copayments
    - Tiered copayment structures
    - Service-specific configurations
    - Network tier integration
    - Currency support with validation
    - Integration with pricing profiles and deductibles
    - Audit trail and compliance features
    """
    __tablename__ = "premium_copayment"

    # =====================================================
    # CORE FIELDS
    # =====================================================
    
    code = Column(String(50), unique=True, nullable=False, index=True,
                 comment="Unique identifier code for the copayment (e.g., 'PCP_VISIT_20')")
    
    label = Column(String(200), nullable=False,
                  comment="Human-readable label (e.g., 'Primary Care Visit Copay')")
    
    description = Column(Text,
                        comment="Detailed description of copayment terms and conditions")

    # =====================================================
    # COPAYMENT CONFIGURATION
    # =====================================================
    
    copayment_type = Column(Enum(CopaymentType), nullable=False, default=CopaymentType.FIXED_AMOUNT,
                           comment="Type of copayment calculation")
    
    # For fixed amount copayments
    fixed_amount = Column(Numeric(10, 2),
                         comment="Fixed copayment amount (when type is fixed_amount)")
    
    # For percentage copayments
    percentage = Column(Numeric(5, 2),
                       comment="Copayment percentage (when type is percentage)")
    
    # For percentage copayments - what to calculate percentage of
    percentage_of = Column(String(50), default="service_cost",
                          comment="What to calculate percentage of: service_cost, allowed_amount, billed_amount")
    
    currency = Column(String(3), default="USD", nullable=False,
                     comment="ISO 3-letter currency code")

    # =====================================================
    # SERVICE AND NETWORK CONFIGURATION
    # =====================================================
    
    service_category = Column(String(100), nullable=False,
                             comment="Service category: primary_care, specialist, emergency, pharmacy, etc.")
    
    service_subcategory = Column(String(100),
                                comment="Service subcategory for more granular control")
    
    network_tier = Column(String(50), default="in_network",
                         comment="Network tier: in_network, out_of_network, preferred, non_preferred")
    
    service_tier = Column(Enum(ServiceTier),
                         comment="Service tier for tiered copayment structures")

    # =====================================================
    # BUSINESS RULES
    # =====================================================
    
    min_copay = Column(Numeric(10, 2),
                      comment="Minimum copayment amount (for percentage-based copays)")
    
    max_copay = Column(Numeric(10, 2),
                      comment="Maximum copayment amount (for percentage-based copays)")
    
    applies_to_deductible = Column(Boolean, default=True,
                                  comment="Whether copayment counts toward deductible")
    
    applies_after_deductible = Column(Boolean, default=False,
                                     comment="Whether copayment only applies after deductible is met")
    
    waived_if_admitted = Column(Boolean, default=False,
                               comment="Whether copay is waived if patient is admitted")
    
    visit_limit = Column(String(50),
                        comment="Visit limits: per_day, per_episode, unlimited")
    
    max_visits_per_period = Column(String(10),
                                  comment="Maximum visits per period (if applicable)")

    # =====================================================
    # TIERED COPAYMENT CONFIGURATION
    # =====================================================
    
    tier_1_amount = Column(Numeric(10, 2),
                          comment="Tier 1 copayment amount")
    
    tier_2_amount = Column(Numeric(10, 2),
                          comment="Tier 2 copayment amount")
    
    tier_3_amount = Column(Numeric(10, 2),
                          comment="Tier 3 copayment amount")
    
    tier_4_amount = Column(Numeric(10, 2),
                          comment="Tier 4 copayment amount")

    # =====================================================
    # INTEGRATION WITH OTHER COMPONENTS
    # =====================================================
    
    profile_id = Column(UUID(as_uuid=True), ForeignKey('quotation_pricing_profiles.id'),
                       comment="Link to pricing profile from Step 4")
    
    deductible_id = Column(UUID(as_uuid=True), ForeignKey('premium_deductible.id'),
                          comment="Associated deductible (if applicable)")
    
    priority = Column(String(20), default="medium",
                     comment="Processing priority: low, medium, high, critical")
    
    calculation_order = Column(String(20), default="after_deductible",
                              comment="When to apply: before_deductible, after_deductible, with_coinsurance")

    # =====================================================
    # VALIDITY AND STATUS
    # =====================================================
    
    effective_date = Column(DateTime, default=datetime.utcnow,
                           comment="Date when this copayment becomes effective")
    
    expiration_date = Column(DateTime,
                            comment="Date when this copayment expires")
    
    is_active = Column(Boolean, default=True, nullable=False, index=True,
                      comment="Whether this copayment is currently active")
    
    is_default = Column(Boolean, default=False,
                       comment="Whether this is the default copayment for its category")

    # =====================================================
    # AUDIT AND COMPLIANCE
    # =====================================================
    
    created_by = Column(UUID(as_uuid=True),
                       comment="User ID who created this copayment")
    
    updated_by = Column(UUID(as_uuid=True),
                       comment="User ID who last updated this copayment")
    
    version = Column(String(20), default="1.0",
                    comment="Version number for change tracking")
    
    approval_status = Column(String(50), default="draft",
                            comment="Approval status: draft, pending, approved, rejected")
    
    approved_by = Column(UUID(as_uuid=True),
                        comment="User ID who approved this copayment")
    
    approved_at = Column(DateTime,
                        comment="Timestamp of approval")

    # =====================================================
    # RELATIONSHIPS
    # =====================================================
    
    # Relationship to pricing profile (Step 4 integration)
    profile = relationship("QuotationPricingProfile", back_populates="copayments")
    
    # Relationship to associated deductible
    deductible = relationship("PricingDeductible", back_populates="copayments")

    # =====================================================
    # TABLE CONFIGURATION
    # =====================================================
    
    __table_args__ = (
        # Indexes for performance
        {"comment": "Pricing copayments for Step 5 advanced pricing components"}
    )

    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def calculate_copayment(self, service_cost: Decimal, service_tier: str = None, 
                           deductible_satisfied: bool = True) -> Decimal:
        """
        Calculate the copayment amount based on service cost and configuration.
        
        Args:
            service_cost: The cost of the service
            service_tier: Service tier for tiered copayments
            deductible_satisfied: Whether the deductible has been satisfied
            
        Returns:
            Calculated copayment amount
        """
        # Check if copay applies after deductible
        if self.applies_after_deductible and not deductible_satisfied:
            return Decimal('0.00')
        
        # Handle tiered copayments
        if self.copayment_type == CopaymentType.TIERED and service_tier:
            return self._calculate_tiered_copayment(service_tier)
        
        # Handle fixed amount copayments
        if self.copayment_type == CopaymentType.FIXED_AMOUNT:
            return self.fixed_amount or Decimal('0.00')
        
        # Handle percentage copayments
        if self.copayment_type == CopaymentType.PERCENTAGE:
            percentage_amount = (service_cost * self.percentage) / 100
            
            # Apply min/max limits
            if self.min_copay:
                percentage_amount = max(percentage_amount, self.min_copay)
            if self.max_copay:
                percentage_amount = min(percentage_amount, self.max_copay)
                
            return percentage_amount
        
        return Decimal('0.00')
    
    def _calculate_tiered_copayment(self, service_tier: str) -> Decimal:
        """
        Calculate copayment for tiered structures.
        
        Args:
            service_tier: The service tier
            
        Returns:
            Tiered copayment amount
        """
        tier_mapping = {
            'tier_1': self.tier_1_amount,
            'tier_2': self.tier_2_amount,
            'tier_3': self.tier_3_amount,
            'tier_4': self.tier_4_amount
        }
        
        return tier_mapping.get(service_tier.lower(), Decimal('0.00')) or Decimal('0.00')
    
    def is_applicable_to_service(self, service_type: str, network_tier: str = None) -> bool:
        """
        Check if this copayment applies to a specific service and network tier.
        
        Args:
            service_type: The type of service
            network_tier: The network tier
            
        Returns:
            True if copayment applies
        """
        # Check service category match
        if not self.service_category or self.service_category.lower() != service_type.lower():
            return False
        
        # Check network tier match (if specified)
        if network_tier and self.network_tier:
            if self.network_tier.lower() != network_tier.lower():
                return False
        
        return True
    
    def validate_configuration(self) -> tuple[bool, str]:
        """
        Validate the copayment configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.copayment_type == CopaymentType.FIXED_AMOUNT:
            if not self.fixed_amount or self.fixed_amount <= 0:
                return False, "Fixed amount must be greater than 0"
        
        elif self.copayment_type == CopaymentType.PERCENTAGE:
            if not self.percentage or self.percentage <= 0 or self.percentage > 100:
                return False, "Percentage must be between 0 and 100"
        
        elif self.copayment_type == CopaymentType.TIERED:
            if not any([self.tier_1_amount, self.tier_2_amount, 
                       self.tier_3_amount, self.tier_4_amount]):
                return False, "At least one tier amount must be specified"
        
        return True, ""
    
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
            'copayment_type': self.copayment_type.value if self.copayment_type else None,
            'fixed_amount': float(self.fixed_amount) if self.fixed_amount else None,
            'percentage': float(self.percentage) if self.percentage else None,
            'currency': self.currency,
            'service_category': self.service_category,
            'network_tier': self.network_tier,
            'min_copay': float(self.min_copay) if self.min_copay else None,
            'max_copay': float(self.max_copay) if self.max_copay else None,
            'is_active': self.is_active,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        if self.copayment_type == CopaymentType.FIXED_AMOUNT:
            return f"<PricingCopayment(code='{self.code}', amount={self.fixed_amount} {self.currency})>"
        elif self.copayment_type == CopaymentType.PERCENTAGE:
            return f"<PricingCopayment(code='{self.code}', percentage={self.percentage}%)>"
        else:
            return f"<PricingCopayment(code='{self.code}', type='{self.copayment_type.value}')>"

    def __str__(self) -> str:
        return f"{self.label}: {self.copayment_type.value}"