# app/modules/insurance/quotations/services/__init__.py

"""
Quotation Services Package

This package contains all service classes for the quotations module,
providing comprehensive business logic orchestration for insurance 
quotation management operations.

Services included:
- QuotationService: Main quotation business logic orchestration
- QuotationItemService: Coverage item management and validation
- QuotationFactorService: Pricing factor analysis and management
- QuotationWorkflowService: Workflow automation and event tracking
- Additional services for complete quotation lifecycle management
"""

from .quotation_service import QuotationService
from .quotation_item_service import QuotationItemService
from .quotation_factor_service import QuotationFactorService
from .quotation_workflow_service import QuotationWorkflowService

# Additional services would be imported here as they are created
# from .quotation_document_service import QuotationDocumentService
# from .quotation_calculation_service import QuotationCalculationService
# from .quotation_validation_service import QuotationValidationService
# from .quotation_notification_service import QuotationNotificationService

# Export all services for easy importing
__all__ = [
    "QuotationService",
    "QuotationItemService", 
    "QuotationFactorService",
    "QuotationWorkflowService",
    # Additional services will be added here
    # "QuotationDocumentService",
    # "QuotationCalculationService",
    # "QuotationValidationService", 
    # "QuotationNotificationService"
]

# Service orchestration patterns
SERVICE_ORCHESTRATION = {
    "quotation_creation": {
        "primary_service": "QuotationService",
        "supporting_services": ["QuotationItemService", "QuotationFactorService", "QuotationWorkflowService"],
        "workflow": [
            "validate_quotation_data",
            "create_quotation_record", 
            "initialize_default_factors",
            "log_creation_event",
            "trigger_automated_workflows"
        ]
    },
    "premium_calculation": {
        "primary_service": "QuotationService",
        "supporting_services": ["QuotationFactorService", "QuotationWorkflowService"],
        "workflow": [
            "validate_calculation_prerequisites",
            "gather_pricing_factors",
            "calculate_premium_components", 
            "update_quotation_premium",
            "log_calculation_event"
        ]
    },
    "status_management": {
        "primary_service": "QuotationService",
        "supporting_services": ["QuotationWorkflowService"],
        "workflow": [
            "validate_status_transition",
            "update_quotation_status",
            "log_status_change",
            "trigger_status_workflows",
            "schedule_reminders"
        ]
    }
}

# Business rules and constraints
BUSINESS_RULES = {
    "quotation_creation": {
        "required_fields": ["customer_name"],
        "validations": [
            "unique_quote_number",
            "valid_email_format", 
            "supported_currency_code",
            "future_expiry_date"
        ],
        "automatic_actions": [
            "generate_quote_number",
            "initialize_factors",
            "log_creation",
            "send_welcome_email"
        ]
    },
    "item_management": {
        "constraints": [
            "at_least_one_coverage_name",
            "non_negative_limit_amount",
            "unique_coverage_per_quotation",
            "sequential_display_orders"
        ],
        "multilingual_support": ["coverage_name", "notes"],
        "metadata_validation": ["json_format", "reasonable_size"]
    },
    "factor_management": {
        "factor_types": [
            "demographic", "risk", "discount", "loading", 
            "geographic", "behavioral", "product", "regulatory"
        ],
        "value_constraints": {
            "discount_factors": "value <= 1.0",
            "loading_factors": "value >= 1.0", 
            "numeric_factors": "parseable_as_number"
        },
        "required_factors": ["base_rate"],
        "impact_analysis": ["automatic_calculation", "transparency_descriptions"]
    },
    "workflow_automation": {
        "trigger_events": [
            "quotation_created", "premium_calculated", "status_changed",
            "quotation_approved", "quotation_expired", "quotation_converted"
        ],
        "automated_actions": [
            "email_notifications", "document_generation", "agent_assignment",
            "reminder_scheduling", "policy_creation", "archival_processes"
        ],
        "performance_monitoring": [
            "event_tracking", "bottleneck_identification", "efficiency_scoring"
        ]
    }
}

# Service dependencies and injection patterns
SERVICE_DEPENDENCIES = {
    "QuotationService": {
        "repositories": ["QuotationRepository", "QuotationItemRepository", "QuotationFactorRepository"],
        "services": ["QuotationItemService", "QuotationFactorService", "QuotationWorkflowService"],
        "external_integrations": ["EmailService", "PolicyService", "DocumentService"]
    },
    "QuotationItemService": {
        "repositories": ["QuotationItemRepository", "QuotationRepository"],
        "services": [],
        "validations": ["multilingual_content", "display_order_integrity", "metadata_structure"]
    },
    "QuotationFactorService": {
        "repositories": ["QuotationFactorRepository", "QuotationRepository"],
        "services": [],
        "calculations": ["impact_analysis", "factor_validation", "business_rule_checking"]
    },
    "QuotationWorkflowService": {
        "repositories": ["QuotationWorkflowLogRepository", "QuotationRepository"],
        "services": [],
        "integrations": ["TaskScheduler", "NotificationService", "PerformanceMonitor"]
    }
}

# Common error handling patterns
ERROR_HANDLING_PATTERNS = {
    "validation_errors": {
        "status_code": 400,
        "error_type": "ValidationError",
        "response_format": "detailed_field_errors"
    },
    "business_logic_errors": {
        "status_code": 422,
        "error_type": "BusinessLogicError", 
        "response_format": "business_rule_violation"
    },
    "not_found_errors": {
        "status_code": 404,
        "error_type": "NotFoundError",
        "response_format": "resource_not_found"
    },
    "conflict_errors": {
        "status_code": 409,
        "error_type": "ConflictError",
        "response_format": "resource_conflict"
    }
}

# Performance optimization strategies
PERFORMANCE_STRATEGIES = {
    "database_optimization": [
        "selective_relationship_loading",
        "pagination_for_large_results",
        "indexed_query_patterns",
        "batch_operations_for_bulk_actions"
    ],
    "business_logic_optimization": [
        "lazy_validation_execution",
        "cached_factor_calculations",
        "async_workflow_processing",
        "parallel_service_execution"
    ],
    "workflow_optimization": [
        "event_batching",
        "smart_reminder_scheduling",
        "automated_bottleneck_detection",
        "performance_metric_tracking"
    ]
}

# Service usage examples and patterns
USAGE_EXAMPLES = {
    "complete_quotation_creation": """
# Create quotation with items and automated workflows
quotation_service = QuotationService(db)

quotation = await quotation_service.create_quotation_with_items(
    quotation_data=QuotationCreate(
        customer_name="John Doe",
        customer_email="john@example.com",
        product_code="MOTOR_COMP",
        currency_code="SAR"
    ),
    items_data=[
        {
            "coverage_name": "Third Party Liability",
            "coverage_name_ar": "تأمين الطرف الثالث", 
            "limit_amount": 100000.00
        }
    ],
    created_by=user_id
)
    """,
    "premium_calculation_with_factors": """
# Calculate premium with custom factors
factor_service = QuotationFactorService(db)

# Add pricing factors
await factor_service.bulk_upsert_factors(
    quotation_id=quotation.id,
    factors={
        "age_factor": 1.25,
        "location_factor": 0.9,
        "vehicle_type": "sedan"
    },
    factor_type=FactorType.DEMOGRAPHIC,
    updated_by=user_id
)

# Calculate premium
calculated_quotation = await quotation_service.calculate_premium(
    quotation_id=quotation.id,
    calculation_request=QuotationCalculationRequest(
        recalculate_all=True
    ),
    calculated_by=user_id
)
    """,
    "workflow_automation": """
# Automated workflow management
workflow_service = QuotationWorkflowService(db)

# Trigger automated workflows on status change
triggered_workflows = await workflow_service.trigger_automated_workflows(
    quotation_id=quotation.id,
    trigger_event="quotation_approved",
    context={"approval_level": "senior_underwriter"}
)

# Schedule reminders
reminders = await workflow_service.schedule_workflow_reminders(quotation.id)

# Analyze performance
performance = await workflow_service.analyze_workflow_performance(quotation.id)
    """
}

# Integration points with external systems
EXTERNAL_INTEGRATIONS = {
    "email_service": {
        "purpose": "Customer communications and notifications",
        "methods": ["send_welcome_email", "send_quotation", "send_reminders"],
        "configuration": ["smtp_settings", "template_management", "delivery_tracking"]
    },
    "document_service": {
        "purpose": "PDF generation and document management", 
        "methods": ["generate_quotation_pdf", "create_proposal", "manage_templates"],
        "configuration": ["template_storage", "branding_options", "multilingual_support"]
    },
    "policy_service": {
        "purpose": "Policy creation from approved quotations",
        "methods": ["create_policy", "transfer_data", "link_documents"],
        "configuration": ["policy_numbering", "data_mapping", "workflow_integration"]
    },
    "notification_service": {
        "purpose": "Real-time notifications and alerts",
        "methods": ["send_push_notification", "create_alert", "manage_preferences"],
        "configuration": ["delivery_channels", "user_preferences", "escalation_rules"]
    },
    "task_scheduler": {
        "purpose": "Automated task scheduling and execution",
        "methods": ["schedule_task", "execute_workflow", "manage_reminders"],
        "configuration": ["cron_expressions", "retry_policies", "failure_handling"]
    }
}

# Quality assurance and testing patterns
TESTING_PATTERNS = {
    "unit_testing": {
        "service_methods": "test_each_service_method_independently",
        "business_logic": "test_validation_rules_and_calculations",
        "error_handling": "test_exception_scenarios_and_edge_cases"
    },
    "integration_testing": {
        "service_orchestration": "test_cross_service_interactions",
        "database_operations": "test_repository_integration",
        "external_services": "test_third_party_integrations"
    },
    "end_to_end_testing": {
        "complete_workflows": "test_full_quotation_lifecycle",
        "user_scenarios": "test_real_world_usage_patterns",
        "performance": "test_under_load_conditions"
    }
}