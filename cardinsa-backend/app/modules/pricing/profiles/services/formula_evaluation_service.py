# app/modules/pricing/profiles/services/formula_evaluation_service.py

"""
Formula Evaluation Service for Pricing Profiles
Handles parsing and evaluation of risk formulas and pricing expressions.
"""

import re
import ast
import operator
from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.exceptions import ValidationError, BusinessLogicError


logger = get_logger(__name__)


class FormulaEvaluationService:
    """
    Service for evaluating pricing formulas and expressions.
    Supports safe mathematical expressions with variables.
    """
    
    # Supported operators for formula evaluation
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Supported functions
    SAFE_FUNCTIONS = {
        'abs': abs,
        'min': min,
        'max': max,
        'round': round,
        'pow': pow,
    }
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def evaluate_formula(
        self,
        formula: str,
        variables: Dict[str, Union[int, float, Decimal]] = None,
        context: Dict[str, Any] = None
    ) -> Decimal:
        """
        Safely evaluate a mathematical formula with variables.
        
        Args:
            formula: The formula string to evaluate
            variables: Dictionary of variable values
            context: Additional context for evaluation
            
        Returns:
            Decimal result of the formula evaluation
            
        Raises:
            ValidationError: If formula is invalid or unsafe
            BusinessLogicError: If evaluation fails
        """
        try:
            if not formula or not formula.strip():
                return Decimal('0')
            
            # Clean and validate the formula
            cleaned_formula = self._clean_formula(formula)
            self._validate_formula_safety(cleaned_formula)
            
            # Prepare variables
            eval_vars = self._prepare_variables(variables or {})
            
            # Parse and evaluate
            parsed = ast.parse(cleaned_formula, mode='eval')
            result = self._eval_ast_node(parsed.body, eval_vars)
            
            # Convert to Decimal and validate result
            decimal_result = Decimal(str(result))
            self._validate_result(decimal_result, context or {})
            
            logger.debug(f"Formula '{formula}' evaluated to {decimal_result}")
            return decimal_result
            
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.error(f"Formula evaluation error: {str(e)}")
            raise BusinessLogicError(f"Formula evaluation failed: {str(e)}")
        except SyntaxError as e:
            logger.error(f"Formula syntax error: {str(e)}")
            raise ValidationError(f"Invalid formula syntax: {str(e)}")
    
    def validate_formula(self, formula: str) -> Dict[str, Any]:
        """
        Validate a formula without evaluating it.
        
        Args:
            formula: The formula string to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'variables_found': [],
            'complexity_score': 0
        }
        
        try:
            if not formula or not formula.strip():
                result['errors'].append("Formula cannot be empty")
                return result
            
            # Clean the formula
            cleaned_formula = self._clean_formula(formula)
            
            # Check syntax
            try:
                parsed = ast.parse(cleaned_formula, mode='eval')
            except SyntaxError as e:
                result['errors'].append(f"Syntax error: {str(e)}")
                return result
            
            # Check for unsafe operations
            safety_check = self._check_formula_safety(parsed)
            if not safety_check['is_safe']:
                result['errors'].extend(safety_check['errors'])
                return result
            
            # Extract variables
            variables = self._extract_variables(parsed)
            result['variables_found'] = list(variables)
            
            # Calculate complexity
            result['complexity_score'] = self._calculate_complexity(parsed)
            
            # Add warnings for high complexity
            if result['complexity_score'] > 10:
                result['warnings'].append("Formula is highly complex and may impact performance")
            
            result['is_valid'] = True
            
        except Exception as e:
            result['errors'].append(f"Unexpected error: {str(e)}")
        
        return result
    
    def get_formula_variables(self, formula: str) -> List[str]:
        """
        Extract variable names from a formula.
        
        Args:
            formula: The formula string
            
        Returns:
            List of variable names found in the formula
        """
        try:
            cleaned_formula = self._clean_formula(formula)
            parsed = ast.parse(cleaned_formula, mode='eval')
            variables = self._extract_variables(parsed)
            return list(variables)
        except Exception as e:
            logger.error(f"Error extracting variables from formula: {str(e)}")
            return []
    
    def test_formula(
        self,
        formula: str,
        test_cases: List[Dict[str, Union[int, float, Decimal]]]
    ) -> List[Dict[str, Any]]:
        """
        Test a formula with multiple test cases.
        
        Args:
            formula: The formula to test
            test_cases: List of variable dictionaries to test
            
        Returns:
            List of test results
        """
        results = []
        
        for i, test_case in enumerate(test_cases):
            result = {
                'test_case': i + 1,
                'variables': test_case,
                'success': False,
                'result': None,
                'error': None
            }
            
            try:
                evaluated_result = self.evaluate_formula(formula, test_case)
                result['success'] = True
                result['result'] = float(evaluated_result)
            except Exception as e:
                result['error'] = str(e)
            
            results.append(result)
        
        return results
    
    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    def _clean_formula(self, formula: str) -> str:
        """Clean and normalize the formula string."""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', formula.strip())
        
        # Replace common math symbols
        replacements = {
            '×': '*',
            '÷': '/',
            '^': '**',
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned
    
    def _validate_formula_safety(self, formula: str) -> None:
        """Validate that the formula is safe to evaluate."""
        # Check for dangerous patterns
        dangerous_patterns = [
            r'__',  # Double underscore (access to internals)
            r'import',  # Import statements
            r'exec',  # Code execution
            r'eval',  # Dynamic evaluation
            r'open',  # File operations
            r'file',  # File operations
            r'input',  # User input
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, formula, re.IGNORECASE):
                raise ValidationError(f"Formula contains unsafe pattern: {pattern}")
    
    def _check_formula_safety(self, parsed_ast: ast.AST) -> Dict[str, Any]:
        """Check if the parsed AST is safe for evaluation."""
        result = {'is_safe': True, 'errors': []}
        
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                result['is_safe'] = False
                result['errors'].append("Import statements are not allowed")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name not in self.SAFE_FUNCTIONS:
                        result['is_safe'] = False
                        result['errors'].append(f"Function '{func_name}' is not allowed")
                else:
                    result['is_safe'] = False
                    result['errors'].append("Complex function calls are not allowed")
            elif isinstance(node, ast.Attribute):
                result['is_safe'] = False
                result['errors'].append("Attribute access is not allowed")
        
        return result
    
    def _prepare_variables(self, variables: Dict[str, Union[int, float, Decimal]]) -> Dict[str, float]:
        """Prepare variables for evaluation."""
        eval_vars = {}
        
        for name, value in variables.items():
            if isinstance(value, Decimal):
                eval_vars[name] = float(value)
            elif isinstance(value, (int, float)):
                eval_vars[name] = float(value)
            else:
                try:
                    eval_vars[name] = float(value)
                except (ValueError, TypeError):
                    raise ValidationError(f"Variable '{name}' must be numeric, got {type(value)}")
        
        # Add safe functions
        eval_vars.update(self.SAFE_FUNCTIONS)
        
        return eval_vars
    
    def _eval_ast_node(self, node: ast.AST, variables: Dict[str, float]) -> float:
        """Safely evaluate an AST node."""
        if isinstance(node, ast.Constant):  # Python 3.8+
            return float(node.value)
        elif isinstance(node, ast.Num):  # Python < 3.8
            return float(node.n)
        elif isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]
            else:
                raise ValidationError(f"Unknown variable: {node.id}")
        elif isinstance(node, ast.BinOp):
            left = self._eval_ast_node(node.left, variables)
            right = self._eval_ast_node(node.right, variables)
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op:
                return op(left, right)
            else:
                raise ValidationError(f"Unsupported operator: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_ast_node(node.operand, variables)
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op:
                return op(operand)
            else:
                raise ValidationError(f"Unsupported unary operator: {type(node.op)}")
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name in self.SAFE_FUNCTIONS:
                args = [self._eval_ast_node(arg, variables) for arg in node.args]
                return self.SAFE_FUNCTIONS[func_name](*args)
            else:
                raise ValidationError(f"Unsupported function: {func_name}")
        else:
            raise ValidationError(f"Unsupported AST node type: {type(node)}")
    
    def _extract_variables(self, parsed_ast: ast.AST) -> set:
        """Extract variable names from the AST."""
        variables = set()
        
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id not in self.SAFE_FUNCTIONS:
                    variables.add(node.id)
        
        return variables
    
    def _calculate_complexity(self, parsed_ast: ast.AST) -> int:
        """Calculate formula complexity score."""
        complexity = 0
        
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.BinOp):
                complexity += 1
            elif isinstance(node, ast.Call):
                complexity += 2
            elif isinstance(node, ast.UnaryOp):
                complexity += 1
        
        return complexity
    
    def _validate_result(self, result: Decimal, context: Dict[str, Any]) -> None:
        """Validate the evaluation result."""
        if result.is_nan():
            raise BusinessLogicError("Formula evaluation resulted in NaN")
        
        if result.is_infinite():
            raise BusinessLogicError("Formula evaluation resulted in infinity")
        
        # Check for reasonable bounds (configurable)
        max_result = context.get('max_result', Decimal('1000000'))
        min_result = context.get('min_result', Decimal('-1000000'))
        
        if result > max_result:
            raise BusinessLogicError(f"Formula result {result} exceeds maximum allowed value {max_result}")
        
        if result < min_result:
            raise BusinessLogicError(f"Formula result {result} is below minimum allowed value {min_result}")


# Convenience functions
def evaluate_risk_formula(formula: str, variables: Dict[str, Any]) -> Decimal:
    """Convenience function to evaluate a risk formula."""
    service = FormulaEvaluationService()
    return service.evaluate_formula(formula, variables)


def validate_risk_formula(formula: str) -> Dict[str, Any]:
    """Convenience function to validate a risk formula."""
    service = FormulaEvaluationService()
    return service.validate_formula(formula)