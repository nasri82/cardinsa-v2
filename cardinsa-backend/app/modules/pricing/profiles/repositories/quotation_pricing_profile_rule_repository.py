# app/modules/pricing/profiles/repositories/quotation_pricing_profile_rule_repository.py
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, desc, asc, func, select, update, delete
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.core.database import get_db
from app.modules.pricing.profiles.models.quotation_pricing_profile_rule_model import QuotationPricingProfileRule
from app.modules.pricing.profiles.models.quotation_pricing_profile_model import QuotationPricingProfile  
from app.modules.pricing.profiles.models.quotation_pricing_rule_model import QuotationPricingRule
from app.core.exceptions import (
    NotFoundError as EntityNotFoundError, 
    BusinessLogicError, 
    ValidationError,
    BaseAppException as DatabaseOperationError
)


class QuotationPricingProfileRuleRepository:
    """
    Repository for managing the relationship between pricing profiles and rules.
    Handles complex operations for profile-rule associations, ordering, and validation.
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    # ============================================================================
    # CREATE OPERATIONS
    # ============================================================================
    
    def create_profile_rule(
        self, 
        profile_id: UUID, 
        rule_id: UUID, 
        order_index: int = 0,
        is_active: bool = True,
        created_by: UUID = None
    ) -> QuotationPricingProfileRule:
        """
        Create a new profile-rule relationship.
        
        Args:
            profile_id: ID of the pricing profile
            rule_id: ID of the pricing rule
            order_index: Execution order (default: 0)
            is_active: Whether the rule is active (default: True)
            created_by: ID of the user creating the relationship
            
        Returns:
            Created profile-rule relationship
            
        Raises:
            ValidationError: If profile or rule doesn't exist
            BusinessLogicError: If relationship already exists
        """
        try:
            # Validate profile exists
            profile = self.db.query(QuotationPricingProfile).filter(
                QuotationPricingProfile.id == profile_id
            ).first()
            if not profile:
                raise ValidationError(f"Pricing profile with ID {profile_id} not found")
            
            # Validate rule exists
            rule = self.db.query(QuotationPricingRule).filter(
                QuotationPricingRule.id == rule_id
            ).first()
            if not rule:
                raise ValidationError(f"Pricing rule with ID {rule_id} not found")
            
            # Check if relationship already exists
            existing = self.db.query(QuotationPricingProfileRule).filter(
                and_(
                    QuotationPricingProfileRule.profile_id == profile_id,
                    QuotationPricingProfileRule.rule_id == rule_id,
                    QuotationPricingProfileRule.archived_at.is_(None)
                )
            ).first()
            
            if existing:
                raise BusinessLogicError(
                    f"Rule {rule_id} is already associated with profile {profile_id}"
                )
            
            # Create new profile-rule relationship
            profile_rule = QuotationPricingProfileRule(
                profile_id=profile_id,
                rule_id=rule_id,
                order_index=order_index,
                is_active=is_active,
                created_by=created_by,
                updated_by=created_by
            )
            
            self.db.add(profile_rule)
            self.db.commit()
            self.db.refresh(profile_rule)
            
            return profile_rule
            
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to create profile-rule relationship: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Unexpected error creating profile-rule relationship: {str(e)}")
    
    def create_bulk_profile_rules(
        self, 
        profile_id: UUID, 
        rule_ids: List[UUID],
        created_by: UUID = None
    ) -> List[QuotationPricingProfileRule]:
        """
        Create multiple profile-rule relationships in bulk.
        
        Args:
            profile_id: ID of the pricing profile
            rule_ids: List of rule IDs to associate
            created_by: ID of the user creating the relationships
            
        Returns:
            List of created profile-rule relationships
        """
        try:
            # Validate profile exists
            profile = self.db.query(QuotationPricingProfile).filter(
                QuotationPricingProfile.id == profile_id
            ).first()
            if not profile:
                raise ValidationError(f"Pricing profile with ID {profile_id} not found")
            
            # Get existing relationships to avoid duplicates
            existing_rule_ids = set(
                self.db.query(QuotationPricingProfileRule.rule_id)
                .filter(
                    and_(
                        QuotationPricingProfileRule.profile_id == profile_id,
                        QuotationPricingProfileRule.rule_id.in_(rule_ids),
                        QuotationPricingProfileRule.archived_at.is_(None)
                    )
                )
                .scalar_all()
            )
            
            # Filter out already existing rule IDs
            new_rule_ids = [rule_id for rule_id in rule_ids if rule_id not in existing_rule_ids]
            
            if not new_rule_ids:
                return []
            
            # Validate all rules exist
            existing_rules_count = self.db.query(QuotationPricingRule).filter(
                QuotationPricingRule.id.in_(new_rule_ids)
            ).count()
            
            if existing_rules_count != len(new_rule_ids):
                raise ValidationError("One or more rule IDs do not exist")
            
            # Create profile-rule relationships
            profile_rules = []
            for index, rule_id in enumerate(new_rule_ids):
                profile_rule = QuotationPricingProfileRule(
                    profile_id=profile_id,
                    rule_id=rule_id,
                    order_index=index,
                    is_active=True,
                    created_by=created_by,
                    updated_by=created_by
                )
                profile_rules.append(profile_rule)
            
            self.db.add_all(profile_rules)
            self.db.commit()
            
            # Refresh all created objects
            for profile_rule in profile_rules:
                self.db.refresh(profile_rule)
            
            return profile_rules
            
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to create bulk profile-rule relationships: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Unexpected error creating bulk profile-rule relationships: {str(e)}")
    
    # ============================================================================
    # READ OPERATIONS
    # ============================================================================
    
    def get_by_id(self, profile_rule_id: UUID) -> Optional[QuotationPricingProfileRule]:
        """Get profile-rule relationship by ID."""
        return self.db.query(QuotationPricingProfileRule)\
            .options(
                joinedload(QuotationPricingProfileRule.profile),
                joinedload(QuotationPricingProfileRule.rule)
            )\
            .filter(
                and_(
                    QuotationPricingProfileRule.id == profile_rule_id,
                    QuotationPricingProfileRule.archived_at.is_(None)
                )
            ).first()
    
    def get_by_profile_id(
        self, 
        profile_id: UUID, 
        active_only: bool = True,
        include_archived: bool = False
    ) -> List[QuotationPricingProfileRule]:
        """
        Get all rules associated with a pricing profile.
        
        Args:
            profile_id: ID of the pricing profile
            active_only: Whether to return only active rules
            include_archived: Whether to include archived relationships
            
        Returns:
            List of profile-rule relationships ordered by order_index
        """
        query = self.db.query(QuotationPricingProfileRule)\
            .options(
                joinedload(QuotationPricingProfileRule.rule),
                joinedload(QuotationPricingProfileRule.profile)
            )\
            .filter(QuotationPricingProfileRule.profile_id == profile_id)
        
        if not include_archived:
            query = query.filter(QuotationPricingProfileRule.archived_at.is_(None))
        
        if active_only:
            query = query.filter(QuotationPricingProfileRule.is_active == True)
        
        return query.order_by(QuotationPricingProfileRule.order_index).all()
    
    def get_by_rule_id(
        self, 
        rule_id: UUID, 
        active_only: bool = True
    ) -> List[QuotationPricingProfileRule]:
        """
        Get all profiles that use a specific rule.
        
        Args:
            rule_id: ID of the pricing rule
            active_only: Whether to return only active relationships
            
        Returns:
            List of profile-rule relationships
        """
        query = self.db.query(QuotationPricingProfileRule)\
            .options(
                joinedload(QuotationPricingProfileRule.profile),
                joinedload(QuotationPricingProfileRule.rule)
            )\
            .filter(
                and_(
                    QuotationPricingProfileRule.rule_id == rule_id,
                    QuotationPricingProfileRule.archived_at.is_(None)
                )
            )
        
        if active_only:
            query = query.filter(QuotationPricingProfileRule.is_active == True)
        
        return query.order_by(QuotationPricingProfileRule.order_index).all()
    
    def get_profile_rules_ordered(
        self, 
        profile_id: UUID,
        insurance_type: str = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get profile rules with complete rule details in execution order.
        
        Args:
            profile_id: ID of the pricing profile
            insurance_type: Filter by insurance type (optional)
            active_only: Whether to return only active rules
            
        Returns:
            List of dictionaries containing profile-rule and rule details
        """
        query = self.db.query(QuotationPricingProfileRule)\
            .join(QuotationPricingRule)\
            .options(
                joinedload(QuotationPricingProfileRule.rule),
                joinedload(QuotationPricingProfileRule.profile)
            )\
            .filter(
                and_(
                    QuotationPricingProfileRule.profile_id == profile_id,
                    QuotationPricingProfileRule.archived_at.is_(None)
                )
            )
        
        if active_only:
            query = query.filter(
                and_(
                    QuotationPricingProfileRule.is_active == True,
                    QuotationPricingRule.is_active == True
                )
            )
        
        if insurance_type:
            query = query.filter(QuotationPricingRule.insurance_type == insurance_type)
        
        results = query.order_by(QuotationPricingProfileRule.order_index).all()
        
        return [
            {
                "profile_rule_id": pr.id,
                "order_index": pr.order_index,
                "is_active": pr.is_active,
                "rule": {
                    "id": pr.rule.id,
                    "name": pr.rule.name,
                    "description": pr.rule.description,
                    "field_name": pr.rule.field_name,
                    "operator": pr.rule.operator,
                    "condition_value": pr.rule.condition_value,
                    "impact_type": pr.rule.impact_type,
                    "impact_value": pr.rule.impact_value,
                    "formula": pr.rule.formula,
                    "insurance_type": pr.rule.insurance_type,
                    "is_active": pr.rule.is_active
                },
                "created_at": pr.created_at,
                "updated_at": pr.updated_at
            }
            for pr in results
        ]
    
    def check_rule_usage(self, rule_id: UUID) -> Dict[str, Any]:
        """
        Check how a rule is being used across profiles.
        
        Args:
            rule_id: ID of the pricing rule
            
        Returns:
            Dictionary with usage statistics
        """
        total_profiles = self.db.query(QuotationPricingProfileRule)\
            .filter(
                and_(
                    QuotationPricingProfileRule.rule_id == rule_id,
                    QuotationPricingProfileRule.archived_at.is_(None)
                )
            ).count()
        
        active_profiles = self.db.query(QuotationPricingProfileRule)\
            .filter(
                and_(
                    QuotationPricingProfileRule.rule_id == rule_id,
                    QuotationPricingProfileRule.is_active == True,
                    QuotationPricingProfileRule.archived_at.is_(None)
                )
            ).count()
        
        profile_names = self.db.query(QuotationPricingProfile.name)\
            .join(QuotationPricingProfileRule)\
            .filter(
                and_(
                    QuotationPricingProfileRule.rule_id == rule_id,
                    QuotationPricingProfileRule.archived_at.is_(None)
                )
            ).all()
        
        return {
            "rule_id": rule_id,
            "total_profiles": total_profiles,
            "active_profiles": active_profiles,
            "inactive_profiles": total_profiles - active_profiles,
            "profile_names": [name[0] for name in profile_names],
            "is_in_use": total_profiles > 0
        }
    
    # ============================================================================
    # UPDATE OPERATIONS
    # ============================================================================
    
    def update_rule_status(
        self, 
        profile_rule_id: UUID, 
        is_active: bool,
        updated_by: UUID = None
    ) -> Optional[QuotationPricingProfileRule]:
        """
        Update the active status of a profile-rule relationship.
        
        Args:
            profile_rule_id: ID of the profile-rule relationship
            is_active: New active status
            updated_by: ID of the user making the update
            
        Returns:
            Updated profile-rule relationship or None if not found
        """
        try:
            profile_rule = self.db.query(QuotationPricingProfileRule)\
                .filter(
                    and_(
                        QuotationPricingProfileRule.id == profile_rule_id,
                        QuotationPricingProfileRule.archived_at.is_(None)
                    )
                ).first()
            
            if not profile_rule:
                return None
            
            profile_rule.is_active = is_active
            profile_rule.updated_by = updated_by
            profile_rule.updated_at = func.now()
            
            self.db.commit()
            self.db.refresh(profile_rule)
            
            return profile_rule
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to update rule status: {str(e)}")
    
    def update_rule_order(
        self, 
        profile_rule_id: UUID, 
        new_order_index: int,
        updated_by: UUID = None
    ) -> Optional[QuotationPricingProfileRule]:
        """
        Update the execution order of a profile-rule relationship.
        
        Args:
            profile_rule_id: ID of the profile-rule relationship
            new_order_index: New order index
            updated_by: ID of the user making the update
            
        Returns:
            Updated profile-rule relationship or None if not found
        """
        try:
            profile_rule = self.db.query(QuotationPricingProfileRule)\
                .filter(
                    and_(
                        QuotationPricingProfileRule.id == profile_rule_id,
                        QuotationPricingProfileRule.archived_at.is_(None)
                    )
                ).first()
            
            if not profile_rule:
                return None
            
            profile_rule.order_index = new_order_index
            profile_rule.updated_by = updated_by
            profile_rule.updated_at = func.now()
            
            self.db.commit()
            self.db.refresh(profile_rule)
            
            return profile_rule
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to update rule order: {str(e)}")
    
    def reorder_profile_rules(
        self, 
        profile_id: UUID, 
        rule_orders: Dict[UUID, int],
        updated_by: UUID = None
    ) -> List[QuotationPricingProfileRule]:
        """
        Reorder multiple rules within a profile.
        
        Args:
            profile_id: ID of the pricing profile
            rule_orders: Dictionary mapping rule_id to new order_index
            updated_by: ID of the user making the update
            
        Returns:
            List of updated profile-rule relationships
        """
        try:
            # Get all profile rules that need reordering
            profile_rules = self.db.query(QuotationPricingProfileRule)\
                .filter(
                    and_(
                        QuotationPricingProfileRule.profile_id == profile_id,
                        QuotationPricingProfileRule.rule_id.in_(rule_orders.keys()),
                        QuotationPricingProfileRule.archived_at.is_(None)
                    )
                ).all()
            
            # Update order indices
            updated_rules = []
            for profile_rule in profile_rules:
                if profile_rule.rule_id in rule_orders:
                    profile_rule.order_index = rule_orders[profile_rule.rule_id]
                    profile_rule.updated_by = updated_by
                    profile_rule.updated_at = func.now()
                    updated_rules.append(profile_rule)
            
            self.db.commit()
            
            # Refresh all updated objects
            for profile_rule in updated_rules:
                self.db.refresh(profile_rule)
            
            return updated_rules
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to reorder profile rules: {str(e)}")
    
    # ============================================================================
    # DELETE OPERATIONS
    # ============================================================================
    
    def remove_profile_rule(
        self, 
        profile_rule_id: UUID,
        updated_by: UUID = None,
        hard_delete: bool = False
    ) -> bool:
        """
        Remove a profile-rule relationship (soft delete by default).
        
        Args:
            profile_rule_id: ID of the profile-rule relationship
            updated_by: ID of the user performing the deletion
            hard_delete: Whether to permanently delete the record
            
        Returns:
            True if successfully removed, False if not found
        """
        try:
            profile_rule = self.db.query(QuotationPricingProfileRule)\
                .filter(QuotationPricingProfileRule.id == profile_rule_id).first()
            
            if not profile_rule:
                return False
            
            if hard_delete:
                self.db.delete(profile_rule)
            else:
                profile_rule.archived_at = func.now()
                profile_rule.updated_by = updated_by
                profile_rule.updated_at = func.now()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to remove profile rule: {str(e)}")
    
    def remove_rule_from_profile(
        self, 
        profile_id: UUID, 
        rule_id: UUID,
        updated_by: UUID = None
    ) -> bool:
        """
        Remove a specific rule from a profile.
        
        Args:
            profile_id: ID of the pricing profile
            rule_id: ID of the pricing rule
            updated_by: ID of the user performing the deletion
            
        Returns:
            True if successfully removed, False if not found
        """
        try:
            profile_rule = self.db.query(QuotationPricingProfileRule)\
                .filter(
                    and_(
                        QuotationPricingProfileRule.profile_id == profile_id,
                        QuotationPricingProfileRule.rule_id == rule_id,
                        QuotationPricingProfileRule.archived_at.is_(None)
                    )
                ).first()
            
            if not profile_rule:
                return False
            
            profile_rule.archived_at = func.now()
            profile_rule.updated_by = updated_by
            profile_rule.updated_at = func.now()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to remove rule from profile: {str(e)}")
    
    def clear_profile_rules(
        self, 
        profile_id: UUID,
        updated_by: UUID = None
    ) -> int:
        """
        Remove all rules from a profile (soft delete).
        
        Args:
            profile_id: ID of the pricing profile
            updated_by: ID of the user performing the deletion
            
        Returns:
            Number of rules removed
        """
        try:
            updated_count = self.db.query(QuotationPricingProfileRule)\
                .filter(
                    and_(
                        QuotationPricingProfileRule.profile_id == profile_id,
                        QuotationPricingProfileRule.archived_at.is_(None)
                    )
                )\
                .update({
                    "archived_at": func.now(),
                    "updated_by": updated_by,
                    "updated_at": func.now()
                })
            
            self.db.commit()
            return updated_count
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to clear profile rules: {str(e)}")
    
    # ============================================================================
    # BUSINESS LOGIC OPERATIONS
    # ============================================================================
    
    def copy_rules_between_profiles(
        self, 
        source_profile_id: UUID, 
        target_profile_id: UUID,
        created_by: UUID = None,
        preserve_order: bool = True
    ) -> List[QuotationPricingProfileRule]:
        """
        Copy all rules from one profile to another.
        
        Args:
            source_profile_id: ID of the source pricing profile
            target_profile_id: ID of the target pricing profile
            created_by: ID of the user performing the copy
            preserve_order: Whether to preserve the original order indices
            
        Returns:
            List of newly created profile-rule relationships
        """
        try:
            # Validate both profiles exist
            source_profile = self.db.query(QuotationPricingProfile)\
                .filter(QuotationPricingProfile.id == source_profile_id).first()
            target_profile = self.db.query(QuotationPricingProfile)\
                .filter(QuotationPricingProfile.id == target_profile_id).first()
            
            if not source_profile:
                raise ValidationError(f"Source profile {source_profile_id} not found")
            if not target_profile:
                raise ValidationError(f"Target profile {target_profile_id} not found")
            
            # Get source profile rules
            source_rules = self.get_by_profile_id(source_profile_id, active_only=True)
            
            if not source_rules:
                return []
            
            # Get existing target rules to avoid duplicates
            existing_rule_ids = set(
                rule.rule_id for rule in self.get_by_profile_id(target_profile_id, active_only=False)
            )
            
            # Create new profile-rule relationships
            new_profile_rules = []
            for source_rule in source_rules:
                if source_rule.rule_id not in existing_rule_ids:
                    new_order = source_rule.order_index if preserve_order else len(new_profile_rules)
                    
                    new_profile_rule = QuotationPricingProfileRule(
                        profile_id=target_profile_id,
                        rule_id=source_rule.rule_id,
                        order_index=new_order,
                        is_active=source_rule.is_active,
                        created_by=created_by,
                        updated_by=created_by
                    )
                    new_profile_rules.append(new_profile_rule)
            
            if new_profile_rules:
                self.db.add_all(new_profile_rules)
                self.db.commit()
                
                # Refresh all created objects
                for profile_rule in new_profile_rules:
                    self.db.refresh(profile_rule)
            
            return new_profile_rules
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to copy rules between profiles: {str(e)}")
    
    def validate_profile_rule_consistency(self, profile_id: UUID) -> Dict[str, Any]:
        """
        Validate the consistency of rules within a profile.
        
        Args:
            profile_id: ID of the pricing profile
            
        Returns:
            Dictionary with validation results and any issues found
        """
        profile_rules = self.get_by_profile_id(profile_id, active_only=True)
        
        issues = []
        warnings = []
        
        # Check for duplicate order indices
        order_indices = [pr.order_index for pr in profile_rules]
        duplicate_orders = [x for x in order_indices if order_indices.count(x) > 1]
        if duplicate_orders:
            issues.append(f"Duplicate order indices found: {set(duplicate_orders)}")
        
        # Check for gaps in order sequence
        if order_indices:
            expected_sequence = list(range(len(order_indices)))
            sorted_orders = sorted(order_indices)
            if sorted_orders != expected_sequence:
                warnings.append("Order indices are not sequential")
        
        # Check for conflicting rules (same field_name with contradictory conditions)
        field_rules = {}
        for pr in profile_rules:
            field_name = pr.rule.field_name
            if field_name not in field_rules:
                field_rules[field_name] = []
            field_rules[field_name].append(pr.rule)
        
        for field_name, rules in field_rules.items():
            if len(rules) > 1:
                operators = [rule.operator for rule in rules]
                if len(set(operators)) > 1:
                    warnings.append(f"Multiple operators for field '{field_name}': {operators}")
        
        return {
            "profile_id": profile_id,
            "total_rules": len(profile_rules),
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "validation_timestamp": datetime.utcnow()
        }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_profile_rule_summary(self, profile_id: UUID) -> Dict[str, Any]:
        """
        Get a summary of rules associated with a profile.
        
        Args:
            profile_id: ID of the pricing profile
            
        Returns:
            Dictionary with profile rule summary
        """
        profile_rules = self.get_by_profile_id(profile_id, active_only=False)
        
        total_rules = len(profile_rules)
        active_rules = len([pr for pr in profile_rules if pr.is_active])
        inactive_rules = total_rules - active_rules
        
        # Group by insurance type
        insurance_types = {}
        for pr in profile_rules:
            if pr.rule.insurance_type:
                ins_type = pr.rule.insurance_type
                if ins_type not in insurance_types:
                    insurance_types[ins_type] = 0
                insurance_types[ins_type] += 1
        
        # Group by impact type
        impact_types = {}
        for pr in profile_rules:
            if pr.rule.impact_type:
                impact_type = pr.rule.impact_type
                if impact_type not in impact_types:
                    impact_types[impact_type] = 0
                impact_types[impact_type] += 1
        
        return {
            "profile_id": profile_id,
            "total_rules": total_rules,
            "active_rules": active_rules,
            "inactive_rules": inactive_rules,
            "rules_by_insurance_type": insurance_types,
            "rules_by_impact_type": impact_types,
            "last_updated": max([pr.updated_at for pr in profile_rules]) if profile_rules else None
        }
    
    def get_rules_execution_plan(self, profile_id: UUID) -> Dict[str, Any]:
        """
        Get the execution plan for rules in a profile, showing the order and logic flow.
        
        Args:
            profile_id: ID of the pricing profile
            
        Returns:
            Dictionary with execution plan details
        """
        profile_rules = self.get_profile_rules_ordered(profile_id, active_only=True)
        
        execution_steps = []
        field_dependencies = {}
        
        for index, rule_data in enumerate(profile_rules):
            rule = rule_data["rule"]
            
            step = {
                "step_number": index + 1,
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "field_name": rule["field_name"],
                "condition": f"{rule['field_name']} {rule['operator']} {rule['condition_value']}",
                "impact": f"{rule['impact_type']}: {rule['impact_value']}",
                "formula": rule.get("formula"),
                "dependencies": []
            }
            
            # Track field dependencies
            field_name = rule["field_name"]
            if field_name not in field_dependencies:
                field_dependencies[field_name] = []
            field_dependencies[field_name].append(index + 1)
            
            execution_steps.append(step)
        
        # Identify potential conflicts or dependencies
        conflicts = []
        for field, steps in field_dependencies.items():
            if len(steps) > 1:
                conflicts.append({
                    "field": field,
                    "conflicting_steps": steps,
                    "warning": f"Multiple rules modify '{field}' - ensure proper ordering"
                })
        
        return {
            "profile_id": profile_id,
            "total_steps": len(execution_steps),
            "execution_steps": execution_steps,
            "field_dependencies": field_dependencies,
            "potential_conflicts": conflicts,
            "execution_time_estimate": len(execution_steps) * 0.1  # Rough estimate in seconds
        }
    
    def optimize_rule_order(
        self, 
        profile_id: UUID,
        updated_by: UUID = None
    ) -> List[QuotationPricingProfileRule]:
        """
        Optimize the execution order of rules based on dependencies and performance.
        
        Args:
            profile_id: ID of the pricing profile
            updated_by: ID of the user performing the optimization
            
        Returns:
            List of reordered profile-rule relationships
        """
        try:
            profile_rules = self.get_by_profile_id(profile_id, active_only=True)
            
            if len(profile_rules) <= 1:
                return profile_rules
            
            # Sort rules by priority:
            # 1. Rules with formulas (lowest impact) first
            # 2. Fixed amount impacts
            # 3. Percentage impacts
            # 4. Multiplier impacts (highest impact) last
            
            priority_order = {
                "FIXED_AMOUNT": 1,
                "PERCENTAGE": 2, 
                "MULTIPLIER": 3
            }
            
            def get_rule_priority(profile_rule):
                rule = profile_rule.rule
                # Rules with formulas get highest priority (executed first)
                if rule.formula:
                    return 0
                # Otherwise sort by impact type
                return priority_order.get(rule.impact_type, 999)
            
            # Sort rules by priority
            sorted_rules = sorted(profile_rules, key=get_rule_priority)
            
            # Update order indices
            rule_orders = {}
            for index, profile_rule in enumerate(sorted_rules):
                rule_orders[profile_rule.rule_id] = index
            
            # Apply the new ordering
            updated_rules = self.reorder_profile_rules(
                profile_id=profile_id,
                rule_orders=rule_orders,
                updated_by=updated_by
            )
            
            return updated_rules
            
        except Exception as e:
            raise DatabaseOperationError(f"Failed to optimize rule order: {str(e)}")
    
    def export_profile_rules(self, profile_id: UUID) -> Dict[str, Any]:
        """
        Export profile rules configuration for backup or migration.
        
        Args:
            profile_id: ID of the pricing profile
            
        Returns:
            Dictionary with complete profile rules configuration
        """
        profile_rules = self.get_profile_rules_ordered(profile_id, active_only=False)
        
        # Get profile details
        profile = self.db.query(QuotationPricingProfile).filter(
            QuotationPricingProfile.id == profile_id
        ).first()
        
        export_data = {
            "export_metadata": {
                "profile_id": str(profile_id),
                "profile_name": profile.name if profile else "Unknown",
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_rules": len(profile_rules)
            },
            "profile_configuration": {
                "name": profile.name if profile else None,
                "description": profile.description if profile else None,
                "code": profile.code if profile else None,
                "insurance_type": profile.insurance_type if profile else None,
                "is_active": profile.is_active if profile else None
            } if profile else {},
            "rules": [
                {
                    "rule_id": str(rule_data["rule"]["id"]),
                    "rule_name": rule_data["rule"]["name"],
                    "description": rule_data["rule"]["description"],
                    "field_name": rule_data["rule"]["field_name"],
                    "operator": rule_data["rule"]["operator"],
                    "condition_value": rule_data["rule"]["condition_value"],
                    "impact_type": rule_data["rule"]["impact_type"],
                    "impact_value": rule_data["rule"]["impact_value"],
                    "formula": rule_data["rule"]["formula"],
                    "insurance_type": rule_data["rule"]["insurance_type"],
                    "order_index": rule_data["order_index"],
                    "is_active": rule_data["is_active"],
                    "profile_rule_id": str(rule_data["profile_rule_id"])
                }
                for rule_data in profile_rules
            ]
        }
        
        return export_data
    
    def import_profile_rules(
        self, 
        profile_id: UUID,
        import_data: Dict[str, Any],
        created_by: UUID = None,
        overwrite_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Import profile rules configuration from exported data.
        
        Args:
            profile_id: ID of the target pricing profile
            import_data: Previously exported profile rules data
            created_by: ID of the user performing the import
            overwrite_existing: Whether to overwrite existing rules
            
        Returns:
            Dictionary with import results
        """
        try:
            if overwrite_existing:
                # Clear existing rules
                self.clear_profile_rules(profile_id, updated_by=created_by)
            
            imported_rules = []
            skipped_rules = []
            errors = []
            
            for rule_config in import_data.get("rules", []):
                try:
                    # Check if rule exists
                    rule_id = UUID(rule_config["rule_id"])
                    existing_rule = self.db.query(QuotationPricingRule).filter(
                        QuotationPricingRule.id == rule_id
                    ).first()
                    
                    if not existing_rule:
                        errors.append(f"Rule {rule_id} not found in system")
                        continue
                    
                    # Check if already associated (if not overwriting)
                    if not overwrite_existing:
                        existing_association = self.db.query(QuotationPricingProfileRule).filter(
                            and_(
                                QuotationPricingProfileRule.profile_id == profile_id,
                                QuotationPricingProfileRule.rule_id == rule_id,
                                QuotationPricingProfileRule.archived_at.is_(None)
                            )
                        ).first()
                        
                        if existing_association:
                            skipped_rules.append(str(rule_id))
                            continue
                    
                    # Create profile-rule relationship
                    profile_rule = self.create_profile_rule(
                        profile_id=profile_id,
                        rule_id=rule_id,
                        order_index=rule_config.get("order_index", 0),
                        is_active=rule_config.get("is_active", True),
                        created_by=created_by
                    )
                    
                    imported_rules.append(str(rule_id))
                    
                except Exception as e:
                    errors.append(f"Error importing rule {rule_config.get('rule_id', 'unknown')}: {str(e)}")
            
            return {
                "import_successful": len(errors) == 0,
                "total_rules_processed": len(import_data.get("rules", [])),
                "imported_rules": imported_rules,
                "skipped_rules": skipped_rules,
                "errors": errors,
                "import_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to import profile rules: {str(e)}")
    
    # ============================================================================
    # SEARCH AND FILTER OPERATIONS
    # ============================================================================
    
    def search_profile_rules(
        self,
        profile_id: UUID = None,
        rule_name: str = None,
        field_name: str = None,
        insurance_type: str = None,
        impact_type: str = None,
        is_active: bool = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search profile rules with various filters.
        
        Args:
            profile_id: Filter by profile ID (optional)
            rule_name: Filter by rule name (partial match)
            field_name: Filter by field name
            insurance_type: Filter by insurance type
            impact_type: Filter by impact type
            is_active: Filter by active status
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Dictionary with search results and pagination info
        """
        query = self.db.query(QuotationPricingProfileRule)\
            .join(QuotationPricingRule)\
            .join(QuotationPricingProfile)\
            .options(
                joinedload(QuotationPricingProfileRule.rule),
                joinedload(QuotationPricingProfileRule.profile)
            )\
            .filter(QuotationPricingProfileRule.archived_at.is_(None))
        
        # Apply filters
        if profile_id:
            query = query.filter(QuotationPricingProfileRule.profile_id == profile_id)
        
        if rule_name:
            query = query.filter(QuotationPricingRule.name.ilike(f"%{rule_name}%"))
        
        if field_name:
            query = query.filter(QuotationPricingRule.field_name == field_name)
        
        if insurance_type:
            query = query.filter(QuotationPricingRule.insurance_type == insurance_type)
        
        if impact_type:
            query = query.filter(QuotationPricingRule.impact_type == impact_type)
        
        if is_active is not None:
            query = query.filter(QuotationPricingProfileRule.is_active == is_active)
        
        # Get total count before applying limit/offset
        total_count = query.count()
        
        # Apply pagination
        results = query.order_by(
            QuotationPricingProfile.name,
            QuotationPricingProfileRule.order_index
        ).limit(limit).offset(offset).all()
        
        # Format results
        formatted_results = []
        for pr in results:
            formatted_results.append({
                "profile_rule_id": pr.id,
                "profile": {
                    "id": pr.profile.id,
                    "name": pr.profile.name,
                    "code": pr.profile.code
                },
                "rule": {
                    "id": pr.rule.id,
                    "name": pr.rule.name,
                    "field_name": pr.rule.field_name,
                    "operator": pr.rule.operator,
                    "impact_type": pr.rule.impact_type,
                    "insurance_type": pr.rule.insurance_type
                },
                "order_index": pr.order_index,
                "is_active": pr.is_active,
                "created_at": pr.created_at.isoformat() if pr.created_at else None
            })
        
        return {
            "results": formatted_results,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_next": (offset + limit) < total_count,
                "has_previous": offset > 0
            },
            "filters_applied": {
                "profile_id": profile_id,
                "rule_name": rule_name,
                "field_name": field_name,
                "insurance_type": insurance_type,
                "impact_type": impact_type,
                "is_active": is_active
            }
        }
    
    def get_orphaned_rules(self) -> List[Dict[str, Any]]:
        """
        Find rules that are not associated with any active profiles.
        
        Returns:
            List of orphaned rules
        """
        # Get all rules that have no active profile associations
        subquery = self.db.query(QuotationPricingProfileRule.rule_id)\
            .filter(
                and_(
                    QuotationPricingProfileRule.is_active == True,
                    QuotationPricingProfileRule.archived_at.is_(None)
                )
            ).subquery()
        
        orphaned_rules = self.db.query(QuotationPricingRule)\
            .filter(~QuotationPricingRule.id.in_(subquery))\
            .filter(QuotationPricingRule.is_active == True)\
            .all()
        
        return [
            {
                "rule_id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "field_name": rule.field_name,
                "insurance_type": rule.insurance_type,
                "created_at": rule.created_at.isoformat() if rule.created_at else None
            }
            for rule in orphaned_rules
        ]
    
    def get_profile_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about profile-rule relationships.
        
        Returns:
            Dictionary with various statistics
        """
        # Total relationships
        total_relationships = self.db.query(QuotationPricingProfileRule)\
            .filter(QuotationPricingProfileRule.archived_at.is_(None))\
            .count()
        
        active_relationships = self.db.query(QuotationPricingProfileRule)\
            .filter(
                and_(
                    QuotationPricingProfileRule.is_active == True,
                    QuotationPricingProfileRule.archived_at.is_(None)
                )
            ).count()
        
        # Profiles with rules
        profiles_with_rules = self.db.query(QuotationPricingProfile.id)\
            .join(QuotationPricingProfileRule)\
            .filter(QuotationPricingProfileRule.archived_at.is_(None))\
            .distinct().count()
        
        # Rules in use
        rules_in_use = self.db.query(QuotationPricingRule.id)\
            .join(QuotationPricingProfileRule)\
            .filter(QuotationPricingProfileRule.archived_at.is_(None))\
            .distinct().count()
        
        # Average rules per profile
        avg_rules_per_profile = total_relationships / profiles_with_rules if profiles_with_rules > 0 else 0
        
        # Most used rules
        most_used_rules = self.db.query(
            QuotationPricingRule.name,
            func.count(QuotationPricingProfileRule.id).label('usage_count')
        )\
        .join(QuotationPricingProfileRule)\
        .filter(QuotationPricingProfileRule.archived_at.is_(None))\
        .group_by(QuotationPricingRule.id, QuotationPricingRule.name)\
        .order_by(desc('usage_count'))\
        .limit(10).all()
        
        return {
            "total_relationships": total_relationships,
            "active_relationships": active_relationships,
            "inactive_relationships": total_relationships - active_relationships,
            "profiles_with_rules": profiles_with_rules,
            "rules_in_use": rules_in_use,
            "average_rules_per_profile": round(avg_rules_per_profile, 2),
            "most_used_rules": [
                {"rule_name": rule.name, "usage_count": rule.usage_count}
                for rule in most_used_rules
            ],
            "statistics_timestamp": datetime.utcnow().isoformat()
        }
