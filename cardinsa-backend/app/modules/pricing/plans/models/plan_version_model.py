# app/modules/pricing/plans/models/plan_version_model.py

"""
Plan Version Model - Production Ready

Tracks version history and changes for insurance plans.
Maintains audit trail and regulatory compliance for plan modifications.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, ForeignKey,
    Index, CheckConstraint, UniqueConstraint, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


# ================================================================
# ENUMS
# ================================================================

class VersionStatus(str, Enum):
    """Version status enumeration"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ChangeType(str, Enum):
    """Type of change in version"""
    MINOR = "minor"           # Small fixes, typos
    MODERATE = "moderate"     # Benefit adjustments, pricing updates
    MAJOR = "major"          # Structural changes, coverage modifications
    CRITICAL = "critical"    # Regulatory required changes


class ApprovalStatus(str, Enum):
    """Approval status for version"""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"


# ================================================================
# PLAN VERSION MODEL
# ================================================================

class PlanVersion(Base):
    """
    Plan Version Model
    
    Maintains complete version history of plan changes.
    Tracks what changed, why, when, and by whom.
    """
    
    __tablename__ = "plan_versions"
    
    __table_args__ = (
        # Unique version number per plan
        UniqueConstraint('plan_id', 'version_number', name='uq_plan_version_number'),
        
        # Indexes
        Index('idx_plan_versions_plan_id', 'plan_id'),
        Index('idx_plan_versions_status', 'status'),
        Index('idx_plan_versions_effective_date', 'effective_date'),
        Index('idx_plan_versions_is_current', 'is_current_version'),
        
        # Composite indexes
        Index('idx_plan_versions_plan_current', 'plan_id', 'is_current_version'),
        Index('idx_plan_versions_plan_effective', 'plan_id', 'effective_date'),
        
        # Constraints
        CheckConstraint('version_number > 0', name='check_version_positive'),
        CheckConstraint('expiry_date IS NULL OR expiry_date > effective_date',
                       name='check_version_date_range'),
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
    
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created this version"
    )
    
    approved_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who approved this version"
    )
    
    # ================================================================
    # VERSION INFORMATION
    # ================================================================
    
    version_number = Column(
        Integer,
        nullable=False,
        comment="Sequential version number"
    )
    
    version_label = Column(
        String(50),
        nullable=True,
        comment="Human-readable version label (e.g., '2.1.0')"
    )
    
    version_description = Column(
        Text,
        nullable=True,
        comment="Description of this version"
    )
    
    # ================================================================
    # CHANGE TRACKING
    # ================================================================
    
    change_type = Column(
        String(20),
        nullable=False,
        default=ChangeType.MINOR.value,
        comment="Type of change"
    )
    
    changes_summary = Column(
        Text,
        nullable=True,
        comment="Summary of changes in this version"
    )
    
    changes_from_previous = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Detailed changelog from previous version"
    )
    
    created_by_reason = Column(
        Text,
        nullable=True,
        comment="Reason for creating this version"
    )
    
    # ================================================================
    # STATUS & FLAGS
    # ================================================================
    
    status = Column(
        String(50),
        nullable=False,
        default=VersionStatus.DRAFT.value,
        comment="Version status"
    )
    
    is_current_version = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Is this the current active version"
    )
    
    is_published = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Is version published/visible"
    )
    
    # ================================================================
    # DATES
    # ================================================================
    
    effective_date = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="When this version becomes effective"
    )
    
    expiry_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When this version expires"
    )
    
    approved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Approval timestamp"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    # ================================================================
    # REGULATORY & COMPLIANCE
    # ================================================================
    
    regulatory_approval_required = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Requires regulatory approval"
    )
    
    approval_status = Column(
        String(50),
        nullable=False,
        default=ApprovalStatus.NOT_REQUIRED.value,
        comment="Approval status"
    )
    
    regulatory_reference = Column(
        String(100),
        nullable=True,
        comment="Regulatory filing reference"
    )
    
    compliance_notes = Column(
        Text,
        nullable=True,
        comment="Compliance review notes"
    )
    
    # ================================================================
    # PLAN SNAPSHOT
    # ================================================================
    
    plan_snapshot = Column(
        JSONB,
        nullable=False,
        default={},
        comment="Complete snapshot of plan at this version"
    )
    
    benefits_snapshot = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Snapshot of benefits configuration"
    )
    
    pricing_snapshot = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Snapshot of pricing configuration"
    )
    
    # ================================================================
    # METADATA
    # ================================================================
    
    tags = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="Version tags for categorization"
    )
    
    version_metadata = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Additional version metadata"
    )
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    plan = relationship(
        "Plan",
        back_populates="versions",
        foreign_keys=[plan_id]
    )
    
    creator = relationship(
        "User",
        foreign_keys=[created_by],
        backref="created_plan_versions"
    )
    
    approver = relationship(
        "User",
        foreign_keys=[approved_by],
        backref="approved_plan_versions"
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('version_number')
    def validate_version_number(self, key, value):
        """Validate version number"""
        if value is not None and value < 1:
            raise ValueError("Version number must be positive")
        return value
    
    @validates('change_type')
    def validate_change_type(self, key, value):
        """Validate change type"""
        if value not in [e.value for e in ChangeType]:
            raise ValueError(f"Invalid change type: {value}")
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        """Validate version status"""
        if value not in [e.value for e in VersionStatus]:
            raise ValueError(f"Invalid version status: {value}")
        return value
    
    # ================================================================
    # METHODS
    # ================================================================
    
    def create_snapshot(self, plan_data: Dict[str, Any]) -> None:
        """
        Create a complete snapshot of the plan
        
        Args:
            plan_data: Complete plan data to snapshot
        """
        self.plan_snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'version': self.version_number,
            'data': plan_data
        }
    
    def get_changes_list(self) -> List[str]:
        """
        Get list of changes in this version
        
        Returns:
            List of change descriptions
        """
        if not self.changes_from_previous:
            return []
        
        changes = []
        for category, items in self.changes_from_previous.items():
            if isinstance(items, list):
                changes.extend(items)
            elif isinstance(items, dict):
                for field, change in items.items():
                    changes.append(f"{category}.{field}: {change}")
        
        return changes
    
    def mark_as_current(self) -> None:
        """Mark this version as current"""
        self.is_current_version = True
        self.is_published = True
        self.status = VersionStatus.APPROVED.value
    
    def supersede(self) -> None:
        """Mark this version as superseded"""
        self.is_current_version = False
        self.status = VersionStatus.SUPERSEDED.value
        self.expiry_date = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'plan_id': str(self.plan_id),
            'version_number': self.version_number,
            'version_label': self.version_label,
            'version_description': self.version_description,
            'change_type': self.change_type,
            'status': self.status,
            'is_current_version': self.is_current_version,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'changes_summary': self.changes_summary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f"<PlanVersion(id={self.id}, plan_id={self.plan_id}, version={self.version_number}, current={self.is_current_version})>"