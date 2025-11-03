# app/modules/providers/models/provider_type_model.py

"""
Provider Type Model - SQLAlchemy Compatible
===========================================

Clean, working implementation without any SQLAlchemy compatibility issues.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Index,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.core.database import Base
from app.core.mixins import AuditMixin, SoftDeleteMixin


class ProviderType(Base, AuditMixin, SoftDeleteMixin):
    """
    Provider Type Model
    
    Represents categories of healthcare and insurance providers
    (hospitals, clinics, specialists, auto repair shops, etc.)
    """
    
    __tablename__ = "provider_types"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core identification fields
    code = Column(String(50), nullable=False, unique=True, index=True)
    label = Column(String(100), nullable=False, index=True)
    
    # Business fields
    description = Column(Text)
    category = Column(String(20), nullable=False, default='medical', index=True)
    icon = Column(Text)
    
    # Status and lifecycle
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Database constraints
    __table_args__ = (
        # Unique constraints
        UniqueConstraint('code', name='uq_provider_types_code'),
        
        # Check constraints for data integrity
        CheckConstraint(
            "category IN ('medical', 'motor')",
            name='ck_provider_types_category'
        ),
        CheckConstraint(
            "length(code) >= 2",
            name='ck_provider_types_code_length'
        ),
        CheckConstraint(
            "length(label) >= 2",
            name='ck_provider_types_label_length'
        ),
        
        # Performance indexes
        Index('ix_provider_types_active', 'is_active'),
        Index('ix_provider_types_category_active', 'category', 'is_active'),
        Index('ix_provider_types_code_active', 'code', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f"<ProviderType(id={self.id}, code='{self.code}', label='{self.label}')>"
    
    def __str__(self) -> str:
        return f"{self.label} ({self.category})"
    
    # Business methods
    def is_medical(self) -> bool:
        return self.category == 'medical'
    
    def is_motor(self) -> bool:
        return self.category == 'motor'
    
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
            'label': self.label,
            'description': self.description,
            'category': self.category,
            'icon': self.icon,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProviderType':
        return cls(
            code=data['code'],
            label=data['label'],
            description=data.get('description'),
            category=data.get('category', 'medical'),
            icon=data.get('icon'),
            is_active=data.get('is_active', True)
        )


# Export the model
__all__ = ['ProviderType']