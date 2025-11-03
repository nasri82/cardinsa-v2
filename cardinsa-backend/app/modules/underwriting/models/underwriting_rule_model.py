# =============================================================================
# FILE: app/modules/underwriting/models/underwriting_rule_model.py
# WORLD-CLASS UNDERWRITING RULE MODEL - ENTERPRISE GRADE
# =============================================================================

"""
Underwriting Rule Model - Enterprise Implementation

Advanced underwriting rules engine with comprehensive risk assessment,
automated decision making, and intelligent workflow management.

Features:
- Multi-condition rule logic (AND/OR/NOT operators)
- Risk scoring with premium adjustments
- Automated decision workflows
- Exception handling and escalation
- Audit trail and compliance tracking
- Version control and approval workflows
"""

from sqlalchemy import Column, String, Text, Integer, Numeric, Boolean, DateTime, Date, JSON, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any, List, Union
from enum import Enum
import json

from app.core.database import Base
from app.core.mixins import TimestampMixin, ArchiveMixin
from app.core.enums import BaseEnum


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class UnderwritingDecision(str, BaseEnum):
    """Underwriting decision outcomes"""
    APPROVED = "approved"
    REFERRED = "referred" 
    REJECTED = "rejected"
    PENDING = "pending"
    CONDITIONAL = "conditional"
    DEFERRED = "deferred"


class RuleCategory(str, BaseEnum):
    """Rule categorization for organization"""
    MEDICAL = "medical"
    FINANCIAL = "financial"
    OCCUPATIONAL = "occupational"
    LIFESTYLE = "lifestyle"
    GEOGRAPHICAL = "geographical"
    LEGAL = "legal"
    ELIGIBILITY = "eligibility"
    COVERAGE_LIMITS = "coverage_limits"


class RuleType(str, BaseEnum):
    """Type of rule evaluation"""
    AUTOMATIC = "automatic"
    MANUAL_REVIEW = "manual_review"
    CONDITIONAL = "conditional"
    EXCEPTION = "exception"


class RuleSeverity(str, BaseEnum):
    """Rule impact severity"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConditionOperator(str, BaseEnum):
    """Operators for rule conditions"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    BETWEEN = "between"
    REGEX_MATCH = "regex_match"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class LogicalOperator(str, BaseEnum):
    """Logical operators for combining conditions"""
    AND = "and"
    OR = "or"
    NOT = "not"


# =============================================================================
# UNDERWRITING RULE MODEL
# =============================================================================

class UnderwritingRule(Base, TimestampMixin, ArchiveMixin):
    """
    Enterprise Underwriting Rule Model
    
    Comprehensive rule definition supporting:
    - Multi-condition logic with nested operators
    - Risk scoring and premium impact calculation
    - Automated decision workflows
    - Exception handling and manual review triggers
    - Version control and approval workflows
    """
    
    __tablename__ = 'underwriting_rules'
    
    # =========================================================================
    # PRIMARY FIELDS
    # =========================================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Rule Identification
    rule_name = Column(String(100), nullable=False, index=True)
    name = Column(String(100), nullable=True)  # Alternative name field
    description = Column(Text, nullable=True)
    
    # Rule Classification
    product_type = Column(String(50), nullable=False, index=True)
    rule_category = Column(String(50), nullable=True, index=True)
    rule_type = Column(String(20), nullable=True, default=RuleType.AUTOMATIC, index=True)
    applies_to = Column(String(50), nullable=True, index=True)  # What entity the rule applies to
    
    # Rule Logic and Conditions
    conditions = Column(JSONB, nullable=False)  # Complex condition structure
    condition_json = Column(JSONB, nullable=True)  # Alternative condition field
    actions = Column(JSONB, nullable=False)  # Actions to take when rule matches
    
    # Decision and Impact
    decision_outcome = Column(String(20), nullable=True, index=True)
    target_score = Column(Numeric(5,2), nullable=True)
    risk_score_impact = Column(Numeric(5,2), default=0, nullable=False)
    premium_adjustment_percentage = Column(Numeric(5,2), default=0, nullable=False)
    coverage_modifications = Column(JSONB, nullable=True)
    
    # Rule Management
    priority = Column(Integer, default=100, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    effective_from = Column(Date, default=func.current_date(), nullable=False)
    effective_to = Column(Date, nullable=True)
    
    # Approval and Governance
    created_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    # Related decisions and applications
    decisions = relationship("UnderwritingDecision", back_populates="rule", cascade="all, delete-orphan")
    exceptions = relationship("UnderwritingException", back_populates="rule", cascade="all, delete-orphan")
    
    # Version control (self-referential)
    parent_rule_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_rules.id'), nullable=True)
    child_rules = relationship("UnderwritingRule", backref="parent_rule", remote_side=[id])
    
    # =========================================================================
    # CONSTRAINTS AND INDEXES
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            decision_outcome.in_(['approved', 'referred', 'rejected', 'pending', 'conditional', 'deferred']),
            name='ck_underwriting_rule_decision_outcome'
        ),
        CheckConstraint(
            rule_type.in_(['automatic', 'manual_review', 'conditional', 'exception']),
            name='ck_underwriting_rule_type'
        ),
        CheckConstraint(
            rule_category.in_(['medical', 'financial', 'occupational', 'lifestyle', 'geographical', 'legal', 'eligibility', 'coverage_limits']),
            name='ck_underwriting_rule_category'
        ),
        CheckConstraint(
            'risk_score_impact >= -100 AND risk_score_impact <= 100',
            name='ck_underwriting_rule_risk_score_range'
        ),
        CheckConstraint(
            'premium_adjustment_percentage >= -100 AND premium_adjustment_percentage <= 500',
            name='ck_underwriting_rule_premium_adjustment_range'
        ),
        CheckConstraint(
            'priority >= 0 AND priority <= 1000',
            name='ck_underwriting_rule_priority_range'
        ),
        CheckConstraint(
            'effective_from <= COALESCE(effective_to, effective_from)',
            name='ck_underwriting_rule_date_range'
        ),
        
        # Composite indexes for performance
        Index('ix_underwriting_rules_product_active', 'product_type', 'is_active'),
        Index('ix_underwriting_rules_category_priority', 'rule_category', 'priority'),
        Index('ix_underwriting_rules_effective_dates', 'effective_from', 'effective_to'),
        Index('ix_underwriting_rules_type_active', 'rule_type', 'is_active'),
        
        # Unique constraints
        Index('ix_underwriting_rules_name_product_unique', 'rule_name', 'product_type', unique=True),
    )
    
    # =========================================================================
    # VALIDATION METHODS
    # =========================================================================
    
    @validates('conditions')
    def validate_conditions(self, key, value):
        """Validate condition structure"""
        if not isinstance(value, dict):
            raise ValueError("Conditions must be a valid JSON object")
        
        # Validate condition structure
        self._validate_condition_structure(value)
        return value
    
    @validates('actions')  
    def validate_actions(self, key, value):
        """Validate action structure"""
        if not isinstance(value, dict):
            raise ValueError("Actions must be a valid JSON object")
        
        # Ensure required action fields
        if 'type' not in value:
            raise ValueError("Actions must specify a type")
        
        return value
    
    @validates('rule_name')
    def validate_rule_name(self, key, value):
        """Validate rule name"""
        if not value or not value.strip():
            raise ValueError("Rule name cannot be empty")
        
        if len(value) > 100:
            raise ValueError("Rule name cannot exceed 100 characters")
        
        return value.strip()
    
    @validates('product_type')
    def validate_product_type(self, key, value):
        """Validate product type"""
        if not value or not value.strip():
            raise ValueError("Product type is required")
        
        valid_types = ['medical', 'motor', 'life', 'property', 'travel', 'general']
        if value.lower() not in valid_types:
            raise ValueError(f"Product type must be one of: {', '.join(valid_types)}")
        
        return value.lower()
    
    @validates('priority')
    def validate_priority(self, key, value):
        """Validate priority range"""
        if value is not None and (value < 0 or value > 1000):
            raise ValueError("Priority must be between 0 and 1000")
        return value
    
    @validates('risk_score_impact')
    def validate_risk_score_impact(self, key, value):
        """Validate risk score impact"""
        if value is not None and (value < -100 or value > 100):
            raise ValueError("Risk score impact must be between -100 and 100")
        return value
    
    @validates('premium_adjustment_percentage')
    def validate_premium_adjustment(self, key, value):
        """Validate premium adjustment percentage"""
        if value is not None and (value < -100 or value > 500):
            raise ValueError("Premium adjustment must be between -100% and 500%")
        return value
    
    # =========================================================================
    # BUSINESS LOGIC METHODS
    # =========================================================================
    
    def is_effective(self, check_date: Optional[date] = None) -> bool:
        """Check if rule is effective on given date"""
        if not self.is_active:
            return False
        
        check_date = check_date or date.today()
        
        if self.effective_from and check_date < self.effective_from:
            return False
        
        if self.effective_to and check_date > self.effective_to:
            return False
        
        return True
    
    def get_condition_summary(self) -> str:
        """Get human-readable condition summary"""
        try:
            return self._format_condition_summary(self.conditions)
        except Exception:
            return "Complex conditions - see rule details"
    
    def get_impact_summary(self) -> str:
        """Get impact summary"""
        impacts = []
        
        if self.risk_score_impact and self.risk_score_impact != 0:
            impacts.append(f"Risk Score: {self.risk_score_impact:+.1f}")
        
        if self.premium_adjustment_percentage and self.premium_adjustment_percentage != 0:
            impacts.append(f"Premium: {self.premium_adjustment_percentage:+.1f}%")
        
        if self.decision_outcome:
            impacts.append(f"Decision: {self.decision_outcome.title()}")
        
        return " | ".join(impacts) if impacts else "No impact defined"
    
    def clone_rule(self, new_name: str, created_by: UUID) -> 'UnderwritingRule':
        """Create a copy of this rule"""
        new_rule = UnderwritingRule(
            rule_name=new_name,
            name=new_name,
            description=f"Cloned from: {self.rule_name}",
            product_type=self.product_type,
            rule_category=self.rule_category,
            rule_type=self.rule_type,
            applies_to=self.applies_to,
            conditions=self.conditions.copy(),
            actions=self.actions.copy(),
            decision_outcome=self.decision_outcome,
            target_score=self.target_score,
            risk_score_impact=self.risk_score_impact,
            premium_adjustment_percentage=self.premium_adjustment_percentage,
            coverage_modifications=self.coverage_modifications.copy() if self.coverage_modifications else None,
            priority=self.priority,
            is_active=False,  # Clones start as inactive
            effective_from=date.today(),
            created_by=created_by,
            parent_rule_id=self.id
        )
        return new_rule
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get version information"""
        return {
            'rule_id': str(self.id),
            'version': len(self.child_rules) + 1,
            'parent_id': str(self.parent_rule_id) if self.parent_rule_id else None,
            'has_children': len(self.child_rules) > 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================
    
    def _validate_condition_structure(self, condition: Dict[str, Any]) -> None:
        """Recursively validate condition structure"""
        if 'operator' in condition:
            # This is a logical condition group
            valid_operators = [op.value for op in LogicalOperator]
            if condition['operator'] not in valid_operators:
                raise ValueError(f"Invalid logical operator: {condition['operator']}")
            
            if 'conditions' in condition:
                if not isinstance(condition['conditions'], list):
                    raise ValueError("Conditions must be a list")
                
                for sub_condition in condition['conditions']:
                    self._validate_condition_structure(sub_condition)
        
        elif 'field' in condition:
            # This is a field condition
            if 'operator' not in condition:
                raise ValueError("Field condition must have an operator")
            
            valid_operators = [op.value for op in ConditionOperator]
            if condition['operator'] not in valid_operators:
                raise ValueError(f"Invalid condition operator: {condition['operator']}")
        
        else:
            raise ValueError("Invalid condition structure - must have 'operator' or 'field'")
    
    def _format_condition_summary(self, condition: Dict[str, Any], depth: int = 0) -> str:
        """Format condition for human readability"""
        if depth > 3:  # Prevent infinite recursion
            return "..."
        
        if 'field' in condition:
            # Field condition
            field = condition.get('field', 'unknown')
            operator = condition.get('operator', 'unknown')
            value = condition.get('value', 'unknown')
            
            return f"{field} {operator} {value}"
        
        elif 'operator' in condition:
            # Logical group
            operator = condition.get('operator', 'AND').upper()
            conditions = condition.get('conditions', [])
            
            if not conditions:
                return "empty condition"
            
            formatted_conditions = [
                self._format_condition_summary(cond, depth + 1) 
                for cond in conditions
            ]
            
            if len(formatted_conditions) == 1:
                return formatted_conditions[0]
            
            return f"({f' {operator} '.join(formatted_conditions)})"
        
        return "invalid condition"
    
    # =========================================================================
    # SERIALIZATION METHODS
    # =========================================================================
    
    def to_dict(self, include_relationships: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = {
            'id': str(self.id),
            'rule_name': self.rule_name,
            'name': self.name,
            'description': self.description,
            'product_type': self.product_type,
            'rule_category': self.rule_category,
            'rule_type': self.rule_type,
            'applies_to': self.applies_to,
            'conditions': self.conditions,
            'actions': self.actions,
            'decision_outcome': self.decision_outcome,
            'target_score': float(self.target_score) if self.target_score else None,
            'risk_score_impact': float(self.risk_score_impact) if self.risk_score_impact else None,
            'premium_adjustment_percentage': float(self.premium_adjustment_percentage) if self.premium_adjustment_percentage else None,
            'coverage_modifications': self.coverage_modifications,
            'priority': self.priority,
            'is_active': self.is_active,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'archived_at': self.archived_at.isoformat() if self.archived_at else None,
            
            # Computed fields
            'is_effective': self.is_effective(),
            'condition_summary': self.get_condition_summary(),
            'impact_summary': self.get_impact_summary(),
            'version_info': self.get_version_info()
        }
        
        if include_relationships:
            base_dict.update({
                'decisions_count': len(self.decisions) if self.decisions else 0,
                'exceptions_count': len(self.exceptions) if self.exceptions else 0,
                'child_rules_count': len(self.child_rules) if self.child_rules else 0,
                'parent_rule_id': str(self.parent_rule_id) if self.parent_rule_id else None
            })
        
        return base_dict
    
    def __repr__(self) -> str:
        return f"<UnderwritingRule(id='{self.id}', name='{self.rule_name}', product='{self.product_type}', active={self.is_active})>"
    
    def __str__(self) -> str:
        return f"{self.rule_name} ({self.product_type})"


# =============================================================================
# RELATED MODELS FOR COMPLETENESS
# =============================================================================

class UnderwritingDecision(Base, TimestampMixin, ArchiveMixin):
    """Individual underwriting decisions based on rules"""
    
    __tablename__ = 'underwriting_decisions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    application_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    rule_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_rules.id'), nullable=True, index=True)
    
    decision = Column(String(20), nullable=False)
    decision_score = Column(Numeric(5,2), nullable=True)
    risk_score = Column(Numeric(5,2), nullable=True)
    premium_adjustment = Column(Numeric(5,2), nullable=True)
    
    conditions_applied = Column(JSONB, nullable=True)
    decision_notes = Column(Text, nullable=True)
    underwriter_notes = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    automated = Column(Boolean, default=True, nullable=False)
    decided_by = Column(UUID(as_uuid=True), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    decision_date = Column(DateTime(timezone=True), nullable=True)
    decision_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    rule = relationship("UnderwritingRule", back_populates="decisions")


class UnderwritingException(Base, TimestampMixin):
    """Underwriting exceptions for special cases"""
    
    __tablename__ = 'underwriting_exceptions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    policy_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    rule_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_rules.id'), nullable=True, index=True)
    
    exception_reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    rule = relationship("UnderwritingRule", back_populates="exceptions")