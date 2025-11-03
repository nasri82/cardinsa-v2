# app/modules/pricing/modifiers/models/pricing_discount_model.py

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from uuid import uuid4
import enum
from typing import Dict, Any, List, Optional

from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin

class DiscountType(enum.Enum):
    """Discount calculation types"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED = "tiered"
    VOLUME = "volume"
    LOYALTY = "loyalty"
    PROMOTIONAL = "promotional"

class DiscountScope(enum.Enum):
    """Discount application scope"""
    PREMIUM = "premium"
    SERVICE = "service"
    CATEGORY = "category"
    GLOBAL = "global"

class EligibilityType(enum.Enum):
    """Eligibility criteria types"""
    AGE_BASED = "age_based"
    VOLUME_BASED = "volume_based"
    LOYALTY_BASED = "loyalty_based"
    MEMBERSHIP_BASED = "membership_based"
    TIME_BASED = "time_based"
    COMBINATION = "combination"

class PricingDiscount(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Pricing Discount Model for Step 5 - Advanced Pricing Components
    
    This model handles complex discount and promotion structures including:
    - Percentage and fixed amount discounts
    - Volume-based discounts
    - Loyalty program discounts
    - Time-sensitive promotional discounts
    - Eligibility criteria and validation
    - Stackable and exclusive discount rules
    
    Key Features:
    - Multiple discount calculation methods
    - Complex eligibility criteria with JSON storage
    - Volume thresholds and loyalty tiers
    - Promotional campaigns with date ranges
    - Stackable vs exclusive discount management
    - Usage tracking and limits
    - Integration with pricing profiles
    - Comprehensive audit trail
    """
    __tablename__ = "premium_discounts_promotions"

    # =====================================================
    # CORE FIELDS
    # =====================================================
    
    code = Column(String(50), unique=True, nullable=False, index=True,
                 comment="Unique identifier code for the discount (e.g., 'LOYALTY_10', 'VOLUME_TIER_2')")
    
    name = Column(String(200), nullable=False,
                 comment="Discount name for display purposes")
    
    description = Column(Text,
                        comment="Detailed description of discount terms and conditions")
    
    internal_notes = Column(Text,
                           comment="Internal notes for administrators")

    # =====================================================
    # DISCOUNT CONFIGURATION
    # =====================================================
    
    discount_type = Column(Enum(DiscountType), nullable=False,
                          comment="Type of discount calculation")
    
    discount_scope = Column(Enum(DiscountScope), nullable=False, default=DiscountScope.PREMIUM,
                           comment="Scope of discount application")
    
    # Basic discount values
    percentage_value = Column(Numeric(5, 2),
                             comment="Percentage discount value (0-100)")
    
    fixed_amount = Column(Numeric(15, 2),
                         comment="Fixed discount amount")
    
    currency = Column(String(3), default="USD", nullable=False,
                     comment="ISO 3-letter currency code")
    
    # Maximum discount limits
    max_discount_amount = Column(Numeric(15, 2),
                                comment="Maximum discount amount (caps percentage discounts)")
    
    min_discount_amount = Column(Numeric(15, 2),
                                comment="Minimum discount amount")

    # =====================================================
    # TIERED DISCOUNT CONFIGURATION
    # =====================================================
    
    # JSON structure for tiered discounts
    tier_structure = Column(JSONB,
                           comment="JSON structure defining discount tiers and thresholds")
    
    # Example tier_structure:
    # {
    #   "tiers": [
    #     {"threshold": 1000, "discount_percentage": 5, "discount_amount": null},
    #     {"threshold": 5000, "discount_percentage": 10, "discount_amount": null},
    #     {"threshold": 10000, "discount_percentage": 15, "discount_amount": 500}
    #   ],
    #   "threshold_type": "premium_amount" // or "policy_count", "years_with_company"
    # }

    # =====================================================
    # ELIGIBILITY CRITERIA
    # =====================================================
    
    eligibility_type = Column(Enum(EligibilityType), nullable=False, default=EligibilityType.TIME_BASED,
                             comment="Primary eligibility criteria type")
    
    # JSON structure for complex eligibility rules
    eligibility_criteria = Column(JSONB,
                                 comment="JSON structure defining eligibility requirements")
    
    # Example eligibility_criteria:
    # {
    #   "age_range": {"min": 25, "max": 65},
    #   "policy_types": ["medical", "dental"],
    #   "minimum_premium": 1000,
    #   "customer_segments": ["individual", "family"],
    #   "geographic_restrictions": ["US", "CA"],
    #   "membership_required": true,
    #   "loyalty_years_min": 2
    # }
    
    # Age-based eligibility
    min_age = Column(Integer,
                    comment="Minimum age for eligibility")
    
    max_age = Column(Integer,
                    comment="Maximum age for eligibility")
    
    # Volume-based eligibility
    min_premium_amount = Column(Numeric(15, 2),
                               comment="Minimum premium amount for eligibility")
    
    min_policy_count = Column(Integer,
                             comment="Minimum number of policies for eligibility")
    
    # Loyalty-based eligibility
    min_loyalty_years = Column(Integer,
                              comment="Minimum years as customer for eligibility")

    # =====================================================
    # PROMOTIONAL CAMPAIGN SETTINGS
    # =====================================================
    
    is_promotional = Column(Boolean, default=False,
                           comment="Whether this is a promotional discount")
    
    campaign_name = Column(String(200),
                          comment="Promotional campaign name")
    
    campaign_code = Column(String(50),
                          comment="Promotional campaign code for tracking")
    
    # Date ranges for promotions
    promotion_start_date = Column(DateTime,
                                 comment="Start date for promotional discount")
    
    promotion_end_date = Column(DateTime,
                               comment="End date for promotional discount")
    
    # Usage limits for promotions
    max_uses_total = Column(Integer,
                           comment="Maximum total uses of this discount")
    
    max_uses_per_customer = Column(Integer, default=1,
                                  comment="Maximum uses per customer")
    
    current_use_count = Column(Integer, default=0,
                              comment="Current number of times discount has been used")

    # =====================================================
    # DISCOUNT RULES AND BEHAVIOR
    # =====================================================
    
    is_stackable = Column(Boolean, default=False,
                         comment="Whether this discount can be combined with others")
    
    stack_priority = Column(Integer, default=100,
                           comment="Priority when stacking discounts (lower = higher priority)")
    
    exclusive_with = Column(JSONB,
                           comment="JSON array of discount codes that this discount is exclusive with")
    
    # Calculation behavior
    apply_before_tax = Column(Boolean, default=True,
                             comment="Whether to apply discount before tax calculation")
    
    apply_to_base_premium = Column(Boolean, default=True,
                                  comment="Whether discount applies to base premium")
    
    apply_to_fees = Column(Boolean, default=False,
                          comment="Whether discount applies to fees")
    
    compound_with_other_discounts = Column(Boolean, default=False,
                                          comment="Whether to compound with other discounts")

    # =====================================================
    # INTEGRATION WITH OTHER COMPONENTS
    # =====================================================
    
    profile_id = Column(UUID(as_uuid=True), ForeignKey('quotation_pricing_profiles.id'),
                       comment="Link to pricing profile from Step 4")
    
    applicable_service_categories = Column(JSONB,
                                          comment="JSON array of applicable service categories")
    
    priority = Column(Integer, default=100,
                     comment="Processing priority (lower = higher priority)")

    # =====================================================
    # VALIDITY AND STATUS
    # =====================================================
    
    effective_date = Column(DateTime, default=datetime.utcnow,
                           comment="Date when this discount becomes effective")
    
    expiration_date = Column(DateTime,
                            comment="Date when this discount expires")
    
    is_active = Column(Boolean, default=True, nullable=False, index=True,
                      comment="Whether this discount is currently active")
    
    is_auto_apply = Column(Boolean, default=False,
                          comment="Whether this discount is automatically applied when eligible")
    
    requires_approval = Column(Boolean, default=False,
                              comment="Whether discount usage requires manual approval")

    # =====================================================
    # AUDIT AND COMPLIANCE
    # =====================================================
    
    created_by = Column(UUID(as_uuid=True),
                       comment="User ID who created this discount")
    
    updated_by = Column(UUID(as_uuid=True),
                       comment="User ID who last updated this discount")
    
    version = Column(String(20), default="1.0",
                    comment="Version number for change tracking")
    
    approval_status = Column(String(50), default="draft",
                            comment="Approval status: draft, pending, approved, rejected")
    
    approved_by = Column(UUID(as_uuid=True),
                        comment="User ID who approved this discount")
    
    approved_at = Column(DateTime,
                        comment="Timestamp of approval")

    # =====================================================
    # RELATIONSHIPS
    # =====================================================
    
    # Relationship to pricing profile (Step 4 integration)
    profile = relationship("QuotationPricingProfile", back_populates="discounts")

    # =====================================================
    # TABLE CONFIGURATION
    # =====================================================
    
    __table_args__ = (
        # Indexes for performance
        {"comment": "Pricing discounts and promotions for Step 5 advanced pricing components"}
    )

    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def calculate_discount(self, base_amount: Decimal, customer_data: Dict[str, Any] = None) -> Decimal:
        """
        Calculate the discount amount based on configuration and customer data.
        
        Args:
            base_amount: The base amount to calculate discount from
            customer_data: Customer information for eligibility checking
            
        Returns:
            Calculated discount amount
        """
        if not self.is_eligible(customer_data):
            return Decimal('0.00')
        
        if self.discount_type == DiscountType.PERCENTAGE:
            discount = (base_amount * self.percentage_value) / 100
        elif self.discount_type == DiscountType.FIXED_AMOUNT:
            discount = self.fixed_amount or Decimal('0.00')
        elif self.discount_type == DiscountType.TIERED:
            discount = self._calculate_tiered_discount(base_amount, customer_data)
        elif self.discount_type == DiscountType.VOLUME:
            discount = self._calculate_volume_discount(base_amount, customer_data)
        else:
            discount = Decimal('0.00')
        
        # Apply limits
        if self.max_discount_amount:
            discount = min(discount, self.max_discount_amount)
        if self.min_discount_amount:
            discount = max(discount, self.min_discount_amount)
        
        return discount
    
    def is_eligible(self, customer_data: Dict[str, Any] = None) -> bool:
        """
        Check if a customer is eligible for this discount.
        
        Args:
            customer_data: Customer information for eligibility checking
            
        Returns:
            True if customer is eligible
        """
        if not self.is_active:
            return False
        
        # Check date validity
        now = datetime.utcnow()
        if self.effective_date and now < self.effective_date:
            return False
        if self.expiration_date and now > self.expiration_date:
            return False
        
        # Check promotional date ranges
        if self.is_promotional:
            if self.promotion_start_date and now < self.promotion_start_date:
                return False
            if self.promotion_end_date and now > self.promotion_end_date:
                return False
        
        # Check usage limits
        if self.max_uses_total and self.current_use_count >= self.max_uses_total:
            return False
        
        if not customer_data:
            return True
        
        # Check age eligibility
        customer_age = customer_data.get('age')
        if customer_age:
            if self.min_age and customer_age < self.min_age:
                return False
            if self.max_age and customer_age > self.max_age:
                return False
        
        # Check premium eligibility
        premium_amount = customer_data.get('premium_amount')
        if premium_amount and self.min_premium_amount:
            if premium_amount < self.min_premium_amount:
                return False
        
        # Check loyalty eligibility
        loyalty_years = customer_data.get('loyalty_years', 0)
        if self.min_loyalty_years and loyalty_years < self.min_loyalty_years:
            return False
        
        # Check complex eligibility criteria from JSON
        if self.eligibility_criteria:
            return self._check_complex_eligibility(customer_data)
        
        return True
    
    def _calculate_tiered_discount(self, base_amount: Decimal, customer_data: Dict[str, Any]) -> Decimal:
        """Calculate discount based on tiered structure."""
        if not self.tier_structure or 'tiers' not in self.tier_structure:
            return Decimal('0.00')
        
        threshold_type = self.tier_structure.get('threshold_type', 'premium_amount')
        
        if threshold_type == 'premium_amount':
            threshold_value = base_amount
        else:
            threshold_value = customer_data.get(threshold_type, 0)
        
        # Find applicable tier
        applicable_tier = None
        for tier in sorted(self.tier_structure['tiers'], key=lambda x: x['threshold']):
            if threshold_value >= tier['threshold']:
                applicable_tier = tier
        
        if not applicable_tier:
            return Decimal('0.00')
        
        # Calculate discount based on tier
        if applicable_tier.get('discount_percentage'):
            return (base_amount * Decimal(applicable_tier['discount_percentage'])) / 100
        elif applicable_tier.get('discount_amount'):
            return Decimal(applicable_tier['discount_amount'])
        
        return Decimal('0.00')
    
    def _calculate_volume_discount(self, base_amount: Decimal, customer_data: Dict[str, Any]) -> Decimal:
        """Calculate volume-based discount."""
        # Volume discount logic - can be customized based on business rules
        volume_factor = customer_data.get('policy_count', 1)
        
        if volume_factor >= 5:
            return (base_amount * Decimal('15')) / 100
        elif volume_factor >= 3:
            return (base_amount * Decimal('10')) / 100
        elif volume_factor >= 2:
            return (base_amount * Decimal('5')) / 100
        
        return Decimal('0.00')
    
    def _check_complex_eligibility(self, customer_data: Dict[str, Any]) -> bool:
        """Check eligibility against complex JSON criteria."""
        criteria = self.eligibility_criteria
        
        # Check geographic restrictions
        if 'geographic_restrictions' in criteria:
            customer_location = customer_data.get('location')
            if customer_location and customer_location not in criteria['geographic_restrictions']:
                return False
        
        # Check policy types
        if 'policy_types' in criteria:
            customer_policy_types = customer_data.get('policy_types', [])
            if not any(pt in criteria['policy_types'] for pt in customer_policy_types):
                return False
        
        # Check customer segments
        if 'customer_segments' in criteria:
            customer_segment = customer_data.get('segment')
            if customer_segment and customer_segment not in criteria['customer_segments']:
                return False
        
        # Check membership requirements
        if criteria.get('membership_required', False):
            if not customer_data.get('has_membership', False):
                return False
        
        return True
    
    def can_stack_with(self, other_discount: 'PricingDiscount') -> bool:
        """
        Check if this discount can be stacked with another discount.
        
        Args:
            other_discount: Another discount to check stacking compatibility
            
        Returns:
            True if discounts can be stacked
        """
        if not self.is_stackable or not other_discount.is_stackable:
            return False
        
        # Check exclusive relationships
        if self.exclusive_with:
            if other_discount.code in self.exclusive_with:
                return False
        
        if other_discount.exclusive_with:
            if self.code in other_discount.exclusive_with:
                return False
        
        return True
    
    def record_usage(self, customer_id: str = None) -> bool:
        """
        Record usage of this discount and check limits.
        
        Args:
            customer_id: ID of customer using the discount
            
        Returns:
            True if usage was recorded successfully
        """
        # Check total usage limit
        if self.max_uses_total and self.current_use_count >= self.max_uses_total:
            return False
        
        # TODO: Check per-customer usage limit (would need usage tracking table)
        
        # Increment usage count
        self.current_use_count = (self.current_use_count or 0) + 1
        
        return True
    
    def validate_configuration(self) -> tuple[bool, str]:
        """
        Validate the discount configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.discount_type == DiscountType.PERCENTAGE:
            if not self.percentage_value or self.percentage_value <= 0 or self.percentage_value > 100:
                return False, "Percentage value must be between 0 and 100"
        
        elif self.discount_type == DiscountType.FIXED_AMOUNT:
            if not self.fixed_amount or self.fixed_amount <= 0:
                return False, "Fixed amount must be greater than 0"
        
        elif self.discount_type == DiscountType.TIERED:
            if not self.tier_structure or 'tiers' not in self.tier_structure:
                return False, "Tiered discount must have tier structure defined"
        
        # Validate date ranges
        if self.promotion_start_date and self.promotion_end_date:
            if self.promotion_start_date >= self.promotion_end_date:
                return False, "Promotion start date must be before end date"
        
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
            'name': self.name,
            'description': self.description,
            'discount_type': self.discount_type.value if self.discount_type else None,
            'discount_scope': self.discount_scope.value if self.discount_scope else None,
            'percentage_value': float(self.percentage_value) if self.percentage_value else None,
            'fixed_amount': float(self.fixed_amount) if self.fixed_amount else None,
            'currency': self.currency,
            'max_discount_amount': float(self.max_discount_amount) if self.max_discount_amount else None,
            'is_promotional': self.is_promotional,
            'campaign_name': self.campaign_name,
            'promotion_start_date': self.promotion_start_date.isoformat() if self.promotion_start_date else None,
            'promotion_end_date': self.promotion_end_date.isoformat() if self.promotion_end_date else None,
            'is_stackable': self.is_stackable,
            'is_active': self.is_active,
            'is_auto_apply': self.is_auto_apply,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        if self.discount_type == DiscountType.PERCENTAGE:
            return f"<PricingDiscount(code='{self.code}', {self.percentage_value}%)>"
        elif self.discount_type == DiscountType.FIXED_AMOUNT:
            return f"<PricingDiscount(code='{self.code}', {self.fixed_amount} {self.currency})>"
        else:
            return f"<PricingDiscount(code='{self.code}', type='{self.discount_type.value}')>"

    def __str__(self) -> str:
        return f"{self.name}: {self.discount_type.value}"