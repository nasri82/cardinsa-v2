# app/modules/plans/repositories/plan_territory_repository.py
"""
Plan Territory Repository

Data access layer for Plan Territory operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.modules.pricing.plans.models.plan_territory_model import (
    PlanTerritory,
    TerritoryType,
    TerritoryStatus,
    RegulatoryStatus
)
from app.core.exceptions import DatabaseOperationError, EntityNotFoundError
import logging

logger = logging.getLogger(__name__)

class PlanTerritoryRepository:
    """Repository for Plan Territory database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        territory_data: Dict[str, Any],
        created_by: Optional[UUID] = None
    ) -> PlanTerritory:
        """Create a new territory"""
        try:
            territory_data['created_by'] = created_by
            territory_data['created_at'] = datetime.utcnow()
            territory_data['version'] = 1
            
            territory = PlanTerritory(**territory_data)
            self.db.add(territory)
            self.db.commit()
            self.db.refresh(territory)
            
            logger.info(f"Created territory {territory.territory_code} for plan {territory.plan_id}")
            return territory
            
        except IntegrityError:
            self.db.rollback()
            raise DatabaseOperationError("Territory code already exists for this plan")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating territory: {str(e)}")
            raise DatabaseOperationError(f"Failed to create territory: {str(e)}")
    
    def get_by_id(self, territory_id: UUID) -> Optional[PlanTerritory]:
        """Get territory by ID"""
        return self.db.query(PlanTerritory).filter(
            PlanTerritory.id == territory_id,
            PlanTerritory.is_active == True
        ).first()
    
    def get_by_plan_and_code(self, plan_id: UUID, territory_code: str) -> Optional[PlanTerritory]:
        """Get territory by plan and territory code"""
        return self.db.query(PlanTerritory).filter(
            PlanTerritory.plan_id == plan_id,
            PlanTerritory.territory_code == territory_code,
            PlanTerritory.is_active == True
        ).first()
    
    def get_territories_by_plan(
        self,
        plan_id: UUID,
        territory_type: Optional[TerritoryType] = None,
        status: Optional[TerritoryStatus] = None,
        effective_date: Optional[date] = None
    ) -> List[PlanTerritory]:
        """Get territories by plan with optional filters"""
        query = self.db.query(PlanTerritory).filter(
            PlanTerritory.plan_id == plan_id,
            PlanTerritory.is_active == True
        )
        
        if territory_type:
            query = query.filter(PlanTerritory.territory_type == territory_type)
        
        if status:
            query = query.filter(PlanTerritory.status == status)
        
        if effective_date:
            query = query.filter(
                PlanTerritory.effective_date <= effective_date,
                or_(
                    PlanTerritory.expiry_date.is_(None),
                    PlanTerritory.expiry_date > effective_date
                )
            )
        
        return query.order_by(PlanTerritory.territory_code).all()
    
    def get_active_territories(
        self,
        plan_id: Optional[UUID] = None,
        regulatory_jurisdiction: Optional[str] = None
    ) -> List[PlanTerritory]:
        """Get active territories with optional filters"""
        query = self.db.query(PlanTerritory).filter(
            PlanTerritory.is_active == True,
            PlanTerritory.status == TerritoryStatus.ACTIVE,
            or_(
                PlanTerritory.expiry_date.is_(None),
                PlanTerritory.expiry_date > func.current_date()
            )
        )
        
        if plan_id:
            query = query.filter(PlanTerritory.plan_id == plan_id)
        
        if regulatory_jurisdiction:
            query = query.filter(
                PlanTerritory.regulatory_jurisdiction == regulatory_jurisdiction
            )
        
        return query.order_by(PlanTerritory.territory_code).all()
    
    def update(
        self,
        territory_id: UUID,
        update_data: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Optional[PlanTerritory]:
        """Update territory"""
        territory = self.get_by_id(territory_id)
        if not territory:
            return None
        
        try:
            # Update version and audit fields
            update_data['updated_by'] = updated_by
            update_data['updated_at'] = datetime.utcnow()
            update_data['version'] = territory.version + 1
            
            for field, value in update_data.items():
                if hasattr(territory, field):
                    setattr(territory, field, value)
            
            self.db.commit()
            self.db.refresh(territory)
            
            logger.info(f"Updated territory {territory.territory_code}")
            return territory
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating territory {territory_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update territory: {str(e)}")
    
    def delete(self, territory_id: UUID) -> bool:
        """Soft delete territory"""
        territory = self.get_by_id(territory_id)
        if not territory:
            return False
        
        try:
            territory.is_active = False
            territory.status = TerritoryStatus.ARCHIVED
            territory.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Deleted territory {territory.territory_code}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting territory {territory_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to delete territory: {str(e)}")
    
    def calculate_adjusted_premium(
        self,
        plan_id: UUID,
        territory_code: str,
        base_premium: Decimal,
        coverage_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Calculate territory-adjusted premium"""
        territory = self.get_by_plan_and_code(plan_id, territory_code)
        if not territory:
            raise EntityNotFoundError(f"Territory {territory_code} not found for plan {plan_id}")
        
        # Apply base rate factor
        adjusted_premium = base_premium * territory.rate_factor
        
        # Apply additional rate adjustments
        if territory.rate_adjustments and coverage_types:
            for adjustment in territory.rate_adjustments:
                if adjustment.get('coverage_type') in coverage_types:
                    if adjustment['adjustment_type'] == 'multiplier':
                        adjusted_premium *= Decimal(str(adjustment['value']))
                    elif adjustment['adjustment_type'] == 'additive':
                        adjusted_premium += Decimal(str(adjustment['value']))
                    elif adjustment['adjustment_type'] == 'percentage':
                        adjusted_premium *= (1 + Decimal(str(adjustment['value'])) / 100)
        
        # Apply min/max limits
        if territory.minimum_premium and adjusted_premium < territory.minimum_premium:
            adjusted_premium = territory.minimum_premium
        
        if territory.maximum_premium and adjusted_premium > territory.maximum_premium:
            adjusted_premium = territory.maximum_premium
        
        return {
            'territory_code': territory_code,
            'base_premium': base_premium,
            'rate_factor': territory.rate_factor,
            'adjusted_premium': adjusted_premium,
            'risk_level': territory.risk_level,
            'catastrophe_zone': territory.catastrophe_zone
        }
    
    def get_territory_analytics(
        self,
        territory_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get territory analytics data"""
        # This would typically involve complex queries across multiple tables
        # For now, returning a placeholder structure
        territory = self.get_by_id(territory_id)
        if not territory:
            raise EntityNotFoundError(f"Territory {territory_id} not found")
        
        # Placeholder analytics - would be replaced with actual queries
        return {
            'territory_id': territory_id,
            'territory_code': territory.territory_code,
            'territory_name': territory.territory_name,
            'active_policies': 0,  # Would query from policies table
            'total_premium': Decimal('0.00'),  # Would sum from policies
            'loss_ratio': Decimal('0.00'),  # Would calculate from claims
            'market_share': territory.market_penetration or Decimal('0.00'),
            'risk_score': self._calculate_risk_score(territory),
            'last_updated': datetime.utcnow()
        }
    
    def _calculate_risk_score(self, territory: PlanTerritory) -> Decimal:
        """Calculate risk score based on territory characteristics"""
        base_score = Decimal('1.0')
        
        # Adjust based on risk level
        risk_multipliers = {
            'low': Decimal('0.8'),
            'standard': Decimal('1.0'),
            'high': Decimal('1.3'),
            'extreme': Decimal('1.6')
        }
        base_score *= risk_multipliers.get(territory.risk_level, Decimal('1.0'))
        
        # Add catastrophe zone adjustments
        if territory.catastrophe_zone:
            base_score *= Decimal('1.2')
        if territory.flood_zone:
            base_score *= Decimal('1.1')
        if territory.earthquake_zone:
            base_score *= Decimal('1.15')
        if territory.hurricane_zone:
            base_score *= Decimal('1.1')
        
        return round(base_score, 2)