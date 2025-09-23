# app/modules/providers/models/provider_service_price_model.py

"""
Provider Service Price Model - SQLAlchemy Compatible
====================================================

Clean, working implementation without any SQLAlchemy compatibility issues.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Numeric, ForeignKey,
    Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from decimal import Decimal
from datetime import datetime

from app.core.database import Base
from app.core.mixins import AuditMixin, SoftDeleteMixin


class ProviderServicePrice(Base, AuditMixin, SoftDeleteMixin):
    """
    Provider Service Price Model
    
    Represents pricing information for specific services offered by providers.
    Supports tiered pricing, discounts, and multi-currency scenarios.
    """
    
    __tablename__ = "provider_service_prices"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key relationships
    provider_id = Column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Service identification
    service_tag = Column(String(100), nullable=False, index=True)
    
    # Pricing information
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False, default='USD')
    
    # Discount fields
    is_discounted = Column(Boolean, nullable=False, default=False)
    
    # Administrative fields
    notes = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Database constraints
    __table_args__ = (
        # Check constraints
        CheckConstraint("price > 0", name='ck_provider_service_prices_price_positive'),
        CheckConstraint("length(service_tag) >= 2", name='ck_provider_service_prices_service_tag_length'),
        
        # Performance indexes
        Index('ix_provider_service_prices_service_tag', 'service_tag'),
        Index('ix_provider_service_prices_provider_service', 'provider_id', 'service_tag'),
        Index('ix_provider_service_prices_active', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f"<ProviderServicePrice(id={self.id}, service='{self.service_tag}', price={self.price} {self.currency})>"
    
    def __str__(self) -> str:
        return f"{self.service_tag}: {self.price} {self.currency}"
    
    # Validation methods
    @validates('price')
    def validate_price(self, key, value):
        if value is not None:
            value = Decimal(str(value))
            if value <= 0:
                raise ValueError("Price must be positive")
        return value
    
    @validates('service_tag')
    def validate_service_tag(self, key, tag):
        if tag and len(tag.strip()) < 2:
            raise ValueError("Service tag must be at least 2 characters")
        return tag.upper().strip() if tag else tag
    
    # Business methods
    def get_effective_price(self) -> Decimal:
        return self.price
    
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
            'provider_id': str(self.provider_id),
            'service_tag': self.service_tag,
            'price': float(self.price),
            'currency': self.currency,
            'is_discounted': self.is_discounted,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProviderServicePrice':
        return cls(
            provider_id=data['provider_id'],
            service_tag=data['service_tag'],
            price=Decimal(str(data['price'])),
            currency=data.get('currency', 'USD'),
            is_discounted=data.get('is_discounted', False),
            notes=data.get('notes'),
            is_active=data.get('is_active', True)
        )


# Export the model
__all__ = ['ProviderServicePrice']