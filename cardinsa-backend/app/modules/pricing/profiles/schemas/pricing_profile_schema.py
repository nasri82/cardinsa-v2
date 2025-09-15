# app/modules/pricing/profiles/schemas/pricing_profile_schema.py

"""
Simplified pricing profile schemas that import from quotation_pricing_profile_schema
and provide convenient aliases for services that expect this naming convention.
Also includes missing schemas like PricingProfileSearchFilters and PricingProfileCloneRequest.
"""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

# Import all the classes from the main schema file
from .quotation_pricing_profile_schema import (
    # Enums
    InsuranceType,
    ProfileStatus,
    CurrencyCode,
    
    # Base profile schemas
    QuotationPricingProfileBase as PricingProfileBase,
    QuotationPricingProfileCreate as PricingProfileCreate,
    QuotationPricingProfileUpdate as PricingProfileUpdate,
    QuotationPricingProfileResponse as PricingProfileResponse,
    QuotationPricingProfileSummary as PricingProfileSummary,
    QuotationPricingProfileBulkCreate as PricingProfileBulkCreate,
    QuotationPricingProfileStatusUpdate as PricingProfileStatusUpdate,
    QuotationPricingProfileValidation as PricingProfileValidation,
    QuotationPricingProfileWithRules as PricingProfileWithRules,
)

# Define the missing schemas that are being imported in the routes

class PricingProfileSearchFilters(BaseModel):
    """Schema for pricing profile search filters"""
    
    name: Optional[str] = Field(None, description="Filter by profile name (partial match)")
    code: Optional[str] = Field(None, description="Filter by profile code")
    insurance_type: Optional[str] = Field(None, description="Filter by insurance type")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    currency: Optional[str] = Field(None, description="Filter by currency code")
    status: Optional[str] = Field(None, description="Filter by profile status")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date (before)")
    min_premium_range: Optional[Decimal] = Field(None, description="Minimum base premium")
    max_premium_range: Optional[Decimal] = Field(None, description="Maximum base premium")
    page: Optional[int] = Field(1, ge=1, description="Page number")
    page_size: Optional[int] = Field(20, ge=1, le=100, description="Items per page")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Motor",
                "insurance_type": "Motor",
                "is_active": True,
                "currency": "SAR",
                "min_premium_range": 1000.0,
                "max_premium_range": 5000.0,
                "page": 1,
                "page_size": 20
            }
        }
    )

class PricingProfileCloneRequest(BaseModel):
    """Schema for cloning a pricing profile"""
    
    new_name: str = Field(..., min_length=1, max_length=255, description="Name for the cloned profile")
    new_code: Optional[str] = Field(None, max_length=50, description="Optional code for the cloned profile")
    include_rules: bool = Field(True, description="Whether to copy associated rules")
    copy_settings: bool = Field(True, description="Whether to copy all profile settings")
    description: Optional[str] = Field(None, max_length=1000, description="Description for the cloned profile")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "new_name": "Motor Premium Profile - Copy",
                "new_code": "MPP_COPY_001",
                "include_rules": True,
                "copy_settings": True,
                "description": "Cloned from Motor Premium Profile for testing purposes"
            }
        }
    )

class PricingProfileActivationRequest(BaseModel):
    """Schema for activating a pricing profile"""
    
    effective_date: Optional[datetime] = Field(None, description="When activation takes effect")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for activation")
    validate_before_activation: bool = Field(True, description="Whether to validate profile before activation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "effective_date": "2024-01-01T00:00:00Z",
                "reason": "Profile has been reviewed and approved for production use",
                "validate_before_activation": True
            }
        }
    )

class PricingProfileDeactivationRequest(BaseModel):
    """Schema for deactivating a pricing profile"""
    
    effective_date: Optional[datetime] = Field(None, description="When deactivation takes effect")
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for deactivation")
    replacement_profile_id: Optional[UUID] = Field(None, description="ID of replacement profile if any")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "effective_date": "2024-12-31T23:59:59Z",
                "reason": "Profile being replaced by updated version",
                "replacement_profile_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )

class PricingProfileBulkActivationRequest(BaseModel):
    """Schema for bulk activating pricing profiles"""
    
    profile_ids: List[UUID] = Field(..., min_length=1, max_length=50, description="List of profile IDs to activate")
    effective_date: Optional[datetime] = Field(None, description="When activation takes effect")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for activation")
    validate_before_activation: bool = Field(True, description="Whether to validate profiles before activation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profile_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "987fcdeb-51a2-43d1-9f12-345678901234"
                ],
                "effective_date": "2024-01-01T00:00:00Z",
                "reason": "Quarterly profile updates approved",
                "validate_before_activation": True
            }
        }
    )

class PricingProfileExportRequest(BaseModel):
    """Schema for exporting pricing profiles"""
    
    profile_ids: Optional[List[UUID]] = Field(None, description="Specific profile IDs to export (if none, export all)")
    include_rules: bool = Field(True, description="Whether to include associated rules")
    include_history: bool = Field(False, description="Whether to include history data")
    export_format: str = Field("json", description="Export format (json, xlsx, csv)")
    compression: bool = Field(False, description="Whether to compress the export")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profile_ids": [
                    "123e4567-e89b-12d3-a456-426614174000"
                ],
                "include_rules": True,
                "include_history": False,
                "export_format": "xlsx",
                "compression": True
            }
        }
    )

class PricingProfileImportRequest(BaseModel):
    """Schema for importing pricing profiles"""
    
    file_content: str = Field(..., description="Base64 encoded file content")
    file_format: str = Field(..., description="File format (json, xlsx, csv)")
    import_mode: str = Field("create_new", description="Import mode (create_new, update_existing, upsert)")
    validate_before_import: bool = Field(True, description="Whether to validate data before import")
    dry_run: bool = Field(False, description="Whether to perform a dry run without actual import")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_content": "eyJwcm9maWxlcyI6W10u...",
                "file_format": "json",
                "import_mode": "create_new",
                "validate_before_import": True,
                "dry_run": False
            }
        }
    )

# Export all classes for easy import
__all__ = [
    # Enums
    "InsuranceType",
    "ProfileStatus",
    "CurrencyCode",
    
    # Core profile schemas
    "PricingProfileBase",
    "PricingProfileCreate",
    "PricingProfileUpdate", 
    "PricingProfileResponse",
    "PricingProfileSummary",
    "PricingProfileBulkCreate",
    "PricingProfileStatusUpdate",
    "PricingProfileValidation",
    "PricingProfileWithRules",
    
    # Additional schemas
    "PricingProfileSearchFilters",
    "PricingProfileCloneRequest",
    "PricingProfileActivationRequest",
    "PricingProfileDeactivationRequest",
    "PricingProfileBulkActivationRequest",
    "PricingProfileExportRequest",
    "PricingProfileImportRequest",
]