# app/modules/pricing/profiles/schemas/quotation_pricing_profile_schema.py

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from enum import Enum

# Enums for validation
class InsuranceType(str, Enum):
    MEDICAL = "Medical"
    MOTOR = "Motor" 
    LIFE = "Life"
    PROPERTY = "Property"
    TRAVEL = "Travel"
    LIABILITY = "Liability"

class ProfileStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"

class CurrencyCode(str, Enum):
    SAR = "SAR"
    USD = "USD"
    EUR = "EUR"
    AED = "AED"

# Base schema with common fields
class QuotationPricingProfileBase(BaseModel):
    """Base schema for pricing profile with common validation"""
    
    name: str = Field(..., min_length=1, max_length=255, description="Profile name")
    description: Optional[str] = Field(None, max_length=1000, description="Profile description")
    insurance_type: InsuranceType = Field(..., description="Type of insurance")
    base_premium: Decimal = Field(..., gt=0, description="Base premium amount")
    min_premium: Decimal = Field(..., gt=0, description="Minimum allowed premium")
    max_premium: Decimal = Field(..., gt=0, description="Maximum allowed premium") 
    currency: CurrencyCode = Field(default=CurrencyCode.SAR, description="Currency code")
    status: ProfileStatus = Field(default=ProfileStatus.DRAFT, description="Profile status")
    effective_date: Optional[datetime] = Field(None, description="When profile becomes effective")

    @field_validator('max_premium')
    @classmethod
    def validate_premium_bounds(cls, v, info):
        """Ensure max_premium >= min_premium"""
        min_premium = info.data.get('min_premium')
        if min_premium and v < min_premium:
            raise ValueError('max_premium must be greater than or equal to min_premium')
        return v

    @field_validator('base_premium')
    @classmethod 
    def validate_base_premium_within_bounds(cls, v, info):
        """Ensure base_premium is within min/max bounds"""
        min_premium = info.data.get('min_premium')
        max_premium = info.data.get('max_premium')
        
        if min_premium and v < min_premium:
            raise ValueError('base_premium cannot be less than min_premium')
        if max_premium and v > max_premium:
            raise ValueError('base_premium cannot be greater than max_premium')
        return v

# Create schema
class QuotationPricingProfileCreate(QuotationPricingProfileBase):
    """Schema for creating a new pricing profile"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Standard Motor Insurance Profile",
                "description": "Basic motor insurance pricing for vehicles under 5 years",
                "insurance_type": "Motor",
                "base_premium": 1500.00,
                "min_premium": 800.00,
                "max_premium": 5000.00,
                "currency": "SAR",
                "status": "DRAFT",
                "effective_date": "2024-01-01T00:00:00Z"
            }
        }
    )

# Update schema
class QuotationPricingProfileUpdate(BaseModel):
    """Schema for updating an existing pricing profile"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    insurance_type: Optional[InsuranceType] = None
    base_premium: Optional[Decimal] = Field(None, gt=0)
    min_premium: Optional[Decimal] = Field(None, gt=0)
    max_premium: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[CurrencyCode] = None
    status: Optional[ProfileStatus] = None
    effective_date: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Motor Insurance Profile",
                "base_premium": 1600.00,
                "status": "ACTIVE"
            }
        }
    )

# Response schema
class QuotationPricingProfileResponse(QuotationPricingProfileBase):
    """Schema for pricing profile responses"""
    
    id: UUID = Field(..., description="Profile unique identifier")
    uuid: UUID = Field(..., description="Profile secondary UUID for external references")
    version: int = Field(..., description="Profile version number")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="Creator user ID")
    updated_by: Optional[UUID] = Field(None, description="Last updater user ID")
    archived_at: Optional[datetime] = Field(None, description="Archive timestamp")

    # Computed properties
    is_active: bool = Field(..., description="Whether profile is currently active")
    premium_range_display: str = Field(..., description="Formatted premium range")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "uuid": "987fcdeb-51a2-43d1-9f12-345678901234", 
                "name": "Standard Motor Insurance Profile",
                "description": "Basic motor insurance pricing for vehicles under 5 years",
                "insurance_type": "Motor",
                "base_premium": 1500.00,
                "min_premium": 800.00,
                "max_premium": 5000.00,
                "currency": "SAR",
                "status": "ACTIVE",
                "version": 1,
                "effective_date": "2024-01-01T00:00:00Z",
                "created_at": "2024-01-01T10:30:00Z",
                "updated_at": "2024-01-15T14:20:00Z",
                "created_by": "456e7890-1ab2-34c5-d678-901234567890",
                "updated_by": "456e7890-1ab2-34c5-d678-901234567890",
                "archived_at": None,
                "is_active": True,
                "premium_range_display": "SAR 800.00 - 5,000.00"
            }
        }
    )

# Summary schema for lists
class QuotationPricingProfileSummary(BaseModel):
    """Lightweight schema for profile lists and summaries"""
    
    id: UUID
    uuid: UUID
    name: str
    insurance_type: InsuranceType
    base_premium: Decimal
    currency: CurrencyCode
    status: ProfileStatus
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Bulk operations schema
class QuotationPricingProfileBulkCreate(BaseModel):
    """Schema for creating multiple pricing profiles"""
    
    profiles: List[QuotationPricingProfileCreate] = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="List of profiles to create"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profiles": [
                    {
                        "name": "Basic Motor Profile",
                        "insurance_type": "Motor",
                        "base_premium": 1500.00,
                        "min_premium": 800.00,
                        "max_premium": 3000.00,
                        "currency": "SAR"
                    },
                    {
                        "name": "Premium Motor Profile", 
                        "insurance_type": "Motor",
                        "base_premium": 2500.00,
                        "min_premium": 1500.00,
                        "max_premium": 6000.00,
                        "currency": "SAR"
                    }
                ]
            }
        }
    )

# Status update schema
class QuotationPricingProfileStatusUpdate(BaseModel):
    """Schema for profile status changes"""
    
    status: ProfileStatus = Field(..., description="New profile status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")
    effective_date: Optional[datetime] = Field(None, description="When status change takes effect")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ACTIVE",
                "reason": "Profile review completed, approved for production use",
                "effective_date": "2024-01-01T00:00:00Z"
            }
        }
    )

# Profile validation schema
class QuotationPricingProfileValidation(BaseModel):
    """Schema for profile validation results"""
    
    is_valid: bool = Field(..., description="Whether profile passes validation")
    errors: List[str] = Field(default_factory=list, description="Validation error messages")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_valid": False,
                "errors": [
                    "Base premium exceeds maximum allowed for Motor insurance",
                    "Missing required rules for age brackets"
                ],
                "warnings": [
                    "Premium range is very wide, consider tighter bounds"
                ],
                "suggestions": [
                    "Add age-specific rules for better pricing accuracy",
                    "Consider regional pricing adjustments"
                ]
            }
        }
    )

# Profile with rules schema
class QuotationPricingProfileWithRules(QuotationPricingProfileResponse):
    """Schema for profile with associated rules"""
    
    rules_count: int = Field(..., description="Number of associated rules")
    active_rules_count: int = Field(..., description="Number of active rules")
    
    model_config = ConfigDict(from_attributes=True)

# Convenience aliases for backward compatibility and shorter imports
PricingProfileBase = QuotationPricingProfileBase
PricingProfileCreate = QuotationPricingProfileCreate
PricingProfileUpdate = QuotationPricingProfileUpdate
PricingProfileResponse = QuotationPricingProfileResponse
PricingProfileSummary = QuotationPricingProfileSummary
PricingProfileBulkCreate = QuotationPricingProfileBulkCreate
PricingProfileStatusUpdate = QuotationPricingProfileStatusUpdate
PricingProfileValidation = QuotationPricingProfileValidation
PricingProfileWithRules = QuotationPricingProfileWithRules