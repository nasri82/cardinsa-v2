# app/modules/pricing/plans/services/plan_exclusion_service.py
"""
Plan Exclusion Service

Business logic layer for Plan Exclusion operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from app.modules.pricing.plans.repositories.plan_exclusion_repository import PlanExclusionRepository
from app.modules.pricing.plans.schemas.plan_exclusion_schema import (
    PlanExclusionCreate,
    PlanExclusionUpdate,
    PlanExclusionResponse,
    BulkExclusionCreate,
    ExclusionSummary,
    ExclusionCheckRequest,
    ExclusionCheckResponse,
    ExclusionSearchFilters,
    AlternativeCoverage
)
from app.modules.pricing.plans.models.plan_exclusion_model import (
    ExclusionType,
    ExclusionCategory,
    ExclusionSeverity
)
from app.core.exceptions import EntityNotFoundError, BusinessLogicError, ValidationError
import logging

logger = logging.getLogger(__name__)

class PlanExclusionService:
    """Service layer for Plan Exclusion operations"""
    
    def __init__(self, repository: PlanExclusionRepository):
        self.repository = repository
    
    def create_exclusion(
        self,
        plan_id: UUID,
        exclusion_data: PlanExclusionCreate,
        created_by: UUID
    ) -> PlanExclusionResponse:
        """Create new exclusion"""
        create_dict = exclusion_data.dict()
        create_dict['plan_id'] = plan_id
        
        exclusion = self.repository.create(create_dict, created_by)
        
        # Add computed fields
        response = PlanExclusionResponse.from_orm(exclusion)
        response.is_waiverable = exclusion.is_waiverable()
        response.is_temporary = exclusion.is_temporary()
        
        return response
    
    def bulk_create_exclusions(
        self,
        plan_id: UUID,
        bulk_data: BulkExclusionCreate,
        created_by: UUID
    ) -> List[PlanExclusionResponse]:
        """Bulk create exclusions"""
        exclusions_data = []
        for exclusion in bulk_data.exclusions:
            exclusion_dict = exclusion.dict()
            exclusion_dict['plan_id'] = plan_id
            exclusions_data.append(exclusion_dict)
        
        exclusions = self.repository.bulk_create(exclusions_data, created_by)
        
        responses = []
        for exclusion in exclusions:
            response = PlanExclusionResponse.from_orm(exclusion)
            response.is_waiverable = exclusion.is_waiverable()
            response.is_temporary = exclusion.is_temporary()
            responses.append(response)
        
        return responses
    
    def get_exclusion(self, exclusion_id: UUID) -> PlanExclusionResponse:
        """Get exclusion by ID"""
        exclusion = self.repository.get_by_id(exclusion_id)
        if not exclusion:
            raise EntityNotFoundError(f"Exclusion {exclusion_id} not found")
        
        response = PlanExclusionResponse.from_orm(exclusion)
        response.is_waiverable = exclusion.is_waiverable()
        response.is_temporary = exclusion.is_temporary()
        
        return response
    
    def get_plan_exclusions(
        self,
        plan_id: UUID,
        filters: Optional[ExclusionSearchFilters] = None
    ) -> List[PlanExclusionResponse]:
        """Get exclusions for a plan with filters"""
        if not filters:
            filters = ExclusionSearchFilters()
        
        exclusions = self.repository.get_by_plan(
            plan_id=plan_id,
            exclusion_type=filters.exclusion_type,
            exclusion_category=filters.exclusion_category,
            exclusion_severity=filters.exclusion_severity,
            is_highlighted=filters.is_highlighted,
            effective_date=filters.effective_date,
            text_search=filters.text_search,
            tags=filters.tags
        )
        
        responses = []
        for exclusion in exclusions:
            response = PlanExclusionResponse.from_orm(exclusion)
            response.is_waiverable = exclusion.is_waiverable()
            response.is_temporary = exclusion.is_temporary()
            responses.append(response)
        
        return responses
    
    def get_active_exclusions(
        self,
        plan_id: UUID,
        check_date: Optional[date] = None
    ) -> List[PlanExclusionResponse]:
        """Get active exclusions for a plan"""
        exclusions = self.repository.get_active_exclusions(plan_id, check_date)
        
        responses = []
        for exclusion in exclusions:
            response = PlanExclusionResponse.from_orm(exclusion)
            response.is_waiverable = exclusion.is_waiverable()
            response.is_temporary = exclusion.is_temporary()
            responses.append(response)
        
        return responses
    
    def get_highlighted_exclusions(self, plan_id: UUID) -> List[PlanExclusionResponse]:
        """Get highlighted exclusions for a plan"""
        exclusions = self.repository.get_highlighted_exclusions(plan_id)
        
        responses = []
        for exclusion in exclusions:
            response = PlanExclusionResponse.from_orm(exclusion)
            response.is_waiverable = exclusion.is_waiverable()
            response.is_temporary = exclusion.is_temporary()
            responses.append(response)
        
        return responses
    
    def get_waiverable_exclusions(self, plan_id: UUID) -> List[PlanExclusionResponse]:
        """Get waiverable exclusions for a plan"""
        exclusions = self.repository.get_waiverable_exclusions(plan_id)
        
        responses = []
        for exclusion in exclusions:
            response = PlanExclusionResponse.from_orm(exclusion)
            response.is_waiverable = exclusion.is_waiverable()
            response.is_temporary = exclusion.is_temporary()
            responses.append(response)
        
        return responses
    
    def update_exclusion(
        self,
        exclusion_id: UUID,
        update_data: PlanExclusionUpdate,
        updated_by: UUID
    ) -> PlanExclusionResponse:
        """Update exclusion"""
        exclusion = self.repository.get_by_id(exclusion_id)
        if not exclusion:
            raise EntityNotFoundError(f"Exclusion {exclusion_id} not found")
        
        update_dict = update_data.dict(exclude_unset=True, exclude_none=True)
        updated = self.repository.update(exclusion_id, update_dict, updated_by)
        
        if not updated:
            raise BusinessLogicError("Failed to update exclusion")
        
        response = PlanExclusionResponse.from_orm(updated)
        response.is_waiverable = updated.is_waiverable()
        response.is_temporary = updated.is_temporary()
        
        return response
    
    def delete_exclusion(self, exclusion_id: UUID) -> bool:
        """Delete exclusion"""
        success = self.repository.delete(exclusion_id)
        if not success:
            raise EntityNotFoundError(f"Exclusion {exclusion_id} not found")
        return success
    
    def check_exclusion_applies(
        self,
        exclusion_id: UUID,
        check_request: ExclusionCheckRequest
    ) -> ExclusionCheckResponse:
        """Check if exclusion applies to a given context"""
        exclusion = self.repository.get_by_id(exclusion_id)
        if not exclusion:
            raise EntityNotFoundError(f"Exclusion {exclusion_id} not found")
        
        check_date = check_request.check_date or date.today()
        
        # Check if exclusion is active
        if not exclusion.is_active(check_date):
            return ExclusionCheckResponse(
                exclusion_id=exclusion_id,
                applies=False,
                reason="Exclusion is not active on the specified date",
                exception_found=False,
                alternative_options=[]
            )
        
        # Check for exceptions
        exception_found = exclusion.check_exception(check_request.context)
        if exception_found:
            return ExclusionCheckResponse(
                exclusion_id=exclusion_id,
                applies=False,
                reason="Exception conditions are met",
                exception_found=True,
                alternative_options=self._get_alternative_options(exclusion)
            )
        
        # Exclusion applies
        return ExclusionCheckResponse(
            exclusion_id=exclusion_id,
            applies=True,
            reason=f"Exclusion applies: {exclusion.exclusion_text[:100]}...",
            exception_found=False,
            alternative_options=self._get_alternative_options(exclusion)
        )
    
    def get_exclusion_summary(self, plan_id: UUID) -> ExclusionSummary:
        """Get exclusion summary for a plan"""
        summary_data = self.repository.get_exclusion_summary(plan_id)
        
        return ExclusionSummary(
            plan_id=UUID(summary_data['plan_id']),
            total_exclusions=summary_data['total_exclusions'],
            by_type=summary_data['by_type'],
            by_category=summary_data['by_category'],
            by_severity=summary_data['by_severity'],
            highlighted_exclusions=summary_data['highlighted_exclusions'],
            temporary_exclusions=summary_data['temporary_exclusions'],
            waiverable_exclusions=summary_data['waiverable_exclusions']
        )
    
    def search_exclusions(
        self,
        plan_id: UUID,
        search_term: str,
        limit: int = 50
    ) -> List[PlanExclusionResponse]:
        """Search exclusions by text"""
        if len(search_term) < 3:
            raise ValidationError("Search term must be at least 3 characters")
        
        exclusions = self.repository.search_exclusions(plan_id, search_term, limit)
        
        responses = []
        for exclusion in exclusions:
            response = PlanExclusionResponse.from_orm(exclusion)
            response.is_waiverable = exclusion.is_waiverable()
            response.is_temporary = exclusion.is_temporary()
            responses.append(response)
        
        return responses
    
    def check_medical_code_exclusions(
        self,
        plan_id: UUID,
        cpt_codes: Optional[List[UUID]] = None,
        icd10_codes: Optional[List[UUID]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Check exclusions for medical codes"""
        exclusions = self.repository.get_by_medical_codes(plan_id, cpt_codes, icd10_codes)
        
        active_exclusions = []
        waived_exclusions = []
        
        for exclusion in exclusions:
            if not exclusion.is_active():
                continue
            
            if context and exclusion.check_exception(context):
                waived_exclusions.append({
                    'exclusion_id': str(exclusion.id),
                    'exclusion_text': exclusion.exclusion_text,
                    'exception_reason': 'Exception conditions met'
                })
            else:
                active_exclusions.append({
                    'exclusion_id': str(exclusion.id),
                    'exclusion_text': exclusion.exclusion_text,
                    'exclusion_severity': exclusion.exclusion_severity,
                    'is_waiverable': exclusion.is_waiverable()
                })
        
        return {
            'plan_id': str(plan_id),
            'total_exclusions_found': len(exclusions),
            'active_exclusions': active_exclusions,
            'waived_exclusions': waived_exclusions,
            'has_blocking_exclusions': any(
                ex['exclusion_severity'] == ExclusionSeverity.ABSOLUTE.value 
                for ex in active_exclusions
            )
        }
    
    def _get_alternative_options(self, exclusion) -> List[AlternativeCoverage]:
        """Get alternative coverage options from exclusion"""
        alternatives = exclusion.get_alternative_options()
        
        coverage_options = []
        for alt in alternatives:
            if isinstance(alt, dict):
                coverage_options.append(AlternativeCoverage(
                    option_name=alt.get('option_name', 'Alternative Coverage'),
                    description=alt.get('description', ''),
                    coverage_percentage=alt.get('coverage_percentage'),
                    additional_cost=alt.get('additional_cost'),
                    requirements=alt.get('requirements', [])
                ))
        
        return coverage_options