# app/modules/providers/schemas/provider_network_member_schema.py

"""
Provider Network Member Schema - Pydantic v2 Compatible
=======================================================

Fixed implementation using Pydantic v2 syntax.
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class MembershipStatusEnum(str, Enum):
    """Membership status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class ProviderNetworkMemberBase(BaseModel):
    """Base schema with common membership fields"""
    
    provider_id: UUID = Field(
        ...,
        description="Reference to the provider",
        examples=["789e0123-e89b-12d3-a456-426614174000"]
    )
    
    provider_network_id: UUID = Field(
        ...,
        description="Reference to the provider network",
        examples=["456e7890-e89b-12d3-a456-426614174000"]
    )
    
    status: MembershipStatusEnum = Field(
        MembershipStatusEnum.ACTIVE,
        description="Membership status",
        examples=["active"]
    )
    
    @model_validator(mode='after')
    def validate_membership_relationship(self):
        """Validate the provider-network relationship"""
        if self.provider_id == self.provider_network_id:
            raise ValueError('Provider ID and Network ID cannot be the same')
        
        return self


class ProviderNetworkMemberCreate(ProviderNetworkMemberBase):
    """Schema for creating new network memberships"""
    
    # Optional fields for creation
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Administrative notes about the membership",
        examples=["High-volume provider with excellent track record"]
    )
    
    @model_validator(mode='after')
    def validate_membership_creation(self):
        """Business validation for membership creation"""
        status = self.status
        
        # Basic validation - can be extended with business rules
        if status == MembershipStatusEnum.TERMINATED:
            # Terminated memberships might need special handling
            pass
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider_id": "789e0123-e89b-12d3-a456-426614174000",
                "provider_network_id": "456e7890-e89b-12d3-a456-426614174000",
                "status": "active",
                "notes": "High-volume provider with excellent track record"
            }
        }
    )


class ProviderNetworkMemberUpdate(BaseModel):
    """Schema for updating network memberships"""
    
    # Only allow updating specific fields
    status: Optional[MembershipStatusEnum] = Field(
        None,
        description="Updated membership status"
    )
    
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated administrative notes"
    )
    
    @model_validator(mode='after')
    def validate_update_data(self):
        """Validate update data"""
        values = self.model_dump(exclude_unset=True)
        if not values:
            raise ValueError('At least one field must be provided for update')
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "suspended",
                "notes": "Temporary suspension pending compliance review"
            }
        }
    )


class ProviderNetworkMemberOut(ProviderNetworkMemberBase):
    """Schema for membership output/response"""
    
    id: UUID = Field(..., description="Unique membership identifier")
    
    # Administrative
    notes: Optional[str] = Field(None, description="Administrative notes")
    
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
                "id": "abc12345-e89b-12d3-a456-426614174000",
                "provider_id": "789e0123-e89b-12d3-a456-426614174000",
                "provider_network_id": "456e7890-e89b-12d3-a456-426614174000",
                "status": "active",
                "notes": "High-volume provider with excellent track record",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z"
            }
        }
    )


class ProviderNetworkMemberList(BaseModel):
    """Schema for membership list items (minimal data)"""
    
    id: UUID = Field(..., description="Membership identifier")
    provider_id: UUID = Field(..., description="Provider ID")
    provider_network_id: UUID = Field(..., description="Network ID") 
    status: MembershipStatusEnum = Field(..., description="Membership status")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "abc12345-e89b-12d3-a456-426614174000",
                "provider_id": "789e0123-e89b-12d3-a456-426614174000",
                "provider_network_id": "456e7890-e89b-12d3-a456-426614174000",
                "status": "active"
            }
        }
    )


class ProviderNetworkMemberSearch(BaseModel):
    """Schema for membership search/filter parameters"""
    
    provider_id: Optional[UUID] = Field(
        None,
        description="Filter by provider ID"
    )
    
    provider_network_id: Optional[UUID] = Field(
        None,
        description="Filter by network ID"
    )
    
    status: Optional[MembershipStatusEnum] = Field(
        None,
        description="Filter by membership status"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "active",
                "provider_network_id": "456e7890-e89b-12d3-a456-426614174000"
            }
        }
    )


# Export all schemas
__all__ = [
    'MembershipStatusEnum',
    'ProviderNetworkMemberBase',
    'ProviderNetworkMemberCreate',
    'ProviderNetworkMemberUpdate',
    'ProviderNetworkMemberOut',
    'ProviderNetworkMemberList',
    'ProviderNetworkMemberSearch'
]