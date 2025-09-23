# app/modules/pricing/plans/models/plan_model.py

"""
Plan Model - Production Ready

Complete implementation of insurance plan model with all enterprise features.
Fully integrated with product catalog and pricing engine.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, ForeignKey, 
    Index, CheckConstraint, Date, UniqueConstraint, Numeric, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
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

class PlanType(str, Enum):
    """Plan type enumeration"""
    INDIVIDUAL = "individual"
    FAMILY = "family"
    GROUP = "group"
    CORPORATE = "corporate"
    SME = "sme"
    GOVERNMENT = "government"
    STUDENT = "student"
    SENIOR = "senior"
    CUSTOM = "custom"


class PlanTier(str, Enum):
    """Plan tier levels"""
    BASIC = "basic"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    CUSTOM = "custom"


class PlanStatus(str, Enum):
    """Plan lifecycle status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISCONTINUED = "discontinued"
    ARCHIVED = "archived"


class ApprovalStatus(str, Enum):
    """Regulatory approval status"""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONDITIONAL = "conditional"


class Visibility(str, Enum):
    """Plan visibility settings"""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    INTERNAL = "internal"
    PARTNER = "partner"


class PaymentFrequency(str, Enum):
    """Premium payment frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    SINGLE = "single"


# ================================================================
# PLAN MODEL
# ================================================================

class Plan(Base):
    """
    Plan Model
    
    Core entity representing insurance plans.
    Links products to specific offerings with pricing and benefits.
    """
    
    __tablename__ = "plans"
    
    # Add table arguments for performance and constraints
    __table_args__ = (
        # Unique constraint on plan code per company
        UniqueConstraint('company_id', 'plan_code', name='uq_company_plan_code'),
        
        # Indexes for performance
        Index('idx_plans_product_id', 'product_id'),
        Index('idx_plans_company_id', 'company_id'),
        Index('idx_plans_plan_type', 'plan_type'),
        Index('idx_plans_status', 'status'),
        Index('idx_plans_is_active', 'is_active'),
        Index('idx_plans_effective_date', 'effective_date'),
        
        # Composite indexes
        Index('idx_plans_product_active', 'product_id', 'is_active'),
        Index('idx_plans_company_active', 'company_id', 'is_active'),
        Index('idx_plans_status_approval', 'status', 'regulatory_approval_status'),
        
        # Check constraints
        CheckConstraint('premium_amount >= 0', name='check_plan_premium_positive'),
        CheckConstraint('coverage_period_months > 0', name='check_plan_coverage_positive'),
        CheckConstraint('minimum_group_size >= 1', name='check_plan_min_group'),
        CheckConstraint('maximum_issue_age >= 0 AND maximum_issue_age <= 150', 
                       name='check_plan_max_age'),
        CheckConstraint('profit_target >= -100 AND profit_target <= 100', 
                       name='check_plan_profit_range'),
        CheckConstraint('end_date IS NULL OR end_date >= start_date', 
                       name='check_plan_date_range'),
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
    
    plan_code = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Unique plan code within company"
    )
    
    # ================================================================
    # FOREIGN KEYS
    # ================================================================
    
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_catalog.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Reference to product catalog"
    )
    
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        comment="Company offering this plan"
    )
    
    # ================================================================
    # BASIC INFORMATION
    # ================================================================
    
    name = Column(
        String(200),
        nullable=False,
        comment="Plan display name"
    )
    
    name_ar = Column(
        String(200),
        nullable=True,
        comment="Plan name in Arabic"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed plan description"
    )
    
    description_ar = Column(
        Text,
        nullable=True,
        comment="Plan description in Arabic"
    )
    
    plan_type = Column(
        String(50),
        nullable=False,
        default=PlanType.INDIVIDUAL.value,
        comment="Type of plan"
    )
    
    plan_tier = Column(
        String(50),
        nullable=True,
        default=PlanTier.SILVER.value,
        comment="Plan tier level"
    )
    
    # ================================================================
    # STATUS & LIFECYCLE
    # ================================================================
    
    status = Column(
        String(50),
        nullable=False,
        default=PlanStatus.DRAFT.value,
        comment="Current plan status"
    )
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Is plan currently active for sale"
    )
    
    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Is default plan for product"
    )
    
    visibility = Column(
        String(20),
        nullable=False,
        default=Visibility.PUBLIC.value,
        comment="Plan visibility setting"
    )
    
    # ================================================================
    # DATES
    # ================================================================
    
    effective_date = Column(
        Date,
        nullable=True,
        comment="Plan effective start date"
    )
    
    expiry_date = Column(
        Date,
        nullable=True,
        comment="Plan expiration date"
    )
    
    start_date = Column(
        Date,
        nullable=True,
        comment="Sales start date"
    )
    
    end_date = Column(
        Date,
        nullable=True,
        comment="Sales end date"
    )
    
    # ================================================================
    # VERSIONING
    # ================================================================
    
    version = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Plan version number"
    )
    
    parent_plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="SET NULL"),
        nullable=True,
        comment="Parent plan for versioning"
    )
    
    # ================================================================
    # PRICING
    # ================================================================
    
    premium_amount = Column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Base premium amount"
    )
    
    currency = Column(
        String(3),
        nullable=False,
        default='USD',
        comment="ISO 4217 currency code"
    )
    
    coverage_period_months = Column(
        Integer,
        nullable=False,
        default=12,
        comment="Coverage period in months"
    )
    
    payment_frequency = Column(
        String(20),
        nullable=False,
        default=PaymentFrequency.MONTHLY.value,
        comment="Premium payment frequency"
    )
    
    profit_target = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Target profit margin percentage"
    )
    
    # ================================================================
    # REGULATORY & COMPLIANCE
    # ================================================================
    
    regulatory_approval_status = Column(
        String(50),
        nullable=False,
        default=ApprovalStatus.NOT_REQUIRED.value,
        comment="Regulatory approval status"
    )
    
    regulatory_filing_reference = Column(
        String(100),
        nullable=True,
        comment="Regulatory filing reference"
    )
    
    approval_required = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Requires approval before activation"
    )
    
    approved_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who approved the plan"
    )
    
    approved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Approval timestamp"
    )
    
    # ================================================================
    # MARKET & DISTRIBUTION
    # ================================================================
    
    target_market_segment = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Target market segments configuration"
    )
    
    distribution_channels = Column(
        ARRAY(String),
        nullable=True,
        default=[],
        comment="Allowed distribution channels"
    )
    
    commission_structure = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Commission structure by channel"
    )
    
    competitive_positioning = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Competitive analysis data"
    )
    
    # ================================================================
    # UNDERWRITING & ELIGIBILITY
    # ================================================================
    
    underwriting_guidelines = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Underwriting rules and guidelines"
    )
    
    minimum_group_size = Column(
        Integer,
        nullable=True,
        comment="Minimum group size for group plans"
    )
    
    maximum_group_size = Column(
        Integer,
        nullable=True,
        comment="Maximum group size"
    )
    
    minimum_age = Column(
        Integer,
        nullable=True,
        comment="Minimum enrollment age"
    )
    
    maximum_issue_age = Column(
        Integer,
        nullable=True,
        comment="Maximum age for new enrollment"
    )
    
    # ================================================================
    # WAITING PERIODS & TERMS
    # ================================================================
    
    waiting_periods = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Waiting periods by benefit type"
    )
    
    renewal_terms = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Renewal terms and conditions"
    )
    
    cancellation_terms = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Cancellation policy"
    )
    
    # ================================================================
    # DOCUMENTS & MATERIALS
    # ================================================================
    
    policy_terms_url = Column(
        String(500),
        nullable=True,
        comment="URL to policy terms document"
    )
    
    marketing_materials_url = Column(
        String(500),
        nullable=True,
        comment="URL to marketing materials"
    )
    
    brochure_url = Column(
        String(500),
        nullable=True,
        comment="URL to plan brochure"
    )
    
    # ================================================================
    # METADATA
    # ================================================================
    
    tags = Column(
        ARRAY(String),
        nullable=True,
        default=[],
        comment="Searchable tags"
    )
    
    plan_metadata = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Additional metadata"
    )
    
    # ================================================================
    # AUDIT FIELDS
    # ================================================================
    
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
    
    archived_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
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
    
    archived_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    # Product relationship
    product = relationship(
        "ProductCatalog",
        back_populates="plans",
        lazy="joined"
    )
    
    # Company relationship
    company = relationship(
        "Company",
        back_populates="plans"
    )
    
    # Benefit schedules
    benefit_schedules = relationship(
        "PlanBenefitSchedule",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Coverage links
    coverage_links = relationship(
        "PlanCoverageLink",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Exclusions
    exclusions = relationship(
        "PlanExclusion",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Versions (self-referential)
    child_versions = relationship(
        "Plan",
        backref="parent_plan",
        remote_side=[id],
        lazy="select"
    )
    
    # Territories
    territories = relationship(
        "PlanTerritory",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('plan_type')
    def validate_plan_type(self, key, value):
        """Validate plan type"""
        if value not in [e.value for e in PlanType]:
            raise ValueError(f"Invalid plan type: {value}")
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        """Validate plan status"""
        if value not in [e.value for e in PlanStatus]:
            raise ValueError(f"Invalid status: {value}")
        return value
    
    @validates('premium_amount')
    def validate_premium(self, key, value):
        """Validate premium amount"""
        if value is not None and value < 0:
            raise ValueError("Premium amount cannot be negative")
        return value
    
    @validates('currency')
    def validate_currency(self, key, value):
        """Validate currency code"""
        if value and len(value) != 3:
            raise ValueError("Currency must be 3-letter ISO code")
        return value.upper() if value else value
    
    # ================================================================
    # PROPERTIES & METHODS
    # ================================================================
    
    @property
    def is_renewable(self) -> bool:
        """Check if plan is renewable"""
        if self.renewal_terms:
            return self.renewal_terms.get('renewable', True)
        return True
    
    @property
    def requires_underwriting(self) -> bool:
        """Check if plan requires underwriting"""
        if self.underwriting_guidelines:
            return self.underwriting_guidelines.get('required', False)
        return False
    
    @property
    def has_waiting_period(self) -> bool:
        """Check if plan has waiting periods"""
        return bool(self.waiting_periods)
    
    @property
    def is_group_plan(self) -> bool:
        """Check if this is a group plan"""
        return self.plan_type in [PlanType.GROUP.value, PlanType.CORPORATE.value]
    
    @property
    def allows_dependents(self) -> bool:
        """Check if plan allows dependents"""
        return self.metadata.get('allows_dependents', True) if self.metadata else True
    
    def get_commission_rate(self, channel: str) -> Decimal:
        """Get commission rate for a channel"""
        if self.commission_structure:
            channel_config = self.commission_structure.get(channel, {})
            return Decimal(str(channel_config.get('rate', 0)))
        return Decimal('0')
    
    def calculate_premium(
        self,
        age: Optional[int] = None,
        group_size: Optional[int] = None
    ) -> Decimal:
        """
        Calculate premium with adjustments
        
        Args:
            age: Member age for age-based pricing
            group_size: Group size for group discounts
            
        Returns:
            Calculated premium amount
        """
        base_premium = Decimal(str(self.premium_amount))
        
        # Age adjustment
        if age and self.metadata and 'age_factors' in self.metadata:
            age_factors = self.metadata['age_factors']
            for bracket in age_factors:
                if bracket['min_age'] <= age <= bracket['max_age']:
                    base_premium *= Decimal(str(bracket['factor']))
                    break
        
        # Group size discount
        if group_size and self.is_group_plan and self.metadata:
            discounts = self.metadata.get('group_discounts', [])
            for discount in discounts:
                if discount['min_size'] <= group_size <= discount.get('max_size', 99999):
                    base_premium *= (1 - Decimal(str(discount['discount'])))
                    break
        
        return base_premium.quantize(Decimal('0.01'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'plan_code': self.plan_code,
            'product_id': str(self.product_id),
            'company_id': str(self.company_id),
            'name': self.name,
            'plan_type': self.plan_type,
            'plan_tier': self.plan_tier,
            'status': self.status,
            'is_active': self.is_active,
            'premium_amount': float(self.premium_amount),
            'currency': self.currency,
            'coverage_period_months': self.coverage_period_months,
            'version': self.version,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f"<Plan(id={self.id}, code={self.plan_code}, name={self.name}, status={self.status})>"