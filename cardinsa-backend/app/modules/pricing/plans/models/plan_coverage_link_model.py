# app/modules/pricing/plans/models/plan_coverage_link_model.py

"""
Plan Coverage Link Model - Production Ready

Links plans to specific coverage options with detailed configuration.
Manages coverage limits, deductibles, and network restrictions.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, ForeignKey,
    Index, CheckConstraint, Date, UniqueConstraint, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import date, datetime
from enum import Enum
import uuid


# ================================================================
# ENUMS
# ================================================================

class CoverageTier(str, Enum):
    """Coverage tier levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    COMPREHENSIVE = "comprehensive"


class LimitType(str, Enum):
    """Coverage limit type"""
    PER_INCIDENT = "per_incident"
    PER_YEAR = "per_year"
    PER_LIFETIME = "per_lifetime"
    PER_PERSON = "per_person"
    PER_FAMILY = "per_family"
    AGGREGATE = "aggregate"


class NetworkRestriction(str, Enum):
    """Network restriction types"""
    NONE = "none"
    IN_NETWORK_ONLY = "in_network_only"
    PREFERRED_NETWORK = "preferred_network"
    TIERED_NETWORK = "tiered_network"
    RESTRICTED_NETWORK = "restricted_network"


class CoverageStatus(str, Enum):
    """Coverage link status"""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    EXCLUDED = "excluded"


# ================================================================
# PLAN COVERAGE LINK MODEL
# ================================================================

class PlanCoverageLink(Base):
    """
    Plan Coverage Link Model
    
    Defines the relationship between plans and coverage options,
    including specific limits, deductibles, and conditions.
    """
    
    __tablename__ = "plan_coverage_links"
    
    __table_args__ = (
        # Unique coverage per plan
        UniqueConstraint('plan_id', 'coverage_id', name='uq_plan_coverage'),
        
        # Indexes
        Index('idx_plan_coverage_links_plan_id', 'plan_id'),
        Index('idx_plan_coverage_links_coverage_id', 'coverage_id'),
        Index('idx_plan_coverage_links_is_mandatory', 'is_mandatory'),
        Index('idx_plan_coverage_links_tier', 'coverage_tier'),
        
        # Composite indexes
        Index('idx_plan_coverage_links_plan_mandatory', 'plan_id', 'is_mandatory'),
        Index('idx_plan_coverage_links_plan_excluded', 'plan_id', 'is_excluded'),
        
        # Constraints
        CheckConstraint('coverage_amount >= 0', name='check_coverage_amount_positive'),
        CheckConstraint('deductible >= 0', name='check_deductible_positive'),
        CheckConstraint('copay_percentage >= 0 AND copay_percentage <= 100',
                       name='check_copay_percentage_range'),
        CheckConstraint('annual_maximum >= 0', name='check_annual_max_positive'),
        CheckConstraint('lifetime_maximum >= 0', name='check_lifetime_max_positive'),
        CheckConstraint('frequency_limit >= 0', name='check_frequency_positive'),
    )
    
    # ================================================================
    # PRIMARY KEY & IDENTIFIERS
    # ================================================================
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # ================================================================
    # FOREIGN KEYS
    # ================================================================
    
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to parent plan"
    )
    
    coverage_id = Column(
        UUID(as_uuid=True),
        ForeignKey("coverages.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to coverage type"
    )
    
    # ================================================================
    # COVERAGE CONFIGURATION
    # ================================================================
    
    coverage_tier = Column(
        String(50),
        nullable=False,
        default=CoverageTier.STANDARD.value,
        comment="Coverage tier level"
    )
    
    coverage_amount = Column(
        NUMERIC(15, 2),
        nullable=False,
        default=0,
        comment="Maximum coverage amount"
    )
    
    specific_limit = Column(
        NUMERIC(15, 2),
        nullable=True,
        comment="Specific sub-limit if applicable"
    )
    
    limit_type = Column(
        String(50),
        nullable=False,
        default=LimitType.PER_YEAR.value,
        comment="Type of limit application"
    )
    
    unit = Column(
        String(50),
        nullable=True,
        comment="Unit of measurement (days, visits, etc.)"
    )
    
    # ================================================================
    # COST SHARING
    # ================================================================
    
    deductible = Column(
        NUMERIC(15, 2),
        nullable=False,
        default=0,
        comment="Deductible amount"
    )
    
    copay_percentage = Column(
        NUMERIC(5, 2),
        nullable=False,
        default=0,
        comment="Copayment percentage"
    )
    
    copay_amount = Column(
        NUMERIC(10, 2),
        nullable=True,
        comment="Fixed copayment amount"
    )
    
    coinsurance = Column(
        NUMERIC(5, 2),
        nullable=True,
        comment="Coinsurance percentage"
    )
    
    # ================================================================
    # LIMITS & RESTRICTIONS
    # ================================================================
    
    frequency_limit = Column(
        Integer,
        nullable=True,
        comment="Frequency limit (per period)"
    )
    
    annual_maximum = Column(
        NUMERIC(15, 2),
        nullable=True,
        comment="Annual maximum coverage"
    )
    
    lifetime_maximum = Column(
        NUMERIC(15, 2),
        nullable=True,
        comment="Lifetime maximum coverage"
    )
    
    waiting_period_days = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Waiting period in days"
    )
    
    # ================================================================
    # CONDITIONS & REQUIREMENTS
    # ================================================================
    
    is_mandatory = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Is mandatory coverage"
    )
    
    is_excluded = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Is explicitly excluded"
    )
    
    approval_needed = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Requires pre-approval"
    )
    
    prior_authorization_required = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Requires prior authorization"
    )
    
    # ================================================================
    # NETWORK & GEOGRAPHIC
    # ================================================================
    
    network_restrictions = Column(
        String(50),
        nullable=False,
        default=NetworkRestriction.NONE.value,
        comment="Network restriction type"
    )
    
    geographic_restrictions = Column(
        JSONB,
        nullable=True,
        comment="Geographic coverage restrictions"
    )
    
    # ================================================================
    # CATEGORIZATION
    # ================================================================
    
    sub_category = Column(
        String(100),
        nullable=True,
        comment="Coverage sub-category"
    )
    
    condition_tag = Column(
        String(100),
        nullable=True,
        comment="Condition/disease tag"
    )
    
    # ================================================================
    # DATES
    # ================================================================
    
    effective_date = Column(
        Date,
        nullable=True,
        comment="Coverage effective date"
    )
    
    expiry_date = Column(
        Date,
        nullable=True,
        comment="Coverage expiry date"
    )
    
    # ================================================================
    # NOTES & DOCUMENTATION
    # ================================================================
    
    notes = Column(
        Text,
        nullable=True,
        comment="Internal notes"
    )
    
    member_description = Column(
        Text,
        nullable=True,
        comment="Member-facing description"
    )
    
    member_description_ar = Column(
        Text,
        nullable=True,
        comment="Member description in Arabic"
    )
    
    # ================================================================
    # METADATA
    # ================================================================
    
    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Display order for UI"
    )
    
    tags = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="Coverage tags"
    )
    
    coverage_link_metadata = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Additional metadata"
    )
    
    # ================================================================
    # AUDIT FIELDS
    # ================================================================
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    archived_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    plan = relationship(
        "Plan",
        back_populates="coverage_links",
        foreign_keys=[plan_id]
    )
    
    coverage = relationship(
        "Coverage",
        back_populates="plan_links",
        foreign_keys=[coverage_id]
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('coverage_tier')
    def validate_coverage_tier(self, key, value):
        """Validate coverage tier"""
        if value not in [e.value for e in CoverageTier]:
            raise ValueError(f"Invalid coverage tier: {value}")
        return value
    
    @validates('limit_type')
    def validate_limit_type(self, key, value):
        """Validate limit type"""
        if value not in [e.value for e in LimitType]:
            raise ValueError(f"Invalid limit type: {value}")
        return value
    
    @validates('network_restrictions')
    def validate_network_restrictions(self, key, value):
        """Validate network restrictions"""
        if value not in [e.value for e in NetworkRestriction]:
            raise ValueError(f"Invalid network restriction: {value}")
        return value
    
    # ================================================================
    # METHODS
    # ================================================================
    
    def calculate_member_cost(
        self,
        service_cost: Decimal,
        accumulated_deductible: Decimal = Decimal('0')
    ) -> Dict[str, Decimal]:
        """
        Calculate member cost for a service
        
        Args:
            service_cost: Total service cost
            accumulated_deductible: Already paid deductible
            
        Returns:
            Dictionary with cost breakdown
        """
        remaining_deductible = max(
            Decimal('0'),
            Decimal(str(self.deductible)) - accumulated_deductible
        )
        
        # Apply deductible
        deductible_portion = min(service_cost, remaining_deductible)
        after_deductible = service_cost - deductible_portion
        
        # Apply copay/coinsurance
        if self.copay_amount:
            copay = Decimal(str(self.copay_amount))
            insurance_pays = after_deductible - copay
        elif self.copay_percentage:
            copay_rate = Decimal(str(self.copay_percentage)) / Decimal('100')
            copay = after_deductible * copay_rate
            insurance_pays = after_deductible - copay
        elif self.coinsurance:
            member_rate = Decimal(str(self.coinsurance)) / Decimal('100')
            copay = after_deductible * member_rate
            insurance_pays = after_deductible - copay
        else:
            copay = Decimal('0')
            insurance_pays = after_deductible
        
        # Apply coverage limit
        if self.coverage_amount:
            max_coverage = Decimal(str(self.coverage_amount))
            if insurance_pays > max_coverage:
                insurance_pays = max_coverage
                copay = after_deductible - insurance_pays
        
        member_total = deductible_portion + copay
        
        return {
            'service_cost': service_cost,
            'deductible': deductible_portion,
            'copay': copay,
            'member_pays': member_total,
            'insurance_pays': insurance_pays
        }
    
    def is_within_limit(self, current_usage: Decimal) -> bool:
        """
        Check if current usage is within limits
        
        Args:
            current_usage: Current usage amount
            
        Returns:
            True if within limits
        """
        if not self.coverage_amount:
            return True
        
        return current_usage < Decimal(str(self.coverage_amount))
    
    def get_remaining_coverage(self, current_usage: Decimal) -> Decimal:
        """
        Get remaining coverage amount
        
        Args:
            current_usage: Current usage amount
            
        Returns:
            Remaining coverage amount
        """
        if not self.coverage_amount:
            return Decimal('999999999')  # Unlimited
        
        remaining = Decimal(str(self.coverage_amount)) - current_usage
        return max(Decimal('0'), remaining)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'plan_id': str(self.plan_id),
            'coverage_id': str(self.coverage_id),
            'coverage_tier': self.coverage_tier,
            'coverage_amount': float(self.coverage_amount) if self.coverage_amount else None,
            'deductible': float(self.deductible) if self.deductible else 0,
            'copay_percentage': float(self.copay_percentage) if self.copay_percentage else 0,
            'is_mandatory': self.is_mandatory,
            'is_excluded': self.is_excluded,
            'waiting_period_days': self.waiting_period_days,
            'network_restrictions': self.network_restrictions
        }
    
    def __repr__(self) -> str:
        return f"<PlanCoverageLink(id={self.id}, plan_id={self.plan_id}, coverage_id={self.coverage_id}, mandatory={self.is_mandatory})>"