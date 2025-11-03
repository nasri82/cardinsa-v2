# app/modules/pricing/plans/repositories/plan_version_repository.py

"""
Plan Version Repository

Data access layer for Plan Version operations.
Handles version tracking, history, and change management.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import and_, or_, func, select, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.modules.pricing.plans.models.plan_version_model import (
    PlanVersion, 
    VersionStatus, 
    ChangeType,
    ApprovalStatus
)
from app.core.exceptions import DatabaseOperationError
import logging

logger = logging.getLogger(__name__)


class PlanVersionRepository:
    """Repository for Plan Version database operations"""
    
    def __init__(self, db: Session):
        """Initialize repository with database session"""
        self.db = db
    
    # ================================================================
    # CREATE OPERATIONS
    # ================================================================
    
    def create_version(
        self,
        plan_id: UUID,
        version_data: Dict[str, Any],
        created_by: Optional[UUID] = None
    ) -> PlanVersion:
        """
        Create a new plan version
        
        Args:
            plan_id: Plan UUID
            version_data: Version data dictionary
            created_by: User ID creating the version
            
        Returns:
            Created version instance
        """
        try:
            # Get next version number
            max_version = self.db.query(func.max(PlanVersion.version_number)).filter(
                PlanVersion.plan_id == plan_id
            ).scalar() or 0
            
            # Set version metadata
            version_data['plan_id'] = plan_id
            version_data['version_number'] = max_version + 1
            version_data['created_by'] = created_by
            version_data['created_at'] = datetime.utcnow()
            
            # Default version label if not provided
            if not version_data.get('version_label'):
                version_data['version_label'] = f"{version_data['version_number']}.0.0"
            
            # Create version
            version = PlanVersion(**version_data)
            
            # Mark previous current version as superseded
            if version_data.get('is_current_version'):
                self._supersede_current_version(plan_id)
            
            self.db.add(version)
            self.db.commit()
            self.db.refresh(version)
            
            logger.info(f"Created version {version.version_number} for plan {plan_id}")
            return version
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating version: {str(e)}")
            raise DatabaseOperationError(f"Failed to create version: {str(e)}")
    
    def _supersede_current_version(self, plan_id: UUID) -> None:
        """Mark current version as superseded"""
        current = self.db.query(PlanVersion).filter(
            PlanVersion.plan_id == plan_id,
            PlanVersion.is_current_version == True
        ).first()
        
        if current:
            current.is_current_version = False
            current.status = VersionStatus.SUPERSEDED.value
            current.expiry_date = datetime.utcnow()
    
    # ================================================================
    # READ OPERATIONS
    # ================================================================
    
    def get_by_id(self, version_id: UUID) -> Optional[PlanVersion]:
        """Get version by ID"""
        return self.db.query(PlanVersion).filter(
            PlanVersion.id == version_id
        ).first()
    
    def get_current_version(self, plan_id: UUID) -> Optional[PlanVersion]:
        """Get current active version for a plan"""
        return self.db.query(PlanVersion).filter(
            PlanVersion.plan_id == plan_id,
            PlanVersion.is_current_version == True
        ).first()
    
    def get_versions_by_plan(
        self,
        plan_id: UUID,
        include_draft: bool = False
    ) -> List[PlanVersion]:
        """
        Get all versions for a plan
        
        Args:
            plan_id: Plan UUID
            include_draft: Include draft versions
            
        Returns:
            List of versions ordered by version number
        """
        query = self.db.query(PlanVersion).filter(
            PlanVersion.plan_id == plan_id
        )
        
        if not include_draft:
            query = query.filter(
                PlanVersion.status != VersionStatus.DRAFT.value
            )
        
        return query.order_by(desc(PlanVersion.version_number)).all()
    
    def get_version_by_number(
        self,
        plan_id: UUID,
        version_number: int
    ) -> Optional[PlanVersion]:
        """Get specific version by number"""
        return self.db.query(PlanVersion).filter(
            PlanVersion.plan_id == plan_id,
            PlanVersion.version_number == version_number
        ).first()
    
    def get_version_history(
        self,
        plan_id: UUID,
        limit: int = 10
    ) -> List[PlanVersion]:
        """Get version history with limit"""
        return self.db.query(PlanVersion).filter(
            PlanVersion.plan_id == plan_id
        ).order_by(
            desc(PlanVersion.version_number)
        ).limit(limit).all()
    
    def get_pending_approvals(
        self,
        company_id: Optional[UUID] = None
    ) -> List[PlanVersion]:
        """Get versions pending approval"""
        query = self.db.query(PlanVersion).filter(
            PlanVersion.approval_status.in_([
                ApprovalStatus.PENDING.value,
                ApprovalStatus.IN_REVIEW.value
            ])
        )
        
        if company_id:
            # Join with plans to filter by company
            from app.modules.pricing.plans.models.plan_model import Plan
            query = query.join(Plan).filter(Plan.company_id == company_id)
        
        return query.all()
    
    # ================================================================
    # UPDATE OPERATIONS
    # ================================================================
    
    def update_version(
        self,
        version_id: UUID,
        update_data: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Optional[PlanVersion]:
        """Update version details"""
        try:
            version = self.get_by_id(version_id)
            if not version:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(version, key):
                    setattr(version, key, value)
            
            self.db.commit()
            self.db.refresh(version)
            
            logger.info(f"Updated version {version_id}")
            return version
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating version: {str(e)}")
            raise DatabaseOperationError(f"Failed to update version: {str(e)}")
    
    def approve_version(
        self,
        version_id: UUID,
        approved_by: UUID,
        notes: Optional[str] = None
    ) -> Optional[PlanVersion]:
        """Approve a version"""
        version = self.get_by_id(version_id)
        if not version:
            return None
        
        version.approval_status = ApprovalStatus.APPROVED.value
        version.status = VersionStatus.APPROVED.value
        version.approved_by = approved_by
        version.approved_at = datetime.utcnow()
        
        if notes:
            if not version.compliance_notes:
                version.compliance_notes = notes
            else:
                version.compliance_notes += f"\n{notes}"
        
        self.db.commit()
        self.db.refresh(version)
        
        logger.info(f"Version {version_id} approved by {approved_by}")
        return version
    
    def reject_version(
        self,
        version_id: UUID,
        rejected_by: UUID,
        reason: str
    ) -> Optional[PlanVersion]:
        """Reject a version"""
        version = self.get_by_id(version_id)
        if not version:
            return None
        
        version.approval_status = ApprovalStatus.REJECTED.value
        version.status = VersionStatus.REJECTED.value
        version.approved_by = rejected_by
        version.approved_at = datetime.utcnow()
        version.compliance_notes = f"Rejected: {reason}"
        
        self.db.commit()
        self.db.refresh(version)
        
        logger.warning(f"Version {version_id} rejected by {rejected_by}: {reason}")
        return version
    
    def activate_version(
        self,
        version_id: UUID,
        effective_date: Optional[datetime] = None
    ) -> Optional[PlanVersion]:
        """Activate a version as current"""
        version = self.get_by_id(version_id)
        if not version:
            return None
        
        # Supersede current version
        self._supersede_current_version(version.plan_id)
        
        # Activate this version
        version.is_current_version = True
        version.is_published = True
        version.status = VersionStatus.APPROVED.value
        version.effective_date = effective_date or datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(version)
        
        logger.info(f"Version {version_id} activated as current")
        return version
    
    # ================================================================
    # COMPARISON OPERATIONS
    # ================================================================
    
    def compare_versions(
        self,
        version_id1: UUID,
        version_id2: UUID
    ) -> Dict[str, Any]:
        """
        Compare two versions
        
        Returns:
            Dictionary with differences
        """
        v1 = self.get_by_id(version_id1)
        v2 = self.get_by_id(version_id2)
        
        if not v1 or not v2:
            return {}
        
        # Compare snapshots
        snapshot1 = v1.plan_snapshot or {}
        snapshot2 = v2.plan_snapshot or {}
        
        differences = {
            'version1': {
                'id': str(v1.id),
                'number': v1.version_number,
                'label': v1.version_label,
                'date': v1.effective_date.isoformat() if v1.effective_date else None
            },
            'version2': {
                'id': str(v2.id),
                'number': v2.version_number,
                'label': v2.version_label,
                'date': v2.effective_date.isoformat() if v2.effective_date else None
            },
            'changes': []
        }
        
        # Find differences
        all_keys = set(snapshot1.keys()) | set(snapshot2.keys())
        for key in all_keys:
            val1 = snapshot1.get(key)
            val2 = snapshot2.get(key)
            if val1 != val2:
                differences['changes'].append({
                    'field': key,
                    'old_value': val1,
                    'new_value': val2
                })
        
        return differences
    
    # ================================================================
    # ROLLBACK OPERATIONS
    # ================================================================
    
    def rollback_to_version(
        self,
        plan_id: UUID,
        version_number: int,
        rolled_back_by: UUID,
        reason: str
    ) -> PlanVersion:
        """
        Rollback to a specific version
        
        Creates a new version with the old version's data
        """
        # Get the version to rollback to
        old_version = self.get_version_by_number(plan_id, version_number)
        if not old_version:
            raise DatabaseOperationError(f"Version {version_number} not found")
        
        # Create new version with old data
        new_version_data = {
            'version_description': f"Rollback to version {version_number}",
            'changes_summary': f"Rolled back: {reason}",
            'changes_from_previous': {
                'rollback': True,
                'from_version': version_number,
                'reason': reason
            },
            'change_type': ChangeType.MAJOR.value,
            'created_by_reason': reason,
            'plan_snapshot': old_version.plan_snapshot,
            'benefits_snapshot': old_version.benefits_snapshot,
            'pricing_snapshot': old_version.pricing_snapshot,
            'is_current_version': True,
            'effective_date': datetime.utcnow()
        }
        
        return self.create_version(plan_id, new_version_data, rolled_back_by)
    
    # ================================================================
    # STATISTICS
    # ================================================================
    
    def get_version_statistics(self, plan_id: UUID) -> Dict[str, Any]:
        """Get version statistics for a plan"""
        versions = self.get_versions_by_plan(plan_id, include_draft=True)
        
        if not versions:
            return {
                'total_versions': 0,
                'current_version': None,
                'last_modified': None
            }
        
        current = next((v for v in versions if v.is_current_version), None)
        
        # Count by change type
        change_types = {}
        for change_type in ChangeType:
            count = sum(1 for v in versions if v.change_type == change_type.value)
            change_types[change_type.value] = count
        
        return {
            'total_versions': len(versions),
            'current_version': current.version_number if current else None,
            'current_version_label': current.version_label if current else None,
            'last_modified': versions[0].created_at.isoformat() if versions else None,
            'change_types': change_types,
            'pending_approvals': sum(1 for v in versions if v.approval_status == ApprovalStatus.PENDING.value)
        }