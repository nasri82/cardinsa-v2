# app/modules/insurance/quotations/routes/__init__.py

"""
Quotation Routes Package

This package contains all FastAPI route definitions for the quotations module,
providing comprehensive REST API endpoints for insurance quotation management.

Routes included:
- quotations_route: Main quotation CRUD and workflow operations
- quotation_items_route: Coverage item management with multilingual support
- quotation_factors_route: Pricing factor management and impact analysis
- Additional routes for complete quotation lifecycle management
"""

from .quotations_route import router as quotations_router
from .quotation_items_route import router as quotation_items_router
from .quotation_factors_route import router as quotation_factors_router

# Additional routes would be imported here as they are created
# from .quotation_documents_route import router as quotation_documents_router
# from .quotation_workflow_route import router as quotation_workflow_router
# from .quotation_analytics_route import router as quotation_analytics_router

# Export all routers for easy importing
__all__ = [
    "quotations_router",
    "quotation_items_router", 
    "quotation_factors_router",
    # Additional routers will be added here
    # "quotation_documents_router",
    # "quotation_workflow_router",
    # "quotation_analytics_router"
]

# API endpoint patterns and conventions
API_PATTERNS = {
    "main_quotations": {
        "base_path": "/quotations",
        "endpoints": [
            "GET /quotations - Get paginated quotations with filters",
            "POST /quotations - Create new quotation",
            "GET /quotations/{id} - Get quotation by ID",
            "PUT /quotations/{id} - Update quotation",
            "DELETE /quotations/{id} - Delete quotation",
            "PATCH /quotations/{id}/status - Update status",
            "POST /quotations/{id}/calculate - Calculate premium",
            "POST /quotations/{id}/lock - Lock quotation",
            "POST /quotations/{id}/unlock - Unlock quotation"
        ]
    },
    "quotation_items": {
        "base_path": "/quotations/{quotation_id}/items",
        "endpoints": [
            "GET /items - Get all items for quotation",
            "POST /items - Create new item",
            "GET /items/{item_id} - Get specific item",
            "PUT /items/{item_id} - Update item",
            "DELETE /items/{item_id} - Delete item",
            "GET /items/localized - Get localized items",
            "PATCH /items/reorder - Reorder multiple items",
            "POST /items/bulk - Create multiple items"
        ]
    },
    "quotation_factors": {
        "base_path": "/quotations/{quotation_id}/factors",
        "endpoints": [
            "GET /factors - Get all factors for quotation",
            "POST /factors - Create new factor",
            "GET /factors/{factor_id} - Get specific factor",
            "PUT /factors/{factor_id} - Update factor",
            "DELETE /factors/{factor_id} - Delete factor",
            "GET /factors/grouped - Get factors by type",
            "PUT /factors/upsert - Upsert factor by key",
            "GET /factors/impact-analysis - Analyze factor impacts"
        ]
    }
}

# HTTP status code usage guidelines
STATUS_CODE_USAGE = {
    "200_OK": [
        "Successful GET requests",
        "Successful PUT/PATCH updates",
        "Successful operations that don't create resources"
    ],
    "201_CREATED": [
        "Successful POST requests that create new resources",
        "Bulk creation operations",
        "Duplication operations"
    ],
    "204_NO_CONTENT": [
        "Successful DELETE operations",
        "Operations that complete without response body"
    ],
    "400_BAD_REQUEST": [
        "Invalid request data",
        "Validation errors",
        "Malformed request body"
    ],
    "401_UNAUTHORIZED": [
        "Missing or invalid authentication",
        "Expired tokens"
    ],
    "403_FORBIDDEN": [
        "Insufficient permissions",
        "Access denied to resource"
    ],
    "404_NOT_FOUND": [
        "Resource doesn't exist",
        "Invalid resource IDs"
    ],
    "409_CONFLICT": [
        "Business rule violations",
        "Resource state conflicts",
        "Duplicate resource creation"
    ],
    "422_UNPROCESSABLE_ENTITY": [
        "Business logic errors",
        "Invalid state transitions",
        "Complex validation failures"
    ],
    "500_INTERNAL_SERVER_ERROR": [
        "Unexpected server errors",
        "Database connection issues",
        "Service integration failures"
    ]
}

# Request/response patterns
REQUEST_RESPONSE_PATTERNS = {
    "pagination": {
        "query_parameters": ["page", "per_page", "sort_by", "sort_order"],
        "response_format": {
            "data": "List of resources",
            "pagination": {
                "page": "Current page",
                "per_page": "Items per page", 
                "total": "Total items",
                "total_pages": "Total pages",
                "has_next": "Has next page",
                "has_prev": "Has previous page"
            }
        }
    },
    "filtering": {
        "common_filters": [
            "status", "customer_email", "product_code", "assigned_to",
            "created_from", "created_to", "min_premium", "max_premium"
        ],
        "advanced_filters": [
            "tags", "metadata_fields", "factor_types", "coverage_names"
        ]
    },
    "search": {
        "endpoints": ["/search/{term}", "/items/search", "/factors/search"],
        "parameters": ["search_term", "language", "fields", "limit"],
        "features": ["partial_matching", "multilingual_search", "fuzzy_search"]
    },
    "bulk_operations": {
        "patterns": [
            "POST /bulk - Create multiple resources",
            "PUT /bulk-update - Update multiple resources", 
            "DELETE /bulk-delete - Delete multiple resources",
            "POST /duplicate-from/{source_id} - Duplicate resources"
        ],
        "request_format": {
            "target_id": "Target resource ID",
            "items": "Array of items to process",
            "options": "Operation-specific options"
        }
    }
}

# Authentication and authorization patterns
AUTH_PATTERNS = {
    "authentication": {
        "method": "Bearer token in Authorization header",
        "dependency": "get_current_user",
        "required_for": "All endpoints except health checks"
    },
    "authorization": {
        "levels": [
            "read_only - View quotations and items",
            "create_edit - Create and modify quotations",
            "admin - Full access including deletion",
            "system - Automated system operations"
        ],
        "resource_based": "Users can only access quotations they own or are assigned to"
    }
}

# Error handling and validation patterns
ERROR_HANDLING = {
    "validation_errors": {
        "source": "Pydantic schema validation",
        "format": "Field-level error details",
        "http_status": 400
    },
    "business_logic_errors": {
        "source": "Service layer business rules", 
        "format": "Business rule violation messages",
        "http_status": 422
    },
    "not_found_errors": {
        "source": "Resource lookup failures",
        "format": "Resource not found messages",
        "http_status": 404
    },
    "conflict_errors": {
        "source": "State or constraint violations",
        "format": "Conflict description and resolution",
        "http_status": 409
    }
}

# Response format standards
RESPONSE_FORMATS = {
    "success_response": {
        "structure": {
            "status": "success",
            "data": "Response data",
            "message": "Success message",
            "timestamp": "ISO datetime",
            "metadata": "Additional context (optional)"
        }
    },
    "error_response": {
        "structure": {
            "status": "error",
            "error": {
                "code": "Error code",
                "message": "Error message",
                "details": "Additional error details",
                "field_errors": "Field-specific errors (for validation)"
            },
            "timestamp": "ISO datetime"
        }
    },
    "paginated_response": {
        "structure": {
            "status": "success",
            "data": {
                "items": "Array of resources",
                "pagination": "Pagination metadata"
            },
            "message": "Success message"
        }
    }
}

# API documentation standards
DOCUMENTATION_STANDARDS = {
    "endpoint_documentation": {
        "summary": "Brief endpoint description",
        "description": "Detailed endpoint explanation with examples",
        "parameters": "Path, query, and body parameter descriptions",
        "responses": "All possible response codes and formats",
        "examples": "Request/response examples for common scenarios"
    },
    "schema_documentation": {
        "field_descriptions": "Clear description for each field",
        "validation_rules": "Constraints and validation rules",
        "examples": "Example values for complex fields",
        "relationships": "Related entities and their connections"
    },
    "error_documentation": {
        "error_codes": "Custom error codes and meanings",
        "troubleshooting": "Common issues and solutions",
        "best_practices": "How to handle errors gracefully"
    }
}

# Performance and caching guidelines
PERFORMANCE_GUIDELINES = {
    "caching_strategy": {
        "cacheable_endpoints": [
            "GET /quotations/{id} - Cache for 5 minutes",
            "GET /quotations/{id}/items - Cache for 10 minutes",
            "GET /quotations/{id}/summary - Cache for 15 minutes"
        ],
        "cache_invalidation": [
            "Invalidate on quotation updates",
            "Invalidate on item/factor changes",
            "Invalidate on status changes"
        ]
    },
    "rate_limiting": {
        "general_endpoints": "100 requests per minute per user",
        "bulk_operations": "10 requests per minute per user",
        "calculation_endpoints": "20 requests per minute per user"
    },
    "optimization_tips": [
        "Use pagination for large result sets",
        "Implement proper database indexing",
        "Use async processing for heavy operations",
        "Implement request/response compression",
        "Monitor and log performance metrics"
    ]
}

# Integration patterns with external systems
INTEGRATION_PATTERNS = {
    "webhook_endpoints": {
        "quotation_events": [
            "quotation.created", "quotation.updated", "quotation.deleted",
            "quotation.status_changed", "quotation.premium_calculated"
        ],
        "webhook_format": {
            "event": "Event name",
            "data": "Event data",
            "timestamp": "Event timestamp",
            "quotation_id": "Related quotation ID"
        }
    },
    "external_api_integration": {
        "payment_systems": "Process premium payments",
        "document_generation": "Generate PDFs and documents",
        "email_services": "Send notifications and documents",
        "crm_systems": "Sync customer data",
        "policy_systems": "Convert quotations to policies"
    }
}

# Testing patterns and strategies
TESTING_STRATEGIES = {
    "unit_testing": {
        "route_testing": "Test individual endpoint logic",
        "validation_testing": "Test request/response validation",
        "error_handling_testing": "Test error scenarios"
    },
    "integration_testing": {
        "service_integration": "Test route-service integration",
        "database_integration": "Test data persistence",
        "external_api_integration": "Test third-party integrations"
    },
    "end_to_end_testing": {
        "workflow_testing": "Test complete quotation workflows",
        "user_journey_testing": "Test real-world usage scenarios",
        "performance_testing": "Test under load conditions"
    }
}

# Monitoring and observability
MONITORING_GUIDELINES = {
    "logging": {
        "log_levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "structured_logging": "Use structured JSON logs",
        "correlation_ids": "Track requests across services",
        "sensitive_data": "Never log sensitive customer data"
    },
    "metrics": {
        "endpoint_metrics": "Response times, error rates, request counts",
        "business_metrics": "Quotation creation rates, conversion rates",
        "system_metrics": "CPU, memory, database performance"
    },
    "alerting": {
        "error_rate_alerts": "Alert on high error rates",
        "performance_alerts": "Alert on slow response times",
        "business_alerts": "Alert on unusual business patterns"
    }
}

# Security best practices
SECURITY_BEST_PRACTICES = {
    "input_validation": [
        "Validate all input parameters",
        "Sanitize user input",
        "Use parameterized queries",
        "Implement rate limiting"
    ],
    "output_security": [
        "Never expose sensitive data in responses",
        "Use proper HTTP security headers",
        "Implement CORS properly",
        "Sanitize error messages"
    ],
    "authentication_security": [
        "Use strong token validation",
        "Implement token expiration",
        "Log authentication attempts",
        "Protect against brute force attacks"
    ]
}