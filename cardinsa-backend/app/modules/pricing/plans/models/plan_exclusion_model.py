# app/modules/pricing/plans/models/plan_exclusion_model.py

"""
Plan Exclusion Model - Production Ready

Manages exclusions and limitations for insurance plans.
Handles medical, motor, and general exclusions with regulatory compliance.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, ForeignKey,
    Index, Date, UniqueConstraint, Integer, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from enum import Enum
import uuid


# ================================================================
# ENUMS
# ================================================================

class ExclusionType(str, Enum):
    """Type of exclusion"""
    MEDICAL = "medical"
    MOTOR = "motor"
    GENERAL = "general"
    DENTAL = "dental"
    VISION = "vision"
    MENTAL_HEALTH = "mental_health"
    MATERNITY = "maternity"
    SPORTS = "sports"
    TRAVEL = "travel"
    OCCUPATIONAL = "occupational"
    PRE_EXISTING = "pre_existing"
    COSMETIC = "cosmetic"
    EXPERIMENTAL = "experimental"


class ExclusionCategory(str, Enum):
    """Exclusion category"""
    CONDITION = "condition"
    PROCEDURE = "procedure"
    MEDICATION = "medication"
    PROVIDER = "provider"
    LOCATION = "location"
    CIRCUMSTANCE = "circumstance"
    TIME_BASED = "time_based"
    AGE_BASED = "age_based"
    BEHAVIORAL = "behavioral"


class ExclusionSeverity(str, Enum):
    """Severity of exclusion"""
    ABSOLUTE = "absolute"      # Never covered
    CONDITIONAL = "conditional" # Covered under specific conditions
    TEMPORARY = "temporary"     # Excluded for a period
    PARTIAL = "partial"        # Partially excluded
    WAIVERABLE = "waiverable"  # Can be waived with approval


class RegulatoryBasis(str, Enum):
    """Regulatory basis for exclusion"""
    REGULATORY_REQUIRED = "regulatory_required"
    COMPANY_POLICY = "company_policy"
    INDUSTRY_STANDARD = "industry_standard"
    RISK_MANAGEMENT = "risk_management"
    COST_CONTROL = "cost_control"


# ================================================================
# PLAN EXCLUSION MODEL
# ================================================================

class PlanExclusion(Base):
    """
    Plan Exclusion Model
    
    Defines what is not covered under a plan, with detailed
    categorization and regulatory compliance tracking.
    """
    
    __tablename__ = "plan_exclusions"
    
    __table_args__ = (
        # Indexes
        Index('idx_plan_exclusions_plan_id', 'plan_id'),
        Index('idx_plan_exclusions_type', 'exclusion_type'),
        Index('idx_plan_exclusions_category', 'exclusion_category'),
        Index('idx_plan_exclusions_severity', 'exclusion_severity'),
        Index('idx_plan_exclusions_cpt_code', 'cpt_code_id'),
        Index('idx_plan_exclusions_icd10_code', 'icd10_code_id'),
        
        # Composite indexes
        Index('idx_plan_exclusions_plan_type', 'plan_id', 'exclusion_type'),
        Index('idx_plan_exclusions_plan_category', 'plan_id', 'exclusion_category'),
        Index('idx_plan_exclusions_effective', 'plan_id', 'effective_date'),
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
    
    # Medical code references (optional)
    cpt_code_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cpt_codes.id", ondelete="SET NULL"),
        nullable=True,
        comment="CPT procedure code reference"
    )
    
    icd10_code_id = Column(
        UUID(as_uuid=True),
        ForeignKey("icd10_codes.id", ondelete="SET NULL"),
        nullable=True,
        comment="ICD-10 diagnosis code reference"
    )
    
    motor_code_id = Column(
        UUID(as_uuid=True),
        ForeignKey("motor_exclusion_codes.id", ondelete="SET NULL"),
        nullable=True,
        comment="Motor exclusion code reference"
    )
    
    # ================================================================
    # EXCLUSION DETAILS
    # ================================================================
    
    exclusion_code = Column(
        String(50),
        nullable=True,
        comment="Internal exclusion code"
    )
    
    exclusion_type = Column(
        String(50),
        nullable=False,
        default=ExclusionType.GENERAL.value,
        comment="Type of exclusion"
    )
    
    exclusion_category = Column(
        String(50),
        nullable=False,
        default=ExclusionCategory.CONDITION.value,
        comment="Category of exclusion"
    )
    
    exclusion_severity = Column(
        String(20),
        nullable=False,
        default=ExclusionSeverity.ABSOLUTE.value,
        comment="Severity level"
    )
    
    # ================================================================
    # EXCLUSION TEXT
    # ================================================================
    
    exclusion_text = Column(
        Text,
        nullable=False,
        comment="Exclusion description in English"
    )
    
    exclusion_text_ar = Column(
        Text,
        nullable=True,
        comment="Exclusion description in Arabic"
    )
    
    member_facing_text = Column(
        Text,
        nullable=True,
        comment="Simplified text for members"
    )
    
    member_facing_text_ar = Column(
        Text,
        nullable=True,
        comment="Simplified text in Arabic"
    )
    
    # ================================================================
    # CONDITIONS & EXCEPTIONS
    # ================================================================
    
    exception_conditions = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Conditions under which exclusion doesn't apply"
    )
    
    waiver_conditions = Column(
        JSONB,
        nullable=True,
        comment="Conditions for waiving exclusion"
    )
    
    alternative_coverage = Column(
        JSONB,
        nullable=True,
        comment="Alternative coverage options"
    )
    
    # ================================================================
    # DATES & PERIODS
    # ================================================================
    
    effective_date = Column(
        Date,
        nullable=True,
        comment="Exclusion effective date"
    )
    
    expiry_date = Column(
        Date,
        nullable=True,
        comment="Exclusion expiry date"
    )
    
    waiting_period_days = Column(
        Integer,
        nullable=True,
        comment="Waiting period after which exclusion lifts"
    )
    
    # ================================================================
    # GEOGRAPHIC & SCOPE
    # ================================================================
    
    geographic_scope = Column(
        JSONB,
        nullable=True,
        comment="Geographic areas where exclusion applies"
    )
    
    provider_scope = Column(
        JSONB,
        nullable=True,
        comment="Provider types/networks where exclusion applies"
    )
    
    # ================================================================
    # REGULATORY & COMPLIANCE
    # ================================================================
    
    regulatory_basis = Column(
        String(50),
        nullable=False,
        default=RegulatoryBasis.COMPANY_POLICY.value,
        comment="Basis for exclusion"
    )
    
    regulatory_reference = Column(
        String(200),
        nullable=True,
        comment="Regulatory reference/citation"
    )
    
    compliance_notes = Column(
        Text,
        nullable=True,
        comment="Compliance review notes"
    )
    
    # ================================================================
    # DISPLAY & DOCUMENTATION
    # ================================================================
    
    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Display order in documents"
    )
    
    is_highlighted = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Should be highlighted to members"
    )
    
    documentation_url = Column(
        String(500),
        nullable=True,
        comment="Link to detailed documentation"
    )
    
    # ================================================================
    # NOTES & METADATA
    # ================================================================
    
    notes = Column(
        Text,
        nullable=True,
        comment="Internal notes"
    )
    
    tags = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="Exclusion tags for categorization"
    )
    
    plan_exclusion_metadata = Column(
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
        back_populates="exclusions",
        foreign_keys=[plan_id]
    )
    
    cpt_code = relationship(
        "CPTCode",
        foreign_keys=[cpt_code_id]
    )
    
    icd10_code = relationship(
        "ICD10Code",
        foreign_keys=[icd10_code_id]
    )
    
    motor_code = relationship(
        "MotorExclusionCode",
        foreign_keys=[motor_code_id]
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('exclusion_type')
    def validate_exclusion_type(self, key, value):
        """Validate exclusion type"""
        if value not in [e.value for e in ExclusionType]:
            raise ValueError(f"Invalid exclusion type: {value}")
        return value
    
    @validates('exclusion_category')
    def validate_exclusion_category(self, key, value):
        """Validate exclusion category"""
        if value not in [e.value for e in ExclusionCategory]:
            raise ValueError(f"Invalid exclusion category: {value}")
        return value
    
    @validates('exclusion_severity')
    def validate_exclusion_severity(self, key, value):
        """Validate exclusion severity"""
        if value not in [e.value for e in ExclusionSeverity]:
            raise ValueError(f"Invalid exclusion severity: {value}")
        return value
    
    @validates('regulatory_basis')
    def validate_regulatory_basis(self, key, value):
        """Validate regulatory basis"""
        if value not in [e.value for e in RegulatoryBasis]:
            raise ValueError(f"Invalid regulatory basis: {value}")
        return value
    
    # ================================================================
    # METHODS
    # ================================================================
    
    def is_waiverable(self) -> bool:
        """Check if exclusion can be waived"""
        return self.exclusion_severity == ExclusionSeverity.WAIVERABLE.value
    
    def is_temporary(self) -> bool:
        """Check if exclusion is temporary"""
        return self.exclusion_severity == ExclusionSeverity.TEMPORARY.value or \
               self.expiry_date is not None
    
    def is_active(self, check_date: Optional[date] = None) -> bool:
        """
        Check if exclusion is active on a given date
        
        Args:
            check_date: Date to check (default: today)
            
        Returns:
            True if active
        """
        if self.archived_at:
            return False
        
        check_date = check_date or date.today()
        
        # Check effective date
        if self.effective_date and check_date < self.effective_date:
            return False
        
        # Check expiry date
        if self.expiry_date and check_date > self.expiry_date:
            return False
        
        return True
    
    def check_exception(self, context: Dict[str, Any]) -> bool:
        """
        Check if exception conditions are met
        
        Args:
            context: Context dictionary to check against
            
        Returns:
            True if exception applies (exclusion doesn't apply)
        """
        if not self.exception_conditions:
            return False
        
        for condition_key, condition_value in self.exception_conditions.items():
            if condition_key not in context:
                return False
            
            if isinstance(condition_value, list):
                if context[condition_key] not in condition_value:
                    return False
            elif context[condition_key] != condition_value:
                return False
        
        return True
    
    def get_alternative_options(self) -> List[Dict[str, Any]]:
        """Get alternative coverage options"""
        if not self.alternative_coverage:
            return []
        
        if isinstance(self.alternative_coverage, list):
            return self.alternative_coverage
        
        return self.alternative_coverage.get('options', [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'plan_id': str(self.plan_id),
            'exclusion_type': self.exclusion_type,
            'exclusion_category': self.exclusion_category,
            'exclusion_severity': self.exclusion_severity,
            'exclusion_text': self.exclusion_text,
            'regulatory_basis': self.regulatory_basis,
            'is_waiverable': self.is_waiverable(),
            'is_temporary': self.is_temporary(),
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None
        }
    
    def __repr__(self) -> str:
        return f"<PlanExclusion(id={self.id}, plan_id={self.plan_id}, type={self.exclusion_type}, severity={self.exclusion_severity})>"