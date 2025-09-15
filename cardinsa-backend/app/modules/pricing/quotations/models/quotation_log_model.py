# app/modules/insurance/quotations/models/quotation_log_model.py

from sqlalchemy import Column, String, Text, DateTime, UUID, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class QuotationStatusEnum(str, Enum):
    """Enumeration for quotation status values"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    CALCULATED = "calculated"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"
    CANCELLED = "cancelled"


class QuotationLog(Base):
    """
    Quotation Log model for tracking status changes and workflow transitions
    
    This model maintains an audit trail of all status changes and workflow
    transitions for quotations, providing complete traceability of the
    quotation lifecycle from creation to conversion or expiry.
    """
    __tablename__ = "quotation_logs"

    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    quotation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=True)
    
    # Status transition tracking
    status_from = Column(String(50), nullable=True, index=True)
    status_to = Column(String(50), nullable=True, index=True)
    
    # Actor information
    actor_id = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)
    
    # Additional notes
    notes = Column(Text, nullable=True)
    
    # Timestamp (no update timestamp needed for logs)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    # Relationships
    quotation = relationship("Quotation", back_populates="logs")

    def __repr__(self):
        return f"<QuotationLog(id={self.id}, status_from={self.status_from}, status_to={self.status_to})>"

    @property
    def transition_description(self) -> str:
        """Get a human-readable description of the status transition"""
        if self.status_from and self.status_to:
            return f"Changed from {self.status_from.replace('_', ' ').title()} to {self.status_to.replace('_', ' ').title()}"
        elif self.status_to:
            return f"Set to {self.status_to.replace('_', ' ').title()}"
        else:
            return "Status change recorded"

    @property
    def is_workflow_progression(self) -> bool:
        """Check if this represents a forward progression in the workflow"""
        workflow_order = [
            QuotationStatusEnum.DRAFT,
            QuotationStatusEnum.IN_PROGRESS,
            QuotationStatusEnum.CALCULATED,
            QuotationStatusEnum.PENDING_APPROVAL,
            QuotationStatusEnum.APPROVED,
            QuotationStatusEnum.CONVERTED
        ]
        
        try:
            from_index = workflow_order.index(self.status_from)
            to_index = workflow_order.index(self.status_to)
            return to_index > from_index
        except (ValueError, TypeError):
            return False

    @property
    def is_regression(self) -> bool:
        """Check if this represents a backward step in the workflow"""
        workflow_order = [
            QuotationStatusEnum.DRAFT,
            QuotationStatusEnum.IN_PROGRESS,
            QuotationStatusEnum.CALCULATED,
            QuotationStatusEnum.PENDING_APPROVAL,
            QuotationStatusEnum.APPROVED,
            QuotationStatusEnum.CONVERTED
        ]
        
        try:
            from_index = workflow_order.index(self.status_from)
            to_index = workflow_order.index(self.status_to)
            return to_index < from_index
        except (ValueError, TypeError):
            return False

    @property
    def is_terminal_status(self) -> bool:
        """Check if the 'status_to' is a terminal status"""
        terminal_statuses = [
            QuotationStatusEnum.CONVERTED,
            QuotationStatusEnum.EXPIRED,
            QuotationStatusEnum.CANCELLED,
            QuotationStatusEnum.REJECTED
        ]
        return self.status_to in terminal_statuses

    @classmethod
    def create_status_change_log(cls, quotation_id: str, status_from: str, status_to: str, 
                                actor_id: str = None, notes: str = None) -> 'QuotationLog':
        """
        Factory method to create a status change log entry
        """
        return cls(
            quotation_id=quotation_id,
            status_from=status_from,
            status_to=status_to,
            actor_id=actor_id,
            notes=notes
        )

    @classmethod
    def create_creation_log(cls, quotation_id: str, actor_id: str = None, notes: str = None) -> 'QuotationLog':
        """
        Factory method to create an initial creation log entry
        """
        return cls(
            quotation_id=quotation_id,
            status_from=None,
            status_to=QuotationStatusEnum.DRAFT,
            actor_id=actor_id,
            notes=notes or "Quotation created"
        )

    def add_context_note(self, additional_note: str) -> None:
        """Add additional context to the notes field"""
        if self.notes:
            self.notes += f" | {additional_note}"
        else:
            self.notes = additional_note

    def to_dict(self) -> Dict[str, Any]:
        """Convert quotation log to dictionary representation"""
        return {
            'id': str(self.id),
            'quotation_id': str(self.quotation_id) if self.quotation_id else None,
            'status_from': self.status_from,
            'status_to': self.status_to,
            'actor_id': str(self.actor_id) if self.actor_id else None,
            'notes': self.notes,
            'transition_description': self.transition_description,
            'is_workflow_progression': self.is_workflow_progression,
            'is_regression': self.is_regression,
            'is_terminal_status': self.is_terminal_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }