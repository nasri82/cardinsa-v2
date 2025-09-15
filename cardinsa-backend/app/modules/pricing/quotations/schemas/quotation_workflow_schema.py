# app/modules/pricing/quotations/schemas/quotation_workflow_schema.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class WorkflowEventType(str, Enum):
    """Workflow event types for quotations"""
    CREATED = "created"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    EXPIRED = "expired"
    CONVERTED = "converted"
    CANCELLED = "cancelled"
    REVIEWED = "reviewed"
    CALCULATED = "calculated"
    UPDATED = "updated"
    ARCHIVED = "archived"
    RESTORED = "restored"

class QuotationWorkflowLogBase(BaseModel):
    """Base schema for quotation workflow logs"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    quotation_id: Optional[UUID] = Field(None, description="Quotation ID")
    event: Optional[str] = Field(None, description="Workflow event description")
    notes: Optional[str] = Field(None, description="Additional notes about the event")
    created_by: Optional[UUID] = Field(None, description="User who triggered the event")

class QuotationWorkflowLogCreate(QuotationWorkflowLogBase):
    """Schema for creating a quotation workflow log"""
    
    quotation_id: UUID = Field(..., description="Quotation ID is required")
    event: str = Field(..., min_length=1, description="Event description is required")

class QuotationWorkflowLogUpdate(BaseModel):
    """Schema for updating a quotation workflow log"""
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    # Generally workflow logs are immutable, but allow notes updates
    notes: Optional[str] = None

class QuotationWorkflowLogResponse(QuotationWorkflowLogBase):
    """Schema for quotation workflow log responses"""
    
    id: UUID = Field(..., description="Workflow log ID")
    created_at: datetime = Field(..., description="Event timestamp")

class QuotationWorkflowLogSummary(BaseModel):
    """Lightweight schema for workflow log lists"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    quotation_id: UUID
    event: str
    created_at: datetime
    created_by: Optional[UUID]

class WorkflowTransition(BaseModel):
    """Schema for workflow state transitions"""
    
    model_config = ConfigDict(from_attributes=True)
    
    from_status: Optional[str] = Field(None, description="Previous status")
    to_status: str = Field(..., description="New status")
    event_type: WorkflowEventType = Field(..., description="Type of workflow event")
    notes: Optional[str] = Field(None, description="Transition notes")
    triggered_by: Optional[UUID] = Field(None, description="User who triggered transition")

class QuotationWorkflowState(BaseModel):
    """Schema representing current workflow state"""
    
    model_config = ConfigDict(from_attributes=True)
    
    quotation_id: UUID
    current_status: str
    is_locked: bool
    can_edit: bool = Field(description="Whether quotation can be edited")
    can_submit: bool = Field(description="Whether quotation can be submitted")
    can_approve: bool = Field(description="Whether quotation can be approved")
    can_reject: bool = Field(description="Whether quotation can be rejected")
    can_lock: bool = Field(description="Whether quotation can be locked")
    can_unlock: bool = Field(description="Whether quotation can be unlocked")
    available_transitions: list[WorkflowEventType] = Field(
        default_factory=list,
        description="Available workflow transitions"
    )
    last_event: Optional[QuotationWorkflowLogSummary] = None

class BulkWorkflowOperation(BaseModel):
    """Schema for bulk workflow operations"""
    
    quotation_ids: list[UUID] = Field(..., min_length=1, description="List of quotation IDs")
    operation: WorkflowEventType = Field(..., description="Workflow operation to perform")
    notes: Optional[str] = Field(None, description="Notes for the operation")
    
class BulkWorkflowResult(BaseModel):
    """Schema for bulk workflow operation results"""
    
    model_config = ConfigDict(from_attributes=True)
    
    successful_operations: list[UUID] = Field(default_factory=list)
    failed_operations: list[dict] = Field(default_factory=list)  # {quotation_id, error}
    total_requested: int
    total_successful: int
    total_failed: int