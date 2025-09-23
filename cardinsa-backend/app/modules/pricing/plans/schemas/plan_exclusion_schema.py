# app/modules/pricing/plans/schemas/plan_exclusion_schema.py
"""
Plan Exclusion Schemas

Pydantic models for API serialization and validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from enum import Enum

# Enums from the model
class ExclusionType(str, Enum):
    MEDICAL = "medical"
    MOTOR = "motor"
    GENERAL = "general"
    DENTAL = "dental"
    VISION = "vision"
    MENTAL_HEALTH = "mental_health"
    MATERNITY = "maternity"
    SPORTS = "sports"
    TRAVEL = "travel"
    OCCUPATIONAL = "occupational"
    PRE_EXISTING = "pre_existing"
    COSMETIC = "cosmetic"
    EXPERIMENTAL = "experimental"

class ExclusionCategory(str, Enum):
    CONDITION = "condition"
    PROCEDURE = "procedure"
    MEDICATION = "medication"
    PROVIDER = "provider"
    LOCATION = "location"
    CIRCUMSTANCE = "circumstance"
    TIME_BASED = "time_based"
    AGE_BASED = "age_based"
    BEHAVIORAL = "behavioral"

class ExclusionSeverity(str, Enum):
    ABSOLUTE = "absolute"
    CONDITIONAL = "conditional"
    TEMPORARY = "temporary"
    PARTIAL = "partial"
    WAIVERABLE = "waiverable"

class RegulatoryBasis(str, Enum):
    REGULATORY_REQUIRED = "regulatory_required"
    COMPANY_POLICY = "company_policy"
    INDUSTRY_STANDARD = "industry_standard"
    RISK_MANAGEMENT = "risk_management"
    COST_CONTROL = "cost_control"

class ExceptionCondition(BaseModel):
    """Exception condition definition"""
    condition_key: str = Field(..., description="Context key to check")
    condition_value: Any = Field(..., description="Value that must match")
    operator: str = Field("equals", description="Comparison operator")

class AlternativeCoverage(BaseModel):
    """Alternative coverage option"""
    option_name: str = Field(..., description="Alternative option name")
    description: str = Field(..., description="Description of alternative")
    coverage_percentage: Optional[int] = Field(None, ge=0, le=100)
    additional_cost: Optional[float] = Field(None, ge=0)
    requirements: Optional[List[str]] = []

class ExclusionCheckRequest(BaseModel):
    """Request to check if exclusion applies"""
    context: Dict[str, Any] = Field(..., description="Context to check against")
    check_date: Optional[date] = Field(None, description="Date to check (default: today)")

class ExclusionCheckResponse(BaseModel):
    """Response for exclusion check"""
    exclusion_id: UUID
    applies: bool
    reason: str
    exception_found: bool
    alternative_options: List[AlternativeCoverage]

class PlanExclusionBase(BaseModel):
    """Base schema for Plan Exclusion"""
    exclusion_code: Optional[str] = Field(None, max_length=50)
    exclusion_type: ExclusionType = ExclusionType.GENERAL
    exclusion_category: ExclusionCategory = ExclusionCategory.CONDITION
    exclusion_severity: ExclusionSeverity = ExclusionSeverity.ABSOLUTE
    
    # Text descriptions
    exclusion_text: str = Field(..., min_length=10, max_length=2000)
    exclusion_text_ar: Optional[str] = Field(None, max_length=2000)
    member_facing_text: Optional[str] = Field(None, max_length=1000)
    member_facing_text_ar: Optional[str] = Field(None, max_length=1000)
    
    # Medical code references
    cpt_code_id: Optional[UUID] = None
    icd10_code_id: Optional[UUID] = None
    motor_code_id: Optional[UUID] = None
    
    # Conditions and exceptions
    exception_conditions: Optional[Dict[str, Any]] = {}
    waiver_conditions: Optional[Dict[str, Any]] = None
    alternative_coverage: Optional[Dict[str, Any]] = None
    
    # Dates and periods
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    waiting_period_days: Optional[int] = Field(None, ge=0)
    
    # Geographic and scope
    geographic_scope: Optional[Dict[str, Any]] = None
    provider_scope: Optional[Dict[str, Any]] = None
    
    # Regulatory
    regulatory_basis: RegulatoryBasis = RegulatoryBasis.COMPANY_POLICY
    regulatory_reference: Optional[str] = Field(None, max_length=200)
    compliance_notes: Optional[str] = None
    
    # Display
    display_order: int = Field(0, ge=0)
    is_highlighted: bool = False
    documentation_url: Optional[str] = Field(None, max_length=500)
    
    # Metadata
    notes: Optional[str] = None
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('expiry_date')
    def expiry_after_effective(cls, v, values):
        if v and 'effective_date' in values and values['effective_date']:
            if v <= values['effective_date']:
                raise ValueError('Expiry date must be after effective date')
        return v
    
    @validator('exclusion_text')
    def exclusion_text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Exclusion text cannot be empty')
        return v.strip()

class PlanExclusionCreate(PlanExclusionBase):
    """Create schema for Plan Exclusion"""
    pass

class PlanExclusionUpdate(BaseModel):
    """Update schema for Plan Exclusion"""
    exclusion_code: Optional[str] = Field(None, max_length=50)
    exclusion_type: Optional[ExclusionType] = None
    exclusion_category: Optional[ExclusionCategory] = None
    exclusion_severity: Optional[ExclusionSeverity] = None
    
    exclusion_text: Optional[str] = Field(None, min_length=10, max_length=2000)
    exclusion_text_ar: Optional[str] = Field(None, max_length=2000)
    member_facing_text: Optional[str] = Field(None, max_length=1000)
    member_facing_text_ar: Optional[str] = Field(None, max_length=1000)
    
    cpt_code_id: Optional[UUID] = None
    icd10_code_id: Optional[UUID] = None
    motor_code_id: Optional[UUID] = None
    
    exception_conditions: Optional[Dict[str, Any]] = None
    waiver_conditions: Optional[Dict[str, Any]] = None
    alternative_coverage: Optional[Dict[str, Any]] = None
    
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    waiting_period_days: Optional[int] = Field(None, ge=0)
    
    geographic_scope: Optional[Dict[str, Any]] = None
    provider_scope: Optional[Dict[str, Any]] = None
    
    regulatory_basis: Optional[RegulatoryBasis] = None
    regulatory_reference: Optional[str] = Field(None, max_length=200)
    compliance_notes: Optional[str] = None
    
    display_order: Optional[int] = Field(None, ge=0)
    is_highlighted: Optional[bool] = None
    documentation_url: Optional[str] = Field(None, max_length=500)
    
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class PlanExclusionResponse(PlanExclusionBase):
    """Response schema for Plan Exclusion"""
    id: UUID
    plan_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    # Computed fields
    is_waiverable: bool = False
    is_temporary: bool = False
    
    class Config:
        from_attributes = True

class BulkExclusionCreate(BaseModel):
    """Bulk create exclusions"""
    exclusions: List[PlanExclusionCreate] = Field(..., min_items=1, max_items=100)

class ExclusionSummary(BaseModel):
    """Summary of exclusions for a plan"""
    plan_id: UUID
    total_exclusions: int
    by_type: Dict[str, int]
    by_category: Dict[str, int]
    by_severity: Dict[str, int]
    highlighted_exclusions: int
    temporary_exclusions: int
    waiverable_exclusions: int

class ExclusionSearchFilters(BaseModel):
    """Search filters for exclusions"""
    exclusion_type: Optional[ExclusionType] = None
    exclusion_category: Optional[ExclusionCategory] = None
    exclusion_severity: Optional[ExclusionSeverity] = None
    is_highlighted: Optional[bool] = None
    effective_date: Optional[date] = None
    text_search: Optional[str] = None
    tags: Optional[List[str]] = None