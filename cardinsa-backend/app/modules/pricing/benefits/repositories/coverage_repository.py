"""
app/modules/benefits/repositories/coverage_repository.py

Repository for managing insurance coverage plans.
Handles network restrictions, coverage periods, and plan relationships.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from app.modules.pricing.benefits.models.coverage_model import Coverage
from app.core.base_repository import BaseRepository
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class CoverageRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """Repository for managing coverage plans"""
    
    def __init__(self, db: Session):
        super().__init__(Coverage, db)
    
    async def get_active_coverages(self) -> List[Coverage]:
        """Get all currently active coverages"""
        try:
            current_date = datetime.utcnow().date()
            return self.db.query(Coverage).filter(
                and_(
                    Coverage.is_active == True,
                    Coverage.effective_date <= current_date,
                    or_(
                        Coverage.termination_date.is_(None),
                        Coverage.termination_date > current_date
                    )
                )
            ).order_by(Coverage.name).all()
        except Exception as e:
            logger.error(f"Error fetching active coverages: {str(e)}")
            raise
    
    async def get_by_network(self, network_id: str) -> List[Coverage]:
        """Get coverages by network"""
        try:
            return self.db.query(Coverage).filter(
                and_(
                    Coverage.network_id == network_id,
                    Coverage.is_active == True
                )
            ).order_by(Coverage.name).all()
        except Exception as e:
            logger.error(f"Error fetching coverages by network: {str(e)}")
            raise
    
    async def get_by_coverage_type(self, coverage_type: str) -> List[Coverage]:
        """Get coverages by type (individual, family, etc.)"""
        try:
            return self.db.query(Coverage).filter(
                and_(
                    Coverage.coverage_type == coverage_type,
                    Coverage.is_active == True
                )
            ).order_by(Coverage.name).all()
        except Exception as e:
            logger.error(f"Error fetching coverages by type: {str(e)}")
            raise
    
    async def search_coverages(self, search_term: str) -> List[Coverage]:
        """Search coverages by name or description"""
        try:
            return self.db.query(Coverage).filter(
                and_(
                    Coverage.is_active == True,
                    or_(
                        Coverage.name.ilike(f"%{search_term}%"),
                        Coverage.description.ilike(f"%{search_term}%")
                    )
                )
            ).order_by(Coverage.name).all()
        except Exception as e:
            logger.error(f"Error searching coverages: {str(e)}")
            raise
    
    async def get_expiring_coverages(self, days_ahead: int = 30) -> List[Coverage]:
        """Get coverages expiring within specified days"""
        try:
            cutoff_date = datetime.utcnow().date()
            future_date = datetime.utcnow().date().replace(day=cutoff_date.day + days_ahead)
            
            return self.db.query(Coverage).filter(
                and_(
                    Coverage.is_active == True,
                    Coverage.termination_date.isnot(None),
                    Coverage.termination_date <= future_date,
                    Coverage.termination_date > cutoff_date
                )
            ).order_by(Coverage.termination_date).all()
        except Exception as e:
            logger.error(f"Error fetching expiring coverages: {str(e)}")
            raise
    
    async def get_coverage_with_options(self, coverage_id: str) -> Optional[Coverage]:
        """Get coverage with all its options"""
        try:
            return self.db.query(Coverage).options(
                joinedload(Coverage.coverage_options)
            ).filter(Coverage.id == coverage_id).first()
        except Exception as e:
            logger.error(f"Error fetching coverage with options: {str(e)}")
            raise
