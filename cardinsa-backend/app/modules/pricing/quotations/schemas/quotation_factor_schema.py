# app/modules/pricing/quotations/schemas/quotation_factor_schema.py

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, Any, Union, List, Dict
from datetime import datetime
from uuid import UUID
from enum import Enum


class FactorType(str, Enum):
    """Factor type enumeration"""
    DEMOGRAPHIC = "demographic"
    RISK = "risk"
    DISCOUNT = "discount"
    LOADING = "loading"
    GEOGRAPHIC = "geographic"
    BEHAVIORAL = "behavioral"
    PRODUCT = "product"
    REGULATORY = "regulatory"
    SEASONAL = "seasonal"
    COMPETITIVE = "competitive"


class QuotationFactorBase(BaseModel):
    """Base quotation factor schema with common fields"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "key": "age_factor",
                "value": "1.25",
                "factor_type": "demographic",
                "impact_description": "25% loading for young driver"
            }
        }
    )
    
    quotation_id: Optional[UUID] = Field(None, description="Parent quotation UUID")
    key: str = Field(..., min_length=1, max_length=100, description="Factor key/name")
    value: str = Field(..., description="Factor value as string")
    factor_type: Optional[FactorType] = Field(None, description="Type of factor")
    impact_description: Optional[str] = Field(None, description="Description of factor impact on pricing")

    @field_validator('key')
    @classmethod
    def validate_key(cls, v):
        # Ensure key follows naming conventions
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Factor key must contain only alphanumeric characters, underscores, and hyphens')
        return v.lower()

    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        if not v.strip():
            raise ValueError('Factor value cannot be empty')
        return v.strip()


class QuotationFactorCreate(QuotationFactorBase):
    """Schema for creating a new quotation factor"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "key": "age_factor",
                "value": "1.2",
                "factor_type": "demographic",
                "impact_description": "20% increase due to driver age under 25"
            }
        }
    )
    
    quotation_id: UUID = Field(..., description="Parent quotation UUID is required")


class QuotationFactorUpdate(BaseModel):
    """Schema for updating a quotation factor"""
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    key: Optional[str] = Field(None, min_length=1, max_length=100, description="Factor key/name")
    value: Optional[str] = Field(None, description="Factor value as string")
    factor_type: Optional[FactorType] = Field(None, description="Type of factor")
    impact_description: Optional[str] = Field(None, description="Description of factor impact")

    @field_validator('key')
    @classmethod
    def validate_key(cls, v):
        if v is not None:
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Factor key must contain only alphanumeric characters, underscores, and hyphens')
            return v.lower()
        return v

    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Factor value cannot be empty')
        return v.strip() if v else v


class QuotationFactorResponse(QuotationFactorBase):
    """Schema for quotation factor response"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )
    
    id: UUID = Field(..., description="Quotation factor UUID")
    created_by: Optional[UUID] = Field(None, description="Creator UUID")
    updated_by: Optional[UUID] = Field(None, description="Last updater UUID")
    created_at: datetime = Field(..., description="Creation datetime")
    updated_at: Optional[datetime] = Field(None, description="Last update datetime")
    archived_at: Optional[datetime] = Field(None, description="Archive datetime")
    
    # Computed properties
    parsed_value: Optional[Union[str, int, float, bool, dict, list]] = Field(None, description="Parsed value")
    is_numeric: Optional[bool] = Field(None, description="Whether value is numeric")
    numeric_value: Optional[float] = Field(None, description="Numeric representation of value")
    is_archived: Optional[bool] = Field(None, description="Whether factor is archived")


class QuotationFactorSummary(BaseModel):
    """Lightweight quotation factor summary"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    key: str
    value: str
    factor_type: Optional[FactorType]
    impact_description: Optional[str]


class QuotationFactorNumericRequest(BaseModel):
    """Schema for setting numeric factor values"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "key": "age_factor",
                "numeric_value": 1.25,
                "factor_type": "demographic",
                "impact_description": "25% loading for young driver"
            }
        }
    )
    
    key: str = Field(..., min_length=1, max_length=100, description="Factor key")
    numeric_value: float = Field(..., description="Numeric value")
    factor_type: Optional[FactorType] = Field(None, description="Type of factor")
    impact_description: Optional[str] = Field(None, description="Impact description")


class QuotationFactorBooleanRequest(BaseModel):
    """Schema for setting boolean factor values"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "key": "has_anti_theft",
                "boolean_value": True,
                "factor_type": "discount",
                "impact_description": "Anti-theft device installed"
            }
        }
    )
    
    key: str = Field(..., min_length=1, max_length=100, description="Factor key")
    boolean_value: bool = Field(..., description="Boolean value")
    factor_type: Optional[FactorType] = Field(None, description="Type of factor")
    impact_description: Optional[str] = Field(None, description="Impact description")


class QuotationFactorComplexRequest(BaseModel):
    """Schema for setting complex factor values (objects/arrays)"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "key": "vehicle_modifications",
                "complex_value": {
                    "engine_modifications": ["turbo", "exhaust"],
                    "safety_features": ["abs", "airbags"],
                    "modification_count": 2
                },
                "factor_type": "risk",
                "impact_description": "Vehicle has performance and safety modifications"
            }
        }
    )
    
    key: str = Field(..., min_length=1, max_length=100, description="Factor key")
    complex_value: Union[Dict[str, Any], List[Any]] = Field(..., description="Complex value (object or array)")
    factor_type: Optional[FactorType] = Field(None, description="Type of factor")
    impact_description: Optional[str] = Field(None, description="Impact description")


class QuotationFactorBulkCreate(BaseModel):
    """Schema for creating multiple quotation factors"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
                "factors": [
                    {
                        "key": "age_factor",
                        "value": "1.2",
                        "factor_type": "demographic",
                        "impact_description": "20% increase due to driver age"
                    },
                    {
                        "key": "location_risk",
                        "value": "0.9",
                        "factor_type": "geographic",
                        "impact_description": "10% discount for low-risk area"
                    }
                ]
            }
        }
    )
    
    quotation_id: UUID = Field(..., description="Parent quotation UUID")
    factors: List[QuotationFactorCreate] = Field(..., min_length=1, description="List of factors to create")
    
    @field_validator('factors')
    @classmethod
    def validate_factors_quotation_id(cls, v, info):
        quotation_id = info.data.get('quotation_id')
        if quotation_id:
            for factor in v:
                if factor.quotation_id and factor.quotation_id != quotation_id:
                    raise ValueError('All factors must belong to the same quotation')
                factor.quotation_id = quotation_id
        return v
    
    @field_validator('factors')
    @classmethod
    def validate_unique_keys(cls, v):
        keys = [factor.key for factor in v]
        if len(keys) != len(set(keys)):
            raise ValueError('Factor keys must be unique within the same quotation')
        return v


class QuotationFactorsByType(BaseModel):
    """Schema for grouping factors by type"""
    
    model_config = ConfigDict(from_attributes=True)
    
    factor_type: FactorType
    factors: List[QuotationFactorResponse]
    total_count: int = Field(..., description="Total number of factors of this type")


class QuotationFactorsGrouped(BaseModel):
    """Schema for all factors grouped by type"""
    
    model_config = ConfigDict(from_attributes=True)
    
    quotation_id: UUID
    factor_groups: List[QuotationFactorsByType]
    total_factors: int = Field(..., description="Total number of all factors")
    last_updated: Optional[datetime] = Field(None, description="Last factor update timestamp")


class QuotationFactorImpactAnalysis(BaseModel):
    """Schema for factor impact analysis"""
    
    model_config = ConfigDict(from_attributes=True)
    
    factor_id: UUID
    key: str
    current_value: str
    factor_type: FactorType
    impact_description: Optional[str]
    impact_amount: Optional[float] = Field(None, description="Calculated impact amount")
    impact_percentage: Optional[float] = Field(None, description="Impact as percentage")
    is_positive_impact: Optional[bool] = Field(None, description="Whether impact increases premium")


class QuotationFactorValidation(BaseModel):
    """Schema for factor validation results"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_valid": False,
                "validation_errors": [
                    "age_factor value must be numeric",
                    "location_code is not a valid location"
                ],
                "warnings": [
                    "risk_score seems unusually high"
                ],
                "suggested_corrections": [
                    "Convert age_factor to numeric value",
                    "Use standard location codes"
                ]
            }
        }
    )
    
    is_valid: bool
    validation_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggested_corrections: List[str] = Field(default_factory=list)