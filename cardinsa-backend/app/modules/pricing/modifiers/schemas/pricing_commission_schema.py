# app/modules/pricing/modifiers/schemas/pricing_commission_schema.py

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# ==================== ENUMS ====================

class CommissionChannel(str, Enum):
    DIRECT_SALES = "direct_sales"
    AGENT = "agent"
    BROKER = "broker"
    PARTNER = "partner"
    AFFILIATE = "affiliate"
    ONLINE = "online"
    CORPORATE = "corporate"
    B2B = "b2b"
    REFERRAL = "referral"

class CommissionType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    TIERED = "tiered"
    HYBRID = "hybrid"
    PERFORMANCE_BASED = "performance_based"

class AgentTier(str, Enum):
    JUNIOR = "junior"
    SENIOR = "senior"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"

class PerformanceRating(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    STANDARD = "standard"
    BELOW = "below"
    PROBATION = "probation"

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    UNDER_REVIEW = "under_review"

# ==================== BASE SCHEMAS ====================

class PricingCommissionBase(BaseModel):
    channel: CommissionChannel = Field(..., description="Sales channel")
    commission_type: CommissionType = Field(default=CommissionType.PERCENTAGE)
    value: Decimal = Field(..., ge=0, description="Commission value")
    currency: Optional[str] = Field("USD", pattern="^[A-Z]{3}$", description="Currency code")
    is_active: Optional[bool] = Field(True)
    
    # Enhanced fields
    min_sale_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum sale for commission")
    max_commission: Optional[Decimal] = Field(None, ge=0, description="Maximum commission cap")
    tier_requirements: Optional[Dict[str, Any]] = Field(None, description="Tier-based requirements")
    performance_multiplier: Optional[bool] = Field(False, description="Apply performance multiplier")
    override_eligible: Optional[bool] = Field(False, description="Eligible for overrides")
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    policy_types: Optional[List[str]] = Field(default_factory=list, description="Applicable policy types")
    excluded_products: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v, info):
        """Validate commission value based on type"""
        commission_type = info.data.get('commission_type')
        if commission_type == CommissionType.PERCENTAGE and v > 100:
            raise ValueError('Percentage commission cannot exceed 100%')
        if commission_type == CommissionType.FIXED and v > 1000000:
            raise ValueError('Fixed commission cannot exceed 1,000,000')
        return v
    
    @field_validator('channel')
    @classmethod
    def validate_channel(cls, v):
        """Validate channel format"""
        return v.lower().replace(' ', '_')
    
    @model_validator(mode='after')
    def validate_commission_logic(self):
        """Cross-field validation"""
        if self.effective_date and self.expiry_date and self.effective_date >= self.expiry_date:
            raise ValueError('Expiry date must be after effective date')
        
        if self.commission_type == CommissionType.TIERED and not self.tier_requirements:
            raise ValueError('Tier requirements needed for tiered commission')
        
        return self

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

class PricingCommissionCreate(PricingCommissionBase):
    """Schema for creating a commission"""
    created_by: Optional[UUID] = Field(None, description="User who created the record")
    requires_approval: Optional[bool] = Field(False, description="Requires approval before activation")

class PricingCommissionUpdate(BaseModel):
    """Schema for updating a commission"""
    channel: Optional[CommissionChannel] = None
    commission_type: Optional[CommissionType] = None
    value: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    is_active: Optional[bool] = None
    min_sale_amount: Optional[Decimal] = Field(None, ge=0)
    max_commission: Optional[Decimal] = Field(None, ge=0)
    tier_requirements: Optional[Dict[str, Any]] = None
    performance_multiplier: Optional[bool] = None
    override_eligible: Optional[bool] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    policy_types: Optional[List[str]] = None
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

class PricingCommission(PricingCommissionBase):
    """Complete commission response schema"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    deleted_at: Optional[datetime] = None
    
    # Computed fields
    compliance_status: Optional[ComplianceStatus] = None
    regulatory_limit: Optional[float] = None
    is_within_limits: Optional[bool] = None
    
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
# ==================== HIERARCHICAL COMMISSION SCHEMAS ====================

class HierarchicalCommissionRequest(BaseModel):
    """Request for hierarchical commission calculation"""
    sale_amount: Decimal = Field(..., gt=0, description="Sale amount")
    agent_id: UUID
    agent_tier: AgentTier
    policy_type: Optional[str] = None
    include_overrides: bool = Field(True)
    include_upline: bool = Field(True)
    performance_period: Optional[str] = Field("current", description="Performance period to consider")

class UplineCommission(BaseModel):
    """Upline commission detail"""
    level: int
    amount: float
    rate: float
    agent_tier: Optional[str] = None
    agent_id: Optional[UUID] = None

class HierarchicalCommissionResponse(BaseModel):
    """Response from hierarchical commission calculation"""
    sale_amount: float
    agent_commission: float
    commission_rate: float
    performance_multiplier: float
    agent_tier: str
    upline_commissions: List[UplineCommission]
    total_commission: float
    net_amount: float
    override_amount: Optional[float] = None
    override_applied: bool = False
    calculation_breakdown: Dict[str, Any]

# ==================== PERFORMANCE TRACKING SCHEMAS ====================

class PerformanceTrackingRequest(BaseModel):
    """Request for agent performance tracking"""
    agent_id: UUID
    period: str = Field("monthly", pattern="^(daily|weekly|monthly|quarterly|yearly)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_team: bool = Field(False)
    include_trends: bool = Field(True)

class PerformanceTrend(BaseModel):
    """Performance trend data point"""
    period: str
    sales: float
    commission: float
    deals: int
    average_deal_size: float

class PerformanceMetrics(BaseModel):
    """Agent performance metrics"""
    agent_id: UUID
    period: str
    period_start: date
    period_end: date
    total_sales: float
    total_commission_earned: float
    average_commission_rate: float
    deals_closed: int
    average_deal_size: float
    performance_rating: PerformanceRating
    rank_in_team: Optional[int] = None
    target_achievement: float
    bonus_eligible: bool
    bonus_amount: Optional[float] = None
    trend: List[PerformanceTrend]

# ==================== TEAM COMMISSION SCHEMAS ====================

class TeamMember(BaseModel):
    """Team member for commission calculation"""
    agent_id: UUID
    tier: AgentTier
    split: float = Field(..., ge=0, le=1, description="Commission split percentage")
    role: Optional[str] = None

class TeamCommissionRequest(BaseModel):
    """Request for team commission calculation"""
    team_id: UUID
    sale_amount: Decimal = Field(..., gt=0)
    team_members: Optional[List[TeamMember]] = None
    split_type: str = Field("percentage", pattern="^(percentage|equal|weighted)$")
    include_hierarchy: bool = Field(True)

class TeamMemberCommission(BaseModel):
    """Individual team member commission"""
    agent_id: UUID
    tier: str
    split_percentage: float
    sale_portion: float
    commission_earned: float
    performance_bonus: Optional[float] = None

class TeamCommissionResponse(BaseModel):
    """Response from team commission calculation"""
    team_id: UUID
    total_sale: float
    team_size: int
    total_commission: float
    average_commission: float
    member_commissions: List[TeamMemberCommission]
    hierarchy_bonuses: Optional[Dict[str, float]] = None

# ==================== COMPLIANCE SCHEMAS ====================

class ComplianceCheckRequest(BaseModel):
    """Request for compliance check"""
    channel: CommissionChannel
    value: Decimal
    commission_type: CommissionType
    include_audit: bool = Field(False)

class ComplianceIssue(BaseModel):
    """Compliance issue detail"""
    commission_id: UUID
    channel: str
    issue: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    recommendation: str

class ComplianceReportResponse(BaseModel):
    """Compliance report response"""
    total_active: int
    compliant_count: int
    violation_count: int
    compliance_rate: float
    violations: List[ComplianceIssue]
    regulatory_compliance: Dict[str, Any]
    audit_items: List[Dict[str, Any]]
    report_date: datetime
    status: ComplianceStatus

# ==================== ANALYTICS SCHEMAS ====================

class CommissionStatistics(BaseModel):
    """Commission statistics"""
    total_configurations: int
    active_configurations: int
    average_percentage_rate: float
    average_fixed_amount: float
    min_commission_value: float
    max_commission_value: float
    channel_distribution: List[Dict[str, Any]]
    compliance_rate: float

class ChannelEffectiveness(BaseModel):
    """Channel effectiveness analysis"""
    channel: str
    commission_rate: float
    conversion_rate: float
    average_deal_size: float
    roi: float
    cost_per_acquisition: float

class TopPerformer(BaseModel):
    """Top performing agent"""
    rank: int
    agent_id: UUID
    agent_name: Optional[str]
    total_commission: float
    deals_closed: int
    average_deal_size: float
    performance_rating: str

class CommissionAnalyticsResponse(BaseModel):
    """Comprehensive commission analytics"""
    statistics: CommissionStatistics
    trends: List[Dict[str, Any]]
    hierarchy_analysis: List[Dict[str, Any]]
    projections: Dict[str, float]
    top_performers: List[TopPerformer]
    channel_effectiveness: Dict[str, ChannelEffectiveness]
    report_period: Dict[str, Optional[str]]
    generated_at: datetime

# ==================== BULK OPERATIONS SCHEMAS ====================

class CommissionBulkCreate(BaseModel):
    """Schema for bulk commission creation"""
    commissions: List[PricingCommissionCreate] = Field(..., min_items=1, max_items=50)
    validate_all: bool = Field(True)
    skip_duplicates: bool = Field(False)

class CommissionBulkUpdate(BaseModel):
    """Schema for bulk commission updates"""
    channel_updates: Dict[str, Decimal] = Field(..., description="Map of channel to new value")
    commission_type: Optional[CommissionType] = None
    updated_by: Optional[UUID] = None

# ==================== QUERY PARAMETER SCHEMAS ====================

class CommissionQueryParams(BaseModel):
    """Query parameters for commission listing"""
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    channel: Optional[CommissionChannel] = None
    commission_type: Optional[CommissionType] = None
    is_active: Optional[bool] = None
    min_value: Optional[Decimal] = Field(None, ge=0)
    max_value: Optional[Decimal] = Field(None, ge=0)
    policy_type: Optional[str] = None
    compliance_status: Optional[ComplianceStatus] = None
    search: Optional[str] = Field(None, min_length=1, max_length=100)
    sort_by: Optional[str] = Field("created_at", pattern="^(channel|value|created_at|compliance_status)$")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")

# ==================== APPROVAL WORKFLOW SCHEMAS ====================

class CommissionApprovalRequest(BaseModel):
    """Request for commission approval"""
    commission_id: UUID
    action: str = Field(..., pattern="^(approve|reject|request_changes)$")
    comments: Optional[str] = Field(None, max_length=500)
    approved_by: UUID

class CommissionApprovalResponse(BaseModel):
    """Response from commission approval"""
    commission_id: UUID
    status: str
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    comments: Optional[str]

# ==================== VALIDATION HELPERS ====================

def validate_commission_limits(
    channel: CommissionChannel,
    value: Decimal,
    commission_type: CommissionType
) -> tuple[bool, Optional[str]]:
    """Validate commission against regulatory limits"""
    limits = {
        CommissionChannel.BROKER: {"percentage": 35, "fixed": 10000},
        CommissionChannel.AGENT: {"percentage": 25, "fixed": 5000},
        CommissionChannel.PARTNER: {"percentage": 20, "fixed": 3000},
        CommissionChannel.DIRECT_SALES: {"percentage": 15, "fixed": 2000},
        CommissionChannel.ONLINE: {"percentage": 10, "fixed": 1000}
    }
    
    channel_limits = limits.get(channel, {"percentage": 30, "fixed": 5000})
    
    if commission_type == CommissionType.PERCENTAGE:
        if value > channel_limits["percentage"]:
            return False, f"Exceeds regulatory limit of {channel_limits['percentage']}%"
    elif commission_type == CommissionType.FIXED:
        if value > channel_limits["fixed"]:
            return False, f"Exceeds regulatory limit of {channel_limits['fixed']}"
    
    return True, None

def calculate_performance_multiplier(rating: PerformanceRating) -> Decimal:
    """Calculate performance-based commission multiplier"""
    multipliers = {
        PerformanceRating.EXCELLENT: Decimal("1.2"),
        PerformanceRating.GOOD: Decimal("1.1"),
        PerformanceRating.STANDARD: Decimal("1.0"),
        PerformanceRating.BELOW: Decimal("0.9"),
        PerformanceRating.PROBATION: Decimal("0.8")
    }
    return multipliers.get(rating, Decimal("1.0"))