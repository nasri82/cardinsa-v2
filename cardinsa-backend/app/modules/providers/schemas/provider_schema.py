# app/modules/providers/schemas/provider_schema.py

"""
Provider Schema - Pydantic v2 Compatible
========================================

Fixed implementation using Pydantic v2 syntax.
"""

from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import re


class ProviderBase(BaseModel):
    """Base schema with common provider fields"""
    
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Provider business name",
        examples=["City General Hospital"]
    )
    
    provider_type_id: UUID = Field(
        ...,
        description="Reference to provider type",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    
    # Contact information
    email: Optional[EmailStr] = Field(
        None,
        description="Primary contact email address",
        examples=["contact@cityhospital.com"]
    )
    
    phone: Optional[str] = Field(
        None,
        max_length=50,
        description="Primary contact phone number",
        examples=["+1-555-0123"]
    )
    
    # Address information
    address: Optional[str] = Field(
        None,
        max_length=500,
        description="Street address",
        examples=["123 Main Street, Downtown"]
    )
    
    city_id: Optional[UUID] = Field(
        None,
        description="Reference to city",
        examples=["456e7890-e89b-12d3-a456-426614174000"]
    )
    
    # Geolocation
    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Latitude coordinate (-90 to 90)",
        examples=[40.7128]
    )
    
    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Longitude coordinate (-180 to 180)",
        examples=[-74.0060]
    )
    
    # Business information
    website: Optional[str] = Field(
        None,
        max_length=500,
        description="Provider website URL",
        examples=["https://www.cityhospital.com"]
    )
    
    logo_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL to provider logo/image",
        examples=["https://cdn.example.com/logos/city-hospital.png"]
    )
    
    # Status
    is_active: bool = Field(
        True,
        description="Whether provider is currently active",
        examples=[True]
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate provider name"""
        if not v or not v.strip():
            raise ValueError('Provider name is required')
        
        v = v.strip()
        
        # Check for minimum meaningful content
        if len(v.split()) == 1 and len(v) < 3:
            raise ValueError('Provider name should be at least 3 characters or multiple words')
        
        # Check for reasonable length
        if len(v.split()) > 10:
            raise ValueError('Provider name should not exceed 10 words')
        
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format"""
        if v is None:
            return None
        
        v = v.strip()
        if not v:
            return None
        
        # Remove common formatting characters for validation
        digits_only = re.sub(r'[^\d+]', '', v)
        
        # Check for reasonable length (international format)
        if len(digits_only) < 10:
            raise ValueError('Phone number too short')
        if len(digits_only) > 15:
            raise ValueError('Phone number too long')
        
        # Basic format validation
        phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)\.]{8,}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Invalid phone number format')
        
        return v
    
    @field_validator('website')
    @classmethod
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        """Validate website URL format"""
        if v is None:
            return None
        
        v = v.strip()
        if not v:
            return None
        
        # Basic URL validation
        url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        if not re.match(url_pattern, v):
            raise ValueError('Invalid website URL format')
        
        return v
    
    @model_validator(mode='after')
    def validate_coordinates(self):
        """Ensure latitude and longitude are provided together"""
        lat = self.latitude
        lng = self.longitude
        
        # Both must be provided together or both must be None
        if (lat is not None and lng is None) or (lat is None and lng is not None):
            raise ValueError('Latitude and longitude must be provided together')
        
        return self


class ProviderCreate(ProviderBase):
    """Schema for creating new providers"""
    
    @model_validator(mode='after')
    def validate_create_requirements(self):
        """Additional validation for provider creation"""
        if not self.name:
            raise ValueError('Provider name is required')
        if not self.provider_type_id:
            raise ValueError('Provider type is required')
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "City General Hospital",
                "provider_type_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "contact@cityhospital.com",
                "phone": "+1-555-0123",
                "address": "123 Main Street, Downtown",
                "city_id": "456e7890-e89b-12d3-a456-426614174001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "website": "https://www.cityhospital.com",
                "is_active": True
            }
        }
    )


class ProviderUpdate(BaseModel):
    """Schema for updating providers"""
    
    # All fields are optional for updates
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Updated provider name"
    )
    
    provider_type_id: Optional[UUID] = Field(
        None,
        description="Updated provider type"
    )
    
    email: Optional[EmailStr] = Field(
        None,
        description="Updated email address"
    )
    
    phone: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated phone number"
    )
    
    address: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated address"
    )
    
    city_id: Optional[UUID] = Field(
        None,
        description="Updated city"
    )
    
    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Updated latitude"
    )
    
    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Updated longitude"
    )
    
    website: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated website"
    )
    
    logo_url: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated logo URL"
    )
    
    is_active: Optional[bool] = Field(
        None,
        description="Updated active status"
    )
    
    # Reuse validators from base class
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return ProviderBase.validate_name(v)
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        return ProviderBase.validate_phone(v)
    
    @field_validator('website')
    @classmethod
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        return ProviderBase.validate_website(v)
    
    @model_validator(mode='after')
    def validate_update_data(self):
        """Validate update data"""
        values = self.model_dump(exclude_unset=True)
        if not values:
            raise ValueError('At least one field must be provided for update')
        
        # Validate coordinates if provided
        if self.latitude is not None or self.longitude is not None:
            if (self.latitude is not None and self.longitude is None) or (self.latitude is None and self.longitude is not None):
                raise ValueError('Latitude and longitude must be provided together')
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Hospital Name",
                "phone": "+1-555-9999",
                "website": "https://www.updatedhospital.com",
                "is_active": False
            }
        }
    )


class ProviderOut(ProviderBase):
    """Schema for provider output/response"""
    
    id: UUID = Field(..., description="Unique identifier")
    
    # Additional fields from database
    rating: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Average customer rating (0-5 scale)",
        examples=[4.2]
    )
    
    total_reviews: int = Field(
        0,
        ge=0,
        description="Total number of reviews received",
        examples=[156]
    )
    
    average_response_time: Optional[int] = Field(
        None,
        ge=0,
        description="Average response time in minutes",
        examples=[15]
    )
    
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
            UUID: lambda v: str(v) if v else None
        },
        json_schema_extra={
            "example": {
                "id": "789e0123-e89b-12d3-a456-426614174000",
                "name": "City General Hospital",
                "provider_type_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "contact@cityhospital.com",
                "phone": "+1-555-0123",
                "address": "123 Main Street, Downtown",
                "city_id": "456e7890-e89b-12d3-a456-426614174001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "website": "https://www.cityhospital.com",
                "logo_url": "https://cdn.example.com/logos/city-hospital.png",
                "is_active": True,
                "rating": 4.2,
                "total_reviews": 156,
                "average_response_time": 15,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z"
            }
        }
    )


class ProviderList(BaseModel):
    """Schema for provider list items (minimal data)"""
    
    id: UUID = Field(..., description="Unique identifier")
    name: str = Field(..., description="Provider name")
    provider_type_id: UUID = Field(..., description="Provider type reference")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    city_id: Optional[UUID] = Field(None, description="City reference")
    rating: Optional[float] = Field(None, description="Average rating")
    is_active: bool = Field(..., description="Active status")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "789e0123-e89b-12d3-a456-426614174000",
                "name": "City General Hospital",
                "provider_type_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "contact@cityhospital.com",
                "phone": "+1-555-0123",
                "city_id": "456e7890-e89b-12d3-a456-426614174001",
                "rating": 4.2,
                "is_active": True
            }
        }
    )


class ProviderSearch(BaseModel):
    """Schema for provider search/filter parameters"""
    
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Search by provider name (partial match)"
    )
    
    provider_type_id: Optional[UUID] = Field(
        None,
        description="Filter by provider type"
    )
    
    city_id: Optional[UUID] = Field(
        None,
        description="Filter by city"
    )
    
    is_active: Optional[bool] = Field(
        None,
        description="Filter by active status"
    )
    
    min_rating: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Minimum rating filter"
    )
    
    max_distance_km: Optional[float] = Field(
        None,
        gt=0,
        le=1000,
        description="Maximum distance in kilometers (requires latitude/longitude)"
    )
    
    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Search center latitude (for distance search)"
    )
    
    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Search center longitude (for distance search)"
    )
    
    # Text search
    search: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Full-text search in name, address, email"
    )
    
    @model_validator(mode='after')
    def validate_distance_search(self):
        """Validate distance search parameters"""
        if self.max_distance_km is not None:
            if self.latitude is None or self.longitude is None:
                raise ValueError('Latitude and longitude required for distance search')
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "hospital",
                "is_active": True,
                "min_rating": 4.0,
                "max_distance_km": 10,
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }
    )


# Export all schemas
__all__ = [
    'ProviderBase',
    'ProviderCreate',
    'ProviderUpdate',
    'ProviderOut',
    'ProviderList',
    'ProviderSearch'
]