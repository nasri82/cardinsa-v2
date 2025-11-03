# app/modules/pricing/plans/repositories/plan_coverage_link_repository.py
"""
Plan Coverage Link Repository

Data access layer for Plan Coverage Link operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.modules.pricing.plans.models.plan_coverage_link_model import (
    PlanCoverageLink,
    CoverageTier,
    LimitType,
    NetworkRestriction,
    CoverageStatus
)
from app.core.exceptions import DatabaseOperationError, EntityNotFoundError
import logging

logger = logging.getLogger(__name__)

class PlanCoverageLinkRepository:
    """Repository for Plan Coverage Link database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        link_data: Dict[str, Any],
        created_by: Optional[UUID] = None
    ) -> PlanCoverageLink:
        """Create a new coverage link"""
        try:
            link_data['created_by'] = created_by
            link_data['created_at'] = datetime.utcnow()
            
            coverage_link = PlanCoverageLink(**link_data)
            self.db.add(coverage_link)
            self.db.commit()
            self.db.refresh(coverage_link)
            
            logger.info(f"Created coverage link {coverage_link.id} for plan {coverage_link.plan_id}")
            return coverage_link
            
        except IntegrityError:
            self.db.rollback()
            raise DatabaseOperationError("Coverage already linked to this plan")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating coverage link: {str(e)}")
            raise DatabaseOperationError(f"Failed to create coverage link: {str(e)}")
    
    def bulk_create(
        self,
        links_data: List[Dict[str, Any]],
        created_by: Optional[UUID] = None
    ) -> List[PlanCoverageLink]:
        """Bulk create coverage links"""
        try:
            coverage_links = []
            for link_data in links_data:
                link_data['created_by'] = created_by
                link_data['created_at'] = datetime.utcnow()
                coverage_links.append(PlanCoverageLink(**link_data))
            
            self.db.add_all(coverage_links)
            self.db.commit()
            
            for link in coverage_links:
                self.db.refresh(link)
            
            logger.info(f"Bulk created {len(coverage_links)} coverage links")
            return coverage_links
            
        except IntegrityError:
            self.db.rollback()
            raise DatabaseOperationError("One or more coverages already linked to the plan")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk creating coverage links: {str(e)}")
            raise DatabaseOperationError(f"Failed to bulk create coverage links: {str(e)}")
    
    def get_by_id(self, link_id: UUID) -> Optional[PlanCoverageLink]:
        """Get coverage link by ID"""
        return self.db.query(PlanCoverageLink).options(
            joinedload(PlanCoverageLink.plan),
            joinedload(PlanCoverageLink.coverage)
        ).filter(
            PlanCoverageLink.id == link_id,
            PlanCoverageLink.archived_at.is_(None)
        ).first()
    
    def get_by_plan_and_coverage(
        self,
        plan_id: UUID,
        coverage_id: UUID
    ) -> Optional[PlanCoverageLink]:
        """Get coverage link by plan and coverage"""
        return self.db.query(PlanCoverageLink).filter(
            PlanCoverageLink.plan_id == plan_id,
            PlanCoverageLink.coverage_id == coverage_id,
            PlanCoverageLink.archived_at.is_(None)
        ).first()
    
    def get_by_plan(
        self,
        plan_id: UUID,
        is_mandatory: Optional[bool] = None,
        is_excluded: Optional[bool] = None,
        coverage_tier: Optional[CoverageTier] = None,
        effective_date: Optional[date] = None
    ) -> List[PlanCoverageLink]:
        """Get coverage links by plan with filters"""
        query = self.db.query(PlanCoverageLink).options(
            joinedload(PlanCoverageLink.coverage)
        ).filter(
            PlanCoverageLink.plan_id == plan_id,
            PlanCoverageLink.archived_at.is_(None)
        )
        
        if is_mandatory is not None:
            query = query.filter(PlanCoverageLink.is_mandatory == is_mandatory)
        
        if is_excluded is not None:
            query = query.filter(PlanCoverageLink.is_excluded == is_excluded)
        
        if coverage_tier:
            query = query.filter(PlanCoverageLink.coverage_tier == coverage_tier.value)
        
        if effective_date:
            query = query.filter(
                or_(
                    PlanCoverageLink.effective_date.is_(None),
                    PlanCoverageLink.effective_date <= effective_date
                ),
                or_(
                    PlanCoverageLink.expiry_date.is_(None),
                    PlanCoverageLink.expiry_date > effective_date
                )
            )
        
        return query.order_by(
            PlanCoverageLink.display_order,
            PlanCoverageLink.created_at
        ).all()
    
    def get_mandatory_coverages(self, plan_id: UUID) -> List[PlanCoverageLink]:
        """Get mandatory coverages for a plan"""
        return self.get_by_plan(plan_id, is_mandatory=True, is_excluded=False)
    
    def get_optional_coverages(self, plan_id: UUID) -> List[PlanCoverageLink]:
        """Get optional coverages for a plan"""
        return self.get_by_plan(plan_id, is_mandatory=False, is_excluded=False)
    
    def update(
        self,
        link_id: UUID,
        update_data: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Optional[PlanCoverageLink]:
        """Update coverage link"""
        coverage_link = self.get_by_id(link_id)
        if not coverage_link:
            return None
        
        try:
            update_data['updated_by'] = updated_by
            update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                if hasattr(coverage_link, field):
                    setattr(coverage_link, field, value)
            
            self.db.commit()
            self.db.refresh(coverage_link)
            
            logger.info(f"Updated coverage link {link_id}")
            return coverage_link
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating coverage link {link_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update coverage link: {str(e)}")
    
    def delete(self, link_id: UUID) -> bool:
        """Soft delete coverage link"""
        coverage_link = self.get_by_id(link_id)
        if not coverage_link:
            return False
        
        try:
            coverage_link.archived_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted coverage link {link_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting coverage link {link_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to delete coverage link: {str(e)}")
    
    def get_coverage_summary(self, plan_id: UUID) -> Dict[str, Any]:
        """Get coverage summary for a plan"""
        links = self.get_by_plan(plan_id)
        
        summary = {
            'plan_id': str(plan_id),
            'total_coverages': len(links),
            'mandatory_coverages': sum(1 for link in links if link.is_mandatory),
            'excluded_coverages': sum(1 for link in links if link.is_excluded),
            'coverage_tiers': {},
            'network_restrictions': {}
        }
        
        # Count by tier
        for link in links:
            tier = link.coverage_tier
            summary['coverage_tiers'][tier] = summary['coverage_tiers'].get(tier, 0) + 1
            
            # Count by network restriction
            restriction = link.network_restrictions
            summary['network_restrictions'][restriction] = summary['network_restrictions'].get(restriction, 0) + 1
        
        return summary
    
    def calculate_total_coverage_value(self, plan_id: UUID) -> Decimal:
        """Calculate total coverage value for a plan"""
        result = self.db.query(
            func.sum(PlanCoverageLink.coverage_amount)
        ).filter(
            PlanCoverageLink.plan_id == plan_id,
            PlanCoverageLink.is_excluded == False,
            PlanCoverageLink.archived_at.is_(None)
        ).scalar()
        
        return Decimal(str(result)) if result else Decimal('0')