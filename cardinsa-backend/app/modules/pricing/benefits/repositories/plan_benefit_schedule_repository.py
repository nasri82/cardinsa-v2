
"""
app/modules/benefits/repositories/plan_benefit_schedule_repository.py

Repository for managing plan benefit schedules.
Handles the master schedules that define benefit structures for insurance plans.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from app.modules.pricing.benefits.models.plan_benefit_schedule_model import PlanBenefitSchedule
from app.core.base_repository import BaseRepository
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class PlanBenefitScheduleRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """Repository for managing plan benefit schedules"""
    
    def __init__(self, db: Session):
        super().__init__(PlanBenefitSchedule, db)
    
    async def get_by_plan(self, plan_id: str) -> List[PlanBenefitSchedule]:
        """Get all benefit schedules for a plan"""
        try:
            return self.db.query(PlanBenefitSchedule).filter(
                and_(
                    PlanBenefitSchedule.plan_id == plan_id,
                    PlanBenefitSchedule.is_active == True
                )
            ).order_by(PlanBenefitSchedule.schedule_version, PlanBenefitSchedule.benefit_type_id).all()
        except Exception as e:
            logger.error(f"Error fetching schedules by plan: {str(e)}")
            raise
    
    async def get_current_schedule(self, plan_id: str) -> Optional[PlanBenefitSchedule]:
        """Get current active schedule for a plan"""
        try:
            current_date = datetime.utcnow().date()
            return self.db.query(PlanBenefitSchedule).filter(
                and_(
                    PlanBenefitSchedule.plan_id == plan_id,
                    PlanBenefitSchedule.effective_date <= current_date,
                    or_(
                        PlanBenefitSchedule.end_date.is_(None),
                        PlanBenefitSchedule.end_date > current_date
                    ),
                    PlanBenefitSchedule.is_active == True
                )
            ).order_by(desc(PlanBenefitSchedule.schedule_version)).first()
        except Exception as e:
            logger.error(f"Error fetching current schedule: {str(e)}")
            raise
    
    async def get_by_schedule_type(self, schedule_type: str) -> List[PlanBenefitSchedule]:
        """Get schedules by type (standard, premium, basic)"""
        try:
            return self.db.query(PlanBenefitSchedule).filter(
                and_(
                    PlanBenefitSchedule.schedule_type == schedule_type,
                    PlanBenefitSchedule.is_active == True
                )
            ).order_by(PlanBenefitSchedule.plan_id, PlanBenefitSchedule.schedule_version).all()
        except Exception as e:
            logger.error(f"Error fetching schedules by type: {str(e)}")
            raise
    
    async def get_schedule_with_benefits(self, schedule_id: str) -> Optional[PlanBenefitSchedule]:
        """Get schedule with all benefit details"""
        try:
            return self.db.query(PlanBenefitSchedule).options(
                joinedload(PlanBenefitSchedule.benefit_type),
                joinedload(PlanBenefitSchedule.plan)
            ).filter(PlanBenefitSchedule.id == schedule_id).first()
        except Exception as e:
            logger.error(f"Error fetching schedule with benefits: {str(e)}")
            raise
    
    async def get_by_benefit_type(self, benefit_type_id: str) -> List[PlanBenefitSchedule]:
        """Get all schedules for a specific benefit type"""
        try:
            return self.db.query(PlanBenefitSchedule).filter(
                and_(
                    PlanBenefitSchedule.benefit_type_id == benefit_type_id,
                    PlanBenefitSchedule.is_active == True
                )
            ).order_by(PlanBenefitSchedule.plan_id, PlanBenefitSchedule.schedule_version).all()
        except Exception as e:
            logger.error(f"Error fetching schedules by benefit type: {str(e)}")
            raise
    
    async def get_pending_schedules(self) -> List[PlanBenefitSchedule]:
        """Get schedules with future effective dates"""
        try:
            current_date = datetime.utcnow().date()
            return self.db.query(PlanBenefitSchedule).filter(
                and_(
                    PlanBenefitSchedule.effective_date > current_date,
                    PlanBenefitSchedule.is_active == True
                )
            ).order_by(PlanBenefitSchedule.effective_date).all()
        except Exception as e:
            logger.error(f"Error fetching pending schedules: {str(e)}")
            raise