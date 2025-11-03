# app/modules/pricing/plans/repositories/plan_exclusion_link_repository.py
"""
Plan Exclusion Link Repository

Data access layer for Plan Exclusion Link operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.modules.pricing.plans.models.plan_exclusion_link_model import (
    PlanExclusionLink,
    LinkStatus,
    ApplicationScope,
    OverrideType
)
from app.core.exceptions import DatabaseOperationError, EntityNotFoundError
import logging

logger = logging.getLogger(__name__)

class PlanExclusionLinkRepository:
    """Repository for Plan Exclusion Link database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        link_data: Dict[str, Any],
        created_by: Optional[UUID] = None
    ) -> PlanExclusionLink:
        """Create a new exclusion link"""
        try:
            link_data['created_by'] = created_by
            link_data['created_at'] = datetime.utcnow()
            
            exclusion_link = PlanExclusionLink(**link_data)
            self.db.add(exclusion_link)
            self.db.commit()
            self.db.refresh(exclusion_link)
            
            logger.info(f"Created exclusion link {exclusion_link.id} for plan {exclusion_link.plan_id}")
            return exclusion_link
            
        except IntegrityError:
            self.db.rollback()
            raise DatabaseOperationError("Exclusion already linked to this plan")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating exclusion link: {str(e)}")
            raise DatabaseOperationError(f"Failed to create exclusion link: {str(e)}")
    
    def bulk_create(
        self,
        links_data: List[Dict[str, Any]],
        created_by: Optional[UUID] = None
    ) -> List[PlanExclusionLink]:
        """Bulk create exclusion links"""
        try:
            exclusion_links = []
            for link_data in links_data:
                link_data['created_by'] = created_by
                link_data['created_at'] = datetime.utcnow()
                exclusion_links.append(PlanExclusionLink(**link_data))
            
            self.db.add_all(exclusion_links)
            self.db.commit()
            
            for link in exclusion_links:
                self.db.refresh(link)
            
            logger.info(f"Bulk created {len(exclusion_links)} exclusion links")
            return exclusion_links
            
        except IntegrityError:
            self.db.rollback()
            raise DatabaseOperationError("One or more exclusions already linked to the plan")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk creating exclusion links: {str(e)}")
            raise DatabaseOperationError(f"Failed to bulk create exclusion links: {str(e)}")
    
    def get_by_id(self, link_id: UUID) -> Optional[PlanExclusionLink]:
        """Get exclusion link by ID"""
        return self.db.query(PlanExclusionLink).options(
            joinedload(PlanExclusionLink.plan),
            joinedload(PlanExclusionLink.exclusion)
        ).filter(
            PlanExclusionLink.id == link_id,
            PlanExclusionLink.archived_at.is_(None)
        ).first()
    
    def get_by_plan_and_exclusion(
        self,
        plan_id: UUID,
        exclusion_id: UUID
    ) -> Optional[PlanExclusionLink]:
        """Get exclusion link by plan and exclusion"""
        return self.db.query(PlanExclusionLink).filter(
            PlanExclusionLink.plan_id == plan_id,
            PlanExclusionLink.exclusion_id == exclusion_id,
            PlanExclusionLink.archived_at.is_(None)
        ).first()
    
    def get_by_plan(
        self,
        plan_id: UUID,
        status: Optional[LinkStatus] = None,
        is_active: Optional[bool] = None,
        is_mandatory: Optional[bool] = None,
        application_scope: Optional[ApplicationScope] = None,
        override_type: Optional[OverrideType] = None,
        is_highlighted: Optional[bool] = None,
        effective_date: Optional[date] = None,
        display_category: Optional[str] = None
    ) -> List[PlanExclusionLink]:
        """Get exclusion links by plan with filters"""
        query = self.db.query(PlanExclusionLink).options(
            joinedload(PlanExclusionLink.exclusion)
        ).filter(
            PlanExclusionLink.plan_id == plan_id,
            PlanExclusionLink.archived_at.is_(None)
        )
        
        if status:
            query = query.filter(PlanExclusionLink.status == status.value)
        
        if is_active is not None:
            query = query.filter(PlanExclusionLink.is_active == is_active)
        
        if is_mandatory is not None:
            query = query.filter(PlanExclusionLink.is_mandatory == is_mandatory)
        
        if application_scope:
            query = query.filter(PlanExclusionLink.application_scope == application_scope.value)
        
        if override_type:
            query = query.filter(PlanExclusionLink.override_type == override_type.value)
        
        if is_highlighted is not None:
            query = query.filter(PlanExclusionLink.is_highlighted == is_highlighted)
        
        if display_category:
            query = query.filter(PlanExclusionLink.display_category == display_category)
        
        if effective_date:
            query = query.filter(
                or_(
                    PlanExclusionLink.effective_date.is_(None),
                    PlanExclusionLink.effective_date <= effective_date
                ),
                or_(
                    PlanExclusionLink.expiry_date.is_(None),
                    PlanExclusionLink.expiry_date > effective_date
                )
            )
        
        return query.order_by(
            PlanExclusionLink.display_order,
            PlanExclusionLink.created_at
        ).all()
    
    def get_effective_links(
        self,
        plan_id: UUID,
        check_date: Optional[date] = None
    ) -> List[PlanExclusionLink]:
        """Get effective exclusion links for a plan"""
        check_date = check_date or date.today()
        
        query = self.db.query(PlanExclusionLink).options(
            joinedload(PlanExclusionLink.exclusion)
        ).filter(
            PlanExclusionLink.plan_id == plan_id,
            PlanExclusionLink.is_active == True,
            PlanExclusionLink.status == LinkStatus.ACTIVE.value,
            PlanExclusionLink.archived_at.is_(None),
            or_(
                PlanExclusionLink.effective_date.is_(None),
                PlanExclusionLink.effective_date <= check_date
            ),
            or_(
                PlanExclusionLink.expiry_date.is_(None),
                PlanExclusionLink.expiry_date > check_date
            )
        )
        
        return query.order_by(PlanExclusionLink.display_order).all()
    
    def get_by_coverage(
        self,
        plan_id: UUID,
        coverage_id: UUID,
        check_date: Optional[date] = None
    ) -> List[PlanExclusionLink]:
        """Get exclusion links that apply to a specific coverage"""
        effective_links = self.get_effective_links(plan_id, check_date)
        
        applicable_links = []
        for link in effective_links:
            if link.applies_to_coverage(str(coverage_id)):
                applicable_links.append(link)
        
        return applicable_links
    
    def get_mandatory_links(self, plan_id: UUID) -> List[PlanExclusionLink]:
        """Get mandatory exclusion links for a plan"""
        return self.get_by_plan(plan_id, is_mandatory=True, is_active=True)
    
    def get_highlighted_links(self, plan_id: UUID) -> List[PlanExclusionLink]:
        """Get highlighted exclusion links for a plan"""
        return self.get_by_plan(plan_id, is_highlighted=True, is_active=True)
    
    def get_overridden_links(self, plan_id: UUID) -> List[PlanExclusionLink]:
        """Get exclusion links with overrides"""
        return self.get_by_plan(plan_id, override_type=OverrideType.CUSTOMIZED)
    
    def update(
        self,
        link_id: UUID,
        update_data: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Optional[PlanExclusionLink]:
        """Update exclusion link"""
        exclusion_link = self.get_by_id(link_id)
        if not exclusion_link:
            return None
        
        try:
            update_data['updated_by'] = updated_by
            update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                if hasattr(exclusion_link, field):
                    setattr(exclusion_link, field, value)
            
            self.db.commit()
            self.db.refresh(exclusion_link)
            
            logger.info(f"Updated exclusion link {link_id}")
            return exclusion_link
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating exclusion link {link_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update exclusion link: {str(e)}")
    
    def delete(self, link_id: UUID) -> bool:
        """Soft delete exclusion link"""
        exclusion_link = self.get_by_id(link_id)
        if not exclusion_link:
            return False
        
        try:
            exclusion_link.archived_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted exclusion link {link_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting exclusion link {link_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to delete exclusion link: {str(e)}")
    
    def get_link_summary(self, plan_id: UUID) -> Dict[str, Any]:
        """Get exclusion link summary for a plan"""
        links = self.get_by_plan(plan_id)
        
        summary = {
            'plan_id': str(plan_id),
            'total_links': len(links),
            'active_links': 0,
            'mandatory_links': 0,
            'by_status': {},
            'by_scope': {},
            'by_override_type': {},
            'highlighted_links': 0
        }
        
        for link in links:
            if link.is_active:
                summary['active_links'] += 1
            
            if link.is_mandatory:
                summary['mandatory_links'] += 1
            
            if link.is_highlighted:
                summary['highlighted_links'] += 1
            
            # Count by status
            status = link.status
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
            
            # Count by scope
            scope = link.application_scope
            summary['by_scope'][scope] = summary['by_scope'].get(scope, 0) + 1
            
            # Count by override type
            override_type = link.override_type
            summary['by_override_type'][override_type] = summary['by_override_type'].get(override_type, 0) + 1
        
        return summary