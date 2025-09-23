# app/modules/providers/schemas/__init__.py

"""
Provider Schemas Module - Pydantic v2 Compatible
================================================

Working schemas with proper Pydantic v2 syntax.
All schemas use @field_validator and @model_validator with proper syntax.
"""

# Provider Type Schemas (Fixed)
from .provider_type_schema import (
    ProviderCategoryEnum,
    ProviderTypeBase,
    ProviderTypeCreate,
    ProviderTypeUpdate,
    ProviderTypeOut,
    ProviderTypeList,
    ProviderTypeSearch
)

# Provider Schemas (Fixed)
from .provider_schema import (
    ProviderBase,
    ProviderCreate,
    ProviderUpdate,
    ProviderOut,
    ProviderList,
    ProviderSearch
)

# Provider Network Schemas (Fixed)
from .provider_network_schema import (
    NetworkTypeEnum,
    ProviderNetworkBase,
    ProviderNetworkCreate,
    ProviderNetworkUpdate,
    ProviderNetworkOut,
    ProviderNetworkList,
    ProviderNetworkSearch
)

# Provider Network Member Schemas (Fixed)  
from .provider_network_member_schema import (
    MembershipStatusEnum,
    ProviderNetworkMemberBase,
    ProviderNetworkMemberCreate,
    ProviderNetworkMemberUpdate,
    ProviderNetworkMemberOut,
    ProviderNetworkMemberList,
    ProviderNetworkMemberSearch
)

# Provider Service Price Schemas (Fixed)
from .provider_service_price_schema import (
    CurrencyEnum,
    ProviderServicePriceBase,
    ProviderServicePriceCreate,
    ProviderServicePriceUpdate,
    ProviderServicePriceOut,
    ProviderServicePriceList,
    ProviderServicePriceSearch
)

# Export all working schemas
__all__ = [
    # Enums
    'ProviderCategoryEnum',
    'NetworkTypeEnum',
    'MembershipStatusEnum',
    'CurrencyEnum',
    
    # Provider Type Schemas
    'ProviderTypeBase',
    'ProviderTypeCreate',
    'ProviderTypeUpdate',
    'ProviderTypeOut',
    'ProviderTypeList',
    'ProviderTypeSearch',
    
    # Provider Schemas
    'ProviderBase',
    'ProviderCreate',
    'ProviderUpdate',
    'ProviderOut',
    'ProviderList',
    'ProviderSearch',
    
    # Provider Network Schemas
    'NetworkTypeEnum',
    'ProviderNetworkBase',
    'ProviderNetworkCreate',
    'ProviderNetworkUpdate',
    'ProviderNetworkOut',
    'ProviderNetworkList',
    'ProviderNetworkSearch',
    
    # Provider Network Member Schemas
    'MembershipStatusEnum',
    'ProviderNetworkMemberBase',
    'ProviderNetworkMemberCreate',
    'ProviderNetworkMemberUpdate',
    'ProviderNetworkMemberOut',
    'ProviderNetworkMemberList',
    'ProviderNetworkMemberSearch',
    
    # Provider Service Price Schemas
    'CurrencyEnum',
    'ProviderServicePriceBase',
    'ProviderServicePriceCreate',
    'ProviderServicePriceUpdate',
    'ProviderServicePriceOut',
    'ProviderServicePriceList',
    'ProviderServicePriceSearch'
]

# Schema collections for easy access
PROVIDER_TYPE_SCHEMAS = [
    ProviderTypeCreate,
    ProviderTypeUpdate,
    ProviderTypeOut,
    ProviderTypeList,
    ProviderTypeSearch
]

PROVIDER_SCHEMAS = [
    ProviderCreate,
    ProviderUpdate,
    ProviderOut,
    ProviderList,
    ProviderSearch
]

PROVIDER_NETWORK_SCHEMAS = [
    ProviderNetworkCreate,
    ProviderNetworkUpdate,
    ProviderNetworkOut,
    ProviderNetworkList,
    ProviderNetworkSearch
]

PROVIDER_NETWORK_MEMBER_SCHEMAS = [
    ProviderNetworkMemberCreate,
    ProviderNetworkMemberUpdate,
    ProviderNetworkMemberOut,
    ProviderNetworkMemberList,
    ProviderNetworkMemberSearch
]

PROVIDER_SERVICE_PRICE_SCHEMAS = [
    ProviderServicePriceCreate,
    ProviderServicePriceUpdate,
    ProviderServicePriceOut,
    ProviderServicePriceList,
    ProviderServicePriceSearch
]