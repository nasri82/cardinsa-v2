# app/modules/pricing/quotations/schemas/quotation_workflow_log_schema.py

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class WorkflowEvent(str, Enum):
    """Workflow event enumeration for schema validation"""
    CREATED = "quotation_created"
    CALCULATED = "premium_calculated"
    SUBMITTED = "quotation_submitted"
    APPROVED = "quotation_approved"
    REJECTED = "quotation_rejected"
    MODIFIED = "quotation_modified"
    EXPIRED = "quotation_expired"
    CONVERTED = "quotation_converted"
    LOCKED = "quotation_locked"
    UNLOCKED = "quotation_unlocked"
    DOCUMENT_GENERATED = "document_generated"
    EMAIL_SENT = "email_sent"
    REMINDER_SENT = "reminder_sent"
    FOLLOW_UP_SCHEDULED = "follow_up_scheduled"
    CUSTOMER_VIEWED = "customer_viewed"
    AGENT_ASSIGNED = "agent_assigned"
    PRICING_UPDATED = "pricing_updated"
    COVERAGE_MODIFIED = "coverage_modified"
    VALIDATION_FAILED = "validation_failed"
    VALIDATION_PASSED = "validation_passed"


class EventCategory(str, Enum):
    """Event category enumeration"""
    LIFECYCLE = "lifecycle"
    PRICING = "pricing"
    APPROVAL = "approval"
    MODIFICATION = "modification"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    COMMUNICATION = "communication"
    INTERACTION = "interaction"
    ASSIGNMENT = "assignment"
    VALIDATION = "validation"
    GENERAL = "general"


class QuotationWorkflowLogBase(BaseModel):
    """Base quotation workflow log schema with common fields"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )
    
    quotation_id: Optional[UUID] = Field(None, description="Parent quotation UUID")
    event: str = Field(..., min_length=1, description="Event description")
    notes: Optional[str] = Field(None, description="Additional event notes")
    created_by: Optional[UUID] = Field(None, description="User who triggered the event")

    @field_validator('event')
    @classmethod
    def validate_event(cls, v):
        if not v.strip():
            raise ValueError('Event cannot be empty')
        return v.strip()

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v


class QuotationWorkflowLogCreate(QuotationWorkflowLogBase):
    """Schema for creating a new quotation workflow log"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "event": "premium_calculated",
                "notes": "Premium calculation completed with all factors applied",
                "created_by": "456e7890-e89b-12d3-a456-426614174000"
            }
        }
    )
    
    quotation_id: UUID = Field(..., description="Parent quotation UUID is required")


class QuotationWorkflowLogResponse(QuotationWorkflowLogBase):
    """Schema for quotation workflow log response"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Workflow log UUID")
    created_at: datetime = Field(..., description="Event creation datetime")
    
    # Computed properties
    event_category: Optional[EventCategory] = Field(None, description="Event category")
    is_system_event: Optional[bool] = Field(None, description="Whether event was system-generated")
    is_user_action: Optional[bool] = Field(None, description="Whether event was user-triggered")
    is_critical_event: Optional[bool] = Field(None, description="Whether event is critical")


class QuotationWorkflowLogSummary(BaseModel):
    """Lightweight quotation workflow log summary"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    quotation_id: UUID
    event: str
    created_at: datetime
    created_by: Optional[UUID]
    event_category: Optional[EventCategory] = None


class QuotationWorkflowEventRequest(BaseModel):
    """Schema for creating workflow event"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "document_generated",
                "notes": "PDF quotation document generated successfully",
                "additional_data": {
                    "document_type": "quotation_pdf",
                    "file_size": "245KB",
                    "generation_time": "2.3s"
                }
            }
        }
    )
    
    event_type: WorkflowEvent = Field(..., description="Type of workflow event")
    notes: Optional[str] = Field(None, description="Event notes")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional event data")


class QuotationWorkflowTimeline(BaseModel):
    """Schema for complete workflow timeline"""
    
    model_config = ConfigDict(from_attributes=True)
    
    quotation_id: UUID
    events: List[QuotationWorkflowLogResponse]
    total_events: int = Field(..., description="Total number of events")
    event_categories: Dict[str, int] = Field(..., description="Event count by category")
    time_span: Optional[int] = Field(None, description="Total time span in minutes")
    most_active_period: Optional[str] = Field(None, description="Period with most activity")


class QuotationWorkflowMetrics(BaseModel):
    """Schema for workflow metrics and analytics"""
    
    model_config = ConfigDict(from_attributes=True)
    
    quotation_id: UUID
    total_events: int = Field(..., description="Total number of workflow events")
    system_events: int = Field(..., description="Number of system events")
    user_events: int = Field(..., description="Number of user events")
    critical_events: int = Field(..., description="Number of critical events")
    events_by_category: Dict[EventCategory, int] = Field(..., description="Events grouped by category")
    events_by_hour: Dict[int, int] = Field(..., description="Events distribution by hour")
    average_events_per_day: float = Field(..., description="Average events per day")
    peak_activity_hour: Optional[int] = Field(None, description="Hour with most activity (0-23)")


class QuotationWorkflowLogBulkCreate(BaseModel):
    """Schema for creating multiple workflow log entries"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "events": [
                    {
                        "event": "quotation_modified",
                        "notes": "Customer information updated"
                    },
                    {
                        "event": "pricing_updated",
                        "notes": "Premium recalculated due to changes"
                    },
                    {
                        "event": "document_generated",
                        "notes": "Updated quotation PDF generated"
                    }
                ]
            }
        }
    )
    
    quotation_id: UUID = Field(..., description="Parent quotation UUID")
    events: List[QuotationWorkflowLogCreate] = Field(..., min_length=1, description="List of events to log")
    
    @field_validator('events')
    @classmethod
    def validate_events_quotation_id(cls, v, info):
        quotation_id = info.data.get('quotation_id')
        if quotation_id:
            for event in v:
                if event.quotation_id and event.quotation_id != quotation_id:
                    raise ValueError('All events must belong to the same quotation')
                event.quotation_id = quotation_id
        return v


class QuotationWorkflowEventFilter(BaseModel):
    """Schema for filtering workflow events"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_categories": ["lifecycle", "pricing"],
                "date_from": "2025-12-01T00:00:00Z",
                "date_to": "2025-12-31T23:59:59Z",
                "is_critical_event": True
            }
        }
    )
    
    event_categories: Optional[List[EventCategory]] = Field(None, description="Filter by event categories")
    event_types: Optional[List[str]] = Field(None, description="Filter by specific event types")
    date_from: Optional[datetime] = Field(None, description="Filter events from date")
    date_to: Optional[datetime] = Field(None, description="Filter events to date")
    created_by: Optional[UUID] = Field(None, description="Filter by event creator")
    is_system_event: Optional[bool] = Field(None, description="Filter by system vs user events")
    is_critical_event: Optional[bool] = Field(None, description="Filter by critical events only")


class QuotationWorkflowCriticalEvent(BaseModel):
    """Schema for critical workflow events"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "quotation_id": "456e7890-e89b-12d3-a456-426614174000",
                "event": "validation_failed",
                "notes": "Customer age validation failed - DOB indicates minor",
                "created_at": "2025-12-09T10:30:00Z",
                "created_by": None,
                "severity_level": "high",
                "requires_attention": True,
                "resolution_status": "pending"
            }
        }
    )
    
    id: UUID
    quotation_id: UUID
    event: str
    notes: Optional[str]
    created_at: datetime
    created_by: Optional[UUID]
    severity_level: str = Field(..., description="Severity level (high/medium/low)")
    requires_attention: bool = Field(..., description="Whether event requires immediate attention")
    resolution_status: Optional[str] = Field(None, description="Resolution status if applicable")


class QuotationWorkflowAuditSummary(BaseModel):
    """Schema for workflow audit summary"""
    
    model_config = ConfigDict(from_attributes=True)
    
    quotation_id: UUID
    audit_period_start: datetime
    audit_period_end: datetime
    total_events: int
    compliance_score: float = Field(..., ge=0, le=1, description="Compliance score (0-1)")
    suspicious_activities: List[str] = Field(default_factory=list, description="Suspicious activities detected")
    missing_events: List[str] = Field(default_factory=list, description="Expected but missing events")
    event_integrity: bool = Field(..., description="Whether event timeline is complete")
    recommendations: List[str] = Field(default_factory=list, description="Audit recommendations")


class QuotationWorkflowPerformanceMetrics(BaseModel):
    """Schema for workflow performance metrics"""
    
    model_config = ConfigDict(from_attributes=True)
    
    quotation_id: UUID
    workflow_start_time: datetime
    workflow_end_time: Optional[datetime]
    total_duration_minutes: Optional[int]
    events_per_stage: Dict[str, int] = Field(..., description="Event count per workflow stage")
    bottlenecks: List[str] = Field(default_factory=list, description="Identified bottlenecks")
    efficiency_score: float = Field(..., ge=0, le=1, description="Workflow efficiency (0-1)")
    average_response_time: Optional[float] = Field(None, description="Average response time in minutes")
    sla_compliance: bool = Field(..., description="Whether workflow meets SLA requirements")


class QuotationWorkflowEventStatistics(BaseModel):
    """Schema for event statistics across quotations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    time_period: str = Field(..., description="Statistics time period")
    total_quotations: int = Field(..., description="Total quotations in period")
    total_events: int = Field(..., description="Total events in period")
    average_events_per_quotation: float = Field(..., description="Average events per quotation")
    most_common_events: Dict[str, int] = Field(..., description="Most common event types")
    event_trends: Dict[str, List[int]] = Field(..., description="Event trends over time")
    peak_activity_times: List[str] = Field(..., description="Peak activity time periods")


class QuotationWorkflowHealthCheck(BaseModel):
    """Schema for workflow health check"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "health_score": 0.85,
                "health_status": "healthy",
                "issues_detected": [],
                "warning_indicators": [
                    "No activity for 2 hours"
                ],
                "recommendations": [
                    "Consider sending follow-up reminder"
                ],
                "last_activity": "2025-12-09T08:30:00Z",
                "stale_duration_minutes": 120
            }
        }
    )
    
    quotation_id: UUID
    health_score: float = Field(..., ge=0, le=1, description="Overall health score (0-1)")
    health_status: str = Field(..., description="Health status (healthy/warning/critical)")
    issues_detected: List[str] = Field(default_factory=list, description="Issues detected")
    warning_indicators: List[str] = Field(default_factory=list, description="Warning indicators")
    recommendations: List[str] = Field(default_factory=list, description="Health improvement recommendations")
    last_activity: datetime = Field(..., description="Last workflow activity")
    stale_duration_minutes: int = Field(..., description="Minutes since last activity")