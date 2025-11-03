# app/modules/pricing/quotations/services/__init__.py

"""
Quotation Services Package

This package contains all business logic services for quotation management,
providing comprehensive functionality for quote generation, calculation integration,
workflow management, and customer presentation.
"""

# ✅ CORRECTED IMPORT - Import the actual class name
try:
    from .quotation_service import EnhancedQuotationService
    # Create alias for backward compatibility
    QuotationService = EnhancedQuotationService
except ImportError as e:
    print(f"Warning: Could not import EnhancedQuotationService: {e}")
    # Create a placeholder to avoid complete import failure
    class QuotationService:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("QuotationService not available")
    
    EnhancedQuotationService = QuotationService

# Try to import other services if they exist
try:
    from .quotation_item_service import QuotationItemService
except ImportError:
    QuotationItemService = None

try:
    from .quotation_factor_service import QuotationFactorService
except ImportError:
    QuotationFactorService = None

try:
    from .quotation_workflow_service import QuotationWorkflowService
except ImportError:
    QuotationWorkflowService = None

# Export all available services
__all__ = [
    # Main quotation services
    "EnhancedQuotationService",
    "QuotationService",  # Alias for backward compatibility
    
    # Additional services (if available)
    "QuotationItemService",
    "QuotationFactorService", 
    "QuotationWorkflowService",
]

# Service registry for dynamic service discovery
AVAILABLE_SERVICES = {
    "enhanced_quotation": EnhancedQuotationService,
    "quotation": QuotationService,  # Alias
}

# Add other services if they're available
if QuotationItemService:
    AVAILABLE_SERVICES["quotation_item"] = QuotationItemService

if QuotationFactorService:
    AVAILABLE_SERVICES["quotation_factor"] = QuotationFactorService

if QuotationWorkflowService:
    AVAILABLE_SERVICES["quotation_workflow"] = QuotationWorkflowService

# Helper function to get services
def get_service(service_name: str, *args, **kwargs):
    """
    Get a service instance by name.
    
    Args:
        service_name: Name of the service to get
        *args, **kwargs: Arguments to pass to service constructor
        
    Returns:
        Service instance
        
    Raises:
        KeyError: If service not found
        NotImplementedError: If service not implemented
    """
    if service_name not in AVAILABLE_SERVICES:
        raise KeyError(f"Service '{service_name}' not found. Available: {list(AVAILABLE_SERVICES.keys())}")
    
    service_class = AVAILABLE_SERVICES[service_name]
    return service_class(*args, **kwargs)

# Service health check
def check_services_health():
    """Check the health of all available services"""
    health_status = {}
    
    for service_name, service_class in AVAILABLE_SERVICES.items():
        try:
            # Try to get service info
            if hasattr(service_class, '__name__'):
                health_status[service_name] = {
                    "status": "available",
                    "class": service_class.__name__,
                    "module": getattr(service_class, '__module__', 'unknown')
                }
            else:
                health_status[service_name] = {
                    "status": "unavailable", 
                    "error": "Class not properly defined"
                }
        except Exception as e:
            health_status[service_name] = {
                "status": "error",
                "error": str(e)
            }
    
    return health_status