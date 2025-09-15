# app/modules/pricing/profiles/schemas/quotation_pricing_history_schema.py

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID
from enum import Enum

# Import the enums we need (avoid circular imports by importing only what we need)
from .quotation_pricing_profile_schema import InsuranceType, ProfileStatus, CurrencyCode

# History operation types
class HistoryOperation(str, Enum):
    """Types of history operations"""
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ARCHIVE = "ARCHIVE"
    ACTIVATE = "ACTIVATE"
    DEACTIVATE = "DEACTIVATE"

# Profile history schemas
class QuotationPricingProfileHistoryBase(BaseModel):
    """Base schema for profile history entries"""
    
    profile_id: UUID = Field(..., description="Profile ID this history entry belongs to")
    operation: HistoryOperation = Field(..., description="Type of operation performed")
    changed_at: datetime = Field(..., description="When the change occurred")
    changed_by: Optional[str] = Field(None, description="User who made the change")
    old_data: Optional[Dict[str, Any]] = Field(None, description="Data before change")
    new_data: Dict[str, Any] = Field(..., description="Data after change")

class QuotationPricingProfileHistoryResponse(QuotationPricingProfileHistoryBase):
    """Schema for profile history responses"""
    
    history_id: UUID = Field(..., description="History entry unique identifier")

    model_config = ConfigDict(from_attributes=True)

# Rules history schemas
class QuotationPricingRulesHistoryBase(BaseModel):
    """Base schema for rules history entries"""
    
    rule_id: UUID = Field(..., description="Rule ID this history entry belongs to")
    operation: HistoryOperation = Field(..., description="Type of operation performed")
    changed_at: datetime = Field(..., description="When the change occurred")
    changed_by: Optional[str] = Field(None, description="User who made the change")
    old_data: Optional[Dict[str, Any]] = Field(None, description="Data before change")
    new_data: Dict[str, Any] = Field(..., description="Data after change")

class QuotationPricingRulesHistoryResponse(QuotationPricingRulesHistoryBase):
    """Schema for rules history responses"""
    
    history_id: UUID = Field(..., description="History entry unique identifier")

    model_config = ConfigDict(from_attributes=True)

# Analytics schemas
class PricingProfileAnalytics(BaseModel):
    """Analytics data for pricing profiles"""
    
    total_profiles: int = Field(..., description="Total number of profiles")
    active_profiles: int = Field(..., description="Number of active profiles")
    draft_profiles: int = Field(..., description="Number of draft profiles")
    archived_profiles: int = Field(..., description="Number of archived profiles")
    profiles_by_insurance_type: Dict[str, int] = Field(..., description="Profile count by insurance type")
    average_base_premium: Decimal = Field(..., description="Average base premium across profiles")
    premium_range_distribution: Dict[str, int] = Field(..., description="Distribution of premium ranges")
    recently_created: int = Field(..., description="Profiles created in last 30 days")
    recently_updated: int = Field(..., description="Profiles updated in last 30 days")

class PricingRuleAnalytics(BaseModel):
    """Analytics data for pricing rules"""
    
    total_rules: int = Field(..., description="Total number of rules")
    active_rules: int = Field(..., description="Number of active rules")
    inactive_rules: int = Field(..., description="Number of inactive rules")
    rules_by_type: Dict[str, int] = Field(..., description="Rule count by type")
    rules_by_insurance_type: Dict[str, int] = Field(..., description="Rule count by insurance type")
    average_adjustment_value: Optional[Decimal] = Field(None, description="Average adjustment value")
    rules_with_formulas: int = Field(..., description="Number of rules using formulas")
    recently_created: int = Field(..., description="Rules created in last 30 days")
    recently_updated: int = Field(..., description="Rules updated in last 30 days")

# Search parameter schemas
class PricingProfileSearchParams(BaseModel):
    """Schema for pricing profile search parameters"""
    
    name: Optional[str] = Field(None, description="Search by profile name")
    insurance_type: Optional[str] = Field(None, description="Filter by insurance type")
    status: Optional[str] = Field(None, description="Filter by status")
    currency: Optional[str] = Field(None, description="Filter by currency")
    min_base_premium: Optional[Decimal] = Field(None, description="Minimum base premium")
    max_base_premium: Optional[Decimal] = Field(None, description="Maximum base premium")
    created_after: Optional[date] = Field(None, description="Created after date")
    created_before: Optional[date] = Field(None, description="Created before date")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=1, le=100, description="Page size")
    
    # Sorting
    sort_by: Optional[str] = Field(default="created_at", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", description="Sort order")

    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v):
        """Validate sort order"""
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be either "asc" or "desc"')
        return v

class PricingRuleSearchParams(BaseModel):
    """Schema for pricing rule search parameters"""
    
    rule_name: Optional[str] = Field(None, description="Search by rule name")
    insurance_type: Optional[str] = Field(None, description="Filter by insurance type")
    rule_type: Optional[str] = Field(None, description="Filter by rule type")
    adjustment_type: Optional[str] = Field(None, description="Filter by adjustment type")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    min_priority: Optional[int] = Field(None, description="Minimum priority")
    max_priority: Optional[int] = Field(None, description="Maximum priority")
    effective_after: Optional[date] = Field(None, description="Effective after date")
    effective_before: Optional[date] = Field(None, description="Effective before date")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=1, le=100, description="Page size")
    
    # Sorting
    sort_by: Optional[str] = Field(default="priority", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", description="Sort order")

    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v):
        """Validate sort order"""
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be either "asc" or "desc"')
        return v

# Import/Export schemas
class PricingDataExport(BaseModel):
    """Schema for pricing data export"""
    
    include_profiles: bool = Field(default=True, description="Include pricing profiles")
    include_rules: bool = Field(default=True, description="Include pricing rules")
    include_history: bool = Field(default=False, description="Include history data")
    insurance_types: Optional[List[str]] = Field(None, description="Filter by insurance types")
    date_from: Optional[date] = Field(None, description="Export data from date")
    date_to: Optional[date] = Field(None, description="Export data to date")
    format: str = Field(default="json", description="Export format")

    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        """Validate export format"""
        if v not in ['json', 'csv', 'xlsx']:
            raise ValueError('format must be one of: json, csv, xlsx')
        return v

class PricingDataImport(BaseModel):
    """Schema for pricing data import"""
    
    data_type: str = Field(..., description="Type of data to import")
    file_format: str = Field(..., description="File format")
    validate_only: bool = Field(default=False, description="Only validate without importing")
    overwrite_existing: bool = Field(default=False, description="Overwrite existing records")
    import_rules_with_profiles: bool = Field(default=True, description="Import associated rules with profiles")

    @field_validator('data_type')
    @classmethod
    def validate_data_type(cls, v):
        """Validate data type"""
        if v not in ['profiles', 'rules', 'both']:
            raise ValueError('data_type must be one of: profiles, rules, both')
        return v

    @field_validator('file_format')
    @classmethod
    def validate_file_format(cls, v):
        """Validate file format"""
        if v not in ['json', 'csv', 'xlsx']:
            raise ValueError('file_format must be one of: json, csv, xlsx')
        return v

# Premium calculation schemas
class PremiumCalculationRequest(BaseModel):
    """Schema for premium calculation requests"""
    
    profile_id: UUID = Field(..., description="Pricing profile to use")
    customer_data: Dict[str, Any] = Field(..., description="Customer information")
    coverage_data: Dict[str, Any] = Field(..., description="Coverage information")
    additional_factors: Optional[Dict[str, Any]] = Field(None, description="Additional pricing factors")
    apply_all_rules: bool = Field(default=True, description="Apply all applicable rules")
    selected_rules: Optional[List[UUID]] = Field(None, description="Specific rules to apply")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "customer_data": {
                    "age": 28,
                    "gender": "M",
                    "location": "Riyadh",
                    "driving_experience": 5
                },
                "coverage_data": {
                    "vehicle_value": 75000,
                    "vehicle_type": "sedan",
                    "vehicle_age": 2,
                    "coverage_type": "comprehensive"
                },
                "additional_factors": {
                    "no_claims_discount": True,
                    "security_features": ["alarm", "gps"]
                },
                "apply_all_rules": True
            }
        }
    )

class PremiumCalculationResponse(BaseModel):
    """Schema for premium calculation responses"""
    
    profile_id: UUID = Field(..., description="Used pricing profile ID")
    profile_name: str = Field(..., description="Profile name")
    base_premium: Decimal = Field(..., description="Base premium amount")
    total_premium: Decimal = Field(..., description="Final calculated premium")
    currency: str = Field(..., description="Currency code")
    
    # Calculation breakdown
    applied_rules: List[Dict[str, Any]] = Field(..., description="Rules that were applied")
    rule_adjustments: List[Dict[str, Any]] = Field(..., description="Individual rule adjustments")
    total_adjustments: Decimal = Field(..., description="Total adjustments amount")
    adjustment_percentage: Decimal = Field(..., description="Total adjustment as percentage")
    
    # Validation
    within_bounds: bool = Field(..., description="Whether result is within profile bounds")
    min_premium_applied: bool = Field(..., description="Whether minimum premium was applied")
    max_premium_applied: bool = Field(..., description="Whether maximum premium was applied")
    
    # Metadata
    calculation_id: UUID = Field(..., description="Unique calculation identifier")
    calculated_at: datetime = Field(..., description="Calculation timestamp")
    calculation_duration_ms: int = Field(..., description="Calculation time in milliseconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "profile_name": "Standard Motor Insurance Profile",
                "base_premium": 1500.00,
                "total_premium": 1725.00,
                "currency": "SAR",
                "applied_rules": [
                    {
                        "rule_id": "456e7890-1ab2-34c5-d678-901234567890",
                        "rule_name": "Age Loading",
                        "adjustment_value": 15.0,
                        "adjustment_type": "PERCENTAGE"
                    }
                ],
                "rule_adjustments": [
                    {
                        "rule_name": "Age Loading",
                        "original_value": 1500.00,
                        "adjustment_amount": 225.00,
                        "adjusted_value": 1725.00
                    }
                ],
                "total_adjustments": 225.00,
                "adjustment_percentage": 15.0,
                "within_bounds": True,
                "min_premium_applied": False,
                "max_premium_applied": False,
                "calculation_id": "789abc12-3def-4567-8901-234567890abc",
                "calculated_at": "2024-01-15T10:30:00Z",
                "calculation_duration_ms": 45
            }
        }
    )