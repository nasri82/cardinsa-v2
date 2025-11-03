
"""
app/modules/benefits/repositories/benefit_preapproval_rule_repository.py

Repository for managing prior authorization and preapproval rules.
Handles complex approval workflows and authorization requirements.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.modules.pricing.benefits.models.benefit_preapproval_rule_model import BenefitPreapprovalRule
from app.core.base_repository import BaseRepository
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BenefitPreapprovalRuleRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """Repository for managing preapproval rules"""
    
    def __init__(self, db: Session):
        super().__init__(BenefitPreapprovalRule, db)
    
    async def get_by_benefit_type(self, benefit_type_id: str) -> List[BenefitPreapprovalRule]:
        """Get preapproval rules for a benefit type"""
        try:
            return self.db.query(BenefitPreapprovalRule).filter(
                and_(
                    BenefitPreapprovalRule.benefit_type_id == benefit_type_id,
                    BenefitPreapprovalRule.is_active == True
                )
            ).order_by(BenefitPreapprovalRule.priority, BenefitPreapprovalRule.rule_name).all()
        except Exception as e:
            logger.error(f"Error fetching preapproval rules: {str(e)}")
            raise
    
    async def get_by_approval_type(self, approval_type: str) -> List[BenefitPreapprovalRule]:
        """Get rules by approval type (prior_auth, referral, etc.)"""
        try:
            return self.db.query(BenefitPreapprovalRule).filter(
                and_(
                    BenefitPreapprovalRule.approval_type == approval_type,
                    BenefitPreapprovalRule.is_active == True
                )
            ).order_by(BenefitPreapprovalRule.priority).all()
        except Exception as e:
            logger.error(f"Error fetching rules by approval type: {str(e)}")
            raise
    
    async def get_required_approvals(self, benefit_type_id: str, 
                                   amount: Optional[Decimal] = None) -> List[BenefitPreapprovalRule]:
        """Get rules that require approval based on criteria"""
        try:
            query = self.db.query(BenefitPreapprovalRule).filter(
                and_(
                    BenefitPreapprovalRule.benefit_type_id == benefit_type_id,
                    BenefitPreapprovalRule.requires_approval == True,
                    BenefitPreapprovalRule.is_active == True
                )
            )
            
            if amount is not None:
                query = query.filter(
                    or_(
                        BenefitPreapprovalRule.threshold_amount.is_(None),
                        BenefitPreapprovalRule.threshold_amount <= amount
                    )
                )
            
            return query.order_by(BenefitPreapprovalRule.priority).all()
        except Exception as e:
            logger.error(f"Error fetching required approvals: {str(e)}")
            raise
    
    async def check_approval_required(self, benefit_type_id: str, 
                                    context: Dict[str, Any]) -> bool:
        """Check if approval is required for given context"""
        try:
            rules = await self.get_required_approvals(benefit_type_id)
            
            for rule in rules:
                if self._evaluate_approval_conditions(rule, context):
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking approval required: {str(e)}")
            raise
    
    def _evaluate_approval_conditions(self, rule: BenefitPreapprovalRule, 
                                    context: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions are met"""
        try:
            # Check amount threshold
            if rule.threshold_amount and 'amount' in context:
                if context['amount'] < rule.threshold_amount:
                    return False
            
            # Check other conditions
            if rule.approval_conditions:
                for key, expected_value in rule.approval_conditions.items():
                    if key not in context or context[key] != expected_value:
                        return False
            
            return True
        except Exception:
            return False
    
    async def get_by_coverage(self, coverage_id: str) -> List[BenefitPreapprovalRule]:
        """Get preapproval rules specific to coverage"""
        try:
            return self.db.query(BenefitPreapprovalRule).filter(
                and_(
                    BenefitPreapprovalRule.coverage_id == coverage_id,
                    BenefitPreapprovalRule.is_active == True
                )
            ).order_by(BenefitPreapprovalRule.priority).all()
        except Exception as e:
            logger.error(f"Error fetching rules by coverage: {str(e)}")
            raise
