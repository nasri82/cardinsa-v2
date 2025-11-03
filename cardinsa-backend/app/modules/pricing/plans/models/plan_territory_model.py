# app/modules/pricing/plans/models/plan_territory_model.py

"""
Plan Territory Model - Production Ready

Manages geographic coverage and territorial restrictions for insurance plans.
Handles regional pricing adjustments and regulatory requirements by territory.
"""

from sqlalchemy import (
    Column, String, Boolean, ForeignKey,
    Index, CheckConstraint, Date, UniqueConstraint, Text, DateTime
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

class TerritoryType(str, Enum):
    """Territory type enumeration"""
    COUNTRY = "country"
    REGION = "region"
    STATE = "state"
    PROVINCE = "province"
    CITY = "city"
    DISTRICT = "district"
    ZONE = "zone"
    CUSTOM = "custom"


class TerritoryStatus(str, Enum):
    """Territory coverage status"""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    RESTRICTED = "restricted"
    DISCONTINUED = "discontinued"


class RegulatoryStatus(str, Enum):
    """Regulatory status for territory"""
    APPROVED = "approved"
    PENDING = "pending"
    RESTRICTED = "restricted"
    PROHIBITED = "prohibited"
    CONDITIONAL = "conditional"


# ================================================================
# PLAN TERRITORY MODEL
# ================================================================

class PlanTerritory(Base):
    """
    Plan Territory Model
    
    Defines geographic coverage areas for plans with specific
    pricing adjustments and regulatory requirements.
    """
    
    __tablename__ = "plan_territories"
    
    __table_args__ = (
        # Unique territory per plan
        UniqueConstraint('plan_id', 'territory_code', name='uq_plan_territory_code'),
        
        # Indexes
        Index('idx_plan_territories_plan_id', 'plan_id'),
        Index('idx_plan_territories_territory_type', 'territory_type'),
        Index('idx_plan_territories_is_active', 'is_active'),
        Index('idx_plan_territories_territory_code', 'territory_code'),
        
        # Composite indexes
        Index('idx_plan_territories_plan_active', 'plan_id', 'is_active'),
        Index('idx_plan_territories_type_active', 'territory_type', 'is_active'),
        
        # Constraints
        CheckConstraint('rate_adjustment >= -100 AND rate_adjustment <= 1000',
                       name='check_territory_rate_adjustment'),
        CheckConstraint('minimum_premium >= 0', name='check_territory_min_premium'),
        CheckConstraint('maximum_premium >= 0', name='check_territory_max_premium'),
        CheckConstraint('expiry_date IS NULL OR expiry_date >= effective_date',
                       name='check_territory_date_range'),
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
    
    # ================================================================
    # TERRITORY IDENTIFICATION
    # ================================================================
    
    territory_code = Column(
        String(50),
        nullable=False,
        comment="Territory code (ISO or custom)"
    )
    
    territory_name = Column(
        String(200),
        nullable=False,
        comment="Territory display name"
    )
    
    territory_name_ar = Column(
        String(200),
        nullable=True,
        comment="Territory name in Arabic"
    )
    
    territory_type = Column(
        String(20),
        nullable=False,
        default=TerritoryType.COUNTRY.value,
        comment="Type of territory"
    )
    
    parent_territory_code = Column(
        String(50),
        nullable=True,
        comment="Parent territory for hierarchical structure"
    )
    
    # ================================================================
    # GEOGRAPHIC DETAILS
    # ================================================================
    
    country_code = Column(
        String(2),
        nullable=True,
        comment="ISO 3166-1 alpha-2 country code"
    )
    
    region_code = Column(
        String(10),
        nullable=True,
        comment="Region/state code"
    )
    
    postal_codes = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="List of covered postal codes"
    )
    
    coordinates = Column(
        JSONB,
        nullable=True,
        comment="Geographic coordinates/boundaries"
    )
    
    timezone = Column(
        String(50),
        nullable=True,
        comment="Territory timezone"
    )
    
    # ================================================================
    # STATUS & AVAILABILITY
    # ================================================================
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Is territory currently active"
    )
    
    status = Column(
        String(20),
        nullable=False,
        default=TerritoryStatus.ACTIVE.value,
        comment="Territory status"
    )
    
    # ================================================================
    # DATES
    # ================================================================
    
    effective_date = Column(
        Date,
        nullable=False,
        server_default=func.current_date(),
        comment="Territory coverage start date"
    )
    
    expiry_date = Column(
        Date,
        nullable=True,
        comment="Territory coverage end date"
    )
    
    # ================================================================
    # PRICING ADJUSTMENTS
    # ================================================================
    
    rate_adjustment = Column(
        NUMERIC(6, 2),
        nullable=False,
        default=0,
        comment="Rate adjustment percentage for territory"
    )
    
    minimum_premium = Column(
        NUMERIC(15, 2),
        nullable=True,
        comment="Minimum premium for territory"
    )
    
    maximum_premium = Column(
        NUMERIC(15, 2),
        nullable=True,
        comment="Maximum premium for territory"
    )
    
    currency_code = Column(
        String(3),
        nullable=True,
        comment="Local currency code if different"
    )
    
    tax_rate = Column(
        NUMERIC(5, 2),
        nullable=True,
        comment="Local tax rate percentage"
    )
    
    # ================================================================
    # REGULATORY REQUIREMENTS
    # ================================================================
    
    regulatory_status = Column(
        String(20),
        nullable=False,
        default=RegulatoryStatus.APPROVED.value,
        comment="Regulatory status for territory"
    )
    
    regulatory_requirements = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Territory-specific regulatory requirements"
    )
    
    license_number = Column(
        String(100),
        nullable=True,
        comment="Territory-specific license number"
    )
    
    compliance_notes = Column(
        Text,
        nullable=True,
        comment="Compliance notes for territory"
    )
    
    # ================================================================
    # RESTRICTIONS & RULES
    # ================================================================
    
    eligibility_rules = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Territory-specific eligibility rules"
    )
    
    excluded_benefits = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="Benefits excluded in this territory"
    )
    
    required_benefits = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="Mandatory benefits for territory"
    )
    
    underwriting_rules = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Territory-specific underwriting rules"
    )
    
    # ================================================================
    # NETWORK & PROVIDERS
    # ================================================================
    
    network_restrictions = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Provider network restrictions"
    )
    
    preferred_providers = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="List of preferred provider IDs"
    )
    
    # ================================================================
    # METADATA
    # ================================================================
    
    tags = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="Territory tags"
    )
    
    territory_metadata = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Additional territory metadata"
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
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    plan = relationship(
        "Plan",
        back_populates="territories",
        foreign_keys=[plan_id]
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('territory_type')
    def validate_territory_type(self, key, value):
        """Validate territory type"""
        if value not in [e.value for e in TerritoryType]:
            raise ValueError(f"Invalid territory type: {value}")
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        """Validate territory status"""
        if value not in [e.value for e in TerritoryStatus]:
            raise ValueError(f"Invalid territory status: {value}")
        return value
    
    @validates('country_code')
    def validate_country_code(self, key, value):
        """Validate country code"""
        if value and len(value) != 2:
            raise ValueError("Country code must be 2-letter ISO code")
        return value.upper() if value else value
    
    @validates('currency_code')
    def validate_currency_code(self, key, value):
        """Validate currency code"""
        if value and len(value) != 3:
            raise ValueError("Currency must be 3-letter ISO code")
        return value.upper() if value else value
    
    # ================================================================
    # METHODS
    # ================================================================
    
    def calculate_adjusted_premium(self, base_premium: Decimal) -> Decimal:
        """
        Calculate premium with territorial adjustments
        
        Args:
            base_premium: Base premium amount
            
        Returns:
            Adjusted premium for territory
        """
        # Apply rate adjustment
        adjustment_factor = Decimal('1') + (Decimal(str(self.rate_adjustment)) / Decimal('100'))
        adjusted = base_premium * adjustment_factor
        
        # Apply minimum
        if self.minimum_premium:
            adjusted = max(adjusted, Decimal(str(self.minimum_premium)))
        
        # Apply maximum
        if self.maximum_premium:
            adjusted = min(adjusted, Decimal(str(self.maximum_premium)))
        
        # Apply tax if configured
        if self.tax_rate:
            tax_factor = Decimal('1') + (Decimal(str(self.tax_rate)) / Decimal('100'))
            adjusted = adjusted * tax_factor
        
        return adjusted.quantize(Decimal('0.01'))
    
    def is_postal_code_covered(self, postal_code: str) -> bool:
        """
        Check if postal code is covered
        
        Args:
            postal_code: Postal code to check
            
        Returns:
            True if covered
        """
        if not self.postal_codes:
            return True  # No restrictions
        
        return postal_code in self.postal_codes
    
    def get_excluded_benefits_list(self) -> List[str]:
        """Get list of excluded benefit IDs"""
        if not self.excluded_benefits:
            return []
        
        if isinstance(self.excluded_benefits, list):
            return self.excluded_benefits
        
        return self.excluded_benefits.get('benefit_ids', [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'plan_id': str(self.plan_id),
            'territory_code': self.territory_code,
            'territory_name': self.territory_name,
            'territory_type': self.territory_type,
            'is_active': self.is_active,
            'status': self.status,
            'rate_adjustment': float(self.rate_adjustment) if self.rate_adjustment else 0,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'regulatory_status': self.regulatory_status
        }
    
    def __repr__(self) -> str:
        return f"<PlanTerritory(id={self.id}, plan_id={self.plan_id}, territory={self.territory_code}, active={self.is_active})>"