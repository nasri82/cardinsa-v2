# app/modules/pricing/modifiers/schemas/pricing_copayment_schema.py

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# ==================== ENUMS ====================

class NetworkTier(str, Enum):
    TIER1 = "tier1"  # Preferred/In-Network
    TIER2 = "tier2"  # Standard Network
    TIER3 = "tier3"  # Extended Network
    OUT_OF_NETWORK = "out_of_network"

class ServiceCategory(str, Enum):
    PRIMARY_CARE = "primary_care"
    SPECIALIST = "specialist"
    EMERGENCY = "emergency"
    URGENT_CARE = "urgent_care"
    HOSPITAL = "hospital"
    SURGERY = "surgery"
    DIAGNOSTIC = "diagnostic"
    PREVENTIVE = "preventive"
    MENTAL_HEALTH = "mental_health"
    GENERIC_DRUG = "generic_drug"
    BRAND_DRUG = "brand_drug"
    SPECIALTY_DRUG = "specialty_drug"

class CopaymentType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    HYBRID = "hybrid"  # Fixed amount or percentage, whichever is less

# ==================== BASE SCHEMAS ====================

class PricingCopaymentBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Unique copayment code")
    label: str = Field(..., min_length=3, max_length=200, description="Display label")
    percentage: Decimal = Field(..., ge=0, le=100, description="Copayment percentage")
    fixed_amount: Optional[Decimal] = Field(None, ge=0, description="Fixed copayment amount")
    copayment_type: CopaymentType = Field(default=CopaymentType.PERCENTAGE)
    service_category: ServiceCategory = Field(default=ServiceCategory.PRIMARY_CARE)
    network_tier: NetworkTier = Field(default=NetworkTier.TIER2)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(True)
    
    # Enhanced fields
    max_copay_per_visit: Optional[Decimal] = Field(None, ge=0, description="Maximum copay per visit")
    max_annual_copay: Optional[Decimal] = Field(None, ge=0, description="Maximum annual copay")
    waive_after_deductible: Optional[bool] = Field(False, description="Waive copay after deductible met")
    visit_limit: Optional[int] = Field(None, ge=0, description="Number of visits before copay changes")
    reduced_copay_after_limit: Optional[Decimal] = Field(None, ge=0, le=100)
    apply_to_oop_max: Optional[bool] = Field(True, description="Count towards out-of-pocket maximum")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        """Validate code format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Code must be alphanumeric (with - or _ allowed)')
        return v.upper()
    
    @field_validator('percentage')
    @classmethod
    def validate_percentage(cls, v, info):
        """Validate percentage based on type"""
        copay_type = info.data.get('copayment_type')
        if copay_type == CopaymentType.FIXED and v > 0:
            raise ValueError('Percentage must be 0 for fixed copayment type')
        return v
    
    @model_validator(mode='after')
    def validate_copayment_logic(self):
        """Cross-field validation"""
        if self.copayment_type == CopaymentType.FIXED and not self.fixed_amount:
            raise ValueError('Fixed amount required for fixed copayment type')
        
        if self.copayment_type == CopaymentType.HYBRID and not (self.percentage and self.fixed_amount):
            raise ValueError('Both percentage and fixed amount required for hybrid type')
        
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

class PricingCopaymentCreate(PricingCopaymentBase):
    """Schema for creating a copayment"""
    created_by: Optional[UUID] = Field(None, description="User who created the record")

class PricingCopaymentUpdate(BaseModel):
    """Schema for updating a copayment"""
    label: Optional[str] = Field(None, min_length=3, max_length=200)
    percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    fixed_amount: Optional[Decimal] = Field(None, ge=0)
    copayment_type: Optional[CopaymentType] = None
    service_category: Optional[ServiceCategory] = None
    network_tier: Optional[NetworkTier] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    max_copay_per_visit: Optional[Decimal] = Field(None, ge=0)
    max_annual_copay: Optional[Decimal] = Field(None, ge=0)
    waive_after_deductible: Optional[bool] = None
    visit_limit: Optional[int] = Field(None, ge=0)
    reduced_copay_after_limit: Optional[Decimal] = Field(None, ge=0, le=100)
    apply_to_oop_max: Optional[bool] = None
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

class PricingCopayment(PricingCopaymentBase):
    """Complete copayment response schema"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    deleted_at: Optional[datetime] = None
    
    # Computed fields
    effective_rate: Optional[float] = Field(None, description="Effective copayment rate")
    tier_display_name: Optional[str] = Field(None, description="Network tier display name")
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_encoders={
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )
# ==================== TIERED CALCULATION SCHEMAS ====================

class TieredCopaymentRequest(BaseModel):
    """Request for tiered copayment calculation"""
    service_type: str = Field(..., description="Type of service")
    network_tier: NetworkTier
    service_cost: Decimal = Field(..., gt=0, description="Cost of service")
    visit_count: int = Field(0, ge=0, description="Number of visits this period")
    deductible_met: bool = Field(False, description="Whether deductible is met")
    ytd_oop: Decimal = Field(default=Decimal("0"), ge=0, description="Year-to-date out-of-pocket")
    member_id: Optional[UUID] = None

class TieredCopaymentResponse(BaseModel):
    """Response from tiered copayment calculation"""
    service_cost: float
    copayment_amount: float
    patient_pays: float
    insurance_pays: float
    copayment_percentage: float
    tier_applied: str
    visit_count: int
    visit_discount_applied: bool
    copayment_waived: bool
    oop_max_reached: bool
    copayment_id: UUID
    copayment_code: str
    calculation_details: Dict[str, Any]

# ==================== NETWORK COMPARISON SCHEMAS ====================

class NetworkComparisonRequest(BaseModel):
    """Request for network tier comparison"""
    service_type: str
    service_cost: Decimal = Field(..., gt=0)
    include_out_of_network: bool = Field(True)
    current_tier: Optional[NetworkTier] = None

class NetworkComparisonItem(BaseModel):
    """Single network tier comparison"""
    network_tier: str
    tier_name: str
    patient_pays: float
    insurance_pays: float
    savings_vs_oon: float
    copayment_percentage: float
    is_current: bool = False

class NetworkComparisonResponse(BaseModel):
    """Response with network tier comparisons"""
    comparisons: List[NetworkComparisonItem]
    best_value_tier: str
    potential_savings: float
    service_cost: float

# ==================== BULK OPERATIONS SCHEMAS ====================

class CopaymentBulkCreate(BaseModel):
    """Schema for bulk copayment creation"""
    copayments: List[PricingCopaymentCreate] = Field(..., min_items=1, max_items=100)
    validate_all: bool = Field(True)
    skip_duplicates: bool = Field(False)

class CopaymentBulkAdjust(BaseModel):
    """Schema for bulk percentage adjustment"""
    percentage_adjustment: Decimal = Field(..., ge=-50, le=50, description="Percentage change")
    service_category: Optional[ServiceCategory] = None
    network_tier: Optional[NetworkTier] = None
    updated_by: Optional[UUID] = None

# ==================== RECOMMENDATION SCHEMAS ====================

class CopaymentStructureRequest(BaseModel):
    """Request for copayment structure recommendation"""
    employee_count: int = Field(..., gt=0)
    industry: str = Field(..., min_length=2, max_length=100)
    budget_per_employee: Decimal = Field(..., gt=0)
    current_structure: Optional[Dict[str, float]] = None
    target_utilization: Optional[float] = Field(None, ge=0, le=100)

class CopaymentStructureRecommendation(BaseModel):
    """Recommended copayment structure"""
    tier1_percentage: float
    tier2_percentage: float
    tier3_percentage: float
    out_of_network_percentage: float
    estimated_annual_copayments: float
    company_profile_summary: Dict[str, str]
    recommendation_confidence: float
    reasoning: List[str]

# ==================== ANALYTICS SCHEMAS ====================

class CopaymentStatistics(BaseModel):
    """Copayment statistics"""
    total_configurations: int
    active_configurations: int
    average_percentage: float
    average_fixed_amount: float
    by_service_category: Dict[str, int]
    by_network_tier: Dict[str, int]
    most_common_type: str

class TierDistribution(BaseModel):
    """Network tier distribution"""
    tier: str
    count: int
    average_percentage: float
    average_fixed_amount: float
    utilization_rate: float

class CopaymentUtilization(BaseModel):
    """Copayment utilization metrics"""
    total_copayments_collected: float
    average_copayment_amount: float
    most_used_tier: str
    tier1_utilization_rate: float
    tier2_utilization_rate: float
    tier3_utilization_rate: float
    out_of_network_rate: float

class ServiceTypeAnalysis(BaseModel):
    """Analysis by service type"""
    service_type: str
    average_copayment: float
    utilization_count: int
    total_collected: float
    trend: str = Field(..., pattern="^(increasing|stable|decreasing)$")

class CopaymentAnalyticsResponse(BaseModel):
    """Comprehensive copayment analytics"""
    statistics: CopaymentStatistics
    tier_distribution: List[TierDistribution]
    utilization: CopaymentUtilization
    average_copayment_by_service: Dict[str, float]
    service_analysis: List[ServiceTypeAnalysis]
    report_period: Dict[str, Optional[str]]
    generated_at: datetime

# ==================== QUERY PARAMETER SCHEMAS ====================

class CopaymentQueryParams(BaseModel):
    """Query parameters for copayment listing"""
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    service_category: Optional[ServiceCategory] = None
    network_tier: Optional[NetworkTier] = None
    is_active: Optional[bool] = None
    copayment_type: Optional[CopaymentType] = None
    min_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    max_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    search: Optional[str] = Field(None, min_length=1, max_length=100)
    sort_by: Optional[str] = Field("created_at", pattern="^(code|percentage|network_tier|created_at)$")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")

# ==================== COMPANY PROFILE SCHEMAS ====================

class CompanyProfileRequest(BaseModel):
    """Company profile for recommendations"""
    employee_count: int = Field(..., gt=0)
    industry: str
    annual_revenue: Optional[Decimal] = Field(None, gt=0)
    average_age: Optional[float] = Field(None, ge=18, le=80)
    risk_tolerance: str = Field("medium", pattern="^(low|medium|high)$")
    current_copayment_spend: Optional[Decimal] = None
    target_reduction: Optional[float] = Field(None, ge=0, le=50)

class CompanyCopaymentProfile(BaseModel):
    """Company copayment profile analysis"""
    recommended_structure: CopaymentStructureRecommendation
    projected_savings: float
    implementation_timeline: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    benchmarks: Dict[str, float]

# ==================== VALIDATION HELPERS ====================

def validate_network_tier_hierarchy(tier: NetworkTier) -> int:
    """Get tier hierarchy level for comparison"""
    hierarchy = {
        NetworkTier.TIER1: 1,
        NetworkTier.TIER2: 2,
        NetworkTier.TIER3: 3,
        NetworkTier.OUT_OF_NETWORK: 4
    }
    return hierarchy.get(tier, 999)

def calculate_effective_copayment(
    percentage: Decimal,
    fixed_amount: Optional[Decimal],
    service_cost: Decimal,
    copayment_type: CopaymentType
) -> Decimal:
    """Calculate effective copayment amount"""
    if copayment_type == CopaymentType.FIXED:
        return fixed_amount or Decimal("0")
    elif copayment_type == CopaymentType.PERCENTAGE:
        return service_cost * (percentage / 100)
    elif copayment_type == CopaymentType.HYBRID:
        percentage_amount = service_cost * (percentage / 100)
        return min(percentage_amount, fixed_amount or percentage_amount)
    return Decimal("0")