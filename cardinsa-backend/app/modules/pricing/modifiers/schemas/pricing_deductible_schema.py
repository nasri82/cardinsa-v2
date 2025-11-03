# app/modules/pricing/modifiers/schemas/pricing_deductible_schema.py

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# ==================== ENUMS ====================

class ServiceType(str, Enum):
    MEDICAL = "medical"
    DENTAL = "dental"
    VISION = "vision"
    PHARMACY = "pharmacy"
    EMERGENCY = "emergency"
    SPECIALIST = "specialist"
    GENERAL = "general"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    AED = "AED"
    SAR = "SAR"
    KWD = "KWD"
    QAR = "QAR"
    OMR = "OMR"

# ==================== BASE SCHEMAS ====================

class PricingDeductibleBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Unique deductible code")
    label: str = Field(..., min_length=3, max_length=200, description="Display label")
    amount: Decimal = Field(..., ge=0, le=100000, description="Deductible amount")
    service_type: ServiceType = Field(default=ServiceType.GENERAL, description="Service type")
    currency: Currency = Field(default=Currency.USD, description="Currency code")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description")
    is_active: Optional[bool] = Field(True, description="Active status")
    
    # New fields for enhanced functionality
    min_claim_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum claim amount to apply")
    max_annual_amount: Optional[Decimal] = Field(None, ge=0, description="Maximum annual deductible")
    carry_forward: Optional[bool] = Field(False, description="Allow carry forward to next period")
    family_aggregate: Optional[bool] = Field(False, description="Apply as family aggregate")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        """Validate code format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Code must be alphanumeric (with - or _ allowed)')
        return v.upper()
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v, info):
        """Validate amount based on service type"""
        service_type = info.data.get('service_type')
        if service_type:
            max_amounts = {
                ServiceType.MEDICAL: Decimal("10000"),
                ServiceType.DENTAL: Decimal("5000"),
                ServiceType.VISION: Decimal("1000"),
                ServiceType.PHARMACY: Decimal("3000"),
                ServiceType.EMERGENCY: Decimal("5000"),
                ServiceType.SPECIALIST: Decimal("2000"),
                ServiceType.GENERAL: Decimal("10000")
            }
            max_amount = max_amounts.get(service_type, Decimal("10000"))
            if v > max_amount:
                raise ValueError(f'Amount exceeds maximum for {service_type}: {max_amount}')
        return v
    
    @model_validator(mode='after')
    def validate_amounts(self):
        """Cross-field validation"""
        if self.min_claim_amount and self.amount and self.min_claim_amount > self.amount:
            raise ValueError('Minimum claim amount cannot exceed deductible amount')
        return self

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )

# ==================== CREATE/UPDATE SCHEMAS ====================

class PricingDeductibleCreate(PricingDeductibleBase):
    """Schema for creating a deductible"""
    created_by: Optional[UUID] = Field(None, description="User who created the record")

class PricingDeductibleUpdate(BaseModel):
    """Schema for updating a deductible"""
    label: Optional[str] = Field(None, min_length=3, max_length=200)
    amount: Optional[Decimal] = Field(None, ge=0, le=100000)
    service_type: Optional[ServiceType] = None
    currency: Optional[Currency] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    min_claim_amount: Optional[Decimal] = Field(None, ge=0)
    max_annual_amount: Optional[Decimal] = Field(None, ge=0)
    carry_forward: Optional[bool] = None
    family_aggregate: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_by: Optional[UUID] = Field(None, description="User who updated the record")
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )

# ==================== RESPONSE SCHEMAS ====================

class PricingDeductible(PricingDeductibleBase):
    """Complete deductible response schema"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    deleted_at: Optional[datetime] = None
    
    # Computed fields
    annual_limit_reached: Optional[bool] = Field(None, description="Whether annual limit is reached")
    effective_amount: Optional[Decimal] = Field(None, description="Effective deductible amount")
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_encoders={
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )

class PricingDeductibleSummary(BaseModel):
    """Summary schema for list views"""
    id: UUID
    code: str
    label: str
    amount: float
    service_type: str
    currency: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

# ==================== BULK OPERATION SCHEMAS ====================

class DeductibleBulkCreate(BaseModel):
    """Schema for bulk deductible creation"""
    deductibles: List[PricingDeductibleCreate] = Field(..., min_items=1, max_items=100)
    validate_all: bool = Field(True, description="Validate all before creating any")
    skip_duplicates: bool = Field(False, description="Skip duplicates instead of failing")

class DeductibleBulkUpdate(BaseModel):
    """Schema for bulk deductible updates"""
    updates: Dict[str, Decimal] = Field(..., description="Map of code to new amount")
    updated_by: Optional[UUID] = None

class DeductibleBulkResult(BaseModel):
    """Result of bulk operations"""
    total_processed: int
    total_created: int = 0
    total_updated: int = 0
    total_failed: int = 0
    created: List[Dict[str, str]] = Field(default_factory=list)
    updated: List[Dict[str, str]] = Field(default_factory=list)
    failed: List[Dict[str, str]] = Field(default_factory=list)

# ==================== CALCULATION SCHEMAS ====================

class DeductibleCalculationRequest(BaseModel):
    """Request for deductible calculation"""
    deductible_id: UUID
    claim_amount: Decimal = Field(..., gt=0, description="Claim amount")
    ytd_claims: Decimal = Field(default=Decimal("0"), ge=0, description="Year-to-date claims")
    service_date: Optional[date] = Field(None, description="Date of service")
    member_id: Optional[UUID] = Field(None, description="Member ID for tracking")

class DeductibleCalculationResponse(BaseModel):
    """Response from deductible calculation"""
    claim_amount: float
    deductible_amount: float
    ytd_claims: float
    remaining_deductible: float
    deductible_applied: float
    covered_amount: float
    coverage_percentage: float
    deductible_met: bool
    service_type: str
    calculation_date: datetime = Field(default_factory=datetime.utcnow)

# ==================== RECOMMENDATION SCHEMAS ====================

class DeductibleRecommendationRequest(BaseModel):
    """Request for deductible recommendations"""
    service_type: ServiceType
    risk_profile: str = Field(..., pattern="^(low|medium|high)$", description="Risk profile")
    budget_min: Decimal = Field(..., ge=0, description="Minimum budget")
    budget_max: Decimal = Field(..., gt=0, description="Maximum budget")
    employee_count: Optional[int] = Field(None, gt=0, description="Number of employees")
    industry_code: Optional[str] = Field(None, description="NAICS industry code")
    
    @model_validator(mode='after')
    def validate_budget(self):
        if self.budget_min and self.budget_max and self.budget_min >= self.budget_max:
            raise ValueError('budget_max must be greater than budget_min')
        return self

class DeductibleRecommendation(BaseModel):
    """Deductible recommendation"""
    deductible_id: UUID
    code: str
    amount: float
    service_type: str
    recommendation_score: float = Field(..., ge=0, le=100)
    risk_alignment: str
    monthly_saving_estimate: float
    reasoning: Optional[str] = None

class DeductibleRecommendationResponse(BaseModel):
    """Response with deductible recommendations"""
    recommendations: List[DeductibleRecommendation]
    request_summary: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# ==================== ANALYTICS SCHEMAS ====================

class DeductibleStatistics(BaseModel):
    """Deductible statistics"""
    total_deductibles: int
    active_deductibles: int
    average_amount: float
    median_amount: float
    min_amount: float
    max_amount: float
    by_service_type: Dict[str, int]
    by_currency: Dict[str, int]

class DeductibleDistribution(BaseModel):
    """Deductible distribution analysis"""
    service_type: str
    count: int
    percentage: float
    average_amount: float
    total_exposure: float

class DeductibleUtilization(BaseModel):
    """Deductible utilization metrics"""
    total_policies_with_deductible: int
    average_deductible_selected: float
    most_popular_deductible: Optional[str]
    deductible_met_rate: float
    average_time_to_meet: Optional[int] = Field(None, description="Days to meet deductible")

class DeductibleAnalyticsResponse(BaseModel):
    """Comprehensive deductible analytics"""
    statistics: DeductibleStatistics
    distribution: List[DeductibleDistribution]
    utilization: DeductibleUtilization
    report_period: Dict[str, Optional[str]]
    generated_at: datetime

# ==================== QUERY PARAMETER SCHEMAS ====================

class DeductibleQueryParams(BaseModel):
    """Query parameters for deductible listing"""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return")
    service_type: Optional[ServiceType] = None
    is_active: Optional[bool] = None
    min_amount: Optional[Decimal] = Field(None, ge=0)
    max_amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[Currency] = None
    search: Optional[str] = Field(None, min_length=1, max_length=100)
    sort_by: Optional[str] = Field("created_at", pattern="^(code|amount|created_at|updated_at)$")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")

# ==================== IMPORT/EXPORT SCHEMAS ====================

class DeductibleImportRequest(BaseModel):
    """Request for importing deductibles"""
    file_format: str = Field(..., pattern="^(csv|json|excel)$")
    data: Optional[str] = Field(None, description="Base64 encoded file data")
    file_url: Optional[str] = Field(None, description="URL to file")
    mapping: Optional[Dict[str, str]] = Field(None, description="Column mapping")
    validate_only: bool = Field(False, description="Only validate without importing")

class DeductibleImportResult(BaseModel):
    """Result of deductible import"""
    total_rows: int
    imported: int
    failed: int
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]

class DeductibleExportRequest(BaseModel):
    """Request for exporting deductibles"""
    format: str = Field("csv", pattern="^(csv|json|excel|pdf)$")
    filters: Optional[DeductibleQueryParams] = None
    include_inactive: bool = Field(False)
    include_metadata: bool = Field(False)

# ==================== AUDIT SCHEMAS ====================

class DeductibleAuditLog(BaseModel):
    """Audit log entry for deductibles"""
    id: UUID
    deductible_id: UUID
    action: str = Field(..., pattern="^(create|update|delete|activate|deactivate)$")
    changes: Dict[str, Dict[str, Any]]
    performed_by: UUID
    performed_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class DeductibleChangeHistory(BaseModel):
    """Change history for a deductible"""
    deductible_id: UUID
    history: List[DeductibleAuditLog]
    total_changes: int

# ==================== VALIDATION HELPERS ====================

def validate_deductible_amount_range(
    amount: Decimal,
    service_type: ServiceType
) -> bool:
    """Validate deductible amount is within acceptable range"""
    ranges = {
        ServiceType.MEDICAL: (Decimal("0"), Decimal("10000")),
        ServiceType.DENTAL: (Decimal("0"), Decimal("5000")),
        ServiceType.VISION: (Decimal("0"), Decimal("1000")),
        ServiceType.PHARMACY: (Decimal("0"), Decimal("3000")),
        ServiceType.EMERGENCY: (Decimal("0"), Decimal("5000")),
        ServiceType.SPECIALIST: (Decimal("0"), Decimal("2000")),
        ServiceType.GENERAL: (Decimal("0"), Decimal("10000"))
    }
    
    min_amount, max_amount = ranges.get(service_type, (Decimal("0"), Decimal("10000")))
    return min_amount <= amount <= max_amount