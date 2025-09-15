# app/modules/insurance/quotations/models/quotation_document_model.py

from sqlalchemy import Column, String, Text, Integer, DateTime, UUID, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Enumeration for document types"""
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


class QuotationDocument(Base):
    """
    Quotation Document model for managing generated documents
    
    This model handles system-generated documents related to quotations,
    such as PDF quotes, proposals, and other formal documentation
    with versioning support and document lifecycle management.
    """
    __tablename__ = "quotation_documents"

    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    quotation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    
    # Document classification
    document_type = Column(String(50), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    
    # File storage information
    file_path = Column(Text, nullable=True)
    
    # Document metadata
    generated_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    version = Column(Integer, nullable=False, default=1)
    
    # Audit fields
    created_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    updated_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=True, onupdate=func.current_timestamp())
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    quotation = relationship("Quotation", back_populates="documents")

    def __repr__(self):
        return f"<QuotationDocument(id={self.id}, document_type={self.document_type}, version={self.version})>"

    @property
    def is_latest_version(self) -> bool:
        """Check if this is the latest version of this document type"""
        # This would require a database query to determine
        # For now, return True as a placeholder
        return True

    @property
    def file_extension(self) -> str:
        """Get the file extension from the file path"""
        if self.file_path:
            return self.file_path.split('.')[-1].lower()
        return ""

    @property
    def is_pdf(self) -> bool:
        """Check if the document is a PDF"""
        return self.file_extension == "pdf"

    @property
    def is_archived(self) -> bool:
        """Check if the document is archived"""
        return self.archived_at is not None

    @property
    def document_type_display(self) -> str:
        """Get a human-readable document type name"""
        type_mapping = {
            DocumentType.QUOTATION_PDF: "Quotation PDF",
            DocumentType.PROPOSAL: "Insurance Proposal",
            DocumentType.TERMS_CONDITIONS: "Terms & Conditions",
            DocumentType.PRODUCT_BROCHURE: "Product Brochure",
            DocumentType.COVERAGE_SUMMARY: "Coverage Summary",
            DocumentType.PREMIUM_BREAKDOWN: "Premium Breakdown",
            DocumentType.POLICY_WORDING: "Policy Wording",
            DocumentType.APPLICATION_FORM: "Application Form",
            DocumentType.MEDICAL_QUESTIONNAIRE: "Medical Questionnaire",
            DocumentType.UNDERWRITING_REPORT: "Underwriting Report",
            DocumentType.RENEWAL_NOTICE: "Renewal Notice",
            DocumentType.INVOICE: "Invoice",
            DocumentType.RECEIPT: "Payment Receipt",
            DocumentType.CERTIFICATE: "Certificate",
            DocumentType.ENDORSEMENT: "Policy Endorsement",
            DocumentType.CLAIM_FORM: "Claim Form",
            DocumentType.CORRESPONDENCE: "Correspondence",
            DocumentType.OTHER: "Other Document"
        }
        return type_mapping.get(self.document_type, self.document_type.replace('_', ' ').title())

    @property
    def is_customer_facing(self) -> bool:
        """Check if this document is intended for customer distribution"""
        customer_facing_types = [
            DocumentType.QUOTATION_PDF,
            DocumentType.PROPOSAL,
            DocumentType.TERMS_CONDITIONS,
            DocumentType.PRODUCT_BROCHURE,
            DocumentType.COVERAGE_SUMMARY,
            DocumentType.PREMIUM_BREAKDOWN,
            DocumentType.INVOICE,
            DocumentType.RECEIPT,
            DocumentType.CERTIFICATE
        ]
        return self.document_type in customer_facing_types

    @property
    def is_internal_document(self) -> bool:
        """Check if this is an internal document"""
        return not self.is_customer_facing

    @classmethod
    def create_document(cls, quotation_id: str, document_type: str, document_name: str,
                       file_path: str = None, created_by: str = None) -> 'QuotationDocument':
        """
        Factory method to create a quotation document
        """
        return cls(
            quotation_id=quotation_id,
            document_type=document_type,
            document_name=document_name,
            file_path=file_path,
            created_by=created_by
        )

    @classmethod
    def create_pdf_quote(cls, quotation_id: str, file_path: str, 
                        created_by: str = None, version: int = 1) -> 'QuotationDocument':
        """
        Factory method to create a PDF quotation document
        """
        return cls(
            quotation_id=quotation_id,
            document_type=DocumentType.QUOTATION_PDF,
            document_name=f"Quotation_v{version}.pdf",
            file_path=file_path,
            version=version,
            created_by=created_by
        )

    def increment_version(self) -> None:
        """Increment the document version"""
        self.version += 1
        # Update document name to reflect new version
        if "_v" in self.document_name:
            base_name = self.document_name.split("_v")[0]
            extension = self.document_name.split(".")[-1]
            self.document_name = f"{base_name}_v{self.version}.{extension}"

    def update_file_path(self, new_file_path: str) -> None:
        """Update the file path"""
        self.file_path = new_file_path

    def soft_delete(self) -> None:
        """Soft delete the document by setting archived_at"""
        self.archived_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted document"""
        self.archived_at = None

    def get_download_url(self, base_url: str = "") -> str:
        """Get the full download URL for the document"""
        if self.file_path:
            if self.file_path.startswith('http'):
                return self.file_path
            else:
                return f"{base_url.rstrip('/')}/{self.file_path.lstrip('/')}"
        return ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert quotation document to dictionary representation"""
        return {
            'id': str(self.id),
            'quotation_id': str(self.quotation_id),
            'document_type': self.document_type,
            'document_type_display': self.document_type_display,
            'document_name': self.document_name,
            'file_path': self.file_path,
            'file_extension': self.file_extension,
            'is_pdf': self.is_pdf,
            'is_customer_facing': self.is_customer_facing,
            'is_internal_document': self.is_internal_document,
            'version': self.version,
            'is_latest_version': self.is_latest_version,
            'is_archived': self.is_archived,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }