# app/modules/pricing/quotations/schemas/quotation_schema.py

from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum
from decimal import Decimal

class QuotationStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"

class QuotationBase(BaseModel):
    """Base schema for quotation with common fields"""
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True
    )
    
    # Basic Information
    quote_number: Optional[str] = Field(None, max_length=50, description="Quotation number")
    customer_name: Optional[str] = Field(None, description="Customer full name")
    customer_email: Optional[str] = Field(None, description="Customer email address")
    customer_phone: Optional[str] = Field(None, description="Customer phone number")
    customer_national_id: Optional[str] = Field(None, description="Customer national ID")
    customer_date_of_birth: Optional[date] = Field(None, description="Customer date of birth")
    customer_address: Optional[str] = Field(None, description="Customer address")
    
    # Channel & Source
    channel: Optional[str] = Field(None, max_length=50, description="Sales channel")
    lead_source: Optional[str] = Field(None, max_length=100, description="Lead source")
    source_of_quote: Optional[str] = Field(None, max_length=50, description="Quote source")
    
    # Assignment & Management
    assigned_to_user_id: Optional[UUID] = Field(None, description="Assigned user ID")
    assigned_team_id: Optional[UUID] = Field(None, description="Assigned team ID")
    follow_up_date: Optional[date] = Field(None, description="Follow-up date")
    last_contacted_at: Optional[datetime] = Field(None, description="Last contact timestamp")
    
    # Status & Workflow
    status: QuotationStatusEnum = Field(QuotationStatusEnum.DRAFT, description="Quotation status")
    priority_level: Optional[str] = Field(None, max_length=50, description="Priority level")
    auto_expire_at: Optional[datetime] = Field(None, description="Auto expiration timestamp")
    
    # Locking
    is_locked: bool = Field(False, description="Is quotation locked")
    lock_reason: Optional[str] = Field(None, description="Lock reason")
    locked_by: Optional[int] = Field(None, description="Locked by user ID")
    locked_at: Optional[datetime] = Field(None, description="Lock timestamp")
    
    # Product & Policy Information
    policy_type_id: Optional[UUID] = Field(None, description="Policy type ID")
    plan_id: Optional[UUID] = Field(None, description="Plan ID")
    product_code: Optional[str] = Field(None, max_length=50, description="Product code")
    profile_id: Optional[UUID] = Field(None, description="Profile ID")
    
    # Pricing Information
    base_premium: Optional[Decimal] = Field(None, ge=0, description="Base premium amount")
    discount_amount: Optional[Decimal] = Field(None, ge=0, description="Discount amount")
    surcharge_amount: Optional[Decimal] = Field(None, ge=0, description="Surcharge amount")
    fees_amount: Optional[Decimal] = Field(None, ge=0, description="Fees amount")
    tax_amount: Optional[Decimal] = Field(None, ge=0, description="Tax amount")
    items_premium: Optional[Decimal] = Field(None, ge=0, description="Items premium")
    total_premium: Optional[Decimal] = Field(None, ge=0, description="Total premium")
    final_premium: Optional[Decimal] = Field(None, ge=0, description="Final premium")
    
    # Currency & Exchange
    currency_code: Optional[str] = Field(None, max_length=10, description="Currency code")
    base_currency: str = Field("USD", max_length=3, description="Base currency")
    converted_premium: Optional[Decimal] = Field(None, ge=0, description="Converted premium")
    exchange_rate_used: Optional[Decimal] = Field(None, gt=0, description="Exchange rate")
    
    # Validity & Dates
    valid_from: Optional[date] = Field(None, description="Valid from date")
    valid_to: Optional[date] = Field(None, description="Valid to date")
    quote_expires_at: Optional[datetime] = Field(None, description="Quote expiration timestamp")
    submitted_at: Optional[datetime] = Field(None, description="Submission timestamp")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    converted_at: Optional[datetime] = Field(None, description="Conversion timestamp")
    
    # Relationships
    converted_policy_id: Optional[UUID] = Field(None, description="Converted policy ID")
    parent_quotation_id: Optional[UUID] = Field(None, description="Parent quotation ID")
    renewal_quotation_id: Optional[UUID] = Field(None, description="Renewal quotation ID")
    quote_bundle_id: Optional[UUID] = Field(None, description="Quote bundle ID")
    
    # Scoring & Analytics
    ai_score: Optional[Decimal] = Field(None, ge=0, le=100, description="AI score")
    risk_score: Optional[Decimal] = Field(None, ge=0, le=100, description="Risk score")
    fraud_score: Optional[Decimal] = Field(None, ge=0, le=100, description="Fraud score")
    priority_score: Optional[Decimal] = Field(None, ge=0, le=100, description="Priority score")
    
    # Summary & Content
    summary_generated: bool = Field(False, description="Is summary generated")
    summary_text: Optional[str] = Field(None, description="Summary text")
    
    # Campaign & Marketing
    campaign_id: Optional[UUID] = Field(None, description="Campaign ID")
    referral_code: Optional[str] = Field(None, max_length=50, description="Referral code")
    
    # Terms & Conditions
    terms_conditions: Optional[str] = Field(None, description="Terms and conditions")
    special_conditions: Optional[str] = Field(None, description="Special conditions")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason")
    cancellation_reason: Optional[str] = Field(None, description="Cancellation reason")
    
    # External Integration
    external_ref_id: Optional[str] = Field(None, max_length=100, description="External reference ID")
    source_system: Optional[str] = Field(None, max_length=100, description="Source system")
    
    # Versioning
    version: Optional[int] = Field(None, ge=1, description="Version number")
    is_latest_version: bool = Field(True, description="Is latest version")
    version_notes: Optional[str] = Field(None, description="Version notes")
    reference_number: Optional[str] = Field(None, max_length=50, description="Reference number")
    
    # Additional Data
    group_size: Optional[int] = Field(None, ge=1, description="Group size")
    customer_id: Optional[UUID] = Field(None, description="Customer ID")
    
    # Metadata (mapped to quotation_metadata in the model)
    quotation_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Quotation metadata")
    
    # Arrays and JSON
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags")
    benefit_presentation_data: Optional[Dict[str, Any]] = Field(None, description="Benefit presentation data")
    coverage_comparison_data: Optional[Dict[str, Any]] = Field(None, description="Coverage comparison data")
    
    # Email validation
    @field_validator('customer_email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('Invalid email format')
        return v.lower()
    
    # Phone validation
    @field_validator('customer_phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Remove spaces and common separators
        cleaned = ''.join(c for c in v if c.isdigit() or c in '+()-')
        if len(cleaned) < 7 or len(cleaned) > 20:
            raise ValueError('Phone number must be between 7 and 20 characters')
        return cleaned
    
    # Currency code validation
    @field_validator('currency_code', 'base_currency')
    @classmethod
    def validate_currency_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) != 3 or not v.isalpha():
            raise ValueError('Currency code must be 3 alphabetic characters')
        return v.upper()
    
    # Date validation
    @model_validator(mode='after')
    def validate_dates(self) -> 'QuotationBase':
        """Validate date relationships"""
        
        # Validate valid_from and valid_to
        if self.valid_from and self.valid_to:
            if self.valid_from >= self.valid_to:
                raise ValueError('valid_from must be before valid_to')
        
        # Validate quote expiration
        if self.quote_expires_at and self.valid_to:
            if self.quote_expires_at.date() > self.valid_to:
                raise ValueError('quote_expires_at cannot be after valid_to')
        
        # Validate customer age
        if self.customer_date_of_birth:
            today = date.today()
            age = today.year - self.customer_date_of_birth.year
            if age < 0 or age > 150:
                raise ValueError('Invalid customer date of birth')
        
        # Validate workflow dates
        if self.submitted_at and self.approved_at:
            if self.submitted_at > self.approved_at:
                raise ValueError('submitted_at cannot be after approved_at')
        
        if self.approved_at and self.converted_at:
            if self.approved_at > self.converted_at:
                raise ValueError('approved_at cannot be after converted_at')
        
        return self

class QuotationCreate(QuotationBase):
    """Schema for creating a quotation"""
    
    # Required fields for creation
    customer_name: str = Field(..., min_length=1, description="Customer name is required")
    customer_email: str = Field(..., description="Customer email is required")

class QuotationUpdate(BaseModel):
    """Schema for updating a quotation"""
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    # All fields are optional for updates
    quote_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    status: Optional[QuotationStatusEnum] = None
    priority_level: Optional[str] = None
    base_premium: Optional[Decimal] = None
    total_premium: Optional[Decimal] = None
    quotation_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class QuotationResponse(QuotationBase):
    """Schema for quotation responses"""
    
    id: UUID = Field(..., description="Quotation ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="Created by user ID")
    updated_by: Optional[int] = Field(None, description="Updated by user ID")
    archived_at: Optional[datetime] = Field(None, description="Archive timestamp")

class QuotationSummary(BaseModel):
    """Lightweight schema for quotation lists"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    quote_number: Optional[str]
    customer_name: Optional[str]
    customer_email: Optional[str]
    status: QuotationStatusEnum
    total_premium: Optional[Decimal]
    currency_code: Optional[str]
    created_at: datetime
    updated_at: datetime

class QuotationStatusUpdate(BaseModel):
    """Schema for status updates"""
    
    status: QuotationStatusEnum = Field(..., description="New status")
    notes: Optional[str] = Field(None, description="Status change notes")

class QuotationCalculationRequest(BaseModel):
    """Schema for quotation calculation requests"""
    
    model_config = ConfigDict(validate_assignment=True)
    
    plan_id: Optional[UUID] = Field(None, description="Plan ID")
    customer_age: Optional[int] = Field(None, ge=0, le=150, description="Customer age")
    group_size: Optional[int] = Field(1, ge=1, description="Group size")
    coverage_options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Coverage options")
    risk_factors: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Risk factors")

class QuotationCalculationResponse(BaseModel):
    """Schema for quotation calculation responses"""
    
    model_config = ConfigDict(from_attributes=True)
    
    base_premium: Decimal = Field(..., description="Base premium")
    discount_amount: Optional[Decimal] = Field(None, description="Discount amount")
    surcharge_amount: Optional[Decimal] = Field(None, description="Surcharge amount")
    fees_amount: Optional[Decimal] = Field(None, description="Fees amount")
    tax_amount: Optional[Decimal] = Field(None, description="Tax amount")
    total_premium: Decimal = Field(..., description="Total premium")
    currency_code: str = Field(..., description="Currency code")
    calculation_details: Optional[Dict[str, Any]] = Field(None, description="Calculation breakdown")