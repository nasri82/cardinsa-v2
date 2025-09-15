# app/modules/pricing/profiles/models/__init__.py
from .quotation_pricing_profile_model import QuotationPricingProfile
from .quotation_pricing_rule_model import QuotationPricingRule
from .quotation_pricing_profile_rule_model import QuotationPricingProfileRule

# History models (if they exist)
try:
    from .quotation_pricing_profile_history_model import QuotationPricingProfileHistory
    from .quotation_pricing_rules_history_model import QuotationPricingRulesHistory
    HISTORY_MODELS_AVAILABLE = True
except ImportError:
    # History models not available, create placeholder classes
    QuotationPricingProfileHistory = None
    QuotationPricingRulesHistory = None
    HISTORY_MODELS_AVAILABLE = False

# Age bracket model (if it exists)
try:
    from .quotation_pricing_rule_age_bracket_model import QuotationPricingRuleAgeBracket
    AGE_BRACKET_MODEL_AVAILABLE = True
except ImportError:
    QuotationPricingRuleAgeBracket = None
    AGE_BRACKET_MODEL_AVAILABLE = False

__all__ = [
    "QuotationPricingProfile",
    "QuotationPricingRule", 
    "QuotationPricingProfileRule"
]

# Add history models to exports if available
if HISTORY_MODELS_AVAILABLE:
    __all__.extend([
        "QuotationPricingProfileHistory",
        "QuotationPricingRulesHistory"
    ])

# Add age bracket model to exports if available
if AGE_BRACKET_MODEL_AVAILABLE:
    __all__.append("QuotationPricingRuleAgeBracket")