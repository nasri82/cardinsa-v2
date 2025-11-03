# app/modules/pricing/plans/repositories/plan_eligibility_rule_repository.py
"""
Plan Eligibility Rule Repository

Data access layer for Plan Eligibility Rule operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.modules.pricing.plans.models.plan_eligibility_rule_model import (
    PlanEligibilityRule,
    RuleCategory,
    RuleType,
    RuleSeverity,
    RuleLogic
)
from app.core.exceptions import DatabaseOperationError, EntityNotFoundError
import logging

logger = logging.getLogger(__name__)

class PlanEligibilityRuleRepository:
    """Repository for Plan Eligibility Rule database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        rule_data: Dict[str, Any],
        created_by: Optional[UUID] = None
    ) -> PlanEligibilityRule:
        """Create a new eligibility rule"""
        try:
            rule_data['created_by'] = created_by
            rule_data['created_at'] = datetime.utcnow()
            
            eligibility_rule = PlanEligibilityRule(**rule_data)
            self.db.add(eligibility_rule)
            self.db.commit()
            self.db.refresh(eligibility_rule)
            
            logger.info(f"Created eligibility rule {eligibility_rule.id} for plan {eligibility_rule.plan_id}")
            return eligibility_rule
            
        except IntegrityError:
            self.db.rollback()
            raise DatabaseOperationError("Rule name already exists for this plan")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating eligibility rule: {str(e)}")
            raise DatabaseOperationError(f"Failed to create eligibility rule: {str(e)}")
    
    def bulk_create(
        self,
        rules_data: List[Dict[str, Any]],
        created_by: Optional[UUID] = None
    ) -> List[PlanEligibilityRule]:
        """Bulk create eligibility rules"""
        try:
            eligibility_rules = []
            for rule_data in rules_data:
                rule_data['created_by'] = created_by
                rule_data['created_at'] = datetime.utcnow()
                eligibility_rules.append(PlanEligibilityRule(**rule_data))
            
            self.db.add_all(eligibility_rules)
            self.db.commit()
            
            for rule in eligibility_rules:
                self.db.refresh(rule)
            
            logger.info(f"Bulk created {len(eligibility_rules)} eligibility rules")
            return eligibility_rules
            
        except IntegrityError:
            self.db.rollback()
            raise DatabaseOperationError("One or more rule names already exist")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk creating eligibility rules: {str(e)}")
            raise DatabaseOperationError(f"Failed to bulk create eligibility rules: {str(e)}")
    
    def get_by_id(self, rule_id: UUID) -> Optional[PlanEligibilityRule]:
        """Get eligibility rule by ID"""
        return self.db.query(PlanEligibilityRule).options(
            joinedload(PlanEligibilityRule.plan),
            joinedload(PlanEligibilityRule.child_rules)
        ).filter(
            PlanEligibilityRule.id == rule_id
        ).first()
    
    def get_by_plan_and_name(
        self,
        plan_id: UUID,
        rule_name: str
    ) -> Optional[PlanEligibilityRule]:
        """Get eligibility rule by plan and name"""
        return self.db.query(PlanEligibilityRule).filter(
            PlanEligibilityRule.plan_id == plan_id,
            PlanEligibilityRule.rule_name == rule_name
        ).first()
    
    def get_by_plan(
        self,
        plan_id: UUID,
        rule_category: Optional[RuleCategory] = None,
        rule_type: Optional[RuleType] = None,
        rule_severity: Optional[RuleSeverity] = None,
        is_mandatory: Optional[bool] = None,
        is_active: Optional[bool] = None,
        can_override: Optional[bool] = None,
        rule_group: Optional[str] = None,
        effective_date: Optional[date] = None,
        text_search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[PlanEligibilityRule]:
        """Get eligibility rules by plan with filters"""
        query = self.db.query(PlanEligibilityRule).options(
            joinedload(PlanEligibilityRule.child_rules)
        ).filter(
            PlanEligibilityRule.plan_id == plan_id
        )
        
        if rule_category:
            query = query.filter(PlanEligibilityRule.rule_category == rule_category.value)
        
        if rule_type:
            query = query.filter(PlanEligibilityRule.rule_type == rule_type.value)
        
        if rule_severity:
            query = query.filter(PlanEligibilityRule.rule_severity == rule_severity.value)
        
        if is_mandatory is not None:
            query = query.filter(PlanEligibilityRule.is_mandatory == is_mandatory)
        
        if is_active is not None:
            query = query.filter(PlanEligibilityRule.is_active == is_active)
        
        if can_override is not None:
            query = query.filter(PlanEligibilityRule.can_override == can_override)
        
        if rule_group:
            query = query.filter(PlanEligibilityRule.rule_group == rule_group)
        
        if effective_date:
            query = query.filter(
                or_(
                    PlanEligibilityRule.effective_date.is_(None),
                    PlanEligibilityRule.effective_date <= effective_date
                ),
                or_(
                    PlanEligibilityRule.expiry_date.is_(None),
                    PlanEligibilityRule.expiry_date > effective_date
                )
            )
        
        if text_search:
            search_term = f"%{text_search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(PlanEligibilityRule.rule_name).like(search_term),
                    func.lower(PlanEligibilityRule.rule_description).like(search_term),
                    func.lower(PlanEligibilityRule.failure_message).like(search_term)
                )
            )
        
        if tags:
            # PostgreSQL JSONB array contains operation
            for tag in tags:
                query = query.filter(PlanEligibilityRule.tags.op('@>')([tag]))
        
        return query.order_by(
            PlanEligibilityRule.priority,
            PlanEligibilityRule.rule_category,
            PlanEligibilityRule.created_at
        ).all()
    
    def get_effective_rules(
        self,
        plan_id: UUID,
        check_date: Optional[date] = None
    ) -> List[PlanEligibilityRule]:
        """Get effective eligibility rules for a plan"""
        check_date = check_date or date.today()
        
        query = self.db.query(PlanEligibilityRule).filter(
            PlanEligibilityRule.plan_id == plan_id,
            PlanEligibilityRule.is_active == True,
            or_(
                PlanEligibilityRule.effective_date.is_(None),
                PlanEligibilityRule.effective_date <= check_date
            ),
            or_(
                PlanEligibilityRule.expiry_date.is_(None),
                PlanEligibilityRule.expiry_date > check_date
            )
        )
        
        return query.order_by(PlanEligibilityRule.priority).all()
    
    def get_mandatory_rules(self, plan_id: UUID) -> List[PlanEligibilityRule]:
        """Get mandatory eligibility rules for a plan"""
        return self.get_by_plan(plan_id, is_mandatory=True, is_active=True)
    
    def get_overridable_rules(self, plan_id: UUID) -> List[PlanEligibilityRule]:
        """Get overridable eligibility rules for a plan"""
        return self.get_by_plan(plan_id, can_override=True, is_active=True)
    
    def get_by_category(
        self,
        plan_id: UUID,
        category: RuleCategory
    ) -> List[PlanEligibilityRule]:
        """Get eligibility rules by category"""
        return self.get_by_plan(plan_id, rule_category=category, is_active=True)
    
    def get_child_rules(self, parent_rule_id: UUID) -> List[PlanEligibilityRule]:
        """Get child rules for a parent rule"""
        return self.db.query(PlanEligibilityRule).filter(
            PlanEligibilityRule.parent_rule_id == parent_rule_id
        ).order_by(PlanEligibilityRule.priority).all()
    
    def update(
        self,
        rule_id: UUID,
        update_data: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Optional[PlanEligibilityRule]:
        """Update eligibility rule"""
        eligibility_rule = self.get_by_id(rule_id)
        if not eligibility_rule:
            return None
        
        try:
            update_data['updated_by'] = updated_by
            update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                if hasattr(eligibility_rule, field):
                    setattr(eligibility_rule, field, value)
            
            self.db.commit()
            self.db.refresh(eligibility_rule)
            
            logger.info(f"Updated eligibility rule {rule_id}")
            return eligibility_rule
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating eligibility rule {rule_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update eligibility rule: {str(e)}")
    
    def delete(self, rule_id: UUID) -> bool:
        """Delete eligibility rule (hard delete due to cascading)"""
        eligibility_rule = self.get_by_id(rule_id)
        if not eligibility_rule:
            return False
        
        try:
            self.db.delete(eligibility_rule)
            self.db.commit()
            
            logger.info(f"Deleted eligibility rule {rule_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting eligibility rule {rule_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to delete eligibility rule: {str(e)}")
    
    def get_rule_summary(self, plan_id: UUID) -> Dict[str, Any]:
        """Get eligibility rule summary for a plan"""
        rules = self.get_by_plan(plan_id)
        
        summary = {
            'plan_id': str(plan_id),
            'total_rules': len(rules),
            'active_rules': 0,
            'mandatory_rules': 0,
            'by_category': {},
            'by_type': {},
            'by_severity': {},
            'overridable_rules': 0
        }
        
        for rule in rules:
            if rule.is_active:
                summary['active_rules'] += 1
            
            if rule.is_mandatory:
                summary['mandatory_rules'] += 1
            
            if rule.can_override:
                summary['overridable_rules'] += 1
            
            # Count by category
            category = rule.rule_category
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
            
            # Count by type
            rule_type = rule.rule_type
            summary['by_type'][rule_type] = summary['by_type'].get(rule_type, 0) + 1
            
            # Count by severity
            severity = rule.rule_severity
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
        
        return summary
