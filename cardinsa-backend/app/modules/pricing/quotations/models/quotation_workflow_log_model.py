# app/modules/insurance/quotations/models/quotation_workflow_log_model.py

from sqlalchemy import Column, Text, DateTime, UUID, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class WorkflowEventType(str, Enum):
    """Enumeration for workflow event types"""
    CREATED = "quotation_created"
    CALCULATED = "premium_calculated"
    SUBMITTED = "quotation_submitted"
    APPROVED = "quotation_approved"
    REJECTED = "quotation_rejected"
    MODIFIED = "quotation_modified"
    EXPIRED = "quotation_expired"
    CONVERTED = "quotation_converted"
    LOCKED = "quotation_locked"
    UNLOCKED = "quotation_unlocked"
    DOCUMENT_GENERATED = "document_generated"
    EMAIL_SENT = "email_sent"
    REMINDER_SENT = "reminder_sent"
    FOLLOW_UP_SCHEDULED = "follow_up_scheduled"
    CUSTOMER_VIEWED = "customer_viewed"
    AGENT_ASSIGNED = "agent_assigned"
    PRICING_UPDATED = "pricing_updated"
    COVERAGE_MODIFIED = "coverage_modified"
    VALIDATION_FAILED = "validation_failed"
    VALIDATION_PASSED = "validation_passed"


class QuotationWorkflowLog(Base):
    """
    Quotation Workflow Log model for detailed workflow event tracking
    
    This model provides granular tracking of all workflow events and
    business processes related to quotations, supporting advanced
    analytics and process optimization.
    """
    __tablename__ = "quotation_workflow_logs"

    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    quotation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=True)
    
    # Event information
    event = Column(Text, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    
    # Actor information
    created_by = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)
    
    # Timestamp (immutable for audit trail)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    quotation = relationship("Quotation", back_populates="workflow_logs")

    def __repr__(self):
        return f"<QuotationWorkflowLog(id={self.id}, event={self.event}, created_at={self.created_at})>"

    @property
    def event_category(self) -> str:
        """Get the category of the workflow event"""
        event_categories = {
            'created': 'lifecycle',
            'calculated': 'pricing',
            'submitted': 'lifecycle',
            'approved': 'approval',
            'rejected': 'approval',
            'modified': 'modification',
            'expired': 'lifecycle',
            'converted': 'lifecycle',
            'locked': 'security',
            'unlocked': 'security',
            'document': 'documentation',
            'email': 'communication',
            'reminder': 'communication',
            'follow_up': 'communication',
            'viewed': 'interaction',
            'assigned': 'assignment',
            'pricing': 'pricing',
            'coverage': 'modification',
            'validation': 'validation'
        }
        
        event_lower = self.event.lower()
        for keyword, category in event_categories.items():
            if keyword in event_lower:
                return category
        return 'general'

    @property
    def is_system_event(self) -> bool:
        """Check if this is a system-generated event"""
        system_events = [
            WorkflowEventType.EXPIRED,
            WorkflowEventType.VALIDATION_FAILED,
            WorkflowEventType.VALIDATION_PASSED,
            WorkflowEventType.REMINDER_SENT,
            WorkflowEventType.DOCUMENT_GENERATED
        ]
        return self.event in system_events

    @property
    def is_user_action(self) -> bool:
        """Check if this represents a user action"""
        return self.created_by is not None and not self.is_system_event

    @property
    def is_critical_event(self) -> bool:
        """Check if this is a critical workflow event"""
        critical_events = [
            WorkflowEventType.APPROVED,
            WorkflowEventType.REJECTED,
            WorkflowEventType.CONVERTED,
            WorkflowEventType.EXPIRED,
            WorkflowEventType.VALIDATION_FAILED
        ]
        return self.event in critical_events

    @classmethod
    def create_event_log(cls, quotation_id: str, event: str, notes: str = None, 
                        created_by: str = None) -> 'QuotationWorkflowLog':
        """
        Factory method to create a workflow event log
        """
        return cls(
            quotation_id=quotation_id,
            event=event,
            notes=notes,
            created_by=created_by
        )

    @classmethod
    def create_lifecycle_event(cls, quotation_id: str, event_type: WorkflowEventType, 
                             notes: str = None, created_by: str = None) -> 'QuotationWorkflowLog':
        """
        Factory method to create a lifecycle event log
        """
        return cls.create_event_log(quotation_id, event_type.value, notes, created_by)

    @classmethod
    def create_system_event(cls, quotation_id: str, event_type: WorkflowEventType, 
                           notes: str = None) -> 'QuotationWorkflowLog':
        """
        Factory method to create a system event log
        """
        return cls.create_event_log(quotation_id, event_type.value, notes, None)

    @classmethod
    def create_user_action(cls, quotation_id: str, event: str, user_id: str, 
                          notes: str = None) -> 'QuotationWorkflowLog':
        """
        Factory method to create a user action log
        """
        return cls.create_event_log(quotation_id, event, notes, user_id)

    def add_contextual_note(self, additional_context: str) -> None:
        """Add additional context to the notes field"""
        if self.notes:
            self.notes += f" | {additional_context}"
        else:
            self.notes = additional_context

    @classmethod
    def get_event_timeline(cls, session, quotation_id: str, limit: int = 50) -> List['QuotationWorkflowLog']:
        """
        Get the event timeline for a quotation
        """
        return session.query(cls).filter(
            cls.quotation_id == quotation_id
        ).order_by(cls.created_at.desc()).limit(limit).all()

    def to_dict(self) -> Dict[str, Any]:
        """Convert quotation workflow log to dictionary representation"""
        return {
            'id': str(self.id),
            'quotation_id': str(self.quotation_id) if self.quotation_id else None,
            'event': self.event,
            'notes': self.notes,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'event_category': self.event_category,
            'is_system_event': self.is_system_event,
            'is_user_action': self.is_user_action,
            'is_critical_event': self.is_critical_event
        }