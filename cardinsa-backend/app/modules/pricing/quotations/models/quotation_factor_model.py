# app/modules/insurance/quotations/models/quotation_factor_model.py

from sqlalchemy import Column, String, Text, DateTime, UUID, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any, Union
from datetime import datetime
import json


class QuotationFactor(Base):
    """
    Quotation Factor model for tracking pricing factors and their impact
    
    This model stores key-value pairs that represent various factors
    affecting the pricing of an insurance quotation, along with their
    impact descriptions for transparency and audit purposes.
    """
    __tablename__ = "quotation_factors"

    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    quotation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    
    # Factor identification
    key = Column(String(100), nullable=False, index=True)
    value = Column(Text, nullable=False)
    factor_type = Column(String(50), nullable=True, index=True)
    
    # Impact description for transparency
    impact_description = Column(Text, nullable=True)
    
    # Audit fields
    created_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    updated_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=True, onupdate=func.current_timestamp())
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    quotation = relationship("Quotation", back_populates="factors")

    def __repr__(self):
        return f"<QuotationFactor(id={self.id}, key={self.key}, value={self.value})>"

    @property
    def parsed_value(self) -> Union[str, int, float, bool, dict, list]:
        """
        Attempt to parse the value field as JSON, falling back to string
        """
        if not self.value:
            return self.value
        
        # Try to parse as JSON for complex data types
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            # Try to parse as common data types
            try:
                # Check if it's a number
                if '.' in self.value:
                    return float(self.value)
                else:
                    return int(self.value)
            except ValueError:
                # Check if it's a boolean
                if self.value.lower() in ('true', 'false'):
                    return self.value.lower() == 'true'
                # Return as string
                return self.value

    @property
    def is_numeric(self) -> bool:
        """Check if the value is numeric"""
        try:
            float(self.value)
            return True
        except (ValueError, TypeError):
            return False

    @property
    def numeric_value(self) -> Optional[float]:
        """Get numeric value if possible"""
        if self.is_numeric:
            return float(self.value)
        return None

    def set_value(self, value: Any) -> None:
        """Set value with automatic JSON serialization for complex types"""
        if isinstance(value, (dict, list)):
            self.value = json.dumps(value)
        elif isinstance(value, (int, float, bool)):
            self.value = str(value)
        else:
            self.value = str(value) if value is not None else ""

    @classmethod
    def create_factor(cls, quotation_id: str, key: str, value: Any, 
                     factor_type: str = None, impact_description: str = None) -> 'QuotationFactor':
        """
        Factory method to create a quotation factor
        """
        factor = cls(
            quotation_id=quotation_id,
            key=key,
            factor_type=factor_type,
            impact_description=impact_description
        )
        factor.set_value(value)
        return factor

    def update_impact_description(self, description: str) -> None:
        """Update the impact description"""
        self.impact_description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert quotation factor to dictionary representation"""
        return {
            'id': str(self.id),
            'quotation_id': str(self.quotation_id),
            'key': self.key,
            'value': self.value,
            'parsed_value': self.parsed_value,
            'factor_type': self.factor_type,
            'impact_description': self.impact_description,
            'is_numeric': self.is_numeric,
            'numeric_value': self.numeric_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    # Common factor types as class constants
    class FactorTypes:
        DEMOGRAPHIC = "demographic"
        RISK = "risk"
        DISCOUNT = "discount" 
        LOADING = "loading"
        GEOGRAPHIC = "geographic"
        BEHAVIORAL = "behavioral"
        PRODUCT = "product"
        REGULATORY = "regulatory"
        SEASONAL = "seasonal"
        COMPETITIVE = "competitive"