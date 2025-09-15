# app/modules/insurance/quotations/models/quotation_attachment_model.py

from sqlalchemy import Column, Text, DateTime, UUID, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import datetime
import os
from pathlib import Path


class QuotationAttachment(Base):
    """
    Quotation Attachment model for managing file uploads
    
    This model handles file attachments associated with quotations,
    supporting various file types and providing metadata about
    uploaded files including upload tracking and file management.
    """
    __tablename__ = "quotation_attachments"

    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    quotation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=True)
    
    # File information
    file_name = Column(Text, nullable=False)
    file_url = Column(Text, nullable=False)
    file_type = Column(Text, nullable=True)
    
    # Upload tracking
    uploaded_at = Column(DateTime, nullable=False, server_default=func.now())
    uploaded_by = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)
    
    # Audit fields
    created_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    updated_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=True, onupdate=func.current_timestamp())
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    quotation = relationship("Quotation", back_populates="attachments")

    def __repr__(self):
        return f"<QuotationAttachment(id={self.id}, file_name={self.file_name}, file_type={self.file_type})>"

    @property
    def file_extension(self) -> str:
        """Get the file extension from the file name"""
        return Path(self.file_name).suffix.lower()

    @property
    def file_size_display(self) -> str:
        """Get a human-readable file size (would need actual file size from storage)"""
        # This would typically require checking the actual file
        # For now, return a placeholder
        return "Unknown size"

    @property
    def is_image(self) -> bool:
        """Check if the attachment is an image file"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        return self.file_extension in image_extensions

    @property
    def is_document(self) -> bool:
        """Check if the attachment is a document file"""
        document_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'}
        return self.file_extension in document_extensions

    @property
    def is_archived(self) -> bool:
        """Check if the attachment is archived"""
        return self.archived_at is not None

    @property
    def file_category(self) -> str:
        """Get the category of the file based on extension"""
        if self.is_image:
            return "image"
        elif self.is_document:
            return "document"
        elif self.file_extension in {'.zip', '.rar', '.7z', '.tar', '.gz'}:
            return "archive"
        elif self.file_extension in {'.mp4', '.avi', '.mov', '.wmv', '.flv'}:
            return "video"
        elif self.file_extension in {'.mp3', '.wav', '.flac', '.aac'}:
            return "audio"
        else:
            return "other"

    @property
    def is_safe_file_type(self) -> bool:
        """Check if the file type is considered safe for upload"""
        safe_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.csv', '.json', '.xml'
        }
        return self.file_extension in safe_extensions

    @classmethod
    def create_attachment(cls, quotation_id: str, file_name: str, file_url: str, 
                         file_type: str = None, uploaded_by: str = None) -> 'QuotationAttachment':
        """
        Factory method to create a quotation attachment
        """
        # Auto-detect file type if not provided
        if file_type is None:
            file_type = Path(file_name).suffix.lower().lstrip('.')
        
        return cls(
            quotation_id=quotation_id,
            file_name=file_name,
            file_url=file_url,
            file_type=file_type,
            uploaded_by=uploaded_by,
            created_by=uploaded_by
        )

    def update_file_info(self, new_file_name: str = None, new_file_url: str = None) -> None:
        """Update file information"""
        if new_file_name:
            self.file_name = new_file_name
            # Update file type based on new name
            self.file_type = Path(new_file_name).suffix.lower().lstrip('.')
        
        if new_file_url:
            self.file_url = new_file_url

    def soft_delete(self) -> None:
        """Soft delete the attachment by setting archived_at"""
        self.archived_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted attachment"""
        self.archived_at = None

    def get_download_url(self, base_url: str = "") -> str:
        """Get the full download URL for the attachment"""
        if self.file_url.startswith('http'):
            return self.file_url
        else:
            return f"{base_url.rstrip('/')}/{self.file_url.lstrip('/')}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert quotation attachment to dictionary representation"""
        return {
            'id': str(self.id),
            'quotation_id': str(self.quotation_id) if self.quotation_id else None,
            'file_name': self.file_name,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'file_extension': self.file_extension,
            'file_category': self.file_category,
            'is_image': self.is_image,
            'is_document': self.is_document,
            'is_safe_file_type': self.is_safe_file_type,
            'is_archived': self.is_archived,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'uploaded_by': str(self.uploaded_by) if self.uploaded_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    # Common file type constants
    class FileTypes:
        PDF = "pdf"
        WORD = "docx"
        EXCEL = "xlsx"
        IMAGE_JPEG = "jpg"
        IMAGE_PNG = "png"
        TEXT = "txt"
        CSV = "csv"