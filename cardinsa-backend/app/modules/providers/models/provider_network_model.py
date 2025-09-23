# app/modules/providers/models/provider_network_model.py

"""
Provider Network Model - SQLAlchemy Compatible
==============================================

Clean, working implementation without any SQLAlchemy compatibility issues.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, ForeignKey,
    Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base
from app.core.mixins import AuditMixin, SoftDeleteMixin


class ProviderNetwork(Base, AuditMixin, SoftDeleteMixin):
    """
    Provider Network Model
    
    Represents networks of healthcare providers or auto repair shops
    that insurance companies contract with for services.
    """
    
    __tablename__ = "provider_networks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Network identification
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Network categorization
    type = Column(String(20), nullable=False, default='medical', index=True)
    
    # Company association for multi-tenancy
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Operational status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Database constraints
    __table_args__ = (
        # Unique constraints
        UniqueConstraint('code', 'company_id', name='uq_provider_networks_code_company'),
        UniqueConstraint('name', 'company_id', name='uq_provider_networks_name_company'),
        
        # Check constraints
        CheckConstraint(
            "type IN ('medical', 'motor')",
            name='ck_provider_networks_type'
        ),
        CheckConstraint(
            "length(code) >= 2",
            name='ck_provider_networks_code_length'
        ),
        CheckConstraint(
            "length(name) >= 2",
            name='ck_provider_networks_name_length'
        ),
        
        # Performance indexes
        Index('ix_provider_networks_active', 'is_active'),
        Index('ix_provider_networks_type_active', 'type', 'is_active'),
        Index('ix_provider_networks_company_active', 'company_id', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f"<ProviderNetwork(id={self.id}, code='{self.code}', name='{self.name}')>"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.type.title()})"
    
    # Business methods
    def is_medical(self) -> bool:
        return self.type == 'medical'
    
    def is_motor(self) -> bool:
        return self.type == 'motor'
    
    def deactivate(self, updated_by: UUID = None):
        self.is_active = False
        if updated_by:
            self.updated_by = updated_by
    
    def activate(self, updated_by: UUID = None):
        self.is_active = True
        if updated_by:
            self.updated_by = updated_by
    
    def to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'company_id': str(self.company_id),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProviderNetwork':
        return cls(
            code=data['code'],
            name=data['name'],
            description=data.get('description'),
            type=data.get('type', 'medical'),
            company_id=data['company_id'],
            is_active=data.get('is_active', True)
        )


# Export the model
__all__ = ['ProviderNetwork']