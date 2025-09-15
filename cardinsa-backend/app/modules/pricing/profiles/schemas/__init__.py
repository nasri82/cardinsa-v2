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
]