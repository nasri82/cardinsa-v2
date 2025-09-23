# app/modules/pricing/plans/models/plan_exclusion_link_model.py

"""
Plan Exclusion Link Model - Production Ready

Links plans to predefined exclusions from the exclusion library.
Allows sharing of common exclusions across multiple plans.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, ForeignKey,
    Index, UniqueConstraint, Date, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import date, datetime
from enum import Enum
import uuid


# ================================================================
# ENUMS
# ================================================================

class LinkStatus(str, Enum):
    """Link status"""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class ApplicationScope(str, Enum):
    """Scope of exclusion application"""
    GLOBAL = "global"              # Applies to all coverages
    SPECIFIC = "specific"          # Applies to specific coverages
    CONDITIONAL = "conditional"    # Applies based on conditions


class OverrideType(str, Enum):
    """Type of override on standard exclusion"""
    NONE = "none"                 # Use standard exclusion as-is
    EXTENDED = "extended"          # Extended/additional restrictions
    REDUCED = "reduced"           # Reduced restrictions
    CUSTOMIZED = "customized"     # Completely customized


# ================================================================
# PLAN EXCLUSION LINK MODEL
# ================================================================

class PlanExclusionLink(Base):
    """
    Plan Exclusion Link Model
    
    Creates relationships between plans and standard exclusions,
    allowing for reuse of common exclusions with plan-specific overrides.
    """
    
    __tablename__ = "plan_exclusion_links"
    
    __table_args__ = (
        # Unique exclusion per plan
        UniqueConstraint('plan_id', 'exclusion_id', name='uq_plan_exclusion'),
        
        # Indexes
        Index('idx_plan_exclusion_links_plan_id', 'plan_id'),
        Index('idx_plan_exclusion_links_exclusion_id', 'exclusion_id'),
        Index('idx_plan_exclusion_links_status', 'status'),
        Index('idx_plan_exclusion_links_scope', 'application_scope'),
        
        # Composite indexes
        Index('idx_plan_exclusion_links_plan_active', 'plan_id', 'is_active'),
        Index('idx_plan_exclusion_links_effective', 'plan_id', 'effective_date'),
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
        comment="Reference to plan"
    )
    
    exclusion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exclusion_library.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to exclusion in library"
    )
    
    # ================================================================
    # LINK CONFIGURATION
    # ================================================================
    
    status = Column(
        String(20),
        nullable=False,
        default=LinkStatus.ACTIVE.value,
        comment="Link status"
    )
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Is link currently active"
    )
    
    is_mandatory = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Is this a mandatory exclusion (regulatory required)"
    )
    
    # ================================================================
    # APPLICATION SCOPE
    # ================================================================
    
    application_scope = Column(
        String(20),
        nullable=False,
        default=ApplicationScope.GLOBAL.value,
        comment="Scope of exclusion application"
    )
    
    applicable_coverages = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="List of coverage IDs if scope is specific"
    )
    
    applicable_conditions = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Conditions for applying exclusion"
    )
    
    # ================================================================
    # OVERRIDES
    # ================================================================
    
    override_type = Column(
        String(20),
        nullable=False,
        default=OverrideType.NONE.value,
        comment="Type of override applied"
    )
    
    override_text = Column(
        Text,
        nullable=True,
        comment="Override exclusion text"
    )
    
    override_text_ar = Column(
        Text,
        nullable=True,
        comment="Override text in Arabic"
    )
    
    override_parameters = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Override parameters (limits, periods, etc.)"
    )
    
    # ================================================================
    # DATES
    # ================================================================
    
    effective_date = Column(
        Date,
        nullable=True,
        comment="When exclusion becomes effective"
    )
    
    expiry_date = Column(
        Date,
        nullable=True,
        comment="When exclusion expires"
    )
    
    # ================================================================
    # DISPLAY & DOCUMENTATION
    # ================================================================
    
    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Display order in plan documents"
    )
    
    display_category = Column(
        String(100),
        nullable=True,
        comment="Category for grouping in display"
    )
    
    is_highlighted = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Should be highlighted to members"
    )
    
    # ================================================================
    # NOTES & METADATA
    # ================================================================
    
    notes = Column(
        Text,
        nullable=True,
        comment="Internal notes about this link"
    )
    
    reason_for_inclusion = Column(
        Text,
        nullable=True,
        comment="Reason why this exclusion is included"
    )
    
    excl_link_metadata = Column(
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
        back_populates="exclusion_links",
        foreign_keys=[plan_id]
    )
    
    exclusion = relationship(
        "ExclusionLibrary",
        back_populates="plan_links",
        foreign_keys=[exclusion_id]
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('status')
    def validate_status(self, key, value):
        """Validate link status"""
        if value not in [e.value for e in LinkStatus]:
            raise ValueError(f"Invalid link status: {value}")
        return value
    
    @validates('application_scope')
    def validate_application_scope(self, key, value):
        """Validate application scope"""
        if value not in [e.value for e in ApplicationScope]:
            raise ValueError(f"Invalid application scope: {value}")
        return value
    
    @validates('override_type')
    def validate_override_type(self, key, value):
        """Validate override type"""
        if value not in [e.value for e in OverrideType]:
            raise ValueError(f"Invalid override type: {value}")
        return value
    
    # ================================================================
    # METHODS
    # ================================================================
    
    def is_effective(self, check_date: Optional[date] = None) -> bool:
        """
        Check if exclusion link is effective on a given date
        
        Args:
            check_date: Date to check (default: today)
            
        Returns:
            True if effective
        """
        if not self.is_active:
            return False
        
        check_date = check_date or date.today()
        
        # Check effective date
        if self.effective_date and check_date < self.effective_date:
            return False
        
        # Check expiry date
        if self.expiry_date and check_date > self.expiry_date:
            return False
        
        return True
    
    def applies_to_coverage(self, coverage_id: str) -> bool:
        """
        Check if exclusion applies to a specific coverage
        
        Args:
            coverage_id: Coverage ID to check
            
        Returns:
            True if applies
        """
        if self.application_scope == ApplicationScope.GLOBAL.value:
            return True
        
        if self.application_scope == ApplicationScope.SPECIFIC.value:
            return coverage_id in (self.applicable_coverages or [])
        
        # For conditional scope, would need to evaluate conditions
        return False
    
    def get_effective_text(self, language: str = 'en') -> str:
        """
        Get effective exclusion text considering overrides
        
        Args:
            language: Language code ('en' or 'ar')
            
        Returns:
            Effective exclusion text
        """
        if self.override_type != OverrideType.NONE.value:
            if language == 'ar' and self.override_text_ar:
                return self.override_text_ar
            elif self.override_text:
                return self.override_text
        
        # Would need to get from related exclusion object
        return ""
    
    def get_override_parameters(self) -> Dict[str, Any]:
        """Get override parameters"""
        return self.override_parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'plan_id': str(self.plan_id),
            'exclusion_id': str(self.exclusion_id),
            'status': self.status,
            'is_active': self.is_active,
            'is_mandatory': self.is_mandatory,
            'application_scope': self.application_scope,
            'override_type': self.override_type,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'display_order': self.display_order
        }
    
    def __repr__(self) -> str:
        return f"<PlanExclusionLink(id={self.id}, plan_id={self.plan_id}, exclusion_id={self.exclusion_id}, active={self.is_active})>"