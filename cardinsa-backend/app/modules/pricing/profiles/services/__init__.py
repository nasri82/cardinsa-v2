# app/modules/pricing/profiles/services/__init__.py
from .pricing_profile_service import PricingProfileService
from .pricing_profile_validation_service import PricingProfileValidationService
from .pricing_rules_service import PricingRulesService

# Import RuleEvaluationService only if it exists
try:
    from .rule_evaluation_service import RuleEvaluationService
    RULE_EVALUATION_AVAILABLE = True
except ImportError:
    RuleEvaluationService = None
    RULE_EVALUATION_AVAILABLE = False

# Build __all__ list dynamically based on what's available
__all__ = [
    "PricingProfileService",
    "PricingProfileValidationService", 
    "PricingRulesService"  # Fixed: Added missing comma here
]

# Add RuleEvaluationService if available
if RULE_EVALUATION_AVAILABLE:
    __all__.append("RuleEvaluationService")