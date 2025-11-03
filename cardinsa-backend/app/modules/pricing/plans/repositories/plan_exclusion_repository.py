# app/modules/pricing/plans/repositories/plan_exclusion_repository.py
"""
Plan Exclusion Repository

Data access layer for Plan Exclusion operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.modules.pricing.plans.models.plan_exclusion_model import (
    PlanExclusion,
    ExclusionType,
    ExclusionCategory,
    ExclusionSeverity,
    RegulatoryBasis
)
from app.core.exceptions import DatabaseOperationError, EntityNotFoundError
import logging

logger = logging.getLogger(__name__)

class PlanExclusionRepository:
    """Repository for Plan Exclusion database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        exclusion_data: Dict[str, Any],
        created_by: Optional[UUID] = None
    ) -> PlanExclusion:
        """Create a new exclusion"""
        try:
            exclusion_data['created_by'] = created_by
            exclusion_data['created_at'] = datetime.utcnow()
            
            exclusion = PlanExclusion(**exclusion_data)
            self.db.add(exclusion)
            self.db.commit()
            self.db.refresh(exclusion)
            
            logger.info(f"Created exclusion {exclusion.id} for plan {exclusion.plan_id}")
            return exclusion
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating exclusion: {str(e)}")
            raise DatabaseOperationError(f"Failed to create exclusion: {str(e)}")
    
    def bulk_create(
        self,
        exclusions_data: List[Dict[str, Any]],
        created_by: Optional[UUID] = None
    ) -> List[PlanExclusion]:
        """Bulk create exclusions"""
        try:
            exclusions = []
            for exclusion_data in exclusions_data:
                exclusion_data['created_by'] = created_by
                exclusion_data['created_at'] = datetime.utcnow()
                exclusions.append(PlanExclusion(**exclusion_data))
            
            self.db.add_all(exclusions)
            self.db.commit()
            
            for exclusion in exclusions:
                self.db.refresh(exclusion)
            
            logger.info(f"Bulk created {len(exclusions)} exclusions")
            return exclusions
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk creating exclusions: {str(e)}")
            raise DatabaseOperationError(f"Failed to bulk create exclusions: {str(e)}")
    
    def get_by_id(self, exclusion_id: UUID) -> Optional[PlanExclusion]:
        """Get exclusion by ID"""
        return self.db.query(PlanExclusion).options(
            joinedload(PlanExclusion.plan),
            joinedload(PlanExclusion.cpt_code),
            joinedload(PlanExclusion.icd10_code)
        ).filter(
            PlanExclusion.id == exclusion_id,
            PlanExclusion.archived_at.is_(None)
        ).first()
    
    def get_by_plan(
        self,
        plan_id: UUID,
        exclusion_type: Optional[ExclusionType] = None,
        exclusion_category: Optional[ExclusionCategory] = None,
        exclusion_severity: Optional[ExclusionSeverity] = None,
        is_highlighted: Optional[bool] = None,
        effective_date: Optional[date] = None,
        text_search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[PlanExclusion]:
        """Get exclusions by plan with filters"""
        query = self.db.query(PlanExclusion).filter(
            PlanExclusion.plan_id == plan_id,
            PlanExclusion.archived_at.is_(None)
        )
        
        if exclusion_type:
            query = query.filter(PlanExclusion.exclusion_type == exclusion_type.value)
        
        if exclusion_category:
            query = query.filter(PlanExclusion.exclusion_category == exclusion_category.value)
        
        if exclusion_severity:
            query = query.filter(PlanExclusion.exclusion_severity == exclusion_severity.value)
        
        if is_highlighted is not None:
            query = query.filter(PlanExclusion.is_highlighted == is_highlighted)
        
        if effective_date:
            query = query.filter(
                or_(
                    PlanExclusion.effective_date.is_(None),
                    PlanExclusion.effective_date <= effective_date
                ),
                or_(
                    PlanExclusion.expiry_date.is_(None),
                    PlanExclusion.expiry_date > effective_date
                )
            )
        
        if text_search:
            search_term = f"%{text_search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(PlanExclusion.exclusion_text).like(search_term),
                    func.lower(PlanExclusion.member_facing_text).like(search_term),
                    func.lower(PlanExclusion.exclusion_code).like(search_term)
                )
            )
        
        if tags:
            # PostgreSQL JSONB array contains operation
            for tag in tags:
                query = query.filter(PlanExclusion.tags.op('@>')([tag]))
        
        return query.order_by(
            PlanExclusion.display_order,
            PlanExclusion.exclusion_type,
            PlanExclusion.created_at
        ).all()
    
    def get_active_exclusions(
        self,
        plan_id: UUID,
        check_date: Optional[date] = None
    ) -> List[PlanExclusion]:
        """Get active exclusions for a plan"""
        check_date = check_date or date.today()
        
        query = self.db.query(PlanExclusion).filter(
            PlanExclusion.plan_id == plan_id,
            PlanExclusion.archived_at.is_(None),
            or_(
                PlanExclusion.effective_date.is_(None),
                PlanExclusion.effective_date <= check_date
            ),
            or_(
                PlanExclusion.expiry_date.is_(None),
                PlanExclusion.expiry_date > check_date
            )
        )
        
        return query.order_by(PlanExclusion.display_order).all()
    
    def get_highlighted_exclusions(self, plan_id: UUID) -> List[PlanExclusion]:
        """Get highlighted exclusions for a plan"""
        return self.get_by_plan(plan_id, is_highlighted=True)
    
    def get_waiverable_exclusions(self, plan_id: UUID) -> List[PlanExclusion]:
        """Get waiverable exclusions for a plan"""
        return self.get_by_plan(plan_id, exclusion_severity=ExclusionSeverity.WAIVERABLE)
    
    def get_by_medical_codes(
        self,
        plan_id: UUID,
        cpt_codes: Optional[List[UUID]] = None,
        icd10_codes: Optional[List[UUID]] = None
    ) -> List[PlanExclusion]:
        """Get exclusions by medical codes"""
        query = self.db.query(PlanExclusion).filter(
            PlanExclusion.plan_id == plan_id,
            PlanExclusion.archived_at.is_(None)
        )
        
        if cpt_codes:
            query = query.filter(PlanExclusion.cpt_code_id.in_(cpt_codes))
        
        if icd10_codes:
            query = query.filter(PlanExclusion.icd10_code_id.in_(icd10_codes))
        
        return query.all()
    
    def update(
        self,
        exclusion_id: UUID,
        update_data: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Optional[PlanExclusion]:
        """Update exclusion"""
        exclusion = self.get_by_id(exclusion_id)
        if not exclusion:
            return None
        
        try:
            update_data['updated_by'] = updated_by
            update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                if hasattr(exclusion, field):
                    setattr(exclusion, field, value)
            
            self.db.commit()
            self.db.refresh(exclusion)
            
            logger.info(f"Updated exclusion {exclusion_id}")
            return exclusion
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating exclusion {exclusion_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update exclusion: {str(e)}")
    
    def delete(self, exclusion_id: UUID) -> bool:
        """Soft delete exclusion"""
        exclusion = self.get_by_id(exclusion_id)
        if not exclusion:
            return False
        
        try:
            exclusion.archived_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted exclusion {exclusion_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting exclusion {exclusion_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to delete exclusion: {str(e)}")
    
    def get_exclusion_summary(self, plan_id: UUID) -> Dict[str, Any]:
        """Get exclusion summary for a plan"""
        exclusions = self.get_by_plan(plan_id)
        
        summary = {
            'plan_id': str(plan_id),
            'total_exclusions': len(exclusions),
            'by_type': {},
            'by_category': {},
            'by_severity': {},
            'highlighted_exclusions': 0,
            'temporary_exclusions': 0,
            'waiverable_exclusions': 0
        }
        
        for exclusion in exclusions:
            # Count by type
            ex_type = exclusion.exclusion_type
            summary['by_type'][ex_type] = summary['by_type'].get(ex_type, 0) + 1
            
            # Count by category
            ex_category = exclusion.exclusion_category
            summary['by_category'][ex_category] = summary['by_category'].get(ex_category, 0) + 1
            
            # Count by severity
            ex_severity = exclusion.exclusion_severity
            summary['by_severity'][ex_severity] = summary['by_severity'].get(ex_severity, 0) + 1
            
            # Count special types
            if exclusion.is_highlighted:
                summary['highlighted_exclusions'] += 1
            
            if exclusion.is_temporary():
                summary['temporary_exclusions'] += 1
            
            if exclusion.is_waiverable():
                summary['waiverable_exclusions'] += 1
        
        return summary
    
    def search_exclusions(
        self,
        plan_id: UUID,
        search_term: str,
        limit: int = 50
    ) -> List[PlanExclusion]:
        """Search exclusions by text"""
        search_pattern = f"%{search_term.lower()}%"
        
        query = self.db.query(PlanExclusion).filter(
            PlanExclusion.plan_id == plan_id,
            PlanExclusion.archived_at.is_(None),
            or_(
                func.lower(PlanExclusion.exclusion_text).like(search_pattern),
                func.lower(PlanExclusion.member_facing_text).like(search_pattern),
                func.lower(PlanExclusion.exclusion_code).like(search_pattern),
                func.lower(PlanExclusion.notes).like(search_pattern)
            )
        ).limit(limit)
        
        return query.all()