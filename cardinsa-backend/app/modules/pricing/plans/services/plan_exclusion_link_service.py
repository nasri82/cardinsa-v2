# app/modules/pricing/plans/services/plan_exclusion_link_service.py
"""
Plan Exclusion Link Service

Business logic layer for Plan Exclusion Link operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from app.modules.pricing.plans.repositories.plan_exclusion_link_repository import PlanExclusionLinkRepository
from app.modules.pricing.plans.schemas.plan_exclusion_link_schema import (
    PlanExclusionLinkCreate,
    PlanExclusionLinkUpdate,
    PlanExclusionLinkResponse,
    BulkExclusionLinkCreate,
    ExclusionLinkSummary,
    ExclusionLinkSearchFilters,
    CoverageApplicationCheck,
    ExclusionLinkEffectivenessCheck
)
from app.modules.pricing.plans.models.plan_exclusion_link_model import (
    LinkStatus,
    ApplicationScope,
    OverrideType
)
from app.core.exceptions import EntityNotFoundError, BusinessLogicError, ValidationError
import logging

logger = logging.getLogger(__name__)

class PlanExclusionLinkService:
    """Service layer for Plan Exclusion Link operations"""
    
    def __init__(self, repository: PlanExclusionLinkRepository):
        self.repository = repository
    
    def create_exclusion_link(
        self,
        plan_id: UUID,
        link_data: PlanExclusionLinkCreate,
        created_by: UUID
    ) -> PlanExclusionLinkResponse:
        """Create new exclusion link"""
        # Validate exclusion doesn't already exist for plan
        existing = self.repository.get_by_plan_and_exclusion(
            plan_id, link_data.exclusion_id
        )
        if existing:
            raise ValidationError("Exclusion already linked to this plan")
        
        create_dict = link_data.dict()
        create_dict['plan_id'] = plan_id
        
        exclusion_link = self.repository.create(create_dict, created_by)
        
        # Add computed fields
        response = PlanExclusionLinkResponse.from_orm(exclusion_link)
        response.is_effective = exclusion_link.is_effective()
        response.effective_text = exclusion_link.get_effective_text()
        
        return response
    
    def bulk_create_exclusion_links(
        self,
        plan_id: UUID,
        bulk_data: BulkExclusionLinkCreate,
        created_by: UUID
    ) -> List[PlanExclusionLinkResponse]:
        """Bulk create exclusion links"""
        # Validate no duplicates in request
        exclusion_ids = [link.exclusion_id for link in bulk_data.exclusion_links]
        if len(exclusion_ids) != len(set(exclusion_ids)):
            raise ValidationError("Duplicate exclusion IDs in request")
        
        # Check for existing links
        existing_links = []
        for exclusion_id in exclusion_ids:
            if self.repository.get_by_plan_and_exclusion(plan_id, exclusion_id):
                existing_links.append(str(exclusion_id))
        
        if existing_links:
            raise ValidationError(f"Exclusions already linked: {', '.join(existing_links)}")
        
        links_data = []
        for link in bulk_data.exclusion_links:
            link_dict = link.dict()
            link_dict['plan_id'] = plan_id
            links_data.append(link_dict)
        
        exclusion_links = self.repository.bulk_create(links_data, created_by)
        
        responses = []
        for link in exclusion_links:
            response = PlanExclusionLinkResponse.from_orm(link)
            response.is_effective = link.is_effective()
            response.effective_text = link.get_effective_text()
            responses.append(response)
        
        return responses
    
    def get_exclusion_link(self, link_id: UUID) -> PlanExclusionLinkResponse:
        """Get exclusion link by ID"""
        exclusion_link = self.repository.get_by_id(link_id)
        if not exclusion_link:
            raise EntityNotFoundError(f"Exclusion link {link_id} not found")
        
        response = PlanExclusionLinkResponse.from_orm(exclusion_link)
        response.is_effective = exclusion_link.is_effective()
        response.effective_text = exclusion_link.get_effective_text()
        
        return response
    
    def get_plan_exclusion_links(
        self,
        plan_id: UUID,
        filters: Optional[ExclusionLinkSearchFilters] = None
    ) -> List[PlanExclusionLinkResponse]:
        """Get exclusion links for a plan with filters"""
        if not filters:
            filters = ExclusionLinkSearchFilters()
        
        exclusion_links = self.repository.get_by_plan(
            plan_id=plan_id,
            status=filters.status,
            is_active=filters.is_active,
            is_mandatory=filters.is_mandatory,
            application_scope=filters.application_scope,
            override_type=filters.override_type,
            is_highlighted=filters.is_highlighted,
            effective_date=filters.effective_date,
            display_category=filters.display_category
        )
        
        responses = []
        for link in exclusion_links:
            response = PlanExclusionLinkResponse.from_orm(link)
            response.is_effective = link.is_effective()
            response.effective_text = link.get_effective_text()
            responses.append(response)
        
        return responses
    
    def get_effective_exclusion_links(
        self,
        plan_id: UUID,
        check_date: Optional[date] = None
    ) -> List[PlanExclusionLinkResponse]:
        """Get effective exclusion links for a plan"""
        exclusion_links = self.repository.get_effective_links(plan_id, check_date)
        
        responses = []
        for link in exclusion_links:
            response = PlanExclusionLinkResponse.from_orm(link)
            response.is_effective = True  # Already filtered for effective
            response.effective_text = link.get_effective_text()
            responses.append(response)
        
        return responses
    
    def get_mandatory_exclusion_links(self, plan_id: UUID) -> List[PlanExclusionLinkResponse]:
        """Get mandatory exclusion links for a plan"""
        exclusion_links = self.repository.get_mandatory_links(plan_id)
        
        responses = []
        for link in exclusion_links:
            response = PlanExclusionLinkResponse.from_orm(link)
            response.is_effective = link.is_effective()
            response.effective_text = link.get_effective_text()
            responses.append(response)
        
        return responses
    
    def get_highlighted_exclusion_links(self, plan_id: UUID) -> List[PlanExclusionLinkResponse]:
        """Get highlighted exclusion links for a plan"""
        exclusion_links = self.repository.get_highlighted_links(plan_id)
        
        responses = []
        for link in exclusion_links:
            response = PlanExclusionLinkResponse.from_orm(link)
            response.is_effective = link.is_effective()
            response.effective_text = link.get_effective_text()
            responses.append(response)
        
        return responses
    
    def get_coverage_exclusion_links(
        self,
        plan_id: UUID,
        coverage_id: UUID,
        check_date: Optional[date] = None
    ) -> List[PlanExclusionLinkResponse]:
        """Get exclusion links that apply to a specific coverage"""
        exclusion_links = self.repository.get_by_coverage(plan_id, coverage_id, check_date)
        
        responses = []
        for link in exclusion_links:
            response = PlanExclusionLinkResponse.from_orm(link)
            response.is_effective = link.is_effective(check_date)
            response.effective_text = link.get_effective_text()
            responses.append(response)
        
        return responses
    
    def update_exclusion_link(
        self,
        link_id: UUID,
        update_data: PlanExclusionLinkUpdate,
        updated_by: UUID
    ) -> PlanExclusionLinkResponse:
        """Update exclusion link"""
        exclusion_link = self.repository.get_by_id(link_id)
        if not exclusion_link:
            raise EntityNotFoundError(f"Exclusion link {link_id} not found")
        
        update_dict = update_data.dict(exclude_unset=True, exclude_none=True)
        updated = self.repository.update(link_id, update_dict, updated_by)
        
        if not updated:
            raise BusinessLogicError("Failed to update exclusion link")
        
        response = PlanExclusionLinkResponse.from_orm(updated)
        response.is_effective = updated.is_effective()
        response.effective_text = updated.get_effective_text()
        
        return response
    
    def delete_exclusion_link(self, link_id: UUID) -> bool:
        """Delete exclusion link"""
        success = self.repository.delete(link_id)
        if not success:
            raise EntityNotFoundError(f"Exclusion link {link_id} not found")
        return success
    
    def check_coverage_application(
        self,
        link_id: UUID,
        coverage_check: CoverageApplicationCheck
    ) -> Dict[str, Any]:
        """Check if exclusion link applies to a coverage"""
        exclusion_link = self.repository.get_by_id(link_id)
        if not exclusion_link:
            raise EntityNotFoundError(f"Exclusion link {link_id} not found")
        
        applies = exclusion_link.applies_to_coverage(str(coverage_check.coverage_id))
        
        return {
            'link_id': str(link_id),
            'coverage_id': str(coverage_check.coverage_id),
            'applies': applies,
            'application_scope': exclusion_link.application_scope,
            'reason': self._get_application_reason(exclusion_link, str(coverage_check.coverage_id)),
            'is_effective': exclusion_link.is_effective()
        }
    
    def check_link_effectiveness(
        self,
        link_id: UUID,
        effectiveness_check: ExclusionLinkEffectivenessCheck
    ) -> Dict[str, Any]:
        """Check if exclusion link is effective"""
        exclusion_link = self.repository.get_by_id(link_id)
        if not exclusion_link:
            raise EntityNotFoundError(f"Exclusion link {link_id} not found")
        
        is_effective = exclusion_link.is_effective(effectiveness_check.check_date)
        
        result = {
            'link_id': str(link_id),
            'check_date': (effectiveness_check.check_date or date.today()).isoformat(),
            'is_effective': is_effective,
            'is_active': exclusion_link.is_active,
            'status': exclusion_link.status,
            'effective_date': exclusion_link.effective_date.isoformat() if exclusion_link.effective_date else None,
            'expiry_date': exclusion_link.expiry_date.isoformat() if exclusion_link.expiry_date else None
        }
        
        if effectiveness_check.coverage_id:
            result['coverage_applies'] = exclusion_link.applies_to_coverage(str(effectiveness_check.coverage_id))
        
        return result
    
    def get_exclusion_link_summary(self, plan_id: UUID) -> ExclusionLinkSummary:
        """Get exclusion link summary for a plan"""
        summary_data = self.repository.get_link_summary(plan_id)
        
        return ExclusionLinkSummary(
            plan_id=UUID(summary_data['plan_id']),
            total_links=summary_data['total_links'],
            active_links=summary_data['active_links'],
            mandatory_links=summary_data['mandatory_links'],
            by_status=summary_data['by_status'],
            by_scope=summary_data['by_scope'],
            by_override_type=summary_data['by_override_type'],
            highlighted_links=summary_data['highlighted_links']
        )
    
    def validate_exclusion_compatibility(
        self,
        plan_id: UUID,
        exclusion_ids: List[UUID]
    ) -> Dict[str, Any]:
        """Validate if exclusions are compatible with the plan"""
        # Get existing exclusion links
        existing_links = self.repository.get_by_plan(plan_id)
        existing_exclusion_ids = {link.exclusion_id for link in existing_links}
        
        # Check for conflicts
        conflicts = []
        new_exclusion_ids = set(exclusion_ids)
        
        # Check for duplicates
        duplicates = new_exclusion_ids.intersection(existing_exclusion_ids)
        if duplicates:
            conflicts.append({
                'type': 'duplicate',
                'message': f'Exclusions already linked: {", ".join(str(e) for e in duplicates)}'
            })
        
        return {
            'plan_id': str(plan_id),
            'valid': len(conflicts) == 0,
            'conflicts': conflicts,
            'total_exclusion_count': len(existing_links) + len(new_exclusion_ids - duplicates)
        }
    
    def _get_application_reason(self, exclusion_link, coverage_id: str) -> str:
        """Get reason why exclusion applies or doesn't apply to coverage"""
        if exclusion_link.application_scope == ApplicationScope.GLOBAL.value:
            return "Exclusion applies globally to all coverages"
        elif exclusion_link.application_scope == ApplicationScope.SPECIFIC.value:
            if coverage_id in (exclusion_link.applicable_coverages or []):
                return "Coverage is in the specific coverage list"
            else:
                return "Coverage is not in the specific coverage list"
        elif exclusion_link.application_scope == ApplicationScope.CONDITIONAL.value:
            return "Application depends on conditional evaluation"
        else:
            return "Unknown application scope"