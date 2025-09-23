# app/modules/pricing/plans/services/plan_coverage_link_service.py
"""
Plan Coverage Link Service

Business logic layer for Plan Coverage Link operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.modules.pricing.plans.repositories.plan_coverage_link_repository import PlanCoverageLinkRepository
from app.modules.pricing.plans.schemas.plan_coverage_link_schema import (
    PlanCoverageLinkCreate,
    PlanCoverageLinkUpdate,
    PlanCoverageLinkResponse,
    BulkCoverageLinkCreate,
    CoverageLinkSummary,
    CostCalculationRequest,
    CostCalculationResponse
)
from app.modules.pricing.plans.models.plan_coverage_link_model import CoverageTier
from app.core.exceptions import EntityNotFoundError, BusinessLogicError, ValidationError
import logging

logger = logging.getLogger(__name__)

class PlanCoverageLinkService:
    """Service layer for Plan Coverage Link operations"""
    
    def __init__(self, repository: PlanCoverageLinkRepository):
        self.repository = repository
    
    def create_coverage_link(
        self,
        plan_id: UUID,
        link_data: PlanCoverageLinkCreate,
        created_by: UUID
    ) -> PlanCoverageLinkResponse:
        """Create new coverage link"""
        # Validate coverage doesn't already exist for plan
        existing = self.repository.get_by_plan_and_coverage(
            plan_id, link_data.coverage_id
        )
        if existing:
            raise ValidationError("Coverage already linked to this plan")
        
        create_dict = link_data.dict()
        create_dict['plan_id'] = plan_id
        
        coverage_link = self.repository.create(create_dict, created_by)
        return PlanCoverageLinkResponse.from_orm(coverage_link)
    
    def bulk_create_coverage_links(
        self,
        plan_id: UUID,
        bulk_data: BulkCoverageLinkCreate,
        created_by: UUID
    ) -> List[PlanCoverageLinkResponse]:
        """Bulk create coverage links"""
        # Validate no duplicates in request
        coverage_ids = [link.coverage_id for link in bulk_data.coverage_links]
        if len(coverage_ids) != len(set(coverage_ids)):
            raise ValidationError("Duplicate coverage IDs in request")
        
        # Check for existing links
        existing_links = []
        for coverage_id in coverage_ids:
            if self.repository.get_by_plan_and_coverage(plan_id, coverage_id):
                existing_links.append(str(coverage_id))
        
        if existing_links:
            raise ValidationError(f"Coverages already linked: {', '.join(existing_links)}")
        
        links_data = []
        for link in bulk_data.coverage_links:
            link_dict = link.dict()
            link_dict['plan_id'] = plan_id
            links_data.append(link_dict)
        
        coverage_links = self.repository.bulk_create(links_data, created_by)
        return [PlanCoverageLinkResponse.from_orm(link) for link in coverage_links]
    
    def get_coverage_link(self, link_id: UUID) -> PlanCoverageLinkResponse:
        """Get coverage link by ID"""
        coverage_link = self.repository.get_by_id(link_id)
        if not coverage_link:
            raise EntityNotFoundError(f"Coverage link {link_id} not found")
        
        return PlanCoverageLinkResponse.from_orm(coverage_link)
    
    def get_plan_coverage_links(
        self,
        plan_id: UUID,
        is_mandatory: Optional[bool] = None,
        is_excluded: Optional[bool] = None,
        coverage_tier: Optional[CoverageTier] = None,
        effective_date: Optional[date] = None
    ) -> List[PlanCoverageLinkResponse]:
        """Get coverage links for a plan"""
        coverage_links = self.repository.get_by_plan(
            plan_id, is_mandatory, is_excluded, coverage_tier, effective_date
        )
        return [PlanCoverageLinkResponse.from_orm(link) for link in coverage_links]
    
    def get_mandatory_coverages(self, plan_id: UUID) -> List[PlanCoverageLinkResponse]:
        """Get mandatory coverages for a plan"""
        coverage_links = self.repository.get_mandatory_coverages(plan_id)
        return [PlanCoverageLinkResponse.from_orm(link) for link in coverage_links]
    
    def get_optional_coverages(self, plan_id: UUID) -> List[PlanCoverageLinkResponse]:
        """Get optional coverages for a plan"""
        coverage_links = self.repository.get_optional_coverages(plan_id)
        return [PlanCoverageLinkResponse.from_orm(link) for link in coverage_links]
    
    def update_coverage_link(
        self,
        link_id: UUID,
        update_data: PlanCoverageLinkUpdate,
        updated_by: UUID
    ) -> PlanCoverageLinkResponse:
        """Update coverage link"""
        coverage_link = self.repository.get_by_id(link_id)
        if not coverage_link:
            raise EntityNotFoundError(f"Coverage link {link_id} not found")
        
        update_dict = update_data.dict(exclude_unset=True, exclude_none=True)
        updated = self.repository.update(link_id, update_dict, updated_by)
        
        if not updated:
            raise BusinessLogicError("Failed to update coverage link")
        
        return PlanCoverageLinkResponse.from_orm(updated)
    
    def delete_coverage_link(self, link_id: UUID) -> bool:
        """Delete coverage link"""
        success = self.repository.delete(link_id)
        if not success:
            raise EntityNotFoundError(f"Coverage link {link_id} not found")
        return success
    
    def calculate_member_cost(
        self,
        link_id: UUID,
        calculation_request: CostCalculationRequest
    ) -> CostCalculationResponse:
        """Calculate member cost for a service"""
        coverage_link = self.repository.get_by_id(link_id)
        if not coverage_link:
            raise EntityNotFoundError(f"Coverage link {link_id} not found")
        
        cost_breakdown = coverage_link.calculate_member_cost(
            calculation_request.service_cost,
            calculation_request.accumulated_deductible
        )
        
        return CostCalculationResponse(
            service_cost=cost_breakdown['service_cost'],
            deductible=cost_breakdown['deductible'],
            copay=cost_breakdown['copay'],
            member_pays=cost_breakdown['member_pays'],
            insurance_pays=cost_breakdown['insurance_pays']
        )
    
    def get_coverage_summary(self, plan_id: UUID) -> CoverageLinkSummary:
        """Get coverage summary for a plan"""
        summary_data = self.repository.get_coverage_summary(plan_id)
        
        return CoverageLinkSummary(
            plan_id=UUID(summary_data['plan_id']),
            total_coverages=summary_data['total_coverages'],
            mandatory_coverages=summary_data['mandatory_coverages'],
            excluded_coverages=summary_data['excluded_coverages'],
            coverage_tiers=summary_data['coverage_tiers'],
            network_restrictions=summary_data['network_restrictions']
        )
    
    def calculate_plan_coverage_value(self, plan_id: UUID) -> Decimal:
        """Calculate total coverage value for a plan"""
        return self.repository.calculate_total_coverage_value(plan_id)
    
    def validate_coverage_compatibility(
        self,
        plan_id: UUID,
        coverage_ids: List[UUID]
    ) -> Dict[str, Any]:
        """Validate if coverages are compatible with each other"""
        # Get existing coverage links
        existing_links = self.repository.get_by_plan(plan_id)
        existing_coverage_ids = {link.coverage_id for link in existing_links}
        
        # Check for conflicts
        conflicts = []
        new_coverage_ids = set(coverage_ids)
        
        # Check for duplicates
        duplicates = new_coverage_ids.intersection(existing_coverage_ids)
        if duplicates:
            conflicts.append({
                'type': 'duplicate',
                'message': f'Coverages already linked: {", ".join(str(c) for c in duplicates)}'
            })
        
        # Additional business logic validations could be added here
        # For example: mutually exclusive coverages, dependency checks, etc.
        
        return {
            'plan_id': str(plan_id),
            'valid': len(conflicts) == 0,
            'conflicts': conflicts,
            'total_coverage_count': len(existing_links) + len(new_coverage_ids - duplicates)
        }