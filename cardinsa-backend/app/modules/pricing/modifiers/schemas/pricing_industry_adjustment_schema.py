# app/modules/pricing/modifiers/schemas/pricing_industry_adjustment_schema.py

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union, Tuple
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# ==================== ENUMS ====================

class RiskLevel(str, Enum):
    LOW = "LOW"
    STANDARD = "STANDARD"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

class IndustryCategory(str, Enum):
    AGRICULTURE = "agriculture"
    MINING = "mining"
    UTILITIES = "utilities"
    CONSTRUCTION = "construction"
    MANUFACTURING = "manufacturing"
    WHOLESALE = "wholesale"
    RETAIL = "retail"
    TRANSPORTATION = "transportation"
    INFORMATION = "information"
    FINANCE = "finance"
    REAL_ESTATE = "real_estate"
    PROFESSIONAL = "professional"
    MANAGEMENT = "management"
    ADMINISTRATIVE = "administrative"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    HOSPITALITY = "hospitality"
    OTHER_SERVICES = "other_services"
    PUBLIC_ADMIN = "public_admin"

class TrendDirection(str, Enum):
    INCREASING = "increasing"
    STABLE = "stable"
    DECREASING = "decreasing"
    VOLATILE = "volatile"

# ==================== BASE SCHEMAS ====================

class PricingIndustryAdjustmentBase(BaseModel):
    industry_code: str = Field(..., min_length=2, max_length=6, description="NAICS industry code")
    adjustment_factor: Decimal = Field(..., ge=0.5, le=3.0, description="Risk adjustment factor")
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(True)
    
    # Enhanced fields
    industry_category: Optional[IndustryCategory] = None
    parent_code: Optional[str] = Field(None, min_length=2, max_length=4, description="Parent NAICS code")
    risk_level: Optional[RiskLevel] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    review_frequency: Optional[int] = Field(None, ge=1, le=365, description="Days between reviews")
    last_review_date: Optional[date] = None
    hazard_categories: Optional[List[str]] = Field(default_factory=list)
    safety_requirements: Optional[List[str]] = Field(default_factory=list)
    regulatory_requirements: Optional[List[str]] = Field(default_factory=list)
    typical_claims: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('industry_code')
    @classmethod
    def validate_naics_code(cls, v):
        """Validate NAICS code format"""
        if not v.replace('-', '').isdigit():
            # Allow codes like "31-33" for manufacturing
            parts = v.split('-')
            if len(parts) == 2 and all(p.isdigit() for p in parts):
                return v
            raise ValueError('Industry code must be numeric or range (e.g., 31-33)')
        if not (2 <= len(v) <= 6):
            raise ValueError('NAICS code must be 2-6 digits')
        return v
    
    @field_validator('adjustment_factor')
    @classmethod
    def validate_factor_range(cls, v):
        """Validate adjustment factor is reasonable"""
        if v < Decimal("0.5"):
            raise ValueError('Adjustment factor below 0.5 requires special approval')
        if v > Decimal("3.0"):
            raise ValueError('Adjustment factor above 3.0 requires special approval')
        return v
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Cross-field validation"""
        if self.effective_date and self.expiry_date and self.effective_date >= self.expiry_date:
            raise ValueError('Expiry date must be after effective date')
        
        # Auto-set risk level based on factor if not provided
        if not self.risk_level and self.adjustment_factor:
            self.risk_level = self._determine_risk_level(self.adjustment_factor)
        
        return self
    
    @staticmethod
    def _determine_risk_level(factor: Decimal) -> RiskLevel:
        """Determine risk level from adjustment factor"""
        if factor <= Decimal("0.8"):
            return RiskLevel.LOW
        elif factor <= Decimal("1.0"):
            return RiskLevel.STANDARD
        elif factor <= Decimal("1.5"):
            return RiskLevel.MODERATE
        elif factor <= Decimal("2.0"):
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )

# ==================== CREATE/UPDATE SCHEMAS ====================

class PricingIndustryAdjustmentCreate(PricingIndustryAdjustmentBase):
    """Schema for creating an industry adjustment"""
    created_by: Optional[UUID] = Field(None, description="User who created the record")
    auto_monitor: Optional[bool] = Field(False, description="Enable automatic monitoring for high-risk")

class PricingIndustryAdjustmentUpdate(BaseModel):
    """Schema for updating an industry adjustment"""
    adjustment_factor: Optional[Decimal] = Field(None, ge=0.5, le=3.0)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    industry_category: Optional[IndustryCategory] = None
    risk_level: Optional[RiskLevel] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    review_frequency: Optional[int] = Field(None, ge=1, le=365)
    hazard_categories: Optional[List[str]] = None
    safety_requirements: Optional[List[str]] = None
    regulatory_requirements: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_by: Optional[UUID] = Field(None, description="User who updated the record")
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )

# ==================== RESPONSE SCHEMAS ====================

class PricingIndustryAdjustment(PricingIndustryAdjustmentBase):
    """Complete industry adjustment response schema"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    deleted_at: Optional[datetime] = None
    
    # Computed fields
    premium_impact: Optional[str] = Field(None, description="Premium impact percentage")
    review_due: Optional[bool] = Field(None, description="Review is due")
    child_codes: Optional[List[str]] = Field(None, description="Child NAICS codes")
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_encoders={
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )
# ==================== RISK CALCULATION SCHEMAS ====================

class IndustryRiskRequest(BaseModel):
    """Request for industry risk calculation"""
    industry_code: str = Field(..., min_length=2, max_length=6)
    base_premium: Decimal = Field(..., gt=0)
    employee_count: Optional[int] = Field(None, ge=1)
    annual_revenue: Optional[Decimal] = Field(None, gt=0)
    years_in_business: Optional[int] = Field(None, ge=0)
    safety_certifications: Optional[List[str]] = Field(default_factory=list)
    claims_history: Optional[Dict[str, Any]] = None

class IndustryRiskResponse(BaseModel):
    """Response from industry risk calculation"""
    base_premium: float
    adjusted_premium: float
    adjustment_factor: float
    risk_level: RiskLevel
    industry_code: str
    industry_description: Optional[str]
    employee_count_modifier: bool
    experience_modifier: Optional[float]
    safety_discount: Optional[float]
    adjustment_applied: bool
    adjustment_id: Optional[UUID]
    calculation_breakdown: Dict[str, Any]

# ==================== MULTI-LOCATION RISK SCHEMAS ====================

class BusinessLocation(BaseModel):
    """Business location for risk calculation"""
    name: str
    industry_code: str
    exposure: Decimal = Field(..., gt=0, description="Financial exposure")
    employees: Optional[int] = Field(None, ge=0)
    address: Optional[Dict[str, str]] = None

class LocationRisk(BaseModel):
    """Risk assessment for a location"""
    location: str
    industry_code: str
    exposure: float
    adjusted_exposure: float
    risk_level: RiskLevel
    adjustment_factor: float

class MultiLocationRiskRequest(BaseModel):
    """Request for multi-location risk calculation"""
    locations: List[BusinessLocation] = Field(..., min_items=1, max_items=100)
    consolidate: bool = Field(True, description="Consolidate into single risk profile")

class MultiLocationRiskResponse(BaseModel):
    """Response from multi-location risk calculation"""
    total_base_exposure: float
    total_adjusted_exposure: float
    average_adjustment_factor: float
    overall_risk_level: RiskLevel
    location_count: int
    location_details: List[LocationRisk]
    consolidation_discount: Optional[float] = None
    recommendations: List[str]

# ==================== COMPREHENSIVE RISK ASSESSMENT ====================

class CompanyProfile(BaseModel):
    """Company profile for comprehensive risk assessment"""
    primary_naics: str
    secondary_naics: Optional[List[str]] = Field(default_factory=list)
    employee_count: int = Field(..., ge=1)
    annual_revenue: Decimal = Field(..., gt=0)
    locations: Optional[List[BusinessLocation]] = Field(default_factory=list)
    years_in_business: int = Field(..., ge=0)
    safety_record: Optional[Dict[str, Any]] = None
    certifications: Optional[List[str]] = Field(default_factory=list)

class RiskModifiers(BaseModel):
    """Risk modifiers breakdown"""
    experience_modifier: float
    size_modifier: float
    safety_modifier: float
    location_modifier: Optional[float]
    total_modifier: float

class ComprehensiveRiskResponse(BaseModel):
    """Comprehensive risk assessment response"""
    company_profile_summary: Dict[str, Any]
    primary_industry_risk: IndustryRiskResponse
    secondary_industry_risks: List[IndustryRiskResponse]
    location_risk: Optional[MultiLocationRiskResponse]
    modifiers: RiskModifiers
    final_risk_assessment: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float

# ==================== NAICS IMPORT/EXPORT SCHEMAS ====================

class NAICSImportRequest(BaseModel):
    """Request for importing NAICS codes"""
    file_path: Optional[str] = None
    file_data: Optional[str] = Field(None, description="Base64 encoded file")
    format: str = Field("csv", pattern="^(csv|json|excel)$")
    update_existing: bool = Field(True)
    validate_only: bool = Field(False)

class NAICSMapping(BaseModel):
    """NAICS code mapping"""
    industry_code: str
    adjustment_factor: Decimal
    description: str
    risk_level: Optional[RiskLevel] = None

class NAICSImportResponse(BaseModel):
    """Response from NAICS import"""
    created: int
    updated: int
    errors: List[Dict[str, str]]
    total_processed: int
    import_timestamp: datetime

# ==================== ANALYTICS SCHEMAS ====================

class RiskDistribution(BaseModel):
    """Risk level distribution"""
    distribution: Dict[str, int]
    percentages: Dict[str, float]
    total_industries: int
    average_factor: float

class HighRiskIndustry(BaseModel):
    """High risk industry detail"""
    industry_code: str
    adjustment_factor: float
    risk_level: RiskLevel
    description: Optional[str]
    premium_increase: str
    typical_claims: List[str]

class IndustryTrend(BaseModel):
    """Industry risk trend"""
    date: str
    adjustment_factor: float
    risk_level: RiskLevel
    events: Optional[List[str]] = None

class SectorAnalysis(BaseModel):
    """Risk analysis by sector"""
    sector: str
    average_factor: float
    risk_level: RiskLevel
    industry_count: int
    trends: TrendDirection

class IndustryAnalyticsResponse(BaseModel):
    """Comprehensive industry analytics"""
    risk_distribution: RiskDistribution
    high_risk_industries: List[HighRiskIndustry]
    total_industries: int
    industry_matrix_summary: Dict[str, int]
    sector_analysis: Dict[str, SectorAnalysis]
    report_period: Dict[str, Optional[str]]
    generated_at: datetime

# ==================== TREND PREDICTION SCHEMAS ====================

class TrendPredictionRequest(BaseModel):
    """Request for risk trend prediction"""
    industry_code: str
    forecast_months: int = Field(12, ge=1, le=60)
    include_factors: bool = Field(True)
    confidence_threshold: float = Field(0.7, ge=0.5, le=1.0)

class PredictedRiskPoint(BaseModel):
    """Predicted risk data point"""
    month: int
    predicted_factor: float
    risk_level: RiskLevel
    confidence: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

class TrendPredictionResponse(BaseModel):
    """Response from trend prediction"""
    industry_code: str
    historical_trend: Dict[str, Any]
    forecast: List[PredictedRiskPoint]
    risk_drivers: List[str]
    confidence_score: float
    model_accuracy: Optional[float]
    generated_at: datetime

# ==================== QUERY PARAMETER SCHEMAS ====================

class IndustryAdjustmentQueryParams(BaseModel):
    """Query parameters for industry adjustment listing"""
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    is_active: Optional[bool] = None
    risk_level: Optional[RiskLevel] = None
    industry_category: Optional[IndustryCategory] = None
    min_factor: Optional[Decimal] = Field(None, ge=0.5)
    max_factor: Optional[Decimal] = Field(None, le=3.0)
    parent_code: Optional[str] = Field(None, min_length=2, max_length=4)
    search: Optional[str] = Field(None, min_length=1, max_length=100)
    review_due: Optional[bool] = None
    sort_by: Optional[str] = Field("industry_code", pattern="^(industry_code|adjustment_factor|risk_level|created_at)$")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$")

# ==================== INDUSTRY REPORT SCHEMAS ====================

class IndustryReportRequest(BaseModel):
    """Request for industry report"""
    industry_code: str
    include_trends: bool = Field(True)
    include_peers: bool = Field(True)
    include_predictions: bool = Field(False)
    trend_days: int = Field(90, ge=30, le=365)

class PeerComparison(BaseModel):
    """Peer industry comparison"""
    peer_count: int
    average_factor: float
    min_factor: float
    max_factor: float
    percentile: Optional[float] = None

class IndustryReportResponse(BaseModel):
    """Comprehensive industry report"""
    industry_code: str
    description: Optional[str]
    current_adjustment: Dict[str, Any]
    trends: List[IndustryTrend]
    risk_drivers: List[str]
    peer_comparison: PeerComparison
    recommendations: List[str]
    last_updated: Optional[datetime]
    report_generated: datetime

# ==================== VALIDATION HELPERS ====================

def validate_naics_hierarchy(code: str) -> int:
    """Get NAICS code hierarchy level"""
    if '-' in code:  # Range like "31-33"
        return 2
    return len(code)

def get_parent_naics_code(code: str) -> Optional[str]:
    """Get parent NAICS code"""
    if '-' in code:
        return None
    if len(code) <= 2:
        return None
    if len(code) == 3:
        return code[:2]
    if len(code) == 4:
        return code[:3]
    if len(code) == 5 or len(code) == 6:
        return code[:4]
    return None

def calculate_risk_premium_impact(factor: Decimal) -> str:
    """Calculate premium impact from adjustment factor"""
    impact = (factor - 1) * 100
    return f"{impact:+.1f}%"