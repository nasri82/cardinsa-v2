# app/modules/providers/schemas/provider_network_schema.py

"""
Provider Network Schema - Pydantic v2 Compatible
================================================

Fixed implementation using Pydantic v2 syntax.
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class NetworkTypeEnum(str, Enum):
    """Network type enumeration"""
    MEDICAL = "medical"
    MOTOR = "motor"


class ProviderNetworkBase(BaseModel):
    """Base schema with common network fields"""
    
    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r'^[A-Z0-9_]+$',
        description="Unique network code (uppercase letters, numbers, underscores only)",
        examples=["MEDICAL_TIER1_NYC"]
    )
    
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Network display name",
        examples=["New York Medical Tier 1 Network"]
    )
    
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed network description",
        examples=["Premium medical provider network covering Manhattan and Brooklyn"]
    )
    
    type: NetworkTypeEnum = Field(
        NetworkTypeEnum.MEDICAL,
        description="Network type: medical or motor",
        examples=["medical"]
    )
    
    company_id: UUID = Field(
        ...,
        description="Company that owns this network",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    
    is_active: bool = Field(
        True,
        description="Whether network is currently active",
        examples=[True]
    )
    
    @field_validator('code')
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        """Ensure code follows business rules"""
        if not v:
            raise ValueError('Network code is required')
        
        v = v.upper().strip()
        
        # Check for reserved words
        reserved_words = ['NULL', 'DEFAULT', 'SYSTEM', 'ADMIN', 'ALL', 'ANY']
        if v in reserved_words:
            raise ValueError(f'Code cannot be a reserved word: {", ".join(reserved_words)}')
        
        # Check for reasonable structure
        if v.startswith('_') or v.endswith('_'):
            raise ValueError('Code cannot start or end with underscore')
        
        # Discourage overly long codes
        if len(v) > 30:
            raise ValueError('Code should not exceed 30 characters for readability')
        
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate network name"""
        if not v or not v.strip():
            raise ValueError('Network name is required')
        
        v = v.strip()
        
        # Check for reasonable length
        if len(v.split()) > 15:
            raise ValueError('Network name should not exceed 15 words')
        
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided"""
        if v is not None:
            v = v.strip()
            if v and len(v) < 10:
                raise ValueError('Description should be at least 10 characters if provided')
        return v


class ProviderNetworkCreate(ProviderNetworkBase):
    """Schema for creating new provider networks"""
    
    @model_validator(mode='after')
    def validate_network_business_rules(self):
        """Apply business validation rules"""
        network_type = self.type
        code = self.code
        
        # Type-specific validation
        if network_type == NetworkTypeEnum.MEDICAL:
            # Medical networks should have appropriate codes
            medical_keywords = ['MEDICAL', 'HEALTH', 'HOSPITAL', 'CLINIC']
            if code and not any(keyword in code for keyword in medical_keywords):
                # Allow but could warn
                pass
        
        elif network_type == NetworkTypeEnum.MOTOR:
            # Motor networks should have appropriate codes
            motor_keywords = ['MOTOR', 'AUTO', 'VEHICLE', 'REPAIR']
            if code and not any(keyword in code for keyword in motor_keywords):
                # Allow but could warn
                pass
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "MEDICAL_TIER1_NYC",
                "name": "New York Medical Tier 1 Network", 
                "description": "Premium medical provider network covering NYC",
                "type": "medical",
                "company_id": "123e4567-e89b-12d3-a456-426614174000",
                "is_active": True
            }
        }
    )


class ProviderNetworkUpdate(BaseModel):
    """Schema for updating provider networks"""
    
    # All fields are optional for updates
    code: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        pattern=r'^[A-Z0-9_]+$',
        description="Updated network code"
    )
    
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Updated network name"
    )
    
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated description"
    )
    
    type: Optional[NetworkTypeEnum] = Field(
        None,
        description="Updated network type (use with extreme caution)"
    )
    
    is_active: Optional[bool] = Field(
        None,
        description="Updated active status"
    )
    
    # Reuse validators from base class
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return ProviderNetworkBase.validate_code_format(v)
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name_update(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return ProviderNetworkBase.validate_name(v)
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description_update(cls, v: Optional[str]) -> Optional[str]:
        return ProviderNetworkBase.validate_description(v)
    
    @model_validator(mode='after')
    def validate_update_data(self):
        """Validate update data"""
        values = self.model_dump(exclude_unset=True)
        if not values:
            raise ValueError('At least one field must be provided for update')
        
        # Warn about dangerous changes
        if self.type is not None:
            # Type changes can affect existing members and billing
            pass
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Network Name",
                "description": "Updated network description with more details",
                "is_active": False
            }
        }
    )


class ProviderNetworkOut(ProviderNetworkBase):
    """Schema for provider network output/response"""
    
    id: UUID = Field(..., description="Unique identifier")
    
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
                "id": "456e7890-e89b-12d3-a456-426614174000",
                "code": "MEDICAL_TIER1_NYC",
                "name": "New York Medical Tier 1 Network",
                "description": "Premium medical provider network covering NYC",
                "type": "medical",
                "company_id": "123e4567-e89b-12d3-a456-426614174000",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z"
            }
        }
    )


class ProviderNetworkList(BaseModel):
    """Schema for network list items (minimal data)"""
    
    id: UUID = Field(..., description="Unique identifier")
    code: str = Field(..., description="Network code")
    name: str = Field(..., description="Network name")
    type: NetworkTypeEnum = Field(..., description="Network type")
    company_id: UUID = Field(..., description="Company ID")
    is_active: bool = Field(..., description="Active status")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174000",
                "code": "MEDICAL_TIER1_NYC",
                "name": "New York Medical Tier 1 Network",
                "type": "medical",
                "company_id": "123e4567-e89b-12d3-a456-426614174000",
                "is_active": True
            }
        }
    )


class ProviderNetworkSearch(BaseModel):
    """Schema for network search/filter parameters"""
    
    code: Optional[str] = Field(
        None,
        max_length=50,
        description="Filter by code (exact match or starts with)"
    )
    
    name: Optional[str] = Field(
        None,
        max_length=100,
        description="Filter by name (partial match)"
    )
    
    type: Optional[NetworkTypeEnum] = Field(
        None,
        description="Filter by network type"
    )
    
    company_id: Optional[UUID] = Field(
        None,
        description="Filter by company"
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
        description="Search in code, name, and description"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "medical",
                "is_active": True,
                "search": "new york"
            }
        }
    )


# Export all schemas
__all__ = [
    'NetworkTypeEnum',
    'ProviderNetworkBase',
    'ProviderNetworkCreate',
    'ProviderNetworkUpdate',
    'ProviderNetworkOut',
    'ProviderNetworkList',
    'ProviderNetworkSearch'
]