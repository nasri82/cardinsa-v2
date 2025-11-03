# app/modules/plans/services/plan_territory_service.py
"""
Plan Territory Service

Business logic layer for Plan Territory operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.modules.pricing.plans.repositories.plan_territory_repository import PlanTerritoryRepository
from app.modules.pricing.plans.schemas.plan_territory_schema import (
    PlanTerritoryCreate,
    PlanTerritoryUpdate,
    PlanTerritoryResponse,
    TerritoryPremiumCalculation,
    TerritoryAnalytics
)
from app.modules.pricing.plans.models.plan_territory_model import TerritoryType, TerritoryStatus
from app.core.exceptions import EntityNotFoundError, BusinessLogicError, ValidationError
import logging

logger = logging.getLogger(__name__)

class PlanTerritoryService:
    """Service layer for Plan Territory operations"""
    
    def __init__(self, repository: PlanTerritoryRepository):
        self.repository = repository
    
    def create_territory(
        self,
        plan_id: UUID,
        territory_data: PlanTerritoryCreate,
        created_by: UUID
    ) -> PlanTerritoryResponse:
        """Create new territory"""
        # Validate territory doesn't already exist
        existing = self.repository.get_by_plan_and_code(
            plan_id, territory_data.territory_code
        )
        if existing:
            raise ValidationError(
                f"Territory code {territory_data.territory_code} already exists for this plan"
            )
        
        # Convert schema to dict and add plan_id
        create_dict = territory_data.dict()
        create_dict['plan_id'] = plan_id
        
        territory = self.repository.create(create_dict, created_by)
        return PlanTerritoryResponse.from_orm(territory)
    
    def get_territory(self, territory_id: UUID) -> PlanTerritoryResponse:
        """Get territory by ID"""
        territory = self.repository.get_by_id(territory_id)
        if not territory:
            raise EntityNotFoundError(f"Territory {territory_id} not found")
        
        return PlanTerritoryResponse.from_orm(territory)
    
    def get_territories_by_plan(
        self,
        plan_id: UUID,
        territory_type: Optional[TerritoryType] = None,
        status: Optional[TerritoryStatus] = None,
        effective_date: Optional[date] = None
    ) -> List[PlanTerritoryResponse]:
        """Get territories for a plan"""
        territories = self.repository.get_territories_by_plan(
            plan_id, territory_type, status, effective_date
        )
        return [PlanTerritoryResponse.from_orm(territory) for territory in territories]
    
    def update_territory(
        self,
        territory_id: UUID,
        update_data: PlanTerritoryUpdate,
        updated_by: UUID
    ) -> PlanTerritoryResponse:
        """Update territory"""
        territory = self.repository.get_by_id(territory_id)
        if not territory:
            raise EntityNotFoundError(f"Territory {territory_id} not found")
        
        update_dict = update_data.dict(exclude_unset=True, exclude_none=True)
        updated = self.repository.update(territory_id, update_dict, updated_by)
        
        if not updated:
            raise BusinessLogicError("Failed to update territory")
        
        return PlanTerritoryResponse.from_orm(updated)
    
    def delete_territory(self, territory_id: UUID) -> bool:
        """Delete territory"""
        success = self.repository.delete(territory_id)
        if not success:
            raise EntityNotFoundError(f"Territory {territory_id} not found")
        return success
    
    def calculate_premium(
        self,
        plan_id: UUID,
        calculation_request: TerritoryPremiumCalculation
    ) -> Dict[str, Any]:
        """Calculate territory-adjusted premium"""
        adjusted = self.repository.calculate_adjusted_premium(
            plan_id,
            calculation_request.territory_code,
            calculation_request.base_premium,
            calculation_request.coverage_types
        )
        
        return {
            'territory_code': calculation_request.territory_code,
            'base_premium': float(calculation_request.base_premium),
            'adjusted_premium': float(adjusted['adjusted_premium']),
            'rate_factor': float(adjusted['rate_factor']),
            'risk_level': adjusted['risk_level'],
            'adjustments_applied': len(calculation_request.coverage_types) > 0,
            'catastrophe_zone': adjusted['catastrophe_zone']
        }
    
    def get_territory_analytics(
        self,
        territory_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> TerritoryAnalytics:
        """Get territory analytics"""
        analytics_data = self.repository.get_territory_analytics(
            territory_id, date_from, date_to
        )
        
        return TerritoryAnalytics(
            territory_code=analytics_data['territory_code'],
            territory_name=analytics_data['territory_name'],
            active_policies=analytics_data['active_policies'],
            total_premium=analytics_data['total_premium'],
            loss_ratio=analytics_data['loss_ratio'],
            market_share=analytics_data['market_share'],
            risk_score=analytics_data['risk_score'],
            last_updated=analytics_data['last_updated']
        )
    
    def get_active_territories_by_jurisdiction(
        self,
        regulatory_jurisdiction: str
    ) -> List[PlanTerritoryResponse]:
        """Get active territories by regulatory jurisdiction"""
        territories = self.repository.get_active_territories(
            regulatory_jurisdiction=regulatory_jurisdiction
        )
        return [PlanTerritoryResponse.from_orm(territory) for territory in territories]
    
    def validate_territory_coverage(
        self,
        plan_id: UUID,
        postal_codes: List[str]
    ) -> Dict[str, Any]:
        """Validate if postal codes are covered by plan territories"""
        territories = self.repository.get_active_territories(plan_id=plan_id)
        
        covered_codes = set()
        uncovered_codes = set(postal_codes)
        territory_mapping = {}
        
        for territory in territories:
            if territory.postal_codes:
                territory_postal_codes = set(territory.postal_codes)
                covered_in_territory = territory_postal_codes.intersection(postal_codes)
                
                for code in covered_in_territory:
                    covered_codes.add(code)
                    uncovered_codes.discard(code)
                    territory_mapping[code] = {
                        'territory_code': territory.territory_code,
                        'territory_name': territory.territory_name,
                        'rate_factor': float(territory.rate_factor)
                    }
        
        return {
            'plan_id': str(plan_id),
            'total_requested': len(postal_codes),
            'covered_count': len(covered_codes),
            'uncovered_count': len(uncovered_codes),
            'coverage_percentage': round((len(covered_codes) / len(postal_codes)) * 100, 2),
            'covered_codes': list(covered_codes),
            'uncovered_codes': list(uncovered_codes),
            'territory_mapping': territory_mapping
        }
