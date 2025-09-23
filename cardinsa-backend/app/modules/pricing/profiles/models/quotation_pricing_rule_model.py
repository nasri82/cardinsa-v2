# app/modules/pricing/profiles/models/quotation_pricing_rule_model.py

"""
Complete QuotationPricingRule Model - Step 4 Implementation

This model represents individual pricing rules that can be applied to profiles.
Rules provide the intelligence layer for dynamic pricing calculations and 
support complex conditional logic for premium adjustments.

Key Features:
- ✅ Multiple rule types (age, gender, occupation, location, etc.)
- ✅ Flexible condition evaluation with operators
- ✅ Various adjustment types (percentage, fixed, multiplier, formula)
- ✅ Priority ordering and effective date management
- ✅ Integration with external pricing components
- ✅ Complete audit trail and validation
"""

from sqlalchemy import Column, String, Text, Boolean, Numeric, DateTime, Integer, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from decimal import Decimal
from typing import Optional, Dict, Any, List, Union
from enum import Enum
import uuid
import json
import re


# Enums for the rule model
class RuleType(str, Enum):
    """Types of pricing rules"""
    AGE_BRACKET = "age_bracket"
    GENDER = "gender"
    OCCUPATION = "occupation"
    LOCATION = "location"
    REGION = "region"
    SMOKING_STATUS = "smoking_status"
    HEALTH_CONDITION = "health_condition"
    FAMILY_SIZE = "family_size"
    INCOME_BRACKET = "income_bracket"
    COVERAGE_AMOUNT = "coverage_amount"
    VEHICLE_TYPE = "vehicle_type"
    DRIVING_RECORD = "driving_record"
    CREDIT_SCORE = "credit_score"
    CLAIMS_HISTORY = "claims_history"
    NETWORK_TIER = "network_tier"
    PROVIDER_TYPE = "provider_type"
    BENEFIT_LEVEL = "benefit_level"
    DEDUCTIBLE_LEVEL = "deductible_level"
    CUSTOM = "custom"
    FORMULA = "formula"


class ComparisonOperator(str, Enum):
    """Comparison operators for rule conditions"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    REGEX_MATCH = "regex_match"


class AdjustmentType(str, Enum):
    """Types of premium adjustments"""
    PERCENTAGE = "percentage"          # Multiply by percentage
    FIXED_AMOUNT = "fixed_amount"      # Add/subtract fixed amount
    MULTIPLIER = "multiplier"          # Multiply by factor
    FORMULA = "formula"                # Use custom formula
    REPLACEMENT = "replacement"        # Replace premium entirely
    MINIMUM = "minimum"                # Set minimum premium
    MAXIMUM = "maximum"                # Set maximum premium
    BENEFIT_BASED = "benefit_based"    # Based on benefit exposure
    NETWORK_BASED = "network_based"    # Based on network costs


class RuleStatus(str, Enum):
    """Rule status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"


class QuotationPricingRule(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Complete QuotationPricingRule Model - Step 4 Implementation
    
    This model provides comprehensive pricing rule management with:
    - Complex conditional logic evaluation
    - Multiple adjustment types and calculations
    - Priority ordering and effective date management
    - Integration with external pricing components
    - Complete audit trail and validation
    """
    
    __tablename__ = "quotation_pricing_rules"
    __table_args__ = (
        # Performance indexes
        Index('idx_pricing_rule_type', 'rule_type'),
        Index('idx_pricing_rule_insurance_type', 'insurance_type'),
        Index('idx_pricing_rule_status', 'status'),
        Index('idx_pricing_rule_priority', 'priority'),
        Index('idx_pricing_rule_active', 'is_active'),
        Index('idx_pricing_rule_effective_from', 'effective_from'),
        Index('idx_pricing_rule_effective_to', 'effective_to'),
        Index('idx_pricing_rule_field_name', 'field_name'),
        Index('idx_pricing_rule_created_by', 'created_by'),
        # Composite indexes for common queries
        Index('idx_pricing_rule_type_status', 'rule_type', 'status'),
        Index('idx_pricing_rule_active_insurance', 'is_active', 'insurance_type'),
        Index('idx_pricing_rule_effective_priority', 'effective_from', 'priority'),
        Index('idx_pricing_rule_field_operator', 'field_name', 'operator'),
        {'extend_existing': True}
    )
    
    # =================================================================
    # CORE RULE IDENTIFICATION
    # =================================================================
    
    # Rule identity (UUIDPrimaryKeyMixin provides 'id')
    rule_name = Column(String(255), nullable=False, comment="Human-readable rule name")
    rule_code = Column(String(50), unique=True, nullable=True, comment="Unique code for API/system reference")
    rule_description = Column(Text, comment="Detailed description of the rule purpose")
    
    # Rule classification
    rule_type = Column(String(50), nullable=False, comment="Type of rule (age_bracket, gender, etc.)")
    insurance_type = Column(String(50), nullable=False, comment="Insurance type this rule applies to")
    product_line = Column(String(100), nullable=True, comment="Specific product line (optional)")
    market_segment = Column(String(100), nullable=True, comment="Target market segment (optional)")
    
    # =================================================================
    # CONDITION DEFINITION - STEP 4 CORE REQUIREMENT
    # =================================================================
    
    # Field and condition configuration
    field_name = Column(String(100), nullable=False, comment="Field name to evaluate (e.g., 'age', 'gender')")
    operator = Column(String(50), nullable=False, comment="Comparison operator (equals, greater_than, etc.)")
    value = Column(Text, nullable=False, comment="Value to compare against (can be JSON for complex values)")
    value_type = Column(String(20), default="string", nullable=False, comment="Data type of the value")
    
    # Complex condition logic
    condition_logic = Column(JSONB, nullable=True, comment="Complex condition logic for advanced rules")
    secondary_conditions = Column(JSONB, nullable=True, comment="Additional conditions that must be met")
    
    # Validation patterns
    validation_pattern = Column(String(500), nullable=True, comment="Regex pattern for value validation")
    validation_message = Column(String(255), nullable=True, comment="Custom validation error message")
    
    # =================================================================
    # ADJUSTMENT DEFINITION - STEP 4 CORE REQUIREMENT
    # =================================================================
    
    # Adjustment configuration
    adjustment_type = Column(String(50), nullable=False, comment="Type of adjustment (percentage, fixed_amount, etc.)")
    adjustment_value = Column(Numeric(15, 4), nullable=False, comment="Adjustment amount or percentage")
    adjustment_formula = Column(Text, nullable=True, comment="Custom formula for complex calculations")
    
    # Adjustment boundaries and limits
    min_adjustment = Column(Numeric(15, 4), nullable=True, comment="Minimum adjustment allowed")
    max_adjustment = Column(Numeric(15, 4), nullable=True, comment="Maximum adjustment allowed")
    adjustment_cap = Column(Numeric(15, 2), nullable=True, comment="Maximum absolute adjustment amount")
    
    # Currency and precision
    currency_code = Column(String(3), nullable=False, default="USD", comment="Currency for adjustment amounts")
    decimal_precision = Column(Integer, default=2, nullable=False, comment="Decimal precision for calculations")
    
    # =================================================================
    # INTEGRATION WITH PRICING COMPONENTS
    # =================================================================
    
    # External component references
    copayment_id = Column(UUID(as_uuid=True), nullable=True, comment="Reference to copayment configuration")
    deductible_id = Column(UUID(as_uuid=True), nullable=True, comment="Reference to deductible configuration")
    discount_id = Column(UUID(as_uuid=True), nullable=True, comment="Reference to discount configuration")
    commission_id = Column(UUID(as_uuid=True), nullable=True, comment="Reference to commission configuration")
    network_id = Column(UUID(as_uuid=True), nullable=True, comment="Reference to network configuration")
    
    # Component integration settings
    apply_after_deductible = Column(Boolean, default=False, nullable=False, comment="Apply adjustment after deductible")
    apply_before_copay = Column(Boolean, default=True, nullable=False, comment="Apply adjustment before copayment")
    compound_with_other_rules = Column(Boolean, default=True, nullable=False, comment="Allow compounding with other rules")
    
    # =================================================================
    # OPERATIONAL SETTINGS
    # =================================================================
    
    # Status and lifecycle
    status = Column(String(20), nullable=False, default=RuleStatus.DRAFT.value, comment="Current rule status")
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether rule is currently active")
    
    # Priority and ordering
    priority = Column(Integer, default=100, nullable=False, comment="Priority order (lower = higher priority)")
    execution_order = Column(Integer, default=100, nullable=False, comment="Order of execution within same priority")
    
    # Effective date management
    effective_from = Column(DateTime(timezone=True), nullable=False, default=func.now(), comment="When rule becomes effective")
    effective_to = Column(DateTime(timezone=True), nullable=True, comment="When rule expires")
    
    # Version and approval
    version = Column(Integer, default=1, nullable=False, comment="Rule version number")
    approval_required = Column(Boolean, default=True, nullable=False, comment="Whether changes require approval")
    approved_by = Column(String(255), nullable=True, comment="Who approved this rule")
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="When rule was approved")
    
    # =================================================================
    # AUDIT AND COMPLIANCE
    # =================================================================
    
    # User tracking (TimestampMixin provides created_at, updated_at)
    created_by = Column(String(255), nullable=False, comment="User who created the rule")
    last_modified_by = Column(String(255), nullable=False, comment="User who last modified the rule")
    
    # Organizational context
    department = Column(String(100), nullable=True, comment="Department responsible for this rule")
    business_unit = Column(String(100), nullable=True, comment="Business unit owning this rule")
    
    # Configuration and metadata
    configuration = Column(JSONB, nullable=True, comment="Extended configuration options")
    tags = Column(JSONB, nullable=True, comment="Tags for categorization and search")
    notes = Column(Text, nullable=True, comment="Internal notes and comments")
    
    # Regulatory and compliance
    regulatory_reference = Column(String(255), nullable=True, comment="Reference to regulatory requirement")
    compliance_notes = Column(Text, nullable=True, comment="Compliance-related notes")
    
    # =================================================================
    # PERFORMANCE TRACKING
    # =================================================================
    
    # Usage statistics
    usage_count = Column(Integer, default=0, nullable=False, comment="Number of times rule has been applied")
    last_used_at = Column(DateTime(timezone=True), nullable=True, comment="When rule was last used")
    application_count = Column(Integer, default=0, nullable=False, comment="Number of applications this rule affected")
    
    # Performance metrics
    avg_adjustment_amount = Column(Numeric(15, 2), nullable=True, comment="Average adjustment amount applied")
    total_adjustment_amount = Column(Numeric(15, 2), default=Decimal('0.00'), nullable=False, comment="Total adjustment amount applied")
    success_rate = Column(Numeric(5, 4), nullable=True, comment="Success rate of rule applications")
    
    # Error tracking
    error_count = Column(Integer, default=0, nullable=False, comment="Number of evaluation errors")
    last_error_at = Column(DateTime(timezone=True), nullable=True, comment="When last error occurred")
    last_error_message = Column(Text, nullable=True, comment="Last error message")
    
    # =================================================================
    # RELATIONSHIPS (will be uncommented when other models are ready)
    # =================================================================
    
    # Note: These relationships will be uncommented once other models are complete
    # profile_rules = relationship(
    #     "QuotationPricingProfileRule",
    #     back_populates="rule",
    #     cascade="all, delete-orphan"
    # )
    
    # age_brackets = relationship(
    #     "QuotationPricingRuleAgeBracket",
    #     back_populates="rule",
    #     cascade="all, delete-orphan",
    #     order_by="QuotationPricingRuleAgeBracket.min_age"
    # )
    
    # =================================================================
    # BUSINESS LOGIC METHODS - STEP 4 CORE REQUIREMENTS
    # =================================================================
    
    def is_currently_effective(self) -> bool:
        """
        Check if rule is currently effective
        
        Returns:
            bool: True if rule is active, effective, and not deleted
        """
        from datetime import datetime
        now = datetime.utcnow()
        
        return (
            self.status == RuleStatus.ACTIVE.value and
            self.is_active and
            self.effective_from <= now and
            (self.effective_to is None or self.effective_to > now) and
            not self.is_deleted  # From SoftDeleteMixin
        )
    
    def is_approved(self) -> bool:
        """
        Check if rule has been approved
        
        Returns:
            bool: True if rule is approved
        """
        return self.approved_by is not None and self.approved_at is not None
    
    def evaluate_condition(self, input_data: Dict[str, Any]) -> bool:
        """
        Evaluate if the rule condition is met - STEP 4 CORE REQUIREMENT
        
        Args:
            input_data (Dict[str, Any]): Input data to evaluate against
            
        Returns:
            bool: True if condition is met
        """
        try:
            # Get the field value from input data
            field_value = input_data.get(self.field_name)
            
            if field_value is None and self.operator not in [ComparisonOperator.IS_NULL.value, ComparisonOperator.IS_NOT_NULL.value]:
                return False
            
            # Parse the comparison value
            comparison_value = self._parse_value(self.value, self.value_type)
            
            # Evaluate based on operator
            return self._evaluate_operator(field_value, self.operator, comparison_value)
            
        except Exception as e:
            self._log_error(f"Condition evaluation error: {str(e)}")
            return False
    
    def calculate_adjustment(self, base_amount: Decimal, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate adjustment amount based on rule configuration - STEP 4 CORE REQUIREMENT
        
        Args:
            base_amount (Decimal): Base amount to adjust
            input_data (Dict[str, Any]): Input data for calculation
            
        Returns:
            Dict[str, Any]: Adjustment calculation results
        """
        try:
            if self.adjustment_type == AdjustmentType.PERCENTAGE.value:
                adjustment = base_amount * (self.adjustment_value / 100)
                
            elif self.adjustment_type == AdjustmentType.FIXED_AMOUNT.value:
                adjustment = self.adjustment_value
                
            elif self.adjustment_type == AdjustmentType.MULTIPLIER.value:
                adjustment = base_amount * self.adjustment_value - base_amount
                
            elif self.adjustment_type == AdjustmentType.FORMULA.value:
                adjustment = self._evaluate_formula(base_amount, input_data)
                
            elif self.adjustment_type == AdjustmentType.REPLACEMENT.value:
                adjustment = self.adjustment_value - base_amount
                
            elif self.adjustment_type == AdjustmentType.BENEFIT_BASED.value:
                benefit_exposure = input_data.get('benefit_exposure', Decimal('0'))
                adjustment = benefit_exposure * self.adjustment_value / 1000  # Scale down
                
            elif self.adjustment_type == AdjustmentType.NETWORK_BASED.value:
                network_cost = input_data.get('network_cost', Decimal('0'))
                adjustment = network_cost * self.adjustment_value
                
            else:
                adjustment = Decimal('0')
            
            # Apply limits
            adjustment = self._apply_adjustment_limits(adjustment)
            
            # Calculate final amount
            final_amount = base_amount + adjustment
            
            return {
                'rule_id': str(self.id),
                'rule_name': self.rule_name,
                'adjustment_type': self.adjustment_type,
                'adjustment_value': float(self.adjustment_value),
                'base_amount': float(base_amount),
                'adjustment_amount': float(adjustment),
                'final_amount': float(final_amount),
                'currency_code': self.currency_code,
                'calculation_date': func.now(),
                'success': True
            }
            
        except Exception as e:
            self._log_error(f"Adjustment calculation error: {str(e)}")
            return {
                'rule_id': str(self.id),
                'rule_name': self.rule_name,
                'error': str(e),
                'success': False
            }
    
    def apply_rule(self, base_amount: Decimal, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Apply complete rule logic - evaluate condition and calculate adjustment
        
        Args:
            base_amount (Decimal): Base amount to adjust
            input_data (Dict[str, Any]): Input data for evaluation
            
        Returns:
            Optional[Dict[str, Any]]: Rule application results or None if not applicable
        """
        # Check if rule is effective
        if not self.is_currently_effective():
            return None
        
        # Evaluate condition
        if not self.evaluate_condition(input_data):
            return None
        
        # Calculate adjustment
        result = self.calculate_adjustment(base_amount, input_data)
        
        # Update usage tracking
        if result.get('success'):
            self.update_usage_tracking(result['adjustment_amount'])
        
        return result
    
    def validate_rule_configuration(self) -> Dict[str, Any]:
        """
        Validate rule configuration - STEP 4 REQUIREMENT
        
        Returns:
            Dict[str, Any]: Validation results
        """
        errors = []
        warnings = []
        
        # Validate field name
        if not self.field_name or not self.field_name.strip():
            errors.append("Field name is required")
        
        # Validate operator
        if self.operator not in [op.value for op in ComparisonOperator]:
            errors.append(f"Invalid operator: {self.operator}")
        
        # Validate value
        if not self.value and self.operator not in [ComparisonOperator.IS_NULL.value, ComparisonOperator.IS_NOT_NULL.value]:
            errors.append("Value is required for this operator")
        
        # Validate adjustment type
        if self.adjustment_type not in [adj.value for adj in AdjustmentType]:
            errors.append(f"Invalid adjustment type: {self.adjustment_type}")
        
        # Validate adjustment value
        if self.adjustment_value is None:
            errors.append("Adjustment value is required")
        
        # Validate adjustment limits
        if self.min_adjustment and self.max_adjustment and self.min_adjustment >= self.max_adjustment:
            errors.append("Minimum adjustment must be less than maximum adjustment")
        
        # Validate effective dates
        if self.effective_to and self.effective_from >= self.effective_to:
            errors.append("Effective from date must be before effective to date")
        
        # Validate formula if applicable
        if self.adjustment_type == AdjustmentType.FORMULA.value and not self.adjustment_formula:
            errors.append("Formula is required for formula adjustment type")
        
        # Validate priority
        if self.priority < 0:
            warnings.append("Negative priority values may cause unexpected behavior")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validation_date': func.now()
        }
    
    def update_usage_tracking(self, adjustment_amount: Optional[Decimal] = None):
        """
        Update usage tracking information
        
        Args:
            adjustment_amount (Optional[Decimal]): Amount of adjustment applied
        """
        from datetime import datetime
        
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        
        if adjustment_amount is not None:
            self.application_count += 1
            self.total_adjustment_amount += adjustment_amount
            
            # Update average
            if self.avg_adjustment_amount:
                self.avg_adjustment_amount = (
                    self.avg_adjustment_amount * (self.application_count - 1) + adjustment_amount
                ) / self.application_count
            else:
                self.avg_adjustment_amount = adjustment_amount
    
    def clone_rule(self, new_name: str, created_by: str) -> "QuotationPricingRule":
        """
        Create a copy of this rule with new name
        
        Args:
            new_name (str): Name for the cloned rule
            created_by (str): User creating the clone
            
        Returns:
            QuotationPricingRule: New cloned rule
        """
        clone = QuotationPricingRule(
            rule_name=new_name,
            rule_code=None,  # Will need to be set separately
            rule_description=f"Cloned from {self.rule_name}",
            rule_type=self.rule_type,
            insurance_type=self.insurance_type,
            product_line=self.product_line,
            market_segment=self.market_segment,
            field_name=self.field_name,
            operator=self.operator,
            value=self.value,
            value_type=self.value_type,
            condition_logic=self.condition_logic.copy() if self.condition_logic else None,
            secondary_conditions=self.secondary_conditions.copy() if self.secondary_conditions else None,
            validation_pattern=self.validation_pattern,
            validation_message=self.validation_message,
            adjustment_type=self.adjustment_type,
            adjustment_value=self.adjustment_value,
            adjustment_formula=self.adjustment_formula,
            min_adjustment=self.min_adjustment,
            max_adjustment=self.max_adjustment,
            adjustment_cap=self.adjustment_cap,
            currency_code=self.currency_code,
            decimal_precision=self.decimal_precision,
            copayment_id=self.copayment_id,
            deductible_id=self.deductible_id,
            discount_id=self.discount_id,
            commission_id=self.commission_id,
            network_id=self.network_id,
            apply_after_deductible=self.apply_after_deductible,
            apply_before_copay=self.apply_before_copay,
            compound_with_other_rules=self.compound_with_other_rules,
            status=RuleStatus.DRAFT.value,  # Always start as draft
            is_active=False,  # Requires activation
            priority=self.priority,
            execution_order=self.execution_order,
            approval_required=self.approval_required,
            created_by=created_by,
            last_modified_by=created_by,
            department=self.department,
            business_unit=self.business_unit,
            configuration=self.configuration.copy() if self.configuration else None,
            tags=self.tags.copy() if self.tags else None,
            regulatory_reference=self.regulatory_reference,
            compliance_notes=self.compliance_notes
        )
        return clone
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert rule to dictionary for API responses
        
        Returns:
            Dict[str, Any]: Rule data as dictionary
        """
        return {
            'id': str(self.id),
            'rule_name': self.rule_name,
            'rule_code': self.rule_code,
            'rule_description': self.rule_description,
            'rule_type': self.rule_type,
            'insurance_type': self.insurance_type,
            'product_line': self.product_line,
            'market_segment': self.market_segment,
            'field_name': self.field_name,
            'operator': self.operator,
            'value': self.value,
            'value_type': self.value_type,
            'adjustment_type': self.adjustment_type,
            'adjustment_value': float(self.adjustment_value),
            'min_adjustment': float(self.min_adjustment) if self.min_adjustment else None,
            'max_adjustment': float(self.max_adjustment) if self.max_adjustment else None,
            'adjustment_cap': float(self.adjustment_cap) if self.adjustment_cap else None,
            'currency_code': self.currency_code,
            'status': self.status,
            'is_active': self.is_active,
            'priority': self.priority,
            'execution_order': self.execution_order,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'version': self.version,
            'is_currently_effective': self.is_currently_effective(),
            'is_approved': self.is_approved(),
            'usage_count': self.usage_count,
            'application_count': self.application_count,
            'avg_adjustment_amount': float(self.avg_adjustment_amount) if self.avg_adjustment_amount else None,
            'total_adjustment_amount': float(self.total_adjustment_amount),
            'success_rate': float(self.success_rate) if self.success_rate else None,
            'error_count': self.error_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'last_modified_by': self.last_modified_by
        }
    
    # =================================================================
    # PRIVATE HELPER METHODS
    # =================================================================
    
    def _parse_value(self, value: str, value_type: str) -> Any:
        """Parse string value to appropriate type"""
        if value_type == "integer":
            return int(value)
        elif value_type == "float":
            return float(value)
        elif value_type == "decimal":
            return Decimal(value)
        elif value_type == "boolean":
            return value.lower() in ('true', '1', 'yes', 'on')
        elif value_type == "json":
            return json.loads(value)
        elif value_type == "list":
            return [item.strip() for item in value.split(',')]
        else:
            return value
    
    def _evaluate_operator(self, field_value: Any, operator: str, comparison_value: Any) -> bool:
        """Evaluate field value against comparison value using operator"""
        try:
            if operator == ComparisonOperator.EQUALS.value:
                return field_value == comparison_value
            elif operator == ComparisonOperator.NOT_EQUALS.value:
                return field_value != comparison_value
            elif operator == ComparisonOperator.GREATER_THAN.value:
                return float(field_value) > float(comparison_value)
            elif operator == ComparisonOperator.GREATER_THAN_OR_EQUAL.value:
                return float(field_value) >= float(comparison_value)
            elif operator == ComparisonOperator.LESS_THAN.value:
                return float(field_value) < float(comparison_value)
            elif operator == ComparisonOperator.LESS_THAN_OR_EQUAL.value:
                return float(field_value) <= float(comparison_value)
            elif operator == ComparisonOperator.IN.value:
                return field_value in comparison_value
            elif operator == ComparisonOperator.NOT_IN.value:
                return field_value not in comparison_value
            elif operator == ComparisonOperator.CONTAINS.value:
                return str(comparison_value).lower() in str(field_value).lower()
            elif operator == ComparisonOperator.NOT_CONTAINS.value:
                return str(comparison_value).lower() not in str(field_value).lower()
            elif operator == ComparisonOperator.STARTS_WITH.value:
                return str(field_value).lower().startswith(str(comparison_value).lower())
            elif operator == ComparisonOperator.ENDS_WITH.value:
                return str(field_value).lower().endswith(str(comparison_value).lower())
            elif operator == ComparisonOperator.BETWEEN.value:
                if isinstance(comparison_value, list) and len(comparison_value) == 2:
                    return comparison_value[0] <= float(field_value) <= comparison_value[1]
                return False
            elif operator == ComparisonOperator.IS_NULL.value:
                return field_value is None
            elif operator == ComparisonOperator.IS_NOT_NULL.value:
                return field_value is not None
            elif operator == ComparisonOperator.REGEX_MATCH.value:
                return bool(re.match(str(comparison_value), str(field_value)))
            else:
                return False
        except Exception:
            return False
    
    def _evaluate_formula(self, base_amount: Decimal, input_data: Dict[str, Any]) -> Decimal:
        """Evaluate custom formula for adjustment calculation"""
        try:
            if not self.adjustment_formula:
                return Decimal('0')
            
            # Create safe evaluation context
            context = {
                'base_amount': float(base_amount),
                'adjustment_value': float(self.adjustment_value),
                **{k: v for k, v in input_data.items() if isinstance(v, (int, float, Decimal))}
            }
            
            # Basic formula evaluation (replace with proper formula engine)
            formula = self.adjustment_formula.lower()
            
            # Simple variable substitution
            for var_name, var_value in context.items():
                formula = formula.replace(var_name, str(var_value))
            
            # Evaluate simple mathematical expressions
            # NOTE: In production, use a proper formula evaluation library
            try:
                result = eval(formula, {"__builtins__": {}}, {})
                return Decimal(str(result))
            except Exception:
                return self.adjustment_value
            
        except Exception:
            return Decimal('0')
    
    def _apply_adjustment_limits(self, adjustment: Decimal) -> Decimal:
        """Apply min/max limits to adjustment amount"""
        if self.min_adjustment is not None:
            adjustment = max(adjustment, self.min_adjustment)
        
        if self.max_adjustment is not None:
            adjustment = min(adjustment, self.max_adjustment)
        
        if self.adjustment_cap is not None:
            adjustment = max(-self.adjustment_cap, min(adjustment, self.adjustment_cap))
        
        return adjustment
    
    def _log_error(self, error_message: str):
        """Log error and update error tracking"""
        from datetime import datetime
        
        self.error_count += 1
        self.last_error_at = datetime.utcnow()
        self.last_error_message = error_message
        
        # In production, integrate with proper logging system
        print(f"Rule {self.id} error: {error_message}")
    
    def __repr__(self):
        return f"<QuotationPricingRule(id={self.id}, name='{self.rule_name}', type='{self.rule_type}', status='{self.status}')>"