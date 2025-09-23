# =============================================================================
# FILE: app/modules/underwriting/models/underwriting_application_model.py
# WORLD-CLASS UNDERWRITING APPLICATION MODEL - ENTERPRISE GRADE
# =============================================================================

"""
Underwriting Application Model - Enterprise Implementation

Comprehensive application management system supporting:
- End-to-end application lifecycle
- Multi-channel submission handling
- Advanced workflow management
- SLA tracking and escalation
- Integration with pricing and policy systems
"""

from sqlalchemy import Column, String, Text, Integer, Numeric, Boolean, DateTime, Date, JSON, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime, date, timedelta
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

class ApplicationStatus(str, BaseEnum):
    """Application processing status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    PENDING_INFO = "pending_info"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class SubmissionChannel(str, BaseEnum):
    """Channel through which application was submitted"""
    ONLINE = "online"
    AGENT = "agent"
    BROKER = "broker"
    PHONE = "phone"
    EMAIL = "email"
    MAIL = "mail"
    WALK_IN = "walk_in"
    PARTNER = "partner"
    API = "api"


class Priority(str, BaseEnum):
    """Application priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class ApplicationSource(str, BaseEnum):
    """Source of the application"""
    DIRECT = "direct"
    REFERRAL = "referral"
    RENEWAL = "renewal"
    CONVERSION = "conversion"
    CROSS_SELL = "cross_sell"
    UP_SELL = "up_sell"
    CAMPAIGN = "campaign"
    PARTNER = "partner"


# =============================================================================
# UNDERWRITING APPLICATION MODEL
# =============================================================================

class UnderwritingApplication(Base, TimestampMixin, ArchiveMixin):
    """
    Enterprise Underwriting Application Model
    
    Comprehensive application management supporting:
    - Multi-channel application processing
    - Advanced workflow and SLA management
    - Integration with pricing and underwriting
    - Document management and tracking
    - Automated routing and assignment
    """
    
    __tablename__ = 'underwriting_applications'
    
    # =========================================================================
    # PRIMARY FIELDS
    # =========================================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Application Identification
    application_number = Column(String(30), nullable=False, unique=True, index=True)
    reference_number = Column(String(50), nullable=True, index=True)
    external_reference = Column(String(100), nullable=True, index=True)
    
    # Application Associations
    member_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    policy_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    quote_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_profiles.id'), nullable=True, index=True)
    
    # Product and Coverage
    product_type = Column(String(50), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    plan_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    coverage_amount = Column(Numeric(15,2), nullable=True)
    
    # Application Data
    application_data = Column(JSONB, nullable=False)  # Complete application information
    applicant_data = Column(JSONB, nullable=True)  # Primary applicant details
    beneficiary_data = Column(JSONB, nullable=True)  # Beneficiary information
    medical_data = Column(JSONB, nullable=True)  # Medical information
    financial_data = Column(JSONB, nullable=True)  # Financial information
    risk_data = Column(JSONB, nullable=True)  # Risk assessment data
    
    # Submission Details
    submission_channel = Column(String(30), nullable=True, index=True)
    source = Column(String(50), nullable=True, index=True)
    channel = Column(String(50), nullable=True, index=True)
    submitted_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    submitted_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Status and Processing
    status = Column(String(30), default=ApplicationStatus.SUBMITTED, nullable=False, index=True)
    priority = Column(String(20), default=Priority.NORMAL, nullable=False, index=True)
    
    # Assignment and Workflow
    assigned_underwriter = Column(UUID(as_uuid=True), nullable=True, index=True)
    assigned_to = Column(UUID(as_uuid=True), nullable=True, index=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    team_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    department_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # SLA and Timing
    sla_due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    target_completion_date = Column(DateTime(timezone=True), nullable=True)
    actual_completion_date = Column(DateTime(timezone=True), nullable=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    
    # Decision Information
    decision_at = Column(DateTime(timezone=True), nullable=True)
    decision_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    decision_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Premium and Pricing
    estimated_premium = Column(Numeric(10,2), nullable=True)
    quoted_premium = Column(Numeric(10,2), nullable=True)
    final_premium = Column(Numeric(10,2), nullable=True)
    premium_score = Column(Numeric(5,2), nullable=True)
    pricing_model_used = Column(String(100), nullable=True)
    
    # Notes and Communication
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    customer_notes = Column(Text, nullable=True)
    underwriter_notes = Column(Text, nullable=True)
    
    # Quality and Compliance
    quality_score = Column(Numeric(5,2), nullable=True)
    compliance_checked = Column(Boolean, default=False, nullable=False)
    compliance_checked_at = Column(DateTime(timezone=True), nullable=True)
    compliance_checked_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Tracking Fields
    created_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    # Related underwriting components
    profile = relationship("UnderwritingProfile", backref="applications")
    decisions = relationship("UnderwritingDecision", foreign_keys="UnderwritingDecision.application_id", cascade="all, delete-orphan")
    documents = relationship("UnderwritingDocument", foreign_keys="UnderwritingDocument.application_id", cascade="all, delete-orphan")
    logs = relationship("UnderwritingLog", foreign_keys="UnderwritingLog.application_id", cascade="all, delete-orphan")
    
    # Communication and follow-ups
    communications = relationship("ApplicationCommunication", back_populates="application", cascade="all, delete-orphan")
    follow_ups = relationship("ApplicationFollowUp", back_populates="application", cascade="all, delete-orphan")
    
    # Parent-child relationships for related applications
    parent_application_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_applications.id'), nullable=True)
    child_applications = relationship("UnderwritingApplication", backref="parent_application", remote_side=[id])
    
    # =========================================================================
    # CONSTRAINTS AND INDEXES
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            status.in_(['draft', 'submitted', 'received', 'in_progress', 'pending_info', 'under_review', 
                       'approved', 'rejected', 'deferred', 'cancelled', 'expired', 'withdrawn']),
            name='ck_underwriting_application_status'
        ),
        CheckConstraint(
            submission_channel.in_(['online', 'agent', 'broker', 'phone', 'email', 'mail', 'walk_in', 'partner', 'api']),
            name='ck_underwriting_application_submission_channel'
        ),
        CheckConstraint(
            priority.in_(['low', 'normal', 'high', 'urgent', 'critical']),
            name='ck_underwriting_application_priority'
        ),
        CheckConstraint(
            source.in_(['direct', 'referral', 'renewal', 'conversion', 'cross_sell', 'up_sell', 'campaign', 'partner']),
            name='ck_underwriting_application_source'
        ),
        CheckConstraint(
            'coverage_amount >= 0',
            name='ck_underwriting_application_coverage_amount_positive'
        ),
        CheckConstraint(
            'estimated_premium >= 0',
            name='ck_underwriting_application_estimated_premium_positive'
        ),
        CheckConstraint(
            'quoted_premium >= 0',
            name='ck_underwriting_application_quoted_premium_positive'
        ),
        CheckConstraint(
            'final_premium >= 0',
            name='ck_underwriting_application_final_premium_positive'
        ),
        CheckConstraint(
            'quality_score >= 0 AND quality_score <= 10',
            name='ck_underwriting_application_quality_score_range'
        ),
        CheckConstraint(
            'premium_score >= 0 AND premium_score <= 100',
            name='ck_underwriting_application_premium_score_range'
        ),
        CheckConstraint(
            'submitted_at <= COALESCE(processing_started_at, submitted_at)',
            name='ck_underwriting_application_processing_after_submission'
        ),
        CheckConstraint(
            'processing_started_at <= COALESCE(actual_completion_date, processing_started_at)',
            name='ck_underwriting_application_completion_after_processing'
        ),
        
        # Performance indexes
        Index('ix_underwriting_applications_status_priority', 'status', 'priority'),
        Index('ix_underwriting_applications_assigned_sla', 'assigned_to', 'sla_due_date'),
        Index('ix_underwriting_applications_product_status', 'product_type', 'status'),
        Index('ix_underwriting_applications_channel_source', 'submission_channel', 'source'),
        Index('ix_underwriting_applications_member_policy', 'member_id', 'policy_id'),
        Index('ix_underwriting_applications_dates', 'submitted_at', 'sla_due_date'),
        Index('ix_underwriting_applications_processing_dates', 'processing_started_at', 'actual_completion_date'),
        
        # Unique constraints
        Index('ix_underwriting_applications_application_number_unique', 'application_number', unique=True),
    )
    
    # =========================================================================
    # VALIDATION METHODS
    # =========================================================================
    
    @validates('application_number')
    def validate_application_number(self, key, value):
        """Validate application number format"""
        if not value or not value.strip():
            raise ValueError("Application number is required")
        
        if len(value) > 30:
            raise ValueError("Application number cannot exceed 30 characters")
        
        return value.strip().upper()
    
    @validates('product_type')
    def validate_product_type(self, key, value):
        """Validate product type"""
        if not value or not value.strip():
            raise ValueError("Product type is required")
        
        valid_types = ['medical', 'motor', 'life', 'property', 'travel', 'general', 'disability', 'critical_illness']
        if value.lower() not in valid_types:
            raise ValueError(f"Product type must be one of: {', '.join(valid_types)}")
        
        return value.lower()
    
    @validates('application_data')
    def validate_application_data(self, key, value):
        """Validate application data structure"""
        if not isinstance(value, dict):
            raise ValueError("Application data must be a valid JSON object")
        
        # Ensure required fields exist
        required_fields = ['applicant_info', 'contact_info']
        for field in required_fields:
            if field not in value:
                raise ValueError(f"Application data must contain '{field}' section")
        
        return value
    
    @validates('coverage_amount', 'estimated_premium', 'quoted_premium', 'final_premium')
    def validate_monetary_amounts(self, key, value):
        """Validate monetary amounts"""
        if value is not None and value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value
    
    @validates('quality_score')
    def validate_quality_score(self, key, value):
        """Validate quality score range"""
        if value is not None and (value < 0 or value > 10):
            raise ValueError("Quality score must be between 0 and 10")
        return value
    
    @validates('premium_score')
    def validate_premium_score(self, key, value):
        """Validate premium score range"""
        if value is not None and (value < 0 or value > 100):
            raise ValueError("Premium score must be between 0 and 100")
        return value
    
    # =========================================================================
    # BUSINESS LOGIC METHODS
    # =========================================================================
    
    def generate_application_number(self) -> str:
        """Generate unique application number"""
        from datetime import datetime
        import random
        import string
        
        # Format: YYYYMMDD-PRODUCT-RANDOM
        date_part = datetime.now().strftime('%Y%m%d')
        product_part = self.product_type[:3].upper() if self.product_type else 'GEN'
        random_part = ''.join(random.choices(string.digits, k=6))
        
        return f"{date_part}-{product_part}-{random_part}"
    
    def is_overdue(self) -> bool:
        """Check if application is overdue"""
        if not self.sla_due_date or self.status in [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED, ApplicationStatus.CANCELLED]:
            return False
        
        return datetime.now() > self.sla_due_date
    
    def is_high_priority(self) -> bool:
        """Check if application is high priority"""
        return self.priority in [Priority.HIGH, Priority.URGENT, Priority.CRITICAL]
    
    def get_processing_duration(self) -> Optional[int]:
        """Get processing duration in hours"""
        if not self.processing_started_at:
            return None
        
        end_time = self.actual_completion_date or datetime.now()
        duration = end_time - self.processing_started_at
        return int(duration.total_seconds() / 3600)
    
    def get_time_to_assignment(self) -> Optional[int]:
        """Get time from submission to assignment in hours"""
        if not self.assigned_at:
            return None
        
        duration = self.assigned_at - self.submitted_at
        return int(duration.total_seconds() / 3600)
    
    def get_sla_status(self) -> Dict[str, Any]:
        """Get SLA performance status"""
        if not self.sla_due_date:
            return {'status': 'no_sla', 'message': 'No SLA defined'}
        
        now = datetime.now()
        
        if self.actual_completion_date:
            # Completed application
            if self.actual_completion_date <= self.sla_due_date:
                early_hours = int((self.sla_due_date - self.actual_completion_date).total_seconds() / 3600)
                return {
                    'status': 'met',
                    'message': 'SLA met',
                    'early_hours': early_hours if early_hours > 0 else 0
                }
            else:
                late_hours = int((self.actual_completion_date - self.sla_due_date).total_seconds() / 3600)
                return {
                    'status': 'missed',
                    'message': 'SLA missed',
                    'late_hours': late_hours
                }
        else:
            # In progress application
            if now <= self.sla_due_date:
                remaining_hours = int((self.sla_due_date - now).total_seconds() / 3600)
                return {
                    'status': 'on_track',
                    'message': 'On track to meet SLA',
                    'remaining_hours': remaining_hours
                }
            else:
                overdue_hours = int((now - self.sla_due_date).total_seconds() / 3600)
                return {
                    'status': 'overdue',
                    'message': 'SLA overdue',
                    'overdue_hours': overdue_hours
                }
    
    def assign_to_underwriter(self, underwriter_id: UUID, assigned_by: UUID) -> None:
        """Assign application to underwriter"""
        self.assigned_underwriter = underwriter_id
        self.assigned_to = underwriter_id
        self.assigned_at = datetime.now()
        self.updated_by = assigned_by
        
        if self.status == ApplicationStatus.SUBMITTED:
            self.status = ApplicationStatus.IN_PROGRESS
            self.processing_started_at = datetime.now()
    
    def start_processing(self, processor_id: UUID) -> None:
        """Start processing the application"""
        if self.status not in [ApplicationStatus.SUBMITTED, ApplicationStatus.RECEIVED]:
            raise ValueError(f"Cannot start processing application in status: {self.status}")
        
        self.status = ApplicationStatus.IN_PROGRESS
        self.processing_started_at = datetime.now()
        self.updated_by = processor_id
        
        if not self.assigned_to:
            self.assign_to_underwriter(processor_id, processor_id)
    
    def complete_application(self, decision: str, decision_by: UUID, notes: Optional[str] = None) -> None:
        """Complete the application with a decision"""
        valid_decisions = [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED, ApplicationStatus.DEFERRED]
        if decision not in valid_decisions:
            raise ValueError(f"Invalid decision: {decision}. Must be one of: {valid_decisions}")
        
        self.status = decision
        self.decision_at = datetime.now()
        self.decision_by = decision_by
        self.actual_completion_date = datetime.now()
        self.updated_by = decision_by
        
        if notes:
            self.decision_notes = notes
    
    def approve_application(self, approved_by: UUID, notes: Optional[str] = None) -> None:
        """Approve the application"""
        self.complete_application(ApplicationStatus.APPROVED, approved_by, notes)
    
    def reject_application(self, rejected_by: UUID, reason: str) -> None:
        """Reject the application"""
        self.complete_application(ApplicationStatus.REJECTED, rejected_by)
        self.rejection_reason = reason
    
    def defer_application(self, deferred_by: UUID, reason: str) -> None:
        """Defer the application"""
        self.complete_application(ApplicationStatus.DEFERRED, deferred_by, reason)
    
    def request_additional_info(self, requested_by: UUID, info_needed: str) -> None:
        """Request additional information"""
        self.status = ApplicationStatus.PENDING_INFO
        self.updated_by = requested_by
        
        if self.internal_notes:
            self.internal_notes += f"\n\nAdditional info requested: {info_needed}"
        else:
            self.internal_notes = f"Additional info requested: {info_needed}"
    
    def escalate_application(self, escalated_by: UUID, reason: str) -> None:
        """Escalate application to higher priority"""
        if self.priority == Priority.CRITICAL:
            raise ValueError("Application is already at highest priority")
        
        # Upgrade priority
        priority_levels = [Priority.LOW, Priority.NORMAL, Priority.HIGH, Priority.URGENT, Priority.CRITICAL]
        current_index = priority_levels.index(self.priority)
        if current_index < len(priority_levels) - 1:
            self.priority = priority_levels[current_index + 1]
        
        self.updated_by = escalated_by
        
        escalation_note = f"Escalated to {self.priority} priority: {reason}"
        if self.internal_notes:
            self.internal_notes += f"\n\n{escalation_note}"
        else:
            self.internal_notes = escalation_note
    
    def set_sla_due_date(self, hours: int = 72) -> None:
        """Set SLA due date based on priority and product type"""
        if self.priority == Priority.CRITICAL:
            hours = 4
        elif self.priority == Priority.URGENT:
            hours = 12
        elif self.priority == Priority.HIGH:
            hours = 24
        elif self.priority == Priority.NORMAL:
            hours = 72
        else:  # LOW
            hours = 168  # 1 week
        
        # Adjust for product complexity
        if self.product_type in ['life', 'disability', 'critical_illness']:
            hours *= 2  # Complex products need more time
        
        self.sla_due_date = self.submitted_at + timedelta(hours=hours)
    
    def calculate_quality_score(self) -> float:
        """Calculate application quality score"""
        score = 10.0
        
        # Deduct points for missing or incomplete information
        if not self.application_data:
            score -= 5.0
        else:
            required_sections = ['applicant_info', 'contact_info', 'coverage_details']
            missing_sections = [section for section in required_sections if section not in self.application_data]
            score -= len(missing_sections) * 1.5
        
        # Deduct points for missing financial information for high coverage
        if self.coverage_amount and self.coverage_amount > 100000 and not self.financial_data:
            score -= 2.0
        
        # Deduct points for missing medical information for life/health products
        if self.product_type in ['medical', 'life', 'disability', 'critical_illness'] and not self.medical_data:
            score -= 2.0
        
        # Bonus for complete documentation
        if self.documents and len(self.documents) > 0:
            score += 0.5
        
        self.quality_score = max(0.0, min(10.0, score))
        return self.quality_score
    
    def get_missing_requirements(self) -> List[str]:
        """Get list of missing requirements"""
        missing = []
        
        if not self.application_data:
            missing.append("Complete application data")
        
        if self.coverage_amount and self.coverage_amount > 100000 and not self.financial_data:
            missing.append("Financial information for high coverage amount")
        
        if self.product_type in ['medical', 'life', 'disability', 'critical_illness'] and not self.medical_data:
            missing.append("Medical information")
        
        if self.product_type == 'motor' and not self.application_data.get('vehicle_info'):
            missing.append("Vehicle information")
        
        if not self.compliance_checked:
            missing.append("Compliance verification")
        
        return missing
    
    def is_complete(self) -> bool:
        """Check if application is complete and ready for processing"""
        return len(self.get_missing_requirements()) == 0
    
    def clone_application(self, new_applicant_data: Dict[str, Any], created_by: UUID) -> 'UnderwritingApplication':
        """Create a copy of this application for a different applicant"""
        new_app_data = self.application_data.copy()
        new_app_data['applicant_info'] = new_applicant_data
        
        new_application = UnderwritingApplication(
            application_number=self.generate_application_number(),
            product_type=self.product_type,
            product_id=self.product_id,
            plan_id=self.plan_id,
            coverage_amount=self.coverage_amount,
            application_data=new_app_data,
            submission_channel=self.submission_channel,
            source=ApplicationSource.REFERRAL,
            priority=self.priority,
            created_by=created_by,
            parent_application_id=self.id
        )
        
        return new_application
    
    # =========================================================================
    # ANALYTICS AND REPORTING
    # =========================================================================
    
    def get_application_summary(self) -> Dict[str, Any]:
        """Get comprehensive application summary"""
        return {
            'id': str(self.id),
            'application_number': self.application_number,
            'product_info': {
                'product_type': self.product_type,
                'coverage_amount': float(self.coverage_amount) if self.coverage_amount else None,
                'product_id': str(self.product_id) if self.product_id else None,
                'plan_id': str(self.plan_id) if self.plan_id else None
            },
            'status_info': {
                'status': self.status,
                'priority': self.priority,
                'is_overdue': self.is_overdue(),
                'is_high_priority': self.is_high_priority(),
                'sla_status': self.get_sla_status()
            },
            'assignment_info': {
                'assigned_to': str(self.assigned_to) if self.assigned_to else None,
                'assigned_underwriter': str(self.assigned_underwriter) if self.assigned_underwriter else None,
                'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
                'time_to_assignment_hours': self.get_time_to_assignment()
            },
            'timing_info': {
                'submitted_at': self.submitted_at.isoformat(),
                'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
                'actual_completion_date': self.actual_completion_date.isoformat() if self.actual_completion_date else None,
                'sla_due_date': self.sla_due_date.isoformat() if self.sla_due_date else None,
                'processing_duration_hours': self.get_processing_duration()
            },
            'submission_info': {
                'submission_channel': self.submission_channel,
                'source': self.source,
                'submitted_by': str(self.submitted_by) if self.submitted_by else None
            },
            'quality_info': {
                'quality_score': float(self.quality_score) if self.quality_score else None,
                'is_complete': self.is_complete(),
                'missing_requirements': self.get_missing_requirements(),
                'compliance_checked': self.compliance_checked
            },
            'premium_info': {
                'estimated_premium': float(self.estimated_premium) if self.estimated_premium else None,
                'quoted_premium': float(self.quoted_premium) if self.quoted_premium else None,
                'final_premium': float(self.final_premium) if self.final_premium else None,
                'premium_score': float(self.premium_score) if self.premium_score else None
            },
            'decision_info': {
                'decision_at': self.decision_at.isoformat() if self.decision_at else None,
                'decision_by': str(self.decision_by) if self.decision_by else None,
                'decision_notes': self.decision_notes,
                'rejection_reason': self.rejection_reason
            }
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this application"""
        metrics = {}
        
        # Processing efficiency
        if self.processing_started_at and self.actual_completion_date:
            duration = self.actual_completion_date - self.processing_started_at
            metrics['processing_time_hours'] = int(duration.total_seconds() / 3600)
        
        # Assignment efficiency
        if self.assigned_at:
            assignment_time = self.assigned_at - self.submitted_at
            metrics['time_to_assignment_hours'] = int(assignment_time.total_seconds() / 3600)
        
        # SLA performance
        sla_status = self.get_sla_status()
        metrics['sla_status'] = sla_status['status']
        if 'early_hours' in sla_status:
            metrics['sla_early_hours'] = sla_status['early_hours']
        elif 'late_hours' in sla_status:
            metrics['sla_late_hours'] = sla_status['late_hours']
        
        # Quality metrics
        metrics['quality_score'] = float(self.quality_score) if self.quality_score else None
        metrics['is_complete'] = self.is_complete()
        metrics['missing_requirements_count'] = len(self.get_missing_requirements())
        
        # Activity metrics
        metrics['documents_count'] = len(self.documents) if self.documents else 0
        metrics['communications_count'] = len(self.communications) if self.communications else 0
        metrics['follow_ups_count'] = len(self.follow_ups) if self.follow_ups else 0
        metrics['logs_count'] = len(self.logs) if self.logs else 0
        
        return metrics
    
    # =========================================================================
    # SERIALIZATION METHODS
    # =========================================================================
    
    def to_dict(self, include_relationships: bool = False, include_sensitive: bool = True) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = {
            'id': str(self.id),
            'application_number': self.application_number,
            'reference_number': self.reference_number,
            'external_reference': self.external_reference,
            
            'member_id': str(self.member_id) if self.member_id else None,
            'policy_id': str(self.policy_id) if self.policy_id else None,
            'quote_id': str(self.quote_id) if self.quote_id else None,
            'profile_id': str(self.profile_id) if self.profile_id else None,
            
            'product_type': self.product_type,
            'product_id': str(self.product_id) if self.product_id else None,
            'plan_id': str(self.plan_id) if self.plan_id else None,
            'coverage_amount': float(self.coverage_amount) if self.coverage_amount else None,
            
            'submission_channel': self.submission_channel,
            'source': self.source,
            'channel': self.channel,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'submitted_by': str(self.submitted_by) if self.submitted_by else None,
            
            'status': self.status,
            'priority': self.priority,
            
            'assigned_underwriter': str(self.assigned_underwriter) if self.assigned_underwriter else None,
            'assigned_to': str(self.assigned_to) if self.assigned_to else None,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'team_id': str(self.team_id) if self.team_id else None,
            'department_id': str(self.department_id) if self.department_id else None,
            
            'sla_due_date': self.sla_due_date.isoformat() if self.sla_due_date else None,
            'target_completion_date': self.target_completion_date.isoformat() if self.target_completion_date else None,
            'actual_completion_date': self.actual_completion_date.isoformat() if self.actual_completion_date else None,
            'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
            
            'decision_at': self.decision_at.isoformat() if self.decision_at else None,
            'decision_by': str(self.decision_by) if self.decision_by else None,
            
            'estimated_premium': float(self.estimated_premium) if self.estimated_premium else None,
            'quoted_premium': float(self.quoted_premium) if self.quoted_premium else None,
            'final_premium': float(self.final_premium) if self.final_premium else None,
            'premium_score': float(self.premium_score) if self.premium_score else None,
            'pricing_model_used': self.pricing_model_used,
            
            'quality_score': float(self.quality_score) if self.quality_score else None,
            'compliance_checked': self.compliance_checked,
            'compliance_checked_at': self.compliance_checked_at.isoformat() if self.compliance_checked_at else None,
            'compliance_checked_by': str(self.compliance_checked_by) if self.compliance_checked_by else None,
            
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            
            # Computed fields
            'is_overdue': self.is_overdue(),
            'is_high_priority': self.is_high_priority(),
            'is_complete': self.is_complete(),
            'processing_duration_hours': self.get_processing_duration(),
            'time_to_assignment_hours': self.get_time_to_assignment(),
            'sla_status': self.get_sla_status(),
            'missing_requirements': self.get_missing_requirements()
        }
        
        if include_sensitive:
            base_dict.update({
                'application_data': self.application_data,
                'applicant_data': self.applicant_data,
                'beneficiary_data': self.beneficiary_data,
                'medical_data': self.medical_data,
                'financial_data': self.financial_data,
                'risk_data': self.risk_data,
                'notes': self.notes,
                'internal_notes': self.internal_notes,
                'customer_notes': self.customer_notes,
                'underwriter_notes': self.underwriter_notes,
                'decision_notes': self.decision_notes,
                'rejection_reason': self.rejection_reason
            })
        
        if include_relationships:
            base_dict.update({
                'decisions_count': len(self.decisions) if self.decisions else 0,
                'documents_count': len(self.documents) if self.documents else 0,
                'logs_count': len(self.logs) if self.logs else 0,
                'communications_count': len(self.communications) if self.communications else 0,
                'follow_ups_count': len(self.follow_ups) if self.follow_ups else 0,
                'child_applications_count': len(self.child_applications) if self.child_applications else 0,
                'parent_application_id': str(self.parent_application_id) if self.parent_application_id else None
            })
        
        return base_dict
    
    def __repr__(self) -> str:
        return f"<UnderwritingApplication(id='{self.id}', number='{self.application_number}', status='{self.status}', product='{self.product_type}')>"
    
    def __str__(self) -> str:
        return f"Application {self.application_number} - {self.status.title()} ({self.product_type})"


# =============================================================================
# SUPPORTING MODELS
# =============================================================================

class ApplicationCommunication(Base, TimestampMixin):
    """Communication history for applications"""
    
    __tablename__ = 'application_communications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_applications.id'), nullable=False, index=True)
    
    communication_type = Column(String(30), nullable=False, index=True)  # email, phone, sms, letter
    direction = Column(String(10), nullable=False)  # inbound, outbound
    subject = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)
    
    from_address = Column(String(200), nullable=True)
    to_address = Column(String(200), nullable=True)
    
    sent_at = Column(DateTime(timezone=True), nullable=True)
    sent_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    received_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    application = relationship("UnderwritingApplication", back_populates="communications")


class ApplicationFollowUp(Base, TimestampMixin):
    """Follow-up tasks and reminders for applications"""
    
    __tablename__ = 'application_follow_ups'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_applications.id'), nullable=False, index=True)
    
    follow_up_type = Column(String(30), nullable=False, index=True)  # reminder, escalation, review
    description = Column(Text, nullable=False)
    priority = Column(String(10), default='normal', nullable=False)
    
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    assigned_to = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completed_by = Column(UUID(as_uuid=True), nullable=True)
    completion_notes = Column(Text, nullable=True)
    
    created_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Relationships
    application = relationship("UnderwritingApplication", back_populates="follow_ups")