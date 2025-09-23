# app/modules/pricing/benefits/models/benefit_calculation_rule_enums.py

"""
Enums for Benefit Calculation Rules

This module contains all enumeration classes used by the benefit calculation
rule models, services, and schemas. These enums provide type safety and
consistent value validation across the benefit calculation system.
"""

from enum import Enum


class RuleType(str, Enum):
    """Types of benefit calculation rules"""
    DEDUCTIBLE = "DEDUCTIBLE"
    COPAY = "COPAY"
    COINSURANCE = "COINSURANCE"
    COVERAGE_LIMIT = "COVERAGE_LIMIT"
    OUT_OF_POCKET = "OUT_OF_POCKET"
    BENEFIT_MAXIMUM = "BENEFIT_MAXIMUM"
    BENEFIT_MAX = "BENEFIT_MAX"  # Alias for BENEFIT_MAXIMUM
    ACCUMULATOR = "ACCUMULATOR"
    RESET = "RESET"
    ELIGIBILITY = "ELIGIBILITY"
    AUTHORIZATION = "AUTHORIZATION"
    PRICING = "PRICING"
    WAITING_PERIOD = "WAITING_PERIOD"
    PRE_EXISTING = "PRE_EXISTING"
    NETWORK_DIFFERENTIAL = "NETWORK_DIFFERENTIAL"


class CalculationMethod(str, Enum):
    """Methods used for performing calculations"""
    FORMULA = "FORMULA"
    LOOKUP_TABLE = "LOOKUP_TABLE"
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    TIERED = "TIERED"
    CONDITIONAL = "CONDITIONAL"
    MATRIX = "MATRIX"
    ALGORITHM = "ALGORITHM"


class RuleCategory(str, Enum):
    """Categories of calculation rules"""
    FINANCIAL = "FINANCIAL"
    UTILIZATION = "UTILIZATION"
    ELIGIBILITY = "ELIGIBILITY"
    AUTHORIZATION = "AUTHORIZATION"
    NETWORK = "NETWORK"
    TEMPORAL = "TEMPORAL"
    BENEFIT = "BENEFIT"
    COST_SHARING = "COST_SHARING"


class ResetFrequency(str, Enum):
    """How often rule accumulators reset"""
    NEVER = "NEVER"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"
    PLAN_YEAR = "PLAN_YEAR"
    LIFETIME = "LIFETIME"
    CONTRACT_YEAR = "CONTRACT_YEAR"
    CALENDAR_YEAR = "CALENDAR_YEAR"


class DeploymentStage(str, Enum):
    """Deployment stages for rules"""
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"
    PILOT = "PILOT"


class RuleStatus(str, Enum):
    """Status values for calculation rules"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"
    UNDER_REVIEW = "UNDER_REVIEW"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    REJECTED = "REJECTED"


class AuthorizationLevel(str, Enum):
    """Authorization levels for rule execution"""
    AUTO = "AUTO"
    SUPERVISOR = "SUPERVISOR"
    MANAGER = "MANAGER"
    MEDICAL_DIRECTOR = "MEDICAL_DIRECTOR"
    EXTERNAL_REVIEW = "EXTERNAL_REVIEW"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class FormulaComplexity(str, Enum):
    """Complexity levels for formulas"""
    SIMPLE = "SIMPLE"
    MODERATE = "MODERATE"
    COMPLEX = "COMPLEX"
    VERY_COMPLEX = "VERY_COMPLEX"


class RuleExecutionResult(str, Enum):
    """Results of rule execution"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    CONDITION_NOT_MET = "CONDITION_NOT_MET"


class AccumulatorType(str, Enum):
    """Types of accumulators used in rules"""
    DEDUCTIBLE = "DEDUCTIBLE"
    OUT_OF_POCKET = "OUT_OF_POCKET"
    BENEFIT_MAXIMUM = "BENEFIT_MAXIMUM"
    VISIT_COUNT = "VISIT_COUNT"
    FREQUENCY = "FREQUENCY"
    DOLLAR_AMOUNT = "DOLLAR_AMOUNT"
    LIFETIME = "LIFETIME"


class NetworkTier(str, Enum):
    """Network tiers for providers"""
    IN_NETWORK = "IN_NETWORK"
    OUT_OF_NETWORK = "OUT_OF_NETWORK"
    PREFERRED = "PREFERRED"
    STANDARD = "STANDARD"
    OUT_OF_AREA = "OUT_OF_AREA"
    EMERGENCY = "EMERGENCY"


class ComparisonOperator(str, Enum):
    """Operators for condition evaluation"""
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    GREATER_THAN = "GREATER_THAN"
    GREATER_THAN_OR_EQUAL = "GREATER_THAN_OR_EQUAL"
    LESS_THAN = "LESS_THAN"
    LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"
    IN = "IN"
    NOT_IN = "NOT_IN"
    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT_BETWEEN"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    IS_NULL = "IS_NULL"
    IS_NOT_NULL = "IS_NOT_NULL"


class CurrencyCode(str, Enum):
    """Currency codes supported by the system"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    SAR = "SAR"  # Saudi Riyal
    AED = "AED"  # UAE Dirham
    KWD = "KWD"  # Kuwaiti Dinar
    QAR = "QAR"  # Qatari Riyal
    OMR = "OMR"  # Omani Rial
    BHD = "BHD"  # Bahraini Dinar


class RoundingMethod(str, Enum):
    """Methods for rounding calculation results"""
    UP = "UP"
    DOWN = "DOWN"
    NEAREST = "NEAREST"
    BANKERS = "BANKERS"
    TRUNCATE = "TRUNCATE"


class ErrorHandlingStrategy(str, Enum):
    """Strategies for handling calculation errors"""
    FAIL_FAST = "FAIL_FAST"
    CONTINUE = "CONTINUE"
    USE_DEFAULT = "USE_DEFAULT"
    SKIP_RULE = "SKIP_RULE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    LOG_AND_CONTINUE = "LOG_AND_CONTINUE"


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    BLOCKER = "BLOCKER"


class WorkflowType(str, Enum):
    """Types of workflows that can be triggered"""
    APPROVAL = "APPROVAL"
    REVIEW = "REVIEW"
    NOTIFICATION = "NOTIFICATION"
    ESCALATION = "ESCALATION"
    AUDIT = "AUDIT"
    RECONCILIATION = "RECONCILIATION"


# Type aliases for backward compatibility
RuleTypeEnum = RuleType
CalculationMethodEnum = CalculationMethod
RuleCategoryEnum = RuleCategory
ResetFrequencyEnum = ResetFrequency
DeploymentStageEnum = DeploymentStage
RuleStatusEnum = RuleStatus