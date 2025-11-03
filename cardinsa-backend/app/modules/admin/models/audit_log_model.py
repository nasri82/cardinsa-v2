"""
Audit Log Model
Tracks all system changes for compliance and debugging
"""

from __future__ import annotations
import uuid
import datetime as dt
from typing import Optional
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Audit log for tracking all system changes

    Stores who did what, when, and from where
    Essential for compliance, security audits, and debugging
    """
    __tablename__ = "audit_logs"

    # What was changed
    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of entity (policy, claim, user, etc.)"
    )

    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of the affected entity"
    )

    # What action was performed
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Action performed (create, update, delete, view, etc.)"
    )

    # Who performed it
    performed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="User who performed the action"
    )

    # What changed
    changes_made: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="JSON object with before/after values"
    )

    # Where it came from
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
        comment="IP address of the request"
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User agent string from the request"
    )

    # Additional context
    request_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Request ID for correlation"
    )

    session_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Session ID for user tracking"
    )

    # Override created_at to add index (from TimestampMixin)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="When the action occurred"
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, "
            f"entity_type='{self.entity_type}', "
            f"action='{self.action}', "
            f"performed_by={self.performed_by})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "entity_type": self.entity_type,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "action": self.action,
            "performed_by": str(self.performed_by) if self.performed_by else None,
            "changes_made": self.changes_made,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
