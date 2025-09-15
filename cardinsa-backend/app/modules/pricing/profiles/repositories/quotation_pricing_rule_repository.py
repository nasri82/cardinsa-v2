# app/modules/pricing/profiles/repositories/quotation_pricing_rule_repository.py

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, and_, or_, desc, asc, func, text
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from ..models import (
    QuotationPricingRule,
    QuotationPricingRulesHistory,
    QuotationPricingRuleAgeBracket,
    QuotationPricingProfileRule
)
from ..schemas import (
    QuotationPricingRuleCreate,
    QuotationPricingRuleUpdate,
    PricingRuleSearchParams,
    InsuranceType,
    RuleType,
    AdjustmentType
)

class QuotationPricingRuleRepository:
    """
    Repository for pricing rule data access operations.
    Handles CRUD operations, rule evaluation, and audit tracking.
    """
    
    def __init__(self, db: Session):
        self.db = db

    # ==================== CREATE OPERATIONS ====================
    
    async def create(
        self, 
        rule_data: QuotationPricingRuleCreate, 
        created_by: UUID
    ) -> QuotationPricingRule:
        """
        Create a new pricing rule with validation and audit trail.
        
        Args:
            rule_data: Rule creation data
            created_by: User ID creating the rule
            
        Returns:
            Created pricing rule
            
        Raises:
            ConflictError: If rule name already exists for insurance type
            ValidationError: If data validation fails
        """
        try:
            # Check for existing rule with same name and insurance type
            existing = await self.get_by_name_and_type(
                rule_data.rule_name, 
                rule_data.insurance_type
            )
            if existing:
                raise ConflictError(
                    f"Rule '{rule_data.rule_name}' already exists for {rule_data.insurance_type} insurance"
                )
            
            # Create rule
            db_rule = QuotationPricingRule(
                **rule_data.model_dump(exclude_unset=True),
                created_by=created_by,
                updated_by=created_by
            )
            
            self.db.add(db_rule)
            self.db.flush()  # Get ID without committing
            
            # Create history entry
            await self._create_history_entry(
                rule_id=db_rule.id,
                operation="CREATE",
                new_data=self._serialize_rule(db_rule),
                changed_by=created_by,
                change_reason="Rule created"
            )
            
            self.db.commit()
            self.db.refresh(db_rule)
            return db_rule
            
        except IntegrityError as e:
            self.db.rollback()
            raise ConflictError(f"Rule creation failed due to constraint violation: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise

    async def create_bulk(
        self, 
        rules_data: List[QuotationPricingRuleCreate], 
        created_by: UUID
    ) -> List[QuotationPricingRule]:
        """Create multiple rules in a single transaction"""
        try:
            created_rules = []
            
            for rule_data in rules_data:
                # Validate each rule
                existing = await self.get_by_name_and_type(
                    rule_data.rule_name, 
                    rule_data.insurance_type
                )
                if existing:
                    raise ConflictError(
                        f"Rule '{rule_data.rule_name}' already exists for {rule_data.insurance_type} insurance"
                    )
                
                # Create rule
                db_rule = QuotationPricingRule(
                    **rule_data.model_dump(exclude_unset=True),
                    created_by=created_by,
                    updated_by=created_by
                )
                self.db.add(db_rule)
                created_rules.append(db_rule)
            
            self.db.flush()  # Get IDs for all rules
            
            # Create history entries for all
            for rule in created_rules:
                await self._create_history_entry(
                    rule_id=rule.id,
                    operation="CREATE",
                    new_data=self._serialize_rule(rule),
                    changed_by=created_by,
                    change_reason="Bulk rule creation"
                )
            
            self.db.commit()
            
            # Refresh all rules
            for rule in created_rules:
                self.db.refresh(rule)
                
            return created_rules
            
        except Exception as e:
            self.db.rollback()
            raise

    # ==================== READ OPERATIONS ====================
    
    async def get_by_id(
        self, 
        rule_id: UUID, 
        include_age_brackets: bool = False
    ) -> Optional[QuotationPricingRule]:
        """Get rule by ID with optional age bracket loading"""
        try:
            query = select(QuotationPricingRule).where(
                QuotationPricingRule.id == rule_id
            )
            
            if include_age_brackets:
                query = query.options(
                    selectinload(QuotationPricingRule.age_brackets)
                )
            
            result = self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            raise ValidationError(f"Error fetching rule: {str(e)}")

    async def get_by_name_and_type(
        self, 
        rule_name: str, 
        insurance_type: InsuranceType
    ) -> Optional[QuotationPricingRule]:
        """Get rule by name and insurance type"""
        try:
            query = select(QuotationPricingRule).where(
                and_(
                    QuotationPricingRule.rule_name == rule_name,
                    QuotationPricingRule.insurance_type == insurance_type,
                    QuotationPricingRule.archived_at.is_(None)
                )
            )
            result = self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise ValidationError(f"Error fetching rule by name and type: {str(e)}")

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
        include_age_brackets: bool = False
    ) -> List[QuotationPricingRule]:
        """Get all rules with pagination and filtering"""
        try:
            query = select(QuotationPricingRule)
            
            if active_only:
                query = query.where(
                    and_(
                        QuotationPricingRule.is_active == True,
                        QuotationPricingRule.archived_at.is_(None)
                    )
                )
            
            if include_age_brackets:
                query = query.options(
                    selectinload(QuotationPricingRule.age_brackets)
                )
            
            query = query.offset(skip).limit(limit).order_by(
                asc(QuotationPricingRule.priority),
                desc(QuotationPricingRule.created_at)
            )
            
            result = self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            raise ValidationError(f"Error fetching rules: {str(e)}")

    async def search(
        self, 
        search_params: PricingRuleSearchParams,
        skip: int = 0,
        limit: int = 100
    ) -> List[QuotationPricingRule]:
        """Advanced search with multiple criteria"""
        try:
            query = select(QuotationPricingRule)
            
            # Build where conditions
            conditions = []
            
            if search_params.rule_name:
                conditions.append(
                    QuotationPricingRule.rule_name.ilike(f"%{search_params.rule_name}%")
                )
            
            if search_params.rule_type:
                conditions.append(
                    QuotationPricingRule.rule_type == search_params.rule_type
                )
            
            if search_params.insurance_type:
                conditions.append(
                    QuotationPricingRule.insurance_type == search_params.insurance_type
                )
            
            if search_params.is_active is not None:
                conditions.append(
                    QuotationPricingRule.is_active == search_params.is_active
                )
            
            if search_params.applies_to:
                conditions.append(
                    QuotationPricingRule.applies_to.ilike(f"%{search_params.applies_to}%")
                )
            
            if search_params.adjustment_type:
                conditions.append(
                    QuotationPricingRule.adjustment_type == search_params.adjustment_type
                )
            
            if search_params.priority_min is not None:
                conditions.append(
                    QuotationPricingRule.priority >= search_params.priority_min
                )
            
            if search_params.priority_max is not None:
                conditions.append(
                    QuotationPricingRule.priority <= search_params.priority_max
                )
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.offset(skip).limit(limit).order_by(
                asc(QuotationPricingRule.priority),
                desc(QuotationPricingRule.created_at)
            )
            
            result = self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            raise ValidationError(f"Error searching rules: {str(e)}")

    async def get_by_insurance_type(
        self, 
        insurance_type: InsuranceType,
        active_only: bool = True,
        order_by_priority: bool = True
    ) -> List[QuotationPricingRule]:
        """Get all rules for a specific insurance type"""
        try:
            query = select(QuotationPricingRule).where(
                QuotationPricingRule.insurance_type == insurance_type
            )
            
            if active_only:
                query = query.where(
                    and_(
                        QuotationPricingRule.is_active == True,
                        QuotationPricingRule.archived_at.is_(None)
                    )
                )
            
            if order_by_priority:
                query = query.order_by(
                    asc(QuotationPricingRule.priority),
                    QuotationPricingRule.rule_name
                )
            else:
                query = query.order_by(QuotationPricingRule.rule_name)
            
            result = self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            raise ValidationError(f"Error fetching rules by insurance type: {str(e)}")

    async def get_by_rule_type(
        self, 
        rule_type: RuleType,
        insurance_type: Optional[InsuranceType] = None,
        active_only: bool = True
    ) -> List[QuotationPricingRule]:
        """Get all rules of a specific type"""
        try:
            query = select(QuotationPricingRule).where(
                QuotationPricingRule.rule_type == rule_type
            )
            
            if insurance_type:
                query = query.where(
                    QuotationPricingRule.insurance_type == insurance_type
                )
            
            if active_only:
                query = query.where(
                    and_(
                        QuotationPricingRule.is_active == True,
                        QuotationPricingRule.archived_at.is_(None)
                    )
                )
            
            query = query.order_by(
                asc(QuotationPricingRule.priority),
                QuotationPricingRule.rule_name
            )
            
            result = self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            raise ValidationError(f"Error fetching rules by type: {str(e)}")

    async def get_effective_rules(
        self,
        insurance_type: InsuranceType,
        evaluation_date: Optional[datetime] = None
    ) -> List[QuotationPricingRule]:
        """Get rules that are effective for a given date and insurance type"""
        try:
            if evaluation_date is None:
                evaluation_date = datetime.utcnow()
            
            query = select(QuotationPricingRule).where(
                and_(
                    QuotationPricingRule.insurance_type == insurance_type,
                    QuotationPricingRule.is_active == True,
                    QuotationPricingRule.archived_at.is_(None),
                    or_(
                        QuotationPricingRule.effective_from.is_(None),
                        QuotationPricingRule.effective_from <= evaluation_date
                    ),
                    or_(
                        QuotationPricingRule.effective_to.is_(None),
                        QuotationPricingRule.effective_to >= evaluation_date
                    )
                )
            ).order_by(asc(QuotationPricingRule.priority))
            
            result = self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            raise ValidationError(f"Error fetching effective rules: {str(e)}")

    # ==================== UPDATE OPERATIONS ====================
    
    async def update(
        self,
        rule_id: UUID,
        rule_data: QuotationPricingRuleUpdate,
        updated_by: UUID,
        change_reason: Optional[str] = None,
        impact_assessment: Optional[str] = None
    ) -> Optional[QuotationPricingRule]:
        """Update rule with validation and audit trail"""
        try:
            rule = await self.get_by_id(rule_id)
            if not rule:
                raise NotFoundError(f"Rule with ID {rule_id} not found")
            
            # Store old data for history
            old_data = self._serialize_rule(rule)
            
            # Update fields
            update_data = rule_data.model_dump(exclude_unset=True)
            changed_fields = []
            
            for field, value in update_data.items():
                if hasattr(rule, field):
                    old_value = getattr(rule, field)
                    if old_value != value:
                        setattr(rule, field, value)
                        changed_fields.append(field)
            
            if changed_fields:
                rule.updated_by = updated_by
                rule.version += 1  # Increment version
                
                # Create history entry
                await self._create_history_entry(
                    rule_id=rule.id,
                    operation="UPDATE",
                    old_data=old_data,
                    new_data=self._serialize_rule(rule),
                    changed_by=updated_by,
                    changed_fields=changed_fields,
                    change_reason=change_reason or "Rule updated",
                    impact_assessment=impact_assessment
                )
            
            self.db.commit()
            self.db.refresh(rule)
            return rule
            
        except Exception as e:
            self.db.rollback()
            raise

    async def update_priority(
        self,
        rule_id: UUID,
        new_priority: int,
        updated_by: UUID
    ) -> Optional[QuotationPricingRule]:
        """Update rule priority"""
        try:
            rule = await self.get_by_id(rule_id)
            if not rule:
                raise NotFoundError(f"Rule with ID {rule_id} not found")
            
            old_data = self._serialize_rule(rule)
            old_priority = rule.priority
            
            rule.priority = new_priority
            rule.updated_by = updated_by
            
            # Create history entry
            await self._create_history_entry(
                rule_id=rule.id,
                operation="UPDATE",
                old_data=old_data,
                new_data=self._serialize_rule(rule),
                changed_by=updated_by,
                changed_fields=["priority"],
                change_reason=f"Priority changed from {old_priority} to {new_priority}"
            )
            
            self.db.commit()
            self.db.refresh(rule)
            return rule
            
        except Exception as e:
            self.db.rollback()
            raise

    async def activate_rule(
        self,
        rule_id: UUID,
        updated_by: UUID,
        effective_from: Optional[datetime] = None
    ) -> Optional[QuotationPricingRule]:
        """Activate a rule"""
        try:
            rule = await self.get_by_id(rule_id)
            if not rule:
                raise NotFoundError(f"Rule with ID {rule_id} not found")
            
            old_data = self._serialize_rule(rule)
            
            rule.is_active = True
            rule.updated_by = updated_by
            
            if effective_from:
                rule.effective_from = effective_from
            
            # Create history entry
            await self._create_history_entry(
                rule_id=rule.id,
                operation="ACTIVATE",
                old_data=old_data,
                new_data=self._serialize_rule(rule),
                changed_by=updated_by,
                change_reason="Rule activated"
            )
            
            self.db.commit()
            self.db.refresh(rule)
            return rule
            
        except Exception as e:
            self.db.rollback()
            raise

    async def deactivate_rule(
        self,
        rule_id: UUID,
        updated_by: UUID,
        effective_to: Optional[datetime] = None,
        reason: Optional[str] = None
    ) -> Optional[QuotationPricingRule]:
        """Deactivate a rule"""
        try:
            rule = await self.get_by_id(rule_id)
            if not rule:
                raise NotFoundError(f"Rule with ID {rule_id} not found")
            
            old_data = self._serialize_rule(rule)
            
            rule.is_active = False
            rule.updated_by = updated_by
            
            if effective_to:
                rule.effective_to = effective_to
            
            # Create history entry
            await self._create_history_entry(
                rule_id=rule.id,
                operation="DEACTIVATE",
                old_data=old_data,
                new_data=self._serialize_rule(rule),
                changed_by=updated_by,
                change_reason=reason or "Rule deactivated"
            )
            
            self.db.commit()
            self.db.refresh(rule)
            return rule
            
        except Exception as e:
            self.db.rollback()
            raise

    # ==================== DELETE OPERATIONS ====================
    
    async def soft_delete(
        self,
        rule_id: UUID,
        deleted_by: UUID,
        reason: Optional[str] = None
    ) -> bool:
        """Soft delete rule (archive)"""
        try:
            rule = await self.get_by_id(rule_id)
            if not rule:
                raise NotFoundError(f"Rule with ID {rule_id} not found")
            
            old_data = self._serialize_rule(rule)
            
            rule.archived_at = datetime.utcnow()
            rule.is_active = False
            rule.updated_by = deleted_by
            
            # Create history entry
            await self._create_history_entry(
                rule_id=rule.id,
                operation="ARCHIVE",
                old_data=old_data,
                new_data=self._serialize_rule(rule),
                changed_by=deleted_by,
                change_reason=reason or "Rule archived"
            )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise

    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_count_by_type(self) -> Dict[str, int]:
        """Get rule counts by rule type"""
        try:
            query = select(
                QuotationPricingRule.rule_type,
                func.count(QuotationPricingRule.id).label('count')
            ).where(
                QuotationPricingRule.archived_at.is_(None)
            ).group_by(QuotationPricingRule.rule_type)
            
            result = self.db.execute(query)
            return {row.rule_type: row.count for row in result}
            
        except Exception as e:
            raise ValidationError(f"Error getting rule type counts: {str(e)}")

    async def get_count_by_insurance_type(self) -> Dict[str, int]:
        """Get rule counts by insurance type"""
        try:
            query = select(
                QuotationPricingRule.insurance_type,
                func.count(QuotationPricingRule.id).label('count')
            ).where(
                QuotationPricingRule.archived_at.is_(None)
            ).group_by(QuotationPricingRule.insurance_type)
            
            result = self.db.execute(query)
            return {row.insurance_type: row.count for row in result}
            
        except Exception as e:
            raise ValidationError(f"Error getting insurance type counts: {str(e)}")

    async def get_average_adjustments_by_type(self) -> Dict[str, Decimal]:
        """Get average adjustment values by rule type"""
        try:
            query = select(
                QuotationPricingRule.rule_type,
                func.avg(QuotationPricingRule.adjustment_value).label('avg_adjustment')
            ).where(
                and_(
                    QuotationPricingRule.is_active == True,
                    QuotationPricingRule.archived_at.is_(None)
                )
            ).group_by(QuotationPricingRule.rule_type)
            
            result = self.db.execute(query)
            return {row.rule_type: row.avg_adjustment for row in result}
            
        except Exception as e:
            raise ValidationError(f"Error getting average adjustments: {str(e)}")

    # ==================== HISTORY OPERATIONS ====================
    
    async def get_history(
        self, 
        rule_id: UUID,
        limit: int = 50
    ) -> List[QuotationPricingRulesHistory]:
        """Get rule change history"""
        try:
            query = select(QuotationPricingRulesHistory).where(
                QuotationPricingRulesHistory.rule_id == rule_id
            ).order_by(
                desc(QuotationPricingRulesHistory.changed_at)
            ).limit(limit)
            
            result = self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            raise ValidationError(f"Error fetching rule history: {str(e)}")

    # ==================== PRIVATE HELPER METHODS ====================
    
    async def _create_history_entry(
        self,
        rule_id: UUID,
        operation: str,
        new_data: Dict[str, Any],
        changed_by: UUID,
        old_data: Optional[Dict[str, Any]] = None,
        changed_fields: Optional[List[str]] = None,
        change_reason: Optional[str] = None,
        impact_assessment: Optional[str] = None
    ) -> None:
        """Create a history entry for rule changes"""
        history_entry = QuotationPricingRulesHistory(
            rule_id=rule_id,
            operation=operation,
            changed_at=datetime.utcnow(),
            changed_by=changed_by,
            old_data=old_data,
            new_data=new_data,
            changed_fields=changed_fields,
            change_reason=change_reason,
            impact_assessment=impact_assessment
        )
        self.db.add(history_entry)

    def _serialize_rule(self, rule: QuotationPricingRule) -> Dict[str, Any]:
        """Serialize rule for history storage"""
        return {
            "id": str(rule.id),
            "rule_name": rule.rule_name,
            "description": rule.description,
            "rule_type": rule.rule_type,
            "insurance_type": rule.insurance_type,
            "base_premium": float(rule.base_premium) if rule.base_premium else None,
            "min_premium": float(rule.min_premium) if rule.min_premium else None,
            "max_premium": float(rule.max_premium) if rule.max_premium else None,
            "currency_code": rule.currency_code,
            "applies_to": rule.applies_to,
            "comparison_operator": rule.comparison_operator,
            "value": rule.value,
            "adjustment_type": rule.adjustment_type,
            "adjustment_value": float(rule.adjustment_value),
            "formula_expression": rule.formula_expression,
            "formula_variables": rule.formula_variables,
            "is_active": rule.is_active,
            "effective_from": rule.effective_from.isoformat() if rule.effective_from else None,
            "effective_to": rule.effective_to.isoformat() if rule.effective_to else None,
            "priority": rule.priority,
            "version": rule.version,
            "created_at": rule.created_at.isoformat(),
            "updated_at": rule.updated_at.isoformat(),
            "created_by": str(rule.created_by) if rule.created_by else None,
            "updated_by": str(rule.updated_by) if rule.updated_by else None,
            "archived_at": rule.archived_at.isoformat() if rule.archived_at else None
        }