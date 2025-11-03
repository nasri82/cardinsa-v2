# app/modules/pricing/plans/schemas/plan_coverage_link_schema.py
"""
Plan Coverage Link Schemas

Pydantic models for API serialization and validation.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

# Enums from the model
class CoverageTier(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    COMPREHENSIVE = "comprehensive"

class LimitType(str, Enum):
    PER_INCIDENT = "per_incident"
    PER_YEAR = "per_year"
    PER_LIFETIME = "per_lifetime"
    PER_PERSON = "per_person"
    PER_FAMILY = "per_family"
    AGGREGATE = "aggregate"

class NetworkRestriction(str, Enum):
    NONE = "none"
    IN_NETWORK_ONLY = "in_network_only"
    PREFERRED_NETWORK = "preferred_network"
    TIERED_NETWORK = "tiered_network"
    RESTRICTED_NETWORK = "restricted_network"

class CoverageStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    EXCLUDED = "excluded"

class CostCalculationRequest(BaseModel):
    """Request for cost calculation"""
    service_cost: Decimal = Field(..., gt=0, description="Total service cost")
    accumulated_deductible: Decimal = Field(0, ge=0, description="Already paid deductible")

class CostCalculationResponse(BaseModel):
    """Response for cost calculation"""
    service_cost: Decimal
    deductible: Decimal
    copay: Decimal
    member_pays: Decimal
    insurance_pays: Decimal

class PlanCoverageLinkBase(BaseModel):
    """Base schema for Plan Coverage Link"""
    coverage_tier: CoverageTier = CoverageTier.STANDARD
    coverage_amount: Decimal = Field(0, ge=0, description="Maximum coverage amount")
    specific_limit: Optional[Decimal] = Field(None, ge=0)
    limit_type: LimitType = LimitType.PER_YEAR
    unit: Optional[str] = Field(None, max_length=50)
    
    # Cost sharing
    deductible: Decimal = Field(0, ge=0)
    copay_percentage: Decimal = Field(0, ge=0, le=100)
    copay_amount: Optional[Decimal] = Field(None, ge=0)
    coinsurance: Optional[Decimal] = Field(None, ge=0, le=100)
    
    # Limits
    frequency_limit: Optional[int] = Field(None, ge=0)
    annual_maximum: Optional[Decimal] = Field(None, ge=0)
    lifetime_maximum: Optional[Decimal] = Field(None, ge=0)
    waiting_period_days: int = Field(0, ge=0)
    
    # Conditions
    is_mandatory: bool = False
    is_excluded: bool = False
    approval_needed: bool = False
    prior_authorization_required: bool = False
    
    # Network
    network_restrictions: NetworkRestriction = NetworkRestriction.NONE
    geographic_restrictions: Optional[Dict[str, Any]] = None
    
    # Categorization
    sub_category: Optional[str] = Field(None, max_length=100)
    condition_tag: Optional[str] = Field(None, max_length=100)
    
    # Dates
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    # Documentation
    notes: Optional[str] = None
    member_description: Optional[str] = None
    member_description_ar: Optional[str] = None
    
    # Metadata
    display_order: int = Field(0, ge=0)
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
    
    @field_validator('expiry_date')
    @classmethod
    def expiry_after_effective(cls, v: Optional[date], info) -> Optional[date]:
        if v and hasattr(info, 'data') and 'effective_date' in info.data:
            effective_date = info.data['effective_date']
            if effective_date and v <= effective_date:
                raise ValueError('Expiry date must be after effective date')
        return v
    
    @model_validator(mode='after')
    def validate_not_both_excluded_and_mandatory(self):
        if self.is_mandatory and self.is_excluded:
            raise ValueError('Coverage cannot be both mandatory and excluded')
        return self

class PlanCoverageLinkCreate(PlanCoverageLinkBase):
    """Create schema for Plan Coverage Link"""
    coverage_id: UUID = Field(..., description="Coverage ID to link")

class PlanCoverageLinkUpdate(BaseModel):
    """Update schema for Plan Coverage Link"""
    coverage_tier: Optional[CoverageTier] = None
    coverage_amount: Optional[Decimal] = Field(None, ge=0)
    specific_limit: Optional[Decimal] = Field(None, ge=0)
    limit_type: Optional[LimitType] = None
    unit: Optional[str] = Field(None, max_length=50)
    
    deductible: Optional[Decimal] = Field(None, ge=0)
    copay_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    copay_amount: Optional[Decimal] = Field(None, ge=0)
    coinsurance: Optional[Decimal] = Field(None, ge=0, le=100)
    
    frequency_limit: Optional[int] = Field(None, ge=0)
    annual_maximum: Optional[Decimal] = Field(None, ge=0)
    lifetime_maximum: Optional[Decimal] = Field(None, ge=0)
    waiting_period_days: Optional[int] = Field(None, ge=0)
    
    is_mandatory: Optional[bool] = None
    is_excluded: Optional[bool] = None
    approval_needed: Optional[bool] = None
    prior_authorization_required: Optional[bool] = None
    
    network_restrictions: Optional[NetworkRestriction] = None
    geographic_restrictions: Optional[Dict[str, Any]] = None
    
    sub_category: Optional[str] = Field(None, max_length=100)
    condition_tag: Optional[str] = Field(None, max_length=100)
    
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    notes: Optional[str] = None
    member_description: Optional[str] = None
    member_description_ar: Optional[str] = None
    
    display_order: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class PlanCoverageLinkResponse(PlanCoverageLinkBase):
    """Response schema for Plan Coverage Link"""
    id: UUID
    plan_id: UUID
    coverage_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    model_config = {"from_attributes": True}

class BulkCoverageLinkCreate(BaseModel):
    """Bulk create coverage links"""
    coverage_links: List[PlanCoverageLinkCreate] = Field(..., min_length=1, max_length=50)

class CoverageLinkSummary(BaseModel):
    """Summary of coverage links for a plan"""
    plan_id: UUID
    total_coverages: int
    mandatory_coverages: int
    excluded_coverages: int
    coverage_tiers: Dict[str, int]
    network_restrictions: Dict[str, int]