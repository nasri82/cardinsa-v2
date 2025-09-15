# app/modules/pricing/profiles/models/quotation_pricing_rule_model.py

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, DateTime, Integer,
    ForeignKey, CheckConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class QuotationPricingRule(Base):
    """
    Model for quotation pricing rules.
    Represents business rules used in premium calculations.
    """
    
    __tablename__ = "quotation_pricing_rules"
    
    # Primary key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    
    # Basic rule information
    insurance_type = Column(String(50), nullable=False, index=True)
    rule_name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Premium boundaries
    base_premium = Column(Numeric(15, 2), nullable=True)
    min_premium = Column(Numeric(15, 2), nullable=True)
    max_premium = Column(Numeric(15, 2), nullable=True)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Rule conditions
    applies_to = Column(String(50), nullable=True)
    comparison_operator = Column(String(10), nullable=True)
    value = Column(Text, nullable=True)
    
    # Rule actions
    adjustment_type = Column(String(20), nullable=True)
    adjustment_value = Column(Numeric(15, 4), nullable=True)
    formula_expression = Column(Text, nullable=True)
    formula_variables = Column(JSON, nullable=True)
    
    # Rule metadata
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    effective_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)
    priority = Column(Integer, nullable=False, default=0, index=True)
    version = Column(Integer, nullable=False, default=1)
    rule_type = Column(String(50), nullable=True, index=True)
    
    # Related entities
    copayment_id = Column(PG_UUID(as_uuid=True), nullable=True)
    deductible_id = Column(PG_UUID(as_uuid=True), nullable=True)
    discount_id = Column(PG_UUID(as_uuid=True), nullable=True)
    commission_id = Column(PG_UUID(as_uuid=True), nullable=True)
    
    # Audit fields
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "adjustment_type IN ('PERCENTAGE', 'FIXED_AMOUNT', 'MULTIPLIER', 'FORMULA')",
            name="valid_adjustment_type"
        ),
        CheckConstraint(
            "comparison_operator IN ('=', '!=', '>', '>=', '<', '<=', 'IN', 'NOT IN', 'BETWEEN')",
            name="valid_comparison_operator"
        ),
        CheckConstraint(
            "currency_code ~ '^[A-Z]{3}$'",
            name="valid_currency_code"
        ),
        CheckConstraint(
            "(effective_to IS NULL) OR (effective_from < effective_to)",
            name="valid_effective_range"
        ),
    )
    
    def __repr__(self):
        return f"<QuotationPricingRule(id={self.id}, name='{self.rule_name}', type='{self.rule_type}')>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the rule has expired."""
        if self.effective_to is None:
            return False
        return datetime.utcnow() > self.effective_to
    
    @property
    def is_effective(self) -> bool:
        """Check if the rule is currently effective."""
        now = datetime.utcnow()
        if now < self.effective_from:
            return False
        if self.effective_to and now > self.effective_to:
            return False
        return self.is_active and self.archived_at is None
    
    @property
    def days_until_effective(self) -> Optional[int]:
        """Get days until the rule becomes effective."""
        if self.effective_from <= datetime.utcnow():
            return None
        delta = self.effective_from - datetime.utcnow()
        return delta.days
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Get days until the rule expires."""
        if not self.effective_to:
            return None
        if self.effective_to <= datetime.utcnow():
            return 0
        delta = self.effective_to - datetime.utcnow()
        return delta.days
    
    def can_apply_to_insurance_type(self, insurance_type: str) -> bool:
        """Check if rule can apply to a specific insurance type."""
        return self.insurance_type.upper() == insurance_type.upper()
    
    def get_adjustment_description(self) -> str:
        """Get human-readable description of the adjustment."""
        if not self.adjustment_type or not self.adjustment_value:
            return "No adjustment"
        
        if self.adjustment_type == "PERCENTAGE":
            return f"{self.adjustment_value}% adjustment"
        elif self.adjustment_type == "FIXED_AMOUNT":
            return f"{self.currency_code} {self.adjustment_value} fixed adjustment"
        elif self.adjustment_type == "MULTIPLIER":
            return f"{self.adjustment_value}x multiplier"
        elif self.adjustment_type == "FORMULA":
            return f"Formula: {self.formula_expression}"
        else:
            return f"{self.adjustment_type}: {self.adjustment_value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the rule to a dictionary."""
        return {
            'id': str(self.id),
            'insurance_type': self.insurance_type,
            'rule_name': self.rule_name,
            'description': self.description,
            'base_premium': float(self.base_premium) if self.base_premium else None,
            'min_premium': float(self.min_premium) if self.min_premium else None,
            'max_premium': float(self.max_premium) if self.max_premium else None,
            'currency_code': self.currency_code,
            'applies_to': self.applies_to,
            'comparison_operator': self.comparison_operator,
            'value': self.value,
            'adjustment_type': self.adjustment_type,
            'adjustment_value': float(self.adjustment_value) if self.adjustment_value else None,
            'formula_expression': self.formula_expression,
            'formula_variables': self.formula_variables,
            'is_active': self.is_active,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'priority': self.priority,
            'version': self.version,
            'rule_type': self.rule_type,
            'copayment_id': str(self.copayment_id) if self.copayment_id else None,
            'deductible_id': str(self.deductible_id) if self.deductible_id else None,
            'discount_id': str(self.discount_id) if self.discount_id else None,
            'commission_id': str(self.commission_id) if self.commission_id else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'archived_at': self.archived_at.isoformat() if self.archived_at else None,
            'is_effective': self.is_effective,
            'is_expired': self.is_expired,
            'adjustment_description': self.get_adjustment_description()
        }