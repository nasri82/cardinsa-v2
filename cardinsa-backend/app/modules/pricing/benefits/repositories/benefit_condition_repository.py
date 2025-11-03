"""
app/modules/benefits/repositories/benefit_condition_repository.py

Repository for managing benefit eligibility conditions and requirements.
Handles complex eligibility rules, waiting periods, and benefit conditions.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from app.modules.pricing.benefits.models.benefit_condition_model import BenefitCondition
from app.core.base_repository import BaseRepository
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class BenefitConditionRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """Repository for managing benefit conditions"""
    
    def __init__(self, db: Session):
        super().__init__(BenefitCondition, db)
    
    async def get_by_benefit_type(self, benefit_type_id: str) -> List[BenefitCondition]:
        """Get conditions for a benefit type"""
        try:
            return self.db.query(BenefitCondition).filter(
                and_(
                    BenefitCondition.benefit_type_id == benefit_type_id,
                    BenefitCondition.is_active == True
                )
            ).order_by(BenefitCondition.priority, BenefitCondition.condition_name).all()
        except Exception as e:
            logger.error(f"Error fetching conditions by benefit type: {str(e)}")
            raise
    
    async def get_by_condition_type(self, condition_type: str) -> List[BenefitCondition]:
        """Get conditions by type (eligibility, waiting_period, etc.)"""
        try:
            return self.db.query(BenefitCondition).filter(
                and_(
                    BenefitCondition.condition_type == condition_type,
                    BenefitCondition.is_active == True
                )
            ).order_by(BenefitCondition.priority).all()
        except Exception as e:
            logger.error(f"Error fetching conditions by type: {str(e)}")
            raise
    
    async def get_eligibility_conditions(self, benefit_type_id: str) -> List[BenefitCondition]:
        """Get eligibility conditions for benefit type"""
        try:
            return self.db.query(BenefitCondition).filter(
                and_(
                    BenefitCondition.benefit_type_id == benefit_type_id,
                    BenefitCondition.condition_type == "eligibility",
                    BenefitCondition.is_active == True
                )
            ).order_by(BenefitCondition.priority).all()
        except Exception as e:
            logger.error(f"Error fetching eligibility conditions: {str(e)}")
            raise
    
    async def check_eligibility(self, benefit_type_id: str, 
                              member_context: Dict[str, Any]) -> Dict[str, Any]:
        """Check member eligibility against all conditions"""
        try:
            conditions = await self.get_eligibility_conditions(benefit_type_id)
            results = {
                'eligible': True,
                'failed_conditions': [],
                'waiting_periods': [],
                'warnings': []
            }
            
            for condition in conditions:
                evaluation = self._evaluate_condition(condition, member_context)
                
                if not evaluation['passed']:
                    results['eligible'] = False
                    results['failed_conditions'].append({
                        'condition_id': condition.id,
                        'condition_name': condition.condition_name,
                        'reason': evaluation['reason']
                    })
                
                if evaluation.get('waiting_period'):
                    results['waiting_periods'].append(evaluation['waiting_period'])
                
                if evaluation.get('warning'):
                    results['warnings'].append(evaluation['warning'])
            
            return results
        except Exception as e:
            logger.error(f"Error checking eligibility: {str(e)}")
            raise
    
    def _evaluate_condition(self, condition: BenefitCondition, 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single condition against context"""
        try:
            result = {'passed': True, 'reason': None}
            
            # Age condition
            if condition.min_age and 'age' in context:
                if context['age'] < condition.min_age:
                    result['passed'] = False
                    result['reason'] = f"Minimum age {condition.min_age} required"
            
            if condition.max_age and 'age' in context:
                if context['age'] > condition.max_age:
                    result['passed'] = False
                    result['reason'] = f"Maximum age {condition.max_age} exceeded"
            
            # Waiting period
            if condition.waiting_period_days and 'enrollment_date' in context:
                enrollment_date = context['enrollment_date']
                if isinstance(enrollment_date, str):
                    enrollment_date = datetime.fromisoformat(enrollment_date).date()
                
                waiting_end = enrollment_date.replace(
                    day=enrollment_date.day + condition.waiting_period_days
                )
                
                if datetime.utcnow().date() < waiting_end:
                    result['passed'] = False
                    result['reason'] = f"Waiting period until {waiting_end}"
                    result['waiting_period'] = waiting_end
            
            # Custom condition evaluation
            if condition.condition_rules:
                custom_result = self._evaluate_custom_rules(
                    condition.condition_rules, context
                )
                if not custom_result:
                    result['passed'] = False
                    result['reason'] = "Custom condition not met"
            
            return result
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return {'passed': False, 'reason': 'Evaluation error'}
    
    def _evaluate_custom_rules(self, rules: Dict[str, Any], 
                             context: Dict[str, Any]) -> bool:
        """Evaluate custom condition rules"""
        try:
            # Simple rule evaluation - can be enhanced
            for key, expected_value in rules.items():
                if key not in context:
                    return False
                if context[key] != expected_value:
                    return False
            
            return True
        except Exception:
            return False
    
    async def get_by_coverage(self, coverage_id: str) -> List[BenefitCondition]:
        """Get conditions specific to coverage"""
        try:
            return self.db.query(BenefitCondition).filter(
                and_(
                    BenefitCondition.coverage_id == coverage_id,
                    BenefitCondition.is_active == True
                )
            ).order_by(BenefitCondition.priority).all()
        except Exception as e:
            logger.error(f"Error fetching conditions by coverage: {str(e)}")
            raise