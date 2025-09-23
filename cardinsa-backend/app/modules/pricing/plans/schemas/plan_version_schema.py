# app/modules/pricing/plans/schemas/plan_version_schema.py

"""
Plan Version Schema

Pydantic schemas for Plan Version validation and serialization.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, validator, ConfigDict
from pydantic.types import constr


# ================================================================
# ENUMS
# ================================================================

class VersionStatus(str, Enum):
    """Version status enumeration"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ChangeType(str, Enum):
    """Type of change in version"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class ApprovalStatus(str, Enum):
    """Approval status for version"""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"


# ================================================================
# CREATE SCHEMAS
# ================================================================

class PlanVersionCreate(BaseModel):
    """Schema for creating a plan version"""
    
    model_config = ConfigDict(from_attributes=True)
    
    version_description: constr(min_length=1, max_length=500) = Field(
        ...,
        description="Description of this version"
    )
    
    change_type: ChangeType = Field(
        ChangeType.MINOR,
        description="Type of change"
    )
    
    changes_summary: Optional[str] = Field(
        None,
        description="Summary of changes"
    )
    
    changes_from_previous: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Detailed changelog"
    )
    
    created_by_reason: Optional[str] = Field(
        None,
        description="Reason for creating this version"
    )
    
    regulatory_approval_required: bool = Field(
        False,
        description="Requires regulatory approval"
    )
    
    effective_date: Optional[datetime] = Field(
        None,
        description="When version becomes effective"
    )
    
    # Snapshots
    benefits_snapshot: Optional[Dict[str, Any]] = Field(
        None,
        description="Snapshot of benefits configuration"
    )
    
    pricing_snapshot: Optional[Dict[str, Any]] = Field(
        None,
        description="Snapshot of pricing configuration"
    )
    
    # Metadata
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Version tags"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


# ================================================================
# UPDATE SCHEMAS
# ================================================================

class PlanVersionUpdate(BaseModel):
    """Schema for updating a plan version (draft only)"""
    
    model_config = ConfigDict(from_attributes=True)
    
    version_description: Optional[str] = None
    changes_summary: Optional[str] = None
    changes_from_previous: Optional[Dict[str, Any]] = None
    created_by_reason: Optional[str] = None
    
    # Dates
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    
    # Snapshots
    benefits_snapshot: Optional[Dict[str, Any]] = None
    pricing_snapshot: Optional[Dict[str, Any]] = None
    
    # Metadata
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# ================================================================
# RESPONSE SCHEMAS
# ================================================================

class PlanVersionResponse(BaseModel):
    """Response schema for plan version"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    plan_id: UUID
    version_number: int
    version_label: Optional[str]
    version_description: Optional[str]
    
    # Change tracking
    change_type: str
    changes_summary: Optional[str]
    changes_from_previous: Optional[Dict[str, Any]]
    created_by_reason: Optional[str]
    
    # Status
    status: str
    is_current_version: bool
    is_published: bool
    
    # Dates
    effective_date: Optional[datetime]
    expiry_date: Optional[datetime]
    created_at: datetime
    approved_at: Optional[datetime]
    
    # Regulatory
    regulatory_approval_required: bool
    approval_status: str
    regulatory_reference: Optional[str]
    compliance_notes: Optional[str]
    
    # Users
    created_by: Optional[UUID]
    approved_by: Optional[UUID]
    
    # Metadata
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]


class PlanVersionDetailResponse(PlanVersionResponse):
    """Detailed version response with snapshots"""
    
    plan_snapshot: Optional[Dict[str, Any]]
    benefits_snapshot: Optional[Dict[str, Any]]
    pricing_snapshot: Optional[Dict[str, Any]]


# ================================================================
# COMPARISON SCHEMAS
# ================================================================

class VersionComparisonRequest(BaseModel):
    """Request for version comparison"""
    
    version_id1: UUID = Field(..., description="First version ID")
    version_id2: UUID = Field(..., description="Second version ID")
    include_snapshots: bool = Field(
        True,
        description="Include full snapshots in comparison"
    )


class VersionComparisonResponse(BaseModel):
    """Response for version comparison"""
    
    model_config = ConfigDict(from_attributes=True)
    
    version1: Dict[str, Any]
    version2: Dict[str, Any]
    changes: List[Dict[str, Any]]
    comparison_date: datetime


# ================================================================
# ROLLBACK SCHEMAS
# ================================================================

class VersionRollbackRequest(BaseModel):
    """Request for version rollback"""
    
    target_version_number: int = Field(
        ...,
        gt=0,
        description="Version number to rollback to"
    )
    reason: constr(min_length=10) = Field(
        ...,
        description="Reason for rollback"
    )
    create_backup: bool = Field(
        True,
        description="Create backup of current version"
    )


# ================================================================
# APPROVAL SCHEMAS
# ================================================================

class VersionApprovalRequest(BaseModel):
    """Request for version approval"""
    
    notes: Optional[str] = Field(
        None,
        description="Approval notes"
    )
    make_current: bool = Field(
        False,
        description="Make this the current version"
    )


class VersionRejectionRequest(BaseModel):
    """Request for version rejection"""
    
    reason: constr(min_length=10) = Field(
        ...,
        description="Rejection reason"
    )


# ================================================================
# HISTORY SCHEMAS
# ================================================================

class VersionHistoryFilters(BaseModel):
    """Filters for version history"""
    
    include_draft: bool = Field(
        False,
        description="Include draft versions"
    )
    change_type: Optional[ChangeType] = Field(
        None,
        description="Filter by change type"
    )
    status: Optional[VersionStatus] = Field(
        None,
        description="Filter by status"
    )
    created_by: Optional[UUID] = Field(
        None,
        description="Filter by creator"
    )
    date_from: Optional[datetime] = Field(
        None,
        description="From date"
    )
    date_to: Optional[datetime] = Field(
        None,
        description="To date"
    )


# ================================================================
# STATISTICS SCHEMAS
# ================================================================

class VersionStatistics(BaseModel):
    """Version statistics schema"""
    
    model_config = ConfigDict(from_attributes=True)
    
    total_versions: int
    current_version: Optional[int]
    current_version_label: Optional[str]
    last_modified: Optional[datetime]
    change_types: Dict[str, int]
    pending_approvals: int