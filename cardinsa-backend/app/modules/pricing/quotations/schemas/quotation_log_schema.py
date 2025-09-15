# app/modules/insurance/quotations/schemas/quotation_log_schema.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

# Import enum from models
from ..models import QuotationStatusEnum


class LoggedQuotationStatus(str, Enum):
    """Status enumeration for logging"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    CALCULATED = "calculated"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"
    CANCELLED = "cancelled"


class QuotationLogBase(BaseModel):
    """Base quotation log schema with common fields"""
    quotation_id: Optional[UUID] = Field(None, description="Parent quotation UUID")
    status_from: Optional[LoggedQuotationStatus] = Field(None, description="Previous status")
    status_to: Optional[LoggedQuotationStatus] = Field(None, description="New status")
    actor_id: Optional[UUID] = Field(None, description="User who made the change")
    notes: Optional[str] = Field(None, description="Additional notes about the change")

    @validator('notes')
    def validate_notes(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class QuotationLogCreate(QuotationLogBase):
    """Schema for creating a new quotation log"""
    quotation_id: UUID = Field(..., description="Parent quotation UUID is required")
    status_to: LoggedQuotationStatus = Field(..., description="New status is required")
    
    class Config:
        schema_extra = {
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "status_from": "draft",
                "status_to": "calculated",
                "actor_id": "456e7890-e89b-12d3-a456-426614174000",
                "notes": "Premium calculation completed successfully"
            }
        }


class QuotationLogResponse(QuotationLogBase):
    """Schema for quotation log response"""
    id: UUID = Field(..., description="Quotation log UUID")
    created_at: datetime = Field(..., description="Log creation datetime")
    
    # Computed properties
    transition_description: Optional[str] = Field(None, description="Human-readable transition description")
    is_workflow_progression: Optional[bool] = Field(None, description="Whether this is forward progression")
    is_regression: Optional[bool] = Field(None, description="Whether this is backward movement")
    is_terminal_status: Optional[bool] = Field(None, description="Whether new status is terminal")
    
    class Config:
        from_attributes = True


class QuotationLogSummary(BaseModel):
    """Lightweight quotation log summary"""
    id: UUID
    quotation_id: UUID
    status_from: Optional[LoggedQuotationStatus]
    status_to: LoggedQuotationStatus
    created_at: datetime
    actor_id: Optional[UUID]
    
    class Config:
        from_attributes = True


class QuotationStatusTransition(BaseModel):
    """Schema for status transition requests"""
    new_status: LoggedQuotationStatus = Field(..., description="Target status")
    notes: Optional[str] = Field(None, description="Transition notes")
    
    @validator('notes')
    def validate_notes(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "new_status": "approved",
                "notes": "Approved by senior underwriter after risk assessment"
            }
        }


class QuotationLogTimeline(BaseModel):
    """Schema for quotation timeline view"""
    quotation_id: UUID
    logs: List[QuotationLogResponse]
    total_transitions: int = Field(..., description="Total number of status transitions")
    current_status: LoggedQuotationStatus = Field(..., description="Current quotation status")
    time_in_current_status: Optional[int] = Field(None, description="Minutes in current status")
    total_processing_time: Optional[int] = Field(None, description="Total processing time in minutes")
    
    class Config:
        from_attributes = True


class QuotationWorkflowAnalysis(BaseModel):
    """Schema for workflow analysis"""
    quotation_id: UUID
    workflow_efficiency: float = Field(..., ge=0, le=1, description="Efficiency score (0-1)")
    total_transitions: int = Field(..., description="Total number of transitions")
    backward_transitions: int = Field(..., description="Number of regression transitions")
    average_time_per_status: Dict[str, int] = Field(..., description="Average time per status in minutes")
    bottleneck_status: Optional[str] = Field(None, description="Status where quotation spends most time")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "workflow_efficiency": 0.85,
                "total_transitions": 5,
                "backward_transitions": 1,
                "average_time_per_status": {
                    "draft": 120,
                    "calculated": 30,
                    "pending_approval": 1440,
                    "approved": 0
                },
                "bottleneck_status": "pending_approval"
            }
        }


class QuotationLogValidation(BaseModel):
    """Schema for validating status transitions"""
    from_status: LoggedQuotationStatus
    to_status: LoggedQuotationStatus
    is_valid_transition: bool = Field(..., description="Whether transition is valid")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    required_conditions: List[str] = Field(default_factory=list, description="Required conditions")
    
    class Config:
        schema_extra = {
            "example": {
                "from_status": "draft",
                "to_status": "approved",
                "is_valid_transition": False,
                "validation_errors": [
                    "Cannot approve quotation directly from draft status",
                    "Quotation must be calculated before approval"
                ],
                "required_conditions": [
                    "Premium must be calculated",
                    "All required fields must be completed",
                    "Risk assessment must be performed"
                ]
            }
        }


class QuotationLogBulkCreate(BaseModel):
    """Schema for creating multiple log entries"""
    quotation_id: UUID = Field(..., description="Parent quotation UUID")
    logs: List[QuotationLogCreate] = Field(..., min_items=1, description="List of logs to create")
    
    @validator('logs')
    def validate_logs_quotation_id(cls, v, values):
        quotation_id = values.get('quotation_id')
        if quotation_id:
            for log in v:
                if log.quotation_id and log.quotation_id != quotation_id:
                    raise ValueError('All logs must belong to the same quotation')
                log.quotation_id = quotation_id
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "logs": [
                    {
                        "status_from": "draft",
                        "status_to": "calculated",
                        "notes": "Premium calculation completed"
                    },
                    {
                        "status_from": "calculated",
                        "status_to": "pending_approval",
                        "notes": "Submitted for underwriter review"
                    }
                ]
            }
        }


class QuotationLogStatistics(BaseModel):
    """Schema for log statistics"""
    quotation_id: UUID
    total_logs: int = Field(..., description="Total number of log entries")
    status_distribution: Dict[str, int] = Field(..., description="Count per status")
    actor_distribution: Dict[str, int] = Field(..., description="Count per actor")
    most_active_day: Optional[str] = Field(None, description="Date with most activity")
    average_daily_transitions: float = Field(..., description="Average transitions per day")
    
    class Config:
        from_attributes = True