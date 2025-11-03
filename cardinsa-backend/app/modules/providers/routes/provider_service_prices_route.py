# app/modules/providers/routes/provider_service_prices_route.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from app.core.dependencies import get_db, require_permission_scoped
from app.core.exceptions import handle_exceptions
from app.modules.providers.schemas.provider_service_price_schema import (
    ProviderServicePriceOut,
    ProviderServicePriceCreate,
    ProviderServicePriceUpdate,
    ProviderServicePriceSearch
)
from app.modules.providers.services import create_provider_service_price_service

router = APIRouter(prefix="/provider-service-prices", tags=["Provider Service Prices"])

# ==================== BASIC CRUD OPERATIONS ====================

@router.get("/{id}", response_model=ProviderServicePriceOut)
@handle_exceptions
def get_service_price(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get service price by ID"""
    service = create_provider_service_price_service(db)
    return service.get_service_price(id)

@router.post("", response_model=ProviderServicePriceOut, status_code=status.HTTP_201_CREATED)
@handle_exceptions
def create_service_price(
    obj_in: ProviderServicePriceCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "create"))
):
    """Create new service price"""
    service = create_provider_service_price_service(db)
    return service.create_service_price(obj_in)

@router.put("/{id}", response_model=ProviderServicePriceOut)
@handle_exceptions
def update_service_price(
    id: UUID,
    obj_in: ProviderServicePriceUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """Update service price"""
    service = create_provider_service_price_service(db)
    return service.update_service_price(id, obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
def delete_service_price(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "delete"))
):
    """Delete service price"""
    service = create_provider_service_price_service(db)
    service.delete_service_price(id)

# ==================== PROVIDER SERVICES ====================

@router.get("/provider/{provider_id}", response_model=List[ProviderServicePriceOut])
@handle_exceptions
def get_provider_services(
    provider_id: UUID,
    active_only: bool = Query(True, description="Include only active services"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get all services and prices for a provider"""
    service = create_provider_service_price_service(db)
    return service.get_provider_services(
        provider_id=provider_id,
        active_only=active_only,
        category=category
    )

@router.get("/provider/{provider_id}/service/{service_tag}", response_model=ProviderServicePriceOut)
@handle_exceptions
def get_service_by_code(
    provider_id: UUID,
    service_tag: str,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get specific service price by provider and service tag"""
    service = create_provider_service_price_service(db)
    service_price = service.get_service_by_code(provider_id, service_tag)
    if not service_price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_tag}' not found for specified provider"
        )
    return service_price

# ==================== ADVANCED SEARCH & FILTERING ====================

@router.get("", response_model=List[ProviderServicePriceOut])
@handle_exceptions
def search_service_prices(
    # Basic filters
    service_tag: Optional[str] = Query(None, description="Search by service tag"),
    service_name: Optional[str] = Query(None, description="Search by service name (partial match)"),
    provider_id: Optional[UUID] = Query(None, description="Filter by provider ID"),
    provider_name: Optional[str] = Query(None, description="Search by provider name"),
    
    # Price range filters
    min_price: Optional[Decimal] = Query(None, description="Minimum price filter", ge=0),
    max_price: Optional[Decimal] = Query(None, description="Maximum price filter", ge=0),
    currency: Optional[str] = Query(None, description="Filter by currency code"),
    is_discounted: Optional[bool] = Query(None, description="Filter by discount status"),
    
    # Category and specialty filters
    category: Optional[str] = Query(None, description="Filter by service category"),
    specialty: Optional[str] = Query(None, description="Filter by provider specialty"),
    
    # Location filters
    city: Optional[str] = Query(None, description="Filter by provider city"),
    region: Optional[str] = Query(None, description="Filter by provider region"),
    
    # Status filters
    active_providers_only: bool = Query(True, description="Include only active providers"),
    
    # Sorting and pagination
    sort_by: Optional[str] = Query("price", description="Sort field: price, service_tag, provider_name, created_at"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc, desc"),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(20, description="Items per page", ge=1, le=100),
    
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """
    Advanced search for service prices with multiple filters
    
    This endpoint supports comprehensive filtering by:
    - Service details (tag, name, category)
    - Provider information (ID, name, specialty, location)
    - Price ranges and currency
    - Discount status
    - Geographic location
    - Active status
    
    Results can be sorted by various fields and paginated.
    """
    service = create_provider_service_price_service(db)
    
    search_params = ProviderServicePriceSearch(
        service_tag=service_tag,
        service_name=service_name,
        provider_id=provider_id,
        provider_name=provider_name,
        min_price=min_price,
        max_price=max_price,
        currency=currency,
        is_discounted=is_discounted,
        category=category,
        specialty=specialty,
        city=city,
        region=region,
        active_providers_only=active_providers_only,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    return service.search_service_prices(search_params)

@router.get("/price-comparison", response_model=Dict[str, Any])
@handle_exceptions
def compare_service_prices(
    service_tag: str = Query(..., description="Service tag to compare"),
    city: Optional[str] = Query(None, description="Filter by city"),
    region: Optional[str] = Query(None, description="Filter by region"),
    provider_ids: Optional[List[UUID]] = Query(None, description="Specific provider IDs to compare"),
    include_inactive: bool = Query(False, description="Include inactive providers"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """
    Compare prices for a specific service across different providers
    
    Returns pricing statistics and provider comparisons for a given service.
    """
    service = create_provider_service_price_service(db)
    return service.compare_service_prices(
        service_tag=service_tag,
        city=city,
        region=region,
        provider_ids=provider_ids,
        include_inactive=include_inactive
    )

@router.get("/pricing-analytics", response_model=Dict[str, Any])
@handle_exceptions
def get_pricing_analytics(
    provider_id: Optional[UUID] = Query(None, description="Specific provider analysis"),
    service_tag: Optional[str] = Query(None, description="Specific service analysis"),
    date_from: Optional[str] = Query(None, description="Start date for analysis (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date for analysis (YYYY-MM-DD)"),
    group_by: str = Query("provider", description="Group by: provider, service, category, city"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """
    Get comprehensive pricing analytics and insights
    
    Provides statistical analysis of pricing data including:
    - Average, min, max prices
    - Price distribution
    - Market positioning
    - Trending analysis
    """
    service = create_provider_service_price_service(db)
    return service.get_pricing_analytics(
        provider_id=provider_id,
        service_tag=service_tag,
        date_from=date_from,
        date_to=date_to,
        group_by=group_by
    )

# ==================== BULK OPERATIONS ====================

@router.post("/bulk-create", response_model=List[ProviderServicePriceOut])
@handle_exceptions
def bulk_create_service_prices(
    prices: List[ProviderServicePriceCreate],
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "create"))
):
    """Create multiple service prices in bulk"""
    service = create_provider_service_price_service(db)
    return service.bulk_create_service_prices(prices)

@router.put("/bulk-update", response_model=List[ProviderServicePriceOut])
@handle_exceptions
def bulk_update_service_prices(
    updates: List[Dict[str, Any]],  # List of {"id": UUID, "data": ProviderServicePriceUpdate}
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """Update multiple service prices in bulk"""
    service = create_provider_service_price_service(db)
    return service.bulk_update_service_prices(updates)

@router.delete("/bulk-delete")
@handle_exceptions
def bulk_delete_service_prices(
    price_ids: List[UUID],
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "delete"))
):
    """Delete multiple service prices in bulk"""
    service = create_provider_service_price_service(db)
    deleted_count = service.bulk_delete_service_prices(price_ids)
    return {"message": f"Successfully deleted {deleted_count} service prices"}

# ==================== IMPORT/EXPORT ====================

@router.post("/import-csv")
@handle_exceptions
def import_prices_from_csv(
    file_url: str = Query(..., description="URL of CSV file to import"),
    provider_id: Optional[UUID] = Query(None, description="Default provider for all records"),
    skip_duplicates: bool = Query(True, description="Skip duplicate service tags"),
    validate_only: bool = Query(False, description="Only validate, don't import"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "create"))
):
    """
    Import service prices from CSV file
    
    Expected CSV format:
    service_tag,price,currency,is_discounted,notes,provider_id
    """
    service = create_provider_service_price_service(db)
    return service.import_prices_from_csv(
        file_url=file_url,
        default_provider_id=provider_id,
        skip_duplicates=skip_duplicates,
        validate_only=validate_only
    )

@router.get("/export-csv")
@handle_exceptions
def export_prices_to_csv(
    provider_id: Optional[UUID] = Query(None, description="Export specific provider"),
    service_tags: Optional[List[str]] = Query(None, description="Export specific services"),
    include_inactive: bool = Query(False, description="Include inactive providers"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Export service prices to CSV format"""
    service = create_provider_service_price_service(db)
    return service.export_prices_to_csv(
        provider_id=provider_id,
        service_tags=service_tags,
        include_inactive=include_inactive
    )

# ==================== SPECIALIZED ENDPOINTS ====================

@router.get("/trending-prices", response_model=List[Dict[str, Any]])
@handle_exceptions
def get_trending_prices(
    period: str = Query("month", description="Trending period: week, month, quarter, year"),
    limit: int = Query(10, description="Number of trending items", ge=1, le=50),
    trend_type: str = Query("increase", description="Trend type: increase, decrease, volatile"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get trending service prices based on recent changes"""
    service = create_provider_service_price_service(db)
    return service.get_trending_prices(
        period=period,
        limit=limit,
        trend_type=trend_type
    )

@router.get("/market-position/{provider_id}", response_model=Dict[str, Any])
@handle_exceptions
def get_provider_market_position(
    provider_id: UUID,
    service_tags: Optional[List[str]] = Query(None, description="Analyze specific services"),
    comparison_scope: str = Query("city", description="Comparison scope: city, region, national"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Analyze provider's market position based on pricing"""
    service = create_provider_service_price_service(db)
    return service.get_provider_market_position(
        provider_id=provider_id,
        service_tags=service_tags,
        comparison_scope=comparison_scope
    )

@router.get("/pricing-suggestions/{provider_id}", response_model=List[Dict[str, Any]])
@handle_exceptions
def get_pricing_suggestions(
    provider_id: UUID,
    strategy: str = Query("competitive", description="Pricing strategy: competitive, premium, budget"),
    target_margin: Optional[float] = Query(None, description="Target profit margin percentage"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get AI-powered pricing suggestions for a provider"""
    service = create_provider_service_price_service(db)
    return service.get_pricing_suggestions(
        provider_id=provider_id,
        strategy=strategy,
        target_margin=target_margin
    )

# ==================== HEALTH CHECK ====================

@router.get("/health", include_in_schema=False)
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "provider-service-prices"}