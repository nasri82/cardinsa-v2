# app/modules/plans/schemas/plan_territory_schema.py
"""
Plan Territory Schemas

Pydantic models for API serialization and validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from app.modules.pricing.plans.models.plan_territory_model import TerritoryType, TerritoryStatus, RegulatoryStatus

class TerritoryGeographicBounds(BaseModel):
    """Geographic boundary definition"""
    type: str = Field(..., description="GeoJSON type")
    coordinates: List[Any] = Field(..., description="GeoJSON coordinates")
    properties: Optional[Dict[str, Any]] = None

class TerritoryRateAdjustment(BaseModel):
    """Rate adjustment definition"""
    coverage_type: str
    adjustment_type: str  # multiplier, additive, percentage
    value: Decimal
    effective_date: date
    expiry_date: Optional[date] = None

class PlanTerritoryBase(BaseModel):
    """Base territory schema"""
    territory_type: TerritoryType
    territory_code: str = Field(..., max_length=20)
    territory_name: str = Field(..., max_length=200)
    territory_description: Optional[str] = None
    
    # Geographic definition
    geographic_bounds: Optional[TerritoryGeographicBounds] = None
    postal_codes: Optional[List[str]] = None
    administrative_zones: Optional[List[str]] = None
    
    # Pricing
    rate_factor: Decimal = Field(1.0000, ge=0.0001, le=10.0000)
    rate_adjustments: Optional[List[TerritoryRateAdjustment]] = None
    minimum_premium: Optional[Decimal] = Field(None, ge=0)
    maximum_premium: Optional[Decimal] = Field(None, ge=0)
    
    # Risk characteristics
    risk_level: str = Field("standard", pattern="^(low|standard|high|extreme)$")
    catastrophe_zone: bool = False
    flood_zone: bool = False
    earthquake_zone: bool = False
    hurricane_zone: bool = False
    
    # Regulatory
    regulatory_jurisdiction: Optional[str] = Field(None, max_length=100)
    regulatory_status: RegulatoryStatus = RegulatoryStatus.APPROVED

    regulatory_requirements: Optional[Dict[str, Any]] = None
    compliance_notes: Optional[str] = None
    
    # Status
    status: TerritoryStatus = TerritoryStatus.ACTIVE
    effective_date: date
    expiry_date: Optional[date] = None
    
    # Business metrics
    market_penetration: Optional[Decimal] = Field(None, ge=0, le=100)
    competitive_position: Optional[str] = Field(None, max_length=50)
    
    @validator('expiry_date')
    def expiry_after_effective(cls, v, values):
        if v and 'effective_date' in values:
            if v <= values['effective_date']:
                raise ValueError('Expiry date must be after effective date')
        return v
    
    @validator('maximum_premium')
    def max_greater_than_min(cls, v, values):
        if v and 'minimum_premium' in values and values['minimum_premium']:
            if v <= values['minimum_premium']:
                raise ValueError('Maximum premium must be greater than minimum premium')
        return v

class PlanTerritoryCreate(PlanTerritoryBase):
    """Create territory schema"""
    pass

class PlanTerritoryUpdate(BaseModel):
    """Update territory schema"""
    territory_name: Optional[str] = Field(None, max_length=200)
    territory_description: Optional[str] = None
    rate_factor: Optional[Decimal] = Field(None, ge=0.0001, le=10.0000)
    rate_adjustments: Optional[List[TerritoryRateAdjustment]] = None
    minimum_premium: Optional[Decimal] = Field(None, ge=0)
    maximum_premium: Optional[Decimal] = Field(None, ge=0)
    risk_level: Optional[str] = Field(None, pattern="^(low|standard|high|extreme)$")
    catastrophe_zone: Optional[bool] = None
    flood_zone: Optional[bool] = None
    earthquake_zone: Optional[bool] = None
    hurricane_zone: Optional[bool] = None
    regulatory_jurisdiction: Optional[str] = Field(None, max_length=100)
    regulatory_status: Optional[RegulatoryStatus] = None
    regulatory_requirements: Optional[Dict[str, Any]] = None
    compliance_notes: Optional[str] = None
    status: Optional[TerritoryStatus] = None
    expiry_date: Optional[date] = None
    market_penetration: Optional[Decimal] = Field(None, ge=0, le=100)
    competitive_position: Optional[str] = Field(None, max_length=50)

class PlanTerritoryResponse(PlanTerritoryBase):
    """Territory response schema"""
    id: UUID
    plan_id: UUID
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    class Config:
        from_attributes = True

class TerritoryPremiumCalculation(BaseModel):
    """Territory premium calculation request"""
    territory_code: str
    base_premium: Decimal = Field(..., gt=0)
    coverage_types: List[str] = []
    policy_data: Optional[Dict[str, Any]] = None

class TerritoryAnalytics(BaseModel):
    """Territory analytics response"""
    territory_code: str
    territory_name: str
    active_policies: int
    total_premium: Decimal
    loss_ratio: Decimal
    market_share: Decimal
    risk_score: Decimal
    last_updated: datetime