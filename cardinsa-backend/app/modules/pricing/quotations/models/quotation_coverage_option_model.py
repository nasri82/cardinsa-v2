# app/modules/insurance/quotations/models/quotation_coverage_option_model.py

from sqlalchemy import Column, Numeric, DateTime, UUID, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class QuotationCoverageOption(Base):
    """
    Quotation Coverage Option model for tracking coverage options and pricing
    
    This model links quotations to specific coverage options and stores
    the calculated pricing for each option, enabling coverage comparison
    and option selection functionality.
    """
    __tablename__ = "quotation_coverage_options"

    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    quotation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False, index=True)
    coverage_option_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)  # References coverage_options table
    
    # Pricing information
    calculated_price = Column(Numeric(15,2), nullable=False)
    
    # Audit fields
    created_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    updated_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=True, onupdate=func.current_timestamp())
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    quotation = relationship("Quotation", back_populates="coverage_options")
    # Note: coverage_option relationship would be defined when the Coverage model is created

    def __repr__(self):
        return f"<QuotationCoverageOption(id={self.id}, quotation_id={self.quotation_id}, calculated_price={self.calculated_price})>"

    @property
    def is_archived(self) -> bool:
        """Check if the coverage option is archived"""
        return self.archived_at is not None

    @property
    def price_display(self) -> str:
        """Get formatted price for display"""
        if self.calculated_price:
            return f"{self.calculated_price:,.2f}"
        return "0.00"

    @property
    def is_premium_calculated(self) -> bool:
        """Check if premium has been calculated"""
        return self.calculated_price is not None and self.calculated_price > 0

    def update_calculated_price(self, new_price: Decimal) -> None:
        """Update the calculated price"""
        self.calculated_price = new_price

    def get_price_difference(self, base_price: Decimal) -> Decimal:
        """Get the price difference from a base price"""
        if self.calculated_price and base_price:
            return self.calculated_price - base_price
        return Decimal('0')

    def get_price_percentage_difference(self, base_price: Decimal) -> float:
        """Get the percentage difference from a base price"""
        if base_price and base_price > 0 and self.calculated_price:
            difference = self.get_price_difference(base_price)
            return float((difference / base_price) * 100)
        return 0.0

    @classmethod
    def create_coverage_option(cls, quotation_id: str, coverage_option_id: str, 
                              calculated_price: Decimal, created_by: str = None) -> 'QuotationCoverageOption':
        """
        Factory method to create a quotation coverage option
        """
        return cls(
            quotation_id=quotation_id,
            coverage_option_id=coverage_option_id,
            calculated_price=calculated_price,
            created_by=created_by
        )

    def soft_delete(self) -> None:
        """Soft delete the coverage option by setting archived_at"""
        self.archived_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted coverage option"""
        self.archived_at = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert quotation coverage option to dictionary representation"""
        return {
            'id': str(self.id),
            'quotation_id': str(self.quotation_id),
            'coverage_option_id': str(self.coverage_option_id),
            'calculated_price': float(self.calculated_price) if self.calculated_price else None,
            'price_display': self.price_display,
            'is_premium_calculated': self.is_premium_calculated,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }