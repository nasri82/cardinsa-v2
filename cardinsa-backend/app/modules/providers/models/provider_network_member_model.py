# app/modules/providers/models/provider_network_member_model.py

"""
Provider Network Member Model - SQLAlchemy Compatible
=====================================================

Clean, working implementation without any SQLAlchemy compatibility issues.
"""

from sqlalchemy import (
    Column, String, ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.core.database import Base
from app.core.mixins import AuditMixin, SoftDeleteMixin


class ProviderNetworkMember(Base, AuditMixin, SoftDeleteMixin):
    """
    Provider Network Member Model
    
    Represents the many-to-many relationship between providers and networks,
    with additional metadata about membership status and lifecycle.
    """
    
    __tablename__ = "provider_network_members"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key relationships
    provider_id = Column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    provider_network_id = Column(
        UUID(as_uuid=True),
        ForeignKey("provider_networks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Membership status
    status = Column(String(20), nullable=False, default='active', index=True)
    
    # Database constraints
    __table_args__ = (
        # Unique constraint - provider can only be active member of network once
        UniqueConstraint(
            'provider_id', 'provider_network_id', 'status',
            name='uq_provider_network_members_active'
        ),
        
        # Check constraints
        CheckConstraint(
            "status IN ('active', 'inactive', 'pending', 'suspended', 'terminated')",
            name='ck_provider_network_members_status'
        ),
        
        # Performance indexes
        Index('ix_provider_network_members_status', 'status'),
        Index('ix_provider_network_members_provider_status', 'provider_id', 'status'),
        Index('ix_provider_network_members_network_status', 'provider_network_id', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<ProviderNetworkMember(id={self.id}, provider_id={self.provider_id}, network_id={self.provider_network_id}, status='{self.status}')>"
    
    def __str__(self) -> str:
        return f"Network Membership ({self.status})"
    
    # Business methods
    def is_active(self) -> bool:
        return self.status == 'active'
    
    def is_pending(self) -> bool:
        return self.status == 'pending'
    
    def is_suspended(self) -> bool:
        return self.status == 'suspended'
    
    def is_terminated(self) -> bool:
        return self.status == 'terminated'
    
    def activate(self, updated_by: UUID = None):
        self.status = 'active'
        if updated_by:
            self.updated_by = updated_by
    
    def deactivate(self, updated_by: UUID = None):
        self.status = 'inactive'
        if updated_by:
            self.updated_by = updated_by
    
    def suspend(self, updated_by: UUID = None):
        self.status = 'suspended'
        if updated_by:
            self.updated_by = updated_by
    
    def terminate(self, updated_by: UUID = None):
        self.status = 'terminated'
        if updated_by:
            self.updated_by = updated_by
    
    def to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'provider_id': str(self.provider_id),
            'provider_network_id': str(self.provider_network_id),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProviderNetworkMember':
        return cls(
            provider_id=data['provider_id'],
            provider_network_id=data['provider_network_id'],
            status=data.get('status', 'active')
        )


# Export the model
__all__ = ['ProviderNetworkMember']