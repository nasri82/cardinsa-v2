# app/modules/pricing/modifiers/models/pricing_commission_model.py

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
import enum
from typing import Dict, Any, Optional

from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin

class CommissionType(enum.Enum):
    """Commission calculation types"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED = "tiered"
    PERFORMANCE_BASED = "performance_based"
    OVERRIDE = "override"
    BONUS = "bonus"

class CommissionBasis(enum.Enum):
    """What commission is calculated on"""
    PREMIUM = "premium"
    FIRST_YEAR_PREMIUM = "first_year_premium"
    RENEWAL_PREMIUM = "renewal_premium"
    NET_PREMIUM = "net_premium"
    GROSS_PREMIUM = "gross_premium"
    POLICY_FEE = "policy_fee"

class PaymentFrequency(enum.Enum):
    """Commission payment frequency"""
    IMMEDIATE = "immediate"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    AS_EARNED = "as_earned"

class AgentLevel(enum.Enum):
    """Agent hierarchy levels"""
    AGENT = "agent"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"
    REGIONAL_MANAGER = "regional_manager"
    DIRECTOR = "director"

class PricingCommission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Pricing Commission Model for Step 5 - Advanced Pricing Components
    
    This model handles complex commission structures for insurance agents,
    brokers, and sales representatives including:
    - Multiple commission calculation methods
    - Tiered commission structures based on performance
    - Override commissions for management
    - Renewal vs new business commission rates
    - Performance bonuses and incentives
    - Multi-level commission hierarchies
    
    Key Features:
    - Flexible commission calculation (percentage, fixed, tiered)
    - Performance-based commission adjustments
    - Multi-level agent hierarchy support
    - Renewal and new business differentiation
    - Commission caps and minimum guarantees
    - Payment scheduling and tracking
    - Integration with pricing profiles
    - Comprehensive audit and compliance features
    """
    __tablename__ = "agent_commissions"

    # =====================================================
    # CORE FIELDS
    # =====================================================
    
    code = Column(String(50), unique=True, nullable=False, index=True,
                 comment="Unique identifier code for the commission (e.g., 'AGENT_MEDICAL_5', 'MGR_OVERRIDE_2')")
    
    name = Column(String(200), nullable=False,
                 comment="Commission structure name")
    
    description = Column(Text,
                        comment="Detailed description of commission terms and conditions")

    # =====================================================
    # COMMISSION CONFIGURATION
    # =====================================================
    
    commission_type = Column(Enum(CommissionType), nullable=False,
                            comment="Type of commission calculation")
    
    commission_basis = Column(Enum(CommissionBasis), nullable=False, default=CommissionBasis.PREMIUM,
                             comment="What the commission is calculated on")
    
    # Basic commission values
    percentage_rate = Column(Numeric(8, 4),
                            comment="Commission percentage rate (supports up to 4 decimal places)")
    
    fixed_amount = Column(Numeric(15, 2),
                         comment="Fixed commission amount per policy")
    
    currency = Column(String(3), default="USD", nullable=False,
                     comment="ISO 3-letter currency code")

    # =====================================================
    # AGENT AND CHANNEL CONFIGURATION
    # =====================================================
    
    channel = Column(String(50), nullable=False,
                    comment="Sales channel: agent, broker, direct, online, phone")
    
    agent_level = Column(Enum(AgentLevel),
                        comment="Agent hierarchy level this commission applies to")
    
    agent_type = Column(String(50),
                       comment="Type of agent: captive, independent, employee, contractor")
    
    territory_restriction = Column(JSONB,
                                  comment="JSON array of territories where this commission applies")

    # =====================================================
    # BUSINESS TYPE CONFIGURATION
    # =====================================================
    
    business_type = Column(String(50), default="all",
                          comment="Type of business: new, renewal, cross_sell, up_sell, all")
    
    policy_types = Column(JSONB,
                         comment="JSON array of policy types this commission applies to")
    
    product_lines = Column(JSONB,
                          comment="JSON array of product lines this commission applies to")

    # =====================================================
    # TIERED COMMISSION STRUCTURE
    # =====================================================
    
    # JSON structure for tiered commissions
    tier_structure = Column(JSONB,
                           comment="JSON structure defining commission tiers and thresholds")
    
    # Example tier_structure:
    # {
    #   "tiers": [
    #     {"threshold": 10000, "rate": 5.0, "type": "premium_volume"},
    #     {"threshold": 50000, "rate": 7.5, "type": "premium_volume"},
    #     {"threshold": 100000, "rate": 10.0, "type": "premium_volume"}
    #   ],
    #   "threshold_type": "annual_premium", // or "policy_count", "retention_rate"
    #   "measurement_period": "annual" // or "quarterly", "monthly"
    # }

    # =====================================================
    # COMMISSION LIMITS AND CONTROLS
    # =====================================================
    
    min_commission = Column(Numeric(15, 2),
                           comment="Minimum commission amount (guaranteed minimum)")
    
    max_commission = Column(Numeric(15, 2),
                           comment="Maximum commission amount (cap)")
    
    min_premium_threshold = Column(Numeric(15, 2),
                                  comment="Minimum premium amount to earn commission")
    
    max_policies_per_period = Column(Integer,
                                    comment="Maximum policies that earn commission per period")

    # =====================================================
    # PERFORMANCE AND BONUS CONFIGURATION
    # =====================================================
    
    performance_metrics = Column(JSONB,
                                comment="JSON structure defining performance bonus criteria")
    
    # Example performance_metrics:
    # {
    #   "retention_rate_bonus": {"threshold": 0.85, "bonus_percentage": 2.0},
    #   "growth_bonus": {"threshold": 0.15, "bonus_percentage": 1.5},
    #   "quality_bonus": {"min_rating": 4.5, "bonus_amount": 500}
    # }
    
    bonus_eligibility = Column(JSONB,
                              comment="JSON structure defining bonus eligibility criteria")

    # =====================================================
    # PAYMENT AND TIMING
    # =====================================================
    
    payment_frequency = Column(Enum(PaymentFrequency), default=PaymentFrequency.MONTHLY,
                              comment="How often commissions are paid")
    
    payment_delay_days = Column(Integer, default=30,
                               comment="Number of days after earning before payment")
    
    advance_commission = Column(Boolean, default=False,
                               comment="Whether commission is paid in advance")
    
    chargeback_period_months = Column(Integer, default=12,
                                     comment="Period during which chargebacks can occur")
    
    # Renewal commission configuration
    renewal_commission_years = Column(Integer, default=1,
                                     comment="Number of years renewal commissions are paid")
    
    renewal_rate_decline = Column(Numeric(5, 2),
                                 comment="Annual decline in renewal commission rate (percentage)")

    # =====================================================
    # OVERRIDE COMMISSIONS
    # =====================================================
    
    is_override = Column(Boolean, default=False,
                        comment="Whether this is an override commission for management")
    
    override_levels = Column(JSONB,
                            comment="JSON structure defining override commission levels")
    
    # Example override_levels:
    # {
    #   "level_1": {"rate": 2.0, "agent_levels": ["agent"]},
    #   "level_2": {"rate": 1.0, "agent_levels": ["supervisor", "agent"]},
    #   "level_3": {"rate": 0.5, "agent_levels": ["manager", "supervisor", "agent"]}
    # }

    # =====================================================
    # INTEGRATION WITH OTHER COMPONENTS
    # =====================================================
    
    profile_id = Column(UUID(as_uuid=True), ForeignKey('quotation_pricing_profiles.id'),
                       comment="Link to pricing profile from Step 4")
    
    priority = Column(Integer, default=100,
                     comment="Processing priority (lower = higher priority)")

    # =====================================================
    # VALIDITY AND STATUS
    # =====================================================
    
    effective_date = Column(DateTime, default=datetime.utcnow,
                           comment="Date when this commission structure becomes effective")
    
    expiration_date = Column(DateTime,
                            comment="Date when this commission structure expires")
    
    is_active = Column(Boolean, default=True, nullable=False, index=True,
                      comment="Whether this commission structure is currently active")
    
    requires_contract = Column(Boolean, default=False,
                              comment="Whether a signed contract is required for this commission")

    # =====================================================
    # AUDIT AND COMPLIANCE
    # =====================================================
    
    created_by = Column(UUID(as_uuid=True),
                       comment="User ID who created this commission structure")
    
    updated_by = Column(UUID(as_uuid=True),
                       comment="User ID who last updated this commission structure")
    
    version = Column(String(20), default="1.0",
                    comment="Version number for change tracking")
    
    approval_status = Column(String(50), default="draft",
                            comment="Approval status: draft, pending, approved, rejected")
    
    approved_by = Column(UUID(as_uuid=True),
                        comment="User ID who approved this commission structure")
    
    approved_at = Column(DateTime,
                        comment="Timestamp of approval")
    
    compliance_notes = Column(Text,
                             comment="Notes related to regulatory compliance")

    # =====================================================
    # RELATIONSHIPS
    # =====================================================
    
    # Relationship to pricing profile (Step 4 integration)
    profile = relationship("QuotationPricingProfile", back_populates="commissions")

    # =====================================================
    # TABLE CONFIGURATION
    # =====================================================
    
    __table_args__ = (
        # Indexes for performance
        {"comment": "Agent commission structures for Step 5 advanced pricing components"}
    )

    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def calculate_commission(self, premium_amount: Decimal, agent_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate commission amount based on premium and agent performance data.
        
        Args:
            premium_amount: The premium amount to calculate commission on
            agent_data: Agent performance and profile data
            
        Returns:
            Dictionary with commission calculation details
        """
        if not self.is_active or not self._is_applicable(agent_data):
            return {
                'commission_amount': Decimal('0.00'),
                'calculation_method': 'not_applicable',
                'details': 'Commission structure not applicable'
            }
        
        base_commission = self._calculate_base_commission(premium_amount, agent_data)
        performance_bonus = self._calculate_performance_bonus(premium_amount, agent_data)
        
        total_commission = base_commission + performance_bonus
        
        # Apply limits
        if self.min_commission:
            total_commission = max(total_commission, self.min_commission)
        if self.max_commission:
            total_commission = min(total_commission, self.max_commission)
        
        return {
            'commission_amount': total_commission,
            'base_commission': base_commission,
            'performance_bonus': performance_bonus,
            'calculation_method': self.commission_type.value,
            'commission_rate': self.percentage_rate,
            'currency': self.currency
        }
    
    def _calculate_base_commission(self, premium_amount: Decimal, agent_data: Dict[str, Any]) -> Decimal:
        """Calculate base commission amount."""
        if self.commission_type == CommissionType.PERCENTAGE:
            return (premium_amount * self.percentage_rate) / 100
        
        elif self.commission_type == CommissionType.FIXED_AMOUNT:
            return self.fixed_amount or Decimal('0.00')
        
        elif self.commission_type == CommissionType.TIERED:
            return self._calculate_tiered_commission(premium_amount, agent_data)
        
        elif self.commission_type == CommissionType.PERFORMANCE_BASED:
            return self._calculate_performance_based_commission(premium_amount, agent_data)
        
        return Decimal('0.00')
    
    def _calculate_tiered_commission(self, premium_amount: Decimal, agent_data: Dict[str, Any]) -> Decimal:
        """Calculate tiered commission based on performance thresholds."""
        if not self.tier_structure or 'tiers' not in self.tier_structure:
            return Decimal('0.00')
        
        threshold_type = self.tier_structure.get('threshold_type', 'annual_premium')
        
        # Get the threshold value from agent data
        if threshold_type == 'annual_premium':
            threshold_value = agent_data.get('annual_premium', premium_amount) if agent_data else premium_amount
        elif threshold_type == 'policy_count':
            threshold_value = agent_data.get('policy_count', 1) if agent_data else 1
        elif threshold_type == 'retention_rate':
            threshold_value = agent_data.get('retention_rate', 0.5) if agent_data else 0.5
        else:
            threshold_value = premium_amount
        
        # Find applicable tier
        applicable_tier = None
        for tier in sorted(self.tier_structure['tiers'], key=lambda x: x['threshold'], reverse=True):
            if threshold_value >= tier['threshold']:
                applicable_tier = tier
                break
        
        if not applicable_tier:
            # Use lowest tier if none match
            applicable_tier = min(self.tier_structure['tiers'], key=lambda x: x['threshold'])
        
        # Calculate commission based on tier rate
        tier_rate = applicable_tier.get('rate', 0)
        return (premium_amount * Decimal(tier_rate)) / 100
    
    def _calculate_performance_based_commission(self, premium_amount: Decimal, agent_data: Dict[str, Any]) -> Decimal:
        """Calculate performance-based commission with adjustments."""
        base_rate = self.percentage_rate or Decimal('5.0')  # Default 5% if not specified
        
        if not agent_data:
            return (premium_amount * base_rate) / 100
        
        # Performance adjustments
        retention_rate = agent_data.get('retention_rate', 0.8)
        growth_rate = agent_data.get('growth_rate', 0.0)
        quality_score = agent_data.get('quality_score', 3.0)
        
        # Adjust base rate based on performance
        adjusted_rate = base_rate
        
        # Retention bonus/penalty
        if retention_rate >= 0.9:
            adjusted_rate += Decimal('1.0')  # 1% bonus for 90%+ retention
        elif retention_rate < 0.7:
            adjusted_rate -= Decimal('1.0')  # 1% penalty for <70% retention
        
        # Growth bonus
        if growth_rate >= 0.15:
            adjusted_rate += Decimal('0.5')  # 0.5% bonus for 15%+ growth
        
        # Quality bonus
        if quality_score >= 4.5:
            adjusted_rate += Decimal('0.5')  # 0.5% bonus for high quality
        
        return (premium_amount * adjusted_rate) / 100
    
    def _calculate_performance_bonus(self, premium_amount: Decimal, agent_data: Dict[str, Any]) -> Decimal:
        """Calculate additional performance bonuses."""
        if not self.performance_metrics or not agent_data:
            return Decimal('0.00')
        
        total_bonus = Decimal('0.00')
        
        # Retention rate bonus
        if 'retention_rate_bonus' in self.performance_metrics:
            bonus_config = self.performance_metrics['retention_rate_bonus']
            retention_rate = agent_data.get('retention_rate', 0)
            
            if retention_rate >= bonus_config.get('threshold', 0.85):
                bonus_percentage = bonus_config.get('bonus_percentage', 0)
                total_bonus += (premium_amount * Decimal(bonus_percentage)) / 100
        
        # Growth bonus
        if 'growth_bonus' in self.performance_metrics:
            bonus_config = self.performance_metrics['growth_bonus']
            growth_rate = agent_data.get('growth_rate', 0)
            
            if growth_rate >= bonus_config.get('threshold', 0.15):
                bonus_percentage = bonus_config.get('bonus_percentage', 0)
                total_bonus += (premium_amount * Decimal(bonus_percentage)) / 100
        
        # Quality bonus (fixed amount)
        if 'quality_bonus' in self.performance_metrics:
            bonus_config = self.performance_metrics['quality_bonus']
            quality_rating = agent_data.get('quality_rating', 0)
            
            if quality_rating >= bonus_config.get('min_rating', 4.5):
                bonus_amount = bonus_config.get('bonus_amount', 0)
                total_bonus += Decimal(bonus_amount)
        
        return total_bonus
    
    def _is_applicable(self, agent_data: Dict[str, Any]) -> bool:
        """Check if this commission structure applies to the agent."""
        if not agent_data:
            return True
        
        # Check channel
        agent_channel = agent_data.get('channel')
        if agent_channel and self.channel != 'all' and agent_channel != self.channel:
            return False
        
        # Check agent level
        if self.agent_level:
            agent_level = agent_data.get('agent_level')
            if agent_level and agent_level != self.agent_level.value:
                return False
        
        # Check territory
        if self.territory_restriction:
            agent_territory = agent_data.get('territory')
            if agent_territory and agent_territory not in self.territory_restriction:
                return False
        
        # Check business type
        business_type = agent_data.get('business_type', 'new')
        if self.business_type != 'all' and business_type != self.business_type:
            return False
        
        return True
    
    def calculate_renewal_commission(self, year: int, original_commission: Decimal) -> Decimal:
        """
        Calculate renewal commission for a specific year.
        
        Args:
            year: Renewal year (1, 2, 3, etc.)
            original_commission: Original first-year commission amount
            
        Returns:
            Renewal commission amount
        """
        if year > self.renewal_commission_years:
            return Decimal('0.00')
        
        if not self.renewal_rate_decline:
            return original_commission
        
        # Apply annual decline
        decline_factor = (100 - (self.renewal_rate_decline * (year - 1))) / 100
        renewal_commission = original_commission * Decimal(decline_factor)
        
        return max(renewal_commission, Decimal('0.00'))
    
    def validate_configuration(self) -> tuple[bool, str]:
        """
        Validate the commission configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.commission_type == CommissionType.PERCENTAGE:
            if not self.percentage_rate or self.percentage_rate <= 0:
                return False, "Percentage rate must be greater than 0"
        
        elif self.commission_type == CommissionType.FIXED_AMOUNT:
            if not self.fixed_amount or self.fixed_amount <= 0:
                return False, "Fixed amount must be greater than 0"
        
        elif self.commission_type == CommissionType.TIERED:
            if not self.tier_structure or 'tiers' not in self.tier_structure:
                return False, "Tiered commission must have tier structure defined"
        
        # Validate limits
        if self.min_commission and self.max_commission:
            if self.min_commission >= self.max_commission:
                return False, "Minimum commission must be less than maximum commission"
        
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
            'commission_type': self.commission_type.value if self.commission_type else None,
            'commission_basis': self.commission_basis.value if self.commission_basis else None,
            'percentage_rate': float(self.percentage_rate) if self.percentage_rate else None,
            'fixed_amount': float(self.fixed_amount) if self.fixed_amount else None,
            'currency': self.currency,
            'channel': self.channel,
            'agent_level': self.agent_level.value if self.agent_level else None,
            'business_type': self.business_type,
            'payment_frequency': self.payment_frequency.value if self.payment_frequency else None,
            'is_override': self.is_override,
            'is_active': self.is_active,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        if self.commission_type == CommissionType.PERCENTAGE:
            return f"<PricingCommission(code='{self.code}', {self.percentage_rate}%, {self.channel})>"
        elif self.commission_type == CommissionType.FIXED_AMOUNT:
            return f"<PricingCommission(code='{self.code}', {self.fixed_amount} {self.currency}, {self.channel})>"
        else:
            return f"<PricingCommission(code='{self.code}', {self.commission_type.value}, {self.channel})>"

    def __str__(self) -> str:
        return f"{self.name}: {self.commission_type.value} - {self.channel}"