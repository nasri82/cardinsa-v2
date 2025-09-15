# app/modules/insurance/quotations/schemas/quotation_document_schema.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

# Import enum from models
from ..models import DocumentType


class QuotationDocumentType(str, Enum):
    """Document type enumeration for schema validation"""
    QUOTATION_PDF = "quotation_pdf"
    PROPOSAL = "proposal"
    TERMS_CONDITIONS = "terms_conditions"
    PRODUCT_BROCHURE = "product_brochure"
    COVERAGE_SUMMARY = "coverage_summary"
    PREMIUM_BREAKDOWN = "premium_breakdown"
    POLICY_WORDING = "policy_wording"
    APPLICATION_FORM = "application_form"
    MEDICAL_QUESTIONNAIRE = "medical_questionnaire"
    UNDERWRITING_REPORT = "underwriting_report"
    RENEWAL_NOTICE = "renewal_notice"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CERTIFICATE = "certificate"
    ENDORSEMENT = "endorsement"
    CLAIM_FORM = "claim_form"
    CORRESPONDENCE = "correspondence"
    OTHER = "other"


class QuotationDocumentBase(BaseModel):
    """Base quotation document schema with common fields"""
    quotation_id: Optional[UUID] = Field(None, description="Parent quotation UUID")
    document_type: QuotationDocumentType = Field(..., description="Type of document")
    document_name: str = Field(..., min_length=1, max_length=255, description="Document name")
    file_path: Optional[str] = Field(None, description="Path to document file")
    version: int = Field(1, ge=1, description="Document version number")

    @validator('document_name')
    def validate_document_name(cls, v):
        if not v.strip():
            raise ValueError('Document name cannot be empty')
        return v.strip()

    @validator('file_path')
    def validate_file_path(cls, v):
        if v is not None and not v.strip():
            return None
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class QuotationDocumentCreate(QuotationDocumentBase):
    """Schema for creating a new quotation document"""
    quotation_id: UUID = Field(..., description="Parent quotation UUID is required")
    
    class Config:
        schema_extra = {
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "document_type": "quotation_pdf",
                "document_name": "Motor Insurance Quote - John Doe.pdf",
                "file_path": "/documents/quotations/2025/12/quote_123.pdf",
                "version": 1
            }
        }


class QuotationDocumentUpdate(BaseModel):
    """Schema for updating a quotation document"""
    document_type: Optional[QuotationDocumentType] = Field(None, description="Type of document")
    document_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Document name")
    file_path: Optional[str] = Field(None, description="Path to document file")
    version: Optional[int] = Field(None, ge=1, description="Document version number")

    @validator('document_name')
    def validate_document_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Document name cannot be empty')
        return v.strip() if v else v

    @validator('file_path')
    def validate_file_path(cls, v):
        if v is not None and not v.strip():
            return None
        return v

    class Config:
        from_attributes = True


class QuotationDocumentResponse(QuotationDocumentBase):
    """Schema for quotation document response"""
    id: UUID = Field(..., description="Document UUID")
    generated_at: datetime = Field(..., description="Document generation datetime")
    created_by: Optional[UUID] = Field(None, description="Creator UUID")
    updated_by: Optional[UUID] = Field(None, description="Last updater UUID")
    created_at: datetime = Field(..., description="Creation datetime")
    updated_at: Optional[datetime] = Field(None, description="Last update datetime")
    archived_at: Optional[datetime] = Field(None, description="Archive datetime")
    
    # Computed properties
    document_type_display: Optional[str] = Field(None, description="Human-readable document type")
    file_extension: Optional[str] = Field(None, description="File extension")
    is_pdf: Optional[bool] = Field(None, description="Whether document is PDF")
    is_customer_facing: Optional[bool] = Field(None, description="Whether document is for customer")
    is_internal_document: Optional[bool] = Field(None, description="Whether document is internal")
    is_latest_version: Optional[bool] = Field(None, description="Whether this is latest version")
    is_archived: Optional[bool] = Field(None, description="Whether document is archived")
    
    class Config:
        from_attributes = True


class QuotationDocumentSummary(BaseModel):
    """Lightweight quotation document summary"""
    id: UUID
    quotation_id: UUID
    document_type: QuotationDocumentType
    document_name: str
    version: int
    generated_at: datetime
    is_customer_facing: bool
    
    class Config:
        from_attributes = True


class QuotationDocumentGenerate(BaseModel):
    """Schema for document generation request"""
    document_type: QuotationDocumentType = Field(..., description="Type of document to generate")
    template_id: Optional[UUID] = Field(None, description="Template to use for generation")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="Custom data for document")
    language: str = Field("en", description="Document language (en/ar)")
    include_attachments: bool = Field(False, description="Whether to include attachments")
    watermark: Optional[str] = Field(None, description="Watermark text")
    
    @validator('language')
    def validate_language(cls, v):
        if v not in ['en', 'ar']:
            raise ValueError('Language must be either "en" or "ar"')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "document_type": "quotation_pdf",
                "template_id": "456e7890-e89b-12d3-a456-426614174000",
                "language": "en",
                "include_attachments": True,
                "watermark": "DRAFT",
                "custom_data": {
                    "show_breakdown": True,
                    "include_terms": True,
                    "highlight_discounts": True
                }
            }
        }


class QuotationDocumentBulkGenerate(BaseModel):
    """Schema for bulk document generation"""
    quotation_id: UUID = Field(..., description="Quotation UUID")
    document_types: List[QuotationDocumentType] = Field(..., min_items=1, description="Document types to generate")
    language: str = Field("en", description="Document language")
    batch_options: Optional[Dict[str, Any]] = Field(None, description="Batch generation options")
    
    @validator('language')
    def validate_language(cls, v):
        if v not in ['en', 'ar']:
            raise ValueError('Language must be either "en" or "ar"')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "document_types": ["quotation_pdf", "coverage_summary", "terms_conditions"],
                "language": "en",
                "batch_options": {
                    "zip_output": True,
                    "email_customer": False,
                    "watermark": "OFFICIAL"
                }
            }
        }


class QuotationDocumentVersion(BaseModel):
    """Schema for document versioning"""
    current_version: int = Field(..., ge=1, description="Current version number")
    new_version: int = Field(..., ge=1, description="New version number")
    version_notes: Optional[str] = Field(None, description="Notes about version change")
    auto_increment: bool = Field(True, description="Whether to auto-increment version")
    
    @validator('new_version')
    def validate_version_increment(cls, v, values):
        current = values.get('current_version')
        if current and v <= current:
            raise ValueError('New version must be greater than current version')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "current_version": 1,
                "new_version": 2,
                "version_notes": "Updated premium calculation and added new coverage options",
                "auto_increment": True
            }
        }


class QuotationDocumentDownload(BaseModel):
    """Schema for document download request"""
    include_metadata: bool = Field(False, description="Include metadata in response")
    download_format: str = Field("original", description="Download format (original/pdf/zip)")
    access_tracking: bool = Field(True, description="Track download access")
    
    @validator('download_format')
    def validate_format(cls, v):
        valid_formats = ['original', 'pdf', 'zip']
        if v not in valid_formats:
            raise ValueError(f'Download format must be one of: {valid_formats}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "include_metadata": True,
                "download_format": "pdf",
                "access_tracking": True
            }
        }


class QuotationDocumentList(BaseModel):
    """Schema for document list response"""
    quotation_id: UUID
    documents: List[QuotationDocumentSummary]
    total_documents: int = Field(..., description="Total number of documents")
    documents_by_type: Dict[str, int] = Field(..., description="Document count by type")
    latest_document: Optional[QuotationDocumentSummary] = Field(None, description="Most recently created document")
    customer_facing_count: int = Field(..., description="Number of customer-facing documents")
    internal_count: int = Field(..., description="Number of internal documents")
    
    class Config:
        from_attributes = True


class QuotationDocumentArchive(BaseModel):
    """Schema for document archiving"""
    archive_reason: str = Field(..., min_length=1, description="Reason for archiving")
    archive_all_versions: bool = Field(False, description="Archive all versions of document")
    
    @validator('archive_reason')
    def validate_reason(cls, v):
        if not v.strip():
            raise ValueError('Archive reason cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "archive_reason": "Document superseded by updated version",
                "archive_all_versions": False
            }
        }