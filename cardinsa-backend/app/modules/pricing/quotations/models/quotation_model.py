# app/modules/pricing/quotations/models/quotation_model.py

from sqlalchemy import Column, String, Text, Date, DateTime, Boolean, Numeric, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum

class QuotationStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted" 
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"

class Quotation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "quotations"
    
    # Basic Information
    quote_number: Mapped[Optional[str]] = mapped_column(String(50))
    customer_name: Mapped[Optional[str]] = mapped_column(Text)
    customer_email: Mapped[Optional[str]] = mapped_column(Text)
    customer_phone: Mapped[Optional[str]] = mapped_column(Text)
    customer_national_id: Mapped[Optional[str]] = mapped_column(String)
    customer_date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    customer_address: Mapped[Optional[str]] = mapped_column(Text)
    
    # Channel & Source
    channel: Mapped[Optional[str]] = mapped_column(String(50))
    lead_source: Mapped[Optional[str]] = mapped_column(String(100))
    source_of_quote: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Assignment & Management
    assigned_to_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    assigned_to_user_id_uuid: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    assigned_team_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date)
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Status & Workflow
    status: Mapped[str] = mapped_column(String(50), default="draft")
    priority_level: Mapped[Optional[str]] = mapped_column(String(50))
    auto_expire_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Locking
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    lock_reason: Mapped[Optional[str]] = mapped_column(Text)
    locked_by: Mapped[Optional[int]] = mapped_column(Integer)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Product & Policy Information
    policy_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    product_code: Mapped[Optional[str]] = mapped_column(String(50))
    profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    
    # Pricing Information
    base_premium: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    discount_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    surcharge_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    fees_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    tax_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    items_premium: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    total_premium: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    final_premium: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    
    # Currency & Exchange
    currency_code: Mapped[Optional[str]] = mapped_column(String(10))
    base_currency: Mapped[str] = mapped_column(String(3), default="USD")
    converted_premium: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    exchange_rate_used: Mapped[Optional[float]] = mapped_column(Numeric(12, 6))
    
    # Validity & Dates
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)
    quote_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Conversion & Relationships
    converted_policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    parent_quotation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    renewal_quotation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    quote_bundle_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    
    # Scoring & Analytics
    ai_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    risk_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    fraud_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    priority_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    
    # Summary & Content
    summary_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    summary_text: Mapped[Optional[str]] = mapped_column(Text)
    
    # Campaign & Marketing
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    referral_code: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Terms & Conditions
    terms_conditions: Mapped[Optional[str]] = mapped_column(Text)
    special_conditions: Mapped[Optional[str]] = mapped_column(Text)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # External Integration
    external_ref_id: Mapped[Optional[str]] = mapped_column(String(100))
    source_system: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Versioning
    version: Mapped[Optional[int]] = mapped_column(Integer)
    is_latest_version: Mapped[bool] = mapped_column(Boolean, default=True)
    version_notes: Mapped[Optional[str]] = mapped_column(Text)
    reference_number: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Additional Data
    group_size: Mapped[Optional[int]] = mapped_column(Integer)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    
    # 🚨 FIX: Map database 'metadata' column to 'quotation_metadata' attribute
    # This avoids SQLAlchemy's reserved 'metadata' attribute conflict
    quotation_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, default=lambda: {})
    
    # Arrays and JSON
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    benefit_presentation_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    coverage_comparison_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Audit fields (already handled by TimestampMixin, but database has different names)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    updated_by: Mapped[Optional[int]] = mapped_column(Integer)  # Note: int type in DB, not UUID
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<Quotation(id={self.id}, quote_number='{self.quote_number}', status='{self.status}')>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the quotation instance to a dictionary.
        Useful for serialization and API responses.
        """
        return {
            'id': str(self.id) if self.id else None,
            'quote_number': self.quote_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'status': self.status,
            'total_premium': float(self.total_premium) if self.total_premium else None,
            'currency_code': self.currency_code,
            'quotation_metadata': self.quotation_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # Add other fields as needed
        }

    def update_metadata(self, key: str, value: Any) -> None:
        """
        Helper method to update a specific key in the quotation metadata.
        """
        if self.quotation_metadata is None:
            self.quotation_metadata = {}
        self.quotation_metadata[key] = value

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """
        Helper method to get a specific value from quotation metadata.
        """
        if self.quotation_metadata is None:
            return default
        return self.quotation_metadata.get(key, default)

    def is_expired(self) -> bool:
        """
        Check if the quotation has expired.
        """
        if self.quote_expires_at is None:
            return False
        return datetime.now() > self.quote_expires_at

    def can_be_converted(self) -> bool:
        """
        Check if the quotation can be converted to a policy.
        """
        return (
            self.status == QuotationStatusEnum.APPROVED and
            not self.is_expired() and
            self.converted_policy_id is None
        )

    def calculate_total_premium(self) -> float:
        """
        Calculate total premium from components.
        """
        base = self.base_premium or 0
        discount = self.discount_amount or 0
        surcharge = self.surcharge_amount or 0
        fees = self.fees_amount or 0
        tax = self.tax_amount or 0
        items = self.items_premium or 0
        
        return base - discount + surcharge + fees + tax + items