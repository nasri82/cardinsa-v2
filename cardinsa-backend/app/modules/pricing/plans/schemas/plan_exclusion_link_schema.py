# app/modules/pricing/plans/schemas/plan_exclusion_link_schema.py
"""
Plan Exclusion Link Schemas - Pydantic v2 Compatible

Pydantic models for API serialization and validation.
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

# Example enums - adjust based on your actual model
class ExclusionStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    EXCLUDED = "excluded"

class ExclusionType(str, Enum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    CONDITIONAL = "conditional"

class LinkStatus(str, Enum):
    """Link status"""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    EXPIRED = "expired"

class ApplicationScope(str, Enum):
    """Scope of exclusion application"""
    GLOBAL = "global"
    SPECIFIC = "specific"
    CONDITIONAL = "conditional"

class OverrideType(str, Enum):
    """Type of override on standard exclusion"""
    NONE = "none"
    EXTENDED = "extended"
    REDUCED = "reduced"
    CUSTOMIZED = "customized"

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

class PlanExclusionLinkBase(BaseModel):
    """Base schema for Plan Exclusion Link"""
    
    exclusion_type: Optional[ExclusionType] = ExclusionType.PERMANENT
    exclusion_amount: Decimal = Field(0, ge=0, description="Exclusion amount if applicable")
    
    # Dates
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    # Conditions
    is_mandatory: bool = False
    is_excluded: bool = True  # Typically true for exclusions
    approval_needed: bool = False
    
    # Documentation
    notes: Optional[str] = None
    exclusion_description: Optional[str] = None
    exclusion_description_ar: Optional[str] = None
    
    # Metadata
    display_order: int = Field(0, ge=0)
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Pydantic v2 model validator for cross-field validation
    @model_validator(mode='after')
    def validate_dates_and_logic(self):
        """Validate expiry date is after effective date and exclusion business logic"""
        # Date validation
        if self.expiry_date and self.effective_date:
            if self.expiry_date <= self.effective_date:
                raise ValueError('Expiry date must be after effective date')
        
        # Business logic validation
        if self.is_mandatory and not self.is_excluded:
            raise ValueError('Exclusions should typically be excluded items')
        
        return self

class PlanExclusionLinkCreate(PlanExclusionLinkBase):
    """Create schema for Plan Exclusion Link"""
    exclusion_id: UUID = Field(..., description="Exclusion ID to link")
    plan_id: Optional[UUID] = Field(None, description="Plan ID (may be set by route)")

class PlanExclusionLinkUpdate(BaseModel):
    """Update schema for Plan Exclusion Link"""
    exclusion_type: Optional[ExclusionType] = None
    exclusion_amount: Optional[Decimal] = Field(None, ge=0)
    
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    is_mandatory: Optional[bool] = None
    is_excluded: Optional[bool] = None
    approval_needed: Optional[bool] = None
    
    notes: Optional[str] = None
    exclusion_description: Optional[str] = None
    exclusion_description_ar: Optional[str] = None
    
    display_order: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Pydantic v2 model validator for update schema
    @model_validator(mode='after')
    def validate_update_dates(self):
        """Validate expiry date is after effective date for updates"""
        if self.expiry_date and self.effective_date:
            if self.expiry_date <= self.effective_date:
                raise ValueError('Expiry date must be after effective date')
        return self

class PlanExclusionLinkResponse(PlanExclusionLinkBase):
    """Response schema for Plan Exclusion Link"""
    id: UUID
    plan_id: UUID
    exclusion_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    # Computed fields
    is_effective: Optional[bool] = None
    effective_text: Optional[str] = None
    
    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)

class BulkExclusionLinkCreate(BaseModel):
    """Bulk create exclusion links"""
    exclusion_links: List[PlanExclusionLinkCreate] = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="List of exclusion links to create"
    )

class ExclusionLinkSummary(BaseModel):
    """Summary of exclusion links for a plan"""
    plan_id: UUID
    total_links: int
    active_links: int
    mandatory_links: int
    by_status: Dict[str, int]
    by_scope: Dict[str, int]
    by_override_type: Dict[str, int]
    highlighted_links: int

class ExclusionLinkSearchFilters(BaseModel):
    """Filters for searching exclusion links"""
    status: Optional[LinkStatus] = None
    is_active: Optional[bool] = None
    is_mandatory: Optional[bool] = None
    application_scope: Optional[ApplicationScope] = None
    override_type: Optional[OverrideType] = None
    is_highlighted: Optional[bool] = None
    effective_date: Optional[date] = None
    display_category: Optional[str] = None

class CoverageApplicationCheck(BaseModel):
    """Request to check coverage application"""
    coverage_id: UUID

class ExclusionLinkEffectivenessCheck(BaseModel):
    """Request to check link effectiveness"""
    check_date: Optional[date] = None
    coverage_id: Optional[UUID] = None