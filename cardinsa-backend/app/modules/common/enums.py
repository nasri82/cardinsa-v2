from enum import StrEnum

class RoleEnum(StrEnum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    UNDERWRITER = "underwriter"
    BROKER = "broker"
    MEMBER = "member"
    GARAGE = "garage"
    PROVIDER = "provider"

class PolicyStatusEnum(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class ClaimStatusEnum(StrEnum):
    NEW = "new"
    REVIEW = "review"
    NEEDS_INFO = "needs_info"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"

class DocumentStatusEnum(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ProviderCategoryEnum(StrEnum):
    MEDICAL = "medical"
    MOTOR = "motor"
