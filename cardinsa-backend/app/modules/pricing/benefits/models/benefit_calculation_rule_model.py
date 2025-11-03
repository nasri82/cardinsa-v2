# app/modules/benefits/models/benefit_calculation_rule_model.py
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
import uuid

from app.core.database import Base

# Import enums from the dedicated enums file
from .benefit_calculation_rule_enums import (
    RuleType,
    CalculationMethod,
    RuleCategory, 
    ResetFrequency,
    DeploymentStage,
    RuleStatus,
    AuthorizationLevel,
    FormulaComplexity,
    NetworkTier,
    CurrencyCode,
    RoundingMethod
)


class BenefitCalculationRule(Base):
    """
    Model for benefit calculation rules and business logic.
    Defines how benefits are calculated, including formulas, conditions, and processing rules.
    """
    
    __tablename__ = "benefit_calculation_rules"
    
    # =====================================================
    # PRIMARY FIELDS
    # =====================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    rule_name = Column(String(100), nullable=False)
    rule_name_ar = Column(String(100), nullable=True)
    
    # =====================================================
    # RULE CLASSIFICATION
    # =====================================================
    
    rule_type = Column(String(30), nullable=False, index=True)
    # Options: DEDUCTIBLE, COPAY, COINSURANCE, COVERAGE_LIMIT, OUT_OF_POCKET, BENEFIT_MAX, 
    #          ACCUMULATOR, RESET, ELIGIBILITY, AUTHORIZATION, PRICING
    
    calculation_method = Column(String(30), nullable=False, default='FORMULA')
    # Options: FORMULA, LOOKUP_TABLE, PERCENTAGE, FIXED_AMOUNT, TIERED, CONDITIONAL, MATRIX
    
    rule_category = Column(String(30), nullable=False, default='FINANCIAL')
    # Options: FINANCIAL, UTILIZATION, ELIGIBILITY, AUTHORIZATION, NETWORK, TEMPORAL
    
    # =====================================================
    # RULE HIERARCHY & DEPENDENCIES
    # =====================================================
    
    priority_order = Column(Integer, default=1, nullable=False)
    execution_sequence = Column(Integer, default=1)
    
    # Parent-child relationships for complex rule chains
    parent_rule_id = Column(UUID(as_uuid=True), ForeignKey('benefit_calculation_rules.id'), nullable=True)
    depends_on_rules = Column(JSONB, nullable=True)  # List of rule IDs this depends on
    
    # Rule grouping
    rule_group = Column(String(50), nullable=True)
    rule_set = Column(String(50), nullable=True)
    
    # =====================================================
    # CALCULATION FORMULAS & LOGIC
    # =====================================================
    
    # Primary calculation formula
    calculation_formula = Column(Text, nullable=True)
    # Example: "IF(service_cost > deductible_remaining, (service_cost - deductible_remaining) * coinsurance_rate, 0)"
    
    # Alternative formulas for different scenarios
    in_network_formula = Column(Text, nullable=True)
    out_of_network_formula = Column(Text, nullable=True)
    emergency_formula = Column(Text, nullable=True)
    
    # Mathematical operations
    formula_variables = Column(JSONB, nullable=True)
    # Example: {"deductible_rate": 0.2, "max_benefit": 5000, "frequency_limit": 12}
    
    calculation_parameters = Column(JSONB, nullable=True)
    # Example: {"rounding_method": "up", "minimum_payment": 10.00, "precision": 2}
    
    # =====================================================
    # CONDITIONS & TRIGGERS
    # =====================================================
    
    # When this rule applies
    trigger_conditions = Column(JSONB, nullable=True)
    # Example: {"age": {"min": 18, "max": 65}, "coverage_type": "MEDICAL", "service_category": "OUTPATIENT"}
    
    # Exclusion conditions
    exclusion_conditions = Column(JSONB, nullable=True)
    # Example: {"pre_existing": true, "experimental_treatment": true}
    
    # Time-based conditions
    effective_conditions = Column(JSONB, nullable=True)
    # Example: {"waiting_period_met": true, "benefit_period_active": true}
    
    # Geographic conditions
    geographic_conditions = Column(JSONB, nullable=True)
    # Example: {"states": ["TX", "CA"], "countries": ["US"], "emergency_worldwide": true}
    
    # =====================================================
    # FINANCIAL PARAMETERS
    # =====================================================
    
    # Base amounts
    base_amount = Column(Numeric(15, 2), nullable=True)
    minimum_amount = Column(Numeric(15, 2), nullable=True)
    maximum_amount = Column(Numeric(15, 2), nullable=True)
    
    # Percentages
    percentage_rate = Column(Numeric(5, 4), nullable=True)  # Supports up to 99.9999%
    discount_rate = Column(Numeric(5, 4), nullable=True)
    penalty_rate = Column(Numeric(5, 4), nullable=True)
    
    # Network-based amounts
    in_network_amount = Column(Numeric(15, 2), nullable=True)
    out_of_network_amount = Column(Numeric(15, 2), nullable=True)
    in_network_percentage = Column(Numeric(5, 4), nullable=True)
    out_of_network_percentage = Column(Numeric(5, 4), nullable=True)
    
    # Currency and precision
    currency_code = Column(String(3), default='USD')
    decimal_precision = Column(Integer, default=2)
    
    # =====================================================
    # ACCUMULATION & TRACKING
    # =====================================================
    
    # What this rule contributes to
    contributes_to_deductible = Column(Boolean, default=False)
    contributes_to_oop_max = Column(Boolean, default=False)
    contributes_to_benefit_max = Column(Boolean, default=False)
    
    # Accumulation behavior
    accumulates_across_family = Column(Boolean, default=False)
    accumulates_across_plans = Column(Boolean, default=False)
    
    # Reset behavior
    reset_frequency = Column(String(20), default='ANNUAL')
    # Options: NEVER, DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUAL, PLAN_YEAR, LIFETIME
    
    reset_conditions = Column(JSONB, nullable=True)
    # Example: {"new_plan_year": true, "member_change": false}
    
    # =====================================================
    # LOOKUP TABLES & REFERENCE DATA
    # =====================================================
    
    # For lookup-based calculations
    lookup_table_data = Column(JSONB, nullable=True)
    # Example: {"age_brackets": [{"min_age": 0, "max_age": 17, "rate": 0.1}, {"min_age": 18, "max_age": 64, "rate": 0.2}]}
    
    # External reference data
    reference_table = Column(String(100), nullable=True)
    reference_key = Column(String(50), nullable=True)
    
    # =====================================================
    # RULE RELATIONSHIPS
    # =====================================================
    
    # Links to other entities
    benefit_type_id = Column(UUID(as_uuid=True), ForeignKey('benefit_types.id'), nullable=True, index=True)
    coverage_id = Column(UUID(as_uuid=True), ForeignKey('coverages.id'), nullable=True, index=True)
    limit_id = Column(UUID(as_uuid=True), ForeignKey('benefit_limits.id'), nullable=True, index=True)
    
    # Product associations
    applies_to_products = Column(JSONB, nullable=True)  # List of product IDs
    applies_to_plans = Column(JSONB, nullable=True)     # List of plan IDs
    
    # =====================================================
    # VALIDATION & BUSINESS RULES
    # =====================================================
    
    # Validation rules
    validation_rules = Column(JSONB, nullable=True)
    # Example: {"required_fields": ["age", "gender"], "min_service_cost": 0.01}
    
    # Error handling
    error_handling = Column(JSONB, nullable=True)
    # Example: {"on_missing_data": "use_default", "on_calculation_error": "deny_claim"}
    
    # Business rule exceptions
    exception_handling = Column(JSONB, nullable=True)
    # Example: {"life_threatening": "override_limits", "experimental": "require_pre_auth"}
    
    # =====================================================
    # AUTHORIZATION & WORKFLOW
    # =====================================================
    
    requires_authorization = Column(Boolean, default=False)
    authorization_level = Column(String(30), nullable=True)
    # Options: AUTO, SUPERVISOR, MANAGER, MEDICAL_DIRECTOR, EXTERNAL_REVIEW
    
    # Workflow integration
    triggers_workflow = Column(Boolean, default=False)
    workflow_type = Column(String(50), nullable=True)
    
    # Notification settings
    notification_rules = Column(JSONB, nullable=True)
    # Example: {"notify_member": true, "notify_provider": false, "alert_threshold": 5000}
    
    # =====================================================
    # REPORTING & ANALYTICS
    # =====================================================
    
    # Tracking and reporting
    track_utilization = Column(Boolean, default=False)
    report_category = Column(String(50), nullable=True)
    
    # Performance metrics
    performance_metrics = Column(JSONB, nullable=True)
    # Example: {"avg_processing_time": 0.5, "accuracy_rate": 99.9, "override_frequency": 0.1}
    
    # =====================================================
    # STATUS & CONTROL
    # =====================================================
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_system_rule = Column(Boolean, default=False)
    is_mandatory = Column(Boolean, default=False)
    
    # Testing and deployment
    is_test_rule = Column(Boolean, default=False)
    deployment_stage = Column(String(20), default='PRODUCTION')
    # Options: DEVELOPMENT, TESTING, STAGING, PRODUCTION, DEPRECATED
    
    # Effective dates
    effective_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    effective_to = Column(DateTime, nullable=True)
    
    # =====================================================
    # METADATA & DOCUMENTATION
    # =====================================================
    
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # Technical documentation
    technical_notes = Column(Text, nullable=True)
    business_rationale = Column(Text, nullable=True)
    
    # Examples and test cases
    example_scenarios = Column(JSONB, nullable=True)
    test_cases = Column(JSONB, nullable=True)
    
    # Regulatory and compliance
    regulatory_reference = Column(String(100), nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
    # =====================================================
    # AUDIT & VERSIONING
    # =====================================================
    
    version = Column(Integer, default=1, nullable=False)
    change_reason = Column(String(255), nullable=True)
    
    # Source tracking
    source_system = Column(String(50), nullable=True)
    external_id = Column(String(50), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # =====================================================
    # RELATIONSHIPS
    # =====================================================
    
    # Parent-child relationships
    child_rules = relationship("BenefitCalculationRule", backref="parent_rule", remote_side=[id])
    
    # Related entities (will be defined when other models exist)
    # benefit_type = relationship("BenefitType", back_populates="calculation_rules")
    # coverage = relationship("Coverage", back_populates="calculation_rules") 
    # limit = relationship("BenefitLimit", back_populates="calculation_rules")
    
    # =====================================================
    # INDEXES
    # =====================================================
    
    __table_args__ = (
        Index('idx_calc_rules_type_method', 'rule_type', 'calculation_method'),
        Index('idx_calc_rules_priority', 'priority_order', 'execution_sequence'),
        Index('idx_calc_rules_active_effective', 'is_active', 'effective_from', 'effective_to'),
        Index('idx_calc_rules_category_group', 'rule_category', 'rule_group'),
        Index('idx_calc_rules_relationships', 'benefit_type_id', 'coverage_id', 'limit_id'),
    )
    
    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def evaluate_rule(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the calculation rule against input data.
        Returns the calculated result and metadata.
        """
        try:
            # Check if rule conditions are met
            if not self._check_conditions(input_data):
                return {
                    'applies': False,
                    'result': None,
                    'reason': 'Conditions not met'
                }
            
            # Perform calculation based on method
            if self.calculation_method == CalculationMethod.FORMULA.value:
                result = self._calculate_by_formula(input_data)
            elif self.calculation_method == CalculationMethod.LOOKUP_TABLE.value:
                result = self._calculate_by_lookup(input_data)
            elif self.calculation_method == CalculationMethod.PERCENTAGE.value:
                result = self._calculate_by_percentage(input_data)
            elif self.calculation_method == CalculationMethod.FIXED_AMOUNT.value:
                result = self._calculate_fixed_amount(input_data)
            else:
                result = self._calculate_default(input_data)
            
            return {
                'applies': True,
                'result': result,
                'method': self.calculation_method,
                'rule_code': self.rule_code,
                'metadata': self._get_calculation_metadata(input_data)
            }
            
        except Exception as e:
            return {
                'applies': False,
                'result': None,
                'error': str(e),
                'rule_code': self.rule_code
            }
    
    def _check_conditions(self, input_data: Dict[str, Any]) -> bool:
        """Check if all conditions for rule application are met"""
        
        # Check trigger conditions
        if self.trigger_conditions:
            if not self._evaluate_conditions(self.trigger_conditions, input_data):
                return False
        
        # Check exclusion conditions
        if self.exclusion_conditions:
            if self._evaluate_conditions(self.exclusion_conditions, input_data):
                return False  # Excluded
        
        # Check effective date conditions
        if self.effective_conditions:
            if not self._evaluate_conditions(self.effective_conditions, input_data):
                return False
        
        return True
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], input_data: Dict[str, Any]) -> bool:
        """Evaluate a set of conditions against input data"""
        for field, condition in conditions.items():
            if field not in input_data:
                return False
            
            value = input_data[field]
            
            if isinstance(condition, dict):
                # Range or complex condition
                if 'min' in condition and value < condition['min']:
                    return False
                if 'max' in condition and value > condition['max']:
                    return False
                if 'equals' in condition and value != condition['equals']:
                    return False
                if 'in' in condition and value not in condition['in']:
                    return False
            else:
                # Simple equality check
                if value != condition:
                    return False
        
        return True
    
    def _calculate_by_formula(self, input_data: Dict[str, Any]) -> Decimal:
        """Calculate result using formula"""
        # This would implement a formula parser/evaluator
        # For now, returning a placeholder
        return Decimal('0')
    
    def _calculate_by_lookup(self, input_data: Dict[str, Any]) -> Decimal:
        """Calculate result using lookup table"""
        if not self.lookup_table_data:
            return Decimal('0')
        
        # Example: Age-based lookup
        if 'age_brackets' in self.lookup_table_data:
            age = input_data.get('age', 0)
            for bracket in self.lookup_table_data['age_brackets']:
                if bracket['min_age'] <= age <= bracket['max_age']:
                    return Decimal(str(bracket.get('rate', 0)))
        
        return Decimal('0')
    
    def _calculate_by_percentage(self, input_data: Dict[str, Any]) -> Decimal:
        """Calculate result as percentage of base amount"""
        base_amount = Decimal(str(input_data.get('service_cost', 0)))
        rate = Decimal(str(self.percentage_rate or 0))
        
        result = base_amount * rate
        
        # Apply min/max limits
        if self.minimum_amount:
            result = max(result, Decimal(str(self.minimum_amount)))
        if self.maximum_amount:
            result = min(result, Decimal(str(self.maximum_amount)))
        
        return result
    
    def _calculate_fixed_amount(self, input_data: Dict[str, Any]) -> Decimal:
        """Return fixed amount"""
        is_in_network = input_data.get('is_in_network', True)
        
        if is_in_network and self.in_network_amount:
            return Decimal(str(self.in_network_amount))
        elif not is_in_network and self.out_of_network_amount:
            return Decimal(str(self.out_of_network_amount))
        elif self.base_amount:
            return Decimal(str(self.base_amount))
        
        return Decimal('0')
    
    def _calculate_default(self, input_data: Dict[str, Any]) -> Decimal:
        """Default calculation method"""
        return Decimal('0')
    
    def _get_calculation_metadata(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata about the calculation"""
        return {
            'rule_name': self.rule_name,
            'rule_type': self.rule_type,
            'calculation_method': self.calculation_method,
            'priority': self.priority_order,
            'currency': self.currency_code,
            'precision': self.decimal_precision
        }
    
    def is_effective_for_date(self, check_date: datetime = None) -> bool:
        """Check if rule is effective for a specific date"""
        if not check_date:
            check_date = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if self.effective_from and check_date < self.effective_from:
            return False
        
        if self.effective_to and check_date > self.effective_to:
            return False
        
        return True
    
    def get_dependencies(self) -> List[UUID]:
        """Get list of rule IDs this rule depends on"""
        if self.depends_on_rules:
            return [UUID(rule_id) for rule_id in self.depends_on_rules]
        return []
    
    def __repr__(self):
        return f"<BenefitCalculationRule(id={self.id}, code='{self.rule_code}', type='{self.rule_type}')>"