# app/modules/providers/routes/provider_network_members_route.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from app.core.dependencies import get_db, require_permission_scoped
from app.core.exceptions import handle_exceptions
from app.modules.providers.schemas.provider_network_member_schema import (
    ProviderNetworkMemberOut,
    ProviderNetworkMemberCreate,
    ProviderNetworkMemberUpdate,
    ProviderNetworkMemberSearch
)
from app.modules.providers.services import create_provider_network_member_service

router = APIRouter(prefix="/provider-network-members", tags=["Provider Network Members"])

# ==================== BASIC CRUD OPERATIONS ====================

@router.get("/{id}", response_model=ProviderNetworkMemberOut)
@handle_exceptions
def get_network_member(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get network member by ID"""
    service = create_provider_network_member_service(db)
    return service.get_network_member(id)

@router.post("", response_model=ProviderNetworkMemberOut, status_code=status.HTTP_201_CREATED)
@handle_exceptions
def create_network_member(
    obj_in: ProviderNetworkMemberCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "create"))
):
    """Create new network membership"""
    service = create_provider_network_member_service(db)
    return service.create_network_member(obj_in)

@router.put("/{id}", response_model=ProviderNetworkMemberOut)
@handle_exceptions
def update_network_member(
    id: UUID,
    obj_in: ProviderNetworkMemberUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """Update network membership"""
    service = create_provider_network_member_service(db)
    return service.update_network_member(id, obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
def delete_network_member(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "delete"))
):
    """Delete network membership"""
    service = create_provider_network_member_service(db)
    service.delete_network_member(id)

# ==================== MEMBERSHIP MANAGEMENT ====================

@router.get("/provider/{provider_id}", response_model=List[ProviderNetworkMemberOut])
@handle_exceptions
def get_provider_memberships(
    provider_id: UUID,
    active_only: bool = Query(True, description="Include only active memberships"),
    include_expired: bool = Query(False, description="Include expired memberships"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get all network memberships for a provider"""
    service = create_provider_network_member_service(db)
    return service.get_provider_memberships(
        provider_id=provider_id,
        active_only=active_only,
        include_expired=include_expired
    )

@router.get("/network/{network_id}", response_model=List[ProviderNetworkMemberOut])
@handle_exceptions
def get_network_members(
    network_id: UUID,
    active_only: bool = Query(True, description="Include only active members"),
    tier_level: Optional[int] = Query(None, ge=1, description="Filter by tier level"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get all members of a network"""
    service = create_provider_network_member_service(db)
    return service.get_network_members(
        network_id=network_id,
        active_only=active_only,
        tier_level=tier_level,
        skip=skip,
        limit=limit
    )

@router.get("/lookup", response_model=ProviderNetworkMemberOut)
@handle_exceptions
def get_membership_by_provider_and_network(
    provider_id: UUID = Query(..., description="Provider ID"),
    network_id: UUID = Query(..., description="Network ID"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get specific membership by provider and network"""
    service = create_provider_network_member_service(db)
    membership = service.get_membership_by_provider_and_network(provider_id, network_id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found for specified provider and network"
        )
    return membership

# ==================== ADVANCED SEARCH & FILTERING ====================

@router.get("", response_model=List[ProviderNetworkMemberOut])
@handle_exceptions
def search_memberships(
    network_id: Optional[UUID] = Query(None, description="Filter by network"),
    provider_id: Optional[UUID] = Query(None, description="Filter by provider"),
    tier_level: Optional[int] = Query(None, ge=1, description="Filter by tier level"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Advanced search for memberships"""
    service = create_provider_network_member_service(db)
    search_params = ProviderNetworkMemberSearch(
        network_id=network_id,
        provider_id=provider_id,
        tier_level=tier_level,
        is_active=is_active
    )
    return service.search_memberships(search_params, skip=skip, limit=limit)

@router.get("/paginated", response_model=dict)
@handle_exceptions
def get_paginated_memberships(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    network_id: Optional[UUID] = Query(None, description="Filter by network"),
    provider_id: Optional[UUID] = Query(None, description="Filter by provider"),
    tier_level: Optional[int] = Query(None, ge=1, description="Filter by tier level"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get paginated memberships with metadata"""
    service = create_provider_network_member_service(db)
    return service.get_paginated_memberships(
        page=page,
        page_size=page_size,
        network_id=network_id,
        provider_id=provider_id,
        tier_level=tier_level,
        is_active=is_active
    )

# ==================== MEMBERSHIP LIFECYCLE ====================

@router.post("/bulk/expire", response_model=dict)
@handle_exceptions
def expire_memberships(
    request: dict,  # Expected: {"membership_ids": [...], "end_date": "2024-12-31"}
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """
    Expire multiple memberships
    
    Request body should contain:
    - membership_ids: List[UUID] - IDs of memberships to expire
    - end_date: str (optional) - End date in YYYY-MM-DD format (defaults to today)
    """
    if "membership_ids" not in request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request must include 'membership_ids' field"
        )
    
    end_date = None
    if "end_date" in request and request["end_date"]:
        try:
            end_date = date.fromisoformat(request["end_date"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD format"
            )
    
    service = create_provider_network_member_service(db)
    return service.expire_memberships(
        membership_ids=request["membership_ids"],
        end_date=end_date
    )

@router.get("/expiring", response_model=List[ProviderNetworkMemberOut])
@handle_exceptions
def get_expiring_memberships(
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead to check for expiration"),
    network_id: Optional[UUID] = Query(None, description="Filter by network"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get memberships expiring within specified days"""
    service = create_provider_network_member_service(db)
    return service.get_expiring_memberships(
        days_ahead=days_ahead,
        network_id=network_id
    )

@router.post("/{id}/renew", response_model=ProviderNetworkMemberOut)
@handle_exceptions
def renew_membership(
    id: UUID,
    new_end_date: Optional[str] = Query(None, description="New end date (YYYY-MM-DD)"),
    extend_months: Optional[int] = Query(None, ge=1, le=60, description="Extend by months"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """Renew a membership by extending end date"""
    parsed_end_date = None
    if new_end_date:
        try:
            parsed_end_date = date.fromisoformat(new_end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD format"
            )
    
    service = create_provider_network_member_service(db)
    return service.renew_membership(
        membership_id=id,
        new_end_date=parsed_end_date,
        extend_months=extend_months
    )

# ==================== TIER MANAGEMENT ====================

@router.post("/bulk/tier-update", response_model=dict)
@handle_exceptions
def bulk_update_tier_levels(
    membership_updates: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """
    Bulk update tier levels for memberships
    
    Request body should be a list of objects with:
    - membership_id: UUID - Membership ID
    - new_tier_level: int - New tier level
    """
    service = create_provider_network_member_service(db)
    return service.bulk_update_tier_levels(membership_updates)

@router.post("/{id}/change-tier", response_model=ProviderNetworkMemberOut)
@handle_exceptions
def change_member_tier(
    id: UUID,
    new_tier_level: int = Query(..., ge=1, description="New tier level"),
    effective_date: Optional[str] = Query(None, description="Effective date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """Change tier level for a specific membership"""
    parsed_date = None
    if effective_date:
        try:
            parsed_date = date.fromisoformat(effective_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD format"
            )
    
    service = create_provider_network_member_service(db)
    return service.change_member_tier(
        membership_id=id,
        new_tier_level=new_tier_level,
        effective_date=parsed_date
    )

# ==================== ANALYTICS & STATISTICS ====================

@router.get("/analytics/statistics", response_model=Dict[str, Any])
@handle_exceptions
def get_membership_statistics(
    network_id: Optional[UUID] = Query(None, description="Filter by network"),
    provider_id: Optional[UUID] = Query(None, description="Filter by provider"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get membership statistics"""
    service = create_provider_network_member_service(db)
    return service.get_membership_statistics(
        network_id=network_id,
        provider_id=provider_id
    )

@router.get("/analytics/membership-overview", response_model=Dict[str, Any])
@handle_exceptions
def get_membership_overview(
    network_id: Optional[UUID] = Query(None, description="Filter by network"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get comprehensive membership overview"""
    service = create_provider_network_member_service(db)
    
    # Get statistics
    stats = service.get_membership_statistics(network_id=network_id)
    
    # Get expiring memberships
    expiring = service.get_expiring_memberships(days_ahead=30, network_id=network_id)
    
    return {
        "statistics": stats,
        "alerts": {
            "expiring_soon": len(expiring),
            "expiring_details": [
                {
                    "id": str(m.id),
                    "provider_id": str(m.provider_id),
                    "network_id": str(m.network_id),
                    "end_date": m.end_date.isoformat() if m.end_date else None,
                    "tier_level": m.tier_level
                }
                for m in expiring[:10]  # Show first 10
            ]
        },
        "filters_applied": {
            "network_id": str(network_id) if network_id else None
        }
    }

# ==================== VALIDATION ENDPOINTS ====================

@router.get("/validate/membership", response_model=dict)
@handle_exceptions
def validate_membership_exists(
    provider_id: UUID = Query(..., description="Provider ID"),
    network_id: UUID = Query(..., description="Network ID"),
    exclude_id: Optional[UUID] = Query(None, description="ID to exclude from validation"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Check if membership already exists"""
    service = create_provider_network_member_service(db)
    existing = service.get_membership_by_provider_and_network(provider_id, network_id)
    
    already_exists = False
    if existing:
        if exclude_id is None or existing.id != exclude_id:
            already_exists = True
    
    return {
        "provider_id": str(provider_id),
        "network_id": str(network_id),
        "already_exists": already_exists,
        "existing_id": str(existing.id) if existing else None,
        "existing_tier_level": existing.tier_level if existing else None,
        "existing_is_active": existing.is_active if existing else None
    }

# ==================== MAINTENANCE OPERATIONS ====================

@router.get("/maintenance/health-check", response_model=Dict[str, Any])
@handle_exceptions
def membership_health_check(
    network_id: Optional[UUID] = Query(None, description="Filter by network"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "admin"))
):
    """Get membership health check report"""
    service = create_provider_network_member_service(db)
    
    # Get various health metrics
    stats = service.get_membership_statistics(network_id=network_id)
    expiring_30 = service.get_expiring_memberships(days_ahead=30, network_id=network_id)
    expiring_7 = service.get_expiring_memberships(days_ahead=7, network_id=network_id)
    
    return {
        "health_summary": {
            "total_memberships": stats.get("total_memberships", 0),
            "active_memberships": stats.get("active_memberships", 0),
            "inactive_memberships": stats.get("inactive_memberships", 0),
            "expiring_in_30_days": len(expiring_30),
            "expiring_in_7_days": len(expiring_7),
            "health_score": "Good" if len(expiring_7) == 0 else "Needs Attention"
        },
        "tier_distribution": stats.get("tier_distribution", []),
        "alerts": {
            "urgent_renewals_needed": len(expiring_7),
            "upcoming_renewals_needed": len(expiring_30)
        },
        "filters_applied": {
            "network_id": str(network_id) if network_id else None
        }
    }