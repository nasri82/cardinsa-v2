# app/modules/pricing/plans/repositories/plan_repository.py

"""
Plan Repository - Production Ready

Data access layer for Plan operations.
Handles all database interactions for insurance plans.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import and_, or_, func, select, update, delete, case, text
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.modules.pricing.plans.models.plan_model import Plan, PlanStatus, PlanType, PlanTier
from app.modules.pricing.plans.models.plan_version_model import PlanVersion
from app.modules.pricing.plans.models.plan_territory_model import PlanTerritory
from app.modules.pricing.plans.models.plan_coverage_link_model import PlanCoverageLink
from app.modules.pricing.plans.models.plan_exclusion_model import PlanExclusion
from app.modules.pricing.plans.models.plan_eligibility_rule_model import PlanEligibilityRule

from app.core.exceptions import DatabaseOperationError, EntityNotFoundError
import logging

logger = logging.getLogger(__name__)


class PlanRepository:
    """Repository for Plan database operations"""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    # ================================================================
    # CREATE OPERATIONS
    # ================================================================
    
    def create(self, plan_data: Dict[str, Any], created_by: Optional[UUID] = None) -> Plan:
        """
        Create a new plan
        
        Args:
            plan_data: Plan data dictionary
            created_by: User ID creating the plan
            
        Returns:
            Created plan instance
            
        Raises:
            DatabaseOperationError: If creation fails
        """
        try:
            # Add metadata
            plan_data['created_by'] = created_by
            plan_data['created_at'] = datetime.utcnow()
            plan_data['status'] = plan_data.get('status', PlanStatus.DRAFT.value)
            plan_data['version'] = 1
            
            # Create plan instance
            plan = Plan(**plan_data)
            
            self.db.add(plan)
            self.db.commit()
            self.db.refresh(plan)
            
            # Create initial version
            self._create_initial_version(plan, created_by)
            
            logger.info(f"Created plan: {plan.id} - {plan.name}")
            return plan
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error creating plan: {str(e)}")
            raise DatabaseOperationError(f"Plan with code already exists")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating plan: {str(e)}")
            raise DatabaseOperationError(f"Failed to create plan: {str(e)}")
    
    def _create_initial_version(self, plan: Plan, created_by: Optional[UUID] = None) -> None:
        """Create initial version record for plan"""
        try:
            version = PlanVersion(
                plan_id=plan.id,
                version_number=1,
                version_label="1.0.0",
                version_description="Initial version",
                change_type="major",
                changes_summary="Initial plan creation",
                status="approved",
                is_current_version=True,
                effective_date=datetime.utcnow(),
                created_by=created_by,
                plan_snapshot=plan.to_dict()
            )
            self.db.add(version)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error creating initial version: {str(e)}")
    
    # ================================================================
    # READ OPERATIONS
    # ================================================================
    
    def get_by_id(
        self,
        plan_id: UUID,
        include_deleted: bool = False,
        load_relationships: bool = False
    ) -> Optional[Plan]:
        """
        Get plan by ID
        
        Args:
            plan_id: Plan UUID
            include_deleted: Include soft-deleted plans
            load_relationships: Load related data
            
        Returns:
            Plan instance or None
        """
        query = self.db.query(Plan).filter(Plan.id == plan_id)
        
        if not include_deleted:
            query = query.filter(Plan.archived_at.is_(None))
        
        if load_relationships:
            query = query.options(
                selectinload(Plan.benefit_schedules),
                selectinload(Plan.coverage_links),
                selectinload(Plan.territories),
                selectinload(Plan.exclusions),
                selectinload(Plan.eligibility_rules)
            )
        
        return query.first()
    
    def get_by_code(
        self,
        plan_code: str,
        company_id: UUID,
        include_deleted: bool = False
    ) -> Optional[Plan]:
        """
        Get plan by code and company
        
        Args:
            plan_code: Plan code
            company_id: Company UUID
            include_deleted: Include soft-deleted plans
            
        Returns:
            Plan instance or None
        """
        query = self.db.query(Plan).filter(
            Plan.plan_code == plan_code,
            Plan.company_id == company_id
        )
        
        if not include_deleted:
            query = query.filter(Plan.archived_at.is_(None))
        
        return query.first()
    
    def get_by_product(
        self,
        product_id: UUID,
        is_active: Optional[bool] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Plan]:
        """
        Get all plans for a product
        
        Args:
            product_id: Product UUID
            is_active: Filter by active status
            status: Filter by plan status
            limit: Maximum records
            offset: Skip records
            
        Returns:
            List of plans
        """
        query = self.db.query(Plan).filter(
            Plan.product_id == product_id,
            Plan.archived_at.is_(None)
        )
        
        if is_active is not None:
            query = query.filter(Plan.is_active == is_active)
        
        if status:
            query = query.filter(Plan.status == status)
        
        return query.order_by(Plan.created_at.desc()).offset(offset).limit(limit).all()
    
    def search(
        self,
        filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> Tuple[List[Plan], int]:
        """
        Search plans with filters
        
        Args:
            filters: Search filters
            limit: Maximum records
            offset: Skip records
            sort_by: Sort field
            sort_order: Sort direction
            
        Returns:
            Tuple of (plans list, total count)
        """
        query = self.db.query(Plan).filter(Plan.archived_at.is_(None))
        
        # Apply filters
        if filters.get('product_id'):
            query = query.filter(Plan.product_id == filters['product_id'])
        
        if filters.get('company_id'):
            query = query.filter(Plan.company_id == filters['company_id'])
        
        if filters.get('plan_type'):
            query = query.filter(Plan.plan_type == filters['plan_type'])
        
        if filters.get('plan_tier'):
            query = query.filter(Plan.plan_tier == filters['plan_tier'])
        
        if filters.get('status'):
            query = query.filter(Plan.status == filters['status'])
        
        if filters.get('is_active') is not None:
            query = query.filter(Plan.is_active == filters['is_active'])
        
        if filters.get('search_term'):
            search = f"%{filters['search_term']}%"
            query = query.filter(
                or_(
                    Plan.name.ilike(search),
                    Plan.plan_code.ilike(search),
                    Plan.description.ilike(search)
                )
            )
        
        # Premium range filters
        if filters.get('min_premium'):
            query = query.filter(Plan.premium_amount >= filters['min_premium'])
        
        if filters.get('max_premium'):
            query = query.filter(Plan.premium_amount <= filters['max_premium'])
        
        # Date filters
        if filters.get('effective_date_from'):
            query = query.filter(Plan.effective_date >= filters['effective_date_from'])
        
        if filters.get('effective_date_to'):
            query = query.filter(Plan.effective_date <= filters['effective_date_to'])
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if hasattr(Plan, sort_by):
            order_column = getattr(Plan, sort_by)
            if sort_order == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column)
        
        # Apply pagination
        plans = query.offset(offset).limit(limit).all()
        
        return plans, total
    
    def get_active_plans(
        self,
        company_id: Optional[UUID] = None,
        product_id: Optional[UUID] = None,
        as_of_date: Optional[date] = None
    ) -> List[Plan]:
        """
        Get active plans
        
        Args:
            company_id: Filter by company
            product_id: Filter by product
            as_of_date: Active as of specific date
            
        Returns:
            List of active plans
        """
        as_of = as_of_date or date.today()
        
        query = self.db.query(Plan).filter(
            Plan.is_active == True,
            Plan.status == PlanStatus.ACTIVE.value,
            Plan.archived_at.is_(None),
            or_(
                Plan.effective_date.is_(None),
                Plan.effective_date <= as_of
            ),
            or_(
                Plan.expiry_date.is_(None),
                Plan.expiry_date >= as_of
            )
        )
        
        if company_id:
            query = query.filter(Plan.company_id == company_id)
        
        if product_id:
            query = query.filter(Plan.product_id == product_id)
        
        return query.all()
    
    # ================================================================
    # UPDATE OPERATIONS
    # ================================================================
    
    def update(
        self,
        plan_id: UUID,
        update_data: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Optional[Plan]:
        """
        Update plan
        
        Args:
            plan_id: Plan UUID
            update_data: Update data dictionary
            updated_by: User ID updating
            
        Returns:
            Updated plan or None
            
        Raises:
            DatabaseOperationError: If update fails
        """
        try:
            plan = self.get_by_id(plan_id)
            if not plan:
                return None
            
            # Track changes for versioning
            changes = self._track_changes(plan, update_data)
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(plan, key):
                    setattr(plan, key, value)
            
            # Update metadata
            plan.updated_by = updated_by
            plan.updated_at = datetime.utcnow()
            
            # Increment version if significant changes
            if self._is_significant_change(changes):
                plan.version += 1
                self._create_version(plan, changes, updated_by)
            
            self.db.commit()
            self.db.refresh(plan)
            
            logger.info(f"Updated plan: {plan_id}")
            return plan
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating plan {plan_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update plan: {str(e)}")
    
    def _track_changes(self, plan: Plan, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track changes for versioning"""
        changes = {}
        for key, new_value in update_data.items():
            if hasattr(plan, key):
                old_value = getattr(plan, key)
                if old_value != new_value:
                    changes[key] = {
                        'old': old_value,
                        'new': new_value
                    }
        return changes
    
    def _is_significant_change(self, changes: Dict[str, Any]) -> bool:
        """Determine if changes are significant enough for new version"""
        significant_fields = [
            'premium_amount', 'coverage_period_months', 
            'underwriting_guidelines', 'waiting_periods',
            'minimum_age', 'maximum_issue_age'
        ]
        return any(field in changes for field in significant_fields)
    
    def _create_version(
        self,
        plan: Plan,
        changes: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> None:
        """Create new version record"""
        try:
            # Mark current version as superseded
            current_version = self.db.query(PlanVersion).filter(
                PlanVersion.plan_id == plan.id,
                PlanVersion.is_current_version == True
            ).first()
            
            if current_version:
                current_version.is_current_version = False
                current_version.expiry_date = datetime.utcnow()
            
            # Create new version
            new_version = PlanVersion(
                plan_id=plan.id,
                version_number=plan.version,
                version_label=f"{plan.version}.0.0",
                version_description="Plan update",
                changes_from_previous=changes,
                status="approved",
                is_current_version=True,
                effective_date=datetime.utcnow(),
                created_by=updated_by,
                plan_snapshot=plan.to_dict()
            )
            self.db.add(new_version)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error creating version: {str(e)}")
    
    def update_status(
        self,
        plan_id: UUID,
        new_status: str,
        updated_by: Optional[UUID] = None,
        notes: Optional[str] = None
    ) -> Optional[Plan]:
        """
        Update plan status
        
        Args:
            plan_id: Plan UUID
            new_status: New status
            updated_by: User ID
            notes: Status change notes
            
        Returns:
            Updated plan or None
        """
        plan = self.get_by_id(plan_id)
        if not plan:
            return None
        
        old_status = plan.status
        plan.status = new_status
        plan.updated_by = updated_by
        plan.updated_at = datetime.utcnow()
        
        # Handle status-specific logic
        if new_status == PlanStatus.ACTIVE.value:
            plan.is_active = True
            if not plan.effective_date:
                plan.effective_date = date.today()
        elif new_status == PlanStatus.SUSPENDED.value:
            plan.is_active = False
        elif new_status == PlanStatus.DISCONTINUED.value:
            plan.is_active = False
            plan.end_date = date.today()
        
        # Log status change
        logger.info(f"Plan {plan_id} status changed from {old_status} to {new_status}")
        
        self.db.commit()
        self.db.refresh(plan)
        
        return plan
    
    # ================================================================
    # DELETE OPERATIONS
    # ================================================================
    
    def delete(
        self,
        plan_id: UUID,
        soft_delete: bool = True,
        deleted_by: Optional[UUID] = None
    ) -> bool:
        """
        Delete plan
        
        Args:
            plan_id: Plan UUID
            soft_delete: Use soft delete
            deleted_by: User ID deleting
            
        Returns:
            Success status
        """
        try:
            plan = self.get_by_id(plan_id)
            if not plan:
                return False
            
            if soft_delete:
                # Soft delete
                plan.archived_at = datetime.utcnow()
                plan.archived_by = deleted_by
                plan.is_active = False
                plan.status = PlanStatus.ARCHIVED.value
            else:
                # Hard delete (cascade will handle relationships)
                self.db.delete(plan)
            
            self.db.commit()
            logger.info(f"Deleted plan: {plan_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting plan {plan_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to delete plan: {str(e)}")
    
    # ================================================================
    # BULK OPERATIONS
    # ================================================================
    
    def bulk_update(
        self,
        plan_ids: List[UUID],
        update_data: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> int:
        """
        Bulk update plans
        
        Args:
            plan_ids: List of plan UUIDs
            update_data: Update data
            updated_by: User ID
            
        Returns:
            Number of updated plans
        """
        try:
            update_data['updated_by'] = updated_by
            update_data['updated_at'] = datetime.utcnow()
            
            updated = self.db.query(Plan).filter(
                Plan.id.in_(plan_ids),
                Plan.archived_at.is_(None)
            ).update(update_data, synchronize_session=False)
            
            self.db.commit()
            logger.info(f"Bulk updated {updated} plans")
            return updated
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk updating plans: {str(e)}")
            raise DatabaseOperationError(f"Failed to bulk update: {str(e)}")
    
    # ================================================================
    # RELATIONSHIP OPERATIONS
    # ================================================================
    
    def add_territory(
        self,
        plan_id: UUID,
        territory_data: Dict[str, Any],
        created_by: Optional[UUID] = None
    ) -> PlanTerritory:
        """Add territory to plan"""
        try:
            territory_data['plan_id'] = plan_id
            territory_data['created_by'] = created_by
            
            territory = PlanTerritory(**territory_data)
            self.db.add(territory)
            self.db.commit()
            self.db.refresh(territory)
            
            return territory
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding territory: {str(e)}")
            raise DatabaseOperationError(f"Failed to add territory: {str(e)}")
    
    def add_coverage_link(
        self,
        plan_id: UUID,
        coverage_data: Dict[str, Any],
        created_by: Optional[UUID] = None
    ) -> PlanCoverageLink:
        """Add coverage link to plan"""
        try:
            coverage_data['plan_id'] = plan_id
            coverage_data['created_by'] = created_by
            
            link = PlanCoverageLink(**coverage_data)
            self.db.add(link)
            self.db.commit()
            self.db.refresh(link)
            
            return link
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding coverage link: {str(e)}")
            raise DatabaseOperationError(f"Failed to add coverage: {str(e)}")
    
    def add_exclusion(
        self,
        plan_id: UUID,
        exclusion_data: Dict[str, Any],
        created_by: Optional[UUID] = None
    ) -> PlanExclusion:
        """Add exclusion to plan"""
        try:
            exclusion_data['plan_id'] = plan_id
            exclusion_data['created_by'] = created_by
            
            exclusion = PlanExclusion(**exclusion_data)
            self.db.add(exclusion)
            self.db.commit()
            self.db.refresh(exclusion)
            
            return exclusion
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding exclusion: {str(e)}")
            raise DatabaseOperationError(f"Failed to add exclusion: {str(e)}")
    
    def add_eligibility_rule(
        self,
        plan_id: UUID,
        rule_data: Dict[str, Any],
        created_by: Optional[UUID] = None
    ) -> PlanEligibilityRule:
        """Add eligibility rule to plan"""
        try:
            rule_data['plan_id'] = plan_id
            rule_data['created_by'] = created_by
            
            rule = PlanEligibilityRule(**rule_data)
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
            
            return rule
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding eligibility rule: {str(e)}")
            raise DatabaseOperationError(f"Failed to add rule: {str(e)}")
    
    # ================================================================
    # ANALYTICS & REPORTING
    # ================================================================
    
    def get_statistics(
        self,
        company_id: Optional[UUID] = None,
        product_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get plan statistics
        
        Args:
            company_id: Filter by company
            product_id: Filter by product
            
        Returns:
            Statistics dictionary
        """
        try:
            query = self.db.query(Plan).filter(Plan.archived_at.is_(None))
            
            if company_id:
                query = query.filter(Plan.company_id == company_id)
            
            if product_id:
                query = query.filter(Plan.product_id == product_id)
            
            # Total plans
            total = query.count()
            
            # Active plans
            active = query.filter(Plan.is_active == True).count()
            
            # By status
            status_counts = {}
            for status in PlanStatus:
                count = query.filter(Plan.status == status.value).count()
                status_counts[status.value] = count
            
            # By type
            type_counts = {}
            for plan_type in PlanType:
                count = query.filter(Plan.plan_type == plan_type.value).count()
                type_counts[plan_type.value] = count
            
            # Premium statistics
            premium_stats = self.db.query(
                func.min(Plan.premium_amount).label('min'),
                func.max(Plan.premium_amount).label('max'),
                func.avg(Plan.premium_amount).label('avg')
            ).filter(
                Plan.archived_at.is_(None)
            )
            
            if company_id:
                premium_stats = premium_stats.filter(Plan.company_id == company_id)
            
            if product_id:
                premium_stats = premium_stats.filter(Plan.product_id == product_id)
            
            premium_result = premium_stats.first()
            
            return {
                'total_plans': total,
                'active_plans': active,
                'inactive_plans': total - active,
                'by_status': status_counts,
                'by_type': type_counts,
                'premium_statistics': {
                    'minimum': float(premium_result.min) if premium_result.min else 0,
                    'maximum': float(premium_result.max) if premium_result.max else 0,
                    'average': float(premium_result.avg) if premium_result.avg else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting plan statistics: {str(e)}")
            return {}
    
    def compare_plans(self, plan_ids: List[UUID]) -> List[Dict[str, Any]]:
        """
        Compare multiple plans
        
        Args:
            plan_ids: List of plan UUIDs to compare
            
        Returns:
            List of plan comparison data
        """
        plans = self.db.query(Plan).filter(
            Plan.id.in_(plan_ids),
            Plan.archived_at.is_(None)
        ).options(
            selectinload(Plan.coverage_links),
            selectinload(Plan.benefit_schedules),
            selectinload(Plan.exclusions)
        ).all()
        
        comparison = []
        for plan in plans:
            comparison.append({
                'id': str(plan.id),
                'name': plan.name,
                'plan_type': plan.plan_type,
                'plan_tier': plan.plan_tier,
                'premium_amount': float(plan.premium_amount),
                'coverage_period_months': plan.coverage_period_months,
                'coverage_count': len(plan.coverage_links),
                'benefit_count': len(plan.benefit_schedules),
                'exclusion_count': len(plan.exclusions),
                'waiting_periods': plan.waiting_periods,
                'minimum_age': plan.minimum_age,
                'maximum_issue_age': plan.maximum_issue_age
            })
        
        return comparison