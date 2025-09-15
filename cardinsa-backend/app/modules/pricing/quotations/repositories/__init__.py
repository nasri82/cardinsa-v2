# app/modules/insurance/quotations/repositories/__init__.py

"""
Quotation Repositories Package

This package contains all repository classes for the quotations module,
providing comprehensive data access patterns for insurance quotation management.

Repositories included:
- QuotationRepository: Main quotation entity operations
- QuotationItemRepository: Coverage item operations
- QuotationFactorRepository: Pricing factor operations  
- QuotationVersionRepository: Version control operations
- QuotationLogRepository: Status logging operations
- QuotationWorkflowLogRepository: Workflow event operations
- QuotationDocumentRepository: Document management operations
- QuotationAttachmentRepository: File upload operations
- QuotationCoverageOptionRepository: Coverage option operations
- QuotationAuditLogRepository: Audit logging operations
"""

from .quotation_repository import QuotationRepository
from .quotation_item_repository import QuotationItemRepository
from .quotation_factor_repository import QuotationFactorRepository

# Note: Additional repositories would be imported here as they are created
# from .quotation_version_repository import QuotationVersionRepository
# from .quotation_log_repository import QuotationLogRepository
# from .quotation_workflow_log_repository import QuotationWorkflowLogRepository
# from .quotation_document_repository import QuotationDocumentRepository
# from .quotation_attachment_repository import QuotationAttachmentRepository
# from .quotation_coverage_option_repository import QuotationCoverageOptionRepository
# from .quotation_audit_log_repository import QuotationAuditLogRepository

# Export all repositories for easy importing
__all__ = [
    "QuotationRepository",
    "QuotationItemRepository", 
    "QuotationFactorRepository",
    # Additional repositories will be added here
    # "QuotationVersionRepository",
    # "QuotationLogRepository", 
    # "QuotationWorkflowLogRepository",
    # "QuotationDocumentRepository",
    # "QuotationAttachmentRepository",
    # "QuotationCoverageOptionRepository",
    # "QuotationAuditLogRepository"
]

# Repository operation patterns
REPOSITORY_PATTERNS = {
    "crud_operations": [
        "create", "get", "get_multi", "update", "delete"
    ],
    "quotation_specific": [
        "get_by_quote_number", "get_by_customer", "get_by_status",
        "update_status", "update_premium", "lock_quotation", "unlock_quotation"
    ],
    "item_specific": [
        "get_by_quotation", "update_display_order", "reorder_items",
        "get_localized_items", "bulk_create_items"
    ],
    "factor_specific": [
        "get_by_key", "get_by_type", "upsert_factor", "bulk_upsert_factors",
        "get_numeric_factors", "validate_factors"
    ],
    "search_operations": [
        "search_quotations", "search_items", "search_factors",
        "get_quotations_paginated", "get_by_filters"
    ],
    "analytics": [
        "get_statistics", "get_conversion_rate", "get_factor_impact_analysis",
        "get_workflow_metrics", "get_performance_data"
    ],
    "bulk_operations": [
        "create_bulk_items", "create_bulk_factors", "delete_all_by_quotation",
        "duplicate_items_to_quotation", "duplicate_factors_to_quotation"
    ]
}

# Common query filters
COMMON_FILTERS = {
    "quotation_filters": {
        "status": ["draft", "calculated", "approved", "converted", "rejected", "expired"],
        "customer_id": "UUID",
        "customer_email": "string",
        "product_code": "string",
        "assigned_to": "UUID",
        "created_from": "datetime",
        "created_to": "datetime",
        "min_premium": "decimal",
        "max_premium": "decimal",
        "is_locked": "boolean",
        "quote_expires_at": "datetime",
        "currency_code": "string(3)"
    },
    "item_filters": {
        "quotation_id": "UUID",
        "coverage_name": "string",
        "min_limit": "decimal",
        "max_limit": "decimal",
        "has_metadata": "boolean",
        "language": ["en", "ar"]
    },
    "factor_filters": {
        "quotation_id": "UUID",
        "factor_type": ["demographic", "risk", "discount", "loading", "geographic"],
        "is_numeric": "boolean",
        "key": "string",
        "has_impact_description": "boolean"
    }
}

# Database indexes for optimal performance
RECOMMENDED_INDEXES = {
    "quotations": [
        "idx_quotations_quote_number",
        "idx_quotations_customer_id",
        "idx_quotations_customer_email", 
        "idx_quotations_status",
        "idx_quotations_created_at",
        "idx_quotations_assigned_to",
        "idx_quotations_product_code",
        "idx_quotations_expires_at"
    ],
    "quotation_items": [
        "idx_quotation_items_quotation_id",
        "idx_quotation_items_display_order",
        "idx_quotation_items_coverage_name",
        "idx_quotation_items_limit_amount"
    ],
    "quotation_factors": [
        "idx_quotation_factors_quotation_id",
        "idx_quotation_factors_key",
        "idx_quotation_factors_type",
        "idx_quotation_factors_composite"
    ]
}

# Repository method signatures for documentation
METHOD_SIGNATURES = {
    "QuotationRepository": {
        "create_operations": {
            "create_quotation": "(quotation_data: QuotationCreate, created_by: UUID = None) -> Quotation",
            "create_with_items_and_factors": "(quotation_data: QuotationCreate, items_data: List[Dict] = None, factors_data: List[Dict] = None, created_by: UUID = None) -> Quotation"
        },
        "read_operations": {
            "get_by_quote_number": "(quote_number: str) -> Optional[Quotation]",
            "get_with_all_relations": "(quotation_id: UUID) -> Optional[Quotation]",
            "get_by_customer": "(customer_id: UUID, limit: int = 50) -> List[Quotation]",
            "get_by_status": "(status: QuotationStatus, limit: int = 100) -> List[Quotation]",
            "search_quotations": "(search_term: str, limit: int = 50) -> List[Quotation]"
        },
        "update_operations": {
            "update_status": "(quotation_id: UUID, new_status: QuotationStatus, updated_by: UUID = None, notes: str = None) -> Optional[Quotation]",
            "update_premium": "(quotation_id: UUID, premium_data: Dict[str, Decimal], updated_by: UUID = None) -> Optional[Quotation]",
            "lock_quotation": "(quotation_id: UUID, lock_reason: str, locked_by: UUID) -> Optional[Quotation]"
        },
        "analytics": {
            "get_statistics": "(date_from: date = None, date_to: date = None) -> Dict[str, Any]",
            "get_conversion_rate": "(date_from: date = None, date_to: date = None) -> float"
        }
    },
    "QuotationItemRepository": {
        "create_operations": {
            "create_item": "(item_data: QuotationItemCreate, created_by: UUID = None) -> QuotationItem",
            "create_bulk_items": "(items_data: List[QuotationItemCreate], created_by: UUID = None) -> List[QuotationItem]"
        },
        "read_operations": {
            "get_by_quotation": "(quotation_id: UUID, active_only: bool = True) -> List[QuotationItem]",
            "get_by_quotation_ordered": "(quotation_id: UUID) -> List[QuotationItem]",
            "get_localized_items": "(quotation_id: UUID, language: str = 'en') -> List[Dict[str, Any]]"
        },
        "update_operations": {
            "update_display_order": "(item_id: UUID, new_order: int, updated_by: UUID = None) -> Optional[QuotationItem]",
            "reorder_items": "(quotation_id: UUID, item_orders: Dict[UUID, int], updated_by: UUID = None) -> List[QuotationItem]",
            "update_metadata": "(item_id: UUID, metadata: Dict[str, Any], merge: bool = True, updated_by: UUID = None) -> Optional[QuotationItem]"
        }
    },
    "QuotationFactorRepository": {
        "create_operations": {
            "create_factor": "(factor_data: QuotationFactorCreate, created_by: UUID = None) -> QuotationFactor",
            "create_numeric_factor": "(quotation_id: UUID, key: str, value: float, factor_type: FactorType = None, impact_description: str = None, created_by: UUID = None) -> QuotationFactor",
            "create_bulk_factors": "(factors_data: List[QuotationFactorCreate], created_by: UUID = None) -> List[QuotationFactor]"
        },
        "read_operations": {
            "get_by_quotation": "(quotation_id: UUID, active_only: bool = True) -> List[QuotationFactor]",
            "get_by_key": "(quotation_id: UUID, key: str) -> Optional[QuotationFactor]",
            "get_by_quotation_and_type": "(quotation_id: UUID, factor_type: FactorType) -> List[QuotationFactor]",
            "get_numeric_factors": "(quotation_id: UUID) -> List[QuotationFactor]"
        },
        "update_operations": {
            "upsert_factor": "(quotation_id: UUID, key: str, value: Any, factor_type: FactorType = None, impact_description: str = None, updated_by: UUID = None) -> QuotationFactor",
            "bulk_upsert_factors": "(quotation_id: UUID, factors: Dict[str, Any], factor_type: FactorType = None, updated_by: UUID = None) -> List[QuotationFactor]"
        },
        "analysis": {
            "get_factor_impact_analysis": "(quotation_id: UUID) -> List[Dict[str, Any]]",
            "validate_factors": "(quotation_id: UUID) -> Dict[str, Any]"
        }
    }
}

# Repository usage examples
USAGE_EXAMPLES = {
    "basic_crud": {
        "create_quotation": """
# Create a new quotation
quotation_data = QuotationCreate(
    customer_name="John Doe",
    customer_email="john@example.com",
    product_code="MOTOR_COMP",
    currency_code="SAR"
)
quotation = quotation_repo.create_quotation(quotation_data, created_by=user_id)
        """,
        "get_by_status": """
# Get all approved quotations
approved_quotations = quotation_repo.get_by_status(QuotationStatus.APPROVED)
        """,
        "update_status": """
# Update quotation status
updated_quotation = quotation_repo.update_status(
    quotation_id=quotation.id,
    new_status=QuotationStatus.APPROVED,
    updated_by=user_id,
    notes="Approved after risk assessment"
)
        """
    },
    "advanced_operations": {
        "create_with_relations": """
# Create quotation with items and factors
quotation = quotation_repo.create_with_items_and_factors(
    quotation_data=quotation_data,
    items_data=[{
        "coverage_name": "Third Party Liability",
        "limit_amount": 100000.00,
        "display_order": 1
    }],
    factors_data=[{
        "key": "age_factor",
        "value": "1.2",
        "factor_type": "demographic"
    }],
    created_by=user_id
)
        """,
        "bulk_factor_operations": """
# Bulk upsert factors
factors = {
    "age_factor": 1.25,
    "location_factor": 0.9,
    "vehicle_type": "sedan"
}
updated_factors = factor_repo.bulk_upsert_factors(
    quotation_id=quotation.id,
    factors=factors,
    factor_type=FactorType.DEMOGRAPHIC,
    updated_by=user_id
)
        """,
        "analytics": """
# Get quotation statistics
stats = quotation_repo.get_statistics(
    date_from=datetime.now() - timedelta(days=30),
    date_to=datetime.now()
)

# Get factor impact analysis  
impact_analysis = factor_repo.get_factor_impact_analysis(quotation.id)
        """
    },
    "search_and_filter": {
        "paginated_search": """
# Get paginated quotations with filters
filters = {
    "status": "approved",
    "min_premium": 1000.00,
    "created_from": datetime.now() - timedelta(days=7)
}
quotations, total = quotation_repo.get_quotations_paginated(
    page=1, 
    per_page=20,
    filters=filters
)
        """,
        "localized_items": """
# Get localized items in Arabic
arabic_items = item_repo.get_localized_items(
    quotation_id=quotation.id,
    language="ar"
)
        """
    }
}

# Best practices for repository usage
BEST_PRACTICES = {
    "performance": [
        "Use pagination for large result sets",
        "Load relationships only when needed",
        "Use bulk operations for multiple records",
        "Index commonly queried fields",
        "Use database-level constraints where possible"
    ],
    "data_integrity": [
        "Always use transactions for multi-table operations",
        "Validate data at repository level",
        "Use soft deletes for audit trails",
        "Implement optimistic locking for concurrent updates",
        "Track all data changes with audit fields"
    ],
    "scalability": [
        "Use read replicas for reporting queries",
        "Implement caching for frequently accessed data",
        "Archive old data periodically",
        "Use database partitioning for large tables",
        "Monitor query performance and optimize slow queries"
    ],
    "security": [
        "Always validate user permissions before operations",
        "Use parameterized queries to prevent SQL injection",
        "Log all data access for audit purposes",
        "Encrypt sensitive data at rest and in transit",
        "Implement row-level security where applicable"
    ]
}