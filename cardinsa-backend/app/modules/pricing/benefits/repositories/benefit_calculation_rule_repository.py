# ===============================================================================
# benefit_calculation_rule_repository.py
# ===============================================================================

"""
app/modules/benefits/repositories/benefit_calculation_rule_repository.py

Repository for managing benefit calculation business rules.
Handles formulas, conditions, and complex calculation logic.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, text
from app.modules.pricing.benefits.models.benefit_calculation_rule_model import BenefitCalculationRule
from app.modules.pricing.benefits.models.benefit_calculation_rule_enums import RuleType
from app.core.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class BenefitCalculationRuleRepository(BaseRepository):
    """Repository for managing benefit calculation rules"""
    
    def __init__(self, db: Session):
        super().__init__(BenefitCalculationRule, db)
    
    async def get_by_benefit_type(self, benefit_type_id: str) -> List[BenefitCalculationRule]:
        """Get calculation rules for a benefit type"""
        try:
            return self.db.query(BenefitCalculationRule).filter(
                and_(
                    BenefitCalculationRule.benefit_type_id == benefit_type_id,
                    BenefitCalculationRule.is_active == True
                )
            ).order_by(BenefitCalculationRule.priority_order, BenefitCalculationRule.rule_name).all()
        except Exception as e:
            logger.error(f"Error fetching calculation rules: {str(e)}")
            raise
    
    async def get_by_rule_type(self, rule_type: str) -> List[BenefitCalculationRule]:
        """Get rules by type (copay, coinsurance, deductible, etc.)"""
        try:
            return self.db.query(BenefitCalculationRule).filter(
                and_(
                    BenefitCalculationRule.rule_type == rule_type,
                    BenefitCalculationRule.is_active == True
                )
            ).order_by(BenefitCalculationRule.priority_order).all()
        except Exception as e:
            logger.error(f"Error fetching rules by type: {str(e)}")
            raise
    
    async def get_applicable_rules(self, benefit_type_id: str, 
                                 context: Dict[str, Any]) -> List[BenefitCalculationRule]:
        """Get rules applicable to specific context"""
        try:
            rules = await self.get_by_benefit_type(benefit_type_id)
            applicable_rules = []
            
            for rule in rules:
                if self._evaluate_conditions(rule.trigger_conditions, context):
                    applicable_rules.append(rule)
            
            return sorted(applicable_rules, key=lambda x: x.priority_order)
        except Exception as e:
            logger.error(f"Error fetching applicable rules: {str(e)}")
            raise
    
    def _evaluate_conditions(self, conditions: Optional[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        """Evaluate rule conditions against context"""
        try:
            if not conditions:
                return True
            
            # Simple condition evaluation - can be enhanced
            for key, expected_value in conditions.items():
                if key not in context:
                    return False
                if context[key] != expected_value:
                    return False
            
            return True
        except Exception:
            return False
    
    async def get_by_priority_range(self, min_priority: int, max_priority: int) -> List[BenefitCalculationRule]:
        """Get rules within priority range"""
        try:
            return self.db.query(BenefitCalculationRule).filter(
                and_(
                    BenefitCalculationRule.priority_order >= min_priority,
                    BenefitCalculationRule.priority_order <= max_priority,
                    BenefitCalculationRule.is_active == True
                )
            ).order_by(BenefitCalculationRule.priority_order).all()
        except Exception as e:
            logger.error(f"Error fetching by priority range: {str(e)}")
            raise

    async def get_by_rule_codes(self, rule_codes: List[str]) -> List[BenefitCalculationRule]:
        """Get rules by their codes"""
        try:
            return self.db.query(BenefitCalculationRule).filter(
                BenefitCalculationRule.rule_code.in_(rule_codes)
            ).all()
        except Exception as e:
            logger.error(f"Error fetching rules by codes: {str(e)}")
            raise

    async def get_active_rules(self) -> List[BenefitCalculationRule]:
        """Get all active rules"""
        try:
            return self.db.query(BenefitCalculationRule).filter(
                BenefitCalculationRule.is_active == True
            ).order_by(BenefitCalculationRule.priority_order).all()
        except Exception as e:
            logger.error(f"Error fetching active rules: {str(e)}")
            raise

    async def search_rules(self, search_term: str) -> List[BenefitCalculationRule]:
        """Search rules by name or description"""
        try:
            search_filter = f"%{search_term.lower()}%"
            return self.db.query(BenefitCalculationRule).filter(
                or_(
                    BenefitCalculationRule.rule_name.ilike(search_filter),
                    BenefitCalculationRule.description.ilike(search_filter),
                    BenefitCalculationRule.rule_code.ilike(search_filter)
                )
            ).all()
        except Exception as e:
            logger.error(f"Error searching rules: {str(e)}")
            raise

    async def get_rules_with_formulas(self) -> List[BenefitCalculationRule]:
        """Get all rules that have calculation formulas"""
        try:
            return self.db.query(BenefitCalculationRule).filter(
                and_(
                    BenefitCalculationRule.calculation_formula.isnot(None),
                    BenefitCalculationRule.calculation_formula != ''
                )
            ).all()
        except Exception as e:
            logger.error(f"Error fetching rules with formulas: {str(e)}")
            raise

    async def get_dependent_rules(self, rule_id: str) -> List[BenefitCalculationRule]:
        """Get rules that depend on the specified rule"""
        try:
            return self.db.query(BenefitCalculationRule).filter(
                BenefitCalculationRule.depends_on_rules.contains([rule_id])
            ).all()
        except Exception as e:
            logger.error(f"Error fetching dependent rules: {str(e)}")
            raise

    async def get_child_rules(self, parent_rule_id: str) -> List[BenefitCalculationRule]:
        """Get child rules for a parent rule"""
        try:
            return self.db.query(BenefitCalculationRule).filter(
                BenefitCalculationRule.parent_rule_id == parent_rule_id
            ).order_by(BenefitCalculationRule.execution_sequence).all()
        except Exception as e:
            logger.error(f"Error fetching child rules: {str(e)}")
            raise

    async def count_rules_by_type(self) -> Dict[str, int]:
        """Count rules grouped by type"""
        try:
            result = self.db.query(
                BenefitCalculationRule.rule_type,
                self.db.func.count(BenefitCalculationRule.id)
            ).group_by(BenefitCalculationRule.rule_type).all()
            
            return {rule_type: count for rule_type, count in result}
        except Exception as e:
            logger.error(f"Error counting rules by type: {str(e)}")
            raise

    async def get_rules_by_deployment_stage(self, stage: str) -> List[BenefitCalculationRule]:
        """Get rules by deployment stage"""
        try:
            return self.db.query(BenefitCalculationRule).filter(
                BenefitCalculationRule.deployment_stage == stage
            ).all()
        except Exception as e:
            logger.error(f"Error fetching rules by deployment stage: {str(e)}")
            raise