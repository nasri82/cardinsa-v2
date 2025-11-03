# app/modules/pricing/profiles/services/advanced_rule_engine.py
"""
Advanced Multi-Condition Logic Engine for Step 6 Completion
Handles complex rule evaluation with AND/OR/NOT operators and nested conditions
"""

from typing import List, Optional, Dict, Any, Union, Tuple
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import json
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ValidationError, BusinessLogicError
from app.core.logging import get_logger

logger = get_logger(__name__)


class LogicalOperator(str, Enum):
    """Supported logical operators for complex conditions."""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class ComparisonOperator(str, Enum):
    """Supported comparison operators."""
    EQUALS = "="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    IN = "IN"
    BETWEEN = "BETWEEN"
    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"


@dataclass
class ConditionNode:
    """Represents a single condition or a group of conditions."""
    operator: Optional[Union[LogicalOperator, ComparisonOperator]] = None
    field: Optional[str] = None
    value: Any = None
    conditions: Optional[List['ConditionNode']] = None
    
    def is_logical(self) -> bool:
        """Check if this is a logical operator node."""
        return self.operator in [LogicalOperator.AND, LogicalOperator.OR, LogicalOperator.NOT]
    
    def is_comparison(self) -> bool:
        """Check if this is a comparison operator node."""
        return self.operator in ComparisonOperator.__members__.values()


@dataclass
class RuleImpact:
    """Represents the impact/action of a rule."""
    type: str  # PERCENTAGE, FIXED_AMOUNT, MULTIPLIER, FORMULA
    value: Any
    formula: Optional[str] = None
    description: Optional[str] = None


@dataclass
class AdvancedRule:
    """Enhanced rule structure with multi-condition support."""
    rule_id: UUID
    name: str
    description: Optional[str]
    conditions: ConditionNode
    impact: RuleImpact
    priority: int = 0
    dependencies: List[UUID] = None
    conflicts_with: List[UUID] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.conflicts_with is None:
            self.conflicts_with = []


class MultiConditionLogicEngine:
    """
    Advanced logic engine for evaluating complex multi-condition rules.
    Supports nested AND/OR/NOT operations and various comparison operators.
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.comparison_operators = {
            ComparisonOperator.EQUALS: self._equals,
            ComparisonOperator.GREATER_THAN: self._greater_than,
            ComparisonOperator.GREATER_EQUAL: self._greater_equal,
            ComparisonOperator.LESS_THAN: self._less_than,
            ComparisonOperator.LESS_EQUAL: self._less_equal,
            ComparisonOperator.IN: self._in_operator,
            ComparisonOperator.BETWEEN: self._between,
            ComparisonOperator.CONTAINS: self._contains,
            ComparisonOperator.STARTS_WITH: self._starts_with,
            ComparisonOperator.ENDS_WITH: self._ends_with,
        }
    
    # ============================================================================
    # CORE EVALUATION METHODS
    # ============================================================================
    
    def evaluate_conditions(
        self,
        conditions: ConditionNode,
        input_data: Dict[str, Any]
    ) -> bool:
        """
        Evaluate complex conditions with nested logic.
        
        Args:
            conditions: The condition tree to evaluate
            input_data: Input data for evaluation
            
        Returns:
            Boolean result of condition evaluation
        """
        try:
            if conditions.is_comparison():
                return self._evaluate_comparison(conditions, input_data)
            elif conditions.is_logical():
                return self._evaluate_logical(conditions, input_data)
            else:
                logger.warning(f"Unknown condition type: {conditions}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating conditions: {str(e)}")
            return False
    
    def _evaluate_comparison(
        self,
        condition: ConditionNode,
        input_data: Dict[str, Any]
    ) -> bool:
        """Evaluate a single comparison condition."""
        if not condition.field:
            logger.warning("Comparison condition missing field name")
            return False
        
        field_value = self._get_nested_field_value(input_data, condition.field)
        
        if field_value is None:
            logger.debug(f"Field {condition.field} not found in input data")
            return False
        
        operator_func = self.comparison_operators.get(condition.operator)
        if not operator_func:
            logger.warning(f"Unsupported comparison operator: {condition.operator}")
            return False
        
        return operator_func(field_value, condition.value)
    
    def _evaluate_logical(
        self,
        condition: ConditionNode,
        input_data: Dict[str, Any]
    ) -> bool:
        """Evaluate logical operators (AND/OR/NOT)."""
        if not condition.conditions:
            logger.warning("Logical condition missing sub-conditions")
            return False
        
        if condition.operator == LogicalOperator.AND:
            return all(
                self.evaluate_conditions(sub_condition, input_data)
                for sub_condition in condition.conditions
            )
        
        elif condition.operator == LogicalOperator.OR:
            return any(
                self.evaluate_conditions(sub_condition, input_data)
                for sub_condition in condition.conditions
            )
        
        elif condition.operator == LogicalOperator.NOT:
            if len(condition.conditions) != 1:
                logger.warning("NOT operator requires exactly one sub-condition")
                return False
            return not self.evaluate_conditions(condition.conditions[0], input_data)
        
        else:
            logger.warning(f"Unsupported logical operator: {condition.operator}")
            return False
    
    # ============================================================================
    # COMPARISON OPERATOR IMPLEMENTATIONS
    # ============================================================================
    
    def _equals(self, field_value: Any, condition_value: Any) -> bool:
        """Equality comparison."""
        return field_value == condition_value
    
    def _greater_than(self, field_value: Any, condition_value: Any) -> bool:
        """Greater than comparison."""
        try:
            return float(field_value) > float(condition_value)
        except (ValueError, TypeError):
            return str(field_value) > str(condition_value)
    
    def _greater_equal(self, field_value: Any, condition_value: Any) -> bool:
        """Greater than or equal comparison."""
        try:
            return float(field_value) >= float(condition_value)
        except (ValueError, TypeError):
            return str(field_value) >= str(condition_value)
    
    def _less_than(self, field_value: Any, condition_value: Any) -> bool:
        """Less than comparison."""
        try:
            return float(field_value) < float(condition_value)
        except (ValueError, TypeError):
            return str(field_value) < str(condition_value)
    
    def _less_equal(self, field_value: Any, condition_value: Any) -> bool:
        """Less than or equal comparison."""
        try:
            return float(field_value) <= float(condition_value)
        except (ValueError, TypeError):
            return str(field_value) <= str(condition_value)
    
    def _in_operator(self, field_value: Any, condition_value: Any) -> bool:
        """IN operator - check if value is in list."""
        if not isinstance(condition_value, (list, tuple, set)):
            return False
        return field_value in condition_value
    
    def _between(self, field_value: Any, condition_value: Any) -> bool:
        """BETWEEN operator - check if value is between two values."""
        if not isinstance(condition_value, (list, tuple)) or len(condition_value) != 2:
            return False
        
        try:
            value = float(field_value)
            min_val = float(condition_value[0])
            max_val = float(condition_value[1])
            return min_val <= value <= max_val
        except (ValueError, TypeError):
            value_str = str(field_value)
            return str(condition_value[0]) <= value_str <= str(condition_value[1])
    
    def _contains(self, field_value: Any, condition_value: Any) -> bool:
        """CONTAINS operator - check if field contains value."""
        return str(condition_value).lower() in str(field_value).lower()
    
    def _starts_with(self, field_value: Any, condition_value: Any) -> bool:
        """STARTS_WITH operator."""
        return str(field_value).lower().startswith(str(condition_value).lower())
    
    def _ends_with(self, field_value: Any, condition_value: Any) -> bool:
        """ENDS_WITH operator."""
        return str(field_value).lower().endswith(str(condition_value).lower())
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _get_nested_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """
        Get value from nested dictionary using dot notation.
        
        Examples:
            'age' -> data['age']
            'member.age' -> data['member']['age']
            'coverage.benefits.dental' -> data['coverage']['benefits']['dental']
        """
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def parse_condition_json(self, condition_json: Union[str, Dict]) -> ConditionNode:
        """
        Parse JSON condition structure into ConditionNode tree.
        
        Example JSON:
        {
          "operator": "AND",
          "conditions": [
            {
              "field": "age",
              "operator": "BETWEEN",
              "value": [25, 65]
            },
            {
              "operator": "OR",
              "conditions": [
                {"field": "premium", "operator": ">", "value": 1000},
                {"field": "coverage_type", "operator": "IN", "value": ["PREMIUM", "PLATINUM"]}
              ]
            }
          ]
        }
        """
        if isinstance(condition_json, str):
            condition_data = json.loads(condition_json)
        else:
            condition_data = condition_json
        
        return self._parse_condition_node(condition_data)
    
    def _parse_condition_node(self, data: Dict[str, Any]) -> ConditionNode:
        """Recursively parse condition node from dictionary."""
        operator = data.get('operator')
        field = data.get('field')
        value = data.get('value')
        sub_conditions = data.get('conditions', [])
        
        # Parse sub-conditions recursively
        parsed_conditions = [
            self._parse_condition_node(sub_condition)
            for sub_condition in sub_conditions
        ] if sub_conditions else None
        
        return ConditionNode(
            operator=operator,
            field=field,
            value=value,
            conditions=parsed_conditions
        )
    
    def validate_condition_structure(self, conditions: ConditionNode) -> List[str]:
        """
        Validate condition structure and return list of validation errors.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        try:
            self._validate_condition_node(conditions, errors)
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors
    
    def _validate_condition_node(
        self,
        condition: ConditionNode,
        errors: List[str],
        depth: int = 0
    ):
        """Recursively validate condition node structure."""
        if depth > 10:  # Prevent infinite recursion
            errors.append("Condition nesting too deep (max 10 levels)")
            return
        
        if not condition.operator:
            errors.append("Missing operator in condition")
            return
        
        # Validate logical operators
        if condition.is_logical():
            if not condition.conditions:
                errors.append(f"Logical operator {condition.operator} requires sub-conditions")
                return
            
            if condition.operator == LogicalOperator.NOT and len(condition.conditions) != 1:
                errors.append("NOT operator requires exactly one sub-condition")
            
            # Recursively validate sub-conditions
            for sub_condition in condition.conditions:
                self._validate_condition_node(sub_condition, errors, depth + 1)
        
        # Validate comparison operators
        elif condition.is_comparison():
            if not condition.field:
                errors.append(f"Comparison operator {condition.operator} requires field name")
            
            if condition.value is None:
                errors.append(f"Comparison operator {condition.operator} requires value")
            
            # Validate operator-specific requirements
            if condition.operator == ComparisonOperator.BETWEEN:
                if not isinstance(condition.value, (list, tuple)) or len(condition.value) != 2:
                    errors.append("BETWEEN operator requires array of exactly 2 values")
            
            elif condition.operator == ComparisonOperator.IN:
                if not isinstance(condition.value, (list, tuple, set)):
                    errors.append("IN operator requires array/list value")
        
        else:
            errors.append(f"Unknown operator: {condition.operator}")


# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

def create_example_rule() -> AdvancedRule:
    """Create an example complex rule for testing."""
    
    # Complex condition: (age BETWEEN 25-65) AND ((premium > 1000) OR (coverage_type IN ['PREMIUM', 'PLATINUM']))
    conditions = ConditionNode(
        operator=LogicalOperator.AND,
        conditions=[
            ConditionNode(
                operator=ComparisonOperator.BETWEEN,
                field="age",
                value=[25, 65]
            ),
            ConditionNode(
                operator=LogicalOperator.OR,
                conditions=[
                    ConditionNode(
                        operator=ComparisonOperator.GREATER_THAN,
                        field="premium",
                        value=1000
                    ),
                    ConditionNode(
                        operator=ComparisonOperator.IN,
                        field="coverage_type",
                        value=["PREMIUM", "PLATINUM"]
                    )
                ]
            )
        ]
    )
    
    impact = RuleImpact(
        type="PERCENTAGE",
        value=-0.10,
        formula="base_premium * (1 - 0.10)",
        description="10% discount for qualified members"
    )
    
    return AdvancedRule(
        rule_id=UUID('12345678-1234-5678-9abc-123456789012'),
        name="Complex Age & Premium Rule",
        description="Discount for age 25-65 with high premium or premium coverage",
        conditions=conditions,
        impact=impact,
        priority=100
    )


def test_multi_condition_engine():
    """Test the multi-condition engine with example data."""
    engine = MultiConditionLogicEngine()
    rule = create_example_rule()
    
    # Test case 1: Should match (age in range, high premium)
    test_data_1 = {
        "age": 35,
        "premium": 1500,
        "coverage_type": "BASIC"
    }
    
    result_1 = engine.evaluate_conditions(rule.conditions, test_data_1)
    print(f"Test 1 - Expected: True, Got: {result_1}")
    
    # Test case 2: Should match (age in range, premium coverage)
    test_data_2 = {
        "age": 45,
        "premium": 800,
        "coverage_type": "PREMIUM"
    }
    
    result_2 = engine.evaluate_conditions(rule.conditions, test_data_2)
    print(f"Test 2 - Expected: True, Got: {result_2}")
    
    # Test case 3: Should NOT match (age out of range)
    test_data_3 = {
        "age": 70,
        "premium": 1500,
        "coverage_type": "PREMIUM"
    }
    
    result_3 = engine.evaluate_conditions(rule.conditions, test_data_3)
    print(f"Test 3 - Expected: False, Got: {result_3}")
    
    # Test case 4: Should NOT match (age in range but low premium and basic coverage)
    test_data_4 = {
        "age": 35,
        "premium": 500,
        "coverage_type": "BASIC"
    }
    
    result_4 = engine.evaluate_conditions(rule.conditions, test_data_4)
    print(f"Test 4 - Expected: False, Got: {result_4}")


if __name__ == "__main__":
    test_multi_condition_engine()