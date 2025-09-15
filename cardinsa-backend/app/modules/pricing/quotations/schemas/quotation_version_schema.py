# app/modules/insurance/quotations/schemas/quotation_version_schema.py

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class QuotationVersionBase(BaseModel):
    """Base quotation version schema with common fields"""
    quotation_id: Optional[UUID] = Field(None, description="Parent quotation UUID")
    version_number: Optional[int] = Field(None, ge=1, description="Version number")
    is_latest_version: bool = Field(True, description="Whether this is the latest version")
    data_snapshot: Optional[Dict[str, Any]] = Field(None, description="Complete data snapshot")

    @validator('data_snapshot')
    def validate_data_snapshot(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('data_snapshot must be a dictionary')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class QuotationVersionCreate(QuotationVersionBase):
    """Schema for creating a new quotation version"""
    quotation_id: UUID = Field(..., description="Parent quotation UUID is required")
    version_number: int = Field(..., ge=1, description="Version number is required")
    
    class Config:
        schema_extra = {
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "version_number": 2,
                "is_latest_version": True,
                "data_snapshot": {
                    "quotation_data": {
                        "customer_name": "John Doe",
                        "total_premium": 1500.00,
                        "status": "calculated"
                    },
                    "items": [],
                    "factors": [],
                    "metadata": {
                        "version_created_at": "2025-12-09T10:30:00Z"
                    }
                }
            }
        }


class QuotationVersionUpdate(BaseModel):
    """Schema for updating a quotation version"""
    is_latest_version: Optional[bool] = Field(None, description="Whether this is the latest version")
    data_snapshot: Optional[Dict[str, Any]] = Field(None, description="Complete data snapshot")

    @validator('data_snapshot')
    def validate_data_snapshot(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('data_snapshot must be a dictionary')
        return v

    class Config:
        from_attributes = True


class QuotationVersionResponse(QuotationVersionBase):
    """Schema for quotation version response"""
    id: UUID = Field(..., description="Quotation version UUID")
    created_by: Optional[UUID] = Field(None, description="Creator UUID")
    updated_by: Optional[UUID] = Field(None, description="Last updater UUID")
    created_at: datetime = Field(..., description="Creation datetime")
    updated_at: Optional[datetime] = Field(None, description="Last update datetime")
    archived_at: Optional[datetime] = Field(None, description="Archive datetime")
    
    # Computed properties
    has_snapshot: Optional[bool] = Field(None, description="Whether version has data snapshot")
    snapshot_size: Optional[int] = Field(None, description="Size of snapshot in characters")
    is_archived: Optional[bool] = Field(None, description="Whether version is archived")
    
    class Config:
        from_attributes = True


class QuotationVersionSummary(BaseModel):
    """Lightweight quotation version summary"""
    id: UUID
    quotation_id: UUID
    version_number: int
    is_latest_version: bool
    created_at: datetime
    has_snapshot: bool
    
    class Config:
        from_attributes = True


class QuotationVersionComparison(BaseModel):
    """Schema for version comparison results"""
    from_version: int = Field(..., description="Source version number")
    to_version: int = Field(..., description="Target version number")
    comparison_date: datetime = Field(..., description="When comparison was performed")
    changes: List[Dict[str, Any]] = Field(..., description="List of changes between versions")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "from_version": 1,
                "to_version": 2,
                "comparison_date": "2025-12-09T10:30:00Z",
                "changes": [
                    {
                        "field": "quotation.total_premium",
                        "from_value": 1200.00,
                        "to_value": 1500.00,
                        "change_type": "modified"
                    },
                    {
                        "field": "quotation.status",
                        "from_value": "draft",
                        "to_value": "calculated",
                        "change_type": "modified"
                    }
                ]
            }
        }


class QuotationVersionSnapshot(BaseModel):
    """Schema for version snapshot data"""
    quotation_data: Dict[str, Any] = Field(..., description="Main quotation data")
    items: List[Dict[str, Any]] = Field(default_factory=list, description="Quotation items")
    factors: List[Dict[str, Any]] = Field(default_factory=list, description="Quotation factors")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Snapshot metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "quotation_data": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "quote_number": "QT-2025-001",
                    "customer_name": "John Doe",
                    "total_premium": 1500.00,
                    "currency_code": "SAR",
                    "status": "calculated"
                },
                "items": [
                    {
                        "coverage_name": "Comprehensive Coverage",
                        "limit_amount": 100000.00,
                        "display_order": 1
                    }
                ],
                "factors": [
                    {
                        "key": "age_factor",
                        "value": "1.2",
                        "factor_type": "demographic"
                    }
                ],
                "metadata": {
                    "version_created_at": "2025-12-09T10:30:00Z",
                    "snapshot_type": "full_quotation"
                }
            }
        }


class QuotationVersionHistory(BaseModel):
    """Schema for complete version history"""
    quotation_id: UUID = Field(..., description="Quotation UUID")
    versions: List[QuotationVersionSummary] = Field(..., description="List of all versions")
    latest_version_number: int = Field(..., description="Highest version number")
    total_versions: int = Field(..., description="Total number of versions")
    first_created: datetime = Field(..., description="First version creation date")
    last_modified: datetime = Field(..., description="Last version modification date")
    
    class Config:
        from_attributes = True


class QuotationVersionRollback(BaseModel):
    """Schema for version rollback request"""
    target_version_number: int = Field(..., ge=1, description="Version to rollback to")
    create_new_version: bool = Field(True, description="Whether to create new version from rollback")
    rollback_reason: Optional[str] = Field(None, description="Reason for rollback")
    
    class Config:
        schema_extra = {
            "example": {
                "target_version_number": 3,
                "create_new_version": True,
                "rollback_reason": "Reverting pricing changes due to calculation error"
            }
        }


class QuotationVersionFieldHistory(BaseModel):
    """Schema for tracking history of specific fields"""
    field_name: str = Field(..., description="Name of the field")
    field_path: str = Field(..., description="Dot notation path to field")
    value_history: List[Dict[str, Any]] = Field(..., description="History of field values")
    
    class Config:
        schema_extra = {
            "example": {
                "field_name": "total_premium",
                "field_path": "quotation_data.total_premium",
                "value_history": [
                    {
                        "version": 1,
                        "value": 1200.00,
                        "changed_at": "2025-12-09T09:00:00Z"
                    },
                    {
                        "version": 2,
                        "value": 1500.00,
                        "changed_at": "2025-12-09T10:30:00Z"
                    }
                ]
            }
        }


class QuotationVersionDiff(BaseModel):
    """Schema for detailed version differences"""
    field: str = Field(..., description="Field that changed")
    from_value: Any = Field(..., description="Previous value")
    to_value: Any = Field(..., description="New value")
    change_type: str = Field(..., description="Type of change (added/modified/removed)")
    
    class Config:
        schema_extra = {
            "example": {
                "field": "quotation.customer_email",
                "from_value": "old@example.com",
                "to_value": "new@example.com",
                "change_type": "modified"
            }
        }