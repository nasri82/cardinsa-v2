# app/modules/pricing/quotations/schemas/__init__.py

"""
Quotation schemas package for request/response models.

This package provides comprehensive schema definitions for quotation management,
with error handling to ensure graceful imports even when some schemas are missing.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, Field

# ===================================================================
# DEFINE ENUMS LOCALLY TO AVOID IMPORT ISSUES
# ===================================================================

class QuotationStatusEnum(str, Enum):
    """Quotation status enumeration"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    CALCULATED = "calculated"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"
    CANCELLED = "cancelled"

class FactorType(str, Enum):
    """Factor type enumeration"""
    DEMOGRAPHIC = "demographic"
    RISK = "risk"
    DISCOUNT = "discount"
    SURCHARGE = "surcharge"
    ADJUSTMENT = "adjustment"

class WorkflowEvent(str, Enum):
    """Workflow event enumeration"""
    CREATED = "created"
    UPDATED = "updated"
    CALCULATED = "calculated"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"

class EventCategory(str, Enum):
    """Event category enumeration"""
    SYSTEM = "system"
    USER = "user"
    AUTOMATIC = "automatic"

# ===================================================================
# BASIC SCHEMAS DEFINED LOCALLY
# ===================================================================

class QuotationBase(BaseModel):
    """Base quotation schema"""
    quote_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    coverage_type: Optional[str] = None
    coverage_amount: Optional[Decimal] = None
    effective_date: Optional[date] = None
    notes: Optional[str] = None

class QuotationCreate(QuotationBase):
    """Create quotation schema"""
    customer_email: str = Field(..., description="Customer email is required")
    coverage_amount: Decimal = Field(..., gt=0, description="Coverage amount must be positive")
    effective_date: date = Field(..., description="Effective date is required")

class QuotationUpdate(BaseModel):
    """Update quotation schema"""
    customer_name: Optional[str] = None
    coverage_type: Optional[str] = None
    coverage_amount: Optional[Decimal] = None
    effective_date: Optional[date] = None
    notes: Optional[str] = None

class QuotationResponse(QuotationBase):
    """Response quotation schema"""
    id: UUID
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QuotationSummary(BaseModel):
    """Summary quotation schema"""
    id: UUID
    quote_number: Optional[str] = None
    customer_name: Optional[str] = None
    status: Optional[str] = None
    total_premium: Optional[Decimal] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QuotationStatusUpdate(BaseModel):
    """Status update schema"""
    status: QuotationStatusEnum
    notes: Optional[str] = None

# ===================================================================
# TRY TO IMPORT FROM INDIVIDUAL SCHEMA FILES
# ===================================================================

# Try to import from quotation_schema.py
try:
    from .quotation_schema import *
    print("✅ Successfully imported from quotation_schema.py")
except ImportError as e:
    print(f"⚠️ Could not import from quotation_schema.py: {e}")
    print("Using fallback schemas defined locally")

# Try to import item schemas
try:
    from .quotation_item_schema import (
        QuotationItemBase,
        QuotationItemCreate,
        QuotationItemUpdate,
        QuotationItemResponse,
        QuotationItemSummary,
    )
    print("✅ Successfully imported quotation item schemas")
except ImportError as e:
    print(f"⚠️ Could not import quotation item schemas: {e}")
    
    # Create fallback item schemas
    class QuotationItemBase(BaseModel):
        quotation_id: UUID
        coverage_name: Optional[str] = None
        limit_amount: Optional[Decimal] = None
        
    class QuotationItemCreate(QuotationItemBase):
        pass
        
    class QuotationItemUpdate(BaseModel):
        coverage_name: Optional[str] = None
        limit_amount: Optional[Decimal] = None
        
    class QuotationItemResponse(QuotationItemBase):
        id: UUID
        created_at: Optional[datetime] = None
        
        class Config:
            from_attributes = True
            
    class QuotationItemSummary(BaseModel):
        id: UUID
        coverage_name: Optional[str] = None
        limit_amount: Optional[Decimal] = None
        
        class Config:
            from_attributes = True

# Try to import factor schemas
try:
    from .quotation_factor_schema import (
        QuotationFactorBase,
        QuotationFactorCreate,
        QuotationFactorUpdate,
        QuotationFactorResponse,
        QuotationFactorSummary,
        QuotationFactorBulkCreate,
        QuotationFactorNumericRequest,
        QuotationFactorBooleanRequest,
        QuotationFactorComplexRequest,
        QuotationFactorsByType,
        QuotationFactorsGrouped,
        QuotationFactorImpactAnalysis,
        QuotationFactorValidation,
    )
    print("✅ Successfully imported quotation factor schemas")
except ImportError as e:
    print(f"⚠️ Could not import quotation factor schemas: {e}")
    
    # Create fallback factor schemas
    class QuotationFactorBase(BaseModel):
        quotation_id: UUID
        factor_type: Optional[str] = None
        factor_name: Optional[str] = None
        factor_value: Optional[str] = None
        
    class QuotationFactorCreate(QuotationFactorBase):
        pass
        
    class QuotationFactorUpdate(BaseModel):
        factor_type: Optional[str] = None
        factor_name: Optional[str] = None
        factor_value: Optional[str] = None
        
    class QuotationFactorResponse(QuotationFactorBase):
        id: UUID
        created_at: Optional[datetime] = None
        
        class Config:
            from_attributes = True
            
    class QuotationFactorSummary(BaseModel):
        id: UUID
        factor_name: Optional[str] = None
        factor_value: Optional[str] = None
        
        class Config:
            from_attributes = True
    
    # Additional factor schemas that were missing
    class QuotationFactorBulkCreate(BaseModel):
        """Bulk create factors schema"""
        factors: List[QuotationFactorCreate] = Field(..., min_items=1, max_items=100)
        
    class QuotationFactorNumericRequest(BaseModel):
        """Numeric factor request schema"""
        quotation_id: UUID
        factor_name: str
        numeric_value: Decimal
        factor_type: Optional[str] = "numeric"
        
    class QuotationFactorBooleanRequest(BaseModel):
        """Boolean factor request schema"""
        quotation_id: UUID
        factor_name: str
        boolean_value: bool
        factor_type: Optional[str] = "boolean"
        
    class QuotationFactorComplexRequest(BaseModel):
        """Complex factor request schema"""
        quotation_id: UUID
        factor_name: str
        complex_value: Dict[str, Any]
        factor_type: Optional[str] = "complex"
        
    class QuotationFactorsByType(BaseModel):
        """Factors grouped by type schema"""
        quotation_id: UUID
        factors_by_type: Dict[str, List[QuotationFactorSummary]] = {}
        
    class QuotationFactorsGrouped(BaseModel):
        """Grouped factors schema"""
        quotation_id: UUID
        grouped_factors: Dict[str, List[Dict[str, Any]]] = {}
        
    class QuotationFactorImpactAnalysis(BaseModel):
        """Factor impact analysis schema"""
        factor_id: UUID
        impact_percentage: Decimal
        impact_amount: Decimal
        description: str
        
    class QuotationFactorValidation(BaseModel):
        """Factor validation schema"""
        factor_id: UUID
        is_valid: bool
        validation_errors: List[str] = []

# Try to import workflow schemas
try:
    from .quotation_workflow_log_schema import (
        QuotationWorkflowLogBase,
        QuotationWorkflowLogCreate,
        QuotationWorkflowLogResponse,
        QuotationWorkflowLogSummary,
    )
    print("✅ Successfully imported quotation workflow schemas")
except ImportError as e:
    print(f"⚠️ Could not import quotation workflow schemas: {e}")
    
    # Create fallback workflow schemas
    class QuotationWorkflowLogBase(BaseModel):
        quotation_id: UUID
        event: Optional[str] = None
        description: Optional[str] = None
        
    class QuotationWorkflowLogCreate(QuotationWorkflowLogBase):
        pass
        
    class QuotationWorkflowLogResponse(QuotationWorkflowLogBase):
        id: UUID
        created_at: Optional[datetime] = None
        
        class Config:
            from_attributes = True
            
    class QuotationWorkflowLogSummary(BaseModel):
        id: UUID
        event: Optional[str] = None
        created_at: Optional[datetime] = None
        
        class Config:
            from_attributes = True

# ===================================================================
# CALCULATION SCHEMAS
# ===================================================================

class QuotationCalculationRequest(BaseModel):
    """Calculation request schema"""
    quotation_id: UUID
    force_recalculate: bool = False
    calculation_options: Dict[str, Any] = {}

class QuotationCalculationResponse(BaseModel):
    """Calculation response schema"""
    quotation_id: UUID
    base_premium: Decimal = Decimal('0.00')
    total_premium: Decimal = Decimal('0.00')
    calculation_date: datetime
    calculation_details: Dict[str, Any] = {}

# ===================================================================
# BULK OPERATION SCHEMAS
# ===================================================================

class QuotationItemBulkCreate(BaseModel):
    """Bulk create items schema"""
    items: List[QuotationItemCreate]

class QuotationItemLocalizedResponse(QuotationItemResponse):
    """Localized item response"""
    coverage_name_ar: Optional[str] = None

class QuotationItemMetadataUpdate(BaseModel):
    """Item metadata update schema"""
    meta_data: Dict[str, Any] = {}

# ===================================================================
# EXPORT ALL SCHEMAS
# ===================================================================

# Aliases for backward compatibility
QuotationStatus = QuotationStatusEnum
QuotationCreateSchema = QuotationCreate
QuotationUpdateSchema = QuotationUpdate
QuotationResponseSchema = QuotationResponse

__all__ = [
    # Enums
    "QuotationStatusEnum",
    "QuotationStatus",  # Alias
    "FactorType",
    "WorkflowEvent",
    "EventCategory",
    
    # Main quotation schemas
    "QuotationBase",
    "QuotationCreate",
    "QuotationUpdate", 
    "QuotationResponse",
    "QuotationSummary",
    "QuotationStatusUpdate",
    
    # Calculation schemas
    "QuotationCalculationRequest",
    "QuotationCalculationResponse",
    
    # Quotation item schemas
    "QuotationItemBase",
    "QuotationItemCreate",
    "QuotationItemUpdate",
    "QuotationItemResponse",
    "QuotationItemSummary",
    "QuotationItemBulkCreate",
    "QuotationItemLocalizedResponse",
    "QuotationItemMetadataUpdate",
    
    # Factor schemas
    "QuotationFactorBase",
    "QuotationFactorCreate",
    "QuotationFactorUpdate",
    "QuotationFactorResponse",
    "QuotationFactorSummary",
    "QuotationFactorBulkCreate",
    "QuotationFactorNumericRequest",
    "QuotationFactorBooleanRequest", 
    "QuotationFactorComplexRequest",
    "QuotationFactorsByType",
    "QuotationFactorsGrouped",
    "QuotationFactorImpactAnalysis",
    "QuotationFactorValidation",
    
    # Workflow schemas
    "QuotationWorkflowLogBase",
    "QuotationWorkflowLogCreate",
    "QuotationWorkflowLogResponse",
    "QuotationWorkflowLogSummary",
    
    # Backward compatibility aliases
    "QuotationCreateSchema",
    "QuotationUpdateSchema",
    "QuotationResponseSchema",
]

# ===================================================================
# UTILITY FUNCTIONS
# ===================================================================

def get_available_schemas():
    """Get list of available schemas"""
    return __all__

def validate_schema_availability():
    """Check which schemas are available"""
    available = {}
    for schema_name in __all__:
        try:
            available[schema_name] = globals()[schema_name] is not None
        except KeyError:
            available[schema_name] = False
    return available

print(f"📋 Quotation schemas package loaded with {len(__all__)} schemas available")