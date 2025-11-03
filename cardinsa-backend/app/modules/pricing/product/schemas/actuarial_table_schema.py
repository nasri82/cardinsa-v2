# app/modules/pricing/product/schemas/actuarial_table_schema.py

"""
Actuarial Table Schema

Pydantic schemas for Actuarial Table validation and serialization.
Handles mortality, morbidity, and other actuarial data tables.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal


# ================================================================
# ENUMS
# ================================================================

class TableType(str, Enum):
    """Actuarial table type enumeration"""
    MORTALITY = "mortality"
    MORBIDITY = "morbidity"
    LAPSE = "lapse"
    DISABILITY = "disability"
    ANNUITY = "annuity"
    EXPERIENCE = "experience"
    COMMISSION = "commission"
    EXPENSE = "expense"
    INTEREST = "interest"
    CUSTOM = "custom"


class TableStatus(str, Enum):
    """Table status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class TableSource(str, Enum):
    """Table source enumeration"""
    INDUSTRY = "industry"
    REGULATORY = "regulatory"
    COMPANY = "company"
    REINSURER = "reinsurer"
    GOVERNMENT = "government"
    CUSTOM = "custom"


class Gender(str, Enum):
    """Gender enumeration for actuarial tables"""
    MALE = "male"
    FEMALE = "female"
    UNISEX = "unisex"
    OTHER = "other"


class SmokingStatus(str, Enum):
    """Smoking status enumeration"""
    SMOKER = "smoker"
    NON_SMOKER = "non_smoker"
    PREFERRED = "preferred"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


# ================================================================
# BASE SCHEMAS
# ================================================================

class ActuarialTableBase(BaseModel):
    """Base schema for actuarial tables"""
    
    model_config = ConfigDict(from_attributes=True)
    
    table_code: str = Field(..., min_length=1, max_length=50, description="Unique table code")
    table_name: str = Field(..., min_length=1, max_length=200, description="Table name")
    description: Optional[str] = Field(None, description="Table description")
    
    table_type: TableType = Field(..., description="Type of actuarial table")
    table_source: TableSource = Field(..., description="Source of table data")
    
    # Version Information
    version: str = Field(..., min_length=1, max_length=20, description="Table version")
    base_year: int = Field(..., ge=1900, le=2100, description="Base year for table")
    
    # Coverage
    country: Optional[str] = Field(None, max_length=2, description="Country code (ISO)")
    region: Optional[str] = Field(None, max_length=100, description="Region/State")
    
    # Demographics
    gender_specific: bool = Field(default=False, description="Is gender-specific")
    smoking_specific: bool = Field(default=False, description="Is smoking-specific")
    
    # Age Range
    min_age: int = Field(0, ge=0, le=150, description="Minimum age in table")
    max_age: int = Field(120, ge=0, le=150, description="Maximum age in table")
    
    # Data Structure
    data_columns: List[str] = Field(
        default_factory=list,
        description="Column names in table data"
    )
    
    @field_validator('table_code')
    @classmethod
    def validate_table_code(cls, v: str) -> str:
        """Validate table code format"""
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError("Table code can only contain letters, numbers, hyphens, and underscores")
        return v.upper()
    
    @field_validator('max_age')
    @classmethod
    def validate_age_range(cls, v: int, values) -> int:
        """Validate age range"""
        if 'min_age' in values.data:
            min_age = values.data.get('min_age')
            if v < min_age:
                raise ValueError("Maximum age must be greater than or equal to minimum age")
        return v
    
    @field_validator('country')
    @classmethod
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate country code format"""
        if v is not None:
            if len(v) != 2 or not v.isalpha():
                raise ValueError("Country code must be 2-letter ISO code")
            return v.upper()
        return v


# ================================================================
# TABLE DATA SCHEMAS
# ================================================================

class ActuarialDataRow(BaseModel):
    """Schema for a single row of actuarial data"""
    
    model_config = ConfigDict(from_attributes=True)
    
    age: int = Field(..., ge=0, le=150, description="Age")
    gender: Optional[Gender] = Field(None, description="Gender")
    smoking_status: Optional[SmokingStatus] = Field(None, description="Smoking status")
    
    # Rates (as decimals, e.g., 0.001 for 0.1%)
    rate: Decimal = Field(..., ge=0, le=1, decimal_places=6, description="Primary rate")
    rate_male: Optional[Decimal] = Field(None, ge=0, le=1, decimal_places=6)
    rate_female: Optional[Decimal] = Field(None, ge=0, le=1, decimal_places=6)
    rate_smoker: Optional[Decimal] = Field(None, ge=0, le=1, decimal_places=6)
    rate_non_smoker: Optional[Decimal] = Field(None, ge=0, le=1, decimal_places=6)
    
    # Additional factors
    improvement_factor: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=6,
        description="Improvement factor"
    )
    selection_factor: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=6,
        description="Selection factor"
    )
    
    # Custom data
    additional_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional data columns"
    )


# ================================================================
# CREATE SCHEMA
# ================================================================

class ActuarialTableCreate(ActuarialTableBase):
    """Schema for creating an actuarial table"""
    
    # Table Data
    table_data: List[ActuarialDataRow] = Field(
        ...,
        min_length=1,
        description="Actuarial table data rows"
    )
    
    # Metadata
    table_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional table metadata"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Table tags"
    )
    
    # Regulatory Information
    regulatory_approval: Optional[str] = Field(None, description="Regulatory approval reference")
    approval_date: Optional[date] = Field(None, description="Approval date")
    
    # Validity Period
    effective_date: Optional[date] = Field(None, description="Effective date")
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    
    # Notes
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @field_validator('table_data')
    @classmethod
    def validate_table_data(cls, v: List[ActuarialDataRow]) -> List[ActuarialDataRow]:
        """Validate table data consistency"""
        if not v:
            raise ValueError("Table data cannot be empty")
        
        # Check for duplicate ages (if not gender/smoking specific)
        ages_seen = set()
        for row in v:
            if row.age in ages_seen:
                # Could be valid if gender/smoking specific
                pass
            ages_seen.add(row.age)
        
        return v
    
    @field_validator('expiry_date')
    @classmethod
    def validate_dates(cls, v: Optional[date], values) -> Optional[date]:
        """Validate date range"""
        if v is not None and 'effective_date' in values.data:
            effective = values.data.get('effective_date')
            if effective is not None and v <= effective:
                raise ValueError("Expiry date must be after effective date")
        return v


# ================================================================
# UPDATE SCHEMA
# ================================================================

class ActuarialTableUpdate(BaseModel):
    """Schema for updating an actuarial table"""
    
    model_config = ConfigDict(from_attributes=True)
    
    table_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    table_source: Optional[TableSource] = None
    
    # Version Information
    version: Optional[str] = Field(None, min_length=1, max_length=20)
    
    # Coverage
    country: Optional[str] = Field(None, max_length=2)
    region: Optional[str] = Field(None, max_length=100)
    
    # Table Data (complete replacement if provided)
    table_data: Optional[List[ActuarialDataRow]] = Field(None, min_length=1)
    
    # Metadata
    table_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    # Regulatory Information
    regulatory_approval: Optional[str] = None
    approval_date: Optional[date] = None
    
    # Validity Period
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    # Notes
    notes: Optional[str] = None
    
    # Status
    status: Optional[TableStatus] = None


# ================================================================
# RESPONSE SCHEMAS
# ================================================================

class ActuarialTableResponse(ActuarialTableBase):
    """Response schema for actuarial table"""
    
    id: UUID = Field(..., description="Table ID")
    
    table_data: List[ActuarialDataRow] = Field(..., description="Table data")
    
    table_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
    
    regulatory_approval: Optional[str] = None
    approval_date: Optional[date] = None
    
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    notes: Optional[str] = None
    status: TableStatus = Field(..., description="Table status")
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool = Field(default=False)


class ActuarialTableListResponse(BaseModel):
    """Response schema for actuarial table list"""
    
    model_config = ConfigDict(from_attributes=True)
    
    tables: List[ActuarialTableResponse] = Field(..., description="List of tables")
    total_count: int = Field(..., ge=0, description="Total count")
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, le=100, description="Page size")
    total_pages: int = Field(..., ge=0, description="Total pages")


# ================================================================
# FILTER SCHEMAS
# ================================================================

class ActuarialTableFilter(BaseModel):
    """Filter schema for actuarial tables"""
    
    model_config = ConfigDict(from_attributes=True)
    
    table_type: Optional[TableType] = None
    table_source: Optional[TableSource] = None
    status: Optional[TableStatus] = None
    
    country: Optional[str] = Field(None, max_length=2)
    region: Optional[str] = None
    
    gender_specific: Optional[bool] = None
    smoking_specific: Optional[bool] = None
    
    base_year_from: Optional[int] = Field(None, ge=1900)
    base_year_to: Optional[int] = Field(None, le=2100)
    
    search_term: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[List[str]] = None
    
    effective_date_from: Optional[date] = None
    effective_date_to: Optional[date] = None


# ================================================================
# CALCULATION SCHEMAS
# ================================================================

class ActuarialCalculationRequest(BaseModel):
    """Request schema for actuarial calculations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    table_id: UUID = Field(..., description="Actuarial table ID")
    age: int = Field(..., ge=0, le=150, description="Age for calculation")
    gender: Optional[Gender] = Field(None, description="Gender")
    smoking_status: Optional[SmokingStatus] = Field(None, description="Smoking status")
    
    # Calculation parameters
    sum_insured: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Sum insured amount"
    )
    term_years: Optional[int] = Field(None, ge=1, description="Term in years")
    interest_rate: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=1, 
        decimal_places=4,
        description="Interest rate"
    )
    
    # Adjustments
    apply_improvement: bool = Field(default=True, description="Apply improvement factors")
    apply_selection: bool = Field(default=False, description="Apply selection factors")
    additional_loading: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=4,
        description="Additional loading factor"
    )


class ActuarialCalculationResponse(BaseModel):
    """Response schema for actuarial calculations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    table_id: UUID
    base_rate: Decimal = Field(..., description="Base rate from table")
    adjusted_rate: Decimal = Field(..., description="Adjusted rate after factors")
    
    # Calculated values
    annual_premium: Optional[Decimal] = Field(None, description="Annual premium")
    monthly_premium: Optional[Decimal] = Field(None, description="Monthly premium")
    net_premium: Optional[Decimal] = Field(None, description="Net premium")
    gross_premium: Optional[Decimal] = Field(None, description="Gross premium")
    
    # Present values
    present_value: Optional[Decimal] = Field(None, description="Present value")
    reserve_amount: Optional[Decimal] = Field(None, description="Reserve amount")
    
    # Details
    calculation_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed calculation breakdown"
    )
    factors_applied: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Factors applied in calculation"
    )


# ================================================================
# IMPORT/EXPORT SCHEMAS
# ================================================================

class ActuarialTableImport(BaseModel):
    """Schema for importing actuarial tables"""
    
    model_config = ConfigDict(from_attributes=True)
    
    format: str = Field(
        ...,
        pattern="^(csv|excel|json|xml)$",
        description="Import format"
    )
    data: Union[str, bytes] = Field(..., description="Import data")
    mapping: Optional[Dict[str, str]] = Field(
        None,
        description="Column mapping configuration"
    )
    validate_only: bool = Field(
        default=False,
        description="Only validate without importing"
    )


class ActuarialTableExport(BaseModel):
    """Schema for exporting actuarial tables"""
    
    model_config = ConfigDict(from_attributes=True)
    
    table_ids: List[UUID] = Field(
        ...,
        min_length=1,
        description="Table IDs to export"
    )
    format: str = Field(
        default="excel",
        pattern="^(csv|excel|json|xml|pdf)$",
        description="Export format"
    )
    include_metadata: bool = Field(
        default=True,
        description="Include metadata in export"
    )


# ================================================================
# END OF SCHEMA
# ================================================================