"""
app/modules/benefits/repositories/benefit_type_repository.py

Repository for managing benefit types within categories.
Handles cost-sharing structures, deductibles, and copay information.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.modules.pricing.benefits.models.benefit_type_model import BenefitType
from app.core.base_repository import BaseRepository
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BenefitTypeRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """Repository for managing benefit types"""
    
    def __init__(self, db: Session):
        super().__init__(BenefitType, db)
    
    async def get_by_category(self, category_id: str) -> List[BenefitType]:
        """Get benefit types by category"""
        try:
            return self.db.query(BenefitType).filter(
                and_(
                    BenefitType.category_id == category_id,
                    BenefitType.is_active == True
                )
            ).order_by(BenefitType.display_order, BenefitType.name).all()
        except Exception as e:
            logger.error(f"Error fetching benefit types by category: {str(e)}")
            raise
    
    async def get_with_cost_sharing(self, benefit_type_id: str) -> Optional[BenefitType]:
        """Get benefit type with full cost-sharing details"""
        try:
            return self.db.query(BenefitType).options(
                joinedload(BenefitType.category)
            ).filter(BenefitType.id == benefit_type_id).first()
        except Exception as e:
            logger.error(f"Error fetching benefit type with cost sharing: {str(e)}")
            raise
    
    async def search_by_coverage_level(self, coverage_level: str) -> List[BenefitType]:
        """Search benefit types by coverage level"""
        try:
            return self.db.query(BenefitType).filter(
                and_(
                    BenefitType.coverage_level == coverage_level,
                    BenefitType.is_active == True
                )
            ).order_by(BenefitType.name).all()
        except Exception as e:
            logger.error(f"Error searching by coverage level: {str(e)}")
            raise
    
    async def get_with_deductible_range(self, min_deductible: Decimal, max_deductible: Decimal) -> List[BenefitType]:
        """Get benefit types within deductible range"""
        try:
            return self.db.query(BenefitType).filter(
                and_(
                    BenefitType.deductible >= min_deductible,
                    BenefitType.deductible <= max_deductible,
                    BenefitType.is_active == True
                )
            ).order_by(BenefitType.deductible).all()
        except Exception as e:
            logger.error(f"Error fetching by deductible range: {str(e)}")
            raise
    
    async def get_preventive_benefits(self) -> List[BenefitType]:
        """Get all preventive benefit types (usually 100% covered)"""
        try:
            return self.db.query(BenefitType).filter(
                and_(
                    BenefitType.is_preventive == True,
                    BenefitType.is_active == True
                )
            ).order_by(BenefitType.category_id, BenefitType.name).all()
        except Exception as e:
            logger.error(f"Error fetching preventive benefits: {str(e)}")
            raise
