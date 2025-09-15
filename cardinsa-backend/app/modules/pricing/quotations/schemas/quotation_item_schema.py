# app/modules/pricing/quotations/schemas/quotation_item_schema.py

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class QuotationItemBase(BaseModel):
    """Base quotation item schema with common fields"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
            UUID: lambda v: str(v)
        }
    )
    
    quotation_id: Optional[UUID] = Field(None, description="Parent quotation UUID")
    coverage_name: Optional[str] = Field(None, description="Coverage name in English")
    coverage_name_ar: Optional[str] = Field(None, description="Coverage name in Arabic")
    limit_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Coverage limit amount")
    notes: Optional[str] = Field(None, description="Coverage notes in English")
    notes_ar: Optional[str] = Field(None, description="Coverage notes in Arabic")
    display_order: int = Field(0, ge=0, description="Display order for sorting")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @field_validator('meta_data')
    @classmethod
    def validate_metadata(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('meta_data must be a dictionary')
        return v

    @model_validator(mode='after')
    def validate_coverage_names(self) -> 'QuotationItemBase':
        if not self.coverage_name and not self.coverage_name_ar:
            raise ValueError('At least one coverage name (English or Arabic) is required')
        return self


class QuotationItemCreate(QuotationItemBase):
    """Schema for creating a new quotation item"""
    
    quotation_id: UUID = Field(..., description="Parent quotation UUID is required")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "coverage_name": "Comprehensive Motor Insurance",
                "coverage_name_ar": "تأمين شامل للسيارات",
                "limit_amount": 50000.00,
                "notes": "Includes theft and accident coverage",
                "notes_ar": "يشمل تغطية السرقة والحوادث",
                "display_order": 1
            }
        }
    )


class QuotationItemUpdate(BaseModel):
    """Schema for updating a quotation item"""
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    coverage_name: Optional[str] = Field(None, description="Coverage name in English")
    coverage_name_ar: Optional[str] = Field(None, description="Coverage name in Arabic")
    limit_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Coverage limit amount")
    notes: Optional[str] = Field(None, description="Coverage notes in English")
    notes_ar: Optional[str] = Field(None, description="Coverage notes in Arabic")
    display_order: Optional[int] = Field(None, ge=0, description="Display order for sorting")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @field_validator('meta_data')
    @classmethod
    def validate_metadata(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('meta_data must be a dictionary')
        return v


class QuotationItemResponse(QuotationItemBase):
    """Schema for quotation item response"""
    
    id: UUID = Field(..., description="Quotation item UUID")
    created_by: Optional[UUID] = Field(None, description="Creator UUID")
    updated_by: Optional[UUID] = Field(None, description="Last updater UUID")
    created_at: datetime = Field(..., description="Creation datetime")
    updated_at: Optional[datetime] = Field(None, description="Last update datetime")
    archived_at: Optional[datetime] = Field(None, description="Archive datetime")
    
    # Computed properties
    coverage_display_name: Optional[str] = Field(None, description="Display name for coverage")
    notes_display: Optional[str] = Field(None, description="Display notes")
    is_archived: Optional[bool] = Field(None, description="Whether item is archived")


class QuotationItemSummary(BaseModel):
    """Lightweight quotation item summary"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    coverage_name: Optional[str]
    coverage_name_ar: Optional[str]
    limit_amount: Optional[Decimal]
    display_order: int


class QuotationItemBulkCreate(BaseModel):
    """Schema for creating multiple quotation items"""
    
    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "items": [
                    {
                        "coverage_name": "Third Party Liability",
                        "coverage_name_ar": "تأمين الطرف الثالث",
                        "limit_amount": 100000.00,
                        "display_order": 1
                    },
                    {
                        "coverage_name": "Comprehensive Coverage",
                        "coverage_name_ar": "التغطية الشاملة",
                        "limit_amount": 200000.00,
                        "display_order": 2
                    }
                ]
            }
        }
    )
    
    quotation_id: UUID = Field(..., description="Parent quotation UUID")
    items: List[QuotationItemCreate] = Field(..., min_length=1, description="List of items to create")
    
    @field_validator('items')
    @classmethod
    def validate_items_quotation_id(cls, v, info):
        quotation_id = info.data.get('quotation_id')
        if quotation_id:
            for item in v:
                if item.quotation_id and item.quotation_id != quotation_id:
                    raise ValueError('All items must belong to the same quotation')
                item.quotation_id = quotation_id
        return v


class QuotationItemLocalizedResponse(BaseModel):
    """Localized quotation item response for specific language"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "quotation_id": "123e4567-e89b-12d3-a456-426614174001",
                "coverage_name": "تأمين شامل للسيارات",
                "notes": "يشمل تغطية السرقة والحوادث",
                "limit_amount": 50000.00,
                "display_order": 1,
                "language": "ar"
            }
        }
    )
    
    id: UUID
    quotation_id: UUID
    coverage_name: str
    notes: Optional[str]
    limit_amount: Optional[Decimal]
    display_order: int
    meta_data: Optional[Dict[str, Any]]
    language: str = Field(..., description="Language code (en/ar)")


class QuotationItemMetadataUpdate(BaseModel):
    """Schema for updating quotation item metadata only"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "meta_data": {
                    "category": "motor",
                    "sub_category": "comprehensive",
                    "risk_level": "medium",
                    "optional": False,
                    "custom_fields": {
                        "vehicle_type": "sedan",
                        "coverage_period": "annual"
                    }
                }
            }
        }
    )
    
    meta_data: Dict[str, Any] = Field(..., description="Metadata to update")
    
    @field_validator('meta_data')
    @classmethod
    def validate_metadata(cls, v):
        if not isinstance(v, dict):
            raise ValueError('meta_data must be a dictionary')
        return v