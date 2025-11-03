
"""
app/modules/benefits/repositories/coverage_option_repository.py

Repository for managing coverage options and variants.
Handles different tiers, add-ons, and alternative coverage configurations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.modules.pricing.benefits.models.coverage_option_model import CoverageOption
from app.core.base_repository import BaseRepository
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CoverageOptionRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """Repository for managing coverage options"""
    
    def __init__(self, db: Session):
        super().__init__(CoverageOption, db)
    
    async def get_by_coverage(self, coverage_id: str) -> List[CoverageOption]:
        """Get all options for a specific coverage"""
        try:
            return self.db.query(CoverageOption).filter(
                and_(
                    CoverageOption.coverage_id == coverage_id,
                    CoverageOption.is_active == True
                )
            ).order_by(CoverageOption.display_order, CoverageOption.name).all()
        except Exception as e:
            logger.error(f"Error fetching coverage options: {str(e)}")
            raise
    
    async def get_by_option_type(self, option_type: str) -> List[CoverageOption]:
        """Get options by type (tier, addon, alternative)"""
        try:
            return self.db.query(CoverageOption).filter(
                and_(
                    CoverageOption.option_type == option_type,
                    CoverageOption.is_active == True
                )
            ).order_by(CoverageOption.name).all()
        except Exception as e:
            logger.error(f"Error fetching options by type: {str(e)}")
            raise
    
    async def get_available_addons(self, coverage_id: str) -> List[CoverageOption]:
        """Get available add-on options for coverage"""
        try:
            return self.db.query(CoverageOption).filter(
                and_(
                    CoverageOption.coverage_id == coverage_id,
                    CoverageOption.option_type == "addon",
                    CoverageOption.is_available == True,
                    CoverageOption.is_active == True
                )
            ).order_by(CoverageOption.additional_premium).all()
        except Exception as e:
            logger.error(f"Error fetching available addons: {str(e)}")
            raise
    
    async def get_by_premium_range(self, min_premium: Decimal, max_premium: Decimal) -> List[CoverageOption]:
        """Get options within premium range"""
        try:
            return self.db.query(CoverageOption).filter(
                and_(
                    CoverageOption.additional_premium >= min_premium,
                    CoverageOption.additional_premium <= max_premium,
                    CoverageOption.is_active == True
                )
            ).order_by(CoverageOption.additional_premium).all()
        except Exception as e:
            logger.error(f"Error fetching by premium range: {str(e)}")
            raise
    
    async def get_mandatory_options(self, coverage_id: str) -> List[CoverageOption]:
        """Get mandatory options for coverage"""
        try:
            return self.db.query(CoverageOption).filter(
                and_(
                    CoverageOption.coverage_id == coverage_id,
                    CoverageOption.is_mandatory == True,
                    CoverageOption.is_active == True
                )
            ).order_by(CoverageOption.display_order).all()
        except Exception as e:
            logger.error(f"Error fetching mandatory options: {str(e)}")
            raise
