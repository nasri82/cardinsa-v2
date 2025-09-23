# app/modules/pricing/modifiers/schemas/pricing_discount_schema.py

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum

# ==================== ENUMS ====================

class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    TIERED = "tiered"
    BUNDLE = "bundle"
    LOYALTY = "loyalty"
    SEASONAL = "seasonal"
    PROMOTIONAL = "promotional"
    REFERRAL = "referral"
    CORPORATE = "corporate"
    EARLY_BIRD = "early_bird"

class CustomerType(str, Enum):
    INDIVIDUAL = "individual"
    FAMILY = "family"
    CORPORATE = "corporate"
    SME = "sme"
    GOVERNMENT = "government"
    VIP = "vip"

class LoyaltyTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class Season(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"
    BLACK_FRIDAY = "black_friday"
    CHRISTMAS = "christmas"
    NEW_YEAR = "new_year"
    RAMADAN = "ramadan"
    EID = "eid"

# ==================== BASE SCHEMAS ====================

class PricingDiscountBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Unique discount code")
    label: str = Field(..., min_length=3, max_length=200, description="Display label")
    percentage: Decimal = Field(..., ge=0, le=100, description="Discount percentage")
    fixed_amount: Optional[Decimal] = Field(None, ge=0, description="Fixed discount amount")
    discount_type: DiscountType = Field(default=DiscountType.PERCENTAGE)
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(True)
    
    # Enhanced fields
    minimum_purchase: Optional[Decimal] = Field(None, ge=0, description="Minimum purchase amount")
    maximum_discount: Optional[Decimal] = Field(None, ge=0, description="Maximum discount amount")
    usage_limit: Optional[int] = Field(None, ge=1, description="Total usage limit")
    usage_per_customer: Optional[int] = Field(None, ge=1, description="Usage limit per customer")
    eligible_customer_types: Optional[List[CustomerType]] = Field(default_factory=list)
    required_loyalty_tier: Optional[LoyaltyTier] = None
    stackable: Optional[bool] = Field(False, description="Can stack with other discounts")
    auto_apply: Optional[bool] = Field(False, description="Automatically apply if eligible")
    requires_code: Optional[bool] = Field(True, description="Requires entering code")
    excluded_products: Optional[List[str]] = Field(default_factory=list)
    included_products: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Campaign fields
    campaign_id: Optional[UUID] = Field(None, description="Associated campaign ID")
    campaign_name: Optional[str] = Field(None, max_length=200)
    tier_requirements: Optional[Dict[str, Any]] = Field(None, description="Tiered discount requirements")
    
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
        discount_type = info.data.get('discount_type')
        if discount_type == DiscountType.FIXED and v > 0:
            raise ValueError('Percentage must be 0 for fixed discount type')
        return v
    
    @model_validator(mode='after')
    def validate_discount_logic(self):
        """Cross-field validation"""
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValueError('valid_to must be after valid_from')
        
        if self.discount_type == DiscountType.FIXED and not self.fixed_amount:
            raise ValueError('Fixed amount required for fixed discount type')
        
        if self.discount_type == DiscountType.TIERED and not self.tier_requirements:
            raise ValueError('Tier requirements needed for tiered discount')
        
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

class PricingDiscountCreate(PricingDiscountBase):
    """Schema for creating a discount"""
    created_by: Optional[UUID] = Field(None, description="User who created the record")
    notify_customers: Optional[bool] = Field(False, description="Send notifications to eligible customers")

class PricingDiscountUpdate(BaseModel):
    """Schema for updating a discount"""
    label: Optional[str] = Field(None, min_length=3, max_length=200)
    percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    fixed_amount: Optional[Decimal] = Field(None, ge=0)
    discount_type: Optional[DiscountType] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    minimum_purchase: Optional[Decimal] = Field(None, ge=0)
    maximum_discount: Optional[Decimal] = Field(None, ge=0)
    usage_limit: Optional[int] = Field(None, ge=1)
    usage_per_customer: Optional[int] = Field(None, ge=1)
    eligible_customer_types: Optional[List[CustomerType]] = None
    required_loyalty_tier: Optional[LoyaltyTier] = None
    stackable: Optional[bool] = None
    auto_apply: Optional[bool] = None
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

class PricingDiscount(PricingDiscountBase):
    """Complete discount response schema"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    deleted_at: Optional[datetime] = None
    
    # Computed fields
    is_valid: Optional[bool] = Field(None, description="Currently valid")
    days_remaining: Optional[int] = Field(None, description="Days until expiration")
    usage_count: Optional[int] = Field(None, description="Times used")
    remaining_uses: Optional[int] = Field(None, description="Remaining uses")
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_encoders={
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )

# ==================== DISCOUNT CALCULATION SCHEMAS ====================

class DiscountCalculationRequest(BaseModel):
    """Request for discount calculation"""
    discount_codes: List[str] = Field(..., min_items=1, max_items=10)
    base_amount: Decimal = Field(..., gt=0, description="Base amount before discount")
    customer_profile: Optional[Dict[str, Any]] = Field(None, description="Customer information")
    product_ids: Optional[List[str]] = Field(default_factory=list)
    apply_best_only: bool = Field(False, description="Apply only the best discount")

class DiscountApplicationResult(BaseModel):
    """Single discount application result"""
    code: str
    label: str
    amount: float
    type: str
    stackable: bool
    applied: bool
    reason: Optional[str] = None

class DiscountCalculationResponse(BaseModel):
    """Response from discount calculation"""
    base_amount: float
    total_discount: float
    final_amount: float
    discounts_applied: List[DiscountApplicationResult]
    savings_percentage: float
    discount_count: int
    eligibility_messages: List[str] = Field(default_factory=list)
    calculation_timestamp: datetime = Field(default_factory=datetime.utcnow)

# ==================== ELIGIBILITY SCHEMAS ====================

class EligibilityCheckRequest(BaseModel):
    """Request for eligibility check"""
    discount_code: str
    customer_id: Optional[UUID] = None
    customer_type: Optional[CustomerType] = None
    loyalty_tier: Optional[LoyaltyTier] = None
    purchase_amount: Optional[Decimal] = Field(None, gt=0)
    product_ids: Optional[List[str]] = Field(default_factory=list)

class EligibilityCheckResponse(BaseModel):
    """Response from eligibility check"""
    eligible: bool
    discount_code: str
    reasons: List[str]
    requirements_met: Dict[str, bool]
    suggested_actions: List[str] = Field(default_factory=list)

# ==================== PROMOTIONAL CAMPAIGN SCHEMAS ====================

class CampaignCreateRequest(BaseModel):
    """Request to create promotional campaign"""
    code: str = Field(..., min_length=2, max_length=50)
    label: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    base_percentage: Decimal = Field(..., ge=0, le=100)
    start_date: datetime
    end_date: datetime
    tiers: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    target_audience: Optional[List[CustomerType]] = Field(default_factory=list)
    budget: Optional[Decimal] = Field(None, gt=0)
    expected_reach: Optional[int] = Field(None, gt=0)
    notification_channels: Optional[List[str]] = Field(default_factory=list)

class CampaignTier(BaseModel):
    """Campaign tier definition"""
    name: str
    label: str
    percentage: Decimal
    min_amount: Decimal
    max_amount: Optional[Decimal] = None

class CampaignCreateResponse(BaseModel):
    """Response from campaign creation"""
    campaign_id: UUID
    campaign_name: str
    discounts_created: int
    discount_codes: List[str]
    valid_from: datetime
    valid_to: datetime
    estimated_impact: Dict[str, float]
    activation_status: str

# ==================== SEASONAL DISCOUNT SCHEMAS ====================

class SeasonalDiscountRequest(BaseModel):
    """Request for seasonal discount setup"""
    season: Season
    percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    duration_days: Optional[int] = Field(None, ge=1, le=365)
    auto_activate: bool = Field(True)
    customer_types: Optional[List[CustomerType]] = Field(default_factory=list)

class SeasonalDiscountResponse(BaseModel):
    """Response from seasonal discount setup"""
    season: str
    discounts_created: List[Dict[str, Any]]
    activation_date: datetime
    expiration_date: datetime
    estimated_revenue_impact: float

# ==================== ANALYTICS SCHEMAS ====================

class DiscountStatistics(BaseModel):
    """Discount statistics"""
    total_discounts: int
    active_discounts: int
    expired_discounts: int
    upcoming_discounts: int
    average_percentage: float
    total_usage: int
    total_savings_provided: float
    by_type: Dict[str, int]
    by_customer_type: Dict[str, float]

class DiscountPerformance(BaseModel):
    """Discount performance metrics"""
    total_discounts_applied: int
    total_discount_amount: float
    average_discount_per_transaction: float
    most_used_discount: Optional[str]
    least_used_discount: Optional[str]
    conversion_rate_with_discount: float
    revenue_impact: float
    roi: float

class ActiveCampaign(BaseModel):
    """Active campaign information"""
    campaign_id: str
    campaign_name: str
    discounts: List[str]
    total_percentage: float
    days_remaining: int
    usage_count: int
    performance_score: float

class DiscountAnalyticsResponse(BaseModel):
    """Comprehensive discount analytics"""
    statistics: DiscountStatistics
    performance: DiscountPerformance
    upcoming_discounts: List[Dict[str, Any]]
    active_campaigns: List[ActiveCampaign]
    trending_discounts: List[Dict[str, Any]]
    report_period: Dict[str, Optional[str]]
    generated_at: datetime

# ==================== BULK OPERATIONS SCHEMAS ====================

class DiscountBulkCreate(BaseModel):
    """Schema for bulk discount creation"""
    discounts: List[PricingDiscountCreate] = Field(..., min_items=1, max_items=100)
    validate_all: bool = Field(True)
    skip_duplicates: bool = Field(False)
    campaign_id: Optional[UUID] = None

class DiscountBulkUpdate(BaseModel):
    """Schema for bulk discount updates"""
    discount_ids: List[UUID] = Field(..., min_items=1)
    update_data: PricingDiscountUpdate
    updated_by: Optional[UUID] = None

class DiscountBulkResult(BaseModel):
    """Result of bulk operations"""
    total_processed: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]

# ==================== QUERY PARAMETER SCHEMAS ====================

class DiscountQueryParams(BaseModel):
    """Query parameters for discount listing"""
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    discount_type: Optional[DiscountType] = None
    is_active: Optional[bool] = None
    is_valid: Optional[bool] = None
    customer_type: Optional[CustomerType] = None
    campaign_id: Optional[UUID] = None
    search: Optional[str] = Field(None, min_length=1, max_length=100)
    valid_on: Optional[date] = None
    min_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    max_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    stackable: Optional[bool] = None
    sort_by: Optional[str] = Field("created_at", pattern="^(code|percentage|valid_from|usage_count|created_at)$")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")

# ==================== CUSTOMER PROFILE SCHEMAS ====================

class CustomerProfile(BaseModel):
    """Customer profile for discount eligibility"""
    customer_id: UUID
    customer_type: CustomerType
    loyalty_tier: Optional[LoyaltyTier] = None
    purchase_amount: Optional[Decimal] = None
    purchase_history: Optional[List[Dict[str, Any]]] = None
    registration_date: Optional[date] = None
    total_purchases: Optional[Decimal] = None
    preferred_categories: Optional[List[str]] = None

class PersonalizedDiscountResponse(BaseModel):
    """Personalized discount recommendations"""
    customer_id: UUID
    eligible_discounts: List[PricingDiscount]
    recommended_discounts: List[Dict[str, Any]]
    potential_savings: float
    loyalty_benefits: Optional[Dict[str, Any]] = None

# ==================== VALIDATION HELPERS ====================

def validate_discount_stacking(
    discounts: List[PricingDiscount],
    max_stack: int = 3
) -> List[PricingDiscount]:
    """Validate and filter stackable discounts"""
    stackable = [d for d in discounts if d.stackable]
    non_stackable = [d for d in discounts if not d.stackable]
    
    # If there's a non-stackable discount, use only the best one
    if non_stackable:
        best_non_stackable = max(non_stackable, key=lambda d: d.percentage)
        return [best_non_stackable]
    
    # Otherwise, return stackable discounts up to max_stack
    return sorted(stackable, key=lambda d: d.percentage, reverse=True)[:max_stack]

def calculate_tiered_discount_amount(
    amount: Decimal,
    tiers: List[Dict[str, Any]]
) -> Decimal:
    """Calculate discount amount for tiered structure"""
    for tier in sorted(tiers, key=lambda t: t.get('min_amount', 0), reverse=True):
        if amount >= tier.get('min_amount', 0):
            return amount * (Decimal(str(tier.get('percentage', 0))) / 100)
    return Decimal("0")