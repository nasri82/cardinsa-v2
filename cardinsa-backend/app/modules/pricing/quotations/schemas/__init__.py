# app/modules/pricing/quotations/schemas/__init__.py

"""
Quotation schemas package for request/response models.
"""

from .quotation_schema import (
    # Enums
    QuotationStatusEnum,
    
    # Base schemas
    QuotationBase,
    QuotationCreate,
    QuotationUpdate,
    QuotationResponse,
    QuotationSummary,
    
    # Action schemas
    QuotationStatusUpdate,
    
    # Calculation schemas
    QuotationCalculationRequest,
    QuotationCalculationResponse,
)

from .quotation_item_schema import (
    QuotationItemBase,
    QuotationItemCreate,
    QuotationItemUpdate,
    QuotationItemResponse,
    QuotationItemSummary,
    QuotationItemBulkCreate,
    QuotationItemLocalizedResponse,
    QuotationItemMetadataUpdate,
)

from .quotation_factor_schema import (
    # Enums
    FactorType,
    
    # Base schemas
    QuotationFactorBase,
    QuotationFactorCreate,
    QuotationFactorUpdate,
    QuotationFactorResponse,
    QuotationFactorSummary,
    
    # Request schemas
    QuotationFactorNumericRequest,
    QuotationFactorBooleanRequest,
    QuotationFactorComplexRequest,
    QuotationFactorBulkCreate,
    
    # Analysis schemas
    QuotationFactorsByType,
    QuotationFactorsGrouped,
    QuotationFactorImpactAnalysis,
    QuotationFactorValidation,
)

# Import from the workflow log schema file (the existing one)
from .quotation_workflow_log_schema import (
    # Enums
    WorkflowEvent,
    EventCategory,
    
    # Main workflow log schemas
    QuotationWorkflowLogBase,
    QuotationWorkflowLogCreate,
    QuotationWorkflowLogResponse,
    QuotationWorkflowLogSummary,
    
    # Advanced workflow schemas
    QuotationWorkflowEventRequest,
    QuotationWorkflowTimeline,
    QuotationWorkflowMetrics,
    QuotationWorkflowLogBulkCreate,
    QuotationWorkflowEventFilter,
    QuotationWorkflowCriticalEvent,
    QuotationWorkflowAuditSummary,
    QuotationWorkflowPerformanceMetrics,
    QuotationWorkflowEventStatistics,
    QuotationWorkflowHealthCheck,
)

# Aliases for backward compatibility
QuotationStatus = QuotationStatusEnum
QuotationCreateSchema = QuotationCreate
QuotationUpdateSchema = QuotationUpdate
QuotationResponseSchema = QuotationResponse

__all__ = [
    # Main quotation schemas
    "QuotationBase",
    "QuotationCreate",
    "QuotationUpdate", 
    "QuotationResponse",
    "QuotationSummary",
    
    # Status and enums
    "QuotationStatusEnum",
    "QuotationStatus",  # Alias
    
    # Action schemas
    "QuotationStatusUpdate",
    
    # Calculation schemas
    "QuotationCalculationRequest",
    "QuotationCalculationResponse",
    
    # Quotation item schemas
    "QuotationItemBase",
    "QuotationItemCreate",
    "QuotationItemUpdate",
    "QuotationItemResponse",
    "QuotationItemSummary",
    "QuotationItemBulkCreate",
    "QuotationItemLocalizedResponse",
    "QuotationItemMetadataUpdate",
    
    # Quotation factor enums
    "FactorType",
    
    # Quotation factor schemas
    "QuotationFactorBase",
    "QuotationFactorCreate",
    "QuotationFactorUpdate",
    "QuotationFactorResponse",
    "QuotationFactorSummary",
    
    # Factor request schemas
    "QuotationFactorNumericRequest",
    "QuotationFactorBooleanRequest",
    "QuotationFactorComplexRequest",
    "QuotationFactorBulkCreate",
    
    # Factor analysis schemas
    "QuotationFactorsByType",
    "QuotationFactorsGrouped",
    "QuotationFactorImpactAnalysis",
    "QuotationFactorValidation",
    
    # Workflow enums
    "WorkflowEvent",
    "EventCategory",
    
    # Workflow log schemas
    "QuotationWorkflowLogBase",
    "QuotationWorkflowLogCreate",
    "QuotationWorkflowLogResponse",
    "QuotationWorkflowLogSummary",
    
    # Advanced workflow schemas
    "QuotationWorkflowEventRequest",
    "QuotationWorkflowTimeline",
    "QuotationWorkflowMetrics",
    "QuotationWorkflowLogBulkCreate",
    "QuotationWorkflowEventFilter",
    "QuotationWorkflowCriticalEvent",
    "QuotationWorkflowAuditSummary",
    "QuotationWorkflowPerformanceMetrics",
    "QuotationWorkflowEventStatistics",
    "QuotationWorkflowHealthCheck",
    
    # Backward compatibility aliases
    "QuotationCreateSchema",
    "QuotationUpdateSchema",
    "QuotationResponseSchema",
]