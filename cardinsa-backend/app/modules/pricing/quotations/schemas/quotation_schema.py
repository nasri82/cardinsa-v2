# app/modules/pricing/quotations/schemas/enhanced_quotation_schemas.py

from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from enum import Enum


class QuotationStatus(str, Enum):
    """Enhanced quotation status"""
    DRAFT = "DRAFT"
    CALCULATING = "CALCULATING"
    CALCULATED = "CALCULATED"
    APPROVED = "APPROVED"
    CONVERTED = "CONVERTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


# ========== BASE SCHEMAS ==========

class QuotationBase(BaseModel):
    """Base quotation schema"""
    insurance_product_id: UUID
    customer_id: Optional[UUID] = None
    coverage_type: str = Field(..., description="Coverage type (INDIVIDUAL, FAMILY, GROUP)")
    coverage_amount: Decimal = Field(..., gt=0, description="Coverage amount")
    effective_date: date = Field(..., description="Policy effective date")
    currency_code: str = Field(default="USD", max_length=3, description="Currency code")
    quotation_data: Optional[Dict[str, Any]] = Field(default={}, description="Additional quotation data")
    notes: Optional[str] = Field(None, max_length=1000, description="Quotation notes")
    
    @validator('currency_code')
    def validate_currency_code(cls, v):
        if len(v) != 3 or not v.isupper():
            raise ValueError('Currency code must be 3 uppercase letters')
        return v


class QuotationCreate(QuotationBase):
    """Create quotation schema"""
    customer_email: Optional[str] = Field(None, description="Customer email if customer_id not provided")
    
    @validator('*', pre=True)
    def validate_customer_identification(cls, v, values):
        if 'customer_id' not in values and 'customer_email' not in values:
            raise ValueError('Either customer_id or customer_email must be provided')
        return v


class QuotationUpdate(BaseModel):
    """Update quotation schema"""
    coverage_type: Optional[str] = None
    coverage_amount: Optional[Decimal] = None
    effective_date: Optional[date] = None
    quotation_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    status: Optional[QuotationStatus] = None


# ========== CALCULATION INTEGRATION SCHEMAS ==========

class PremiumBreakdown(BaseModel):
    """Premium calculation breakdown"""
    base_premium: Decimal = Field(..., description="Base premium amount")
    demographic_adjustments: Decimal = Field(default=0, description="Age/demographic adjustments")
    risk_adjustments: Decimal = Field(default=0, description="Risk factor adjustments")
    component_adjustments: Decimal = Field(default=0, description="Deductible/copay adjustments")
    total_adjustments: Decimal = Field(default=0, description="Total adjustments")
    subtotal: Decimal = Field(..., description="Premium after adjustments")
    total_discounts: Decimal = Field(default=0, description="Total discount amount")
    tax_amount: Decimal = Field(default=0, description="Tax amount")
    commission_amount: Decimal = Field(default=0, description="Commission amount")
    total_premium: Decimal = Field(..., description="Final premium amount")
    
    @validator('total_premium')
    def calculate_total(cls, v, values):
        """Auto-calculate total if not provided"""
        if v is None or v == 0:
            return (
                values.get('subtotal', 0) -
                values.get('total_discounts', 0) +
                values.get('tax_amount', 0)
            )
        return v


class BenefitDetailsResponse(BaseModel):
    """Detailed benefit information for customer presentation"""
    benefit_id: UUID
    benefit_name: str
    benefit_description: str
    coverage_amount: Decimal
    base_premium: Decimal
    adjustments: List[Dict[str, Any]] = Field(default=[], description="Applied adjustments")
    final_premium: Decimal
    deductible: Optional[Decimal] = Field(default=0, description="Deductible amount")
    copay_percentage: Optional[Decimal] = Field(default=0, description="Copay percentage")
    coverage_limits: Dict[str, Any] = Field(default={}, description="Coverage limits")
    exclusions: List[str] = Field(default=[], description="Coverage exclusions")
    included_services: List[str] = Field(default=[], description="Included services")
    key_features: List[str] = Field(default=[], description="Key benefit features")
    
    class Config:
        from_attributes = True


class CoverageComparisonResponse(BaseModel):
    """Coverage option comparison for customer choice"""
    option_name: str = Field(..., description="Option name (BASIC, STANDARD, PREMIUM)")
    monthly_premium: Decimal = Field(..., description="Monthly premium")
    annual_premium: Decimal = Field(..., description="Annual premium")
    coverage_amount: Decimal = Field(..., description="Total coverage amount")
    deductible: Decimal = Field(..., description="Deductible amount")
    copay_percentage: Decimal = Field(..., description="Copay percentage")
    key_benefits: List[str] = Field(default=[], description="Key benefits included")
    limitations: List[str] = Field(default=[], description="Coverage limitations")
    recommended: bool = Field(default=False, description="Whether this option is recommended")
    
    class Config:
        from_attributes = True


class PricingFactorSummary(BaseModel):
    """Pricing factor summary for transparency"""
    demographic_factors: List[Dict[str, Any]] = Field(default=[], description="Age, gender, location factors")
    risk_factors: List[Dict[str, Any]] = Field(default=[], description="Health, lifestyle risk factors")
    discount_factors: List[Dict[str, Any]] = Field(default=[], description="Applied discounts")
    other_factors: List[Dict[str, Any]] = Field(default=[], description="Other pricing factors")


# ========== RESPONSE SCHEMAS ==========

class QuotationResponse(BaseModel):
    """Standard quotation response"""
    id: UUID
    quote_number: str
    insurance_product_id: UUID
    customer_id: UUID
    status: QuotationStatus
    coverage_type: str
    coverage_amount: Decimal
    effective_date: date
    valid_until: Optional[datetime]
    
    # Premium information
    base_premium: Optional[Decimal] = None
    total_premium: Optional[Decimal] = None
    total_adjustments: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    commission_amount: Optional[Decimal] = None
    
    # Metadata
    currency_code: str
    quotation_data: Optional[Dict[str, Any]] = None
    calculation_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    calculated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    
    # User tracking
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    
    class Config:
        from_attributes = True


class QuotationDetailResponse(BaseModel):
    """Comprehensive quotation response with calculation details"""
    quotation: QuotationResponse
    premium_breakdown: Dict[str, Any] = Field(default={}, description="Detailed premium breakdown")
    benefit_details: List[BenefitDetailsResponse] = Field(default=[], description="Benefit-level details")
    coverage_options: List[CoverageComparisonResponse] = Field(default=[], description="Coverage comparisons")
    pricing_factors: PricingFactorSummary = Field(default_factory=PricingFactorSummary, description="Pricing factors")
    recommendations: List[str] = Field(default=[], description="Personalized recommendations")
    
    class Config:
        from_attributes = True


class QuotationSummary(BaseModel):
    """Quotation summary for lists"""
    id: UUID
    quote_number: str
    status: QuotationStatus
    coverage_type: str
    total_premium: Optional[Decimal] = None
    effective_date: date
    valid_until: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== WORKFLOW SCHEMAS ==========

class QuotationApprovalRequest(BaseModel):
    """Quotation approval request"""
    approval_notes: Optional[str] = Field(None, max_length=500, description="Approval notes")


class QuotationPolicyConversion(BaseModel):
    """Policy conversion request"""
    policy_start_date: Optional[date] = Field(None, description="Policy start date")
    payment_method: Optional[str] = Field(None, description="Payment method")
    billing_frequency: Optional[str] = Field(default="MONTHLY", description="Billing frequency")
    additional_data: Optional[Dict[str, Any]] = Field(default={}, description="Additional policy data")


class QuotationRecalculationRequest(BaseModel):
    """Recalculation request"""
    force_recalculation: bool = Field(default=False, description="Force recalculation even if recent")
    update_data: Optional[Dict[str, Any]] = Field(default={}, description="Data to update before recalculation")


# ========== SEARCH AND FILTER SCHEMAS ==========

class QuotationFilters(BaseModel):
    """Quotation filtering options"""
    status: Optional[List[QuotationStatus]] = None
    coverage_type: Optional[List[str]] = None
    insurance_product_id: Optional[List[UUID]] = None
    customer_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    min_premium: Optional[Decimal] = None
    max_premium: Optional[Decimal] = None
    created_by: Optional[UUID] = None
    
    class Config:
        extra = "forbid"


class QuotationSearchRequest(BaseModel):
    """Quotation search request"""
    search_term: Optional[str] = Field(None, min_length=2, description="Search term")
    filters: Optional[QuotationFilters] = Field(default_factory=QuotationFilters)
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default="created_at", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", patterm="^(asc|desc)$", description="Sort order")


class QuotationSearchResponse(BaseModel):
    """Quotation search response"""
    quotations: List[QuotationSummary]
    total: int
    page: int
    per_page: int
    total_pages: int
    
    @validator('total_pages')
    def calculate_total_pages(cls, v, values):
        total = values.get('total', 0)
        per_page = values.get('per_page', 20)
        return (total + per_page - 1) // per_page if total > 0 else 0


# ========== ERROR SCHEMAS ==========

class QuotationError(BaseModel):
    """Quotation error response"""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default={}, description="Error details")
    quotation_id: Optional[UUID] = Field(None, description="Related quotation ID")


# ========== CUSTOMER-FACING SCHEMAS ==========

class CustomerQuoteRequest(BaseModel):
    """Customer quote request (simplified)"""
    insurance_product_id: UUID
    coverage_type: str = Field(..., description="INDIVIDUAL, FAMILY, or GROUP")
    coverage_amount: Decimal = Field(..., gt=0, description="Desired coverage amount")
    effective_date: date = Field(..., description="When coverage should start")
    customer_info: Optional[Dict[str, Any]] = Field(default={}, description="Customer information")
    
    @validator('effective_date')
    def validate_effective_date(cls, v):
        if v < date.today():
            raise ValueError('Effective date cannot be in the past')
        return v


class CustomerQuoteResponse(BaseModel):
    """Customer-facing quote response"""
    quote_number: str
    monthly_premium: Decimal
    annual_premium: Decimal
    coverage_amount: Decimal
    effective_date: date
    valid_until: datetime
    
    # Simplified benefit information
    key_benefits: List[str] = Field(default=[], description="Main benefits")
    coverage_highlights: List[str] = Field(default=[], description="Coverage highlights")
    
    # Options for customer
    coverage_options: List[CoverageComparisonResponse] = Field(default=[], description="Available options")
    next_steps: List[str] = Field(default=[], description="Next steps for customer")
    
    class Config:
        from_attributes = True


# ========== ANALYTICS SCHEMAS ==========

class QuotationMetrics(BaseModel):
    """Quotation performance metrics"""
    total_quotes: int = 0
    conversion_rate: float = 0.0
    average_premium: Decimal = Decimal('0.00')
    total_premium_volume: Decimal = Decimal('0.00')
    quotes_by_status: Dict[str, int] = Field(default_factory=dict)
    quotes_by_product: Dict[str, int] = Field(default_factory=dict)
    average_calculation_time: float = 0.0
    
    class Config:
        from_attributes = True


class QuotationTrend(BaseModel):
    """Quotation trend data"""
    date: date
    quote_count: int
    conversion_count: int
    average_premium: Decimal
    total_volume: Decimal
    
    class Config:
        from_attributes = True


# ========== VALIDATION HELPERS ==========

def validate_coverage_type(coverage_type: str) -> str:
    """Validate coverage type"""
    valid_types = ['INDIVIDUAL', 'FAMILY', 'GROUP']
    if coverage_type.upper() not in valid_types:
        raise ValueError(f'Coverage type must be one of: {", ".join(valid_types)}')
    return coverage_type.upper()


def validate_quotation_status_transition(current_status: QuotationStatus, 
                                       new_status: QuotationStatus) -> bool:
    """Validate status transition"""
    valid_transitions = {
        QuotationStatus.DRAFT: [QuotationStatus.CALCULATING, QuotationStatus.CANCELLED],
        QuotationStatus.CALCULATING: [QuotationStatus.CALCULATED, QuotationStatus.DRAFT, QuotationStatus.CANCELLED],
        QuotationStatus.CALCULATED: [QuotationStatus.APPROVED, QuotationStatus.CALCULATING, QuotationStatus.EXPIRED, QuotationStatus.CANCELLED],
        QuotationStatus.APPROVED: [QuotationStatus.CONVERTED, QuotationStatus.EXPIRED, QuotationStatus.CANCELLED],
        QuotationStatus.CONVERTED: [],  # Final status
        QuotationStatus.EXPIRED: [],    # Final status
        QuotationStatus.CANCELLED: []   # Final status
    }
    
    return new_status in valid_transitions.get(current_status, [])