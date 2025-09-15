# app/modules/insurance/quotations/models/quotation_item_model.py

from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime, UUID, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class QuotationItem(Base):
    """
    Quotation Item model representing individual coverage items in a quote
    
    This model handles individual coverage line items within a quotation,
    supporting multilingual content (English and Arabic) and flexible
    coverage configurations with metadata support.
    """
    __tablename__ = "quotation_items"

    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    quotation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=True)
    
    # Coverage information (multilingual)
    coverage_name = Column(Text, nullable=True)
    coverage_name_ar = Column(Text, nullable=True, comment="Arabic coverage name")
    
    # Coverage limits and amounts
    limit_amount = Column(Numeric(12,2), nullable=True)
    
    # Notes and descriptions (multilingual)
    notes = Column(Text, nullable=True)
    notes_ar = Column(Text, nullable=True, comment="Arabic notes")
    
    # Display configuration
    display_order = Column(Integer, nullable=False, default=0)
    
    # Flexible metadata storage
    meta_data = Column(JSONB, nullable=True, default=text("'{}'::jsonb"))
    
    # Audit fields
    created_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    updated_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=True, onupdate=func.current_timestamp())
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    quotation = relationship("Quotation", back_populates="items")

    def __repr__(self):
        return f"<QuotationItem(id={self.id}, coverage_name={self.coverage_name}, limit_amount={self.limit_amount})>"

    @property
    def coverage_display_name(self) -> str:
        """Get the coverage name, preferring English over Arabic"""
        return self.coverage_name or self.coverage_name_ar or "Unnamed Coverage"
    
    @property
    def notes_display(self) -> str:
        """Get the notes, preferring English over Arabic"""
        return self.notes or self.notes_ar or ""
    
    def get_localized_coverage_name(self, language: str = 'en') -> str:
        """Get coverage name in specified language"""
        if language.lower() == 'ar' and self.coverage_name_ar:
            return self.coverage_name_ar
        return self.coverage_name or self.coverage_name_ar or "Unnamed Coverage"
    
    def get_localized_notes(self, language: str = 'en') -> str:
        """Get notes in specified language"""
        if language.lower() == 'ar' and self.notes_ar:
            return self.notes_ar
        return self.notes or self.notes_ar or ""
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update a specific metadata field"""
        if self.meta_data is None:
            self.meta_data = {}
        self.meta_data[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a specific metadata field"""
        if self.meta_data is None:
            return default
        return self.meta_data.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quotation item to dictionary representation"""
        return {
            'id': str(self.id),
            'quotation_id': str(self.quotation_id) if self.quotation_id else None,
            'coverage_name': self.coverage_name,
            'coverage_name_ar': self.coverage_name_ar,
            'limit_amount': float(self.limit_amount) if self.limit_amount else None,
            'notes': self.notes,
            'notes_ar': self.notes_ar,
            'display_order': self.display_order,
            'meta_data': self.meta_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }