# app/modules/providers/routes/providers_route.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.dependencies import get_db, require_permission_scoped
from app.core.exceptions import handle_exceptions
from app.modules.providers.schemas.provider_schema import (
    ProviderOut,
    ProviderCreate,
    ProviderUpdate,
    ProviderSearch
)
from app.modules.providers.services import create_provider_service

router = APIRouter(prefix="/providers", tags=["Providers"])

# ==================== BASIC CRUD OPERATIONS ====================

@router.get("/{id}", response_model=ProviderOut)
@handle_exceptions
def get_provider(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get provider by ID"""
    service = create_provider_service(db)
    return service.get_provider(id)

@router.post("", response_model=ProviderOut, status_code=status.HTTP_201_CREATED)
@handle_exceptions
def create_provider(
    obj_in: ProviderCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "create"))
):
    """Create new provider"""
    service = create_provider_service(db)
    return service.create_provider(obj_in)

@router.put("/{id}", response_model=ProviderOut)
@handle_exceptions
def update_provider(
    id: UUID,
    obj_in: ProviderUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """Update provider"""
    service = create_provider_service(db)
    return service.update_provider(id, obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
def delete_provider(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "delete"))
):
    """Delete provider"""
    service = create_provider_service(db)
    service.delete_provider(id)

# ==================== ADVANCED SEARCH & FILTERING ====================

@router.get("", response_model=List[ProviderOut])
@handle_exceptions
def list_providers(
    search: Optional[str] = Query(None, description="Search in name, email, address, or phone"),
    provider_type_id: Optional[UUID] = Query(None, description="Filter by provider type"),
    city: Optional[str] = Query(None, description="Filter by city"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    has_coordinates: Optional[bool] = Query(None, description="Filter by coordinate availability"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """List providers with advanced filtering and search"""
    service = create_provider_service(db)
    search_params = ProviderSearch(
        search=search,
        provider_type_id=provider_type_id,
        city=city,
        is_active=is_active,
        has_coordinates=has_coordinates
    )
    return service.search_providers(search_params, skip=skip, limit=limit)

@router.get("/paginated", response_model=dict)
@handle_exceptions
def get_paginated_providers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    provider_type_id: Optional[UUID] = Query(None, description="Filter by provider type"),
    city: Optional[str] = Query(None, description="Filter by city"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get paginated providers with metadata"""
    service = create_provider_service(db)
    return service.get_paginated_providers(
        page=page,
        page_size=page_size,
        provider_type_id=provider_type_id,
        city=city,
        is_active=is_active,
        search_term=search
    )

# ==================== GEOSPATIAL OPERATIONS ====================

@router.get("/nearby", response_model=List[Dict[str, Any]])
@handle_exceptions
def find_nearby_providers(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    radius_km: float = Query(50.0, ge=1, le=1000, description="Search radius in kilometers"),
    provider_type_id: Optional[UUID] = Query(None, description="Filter by provider type"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Find providers within specified radius of coordinates"""
    service = create_provider_service(db)
    return service.find_nearby_providers(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        provider_type_id=provider_type_id,
        limit=limit
    )

@router.get("/by-city/{city}", response_model=List[ProviderOut])
@handle_exceptions
def get_providers_by_city(
    city: str,
    provider_type_id: Optional[UUID] = Query(None, description="Filter by provider type"),
    active_only: bool = Query(True, description="Include only active providers"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get providers by city"""
    service = create_provider_service(db)
    return service.get_providers_by_city(
        city=city,
        provider_type_id=provider_type_id,
        active_only=active_only
    )

@router.get("/missing-coordinates", response_model=List[ProviderOut])
@handle_exceptions
def get_providers_without_coordinates(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get providers that don't have coordinates (for geocoding)"""
    service = create_provider_service(db)
    return service.get_providers_without_coordinates(limit=limit)

@router.patch("/bulk/coordinates", response_model=dict)
@handle_exceptions
def bulk_update_coordinates(
    coordinates_data: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """
    Bulk update provider coordinates
    
    Request body should be a list of objects with:
    - provider_id: UUID - Provider ID
    - latitude: float - Latitude coordinate
    - longitude: float - Longitude coordinate
    """
    service = create_provider_service(db)
    return service.bulk_update_coordinates(coordinates_data)

# ==================== PROVIDER LOOKUP ====================

@router.get("/by-email/{email}", response_model=ProviderOut)
@handle_exceptions
def get_provider_by_email(
    email: str,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get provider by email address"""
    service = create_provider_service(db)
    provider = service.get_provider_by_email(email)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider with email '{email}' not found"
        )
    return provider

# ==================== ANALYTICS & STATISTICS ====================

@router.get("/analytics/cities", response_model=List[Dict[str, Any]])
@handle_exceptions
def get_cities_with_counts(
    active_only: bool = Query(True, description="Include only active providers"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get cities with provider counts"""
    service = create_provider_service(db)
    return service.get_cities_with_counts(active_only=active_only)

@router.get("/{id}/summary", response_model=Dict[str, Any])
@handle_exceptions
def get_provider_summary(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get comprehensive provider summary with related data"""
    service = create_provider_service(db)
    return service.get_provider_summary(id)

@router.get("/analytics/geographic-distribution", response_model=Dict[str, Any])
@handle_exceptions
def get_geographic_distribution(
    provider_type_id: Optional[UUID] = Query(None, description="Filter by provider type"),
    active_only: bool = Query(True, description="Include only active providers"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get geographic distribution of providers"""
    service = create_provider_service(db)
    cities = service.get_cities_with_counts(active_only=active_only)
    
    # TODO: Add provider type filtering when needed
    total_providers = sum(city['provider_count'] for city in cities)
    
    return {
        "total_providers": total_providers,
        "total_cities": len(cities),
        "cities": cities,
        "filters_applied": {
            "provider_type_id": str(provider_type_id) if provider_type_id else None,
            "active_only": active_only
        }
    }

# ==================== VALIDATION ENDPOINTS ====================

@router.get("/validate/email/{email}", response_model=dict)
@handle_exceptions
def validate_email_availability(
    email: str,
    exclude_id: Optional[UUID] = Query(None, description="ID to exclude from validation"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Check if provider email is available"""
    service = create_provider_service(db)
    existing = service.get_provider_by_email(email)
    
    is_available = True
    if existing:
        if exclude_id is None or existing.id != exclude_id:
            is_available = False
    
    return {
        "email": email,
        "is_available": is_available,
        "existing_id": str(existing.id) if existing else None,
        "existing_name": existing.name if existing else None
    }

# ==================== MAINTENANCE OPERATIONS ====================

@router.get("/maintenance/data-quality", response_model=dict)
@handle_exceptions
def get_data_quality_report(
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "admin"))
):
    """Get data quality report for providers"""
    service = create_provider_service(db)
    
    # Get providers without coordinates
    missing_coords = service.get_providers_without_coordinates(limit=1000)
    
    # Get all cities for analysis
    cities = service.get_cities_with_counts(active_only=False)
    
    return {
        "summary": {
            "total_cities": len(cities),
            "providers_missing_coordinates": len(missing_coords)
        },
        "missing_coordinates_sample": [
            {
                "id": str(p.id),
                "name": p.name,
                "address": p.address,
                "city": p.city
            }
            for p in missing_coords[:10]  # Show first 10 as sample
        ],
        "cities_distribution": cities[:20]  # Show top 20 cities
    }

@router.post("/maintenance/geocode", response_model=dict)
@handle_exceptions
def trigger_geocoding(
    limit: int = Query(50, ge=1, le=100, description="Number of providers to process"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "admin"))
):
    """Trigger geocoding for providers without coordinates (simulation)"""
    service = create_provider_service(db)
    
    providers_to_geocode = service.get_providers_without_coordinates(limit=limit)
    
    # In a real implementation, this would integrate with a geocoding service
    # For now, return information about what would be processed
    
    return {
        "message": "Geocoding simulation - would process these providers",
        "providers_to_process": len(providers_to_geocode),
        "sample_providers": [
            {
                "id": str(p.id),
                "name": p.name,
                "address": p.address,
                "city": p.city
            }
            for p in providers_to_geocode[:5]  # Show first 5 as sample
        ],
        "note": "This is a simulation. Integrate with actual geocoding service for production."
    }