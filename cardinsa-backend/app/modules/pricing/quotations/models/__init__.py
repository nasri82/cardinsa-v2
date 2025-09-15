# app/modules/insurance/quotations/models/__init__.py

"""
Quotation Models Package

This package contains all SQLAlchemy models related to the quotations module,
providing comprehensive data models for insurance quotation management,
workflow tracking, document management, and audit logging.

Models included:
- Quotation: Main quotation entity with comprehensive customer and pricing data
- QuotationItem: Individual coverage items within quotations
- QuotationFactor: Pricing factors and their impact descriptions
- QuotationVersion: Version control and change tracking
- QuotationLog: Status change audit trail
- QuotationWorkflowLog: Detailed workflow event tracking
- QuotationAttachment: File upload management
- QuotationDocument: Generated document management
- QuotationCoverageOption: Coverage option pricing
- QuotationAuditLog: Comprehensive audit trail
"""

from .quotation_model import Quotation
from .quotation_item_model import QuotationItem
from .quotation_factor_model import QuotationFactor
from .quotation_version_model import QuotationVersion
from .quotation_log_model import QuotationLog, QuotationStatusEnum
from .quotation_workflow_log_model import QuotationWorkflowLog, WorkflowEventType
from .quotation_attachment_model import QuotationAttachment
from .quotation_document_model import QuotationDocument, DocumentType
from .quotation_coverage_option_model import QuotationCoverageOption
from .quotation_audit_log_model import QuotationAuditLog, AuditActionType

# Export all models for easy importing
__all__ = [
    # Main models
    "Quotation",
    "QuotationItem",
    "QuotationFactor",
    "QuotationVersion",
    "QuotationLog",
    "QuotationWorkflowLog",
    "QuotationAttachment",
    "QuotationDocument",
    "QuotationCoverageOption",
    "QuotationAuditLog",
    
    # Enums
    "QuotationStatusEnum",
    "WorkflowEventType",
    "DocumentType",
    "AuditActionType"
]

# Model relationships mapping for reference
MODEL_RELATIONSHIPS = {
    "Quotation": [
        "items",           # QuotationItem
        "factors",         # QuotationFactor
        "versions",        # QuotationVersion
        "logs",           # QuotationLog
        "workflow_logs",  # QuotationWorkflowLog
        "attachments",    # QuotationAttachment
        "documents",      # QuotationDocument
        "coverage_options", # QuotationCoverageOption
        "audit_logs"      # QuotationAuditLog
    ],
    "QuotationItem": ["quotation"],
    "QuotationFactor": ["quotation"],
    "QuotationVersion": ["quotation"],
    "QuotationLog": ["quotation"],
    "QuotationWorkflowLog": ["quotation"],
    "QuotationAttachment": ["quotation"],
    "QuotationDocument": ["quotation"],
    "QuotationCoverageOption": ["quotation"],
    "QuotationAuditLog": ["quotation"]
}

# Status workflow definitions
QUOTATION_STATUS_WORKFLOW = {
    "draft": ["in_progress", "calculated"],
    "in_progress": ["calculated", "draft"],
    "calculated": ["pending_approval", "approved", "in_progress"],
    "pending_approval": ["approved", "rejected", "calculated"],
    "approved": ["converted", "expired"],
    "rejected": ["draft", "calculated"],
    "converted": [],  # Terminal state
    "expired": ["draft"],  # Can restart
    "cancelled": []   # Terminal state
}

# Document type categories
DOCUMENT_CATEGORIES = {
    "customer_facing": [
        DocumentType.QUOTATION_PDF,
        DocumentType.PROPOSAL,
        DocumentType.TERMS_CONDITIONS,
        DocumentType.PRODUCT_BROCHURE,
        DocumentType.COVERAGE_SUMMARY,
        DocumentType.PREMIUM_BREAKDOWN,
        DocumentType.INVOICE,
        DocumentType.RECEIPT,
        DocumentType.CERTIFICATE
    ],
    "internal": [
        DocumentType.APPLICATION_FORM,
        DocumentType.MEDICAL_QUESTIONNAIRE,
        DocumentType.UNDERWRITING_REPORT,
        DocumentType.CORRESPONDENCE,
        DocumentType.OTHER
    ],
    "regulatory": [
        DocumentType.POLICY_WORDING,
        DocumentType.TERMS_CONDITIONS,
        DocumentType.ENDORSEMENT
    ]
}

# Audit event risk levels
AUDIT_RISK_LEVELS = {
    "HIGH": [
        AuditActionType.DATA_BREACH_ATTEMPT,
        AuditActionType.UNAUTHORIZED_ACCESS
    ],
    "MEDIUM": [
        AuditActionType.DELETE,
        AuditActionType.EXPORT
    ],
    "LOW": [
        AuditActionType.CREATE,
        AuditActionType.UPDATE,
        AuditActionType.ARCHIVE,
        AuditActionType.RESTORE
    ],
    "INFO": [
        AuditActionType.VIEW,
        AuditActionType.PRINT,
        AuditActionType.LOGIN_ACCESS
    ]
}