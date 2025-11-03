# app/core/enums.py

"""
Core Enums Module
================

Base enumerations and common enum patterns used throughout the insurance system.
Provides consistent enum base classes and frequently used enums.
"""

from enum import Enum, IntEnum, Flag, auto
from typing import List, Dict, Any, Optional, Type
import json


class BaseEnum(Enum):
    """
    Enhanced base enum class with additional utility methods
    
    Provides common functionality for all enums in the system:
    - JSON serialization
    - Display names
    - Validation
    - Choice generation for forms
    """
    
    def __str__(self) -> str:
        """Return the enum value as string"""
        return str(self.value)
    
    def __repr__(self) -> str:
        """Return detailed representation"""
        return f"{self.__class__.__name__}.{self.name}"
    
    @classmethod
    def choices(cls) -> List[tuple]:
        """Return choices suitable for form fields"""
        return [(item.value, item.display_name) for item in cls]
    
    @classmethod
    def values(cls) -> List[str]:
        """Return list of enum values"""
        return [item.value for item in cls]
    
    @classmethod
    def names(cls) -> List[str]:
        """Return list of enum names"""
        return [item.name for item in cls]
    
    @classmethod
    def dict(cls) -> Dict[str, str]:
        """Return dict mapping values to display names"""
        return {item.value: item.display_name for item in cls}
    
    @classmethod
    def from_value(cls, value: str, default=None):
        """Get enum member from value with optional default"""
        try:
            return cls(value)
        except ValueError:
            if default is not None:
                return default
            raise ValueError(f"Invalid value '{value}' for {cls.__name__}")
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if value is valid for this enum"""
        try:
            cls(value)
            return True
        except ValueError:
            return False
    
    @property
    def display_name(self) -> str:
        """Human-readable display name"""
        # Default: convert SNAKE_CASE to Title Case
        return self.name.replace('_', ' ').title()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'value': self.value,
            'display_name': self.display_name
        }
    
    def __json__(self):
        """JSON serialization support"""
        return self.value


class StatusEnum(BaseEnum):
    """Base enum for status fields"""
    pass


class TypeEnum(BaseEnum):
    """Base enum for type fields"""
    pass


# =================================================================
# COMMON STATUS ENUMS
# =================================================================

class ActiveStatus(StatusEnum):
    """Generic active/inactive status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    
    @property
    def display_name(self) -> str:
        return {
            self.ACTIVE: "Active",
            self.INACTIVE: "Inactive"
        }[self]


class ProcessingStatus(StatusEnum):
    """Generic processing status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
    @property
    def display_name(self) -> str:
        return {
            self.PENDING: "Pending",
            self.IN_PROGRESS: "In Progress",
            self.COMPLETED: "Completed",
            self.FAILED: "Failed",
            self.CANCELLED: "Cancelled"
        }[self]


class ApprovalStatus(StatusEnum):
    """Generic approval status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_REVISION = "pending_revision"
    
    @property
    def display_name(self) -> str:
        return {
            self.DRAFT: "Draft",
            self.SUBMITTED: "Submitted",
            self.UNDER_REVIEW: "Under Review", 
            self.APPROVED: "Approved",
            self.REJECTED: "Rejected",
            self.PENDING_REVISION: "Pending Revision"
        }[self]


# =================================================================
# INSURANCE-SPECIFIC ENUMS
# =================================================================

class InsuranceType(TypeEnum):
    """Types of insurance products"""
    MEDICAL = "medical"
    MOTOR = "motor"
    LIFE = "life"
    PROPERTY = "property"
    TRAVEL = "travel"
    MARINE = "marine"
    LIABILITY = "liability"
    DISABILITY = "disability"
    CRITICAL_ILLNESS = "critical_illness"
    DENTAL = "dental"
    VISION = "vision"
    
    @property
    def display_name(self) -> str:
        return {
            self.MEDICAL: "Medical Insurance",
            self.MOTOR: "Motor Insurance",
            self.LIFE: "Life Insurance",
            self.PROPERTY: "Property Insurance",
            self.TRAVEL: "Travel Insurance",
            self.MARINE: "Marine Insurance",
            self.LIABILITY: "Liability Insurance",
            self.DISABILITY: "Disability Insurance",
            self.CRITICAL_ILLNESS: "Critical Illness",
            self.DENTAL: "Dental Insurance",
            self.VISION: "Vision Insurance"
        }[self]


class PolicyStatus(StatusEnum):
    """Insurance policy status"""
    QUOTE = "quote"
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    LAPSED = "lapsed"
    
    @property
    def display_name(self) -> str:
        return {
            self.QUOTE: "Quote",
            self.PENDING: "Pending",
            self.ACTIVE: "Active",
            self.SUSPENDED: "Suspended",
            self.CANCELLED: "Cancelled",
            self.EXPIRED: "Expired",
            self.TERMINATED: "Terminated",
            self.LAPSED: "Lapsed"
        }[self]


class ClaimStatus(StatusEnum):
    """Insurance claim status"""
    REPORTED = "reported"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    APPROVED = "approved"
    REJECTED = "rejected"
    SETTLED = "settled"
    CLOSED = "closed"
    REOPENED = "reopened"
    
    @property
    def display_name(self) -> str:
        return {
            self.REPORTED: "Reported",
            self.ACKNOWLEDGED: "Acknowledged",
            self.INVESTIGATING: "Under Investigation",
            self.APPROVED: "Approved",
            self.REJECTED: "Rejected",
            self.SETTLED: "Settled",
            self.CLOSED: "Closed",
            self.REOPENED: "Reopened"
        }[self]


class UnderwritingDecision(StatusEnum):
    """Underwriting decisions"""
    ACCEPT = "accept"
    DECLINE = "decline"
    REFER = "refer"
    ACCEPT_WITH_CONDITIONS = "accept_with_conditions"
    ACCEPT_WITH_LOADING = "accept_with_loading"
    ACCEPT_WITH_EXCLUSIONS = "accept_with_exclusions"
    POSTPONE = "postpone"
    
    @property
    def display_name(self) -> str:
        return {
            self.ACCEPT: "Accept",
            self.DECLINE: "Decline",
            self.REFER: "Refer to Underwriter",
            self.ACCEPT_WITH_CONDITIONS: "Accept with Conditions",
            self.ACCEPT_WITH_LOADING: "Accept with Loading",
            self.ACCEPT_WITH_EXCLUSIONS: "Accept with Exclusions",
            self.POSTPONE: "Postpone"
        }[self]


# =================================================================
# DEMOGRAPHIC ENUMS
# =================================================================

class Gender(BaseEnum):
    """Gender categories"""
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    PREFER_NOT_TO_SAY = "N"
    
    @property
    def display_name(self) -> str:
        return {
            self.MALE: "Male",
            self.FEMALE: "Female",
            self.OTHER: "Other",
            self.PREFER_NOT_TO_SAY: "Prefer not to say"
        }[self]


class MaritalStatus(BaseEnum):
    """Marital status categories"""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"
    DOMESTIC_PARTNERSHIP = "domestic_partnership"
    
    @property
    def display_name(self) -> str:
        return {
            self.SINGLE: "Single",
            self.MARRIED: "Married",
            self.DIVORCED: "Divorced",
            self.WIDOWED: "Widowed",
            self.SEPARATED: "Separated",
            self.DOMESTIC_PARTNERSHIP: "Domestic Partnership"
        }[self]


# =================================================================
# CURRENCY AND FINANCIAL ENUMS
# =================================================================

class CurrencyCode(BaseEnum):
    """ISO 4217 Currency Codes"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    AUD = "AUD"
    CAD = "CAD"
    CHF = "CHF"
    CNY = "CNY"
    AED = "AED"
    SAR = "SAR"
    LBP = "LBP"
    
    @property
    def display_name(self) -> str:
        return {
            self.USD: "US Dollar",
            self.EUR: "Euro",
            self.GBP: "British Pound",
            self.JPY: "Japanese Yen",
            self.AUD: "Australian Dollar",
            self.CAD: "Canadian Dollar",
            self.CHF: "Swiss Franc",
            self.CNY: "Chinese Yuan",
            self.AED: "UAE Dirham",
            self.SAR: "Saudi Riyal",
            self.LBP: "Lebanese Pound"
        }[self]


class PaymentFrequency(BaseEnum):
    """Premium payment frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    
    @property
    def display_name(self) -> str:
        return {
            self.MONTHLY: "Monthly",
            self.QUARTERLY: "Quarterly",
            self.SEMI_ANNUALLY: "Semi-Annually",
            self.ANNUALLY: "Annually"
        }[self]


class PaymentMethod(BaseEnum):
    """Payment methods"""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIRECT_DEBIT = "direct_debit"
    CHECK = "check"
    ONLINE_PAYMENT = "online_payment"
    
    @property
    def display_name(self) -> str:
        return {
            self.CASH: "Cash",
            self.CREDIT_CARD: "Credit Card",
            self.DEBIT_CARD: "Debit Card",
            self.BANK_TRANSFER: "Bank Transfer",
            self.DIRECT_DEBIT: "Direct Debit",
            self.CHECK: "Check",
            self.ONLINE_PAYMENT: "Online Payment"
        }[self]


# =================================================================
# PRIORITY AND SEVERITY ENUMS
# =================================================================

class Priority(IntEnum):
    """Priority levels (as integers for sorting)"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5
    
    @property
    def display_name(self) -> str:
        return {
            self.LOW: "Low",
            self.MEDIUM: "Medium", 
            self.HIGH: "High",
            self.CRITICAL: "Critical",
            self.URGENT: "Urgent"
        }[self]


class Severity(BaseEnum):
    """Severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"
    
    @property
    def display_name(self) -> str:
        return {
            self.MINOR: "Minor",
            self.MODERATE: "Moderate",
            self.MAJOR: "Major", 
            self.CRITICAL: "Critical",
            self.CATASTROPHIC: "Catastrophic"
        }[self]


# =================================================================
# DOCUMENT AND COMMUNICATION ENUMS
# =================================================================

class DocumentType(BaseEnum):
    """Document types"""
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    IMAGE = "image"
    EMAIL = "email"
    FORM = "form"
    CERTIFICATE = "certificate"
    REPORT = "report"
    
    @property
    def display_name(self) -> str:
        return {
            self.PDF: "PDF Document",
            self.WORD: "Word Document",
            self.EXCEL: "Excel Spreadsheet",
            self.IMAGE: "Image",
            self.EMAIL: "Email",
            self.FORM: "Form",
            self.CERTIFICATE: "Certificate",
            self.REPORT: "Report"
        }[self]


class CommunicationChannel(BaseEnum):
    """Communication channels"""
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    MAIL = "mail"
    PORTAL = "portal"
    MOBILE_APP = "mobile_app"
    
    @property
    def display_name(self) -> str:
        return {
            self.EMAIL: "Email",
            self.SMS: "SMS",
            self.PHONE: "Phone",
            self.MAIL: "Mail",
            self.PORTAL: "Customer Portal",
            self.MOBILE_APP: "Mobile App"
        }[self]


# =================================================================
# UTILITY FUNCTIONS
# =================================================================

def get_enum_choices(enum_class: Type[BaseEnum]) -> List[tuple]:
    """Get choices for any BaseEnum class"""
    return enum_class.choices()


def validate_enum_value(enum_class: Type[BaseEnum], value: str) -> bool:
    """Validate if value is valid for given enum class"""
    return enum_class.is_valid(value)


def get_all_enums() -> Dict[str, Type[BaseEnum]]:
    """Get all enum classes defined in this module"""
    import inspect
    current_module = inspect.getmodule(inspect.currentframe())
    
    enums = {}
    for name, obj in inspect.getmembers(current_module):
        if (inspect.isclass(obj) and 
            issubclass(obj, BaseEnum) and 
            obj is not BaseEnum):
            enums[name] = obj
    
    return enums


# Export all enums and utilities
__all__ = [
    # Base classes
    'BaseEnum', 'StatusEnum', 'TypeEnum',
    
    # Status enums
    'ActiveStatus', 'ProcessingStatus', 'ApprovalStatus',
    
    # Insurance enums
    'InsuranceType', 'PolicyStatus', 'ClaimStatus', 'UnderwritingDecision',
    
    # Demographic enums
    'Gender', 'MaritalStatus',
    
    # Financial enums
    'CurrencyCode', 'PaymentFrequency', 'PaymentMethod',
    
    # Priority/Severity enums
    'Priority', 'Severity',
    
    # Document/Communication enums
    'DocumentType', 'CommunicationChannel',
    
    # Utility functions
    'get_enum_choices', 'validate_enum_value', 'get_all_enums'
]