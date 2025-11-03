# app/modules/providers/schemas/provider_type_schema.py

"""
Provider Type Schema - Pydantic v2 Compatible
=============================================

Fixed implementation using Pydantic v2 syntax with @field_validator and @model_validator.
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime
from enum import Enum


class ProviderCategoryEnum(str, Enum):
    """Provider category enumeration"""
    MEDICAL = "medical"
    MOTOR = "motor"


class ProviderTypeBase(BaseModel):
    """Base schema with common fields"""
    
    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r'^[A-Z0-9_]+$',
        description="Unique business code (uppercase letters, numbers, underscores only)",
        examples=["HOSPITAL"]
    )
    
    label: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Human-readable display name",
        examples=["General Hospital"]
    )
    
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed description of provider type",
        examples=["General hospitals providing comprehensive medical care and emergency services"]
    )
    
    category: ProviderCategoryEnum = Field(
        ProviderCategoryEnum.MEDICAL,
        description="Provider category: medical or motor",
        examples=["medical"]
    )
    
    icon: Optional[str] = Field(
        None,
        max_length=100,
        description="Icon identifier or class name for UI display",
        examples=["fas fa-hospital"]
    )
    
    is_active: bool = Field(
        True,
        description="Whether this provider type is currently active",
        examples=[True]
    )
    
    @field_validator('code')
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        """Ensure code follows business rules"""
        if not v:
            raise ValueError('Code is required')
        
        v = v.upper().strip()
        
        # Check for reserved words
        reserved_words = ['NULL', 'DEFAULT', 'SYSTEM', 'ADMIN']
        if v in reserved_words:
            raise ValueError(f'Code cannot be a reserved word: {", ".join(reserved_words)}')
        
        # Check for special business rules
        if v.startswith('_') or v.endswith('_'):
            raise ValueError('Code cannot start or end with underscore')
        
        return v
    
    @field_validator('label')
    @classmethod
    def validate_label(cls, v: str) -> str:
        """Validate label format"""
        if not v or not v.strip():
            raise ValueError('Label is required')
        
        v = v.strip()
        
        # Check for reasonable content
        if len(v.split()) > 10:
            raise ValueError('Label should not exceed 10 words')
        
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided"""
        if v is not None:
            v = v.strip()
            if len(v) < 10:
                raise ValueError('Description should be at least 10 characters if provided')
        return v
    
    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v: Optional[str]) -> Optional[str]:
        """Validate icon format"""
        if v is not None:
            v = v.strip()
            # Basic validation for common icon formats
            valid_prefixes = ['fa-', 'fas ', 'far ', 'fab ', 'icon-', 'mdi-', 'material-icons']
            if v and not any(v.startswith(prefix) for prefix in valid_prefixes):
                # Allow simple icon names without prefix
                if not v.replace('-', '').replace('_', '').isalnum():
                    raise ValueError('Icon should be a valid icon class or identifier')
        return v


class ProviderTypeCreate(ProviderTypeBase):
    """Schema for creating new provider types"""
    
    @model_validator(mode='after')
    def validate_create_data(self):
        """Business logic validation for creation"""
        code = self.code
        category = self.category
        
        # Category-specific code prefixes (business rule examples)
        if category == ProviderCategoryEnum.MEDICAL:
            medical_prefixes = ['HOSPITAL', 'CLINIC', 'SPECIALIST', 'PHARMACY', 'LAB']
            if code and not any(code.startswith(prefix) for prefix in medical_prefixes):
                # Allow but warn - don't enforce strictly
                pass
        
        elif category == ProviderCategoryEnum.MOTOR:
            motor_prefixes = ['AUTO', 'MOTOR', 'GARAGE', 'REPAIR', 'BODY', 'TIRE']
            if code and not any(code.startswith(prefix) for prefix in motor_prefixes):
                # Allow but warn - don't enforce strictly
                pass
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "HOSPITAL_GENERAL",
                "label": "General Hospital",
                "description": "General hospitals providing comprehensive medical care",
                "category": "medical",
                "icon": "fas fa-hospital",
                "is_active": True
            }
        }
    )


class ProviderTypeUpdate(BaseModel):
    """Schema for updating provider types"""
    
    # All fields are optional for updates
    code: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        pattern=r'^[A-Z0-9_]+$',
        description="Updated business code"
    )
    
    label: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Updated display name"
    )
    
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated description"
    )
    
    category: Optional[ProviderCategoryEnum] = Field(
        None,
        description="Updated category (use with caution)"
    )
    
    icon: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated icon"
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
            return ProviderTypeBase.validate_code_format(v)
        return v
    
    @field_validator('label')
    @classmethod
    def validate_label_update(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return ProviderTypeBase.validate_label(v)
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description_update(cls, v: Optional[str]) -> Optional[str]:
        return ProviderTypeBase.validate_description(v)
    
    @field_validator('icon')
    @classmethod
    def validate_icon_update(cls, v: Optional[str]) -> Optional[str]:
        return ProviderTypeBase.validate_icon(v)
    
    @model_validator(mode='after')
    def validate_update_data(self):
        """Ensure at least one field is provided for update"""
        values = self.model_dump(exclude_unset=True)
        if not values:
            raise ValueError('At least one field must be provided for update')
        
        # Warn about category changes
        if self.category is not None:
            # In a real application, you might want to add additional validation
            # or require special permissions for category changes
            pass
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "Updated Hospital Name",
                "description": "Updated description with more details",
                "is_active": False
            }
        }
    )


class ProviderTypeOut(ProviderTypeBase):
    """Schema for provider type output/response"""
    
    id: UUID = Field(..., description="Unique identifier")
    
    # Audit fields
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="User who created this record")
    updated_by: Optional[UUID] = Field(None, description="User who last updated this record")
    
    # Soft delete field
    archived_at: Optional[datetime] = Field(None, description="Archive/deletion timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v) if v else None
        },
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "code": "HOSPITAL_GENERAL",
                "label": "General Hospital",
                "description": "General hospitals providing comprehensive medical care",
                "category": "medical",
                "icon": "fas fa-hospital",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z",
                "created_by": "123e4567-e89b-12d3-a456-426614174001",
                "updated_by": None,
                "archived_at": None
            }
        }
    )


class ProviderTypeList(BaseModel):
    """Schema for provider type list items (minimal data)"""
    
    id: UUID = Field(..., description="Unique identifier")
    code: str = Field(..., description="Business code")
    label: str = Field(..., description="Display name")
    category: ProviderCategoryEnum = Field(..., description="Category")
    is_active: bool = Field(..., description="Active status")
    icon: Optional[str] = Field(None, description="Icon identifier")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "code": "HOSPITAL_GENERAL",
                "label": "General Hospital",
                "category": "medical",
                "is_active": True,
                "icon": "fas fa-hospital"
            }
        }
    )


class ProviderTypeSearch(BaseModel):
    """Schema for provider type search/filter parameters"""
    
    code: Optional[str] = Field(
        None,
        max_length=50,
        description="Filter by code (exact match or starts with)"
    )
    
    label: Optional[str] = Field(
        None,
        max_length=100,
        description="Filter by label (partial match)"
    )
    
    category: Optional[ProviderCategoryEnum] = Field(
        None,
        description="Filter by category"
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
        description="Search in code, label, and description"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "medical",
                "is_active": True,
                "search": "hospital"
            }
        }
    )


# Export all schemas
__all__ = [
    'ProviderCategoryEnum',
    'ProviderTypeBase',
    'ProviderTypeCreate',
    'ProviderTypeUpdate', 
    'ProviderTypeOut',
    'ProviderTypeList',
    'ProviderTypeSearch'
]