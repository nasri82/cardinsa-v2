# app/modules/providers/routes/provider_networks_route.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.dependencies import get_db, require_permission_scoped
from app.core.exceptions import handle_exceptions
from app.modules.providers.schemas.provider_network_schema import (
    ProviderNetworkOut,
    ProviderNetworkCreate,
    ProviderNetworkUpdate,
    ProviderNetworkSearch
)
from app.modules.providers.services import create_provider_network_service

router = APIRouter(prefix="/provider-networks", tags=["Provider Networks"])

# ==================== BASIC CRUD OPERATIONS ====================

@router.get("/{id}", response_model=ProviderNetworkOut)
@handle_exceptions
def get_provider_network(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get provider network by ID"""
    service = create_provider_network_service(db)
    return service.get_provider_network(id)

@router.post("", response_model=ProviderNetworkOut, status_code=status.HTTP_201_CREATED)
@handle_exceptions
def create_provider_network(
    obj_in: ProviderNetworkCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "create"))
):
    """Create new provider network"""
    service = create_provider_network_service(db)
    return service.create_provider_network(obj_in)

@router.put("/{id}", response_model=ProviderNetworkOut)
@handle_exceptions
def update_provider_network(
    id: UUID,
    obj_in: ProviderNetworkUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """Update provider network"""
    service = create_provider_network_service(db)
    return service.update_provider_network(id, obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
def delete_provider_network(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "delete"))
):
    """Delete provider network"""
    service = create_provider_network_service(db)
    service.delete_provider_network(id)

# ==================== ADVANCED SEARCH & FILTERING ====================

@router.get("", response_model=List[ProviderNetworkOut])
@handle_exceptions
def list_provider_networks(
    search: Optional[str] = Query(None, description="Search in code, name, or description"),
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    coverage_area: Optional[str] = Query(None, description="Filter by coverage area"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """List provider networks with advanced filtering and search"""
    service = create_provider_network_service(db)
    search_params = ProviderNetworkSearch(
        search=search,
        company_id=company_id,
        tier=tier,
        is_active=is_active,
        coverage_area=coverage_area
    )
    return service.search_networks(search_params, skip=skip, limit=limit)

@router.get("/paginated", response_model=dict)
@handle_exceptions
def get_paginated_networks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get paginated networks with metadata"""
    service = create_provider_network_service(db)
    return service.get_paginated_networks(
        page=page,
        page_size=page_size,
        company_id=company_id,
        tier=tier,
        is_active=is_active,
        search_term=search
    )

# ==================== BUSINESS LOGIC OPERATIONS ====================

@router.get("/active", response_model=List[ProviderNetworkOut])
@handle_exceptions
def get_active_networks(
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get all active networks"""
    service = create_provider_network_service(db)
    return service.get_active_networks(company_id=company_id, tier=tier)

@router.get("/by-code/{code}", response_model=ProviderNetworkOut)
@handle_exceptions
def get_network_by_code(
    code: str,
    company_id: UUID = Query(..., description="Company ID for scope"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get network by unique code within company scope"""
    service = create_provider_network_service(db)
    network = service.get_network_by_code(code, company_id)
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network with code '{code}' not found in specified company"
        )
    return network

@router.get("/by-coverage/{coverage_area}", response_model=List[ProviderNetworkOut])
@handle_exceptions
def get_networks_by_coverage_area(
    coverage_area: str,
    active_only: bool = Query(True, description="Include only active networks"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get networks by coverage area"""
    service = create_provider_network_service(db)
    return service.get_networks_by_coverage_area(
        coverage_area=coverage_area,
        active_only=active_only
    )

# ==================== ANALYTICS & STATISTICS ====================

@router.get("/analytics/tier-distribution", response_model=List[Dict[str, Any]])
@handle_exceptions
def get_tier_distribution(
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    active_only: bool = Query(True, description="Include only active networks"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get network distribution by tier"""
    service = create_provider_network_service(db)
    return service.get_tier_distribution(
        company_id=company_id,
        active_only=active_only
    )

@router.get("/analytics/coverage-areas", response_model=List[Dict[str, Any]])
@handle_exceptions
def get_coverage_areas_with_counts(
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get coverage areas with network counts"""
    service = create_provider_network_service(db)
    return service.get_coverage_areas_with_counts(company_id=company_id)

@router.get("/{id}/statistics", response_model=Dict[str, Any])
@handle_exceptions
def get_network_statistics(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get comprehensive network statistics"""
    service = create_provider_network_service(db)
    return service.get_network_statistics(id)

@router.get("/analytics/overview", response_model=Dict[str, Any])
@handle_exceptions
def get_networks_overview(
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get comprehensive networks overview"""
    service = create_provider_network_service(db)
    
    # Get various analytics
    tier_dist = service.get_tier_distribution(company_id=company_id, active_only=True)
    coverage_areas = service.get_coverage_areas_with_counts(company_id=company_id)
    active_networks = service.get_active_networks(company_id=company_id)
    
    total_networks = len(active_networks)
    total_coverage_areas = len(coverage_areas)
    
    return {
        "summary": {
            "total_active_networks": total_networks,
            "total_coverage_areas": total_coverage_areas,
            "company_id": str(company_id) if company_id else None
        },
        "tier_distribution": tier_dist,
        "coverage_areas": coverage_areas,
        "networks_by_tier": {
            item["tier"]: item["network_count"] for item in tier_dist
        }
    }

# ==================== NETWORK OVERLAP ANALYSIS ====================

@router.get("/overlap-analysis", response_model=List[ProviderNetworkOut])
@handle_exceptions
def find_overlapping_networks(
    coverage_area: str = Query(..., description="Coverage area to check"),
    tier: str = Query(..., description="Tier to check"),
    company_id: UUID = Query(..., description="Company ID"),
    exclude_id: Optional[UUID] = Query(None, description="Network ID to exclude"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Find networks with overlapping coverage and tier"""
    service = create_provider_network_service(db)
    return service.find_overlapping_networks(
        coverage_area=coverage_area,
        tier=tier,
        company_id=company_id,
        exclude_id=exclude_id
    )

# ==================== BULK OPERATIONS ====================

@router.patch("/bulk/status", response_model=dict)
@handle_exceptions
def bulk_update_status(
    request: dict,  # Expected: {"network_ids": [...], "is_active": bool, "company_id": UUID}
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """
    Bulk update network status
    
    Request body should contain:
    - network_ids: List[UUID] - IDs of networks to update
    - is_active: bool - New active status
    - company_id: UUID (optional) - Company ID for validation
    """
    if "network_ids" not in request or "is_active" not in request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request must include 'network_ids' and 'is_active' fields"
        )
    
    service = create_provider_network_service(db)
    return service.bulk_update_status(
        network_ids=request["network_ids"],
        is_active=request["is_active"],
        company_id=request.get("company_id")
    )

# ==================== VALIDATION ENDPOINTS ====================

@router.get("/validate/code/{code}", response_model=dict)
@handle_exceptions
def validate_code_availability(
    code: str,
    company_id: UUID = Query(..., description="Company ID for scope"),
    exclude_id: Optional[UUID] = Query(None, description="ID to exclude from validation"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Check if network code is available within company scope"""
    service = create_provider_network_service(db)
    existing = service.get_network_by_code(code, company_id)
    
    is_available = True
    if existing:
        if exclude_id is None or existing.id != exclude_id:
            is_available = False
    
    return {
        "code": code,
        "company_id": str(company_id),
        "is_available": is_available,
        "existing_id": str(existing.id) if existing else None,
        "existing_name": existing.name if existing else None
    }

# ==================== REFERENCE DATA ====================

@router.get("/tiers/enum", response_model=List[str])
@handle_exceptions
def get_valid_tiers(
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get list of valid network tiers"""
    return ["Tier1", "Tier2", "OutOfNetwork", "Premium", "Standard", "Basic"]

@router.get("/coverage-areas/list", response_model=List[str])
@handle_exceptions
def list_coverage_areas(
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get list of existing coverage areas"""
    service = create_provider_network_service(db)
    coverage_data = service.get_coverage_areas_with_counts(company_id=company_id)
    return [item["coverage_area"] for item in coverage_data if item["coverage_area"]]