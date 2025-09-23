# app/modules/pricing/plans/models/plan_eligibility_rule_model.py

"""
Plan Eligibility Rule Model - Production Ready

Defines eligibility criteria and rules for plan enrollment.
Handles age, demographic, medical, and business rule validations.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, ForeignKey,
    Index, UniqueConstraint, Date, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import date, datetime
from enum import Enum
import uuid
import json


# ================================================================
# ENUMS
# ================================================================

class RuleCategory(str, Enum):
    """Rule category"""
    AGE = "age"
    GENDER = "gender"
    LOCATION = "location"
    OCCUPATION = "occupation"
    INCOME = "income"
    HEALTH = "health"
    FAMILY = "family"
    EMPLOYMENT = "employment"
    LIFESTYLE = "lifestyle"
    EXISTING_COVERAGE = "existing_coverage"
    CUSTOM = "custom"


class RuleType(str, Enum):
    """Type of eligibility rule"""
    INCLUSION = "inclusion"      # Must meet to be eligible
    EXCLUSION = "exclusion"      # Disqualifies if met
    PREFERENCE = "preference"    # Preferred but not required
    WARNING = "warning"          # Generates warning but doesn't block


class RuleOperator(str, Enum):
    """Comparison operators for rules"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_EQUAL = "greater_equal"
    LESS_THAN = "less_than"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"


class RuleLogic(str, Enum):
    """Logical operators for combining rules"""
    AND = "and"
    OR = "or"
    NOT = "not"
    XOR = "xor"


class RuleSeverity(str, Enum):
    """Severity of rule violation"""
    CRITICAL = "critical"        # Absolute block
    HIGH = "high"               # Strong recommendation against
    MEDIUM = "medium"           # Moderate concern
    LOW = "low"                 # Minor issue
    INFO = "info"               # Informational only


# ================================================================
# PLAN ELIGIBILITY RULE MODEL
# ================================================================

class PlanEligibilityRule(Base):
    """
    Plan Eligibility Rule Model
    
    Defines complex eligibility criteria for plan enrollment
    with support for nested conditions and business rules.
    """
    
    __tablename__ = "plan_eligibility_rules"
    
    __table_args__ = (
        # Unique rule name per plan
        UniqueConstraint('plan_id', 'rule_name', name='uq_plan_rule_name'),
        
        # Indexes
        Index('idx_plan_eligibility_rules_plan_id', 'plan_id'),
        Index('idx_plan_eligibility_rules_category', 'rule_category'),
        Index('idx_plan_eligibility_rules_type', 'rule_type'),
        Index('idx_plan_eligibility_rules_is_mandatory', 'is_mandatory'),
        Index('idx_plan_eligibility_rules_priority', 'priority'),
        
        # Composite indexes
        Index('idx_plan_eligibility_rules_plan_mandatory', 'plan_id', 'is_mandatory'),
        Index('idx_plan_eligibility_rules_plan_active', 'plan_id', 'is_active'),
    )
    
    # ================================================================
    # PRIMARY KEY & IDENTIFIERS
    # ================================================================
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # ================================================================
    # FOREIGN KEYS
    # ================================================================
    
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to plan"
    )
    
    parent_rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plan_eligibility_rules.id", ondelete="CASCADE"),
        nullable=True,
        comment="Parent rule for nested conditions"
    )
    
    # ================================================================
    # RULE IDENTIFICATION
    # ================================================================
    
    rule_name = Column(
        String(100),
        nullable=False,
        comment="Unique rule name within plan"
    )
    
    rule_description = Column(
        Text,
        nullable=True,
        comment="Human-readable rule description"
    )
    
    rule_code = Column(
        String(50),
        nullable=True,
        comment="Internal rule code"
    )
    
    # ================================================================
    # RULE CONFIGURATION
    # ================================================================
    
    rule_category = Column(
        String(50),
        nullable=False,
        default=RuleCategory.CUSTOM.value,
        comment="Category of rule"
    )
    
    rule_type = Column(
        String(20),
        nullable=False,
        default=RuleType.INCLUSION.value,
        comment="Type of rule"
    )
    
    rule_severity = Column(
        String(20),
        nullable=False,
        default=RuleSeverity.CRITICAL.value,
        comment="Severity of rule violation"
    )
    
    # ================================================================
    # RULE CRITERIA
    # ================================================================
    
    field_name = Column(
        String(100),
        nullable=True,
        comment="Field/attribute to evaluate"
    )
    
    operator = Column(
        String(20),
        nullable=True,
        comment="Comparison operator"
    )
    
    value = Column(
        JSONB,
        nullable=True,
        comment="Value(s) to compare against"
    )
    
    eligibility_criteria = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Complex eligibility criteria as JSON"
    )
    
    # ================================================================
    # RULE LOGIC
    # ================================================================
    
    logic_operator = Column(
        String(10),
        nullable=False,
        default=RuleLogic.AND.value,
        comment="Logic for combining with other rules"
    )
    
    rule_group = Column(
        String(50),
        nullable=True,
        comment="Group identifier for related rules"
    )
    
    priority = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Execution priority (lower first)"
    )
    
    # ================================================================
    # CONDITIONS & REQUIREMENTS
    # ================================================================
    
    is_mandatory = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Is this a mandatory rule"
    )
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Is rule currently active"
    )
    
    can_override = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Can be overridden with approval"
    )
    
    requires_documentation = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Requires supporting documentation"
    )
    
    # ================================================================
    # AGE-SPECIFIC RULES
    # ================================================================
    
    min_age = Column(
        Integer,
        nullable=True,
        comment="Minimum age requirement"
    )
    
    max_age = Column(
        Integer,
        nullable=True,
        comment="Maximum age requirement"
    )
    
    age_calculation_date = Column(
        String(50),
        nullable=True,
        comment="How to calculate age (enrollment, birthday, etc.)"
    )
    
    # ================================================================
    # MESSAGES & FEEDBACK
    # ================================================================
    
    success_message = Column(
        Text,
        nullable=True,
        comment="Message when rule passes"
    )
    
    failure_message = Column(
        Text,
        nullable=True,
        comment="Message when rule fails"
    )
    
    failure_message_ar = Column(
        Text,
        nullable=True,
        comment="Failure message in Arabic"
    )
    
    recommendation = Column(
        Text,
        nullable=True,
        comment="Recommendation if rule fails"
    )
    
    # ================================================================
    # DATES
    # ================================================================
    
    effective_date = Column(
        Date,
        nullable=True,
        comment="Rule effective date"
    )
    
    expiry_date = Column(
        Date,
        nullable=True,
        comment="Rule expiry date"
    )
    
    # ================================================================
    # EXCEPTIONS & OVERRIDES
    # ================================================================
    
    exception_conditions = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Conditions that exempt from rule"
    )
    
    override_codes = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="Authorization codes that can override"
    )
    
    # ================================================================
    # METADATA
    # ================================================================
    
    validation_script = Column(
        Text,
        nullable=True,
        comment="Custom validation script/formula"
    )
    
    external_system_ref = Column(
        String(100),
        nullable=True,
        comment="Reference to external validation system"
    )
    
    tags = Column(
        JSONB,
        nullable=True,
        default=[],
        comment="Rule tags for categorization"
    )
    
    plan_eligibility_metadata = Column(
        JSONB,
        nullable=True,
        default={},
        comment="Additional metadata"
    )
    
    # ================================================================
    # AUDIT FIELDS
    # ================================================================
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    plan = relationship(
        "Plan",
        back_populates="eligibility_rules",
        foreign_keys=[plan_id]
    )
    
    # Self-referential relationship for nested rules
    child_rules = relationship(
        "PlanEligibilityRule",
        backref="parent_rule",
        remote_side=[id],
        cascade="all, delete-orphan"
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('rule_category')
    def validate_rule_category(self, key, value):
        """Validate rule category"""
        if value not in [e.value for e in RuleCategory]:
            raise ValueError(f"Invalid rule category: {value}")
        return value
    
    @validates('rule_type')
    def validate_rule_type(self, key, value):
        """Validate rule type"""
        if value not in [e.value for e in RuleType]:
            raise ValueError(f"Invalid rule type: {value}")
        return value
    
    @validates('operator')
    def validate_operator(self, key, value):
        """Validate operator"""
        if value and value not in [e.value for e in RuleOperator]:
            raise ValueError(f"Invalid operator: {value}")
        return value
    
    @validates('logic_operator')
    def validate_logic_operator(self, key, value):
        """Validate logic operator"""
        if value not in [e.value for e in RuleLogic]:
            raise ValueError(f"Invalid logic operator: {value}")
        return value
    
    @validates('min_age')
    def validate_min_age(self, key, value):
        """Validate minimum age"""
        if value is not None and (value < 0 or value > 150):
            raise ValueError("Invalid minimum age")
        return value
    
    @validates('max_age')
    def validate_max_age(self, key, value):
        """Validate maximum age"""
        if value is not None and (value < 0 or value > 150):
            raise ValueError("Invalid maximum age")
        return value
    
    # ================================================================
    # METHODS
    # ================================================================
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate rule against given context
        
        Args:
            context: Dictionary containing data to evaluate
            
        Returns:
            Dictionary with evaluation result
        """
        result = {
            'rule_id': str(self.id),
            'rule_name': self.rule_name,
            'passed': False,
            'message': None,
            'severity': self.rule_severity
        }
        
        try:
            # Simple field-based evaluation
            if self.field_name and self.operator and self.value is not None:
                field_value = context.get(self.field_name)
                passed = self._evaluate_condition(field_value, self.operator, self.value)
            
            # Complex criteria evaluation
            elif self.eligibility_criteria:
                passed = self._evaluate_complex_criteria(context, self.eligibility_criteria)
            
            # Age-based evaluation
            elif self.rule_category == RuleCategory.AGE.value:
                age = context.get('age')
                passed = self._evaluate_age(age)
            
            # Custom validation script
            elif self.validation_script:
                # Would need safe execution environment
                passed = False
            
            else:
                passed = True
            
            # Check exceptions
            if not passed and self.exception_conditions:
                if self._check_exceptions(context):
                    passed = True
                    result['exception_applied'] = True
            
            result['passed'] = passed
            result['message'] = self.success_message if passed else self.failure_message
            
            # Handle rule type
            if self.rule_type == RuleType.EXCLUSION.value:
                # Invert for exclusion rules
                result['passed'] = not passed
            
        except Exception as e:
            result['error'] = str(e)
            result['passed'] = False
            
        return result
    
    def _evaluate_condition(self, field_value: Any, operator: str, compare_value: Any) -> bool:
        """Evaluate a single condition"""
        if operator == RuleOperator.EQUALS.value:
            return field_value == compare_value
        elif operator == RuleOperator.NOT_EQUALS.value:
            return field_value != compare_value
        elif operator == RuleOperator.GREATER_THAN.value:
            return field_value > compare_value
        elif operator == RuleOperator.GREATER_EQUAL.value:
            return field_value >= compare_value
        elif operator == RuleOperator.LESS_THAN.value:
            return field_value < compare_value
        elif operator == RuleOperator.LESS_EQUAL.value:
            return field_value <= compare_value
        elif operator == RuleOperator.IN.value:
            return field_value in compare_value
        elif operator == RuleOperator.NOT_IN.value:
            return field_value not in compare_value
        elif operator == RuleOperator.BETWEEN.value:
            return compare_value[0] <= field_value <= compare_value[1]
        elif operator == RuleOperator.CONTAINS.value:
            return compare_value in str(field_value)
        elif operator == RuleOperator.STARTS_WITH.value:
            return str(field_value).startswith(compare_value)
        elif operator == RuleOperator.ENDS_WITH.value:
            return str(field_value).endswith(compare_value)
        return False
    
    def _evaluate_age(self, age: Optional[int]) -> bool:
        """Evaluate age-based rule"""
        if age is None:
            return False
        
        if self.min_age is not None and age < self.min_age:
            return False
        
        if self.max_age is not None and age > self.max_age:
            return False
        
        return True
    
    def _evaluate_complex_criteria(self, context: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Evaluate complex nested criteria"""
        # This would implement complex JSON-based rule evaluation
        # For now, return simplified version
        for key, condition in criteria.items():
            if key not in context:
                return False
            
            if isinstance(condition, dict):
                operator = condition.get('operator', 'equals')
                value = condition.get('value')
                if not self._evaluate_condition(context[key], operator, value):
                    return False
            elif context[key] != condition:
                return False
        
        return True
    
    def _check_exceptions(self, context: Dict[str, Any]) -> bool:
        """Check if exception conditions are met"""
        if not self.exception_conditions:
            return False
        
        return self._evaluate_complex_criteria(context, self.exception_conditions)
    
    def can_be_overridden(self, override_code: Optional[str] = None) -> bool:
        """
        Check if rule can be overridden
        
        Args:
            override_code: Override authorization code
            
        Returns:
            True if can be overridden
        """
        if not self.can_override:
            return False
        
        if override_code and self.override_codes:
            return override_code in self.override_codes
        
        return True
    
    def is_effective(self, check_date: Optional[date] = None) -> bool:
        """Check if rule is effective on given date"""
        if not self.is_active:
            return False
        
        check_date = check_date or date.today()
        
        if self.effective_date and check_date < self.effective_date:
            return False
        
        if self.expiry_date and check_date > self.expiry_date:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'plan_id': str(self.plan_id),
            'rule_name': self.rule_name,
            'rule_category': self.rule_category,
            'rule_type': self.rule_type,
            'rule_severity': self.rule_severity,
            'is_mandatory': self.is_mandatory,
            'is_active': self.is_active,
            'can_override': self.can_override,
            'min_age': self.min_age,
            'max_age': self.max_age,
            'priority': self.priority
        }
    
    def __repr__(self) -> str:
        return f"<PlanEligibilityRule(id={self.id}, plan_id={self.plan_id}, name={self.rule_name}, type={self.rule_type})>"