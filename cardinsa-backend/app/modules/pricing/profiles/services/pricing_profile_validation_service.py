# app/modules/pricing/profiles/services/pricing_profile_validation_service.py
from typing import List, Dict, Any, Optional, Union, Tuple
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import re
import json
import ast
import operator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.pricing.profiles.repositories.quotation_pricing_profile_repository import QuotationPricingProfileRepository
from app.modules.pricing.profiles.repositories.quotation_pricing_profile_rule_repository import QuotationPricingProfileRuleRepository
from app.modules.pricing.profiles.models.quotation_pricing_profile_model import QuotationPricingProfile
from app.core.exceptions import ValidationError, BusinessLogicError
from app.core.logging import get_logger


logger = get_logger(__name__)


class PricingProfileValidationService:
    """
    Comprehensive validation service for pricing profiles.
    Handles business rule validation, data integrity checks, and formula validation.
    """
    
    # Supported currencies (ISO 4217)
    VALID_CURRENCIES = {
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD',
        'MXN', 'SGD', 'HKD', 'NOK', 'KRW', 'TRY', 'RUB', 'INR', 'BRL', 'ZAR',
        'AED', 'SAR', 'QAR', 'KWD', 'BHD', 'OMR', 'JOD', 'LBP', 'EGP', 'MAD'
    }
    
    # Supported insurance types
    VALID_INSURANCE_TYPES = {
        'MEDICAL', 'MOTOR', 'LIFE', 'PROPERTY', 'TRAVEL', 'MARINE', 'GENERAL'
    }
    
    # Mathematical operators allowed in formulas
    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Allowed functions in formulas
    ALLOWED_FUNCTIONS = {
        'abs', 'min', 'max', 'round', 'sum', 'avg', 'sqrt', 'log', 'exp'
    }
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.profile_repo = QuotationPricingProfileRepository(self.db)
        self.profile_rule_repo = QuotationPricingProfileRuleRepository(self.db)
    
    # ============================================================================
    # PROFILE VALIDATION METHODS
    # ============================================================================
    
    def validate_profile_create(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation for profile creation.
        
        Args:
            profile_data: Profile data to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'field_validations': {}
            }
            
            # Validate required fields
            self._validate_required_fields(profile_data, validation_result)
            
            # Validate field formats and constraints
            self._validate_field_formats(profile_data, validation_result)
            
            # Validate business rules
            self._validate_business_rules(profile_data, validation_result)
            
            # Validate risk formula if provided
            if profile_data.get('risk_formula'):
                formula_validation = self.validate_risk_formula(profile_data['risk_formula'])
                if not formula_validation['is_valid']:
                    validation_result['errors'].extend(formula_validation['errors'])
                    validation_result['field_validations']['risk_formula'] = formula_validation
            
            # Check for duplicate code
            if profile_data.get('code'):
                if self._check_duplicate_code(profile_data['code']):
                    validation_result['errors'].append(f"Profile code '{profile_data['code']}' already exists")
                    validation_result['field_validations']['code'] = {
                        'is_valid': False,
                        'error': 'Duplicate code'
                    }
            
            # Final validation status
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
            logger.info(f"Profile validation completed: {'PASSED' if validation_result['is_valid'] else 'FAILED'}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating profile data: {str(e)}")
            raise ValidationError(f"Validation error: {str(e)}")
    
    def validate_profile_update(
        self, 
        profile_id: UUID, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate profile update data.
        
        Args:
            profile_id: ID of the profile being updated
            update_data: Data to update
            
        Returns:
            Dictionary with validation results
        """
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'field_validations': {},
                'impact_analysis': {}
            }
            
            # Get existing profile
            existing_profile = self.profile_repo.get_by_id(profile_id)
            if not existing_profile:
                validation_result['errors'].append(f"Profile {profile_id} not found")
                validation_result['is_valid'] = False
                return validation_result
            
            # Validate only fields being updated
            self._validate_update_fields(update_data, existing_profile, validation_result)
            
            # Analyze impact of changes
            self._analyze_update_impact(update_data, existing_profile, validation_result)
            
            # Check for duplicate code (if code is being updated)
            if 'code' in update_data and update_data['code'] != existing_profile.code:
                if self._check_duplicate_code(update_data['code'], exclude_id=profile_id):
                    validation_result['errors'].append(f"Profile code '{update_data['code']}' already exists")
                    validation_result['field_validations']['code'] = {
                        'is_valid': False,
                        'error': 'Duplicate code'
                    }
            
            # Final validation status
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating profile update: {str(e)}")
            raise ValidationError(f"Update validation error: {str(e)}")
    
    def validate_profile_deletion(self, profile_id: UUID) -> Dict[str, Any]:
        """
        Validate if a profile can be safely deleted.
        
        Args:
            profile_id: ID of the profile to delete
            
        Returns:
            Dictionary with deletion validation results
        """
        try:
            validation_result = {
                'can_delete': True,
                'deletion_impact': {},
                'warnings': [],
                'dependencies': []
            }
            
            # Check if profile exists
            profile = self.profile_repo.get_by_id(profile_id)
            if not profile:
                validation_result['can_delete'] = False
                validation_result['warnings'].append("Profile not found")
                return validation_result
            
            # Check for active quotations using this profile
            # TODO: Implement when quotation module is available
            quotation_usage = self._check_quotation_usage(profile_id)
            if quotation_usage['active_count'] > 0:
                validation_result['can_delete'] = False
                validation_result['dependencies'].append({
                    'type': 'active_quotations',
                    'count': quotation_usage['active_count'],
                    'description': f"Profile is used in {quotation_usage['active_count']} active quotations"
                })
            
            # Check for recent usage
            if quotation_usage['recent_count'] > 0:
                validation_result['warnings'].append(
                    f"Profile was used in {quotation_usage['recent_count']} quotations in the last 30 days"
                )
            
            # Check associated rules
            profile_rules = self.profile_rule_repo.get_by_profile_id(profile_id)
            if profile_rules:
                validation_result['deletion_impact']['rules_affected'] = len(profile_rules)
                validation_result['warnings'].append(
                    f"Deletion will remove {len(profile_rules)} rule associations"
                )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating profile deletion: {str(e)}")
            raise ValidationError(f"Deletion validation error: {str(e)}")
    
    # ============================================================================
    # RISK FORMULA VALIDATION
    # ============================================================================
    
    def validate_risk_formula(self, formula: str) -> Dict[str, Any]:
        """
        Comprehensive validation of risk formulas.
        
        Args:
            formula: Formula string to validate
            
        Returns:
            Dictionary with formula validation results
        """
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'formula_analysis': {},
                'variables_found': [],
                'functions_used': []
            }
            
            if not formula or not formula.strip():
                validation_result['errors'].append("Formula cannot be empty")
                validation_result['is_valid'] = False
                return validation_result
            
            # Basic syntax validation
            self._validate_formula_syntax(formula, validation_result)
            
            # Security validation
            self._validate_formula_security(formula, validation_result)
            
            # Parse and analyze formula
            if validation_result['is_valid']:
                self._analyze_formula_structure(formula, validation_result)
            
            # Validate variables and functions
            self._validate_formula_components(validation_result)
            
            # Test formula execution
            if validation_result['is_valid']:
                self._test_formula_execution(formula, validation_result)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating formula: {str(e)}")
            return {
                'is_valid': False,
                'errors': [f"Formula validation error: {str(e)}"],
                'warnings': [],
                'formula_analysis': {},
                'variables_found': [],
                'functions_used': []
            }
    
    def _validate_formula_syntax(self, formula: str, validation_result: Dict[str, Any]) -> None:
        """Validate basic formula syntax."""
        try:
            # Try to parse the formula as Python expression
            parsed = ast.parse(formula, mode='eval')
            validation_result['formula_analysis']['ast_valid'] = True
        except SyntaxError as e:
            validation_result['errors'].append(f"Formula syntax error: {str(e)}")
            validation_result['is_valid'] = False
            validation_result['formula_analysis']['ast_valid'] = False
    
    def _validate_formula_security(self, formula: str, validation_result: Dict[str, Any]) -> None:
        """Validate formula for security issues."""
        # Check for dangerous keywords
        dangerous_keywords = [
            'import', 'exec', 'eval', 'compile', 'open', 'file', '__',
            'globals', 'locals', 'vars', 'dir', 'getattr', 'setattr',
            'delattr', 'hasattr', 'callable', 'isinstance', 'issubclass'
        ]
        
        formula_lower = formula.lower()
        for keyword in dangerous_keywords:
            if keyword in formula_lower:
                validation_result['errors'].append(f"Forbidden keyword in formula: {keyword}")
                validation_result['is_valid'] = False
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'__\w+__',  # Dunder methods
            r'\.\w*import',  # Import statements
            r'lambda\s',  # Lambda functions
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, formula, re.IGNORECASE):
                validation_result['errors'].append(f"Dangerous pattern detected in formula")
                validation_result['is_valid'] = False
    
    def _analyze_formula_structure(self, formula: str, validation_result: Dict[str, Any]) -> None:
        """Analyze the structure of the formula."""
        try:
            parsed = ast.parse(formula, mode='eval')
            
            # Extract variables and functions
            visitor = FormulaVisitor()
            visitor.visit(parsed)
            
            validation_result['variables_found'] = visitor.variables
            validation_result['functions_used'] = visitor.functions
            validation_result['formula_analysis']['complexity'] = visitor.complexity
            validation_result['formula_analysis']['depth'] = visitor.max_depth
            
        except Exception as e:
            validation_result['warnings'].append(f"Could not analyze formula structure: {str(e)}")
    
    def _validate_formula_components(self, validation_result: Dict[str, Any]) -> None:
        """Validate variables and functions used in formula."""
        # Validate functions
        for func in validation_result['functions_used']:
            if func not in self.ALLOWED_FUNCTIONS:
                validation_result['errors'].append(f"Function '{func}' is not allowed in formulas")
                validation_result['is_valid'] = False
        
        # Validate variables (should be valid field names)
        valid_variables = {
            'base_premium', 'age', 'sum_insured', 'deductible', 'copay_percentage',
            'network_discount', 'benefit_value', 'risk_score', 'industry_factor',
            'regional_factor', 'claims_history', 'coverage_level'
        }
        
        for var in validation_result['variables_found']:
            if var not in valid_variables:
                validation_result['warnings'].append(f"Variable '{var}' may not be available during calculation")
    
    def _test_formula_execution(self, formula: str, validation_result: Dict[str, Any]) -> None:
        """Test formula execution with sample data."""
        try:
            # Create sample data for testing
            test_data = {
                'base_premium': 1000.0,
                'age': 35,
                'sum_insured': 50000.0,
                'deductible': 500.0,
                'copay_percentage': 0.2,
                'network_discount': 0.1,
                'benefit_value': 10000.0,
                'risk_score': 0.5,
                'industry_factor': 1.2,
                'regional_factor': 1.1,
                'claims_history': 0.8,
                'coverage_level': 1.0
            }
            
            # Create safe environment for evaluation
            safe_dict = {
                "__builtins__": {},
                **{name: func for name, func in vars(__builtins__).items() 
                   if name in self.ALLOWED_FUNCTIONS}
            }
            safe_dict.update(test_data)
            
            # Test formula execution
            result = eval(formula, safe_dict)
            
            # Validate result
            if not isinstance(result, (int, float, Decimal)):
                validation_result['errors'].append("Formula must return a numeric value")
                validation_result['is_valid'] = False
            elif result < 0:
                validation_result['warnings'].append("Formula returns negative value with test data")
            
            validation_result['formula_analysis']['test_result'] = float(result)
            validation_result['formula_analysis']['test_successful'] = True
            
        except Exception as e:
            validation_result['errors'].append(f"Formula execution test failed: {str(e)}")
            validation_result['is_valid'] = False
            validation_result['formula_analysis']['test_successful'] = False
    
    # ============================================================================
    # FIELD VALIDATION METHODS
    # ============================================================================
    
    def _validate_required_fields(self, data: Dict[str, Any], validation_result: Dict[str, Any]) -> None:
        """Validate required fields."""
        required_fields = ['name']
        
        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == '':
                validation_result['errors'].append(f"Field '{field}' is required")
                validation_result['field_validations'][field] = {
                    'is_valid': False,
                    'error': 'Required field missing'
                }
    
    def _validate_field_formats(self, data: Dict[str, Any], validation_result: Dict[str, Any]) -> None:
        """Validate field formats and constraints."""
        # Name validation
        if 'name' in data and data['name']:
            if len(data['name']) > 255:
                validation_result['errors'].append("Profile name cannot exceed 255 characters")
                validation_result['field_validations']['name'] = {
                    'is_valid': False,
                    'error': 'Name too long'
                }
        
        # Code validation
        if 'code' in data and data['code']:
            if len(data['code']) > 50:
                validation_result['errors'].append("Profile code cannot exceed 50 characters")
                validation_result['field_validations']['code'] = {
                    'is_valid': False,
                    'error': 'Code too long'
                }
            
            # Code format validation (alphanumeric and underscores only)
            if not re.match(r'^[A-Za-z0-9_]+$', data['code']):
                validation_result['errors'].append("Profile code can only contain letters, numbers, and underscores")
                validation_result['field_validations']['code'] = {
                    'is_valid': False,
                    'error': 'Invalid code format'
                }
        
        # Currency validation
        if 'currency' in data and data['currency']:
            if data['currency'] not in self.VALID_CURRENCIES:
                validation_result['errors'].append(f"Invalid currency code: {data['currency']}")
                validation_result['field_validations']['currency'] = {
                    'is_valid': False,
                    'error': 'Invalid currency'
                }
        
        # Insurance type validation
        if 'insurance_type' in data and data['insurance_type']:
            if data['insurance_type'].upper() not in self.VALID_INSURANCE_TYPES:
                validation_result['warnings'].append(f"Unusual insurance type: {data['insurance_type']}")
                validation_result['field_validations']['insurance_type'] = {
                    'is_valid': True,
                    'warning': 'Non-standard insurance type'
                }
        
        # Premium boundary validation
        if 'min_premium' in data and data['min_premium'] is not None:
            if data['min_premium'] < 0:
                validation_result['errors'].append("Minimum premium cannot be negative")
                validation_result['field_validations']['min_premium'] = {
                    'is_valid': False,
                    'error': 'Cannot be negative'
                }
        
        if 'max_premium' in data and data['max_premium'] is not None:
            if data['max_premium'] < 0:
                validation_result['errors'].append("Maximum premium cannot be negative")
                validation_result['field_validations']['max_premium'] = {
                    'is_valid': False,
                    'error': 'Cannot be negative'
                }
        
        # Factor validations
        factor_fields = ['benefit_exposure_factor', 'network_cost_factor']
        for field in factor_fields:
            if field in data and data[field] is not None:
                if data[field] <= 0:
                    validation_result['errors'].append(f"{field.replace('_', ' ').title()} must be positive")
                    validation_result['field_validations'][field] = {
                        'is_valid': False,
                        'error': 'Must be positive'
                    }
                elif data[field] > 10:
                    validation_result['warnings'].append(f"{field.replace('_', ' ').title()} is unusually high: {data[field]}")
                    validation_result['field_validations'][field] = {
                        'is_valid': True,
                        'warning': 'Unusually high value'
                    }
    
    def _validate_business_rules(self, data: Dict[str, Any], validation_result: Dict[str, Any]) -> None:
        """Validate business rules and logical consistency."""
        # Premium boundary consistency
        min_premium = data.get('min_premium')
        max_premium = data.get('max_premium')
        
        if min_premium is not None and max_premium is not None:
            if min_premium >= max_premium:
                validation_result['errors'].append("Minimum premium must be less than maximum premium")
                validation_result['field_validations']['premium_boundaries'] = {
                    'is_valid': False,
                    'error': 'Invalid boundary relationship'
                }
        
        # Benefit exposure consistency
        enable_benefit_exposure = data.get('enable_benefit_exposure', False)
        benefit_exposure_factor = data.get('benefit_exposure_factor')
        
        if enable_benefit_exposure and benefit_exposure_factor is None:
            validation_result['warnings'].append("Benefit exposure is enabled but no factor is specified")
        elif not enable_benefit_exposure and benefit_exposure_factor is not None:
            validation_result['warnings'].append("Benefit exposure factor specified but feature is disabled")
        
        # Network cost consistency
        enable_network_costs = data.get('enable_network_costs', False)
        network_cost_factor = data.get('network_cost_factor')
        
        if enable_network_costs and network_cost_factor is None:
            validation_result['warnings'].append("Network costs are enabled but no factor is specified")
        elif not enable_network_costs and network_cost_factor is not None:
            validation_result['warnings'].append("Network cost factor specified but feature is disabled")
    
    def _validate_update_fields(
        self, 
        update_data: Dict[str, Any], 
        existing_profile: QuotationPricingProfile,
        validation_result: Dict[str, Any]
    ) -> None:
        """Validate fields being updated."""
        # Only validate fields that are being updated
        update_fields = {k: v for k, v in update_data.items() if v is not None}
        
        if update_fields:
            self._validate_field_formats(update_fields, validation_result)
            
            # Merge with existing data for business rule validation
            merged_data = existing_profile.__dict__.copy()
            merged_data.update(update_fields)
            self._validate_business_rules(merged_data, validation_result)
    
    def _analyze_update_impact(
        self, 
        update_data: Dict[str, Any], 
        existing_profile: QuotationPricingProfile,
        validation_result: Dict[str, Any]
    ) -> None:
        """Analyze the impact of profile updates."""
        impact_analysis = {
            'high_impact_changes': [],
            'medium_impact_changes': [],
            'low_impact_changes': []
        }
        
        # High impact changes
        high_impact_fields = ['risk_formula', 'min_premium', 'max_premium', 'insurance_type']
        for field in high_impact_fields:
            if field in update_data and getattr(existing_profile, field) != update_data[field]:
                impact_analysis['high_impact_changes'].append({
                    'field': field,
                    'old_value': getattr(existing_profile, field),
                    'new_value': update_data[field],
                    'impact': 'May significantly affect pricing calculations'
                })
        
        # Medium impact changes
        medium_impact_fields = ['benefit_exposure_factor', 'network_cost_factor', 'currency']
        for field in medium_impact_fields:
            if field in update_data and getattr(existing_profile, field) != update_data[field]:
                impact_analysis['medium_impact_changes'].append({
                    'field': field,
                    'old_value': getattr(existing_profile, field),
                    'new_value': update_data[field],
                    'impact': 'May affect pricing calculations'
                })
        
        # Low impact changes
        low_impact_fields = ['name', 'description', 'code']
        for field in low_impact_fields:
            if field in update_data and getattr(existing_profile, field) != update_data[field]:
                impact_analysis['low_impact_changes'].append({
                    'field': field,
                    'old_value': getattr(existing_profile, field),
                    'new_value': update_data[field],
                    'impact': 'Minimal impact on calculations'
                })
        
        validation_result['impact_analysis'] = impact_analysis
        
        # Add warnings for high impact changes
        if impact_analysis['high_impact_changes']:
            validation_result['warnings'].append(
                f"This update includes {len(impact_analysis['high_impact_changes'])} high-impact changes"
            )
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _check_duplicate_code(self, code: str, exclude_id: UUID = None) -> bool:
        """Check if profile code already exists."""
        existing = self.profile_repo.get_by_code(code)
        if existing and (exclude_id is None or existing.id != exclude_id):
            return True
        return False
    
    def _check_quotation_usage(self, profile_id: UUID) -> Dict[str, int]:
        """Check quotation usage for a profile."""
        # TODO: Implement when quotation module is available
        # This would query quotation tables to find usage
        return {
            'active_count': 0,
            'total_count': 0,
            'recent_count': 0
        }


class FormulaVisitor(ast.NodeVisitor):
    """AST visitor for analyzing formula structure."""
    
    def __init__(self):
        self.variables = []
        self.functions = []
        self.complexity = 0
        self.depth = 0
        self.current_depth = 0
        self.max_depth = 0
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id not in self.variables:
                self.variables.append(node.id)
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id not in self.functions:
                self.functions.append(node.func.id)
        self.complexity += 2
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_BinOp(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_UnaryOp(self, node):
        self.complexity += 1
        self.generic_visit(node)