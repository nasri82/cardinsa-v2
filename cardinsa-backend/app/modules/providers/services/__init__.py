# app/modules/providers/services/__init__.py
"""
Provider module services
"""

# Enhanced Service Classes
from .provider_type_service import (
    ProviderTypeService,
    create_provider_type_service
)
from .provider_service import (
    ProviderService,
    create_provider_service
)
from .provider_network_service import (
    ProviderNetworkService,
    create_provider_network_service
)
from .provider_network_member_service import (
    ProviderNetworkMemberService,
    create_provider_network_member_service
)
from .provider_service_price_service import (
    ProviderServicePriceService,
    create_provider_service_price_service
)

# Legacy Compatibility Functions
from .provider_type_service import (
    get_provider_type,
    create_provider_type,
    update_provider_type,
    delete_provider_type
)
from .provider_service import (
    get_provider,
    create_provider,
    update_provider,
    delete_provider
)
from .provider_network_service import (
    get_provider_network,
    create_provider_network,
    update_provider_network,
    delete_provider_network
)
from .provider_network_member_service import (
    get_network_member,
    create_network_member,
    update_network_member,
    delete_network_member
)
from .provider_service_price_service import (
    get_service_price,
    create_service_price,
    update_service_price,
    delete_service_price
)

__all__ = [
    # Enhanced Service Classes
    "ProviderTypeService",
    "ProviderService",
    "ProviderNetworkService", 
    "ProviderNetworkMemberService",
    "ProviderServicePriceService",
    
    # Service Factory Functions
    "create_provider_type_service",
    "create_provider_service",
    "create_provider_network_service",
    "create_provider_network_member_service", 
    "create_provider_service_price_service",
    
    # Legacy Compatibility Functions (for existing routes)
    "get_provider_type",
    "create_provider_type",
    "update_provider_type", 
    "delete_provider_type",
    "get_provider",
    "create_provider",
    "update_provider",
    "delete_provider",
    "get_provider_network",
    "create_provider_network",
    "update_provider_network",
    "delete_provider_network",
    "get_network_member",
    "create_network_member", 
    "update_network_member",
    "delete_network_member",
    "get_service_price",
    "create_service_price",
    "update_service_price",
    "delete_service_price"
]