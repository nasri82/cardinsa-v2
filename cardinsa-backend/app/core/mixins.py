# app/core/mixins.py

"""
Core Database Mixins
====================

Reusable SQLAlchemy mixins for common database patterns:
- AuditMixin: Created/updated timestamps and user tracking
- SoftDeleteMixin: Soft delete functionality
- TimestampMixin: Basic timestamp tracking
"""

from sqlalchemy import Column, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional


class TimestampMixin:
    """
    Mixin for basic timestamp tracking
    Adds created_at and updated_at columns
    """
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when record was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Timestamp when record was last updated"
    )
    
    def touch(self):
        """Update the updated_at timestamp"""
        self.updated_at = func.now()


class AuditMixin(TimestampMixin):
    """
    Mixin for comprehensive audit tracking
    Extends TimestampMixin with user tracking
    """
    
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="User who created this record"
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="User who last updated this record"
    )
    
    # Note: Relationships to User would be defined in models that use this mixin
    # to avoid circular imports. Example:
    # created_by_user = relationship("User", foreign_keys=[created_by])
    # updated_by_user = relationship("User", foreign_keys=[updated_by])
    
    def set_audit_fields(self, user_id: UUID, is_create: bool = False):
        """Set audit fields for create or update operations"""
        if is_create:
            self.created_by = user_id
        self.updated_by = user_id


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality
    Adds archived_at column and related methods
    """
    
    archived_at = Column(
        DateTime(timezone=True),
        comment="Timestamp when record was soft deleted (archived)"
    )
    
    @property
    def is_archived(self) -> bool:
        """Check if record is soft deleted"""
        return self.archived_at is not None
    
    @property
    def is_active(self) -> bool:
        """Check if record is active (not soft deleted)"""
        return self.archived_at is None
    
    def archive(self, archived_by: Optional[UUID] = None):
        """Soft delete the record"""
        self.archived_at = func.now()
        if hasattr(self, 'updated_by') and archived_by:
            self.updated_by = archived_by
    
    def restore(self, restored_by: Optional[UUID] = None):
        """Restore soft deleted record"""
        self.archived_at = None
        if hasattr(self, 'updated_by') and restored_by:
            self.updated_by = restored_by
    
    def delete_permanently(self):
        """Mark for permanent deletion (implementation depends on your deletion strategy)"""
        # This is typically handled at the service/repository level
        # You might set a different timestamp or flag here
        pass


class FullAuditMixin(AuditMixin, SoftDeleteMixin):
    """
    Complete audit mixin combining timestamp, user tracking, and soft delete
    Use this for tables that need comprehensive audit capabilities
    """
    pass


# Utility functions for working with mixins
def is_soft_deleted(instance) -> bool:
    """Check if an instance is soft deleted (works with any object that has archived_at)"""
    return hasattr(instance, 'archived_at') and instance.archived_at is not None


def get_active_records(query):
    """Filter query to only return non-archived records"""
    return query.filter_by(archived_at=None)


def get_archived_records(query):
    """Filter query to only return archived records"""
    return query.filter(query.model_class.archived_at.isnot(None))

# Alias for backward compatibility
ArchiveMixin = SoftDeleteMixin

# Export the mixins
__all__ = [
    'TimestampMixin',
    'AuditMixin', 
    'SoftDeleteMixin',
    'FullAuditMixin',
    'ArchiveMixin',
    'is_soft_deleted',
    'get_active_records',
    'get_archived_records'
]
