# app/modules/providers/routes/provider_types_route.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.dependencies import get_db, require_permission_scoped
from app.core.exceptions import handle_exceptions
from app.modules.providers.schemas.provider_type_schema import (
    ProviderTypeOut,
    ProviderTypeCreate,
    ProviderTypeUpdate,
    ProviderTypeSearch
)
from app.modules.providers.services import create_provider_type_service

router = APIRouter(prefix="/provider-types", tags=["Provider Types"])

# ==================== BASIC CRUD OPERATIONS ====================

@router.get("/{id}", response_model=ProviderTypeOut)
@handle_exceptions
def get_provider_type(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get provider type by ID"""
    service = create_provider_type_service(db)
    return service.get_provider_type(id)

@router.post("", response_model=ProviderTypeOut, status_code=status.HTTP_201_CREATED)
@handle_exceptions
def create_provider_type(
    obj_in: ProviderTypeCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "create"))
):
    """Create new provider type"""
    service = create_provider_type_service(db)
    return service.create_provider_type(obj_in)

@router.put("/{id}", response_model=ProviderTypeOut)
@handle_exceptions
def update_provider_type(
    id: UUID,
    obj_in: ProviderTypeUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """Update provider type"""
    service = create_provider_type_service(db)
    return service.update_provider_type(id, obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
def delete_provider_type(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "delete"))
):
    """Delete provider type"""
    service = create_provider_type_service(db)
    service.delete_provider_type(id)

# ==================== ADVANCED SEARCH & FILTERING ====================

@router.get("", response_model=List[ProviderTypeOut])
@handle_exceptions
def list_provider_types(
    search: Optional[str] = Query(None, description="Search in code, label, or description"),
    category: Optional[str] = Query(None, description="Filter by category (medical, motor, dental, vision, pharmacy)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """List provider types with advanced filtering and search"""
    service = create_provider_type_service(db)
    search_params = ProviderTypeSearch(
        search=search,
        category=category,
        is_active=is_active
    )
    return service.search_provider_types(search_params, skip=skip, limit=limit)

@router.get("/paginated", response_model=dict)
@handle_exceptions
def get_paginated_provider_types(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get paginated provider types with metadata"""
    service = create_provider_type_service(db)
    return service.get_paginated_provider_types(
        page=page,
        page_size=page_size,
        category=category,
        is_active=is_active,
        search_term=search
    )

# ==================== BUSINESS LOGIC OPERATIONS ====================

@router.get("/active", response_model=List[ProviderTypeOut])
@handle_exceptions
def get_active_provider_types(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get all active provider types, optionally filtered by category"""
    service = create_provider_type_service(db)
    return service.get_active_types(category=category)

@router.get("/by-code/{code}", response_model=ProviderTypeOut)
@handle_exceptions
def get_provider_type_by_code(
    code: str,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get provider type by unique code"""
    service = create_provider_type_service(db)
    provider_type = service.get_provider_type_by_code(code)
    if not provider_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider type with code '{code}' not found"
        )
    return provider_type

# ==================== ANALYTICS & STATISTICS ====================

@router.get("/analytics/categories", response_model=List[dict])
@handle_exceptions
def get_categories_with_stats(
    active_only: bool = Query(True, description="Include only active provider types"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get categories with provider type counts and statistics"""
    service = create_provider_type_service(db)
    return service.get_categories_with_stats(active_only=active_only)

@router.get("/{id}/usage", response_model=dict)
@handle_exceptions
def get_provider_type_usage(
    id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get usage statistics for a provider type"""
    service = create_provider_type_service(db)
    return service.get_provider_type_usage(id)

# ==================== BULK OPERATIONS ====================

@router.patch("/bulk/status", response_model=dict)
@handle_exceptions
def bulk_update_status(
    request: dict,  # Expected: {"provider_type_ids": [...], "is_active": bool}
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "update"))
):
    """
    Bulk update active status for multiple provider types
    
    Request body should contain:
    - provider_type_ids: List[UUID] - IDs of provider types to update
    - is_active: bool - New active status
    """
    if "provider_type_ids" not in request or "is_active" not in request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request must include 'provider_type_ids' and 'is_active' fields"
        )
    
    service = create_provider_type_service(db)
    return service.bulk_update_status(
        provider_type_ids=request["provider_type_ids"],
        is_active=request["is_active"]
    )

# ==================== VALIDATION ENDPOINTS ====================

@router.get("/validate/code/{code}", response_model=dict)
@handle_exceptions
def validate_code_availability(
    code: str,
    exclude_id: Optional[UUID] = Query(None, description="ID to exclude from validation"),
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Check if provider type code is available"""
    service = create_provider_type_service(db)
    existing = service.get_provider_type_by_code(code)
    
    is_available = True
    if existing:
        if exclude_id is None or existing.id != exclude_id:
            is_available = False
    
    return {
        "code": code,
        "is_available": is_available,
        "existing_id": str(existing.id) if existing else None,
        "existing_label": existing.label if existing else None
    }

# ==================== MAINTENANCE OPERATIONS ====================

@router.get("/maintenance/duplicates", response_model=List[dict])
@handle_exceptions
def find_duplicate_codes(
    db: Session = Depends(get_db),
    _=Depends(require_permission_scoped("provider", "admin"))
):
    """Find provider types with duplicate codes (maintenance endpoint)"""
    # This would use a repository method to find duplicates
    # For now, return empty list as duplicate prevention is handled at service level
    return []

@router.get("/categories/enum", response_model=List[str])
@handle_exceptions
def get_valid_categories(
    _=Depends(require_permission_scoped("provider", "view"))
):
    """Get list of valid categories"""
    return ["medical", "motor", "dental", "vision", "pharmacy"]