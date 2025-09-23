
"""
app/modules/benefits/repositories/benefit_limit_repository.py

Repository for managing benefit limits and restrictions.
Handles annual limits, visit limits, dollar limits, and various restrictions.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from app.modules.pricing.benefits.models.benefit_limit_model import BenefitLimit
from app.core.base_repository import BaseRepository
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BenefitLimitRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """Repository for managing benefit limits"""
    
    def __init__(self, db: Session):
        super().__init__(BenefitLimit, db)
    
    async def get_by_benefit_type(self, benefit_type_id: str) -> List[BenefitLimit]:
        """Get all limits for a benefit type"""
        try:
            return self.db.query(BenefitLimit).filter(
                and_(
                    BenefitLimit.benefit_type_id == benefit_type_id,
                    BenefitLimit.is_active == True
                )
            ).order_by(BenefitLimit.limit_type, BenefitLimit.limit_period).all()
        except Exception as e:
            logger.error(f"Error fetching limits by benefit type: {str(e)}")
            raise
    
    async def get_by_limit_type(self, limit_type: str) -> List[BenefitLimit]:
        """Get limits by type (annual, lifetime, visit, etc.)"""
        try:
            return self.db.query(BenefitLimit).filter(
                and_(
                    BenefitLimit.limit_type == limit_type,
                    BenefitLimit.is_active == True
                )
            ).order_by(BenefitLimit.benefit_type_id).all()
        except Exception as e:
            logger.error(f"Error fetching limits by type: {str(e)}")
            raise
    
    async def get_annual_limits(self) -> List[BenefitLimit]:
        """Get all annual limits"""
        try:
            return self.db.query(BenefitLimit).filter(
                and_(
                    BenefitLimit.limit_period == "annual",
                    BenefitLimit.is_active == True
                )
            ).order_by(BenefitLimit.benefit_type_id).all()
        except Exception as e:
            logger.error(f"Error fetching annual limits: {str(e)}")
            raise
    
    async def get_by_coverage(self, coverage_id: str) -> List[BenefitLimit]:
        """Get all limits for a coverage plan"""
        try:
            return self.db.query(BenefitLimit).filter(
                and_(
                    BenefitLimit.coverage_id == coverage_id,
                    BenefitLimit.is_active == True
                )
            ).order_by(BenefitLimit.limit_type, BenefitLimit.benefit_type_id).all()
        except Exception as e:
            logger.error(f"Error fetching limits by coverage: {str(e)}")
            raise
    
    async def check_limit_exceeded(self, benefit_type_id: str, coverage_id: str, 
                                 current_usage: Decimal) -> List[BenefitLimit]:
        """Check which limits would be exceeded by current usage"""
        try:
            limits = await self.get_by_benefit_type(benefit_type_id)
            exceeded_limits = []
            
            for limit in limits:
                if limit.coverage_id and limit.coverage_id != coverage_id:
                    continue
                    
                if limit.dollar_limit and current_usage > limit.dollar_limit:
                    exceeded_limits.append(limit)
                elif limit.visit_limit and current_usage > limit.visit_limit:
                    exceeded_limits.append(limit)
            
            return exceeded_limits
        except Exception as e:
            logger.error(f"Error checking limit exceeded: {str(e)}")
            raise

