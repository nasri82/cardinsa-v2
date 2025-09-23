# app/modules/providers/schemas/provider_service_price_schema.py

"""
Provider Service Price Schema - Pydantic v2 Compatible
======================================================

Fixed implementation using Pydantic v2 syntax with simplified validation.
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum


class CurrencyEnum(str, Enum):
    """Supported currency enumeration"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"


class ProviderServicePriceBase(BaseModel):
    """Base schema with common service price fields"""
    
    provider_id: UUID = Field(
        ...,
        description="Reference to the provider",
        examples=["789e0123-e89b-12d3-a456-426614174000"]
    )
    
    service_tag: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r'^[A-Z0-9_]+$',
        description="Service identifier/code (uppercase letters, numbers, underscores)",
        examples=["CONSULTATION_GENERAL"]
    )
    
    price: Decimal = Field(
        ...,
        gt=0,
        description="Service price (must be positive)",
        examples=[150.00]
    )
    
    currency: CurrencyEnum = Field(
        CurrencyEnum.USD,
        description="Currency code",
        examples=["USD"]
    )
    
    is_discounted: bool = Field(
        False,
        description="Whether this price includes a discount",
        examples=[False]
    )
    
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional notes about pricing or service terms",
        examples=["Includes basic consultation and initial assessment"]
    )
    
    is_active: bool = Field(
        True,
        description="Whether this price is currently active and available",
        examples=[True]
    )
    
    @field_validator('service_tag')
    @classmethod
    def validate_service_tag_format(cls, v: str) -> str:
        """Ensure service tag follows business rules"""
        if not v:
            raise ValueError('Service tag is required')
        
        v = v.upper().strip()
        
        # Check for reasonable length
        if len(v) > 50:
            raise ValueError('Service tag should not exceed 50 characters for readability')
        
        # Check for meaningful content
        if len(v) < 3:
            raise ValueError('Service tag should be at least 3 characters')
        
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price_amount(cls, v: Decimal) -> Decimal:
        """Validate price is reasonable"""
        if v <= 0:
            raise ValueError('Price must be positive')
        
        # Check for reasonable upper limit (adjust based on business needs)
        if v > 100000:
            raise ValueError('Price exceeds maximum allowed amount (100,000)')
        
        return v


class ProviderServicePriceCreate(ProviderServicePriceBase):
    """Schema for creating new service prices"""
    
    # Optional fields for creation
    service_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Human-readable service name",
        examples=["General Medical Consultation"]
    )
    
    service_description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed description of the service",
        examples=["Comprehensive general medical consultation including examination and assessment"]
    )
    
    # Discount information (if applicable)
    original_price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Original price before discount (if discounted)",
        examples=[200.00]
    )
    
    discount_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Discount percentage (0-100)",
        examples=[25.00]
    )
    
    discount_reason: Optional[str] = Field(
        None,
        max_length=100,
        description="Reason for discount",
        examples=["network_agreement"]
    )
    
    # Service categorization
    service_category: Optional[str] = Field(
        None,
        max_length=50,
        description="Service category for grouping",
        examples=["consultation"]
    )
    
    @field_validator('original_price')
    @classmethod
    def validate_original_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate original price if provided"""
        if v is not None and v <= 0:
            raise ValueError('Original price must be positive')
        return v
    
    @model_validator(mode='after')
    def validate_discount_logic(self):
        """Validate discount-related fields"""
        if self.is_discounted:
            if not self.original_price:
                raise ValueError('Original price required for discounted items')
            if not self.discount_percentage:
                raise ValueError('Discount percentage required for discounted items')
            
            # Validate that original price is greater than current price
            if self.original_price <= self.price:
                raise ValueError('Original price must be greater than current price for discounted items')
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider_id": "789e0123-e89b-12d3-a456-426614174000",
                "service_tag": "CONSULTATION_GENERAL",
                "service_name": "General Medical Consultation",
                "service_description": "Comprehensive general medical consultation including examination",
                "price": 150.00,
                "currency": "USD",
                "is_discounted": True,
                "original_price": 200.00,
                "discount_percentage": 25.00,
                "discount_reason": "network_agreement",
                "service_category": "consultation",
                "is_active": True
            }
        }
    )


class ProviderServicePriceUpdate(BaseModel):
    """Schema for updating service prices"""
    
    # Only allow updating specific fields
    price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Updated service price"
    )
    
    currency: Optional[CurrencyEnum] = Field(
        None,
        description="Updated currency"
    )
    
    is_discounted: Optional[bool] = Field(
        None,
        description="Updated discount status"
    )
    
    original_price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Updated original price"
    )
    
    discount_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Updated discount percentage"
    )
    
    discount_reason: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated discount reason"
    )
    
    service_category: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated service category"
    )
    
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated notes"
    )
    
    is_active: Optional[bool] = Field(
        None,
        description="Updated active status"
    )
    
    # Reuse validators from base class
    @field_validator('price')
    @classmethod
    def validate_price_update(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            return ProviderServicePriceBase.validate_price_amount(v)
        return v
    
    @model_validator(mode='after')
    def validate_update_data(self):
        """Validate update data"""
        values = self.model_dump(exclude_unset=True)
        if not values:
            raise ValueError('At least one field must be provided for update')
        
        # Validate discount logic if discount fields are being updated
        if self.is_discounted is True:
            if self.original_price is None and self.discount_percentage is None:
                raise ValueError('Original price and discount percentage required when setting discounted=true')
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "price": 175.00,
                "discount_percentage": 20.00,
                "notes": "Updated pricing for 2024",
                "is_active": True
            }
        }
    )


class ProviderServicePriceOut(ProviderServicePriceBase):
    """Schema for service price output/response"""
    
    id: UUID = Field(..., description="Unique identifier")
    
    # Extended fields
    service_name: Optional[str] = Field(None, description="Service name")
    service_description: Optional[str] = Field(None, description="Service description")
    original_price: Optional[Decimal] = Field(None, description="Original price before discount")
    discount_percentage: Optional[Decimal] = Field(None, description="Discount percentage")
    discount_reason: Optional[str] = Field(None, description="Discount reason")
    service_category: Optional[str] = Field(None, description="Service category")
    
    # Audit fields
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="User who created this record")
    updated_by: Optional[UUID] = Field(None, description="User who last updated this record")
    archived_at: Optional[datetime] = Field(None, description="Archive timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v) if v else None,
            Decimal: lambda v: float(v) if v else None
        },
        json_schema_extra={
            "example": {
                "id": "def45678-e89b-12d3-a456-426614174000",
                "provider_id": "789e0123-e89b-12d3-a456-426614174000",
                "service_tag": "CONSULTATION_GENERAL",
                "service_name": "General Medical Consultation",
                "price": 150.00,
                "currency": "USD",
                "is_discounted": True,
                "original_price": 200.00,
                "discount_percentage": 25.00,
                "discount_reason": "network_agreement",
                "service_category": "consultation",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z"
            }
        }
    )


class ProviderServicePriceList(BaseModel):
    """Schema for service price list items (minimal data)"""
    
    id: UUID = Field(..., description="Unique identifier")
    provider_id: UUID = Field(..., description="Provider ID")
    service_tag: str = Field(..., description="Service tag")
    service_name: Optional[str] = Field(None, description="Service name")
    price: Decimal = Field(..., description="Current price")
    currency: str = Field(..., description="Currency")
    is_discounted: bool = Field(..., description="Is discounted")
    service_category: Optional[str] = Field(None, description="Category")
    is_active: bool = Field(..., description="Active status")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: lambda v: float(v) if v else None
        },
        json_schema_extra={
            "example": {
                "id": "def45678-e89b-12d3-a456-426614174000",
                "provider_id": "789e0123-e89b-12d3-a456-426614174000",
                "service_tag": "CONSULTATION_GENERAL",
                "service_name": "General Medical Consultation",
                "price": 150.00,
                "currency": "USD",
                "is_discounted": True,
                "service_category": "consultation",
                "is_active": True
            }
        }
    )


class ProviderServicePriceSearch(BaseModel):
    """Schema for service price search/filter parameters"""
    
    provider_id: Optional[UUID] = Field(
        None,
        description="Filter by provider ID"
    )
    
    service_tag: Optional[str] = Field(
        None,
        max_length=100,
        description="Filter by service tag (exact match or starts with)"
    )
    
    service_category: Optional[str] = Field(
        None,
        max_length=50,
        description="Filter by service category"
    )
    
    currency: Optional[CurrencyEnum] = Field(
        None,
        description="Filter by currency"
    )
    
    min_price: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Minimum price filter"
    )
    
    max_price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Maximum price filter"
    )
    
    is_discounted: Optional[bool] = Field(
        None,
        description="Filter by discount status"
    )
    
    is_active: Optional[bool] = Field(
        None,
        description="Filter by active status"
    )
    
    # Text search
    search: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Search in service tag, name, and description"
    )
    
    @field_validator('max_price')
    @classmethod
    def validate_price_range(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Ensure max_price is greater than min_price"""
        if v is not None and hasattr(info.data, 'min_price') and info.data.get('min_price') is not None:
            min_price = info.data['min_price']
            if v <= min_price:
                raise ValueError('Maximum price must be greater than minimum price')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "service_category": "consultation",
                "currency": "USD",
                "min_price": 100.00,
                "max_price": 300.00,
                "is_active": True,
                "search": "consultation"
            }
        }
    )


# Export all schemas
__all__ = [
    'CurrencyEnum',
    'ProviderServicePriceBase',
    'ProviderServicePriceCreate',
    'ProviderServicePriceUpdate',
    'ProviderServicePriceOut',
    'ProviderServicePriceList',
    'ProviderServicePriceSearch'
]