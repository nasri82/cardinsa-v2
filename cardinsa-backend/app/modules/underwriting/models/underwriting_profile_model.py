# =============================================================================
# FILE: app/modules/underwriting/models/underwriting_profile_model.py
# WORLD-CLASS UNDERWRITING PROFILE MODEL - ENTERPRISE GRADE
# =============================================================================

"""
Underwriting Profile Model - Enterprise Implementation

Comprehensive risk assessment and profile management system supporting:
- Multi-dimensional risk scoring
- Dynamic profile evaluation
- Historical tracking and analysis
- Integration with pricing and policy systems
- Advanced workflow management
"""

from sqlalchemy import Column, String, Text, Integer, Numeric, Boolean, DateTime, Date, JSON, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any, List, Union
from enum import Enum
import json

from app.core.database import Base
from app.core.mixins import TimestampMixin, ArchiveMixin
from app.core.enums import BaseEnum


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class ProfileDecision(str, BaseEnum):
    """Profile decision outcomes"""
    APPROVED = "approved"
    REFERRED = "referred"
    REJECTED = "rejected"
    PENDING = "pending"
    CONDITIONAL = "conditional"
    DEFERRED = "deferred"
    DECLINED = "declined"


class RiskLevel(str, BaseEnum):
    """Risk level classification"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    UNACCEPTABLE = "unacceptable"


class ProfileStatus(str, BaseEnum):
    """Profile processing status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class EvaluationMethod(str, BaseEnum):
    """Method of evaluation"""
    AUTOMATED = "automated"
    MANUAL = "manual"
    HYBRID = "hybrid"
    EXCEPTION = "exception"


# =============================================================================
# UNDERWRITING PROFILE MODEL
# =============================================================================

class UnderwritingProfile(Base, TimestampMixin, ArchiveMixin):
    """
    Enterprise Underwriting Profile Model
    
    Comprehensive risk profile management supporting:
    - Multi-dimensional risk assessment
    - Dynamic scoring and evaluation
    - Workflow integration and tracking
    - Historical analysis and trends
    - Integration with policies and quotes
    """
    
    __tablename__ = 'underwriting_profiles'
    
    # =========================================================================
    # PRIMARY FIELDS
    # =========================================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Profile Associations
    member_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    policy_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    plan_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    quote_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    application_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Risk Assessment
    risk_score = Column(Numeric(5,2), nullable=True, index=True)
    risk_level = Column(String(20), nullable=True, index=True)
    base_risk_score = Column(Numeric(5,2), nullable=True)
    adjusted_risk_score = Column(Numeric(5,2), nullable=True)
    
    # Decision and Status
    decision = Column(String(20), nullable=True, index=True)
    status = Column(String(20), default=ProfileStatus.DRAFT, nullable=False, index=True)
    evaluation_method = Column(String(20), default=EvaluationMethod.AUTOMATED, nullable=False)
    
    # Profile Details
    profile_data = Column(JSONB, nullable=True)  # Comprehensive profile information
    risk_factors = Column(JSONB, nullable=True)  # Identified risk factors
    mitigation_factors = Column(JSONB, nullable=True)  # Factors that reduce risk
    exclusions = Column(JSONB, nullable=True)  # Coverage exclusions
    conditions = Column(JSONB, nullable=True)  # Special conditions
    
    # Premium Impact
    premium_loading = Column(Numeric(5,2), default=0, nullable=False)
    premium_discount = Column(Numeric(5,2), default=0, nullable=False)
    net_premium_adjustment = Column(Numeric(5,2), default=0, nullable=False)
    
    # Coverage Modifications
    coverage_limits = Column(JSONB, nullable=True)
    waiting_periods = Column(JSONB, nullable=True)
    deductible_adjustments = Column(JSONB, nullable=True)
    
    # Notes and Documentation
    notes = Column(Text, nullable=True)
    underwriter_notes = Column(Text, nullable=True)
    medical_notes = Column(Text, nullable=True)
    financial_notes = Column(Text, nullable=True)
    
    # Workflow Management
    assigned_to = Column(UUID(as_uuid=True), nullable=True, index=True)
    priority = Column(Integer, default=5, nullable=False)
    sla_due_date = Column(DateTime(timezone=True), nullable=True)
    evaluation_started_at = Column(DateTime(timezone=True), nullable=True)
    evaluation_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Tracking
    created_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    evaluated_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    # Related actions and documents
    actions = relationship("UnderwritingAction", back_populates="profile", cascade="all, delete-orphan")
    documents = relationship("UnderwritingDocument", back_populates="profile", cascade="all, delete-orphan")
    logs = relationship("UnderwritingLog", back_populates="profile", cascade="all, delete-orphan")
    
    # Decision history
    decisions = relationship("UnderwritingDecision", foreign_keys="UnderwritingDecision.profile_id", cascade="all, delete-orphan")
    
    # Related profiles (for comparison, family members, etc.)
    parent_profile_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_profiles.id'), nullable=True)
    child_profiles = relationship("UnderwritingProfile", backref="parent_profile", remote_side=[id])
    
    # =========================================================================
    # CONSTRAINTS AND INDEXES
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            decision.in_(['approved', 'referred', 'rejected', 'pending', 'conditional', 'deferred', 'declined']),
            name='ck_underwriting_profile_decision'
        ),
        CheckConstraint(
            status.in_(['draft', 'submitted', 'in_progress', 'review', 'completed', 'cancelled', 'expired']),
            name='ck_underwriting_profile_status'
        ),
        CheckConstraint(
            evaluation_method.in_(['automated', 'manual', 'hybrid', 'exception']),
            name='ck_underwriting_profile_evaluation_method'
        ),
        CheckConstraint(
            risk_level.in_(['very_low', 'low', 'moderate', 'high', 'very_high', 'unacceptable']),
            name='ck_underwriting_profile_risk_level'
        ),
        CheckConstraint(
            'risk_score >= 0 AND risk_score <= 100',
            name='ck_underwriting_profile_risk_score_range'
        ),
        CheckConstraint(
            'base_risk_score >= 0 AND base_risk_score <= 100',
            name='ck_underwriting_profile_base_risk_score_range'
        ),
        CheckConstraint(
            'adjusted_risk_score >= 0 AND adjusted_risk_score <= 100',
            name='ck_underwriting_profile_adjusted_risk_score_range'
        ),
        CheckConstraint(
            'premium_loading >= -100 AND premium_loading <= 500',
            name='ck_underwriting_profile_premium_loading_range'
        ),
        CheckConstraint(
            'premium_discount >= 0 AND premium_discount <= 100',
            name='ck_underwriting_profile_premium_discount_range'
        ),
        CheckConstraint(
            'priority >= 1 AND priority <= 10',
            name='ck_underwriting_profile_priority_range'
        ),
        CheckConstraint(
            'evaluation_started_at <= COALESCE(evaluation_completed_at, evaluation_started_at)',
            name='ck_underwriting_profile_evaluation_dates'
        ),
        
        # Performance indexes
        Index('ix_underwriting_profiles_member_policy', 'member_id', 'policy_id'),
        Index('ix_underwriting_profiles_risk_decision', 'risk_score', 'decision'),
        Index('ix_underwriting_profiles_status_priority', 'status', 'priority'),
        Index('ix_underwriting_profiles_assigned_sla', 'assigned_to', 'sla_due_date'),
        Index('ix_underwriting_profiles_evaluation_dates', 'evaluation_started_at', 'evaluation_completed_at'),
        Index('ix_underwriting_profiles_quote_plan', 'quote_id', 'plan_id'),
    )
    
    # =========================================================================
    # VALIDATION METHODS
    # =========================================================================
    
    @validates('risk_score', 'base_risk_score', 'adjusted_risk_score')
    def validate_risk_scores(self, key, value):
        """Validate risk score range"""
        if value is not None and (value < 0 or value > 100):
            raise ValueError(f"{key} must be between 0 and 100")
        return value
    
    @validates('premium_loading')
    def validate_premium_loading(self, key, value):
        """Validate premium loading range"""
        if value is not None and (value < -100 or value > 500):
            raise ValueError("Premium loading must be between -100% and 500%")
        return value
    
    @validates('premium_discount')
    def validate_premium_discount(self, key, value):
        """Validate premium discount range"""
        if value is not None and (value < 0 or value > 100):
            raise ValueError("Premium discount must be between 0% and 100%")
        return value
    
    @validates('priority')
    def validate_priority(self, key, value):
        """Validate priority range"""
        if value is not None and (value < 1 or value > 10):
            raise ValueError("Priority must be between 1 and 10")
        return value
    
    @validates('profile_data', 'risk_factors', 'mitigation_factors', 'exclusions', 'conditions')
    def validate_json_fields(self, key, value):
        """Validate JSON structure"""
        if value is not None and not isinstance(value, dict):
            raise ValueError(f"{key} must be a valid JSON object")
        return value
    
    # =========================================================================
    # BUSINESS LOGIC METHODS
    # =========================================================================
    
    def calculate_risk_level(self) -> str:
        """Calculate risk level based on score"""
        if not self.risk_score:
            return RiskLevel.MODERATE
        
        score = float(self.risk_score)
        
        if score < 20:
            return RiskLevel.VERY_LOW
        elif score < 40:
            return RiskLevel.LOW
        elif score < 60:
            return RiskLevel.MODERATE
        elif score < 80:
            return RiskLevel.HIGH
        elif score < 95:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.UNACCEPTABLE
    
    def calculate_net_premium_adjustment(self) -> Decimal:
        """Calculate net premium adjustment"""
        loading = Decimal(str(self.premium_loading or 0))
        discount = Decimal(str(self.premium_discount or 0))
        
        # Net adjustment = loading - discount
        net_adjustment = loading - discount
        self.net_premium_adjustment = net_adjustment
        
        return net_adjustment
    
    def get_evaluation_duration(self) -> Optional[int]:
        """Get evaluation duration in minutes"""
        if not self.evaluation_started_at or not self.evaluation_completed_at:
            return None
        
        duration = self.evaluation_completed_at - self.evaluation_started_at
        return int(duration.total_seconds() / 60)
    
    def is_overdue(self) -> bool:
        """Check if profile is overdue"""
        if not self.sla_due_date:
            return False
        
        return datetime.now() > self.sla_due_date and self.status not in [ProfileStatus.COMPLETED, ProfileStatus.CANCELLED]
    
    def is_high_priority(self) -> bool:
        """Check if profile is high priority"""
        return self.priority <= 3 or self.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.UNACCEPTABLE]
    
    def get_risk_factors_summary(self) -> List[str]:
        """Get summary of risk factors"""
        if not self.risk_factors:
            return []
        
        factors = []
        for category, items in self.risk_factors.items():
            if isinstance(items, list):
                factors.extend([f"{category}: {item}" for item in items])
            elif isinstance(items, dict):
                factors.extend([f"{category}: {key}" for key in items.keys()])
            else:
                factors.append(f"{category}: {items}")
        
        return factors
    
    def get_coverage_modifications_summary(self) -> Dict[str, Any]:
        """Get summary of coverage modifications"""
        modifications = {}
        
        if self.coverage_limits:
            modifications['limits'] = self.coverage_limits
        
        if self.waiting_periods:
            modifications['waiting_periods'] = self.waiting_periods
        
        if self.deductible_adjustments:
            modifications['deductibles'] = self.deductible_adjustments
        
        if self.exclusions:
            modifications['exclusions'] = self.exclusions
        
        return modifications
    
    def add_risk_factor(self, category: str, factor: str, impact: Optional[float] = None) -> None:
        """Add a risk factor"""
        if not self.risk_factors:
            self.risk_factors = {}
        
        if category not in self.risk_factors:
            self.risk_factors[category] = []
        
        factor_data = {
            'factor': factor,
            'impact': impact,
            'added_at': datetime.now().isoformat()
        }
        
        self.risk_factors[category].append(factor_data)
    
    def add_mitigation_factor(self, category: str, factor: str, benefit: Optional[float] = None) -> None:
        """Add a mitigation factor"""
        if not self.mitigation_factors:
            self.mitigation_factors = {}
        
        if category not in self.mitigation_factors:
            self.mitigation_factors[category] = []
        
        factor_data = {
            'factor': factor,
            'benefit': benefit,
            'added_at': datetime.now().isoformat()
        }
        
        self.mitigation_factors[category].append(factor_data)
    
    def start_evaluation(self, evaluator_id: UUID) -> None:
        """Start the evaluation process"""
        self.status = ProfileStatus.IN_PROGRESS
        self.evaluation_started_at = datetime.now()
        self.assigned_to = evaluator_id
        self.updated_by = evaluator_id
    
    def complete_evaluation(self, decision: str, evaluator_id: UUID, notes: Optional[str] = None) -> None:
        """Complete the evaluation process"""
        self.status = ProfileStatus.COMPLETED
        self.decision = decision
        self.evaluation_completed_at = datetime.now()
        self.evaluated_by = evaluator_id
        self.updated_by = evaluator_id
        
        if notes:
            if self.underwriter_notes:
                self.underwriter_notes += f"\n\nFinal Decision Notes: {notes}"
            else:
                self.underwriter_notes = f"Final Decision Notes: {notes}"
        
        # Auto-calculate risk level and net premium adjustment
        self.risk_level = self.calculate_risk_level()
        self.calculate_net_premium_adjustment()
    
    def reject_profile(self, reason: str, evaluator_id: UUID) -> None:
        """Reject the profile"""
        self.complete_evaluation(ProfileDecision.REJECTED, evaluator_id, reason)
    
    def approve_profile(self, evaluator_id: UUID, conditions: Optional[Dict] = None) -> None:
        """Approve the profile"""
        decision = ProfileDecision.CONDITIONAL if conditions else ProfileDecision.APPROVED
        
        if conditions:
            if not self.conditions:
                self.conditions = {}
            self.conditions.update(conditions)
        
        self.complete_evaluation(decision, evaluator_id)
    
    def refer_for_manual_review(self, reason: str, evaluator_id: UUID) -> None:
        """Refer profile for manual review"""
        self.status = ProfileStatus.REVIEW
        self.decision = ProfileDecision.REFERRED
        self.evaluation_method = EvaluationMethod.MANUAL
        self.updated_by = evaluator_id
        
        if self.underwriter_notes:
            self.underwriter_notes += f"\n\nReferred for manual review: {reason}"
        else:
            self.underwriter_notes = f"Referred for manual review: {reason}"
    
    # =========================================================================
    # ANALYTICS AND REPORTING
    # =========================================================================
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get comprehensive profile summary"""
        return {
            'id': str(self.id),
            'risk_assessment': {
                'risk_score': float(self.risk_score) if self.risk_score else None,
                'risk_level': self.risk_level,
                'base_score': float(self.base_risk_score) if self.base_risk_score else None,
                'adjusted_score': float(self.adjusted_risk_score) if self.adjusted_risk_score else None
            },
            'decision_info': {
                'decision': self.decision,
                'status': self.status,
                'evaluation_method': self.evaluation_method,
                'evaluation_duration_minutes': self.get_evaluation_duration()
            },
            'premium_impact': {
                'loading': float(self.premium_loading) if self.premium_loading else 0,
                'discount': float(self.premium_discount) if self.premium_discount else 0,
                'net_adjustment': float(self.net_premium_adjustment) if self.net_premium_adjustment else 0
            },
            'workflow_info': {
                'priority': self.priority,
                'assigned_to': str(self.assigned_to) if self.assigned_to else None,
                'is_overdue': self.is_overdue(),
                'is_high_priority': self.is_high_priority(),
                'sla_due_date': self.sla_due_date.isoformat() if self.sla_due_date else None
            },
            'associations': {
                'member_id': str(self.member_id) if self.member_id else None,
                'policy_id': str(self.policy_id) if self.policy_id else None,
                'quote_id': str(self.quote_id) if self.quote_id else None,
                'plan_id': str(self.plan_id) if self.plan_id else None
            },
            'risk_factors': self.get_risk_factors_summary(),
            'coverage_modifications': self.get_coverage_modifications_summary(),
            'timestamps': {
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'evaluation_started': self.evaluation_started_at.isoformat() if self.evaluation_started_at else None,
                'evaluation_completed': self.evaluation_completed_at.isoformat() if self.evaluation_completed_at else None
            }
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this profile"""
        metrics = {}
        
        # Processing efficiency
        if self.evaluation_started_at and self.evaluation_completed_at:
            duration = self.evaluation_completed_at - self.evaluation_started_at
            metrics['processing_time_minutes'] = int(duration.total_seconds() / 60)
        
        # SLA performance
        if self.sla_due_date:
            if self.evaluation_completed_at:
                if self.evaluation_completed_at <= self.sla_due_date:
                    metrics['sla_met'] = True
                    early_minutes = int((self.sla_due_date - self.evaluation_completed_at).total_seconds() / 60)
                    metrics['sla_early_minutes'] = early_minutes if early_minutes > 0 else 0
                else:
                    metrics['sla_met'] = False
                    late_minutes = int((self.evaluation_completed_at - self.sla_due_date).total_seconds() / 60)
                    metrics['sla_late_minutes'] = late_minutes
            else:
                metrics['sla_met'] = not self.is_overdue()
        
        # Activity metrics
        metrics['actions_count'] = len(self.actions) if self.actions else 0
        metrics['documents_count'] = len(self.documents) if self.documents else 0
        metrics['log_entries_count'] = len(self.logs) if self.logs else 0
        
        return metrics
    
    # =========================================================================
    # SERIALIZATION METHODS
    # =========================================================================
    
    def to_dict(self, include_relationships: bool = False, include_sensitive: bool = True) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = {
            'id': str(self.id),
            'member_id': str(self.member_id) if self.member_id else None,
            'policy_id': str(self.policy_id) if self.policy_id else None,
            'plan_id': str(self.plan_id) if self.plan_id else None,
            'quote_id': str(self.quote_id) if self.quote_id else None,
            'application_id': str(self.application_id) if self.application_id else None,
            
            'risk_score': float(self.risk_score) if self.risk_score else None,
            'risk_level': self.risk_level,
            'base_risk_score': float(self.base_risk_score) if self.base_risk_score else None,
            'adjusted_risk_score': float(self.adjusted_risk_score) if self.adjusted_risk_score else None,
            
            'decision': self.decision,
            'status': self.status,
            'evaluation_method': self.evaluation_method,
            
            'premium_loading': float(self.premium_loading) if self.premium_loading else None,
            'premium_discount': float(self.premium_discount) if self.premium_discount else None,
            'net_premium_adjustment': float(self.net_premium_adjustment) if self.net_premium_adjustment else None,
            
            'priority': self.priority,
            'assigned_to': str(self.assigned_to) if self.assigned_to else None,
            'sla_due_date': self.sla_due_date.isoformat() if self.sla_due_date else None,
            
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'evaluation_started_at': self.evaluation_started_at.isoformat() if self.evaluation_started_at else None,
            'evaluation_completed_at': self.evaluation_completed_at.isoformat() if self.evaluation_completed_at else None,
            
            # Computed fields
            'is_overdue': self.is_overdue(),
            'is_high_priority': self.is_high_priority(),
            'evaluation_duration_minutes': self.get_evaluation_duration()
        }
        
        if include_sensitive:
            base_dict.update({
                'profile_data': self.profile_data,
                'risk_factors': self.risk_factors,
                'mitigation_factors': self.mitigation_factors,
                'exclusions': self.exclusions,
                'conditions': self.conditions,
                'coverage_limits': self.coverage_limits,
                'waiting_periods': self.waiting_periods,
                'deductible_adjustments': self.deductible_adjustments,
                'notes': self.notes,
                'underwriter_notes': self.underwriter_notes,
                'medical_notes': self.medical_notes,
                'financial_notes': self.financial_notes
            })
        
        if include_relationships:
            base_dict.update({
                'actions_count': len(self.actions) if self.actions else 0,
                'documents_count': len(self.documents) if self.documents else 0,
                'logs_count': len(self.logs) if self.logs else 0,
                'decisions_count': len(self.decisions) if self.decisions else 0,
                'child_profiles_count': len(self.child_profiles) if self.child_profiles else 0,
                'parent_profile_id': str(self.parent_profile_id) if self.parent_profile_id else None
            })
        
        return base_dict
    
    def __repr__(self) -> str:
        return f"<UnderwritingProfile(id='{self.id}', member='{self.member_id}', decision='{self.decision}', risk_score={self.risk_score})>"
    
    def __str__(self) -> str:
        return f"Profile {str(self.id)[:8]} - {self.decision or 'Pending'} (Risk: {self.risk_score or 'N/A'})"


# =============================================================================
# SUPPORTING MODELS
# =============================================================================

class UnderwritingAction(Base, TimestampMixin, ArchiveMixin):
    """Actions taken on underwriting profiles"""
    
    __tablename__ = 'underwriting_actions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_profiles.id'), nullable=True, index=True)
    
    action_type = Column(String(20), nullable=False, index=True)
    taken_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    taken_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    profile = relationship("UnderwritingProfile", back_populates="actions")
    
    __table_args__ = (
        CheckConstraint(
            action_type.in_(['approve', 'refer', 'reject', 'escalate', 'request_info', 'defer']),
            name='ck_underwriting_action_type'
        ),
    )


class UnderwritingDocument(Base, TimestampMixin, ArchiveMixin):
    """Documents associated with underwriting profiles"""
    
    __tablename__ = 'underwriting_documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_profiles.id'), nullable=True, index=True)
    
    document_type = Column(String(50), nullable=False, index=True)
    file_url = Column(String(500), nullable=True)
    file_name = Column(String(200), nullable=True)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)
    
    uploaded_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    uploaded_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    profile = relationship("UnderwritingProfile", back_populates="documents")


class UnderwritingLog(Base, TimestampMixin):
    """Comprehensive logging for underwriting activities"""
    
    __tablename__ = 'underwriting_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_profiles.id'), nullable=True, index=True)
    application_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    action = Column(String(50), nullable=False, index=True)
    log_type = Column(String(30), nullable=True, index=True)
    log_data = Column(JSONB, nullable=True)
    
    performed_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    profile = relationship("UnderwritingProfile", back_populates="logs")