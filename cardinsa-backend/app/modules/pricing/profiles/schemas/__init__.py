# app/modules/pricing/profiles/schemas/__init__.py

"""
Pricing Profile Schemas

This module contains all Pydantic schemas for the pricing profiles API.
Schemas are organized by functionality and provide comprehensive validation
for all pricing-related operations.

Profile Schemas:
- QuotationPricingProfileCreate/Update/Response: Main profile operations
- QuotationPricingProfileSummary: Lightweight profile data
- QuotationPricingProfileBulkCreate: Bulk operations
- QuotationPricingProfileStatusUpdate: Status management
- QuotationPricingProfileValidation: Validation results

Rule Schemas:
- QuotationPricingRuleCreate/Update/Response: Rule operations
- QuotationPricingRuleEvaluation: Rule testing
- QuotationPricingRuleBulkCreate: Bulk rule operations
- QuotationPricingRulePriorityUpdate: Priority management

Relationship Schemas:
- QuotationPricingProfileRuleCreate/Response: Profile-rule links
- QuotationPricingRuleAgeBracketCreate/Response: Age-specific rules

History Schemas:
- QuotationPricingProfileHistoryResponse: Profile audit trail
- QuotationPricingRulesHistoryResponse: Rule audit trail

Analytics Schemas:
- PricingProfileAnalytics: Profile statistics
- PricingRuleAnalytics: Rule statistics
- PricingProfileSearchParams: Search functionality
- PricingRuleSearchParams: Rule search

Import/Export Schemas:
- PricingDataExport: Data export
- PricingDataImport: Data import

Calculation Schemas:
- PremiumCalculationRequest: Premium calculation input
- PremiumCalculationResponse: Premium calculation results
"""

# Add missing imports for schemas that are being imported but don't exist
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

# Import enums first
from .quotation_pricing_profile_schema import (
    InsuranceType,
    ProfileStatus, 
    CurrencyCode
)

from .quotation_pricing_rule_schema import (
    RuleType,
    ComparisonOperator,
    AdjustmentType
)

# Import profile schemas
from .quotation_pricing_profile_schema import (
    QuotationPricingProfileBase,
    QuotationPricingProfileCreate,
    QuotationPricingProfileUpdate,
    QuotationPricingProfileResponse,
    QuotationPricingProfileSummary,
    QuotationPricingProfileBulkCreate,
    QuotationPricingProfileStatusUpdate,
    QuotationPricingProfileValidation,
    QuotationPricingProfileWithRules,
    # Add the aliases
    PricingProfileBase,
    PricingProfileCreate,
    PricingProfileUpdate,
    PricingProfileResponse,
    PricingProfileSummary,
    PricingProfileBulkCreate,
    PricingProfileStatusUpdate,
    PricingProfileValidation,
    PricingProfileWithRules,
)

# Import rule schemas
from .quotation_pricing_rule_schema import (
    QuotationPricingRuleBase,
    QuotationPricingRuleCreate,
    QuotationPricingRuleUpdate,
    QuotationPricingRuleResponse,
    QuotationPricingRuleEvaluation,
    QuotationPricingRuleEvaluationResult,
    QuotationPricingRuleBulkCreate,
    QuotationPricingRulePriorityUpdate,
    QuotationPricingProfileRuleBase,
    QuotationPricingProfileRuleCreate,
    QuotationPricingProfileRuleResponse,
    QuotationPricingRuleAgeBracketBase,
    QuotationPricingRuleAgeBracketCreate,
    QuotationPricingRuleAgeBracketResponse,
    # Add these new evaluation classes
    RuleEvaluationRequest,
    RuleEvaluationResult,
    BatchEvaluationRequest,
    BatchEvaluationResult,
    BatchEvaluationProfileRequest,
    BatchEvaluationProfileResult,
    # Add the aliases
    PricingRuleBase,
    PricingRuleCreate,
    PricingRuleUpdate,
    PricingRuleResponse,
    PricingRuleEvaluation,
    PricingRuleEvaluationResult,
    PricingRuleBulkCreate,
    PricingRulePriorityUpdate,
)

# Import history schemas
from .quotation_pricing_history_schema import (
    HistoryOperation,
    QuotationPricingProfileHistoryBase,
    QuotationPricingProfileHistoryResponse,
    QuotationPricingRulesHistoryBase,
    QuotationPricingRulesHistoryResponse,
    PricingProfileAnalytics,
    PricingRuleAnalytics,
    PricingProfileSearchParams,
    PricingRuleSearchParams,
    PricingDataExport,
    PricingDataImport,
    PremiumCalculationRequest,
    PremiumCalculationResponse
)

# ADD MISSING SCHEMAS that your service is trying to import

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


class PricingProfileCloneRequest(BaseModel):
    """Schema for cloning pricing profiles"""
    
    new_name: str = Field(..., description="Name for the cloned profile")
    new_code: Optional[str] = Field(None, description="Code for cloned profile (auto-generated if not provided)")
    include_rules: bool = Field(True, description="Clone associated rules")
    customizations: Optional[Dict[str, Any]] = Field(None, description="Field customizations for clone")


class PricingProfileComparisonResult(BaseModel):
    """Schema for profile comparison results - THIS WAS THE MISSING ONE CAUSING THE ERROR"""
    
    profile1_id: UUID = Field(..., description="First profile ID")
    profile2_id: UUID = Field(..., description="Second profile ID")
    compatibility_score: float = Field(..., description="Compatibility score (0-100)")
    differences: Dict[str, Any] = Field(default_factory=dict, description="Field differences")
    similarities: Dict[str, Any] = Field(default_factory=dict, description="Common fields")
    recommendations: List[str] = Field(default_factory=list, description="Merge recommendations")


class PricingProfileComparison(BaseModel):
    """Schema for profile comparison request"""
    
    profile_id_1: UUID = Field(..., description="First profile to compare")
    profile_id_2: UUID = Field(..., description="Second profile to compare")
    include_rules: bool = Field(True, description="Include rule comparison")
    detailed_analysis: bool = Field(False, description="Perform detailed analysis")


__all__ = [
    # Enums
    "InsuranceType",
    "ProfileStatus", 
    "CurrencyCode",
    "RuleType",
    "ComparisonOperator",
    "AdjustmentType",
    "HistoryOperation",
    
    # Profile schemas (full names)
    "QuotationPricingProfileBase",
    "QuotationPricingProfileCreate",
    "QuotationPricingProfileUpdate", 
    "QuotationPricingProfileResponse",
    "QuotationPricingProfileSummary",
    "QuotationPricingProfileBulkCreate",
    "QuotationPricingProfileStatusUpdate",
    "QuotationPricingProfileValidation",
    "QuotationPricingProfileWithRules",
    
    # Profile schema aliases (short names)
    "PricingProfileBase",
    "PricingProfileCreate",
    "PricingProfileUpdate",
    "PricingProfileResponse",
    "PricingProfileSummary",
    "PricingProfileBulkCreate",
    "PricingProfileStatusUpdate",
    "PricingProfileValidation",
    "PricingProfileWithRules",
    
    # Rule schemas (full names)
    "QuotationPricingRuleBase",
    "QuotationPricingRuleCreate",
    "QuotationPricingRuleUpdate",
    "QuotationPricingRuleResponse",
    "QuotationPricingRuleEvaluation",
    "QuotationPricingRuleEvaluationResult",
    "QuotationPricingRuleBulkCreate",
    "QuotationPricingRulePriorityUpdate",
    
    # Rule schema aliases (short names)
    "PricingRuleBase",
    "PricingRuleCreate",
    "PricingRuleUpdate",
    "PricingRuleResponse",
    "PricingRuleEvaluation",
    "PricingRuleEvaluationResult",
    "PricingRuleBulkCreate",
    "PricingRulePriorityUpdate",
    
    # Relationship schemas
    "QuotationPricingProfileRuleBase",
    "QuotationPricingProfileRuleCreate",
    "QuotationPricingProfileRuleResponse",
    "QuotationPricingRuleAgeBracketBase",
    "QuotationPricingRuleAgeBracketCreate",
    "QuotationPricingRuleAgeBracketResponse",
    
    # History schemas
    "QuotationPricingProfileHistoryResponse",
    "QuotationPricingRulesHistoryResponse",
    
    # Analytics and search
    "PricingProfileAnalytics",
    "PricingRuleAnalytics", 
    "PricingProfileSearchParams",
    "PricingRuleSearchParams",
    
    # Import/Export
    "PricingDataExport",
    "PricingDataImport",
    
    # Calculations
    "PremiumCalculationRequest",
    "PremiumCalculationResponse",

    "RuleEvaluationRequest",
    "RuleEvaluationResult",
    "BatchEvaluationRequest",
    "BatchEvaluationResult",
    "BatchEvaluationProfileRequest",
    "BatchEvaluationProfileResult",
    
    # ADDED MISSING SCHEMAS
    "PricingProfileSearchFilters",
    "PricingProfileCloneRequest", 
    "PricingProfileComparisonResult",  # This was the main one causing the error
    "PricingProfileComparison",
]