# app/modules/pricing/profiles/services/pricing_rules_service.py
from typing import List, Optional, Dict, Any, Union, Tuple
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.modules.pricing.profiles.repositories.quotation_pricing_rule_repository import QuotationPricingRuleRepository
from app.modules.pricing.profiles.repositories.quotation_pricing_profile_rule_repository import QuotationPricingProfileRuleRepository
from app.modules.pricing.profiles.models.quotation_pricing_rule_model import QuotationPricingRule
from app.modules.pricing.profiles.schemas.quotation_pricing_rule_schema import (
    PricingRuleCreate,
    PricingRuleUpdate, 
    PricingRuleResponse,
    RuleEvaluationRequest,
    RuleEvaluationResult
)
from app.core.exceptions import (
    EntityNotFoundError,
    BusinessLogicError,
    ValidationError,
    DatabaseOperationError
)
from app.core.logging import get_logger


logger = get_logger(__name__)


class PricingRulesService:
    """
    Service layer for managing pricing rules with comprehensive business logic.
    Handles rule evaluation, validation, and orchestration.
    """
    
    # Supported operators for rule conditions
    SUPPORTED_OPERATORS = {
        '=': lambda x, y: x == y,
        '>': lambda x, y: x > y,
        '>=': lambda x, y: x >= y,
        '<': lambda x, y: x < y,
        '<=': lambda x, y: x <= y,
        'IN': lambda x, y: x in y if isinstance(y, (list, tuple, set)) else False,
        'BETWEEN': lambda x, y: y[0] <= x <= y[1] if isinstance(y, (list, tuple)) and len(y) == 2 else False
    }
    
    # Supported impact types
    IMPACT_TYPES = {
        'PERCENTAGE': 'percentage',
        'FIXED_AMOUNT': 'fixed_amount', 
        'MULTIPLIER': 'multiplier'
    }
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.rule_repo = QuotationPricingRuleRepository(self.db)
        self.profile_rule_repo = QuotationPricingProfileRuleRepository(self.db)
    
    # ============================================================================
    # RULE MANAGEMENT OPERATIONS
    # ============================================================================
    
    def create_pricing_rule(
        self,
        rule_data: PricingRuleCreate,
        created_by: UUID = None
    ) -> PricingRuleResponse:
        """
        Create a new pricing rule with comprehensive validation.
        
        Args:
            rule_data: Rule creation data
            created_by: ID of the user creating the rule
            
        Returns:
            Created pricing rule
            
        Raises:
            ValidationError: If rule data is invalid
            BusinessLogicError: If business rules are violated
        """
        try:
            logger.info(f"Creating pricing rule: {rule_data.name}")
            
            # Validate rule data
            self._validate_rule_data(rule_data)
            
            # Validate operator and condition value compatibility
            self._validate_operator_condition(rule_data.operator, rule_data.condition_value)
            
            # Validate impact type and value
            self._validate_impact_configuration(rule_data.impact_type, rule_data.impact_value)
            
            # Validate formula if provided
            if rule_data.formula:
                self._validate_rule_formula(rule_data.formula)
            
            # Create the rule
            rule = self.rule_repo.create_rule(
                rule_data=rule_data,
                created_by=created_by
            )
            
            logger.info(f"Successfully created pricing rule: {rule.id}")
            
            return PricingRuleResponse.from_orm(rule)
            
        except Exception as e:
            logger.error(f"Error creating pricing rule: {str(e)}")
            raise
    
    def get_pricing_rule(self, rule_id: UUID) -> Optional[PricingRuleResponse]:
        """
        Get a pricing rule by ID.
        
        Args:
            rule_id: ID of the pricing rule
            
        Returns:
            Pricing rule or None if not found
        """
        try:
            rule = self.rule_repo.get_by_id(rule_id)
            if not rule:
                return None
            
            return PricingRuleResponse.from_orm(rule)
            
        except Exception as e:
            logger.error(f"Error getting pricing rule {rule_id}: {str(e)}")
            raise
    
    def update_pricing_rule(
        self,
        rule_id: UUID,
        rule_data: PricingRuleUpdate,
        updated_by: UUID = None
    ) -> Optional[PricingRuleResponse]:
        """
        Update an existing pricing rule.
        
        Args:
            rule_id: ID of the pricing rule
            rule_data: Updated rule data
            updated_by: ID of the user updating the rule
            
        Returns:
            Updated pricing rule or None if not found
        """
        try:
            logger.info(f"Updating pricing rule: {rule_id}")
            
            # Check if rule exists
            existing_rule = self.rule_repo.get_by_id(rule_id)
            if not existing_rule:
                raise EntityNotFoundError(f"Pricing rule {rule_id} not found")
            
            # Validate update data
            self._validate_rule_update_data(rule_data, existing_rule)
            
            # Check if rule is in use and changes are significant
            if self._requires_impact_analysis(rule_data, existing_rule):
                usage_info = self.check_rule_usage(rule_id)
                if usage_info['is_in_use']:
                    logger.warning(f"Updating rule {rule_id} that is in use in {usage_info['total_profiles']} profiles")
            
            # Create version history if significant changes
            if self._requires_rule_versioning(rule_data, existing_rule):
                self.rule_repo.create_rule_version(
                    rule_id=rule_id,
                    version_reason="Rule update with significant changes",
                    created_by=updated_by
                )
            
            # Update the rule
            updated_rule = self.rule_repo.update_rule(
                rule_id=rule_id,
                rule_data=rule_data,
                updated_by=updated_by
            )
            
            logger.info(f"Successfully updated pricing rule: {rule_id}")
            
            return PricingRuleResponse.from_orm(updated_rule)
            
        except Exception as e:
            logger.error(f"Error updating pricing rule {rule_id}: {str(e)}")
            raise
    
    def delete_pricing_rule(
        self,
        rule_id: UUID,
        updated_by: UUID = None,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a pricing rule (soft delete by default).
        
        Args:
            rule_id: ID of the pricing rule
            updated_by: ID of the user deleting the rule
            hard_delete: Whether to permanently delete
            
        Returns:
            True if successfully deleted
        """
        try:
            logger.info(f"Deleting pricing rule: {rule_id}")
            
            # Check if rule exists
            rule = self.rule_repo.get_by_id(rule_id)
            if not rule:
                raise EntityNotFoundError(f"Pricing rule {rule_id} not found")
            
            # Check if rule is in use
            usage_info = self.check_rule_usage(rule_id)
            if usage_info['is_in_use'] and not hard_delete:
                raise BusinessLogicError(
                    f"Cannot delete rule '{rule.name}' - it is currently in use. "
                    f"Used in {usage_info['total_profiles']} profiles."
                )
            
            # Delete the rule
            success = self.rule_repo.delete_rule(
                rule_id=rule_id,
                updated_by=updated_by,
                hard_delete=hard_delete
            )
            
            if success:
                logger.info(f"Successfully deleted pricing rule: {rule_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting pricing rule {rule_id}: {str(e)}")
            raise
    
    # ============================================================================
    # RULE SEARCH AND FILTERING
    # ============================================================================
    
    def search_pricing_rules(
        self,
        name: str = None,
        field_name: str = None,
        insurance_type: str = None,
        impact_type: str = None,
        operator: str = None,
        is_active: bool = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search pricing rules with various filters.
        
        Args:
            name: Filter by rule name (partial match)
            field_name: Filter by field name
            insurance_type: Filter by insurance type
            impact_type: Filter by impact type
            operator: Filter by operator
            is_active: Filter by active status
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Dictionary with search results and pagination
        """
        try:
            results = self.rule_repo.search_rules(
                name=name,
                field_name=field_name,
                insurance_type=insurance_type,
                impact_type=impact_type,
                operator=operator,
                is_active=is_active,
                limit=limit,
                offset=offset
            )
            
            # Convert to response models
            rules = [PricingRuleResponse.from_orm(rule) for rule in results['rules']]
            
            return {
                'rules': rules,
                'pagination': results['pagination'],
                'filters_applied': results['filters_applied']
            }
            
        except Exception as e:
            logger.error(f"Error searching pricing rules: {str(e)}")
            raise
    
    def get_rules_by_field(
        self,
        field_name: str,
        active_only: bool = True
    ) -> List[PricingRuleResponse]:
        """
        Get all rules that operate on a specific field.
        
        Args:
            field_name: Name of the field
            active_only: Whether to return only active rules
            
        Returns:
            List of pricing rules
        """
        try:
            rules = self.rule_repo.get_by_field_name(
                field_name=field_name,
                active_only=active_only
            )
            
            return [PricingRuleResponse.from_orm(rule) for rule in rules]
            
        except Exception as e:
            logger.error(f"Error getting rules for field {field_name}: {str(e)}")
            raise
    
    def get_rules_by_insurance_type(
        self,
        insurance_type: str,
        active_only: bool = True
    ) -> List[PricingRuleResponse]:
        """
        Get all rules for a specific insurance type.
        
        Args:
            insurance_type: Type of insurance
            active_only: Whether to return only active rules
            
        Returns:
            List of pricing rules
        """
        try:
            rules = self.rule_repo.get_by_insurance_type(
                insurance_type=insurance_type,
                active_only=active_only
            )
            
            return [PricingRuleResponse.from_orm(rule) for rule in rules]
            
        except Exception as e:
            logger.error(f"Error getting rules for insurance type {insurance_type}: {str(e)}")
            raise
    
    # ============================================================================
    # RULE EVALUATION ENGINE
    # ============================================================================
    
    def evaluate_single_rule(
        self,
        rule_id: UUID,
        input_data: Dict[str, Any]
    ) -> RuleEvaluationResult:
        """
        Evaluate a single pricing rule against input data.
        
        Args:
            rule_id: ID of the rule to evaluate
            input_data: Input data for rule evaluation
            
        Returns:
            Rule evaluation result
        """
        try:
            logger.debug(f"Evaluating rule {rule_id}")
            
            # Get the rule
            rule = self.rule_repo.get_by_id(rule_id)
            if not rule:
                raise EntityNotFoundError(f"Pricing rule {rule_id} not found")
            
            if not rule.is_active:
                return RuleEvaluationResult(
                    rule_id=rule_id,
                    rule_name=rule.name,
                    condition_met=False,
                    impact_applied=False,
                    result_value=None,
                    evaluation_details={'error': 'Rule is inactive'}
                )
            
            # Extract field value from input data
            field_value = input_data.get(rule.field_name)
            if field_value is None:
                return RuleEvaluationResult(
                    rule_id=rule_id,
                    rule_name=rule.name,
                    condition_met=False,
                    impact_applied=False,
                    result_value=None,
                    evaluation_details={'error': f'Field {rule.field_name} not found in input data'}
                )
            
            # Evaluate condition
            condition_result = self._evaluate_condition(
                field_value=field_value,
                operator=rule.operator,
                condition_value=rule.condition_value
            )
            
            # Calculate impact if condition is met
            impact_value = None
            if condition_result:
                impact_value = self._calculate_rule_impact(
                    rule=rule,
                    input_data=input_data
                )
            
            evaluation_details = {
                'field_name': rule.field_name,
                'field_value': field_value,
                'operator': rule.operator,
                'condition_value': rule.condition_value,
                'condition_evaluation': condition_result,
                'impact_type': rule.impact_type,
                'impact_value_config': rule.impact_value,
                'calculated_impact': impact_value
            }
            
            return RuleEvaluationResult(
                rule_id=rule_id,
                rule_name=rule.name,
                condition_met=condition_result,
                impact_applied=condition_result,
                result_value=impact_value,
                evaluation_details=evaluation_details
            )
            
        except Exception as e:
            logger.error(f"Error evaluating rule {rule_id}: {str(e)}")
            return RuleEvaluationResult(
                rule_id=rule_id,
                rule_name="Unknown",
                condition_met=False,
                impact_applied=False,
                result_value=None,
                evaluation_details={'error': str(e)}
            )
    
    def evaluate_rule_set(
        self,
        rule_ids: List[UUID],
        input_data: Dict[str, Any],
        evaluation_order: str = 'sequential'
    ) -> Dict[str, Any]:
        """
        Evaluate a set of pricing rules against input data.
        
        Args:
            rule_ids: List of rule IDs to evaluate
            input_data: Input data for rule evaluation
            evaluation_order: Order of evaluation ('sequential', 'parallel')
            
        Returns:
            Dictionary with evaluation results
        """
        try:
            logger.info(f"Evaluating rule set with {len(rule_ids)} rules")
            
            evaluation_results = []
            total_impact = 0.0
            rules_applied = 0
            
            # Evaluate each rule
            for rule_id in rule_ids:
                result = self.evaluate_single_rule(rule_id, input_data)
                evaluation_results.append(result)
                
                if result.impact_applied and result.result_value is not None:
                    total_impact += float(result.result_value)
                    rules_applied += 1
            
            # Calculate summary statistics
            rules_with_conditions_met = sum(1 for r in evaluation_results if r.condition_met)
            
            return {
                'total_rules_evaluated': len(rule_ids),
                'rules_with_conditions_met': rules_with_conditions_met,
                'rules_applied': rules_applied,
                'total_impact': total_impact,
                'average_impact': total_impact / rules_applied if rules_applied > 0 else 0,
                'evaluation_order': evaluation_order,
                'individual_results': evaluation_results,
                'evaluation_timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating rule set: {str(e)}")
            raise
    
    def evaluate_profile_rules(
        self,
        profile_id: UUID,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate all rules associated with a pricing profile.
        
        Args:
            profile_id: ID of the pricing profile
            input_data: Input data for rule evaluation
            
        Returns:
            Dictionary with profile rule evaluation results
        """
        try:
            logger.info(f"Evaluating rules for profile {profile_id}")
            
            # Get profile rules in order
            profile_rules = self.profile_rule_repo.get_profile_rules_ordered(
                profile_id=profile_id,
                active_only=True
            )
            
            if not profile_rules:
                return {
                    'profile_id': str(profile_id),
                    'total_rules': 0,
                    'evaluation_successful': True,
                    'total_impact': 0.0,
                    'rule_results': []
                }
            
            # Extract rule IDs in order
            rule_ids = [UUID(rule_data['rule']['id']) for rule_data in profile_rules]
            
            # Evaluate rules
            evaluation_results = self.evaluate_rule_set(
                rule_ids=rule_ids,
                input_data=input_data,
                evaluation_order='sequential'
            )
            
            # Add profile-specific information
            evaluation_results['profile_id'] = str(profile_id)
            evaluation_results['profile_rule_count'] = len(profile_rules)
            evaluation_results['evaluation_successful'] = True
            
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Error evaluating profile rules: {str(e)}")
            raise
    
    # ============================================================================
    # RULE ANALYSIS AND VALIDATION
    # ============================================================================
    
    def validate_rule_configuration(self, rule_id: UUID) -> Dict[str, Any]:
        """
        Validate the configuration of a pricing rule.
        
        Args:
            rule_id: ID of the pricing rule
            
        Returns:
            Dictionary with validation results
        """
        try:
            rule = self.rule_repo.get_by_id(rule_id)
            if not rule:
                raise EntityNotFoundError(f"Pricing rule {rule_id} not found")
            
            validation_result = {
                'rule_id': str(rule_id),
                'rule_name': rule.name,
                'is_valid': True,
                'issues': [],
                'warnings': [],
                'configuration_analysis': {}
            }
            
            # Validate basic configuration
            if not rule.name or len(rule.name.strip()) == 0:
                validation_result['issues'].append("Rule name is required")
            
            if not rule.field_name:
                validation_result['issues'].append("Field name is required")
            
            if rule.operator not in self.SUPPORTED_OPERATORS:
                validation_result['issues'].append(f"Unsupported operator: {rule.operator}")
            
            if rule.impact_type not in self.IMPACT_TYPES:
                validation_result['issues'].append(f"Invalid impact type: {rule.impact_type}")
            
            # Validate operator-condition compatibility
            try:
                self._validate_operator_condition(rule.operator, rule.condition_value)
            except ValidationError as e:
                validation_result['issues'].append(f"Operator-condition mismatch: {str(e)}")
            
            # Validate impact configuration
            try:
                self._validate_impact_configuration(rule.impact_type, rule.impact_value)
            except ValidationError as e:
                validation_result['issues'].append(f"Invalid impact configuration: {str(e)}")
            
            # Validate formula if present
            if rule.formula:
                try:
                    self._validate_rule_formula(rule.formula)
                    validation_result['configuration_analysis']['has_formula'] = True
                except ValidationError as e:
                    validation_result['issues'].append(f"Invalid formula: {str(e)}")
            
            # Performance analysis
            validation_result['configuration_analysis'].update({
                'complexity_score': self._calculate_rule_complexity(rule),
                'performance_impact': self._assess_performance_impact(rule),
                'field_dependencies': [rule.field_name]
            })
            
            validation_result['is_valid'] = len(validation_result['issues']) == 0
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating rule configuration: {str(e)}")
            raise
    
    def check_rule_usage(self, rule_id: UUID) -> Dict[str, Any]:
        """
        Check how a rule is being used across profiles.
        
        Args:
            rule_id: ID of the pricing rule
            
        Returns:
            Dictionary with usage information
        """
        try:
            return self.profile_rule_repo.check_rule_usage(rule_id)
            
        except Exception as e:
            logger.error(f"Error checking rule usage: {str(e)}")
            raise
    
    def analyze_rule_conflicts(
        self,
        profile_id: UUID = None,
        rule_ids: List[UUID] = None
    ) -> Dict[str, Any]:
        """
        Analyze potential conflicts between rules.
        
        Args:
            profile_id: Profile ID to analyze (optional)
            rule_ids: Specific rule IDs to analyze (optional)
            
        Returns:
            Dictionary with conflict analysis
        """
        try:
            if profile_id:
                # Get rules from profile
                profile_rules = self.profile_rule_repo.get_profile_rules_ordered(profile_id)
                rules_to_analyze = [UUID(rule_data['rule']['id']) for rule_data in profile_rules]
            elif rule_ids:
                rules_to_analyze = rule_ids
            else:
                raise ValidationError("Either profile_id or rule_ids must be provided")
            
            # Get rule details
            rules = [self.rule_repo.get_by_id(rule_id) for rule_id in rules_to_analyze]
            rules = [rule for rule in rules if rule is not None]
            
            conflicts = []
            
            # Check for field conflicts
            field_groups = {}
            for rule in rules:
                if rule.field_name not in field_groups:
                    field_groups[rule.field_name] = []
                field_groups[rule.field_name].append(rule)
            
            for field_name, field_rules in field_groups.items():
                if len(field_rules) > 1:
                    # Analyze rules for the same field
                    field_conflicts = self._analyze_field_rule_conflicts(field_rules)
                    if field_conflicts:
                        conflicts.extend(field_conflicts)
            
            return {
                'total_rules_analyzed': len(rules),
                'conflicts_found': len(conflicts),
                'conflict_details': conflicts,
                'analysis_timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing rule conflicts: {str(e)}")
            raise
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _validate_rule_data(self, rule_data: PricingRuleCreate) -> None:
        """Validate rule creation data."""
        if not rule_data.name or len(rule_data.name.strip()) == 0:
            raise ValidationError("Rule name is required")
        
        if not rule_data.field_name or len(rule_data.field_name.strip()) == 0:
            raise ValidationError("Field name is required")
        
        if rule_data.operator not in self.SUPPORTED_OPERATORS:
            raise ValidationError(f"Unsupported operator: {rule_data.operator}")
        
        if rule_data.impact_type not in self.IMPACT_TYPES:
            raise ValidationError(f"Invalid impact type: {rule_data.impact_type}")
    
    def _validate_rule_update_data(
        self, 
        rule_data: PricingRuleUpdate, 
        existing_rule: QuotationPricingRule
    ) -> None:
        """Validate rule update data."""
        if rule_data.name is not None:
            if not rule_data.name or len(rule_data.name.strip()) == 0:
                raise ValidationError("Rule name cannot be empty")
        
        if rule_data.operator is not None and rule_data.operator not in self.SUPPORTED_OPERATORS:
            raise ValidationError(f"Unsupported operator: {rule_data.operator}")
        
        if rule_data.impact_type is not None and rule_data.impact_type not in self.IMPACT_TYPES:
            raise ValidationError(f"Invalid impact type: {rule_data.impact_type}")
    
    def _validate_operator_condition(self, operator: str, condition_value: Any) -> None:
        """Validate operator and condition value compatibility."""
        if operator in ['IN']:
            if not isinstance(condition_value, (list, tuple, set)):
                raise ValidationError(f"Operator '{operator}' requires a list/array condition value")
        
        elif operator == 'BETWEEN':
            if not isinstance(condition_value, (list, tuple)) or len(condition_value) != 2:
                raise ValidationError("Operator 'BETWEEN' requires exactly 2 values")
        
        elif operator in ['=', '>', '>=', '<', '<=']:
            if isinstance(condition_value, (list, tuple, set)):
                raise ValidationError(f"Operator '{operator}' requires a single value")
    
    def _validate_impact_configuration(self, impact_type: str, impact_value: Any) -> None:
        """Validate impact type and value configuration."""
        if impact_type == 'PERCENTAGE':
            if not isinstance(impact_value, (int, float, Decimal)):
                raise ValidationError("Percentage impact requires numeric value")
            if float(impact_value) < 0 or float(impact_value) > 100:
                raise ValidationError("Percentage impact must be between 0 and 100")
        
        elif impact_type == 'FIXED_AMOUNT':
            if not isinstance(impact_value, (int, float, Decimal)):
                raise ValidationError("Fixed amount impact requires numeric value")
        
        elif impact_type == 'MULTIPLIER':
            if not isinstance(impact_value, (int, float, Decimal)):
                raise ValidationError("Multiplier impact requires numeric value")
            if float(impact_value) <= 0:
                raise ValidationError("Multiplier impact must be positive")
    
    def _validate_rule_formula(self, formula: str) -> None:
        """Validate rule formula syntax and security."""
        if not formula or len(formula.strip()) == 0:
            raise ValidationError("Formula cannot be empty")
        
        # Basic security checks
        forbidden_keywords = ['import', 'exec', 'eval', '__']
        for keyword in forbidden_keywords:
            if keyword in formula.lower():
                raise ValidationError(f"Formula contains forbidden keyword: {keyword}")
    
    def _evaluate_condition(
        self, 
        field_value: Any, 
        operator: str, 
        condition_value: Any
    ) -> bool:
        """Evaluate a rule condition."""
        try:
            if operator not in self.SUPPORTED_OPERATORS:
                return False
            
            return self.SUPPORTED_OPERATORS[operator](field_value, condition_value)
            
        except Exception as e:
            logger.warning(f"Error evaluating condition: {str(e)}")
            return False
    
    def _calculate_rule_impact(
        self, 
        rule: QuotationPricingRule, 
        input_data: Dict[str, Any]
    ) -> float:
        """Calculate the impact value for a rule."""
        try:
            if rule.formula:
                # Use formula if available
                return self._evaluate_formula(rule.formula, input_data)
            else:
                # Use simple impact value
                return float(rule.impact_value)
                
        except Exception as e:
            logger.warning(f"Error calculating rule impact: {str(e)}")
            return 0.0
    
    def _evaluate_formula(self, formula: str, input_data: Dict[str, Any]) -> float:
        """Safely evaluate a formula with input data."""
        try:
            # Create safe environment for evaluation
            safe_dict = {
                "__builtins__": {},
                "abs": abs, "min": min, "max": max, "round": round,
                "sum": sum, "len": len
            }
            safe_dict.update(input_data)
            
            result = eval(formula, safe_dict)
            return float(result)
            
        except Exception as e:
            logger.warning(f"Error evaluating formula '{formula}': {str(e)}")
            return 0.0
    
    def _requires_impact_analysis(
        self, 
        rule_data: PricingRuleUpdate, 
        existing_rule: QuotationPricingRule
    ) -> bool:
        """Check if rule changes require impact analysis."""
        significant_fields = [
            'operator', 'condition_value', 'impact_type', 
            'impact_value', 'formula'
        ]
        
        for field in significant_fields:
            if hasattr(rule_data, field) and getattr(rule_data, field) is not None:
                if getattr(rule_data, field) != getattr(existing_rule, field):
                    return True
        
        return False
    
    def _requires_rule_versioning(
        self, 
        rule_data: PricingRuleUpdate, 
        existing_rule: QuotationPricingRule
    ) -> bool:
        """Check if changes require rule versioning."""
        return self._requires_impact_analysis(rule_data, existing_rule)
    
    def _calculate_rule_complexity(self, rule: QuotationPricingRule) -> int:
        """Calculate complexity score for a rule."""
        complexity = 1  # Base complexity
        
        # Add complexity for operator type
        if rule.operator in ['IN', 'BETWEEN']:
            complexity += 2
        elif rule.operator in ['>', '>=', '<', '<=']:
            complexity += 1
        
        # Add complexity for formula
        if rule.formula:
            complexity += 3
        
        # Add complexity for condition value type
        if isinstance(rule.condition_value, (list, tuple)):
            complexity += len(rule.condition_value)
        
        return complexity
    
    def _assess_performance_impact(self, rule: QuotationPricingRule) -> str:
        """Assess performance impact of a rule."""
        complexity = self._calculate_rule_complexity(rule)
        
        if complexity <= 2:
            return 'LOW'
        elif complexity <= 5:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _analyze_field_rule_conflicts(
        self, 
        field_rules: List[QuotationPricingRule]
    ) -> List[Dict[str, Any]]:
        """Analyze conflicts between rules for the same field."""
        conflicts = []
        
        for i, rule1 in enumerate(field_rules):
            for j, rule2 in enumerate(field_rules[i+1:], i+1):
                # Check for conflicting conditions
                if self._rules_have_conflicting_conditions(rule1, rule2):
                    conflicts.append({
                        'conflict_type': 'overlapping_conditions',
                        'rule1_id': str(rule1.id),
                        'rule1_name': rule1.name,
                        'rule2_id': str(rule2.id),
                        'rule2_name': rule2.name,
                        'field_name': rule1.field_name,
                        'description': f"Rules may have overlapping conditions for field '{rule1.field_name}'"
                    })
        
        return conflicts
    
    def _rules_have_conflicting_conditions(
        self, 
        rule1: QuotationPricingRule, 
        rule2: QuotationPricingRule
    ) -> bool:
        """Check if two rules have potentially conflicting conditions."""
        # Simple conflict detection - can be enhanced
        if rule1.operator == rule2.operator == '=':
            return rule1.condition_value == rule2.condition_value
        
        # Add more sophisticated conflict detection logic here
        return False