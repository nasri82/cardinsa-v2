# app/modules/pricing/plans/services/plan_version_service.py

"""
Plan Version Service

Business logic layer for Plan Version management.
Handles version control, approval workflows, and rollbacks.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.modules.pricing.plans.repositories.plan_version_repository import PlanVersionRepository
from app.modules.pricing.plans.repositories.plan_repository import PlanRepository
from app.modules.pricing.plans.models.plan_version_model import (
    PlanVersion,
    VersionStatus,
    ChangeType,
    ApprovalStatus
)
from app.modules.pricing.plans.schemas.plan_version_schema import (
    PlanVersionCreate,
    PlanVersionUpdate,
    PlanVersionResponse,
    VersionComparisonRequest,
    VersionRollbackRequest
)

from app.core.exceptions import (
    BusinessLogicError,
    ValidationError,
    EntityNotFoundError,
    UnauthorizedError
)
import logging

logger = logging.getLogger(__name__)


class PlanVersionService:
    """Service layer for Plan Version management"""
    
    def __init__(self, db: Session):
        """Initialize service with database session"""
        self.db = db
        self.repository = PlanVersionRepository(db)
        self.plan_repository = PlanRepository(db)
    
    # ================================================================
    # VERSION CREATION
    # ================================================================
    
    def create_version(
        self,
        plan_id: UUID,
        version_data: PlanVersionCreate,
        created_by: UUID
    ) -> PlanVersionResponse:
        """
        Create a new plan version
        
        Args:
            plan_id: Plan UUID
            version_data: Version creation data
            created_by: User ID creating the version
            
        Returns:
            Created version response
        """
        try:
            # Verify plan exists
            plan = self.plan_repository.get_by_id(plan_id)
            if not plan:
                raise EntityNotFoundError(f"Plan {plan_id} not found")
            
            # Validate change type based on changes
            if not self._validate_change_type(version_data):
                raise ValidationError("Change type doesn't match the scope of changes")
            
            # Create plan snapshot
            plan_snapshot = plan.to_dict()
            
            # Prepare version data
            version_dict = version_data.dict(exclude_unset=True)
            version_dict['plan_snapshot'] = plan_snapshot
            
            # Set approval requirements based on change type
            if version_data.change_type in [ChangeType.MAJOR, ChangeType.CRITICAL]:
                version_dict['regulatory_approval_required'] = True
                version_dict['approval_status'] = ApprovalStatus.PENDING.value
            
            # Create version
            version = self.repository.create_version(
                plan_id,
                version_dict,
                created_by
            )
            
            logger.info(f"Created version {version.version_number} for plan {plan_id}")
            
            return PlanVersionResponse.from_orm(version)
            
        except (EntityNotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error creating version: {str(e)}")
            raise BusinessLogicError(f"Failed to create version: {str(e)}")
    
    def _validate_change_type(self, version_data: PlanVersionCreate) -> bool:
        """Validate change type matches the changes"""
        # Simple validation - can be enhanced
        if version_data.change_type == ChangeType.MINOR:
            # Minor changes shouldn't require approval
            return True
        elif version_data.change_type == ChangeType.MAJOR:
            # Major changes should have substantial modifications
            return bool(version_data.changes_from_previous)
        return True
    
    # ================================================================
    # VERSION RETRIEVAL
    # ================================================================
    
    def get_version(self, version_id: UUID) -> PlanVersionResponse:
        """Get version by ID"""
        version = self.repository.get_by_id(version_id)
        if not version:
            raise EntityNotFoundError(f"Version {version_id} not found")
        
        return PlanVersionResponse.from_orm(version)
    
    def get_current_version(self, plan_id: UUID) -> PlanVersionResponse:
        """Get current active version for a plan"""
        version = self.repository.get_current_version(plan_id)
        if not version:
            raise EntityNotFoundError(f"No current version found for plan {plan_id}")
        
        return PlanVersionResponse.from_orm(version)
    
    def get_version_history(
        self,
        plan_id: UUID,
        include_draft: bool = False,
        limit: int = 10
    ) -> List[PlanVersionResponse]:
        """Get version history for a plan"""
        versions = self.repository.get_versions_by_plan(plan_id, include_draft)
        
        # Apply limit
        if limit:
            versions = versions[:limit]
        
        return [PlanVersionResponse.from_orm(v) for v in versions]
    
    def get_pending_approvals(
        self,
        company_id: Optional[UUID] = None
    ) -> List[PlanVersionResponse]:
        """Get versions pending approval"""
        versions = self.repository.get_pending_approvals(company_id)
        return [PlanVersionResponse.from_orm(v) for v in versions]
    
    # ================================================================
    # VERSION UPDATES
    # ================================================================
    
    def update_version(
        self,
        version_id: UUID,
        update_data: PlanVersionUpdate,
        updated_by: UUID
    ) -> PlanVersionResponse:
        """
        Update version details
        
        Only draft versions can be updated
        """
        version = self.repository.get_by_id(version_id)
        if not version:
            raise EntityNotFoundError(f"Version {version_id} not found")
        
        # Only draft versions can be updated
        if version.status != VersionStatus.DRAFT.value:
            raise BusinessLogicError("Only draft versions can be updated")
        
        # Update version
        update_dict = update_data.dict(exclude_unset=True, exclude_none=True)
        updated_version = self.repository.update_version(
            version_id,
            update_dict,
            updated_by
        )
        
        if not updated_version:
            raise BusinessLogicError("Failed to update version")
        
        return PlanVersionResponse.from_orm(updated_version)
    
    # ================================================================
    # APPROVAL WORKFLOW
    # ================================================================
    
    def submit_for_approval(
        self,
        version_id: UUID,
        submitted_by: UUID,
        notes: Optional[str] = None
    ) -> PlanVersionResponse:
        """Submit version for approval"""
        version = self.repository.get_by_id(version_id)
        if not version:
            raise EntityNotFoundError(f"Version {version_id} not found")
        
        # Validate status
        if version.status != VersionStatus.DRAFT.value:
            raise BusinessLogicError("Only draft versions can be submitted for approval")
        
        # Update status
        update_data = {
            'status': VersionStatus.PENDING_REVIEW.value,
            'approval_status': ApprovalStatus.PENDING.value
        }
        
        if notes:
            update_data['created_by_reason'] = notes
        
        updated = self.repository.update_version(version_id, update_data)
        
        logger.info(f"Version {version_id} submitted for approval by {submitted_by}")
        
        return PlanVersionResponse.from_orm(updated)
    
    def approve_version(
        self,
        version_id: UUID,
        approved_by: UUID,
        notes: Optional[str] = None,
        make_current: bool = False
    ) -> PlanVersionResponse:
        """
        Approve a version
        
        Args:
            version_id: Version UUID
            approved_by: Approver user ID
            notes: Approval notes
            make_current: Make this the current version
            
        Returns:
            Approved version response
        """
        version = self.repository.get_by_id(version_id)
        if not version:
            raise EntityNotFoundError(f"Version {version_id} not found")
        
        # Validate status
        if version.approval_status not in [
            ApprovalStatus.PENDING.value,
            ApprovalStatus.IN_REVIEW.value
        ]:
            raise BusinessLogicError("Version is not pending approval")
        
        # Approve version
        approved = self.repository.approve_version(version_id, approved_by, notes)
        
        # Make current if requested
        if make_current:
            self.repository.activate_version(version_id)
            
            # Update plan version number
            plan = self.plan_repository.get_by_id(version.plan_id)
            if plan:
                self.plan_repository.update(
                    version.plan_id,
                    {'version': version.version_number},
                    approved_by
                )
        
        logger.info(f"Version {version_id} approved by {approved_by}")
        
        return PlanVersionResponse.from_orm(approved)
    
    def reject_version(
        self,
        version_id: UUID,
        rejected_by: UUID,
        reason: str
    ) -> PlanVersionResponse:
        """Reject a version"""
        version = self.repository.get_by_id(version_id)
        if not version:
            raise EntityNotFoundError(f"Version {version_id} not found")
        
        # Validate status
        if version.approval_status not in [
            ApprovalStatus.PENDING.value,
            ApprovalStatus.IN_REVIEW.value
        ]:
            raise BusinessLogicError("Version is not pending approval")
        
        # Reject version
        rejected = self.repository.reject_version(version_id, rejected_by, reason)
        
        logger.warning(f"Version {version_id} rejected by {rejected_by}: {reason}")
        
        return PlanVersionResponse.from_orm(rejected)
    
    # ================================================================
    # VERSION ACTIVATION
    # ================================================================
    
    def activate_version(
        self,
        version_id: UUID,
        activated_by: UUID,
        effective_date: Optional[datetime] = None
    ) -> PlanVersionResponse:
        """
        Activate a version as current
        
        Version must be approved before activation
        """
        version = self.repository.get_by_id(version_id)
        if not version:
            raise EntityNotFoundError(f"Version {version_id} not found")
        
        # Validate approval status
        if version.approval_status != ApprovalStatus.APPROVED.value:
            raise BusinessLogicError("Version must be approved before activation")
        
        # Activate version
        activated = self.repository.activate_version(version_id, effective_date)
        
        # Update plan
        plan = self.plan_repository.get_by_id(version.plan_id)
        if plan:
            self.plan_repository.update(
                version.plan_id,
                {'version': version.version_number},
                activated_by
            )
        
        logger.info(f"Version {version_id} activated as current by {activated_by}")
        
        return PlanVersionResponse.from_orm(activated)
    
    # ================================================================
    # VERSION COMPARISON
    # ================================================================
    
    def compare_versions(
        self,
        comparison_request: VersionComparisonRequest
    ) -> Dict[str, Any]:
        """
        Compare two versions
        
        Returns detailed differences between versions
        """
        if comparison_request.version_id1 == comparison_request.version_id2:
            raise ValidationError("Cannot compare version with itself")
        
        comparison = self.repository.compare_versions(
            comparison_request.version_id1,
            comparison_request.version_id2
        )
        
        if not comparison:
            raise EntityNotFoundError("One or both versions not found")
        
        return comparison
    
    # ================================================================
    # VERSION ROLLBACK
    # ================================================================
    
    def rollback_to_version(
        self,
        plan_id: UUID,
        rollback_request: VersionRollbackRequest,
        rolled_back_by: UUID
    ) -> PlanVersionResponse:
        """
        Rollback to a previous version
        
        Creates a new version with the old version's data
        """
        # Verify plan exists
        plan = self.plan_repository.get_by_id(plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan {plan_id} not found")
        
        # Verify target version exists
        target_version = self.repository.get_version_by_number(
            plan_id,
            rollback_request.target_version_number
        )
        if not target_version:
            raise EntityNotFoundError(
                f"Version {rollback_request.target_version_number} not found"
            )
        
        # Create rollback version
        new_version = self.repository.rollback_to_version(
            plan_id,
            rollback_request.target_version_number,
            rolled_back_by,
            rollback_request.reason
        )
        
        # Update plan
        self.plan_repository.update(
            plan_id,
            {'version': new_version.version_number},
            rolled_back_by
        )
        
        logger.warning(
            f"Plan {plan_id} rolled back to version {rollback_request.target_version_number} "
            f"by {rolled_back_by}: {rollback_request.reason}"
        )
        
        return PlanVersionResponse.from_orm(new_version)
    
    # ================================================================
    # STATISTICS
    # ================================================================
    
    def get_version_statistics(self, plan_id: UUID) -> Dict[str, Any]:
        """Get version statistics for a plan"""
        return self.repository.get_version_statistics(plan_id)