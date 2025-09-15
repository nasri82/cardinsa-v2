# app/modules/pricing/profiles/routes/pricing_profile_route.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.responses import create_response, create_error_response, success_response
from app.modules.pricing.profiles.services.pricing_profile_service import PricingProfileService
from app.modules.pricing.profiles.services.pricing_profile_validation_service import PricingProfileValidationService
from app.modules.pricing.profiles.schemas.pricing_profile_schema import (
    PricingProfileCreate,
    PricingProfileUpdate,
    PricingProfileResponse,
    PricingProfileWithRules,
    PricingProfileSearchFilters,
    PricingProfileCloneRequest
)
from app.modules.auth.models.user_model import User
from app.core.exceptions import EntityNotFoundError, BusinessLogicError, ValidationError


router = APIRouter(prefix="/pricing/profiles", tags=["Pricing Profiles"])


def get_pricing_profile_service(db: Session = Depends(get_db)) -> PricingProfileService:
    """Dependency to get pricing profile service."""
    return PricingProfileService(db)


def get_validation_service(db: Session = Depends(get_db)) -> PricingProfileValidationService:
    """Dependency to get validation service."""
    return PricingProfileValidationService(db)


# ============================================================================
# PROFILE CRUD ENDPOINTS
# ============================================================================

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_pricing_profile(
    profile_data: PricingProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service),
    validation_service: PricingProfileValidationService = Depends(get_validation_service)
):
    """
    Create a new pricing profile.
    
    - **name**: Required profile name (max 255 characters)
    - **description**: Optional profile description
    - **code**: Optional unique profile code (max 50 characters)
    - **insurance_type**: Type of insurance (Medical, Motor, Life, etc.)
    - **currency**: 3-letter currency code (USD, EUR, etc.)
    - **min_premium**: Minimum premium boundary
    - **max_premium**: Maximum premium boundary
    - **risk_formula**: Optional risk calculation formula
    - **enable_benefit_exposure**: Enable benefit exposure calculations
    - **benefit_exposure_factor**: Factor for benefit exposure (if enabled)
    - **enable_network_costs**: Enable network cost calculations
    - **network_cost_factor**: Factor for network costs (if enabled)
    """
    try:
        # Validate profile data
        validation_result = validation_service.validate_profile_create(profile_data.model_dump())
        
        if not validation_result['is_valid']:
            return create_error_response(
                message="Profile validation failed",
                errors=validation_result['errors'],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the profile
        created_profile = profile_service.create_pricing_profile(
            profile_data=profile_data,
            created_by=current_user.id
        )
        
        return create_response(
            data=created_profile.model_dump(),
            message="Pricing profile created successfully",
            status_code=status.HTTP_201_CREATED,
            meta={
                "validation_warnings": validation_result.get('warnings', []),
                "created_by": str(current_user.id)
            }
        )
        
    except ValidationError as e:
        return create_error_response(
            message="Validation error",
            errors=[str(e)],
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except BusinessLogicError as e:
        return create_error_response(
            message="Business logic error",
            errors=[str(e)],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return create_error_response(
            message="Failed to create pricing profile",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{profile_id}", response_model=Dict[str, Any])
async def get_pricing_profile(
    profile_id: UUID,
    include_rules: bool = Query(False, description="Include associated pricing rules"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Get a pricing profile by ID.
    
    - **profile_id**: UUID of the pricing profile
    - **include_rules**: Whether to include associated rules in response
    """
    try:
        profile = profile_service.get_pricing_profile(
            profile_id=profile_id,
            include_rules=include_rules
        )
        
        if not profile:
            return create_error_response(
                message=f"Pricing profile {profile_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return create_response(
            data=profile.model_dump() if hasattr(profile, 'model_dump') else profile,
            message="Pricing profile retrieved successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to retrieve pricing profile",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{profile_id}", response_model=Dict[str, Any])
async def update_pricing_profile(
    profile_id: UUID,
    profile_data: PricingProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service),
    validation_service: PricingProfileValidationService = Depends(get_validation_service)
):
    """
    Update an existing pricing profile.
    
    - **profile_id**: UUID of the pricing profile to update
    - All fields are optional and only provided fields will be updated
    """
    try:
        # Validate update data
        validation_result = validation_service.validate_profile_update(
            profile_id=profile_id,
            update_data=profile_data.model_dump(exclude_unset=True)
        )
        
        if not validation_result['is_valid']:
            return create_error_response(
                message="Profile update validation failed",
                errors=validation_result['errors'],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the profile
        updated_profile = profile_service.update_pricing_profile(
            profile_id=profile_id,
            profile_data=profile_data,
            updated_by=current_user.id
        )
        
        if not updated_profile:
            return create_error_response(
                message=f"Pricing profile {profile_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return create_response(
            data=updated_profile.model_dump(),
            message="Pricing profile updated successfully",
            meta={
                "validation_warnings": validation_result.get('warnings', []),
                "impact_analysis": validation_result.get('impact_analysis', {}),
                "updated_by": str(current_user.id)
            }
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except ValidationError as e:
        return create_error_response(
            message="Validation error",
            errors=[str(e)],
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except BusinessLogicError as e:
        return create_error_response(
            message="Business logic error",
            errors=[str(e)],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return create_error_response(
            message="Failed to update pricing profile",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{profile_id}", response_model=Dict[str, Any])
async def delete_pricing_profile(
    profile_id: UUID,
    hard_delete: bool = Query(False, description="Permanently delete the profile"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service),
    validation_service: PricingProfileValidationService = Depends(get_validation_service)
):
    """
    Delete a pricing profile.
    
    - **profile_id**: UUID of the pricing profile to delete
    - **hard_delete**: Whether to permanently delete (default: soft delete)
    """
    try:
        # Validate deletion
        validation_result = validation_service.validate_profile_deletion(profile_id)
        
        if not validation_result['can_delete']:
            return create_error_response(
                message="Cannot delete pricing profile",
                errors=[dep['description'] for dep in validation_result['dependencies']],
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        # Delete the profile
        success = profile_service.delete_pricing_profile(
            profile_id=profile_id,
            updated_by=current_user.id,
            hard_delete=hard_delete
        )
        
        if not success:
            return create_error_response(
                message=f"Pricing profile {profile_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return create_response(
            data={"profile_id": str(profile_id), "deleted": True},
            message="Pricing profile deleted successfully",
            meta={
                "deletion_type": "hard" if hard_delete else "soft",
                "deletion_warnings": validation_result.get('warnings', []),
                "deleted_by": str(current_user.id)
            }
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except BusinessLogicError as e:
        return create_error_response(
            message="Business logic error",
            errors=[str(e)],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return create_error_response(
            message="Failed to delete pricing profile",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# PROFILE SEARCH AND FILTERING ENDPOINTS
# ============================================================================

@router.get("/", response_model=Dict[str, Any])
async def search_pricing_profiles(
    name: Optional[str] = Query(None, description="Filter by profile name (partial match)"),
    code: Optional[str] = Query(None, description="Filter by profile code"),
    insurance_type: Optional[str] = Query(None, description="Filter by insurance type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    currency: Optional[str] = Query(None, description="Filter by currency"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Search and filter pricing profiles.
    
    - **name**: Partial match on profile name
    - **code**: Exact match on profile code
    - **insurance_type**: Filter by insurance type
    - **is_active**: Filter by active status
    - **currency**: Filter by currency code
    - **page**: Page number for pagination
    - **page_size**: Number of items per page (max 100)
    """
    try:
        offset = (page - 1) * page_size
        
        results = profile_service.search_pricing_profiles(
            name=name,
            code=code,
            insurance_type=insurance_type,
            is_active=is_active,
            currency=currency,
            limit=page_size,
            offset=offset
        )
        
        return create_response(
            data={
                "profiles": [profile.model_dump() for profile in results['profiles']],
                "pagination": {
                    **results['pagination'],
                    "page": page,
                    "page_size": page_size
                }
            },
            message="Pricing profiles retrieved successfully",
            meta={
                "filters_applied": results['filters_applied']
            }
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to search pricing profiles",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/by-insurance-type/{insurance_type}", response_model=Dict[str, Any])
async def get_profiles_by_insurance_type(
    insurance_type: str,
    active_only: bool = Query(True, description="Return only active profiles"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Get all profiles for a specific insurance type.
    
    - **insurance_type**: Type of insurance (Medical, Motor, Life, etc.)
    - **active_only**: Whether to return only active profiles
    """
    try:
        profiles = profile_service.get_profiles_by_insurance_type(
            insurance_type=insurance_type,
            active_only=active_only
        )
        
        return create_response(
            data={
                "profiles": [profile.model_dump() for profile in profiles],
                "insurance_type": insurance_type,
                "total_count": len(profiles)
            },
            message=f"Profiles for {insurance_type} insurance retrieved successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message=f"Failed to retrieve profiles for {insurance_type} insurance",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# PROFILE RULE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/{profile_id}/rules/{rule_id}", response_model=Dict[str, Any])
async def add_rule_to_profile(
    profile_id: UUID,
    rule_id: UUID,
    order_index: Optional[int] = Query(None, description="Execution order for the rule"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Add a pricing rule to a profile.
    
    - **profile_id**: UUID of the pricing profile
    - **rule_id**: UUID of the pricing rule to add
    - **order_index**: Execution order (auto-assigned if not provided)
    """
    try:
        result = profile_service.add_rule_to_profile(
            profile_id=profile_id,
            rule_id=rule_id,
            order_index=order_index,
            created_by=current_user.id
        )
        
        return create_response(
            data=result,
            message="Rule successfully added to profile",
            status_code=status.HTTP_201_CREATED
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except BusinessLogicError as e:
        return create_error_response(
            message="Business logic error",
            errors=[str(e)],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return create_error_response(
            message="Failed to add rule to profile",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{profile_id}/rules/{rule_id}", response_model=Dict[str, Any])
async def remove_rule_from_profile(
    profile_id: UUID,
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Remove a pricing rule from a profile.
    
    - **profile_id**: UUID of the pricing profile
    - **rule_id**: UUID of the pricing rule to remove
    """
    try:
        result = profile_service.remove_rule_from_profile(
            profile_id=profile_id,
            rule_id=rule_id,
            updated_by=current_user.id
        )
        
        if not result['success']:
            return create_error_response(
                message=result['message'],
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return create_response(
            data={"profile_id": str(profile_id), "rule_id": str(rule_id)},
            message="Rule successfully removed from profile"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to remove rule from profile",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{profile_id}/rules/reorder", response_model=Dict[str, Any])
async def reorder_profile_rules(
    profile_id: UUID,
    rule_orders: Dict[str, int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Reorder rules within a profile.
    
    - **profile_id**: UUID of the pricing profile
    - **rule_orders**: Dictionary mapping rule_id (as string) to new order_index
    
    Example request body:
    ```json
    {
        "550e8400-e29b-41d4-a716-446655440000": 0,
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8": 1,
        "6ba7b811-9dad-11d1-80b4-00c04fd430c8": 2
    }
    ```
    """
    try:
        # Convert string UUIDs to UUID objects
        rule_orders_uuid = {UUID(rule_id): order for rule_id, order in rule_orders.items()}
        
        result = profile_service.reorder_profile_rules(
            profile_id=profile_id,
            rule_orders=rule_orders_uuid,
            updated_by=current_user.id
        )
        
        return create_response(
            data=result,
            message="Profile rules reordered successfully"
        )
        
    except ValueError as e:
        return create_error_response(
            message="Invalid UUID format in rule_orders",
            errors=[str(e)],
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return create_error_response(
            message="Failed to reorder profile rules",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# PROFILE ANALYSIS AND VALIDATION ENDPOINTS
# ============================================================================

@router.get("/{profile_id}/validate", response_model=Dict[str, Any])
async def validate_profile_configuration(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Validate the complete configuration of a pricing profile.
    
    - **profile_id**: UUID of the pricing profile to validate
    
    Returns comprehensive validation results including:
    - Profile configuration validation
    - Rule consistency checks
    - Business logic validation
    - Performance recommendations
    """
    try:
        validation_result = profile_service.validate_profile_configuration(profile_id)
        
        return create_response(
            data=validation_result,
            message="Profile validation completed",
            meta={
                "validation_summary": {
                    "is_valid": validation_result['is_valid'],
                    "total_issues": len(validation_result['issues']),
                    "total_warnings": len(validation_result['warnings'])
                }
            }
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return create_error_response(
            message="Failed to validate profile configuration",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{profile_id}/usage", response_model=Dict[str, Any])
async def check_profile_usage(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Check how a pricing profile is being used in the system.
    
    - **profile_id**: UUID of the pricing profile
    
    Returns usage information including:
    - Number of quotations using this profile
    - Active vs inactive usage
    - Recent usage patterns
    """
    try:
        usage_info = profile_service.check_profile_usage(profile_id)
        
        return create_response(
            data=usage_info,
            message="Profile usage information retrieved successfully"
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return create_error_response(
            message="Failed to check profile usage",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{profile_id}/analytics", response_model=Dict[str, Any])
async def get_profile_analytics(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Get comprehensive analytics for a pricing profile.
    
    - **profile_id**: UUID of the pricing profile
    
    Returns detailed analytics including:
    - Profile configuration summary
    - Rule analytics and statistics
    - Usage patterns and metrics
    - Validation status overview
    """
    try:
        analytics = profile_service.get_profile_analytics(profile_id)
        
        return create_response(
            data=analytics,
            message="Profile analytics retrieved successfully"
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return create_error_response(
            message="Failed to retrieve profile analytics",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# PROFILE OPERATIONS ENDPOINTS
# ============================================================================

@router.post("/{profile_id}/clone", response_model=Dict[str, Any])
async def clone_pricing_profile(
    profile_id: UUID,
    clone_request: PricingProfileCloneRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Clone an existing pricing profile.
    
    - **profile_id**: UUID of the profile to clone
    - **new_name**: Name for the cloned profile
    - **new_code**: Optional code for the cloned profile
    - **include_rules**: Whether to copy associated rules
    """
    try:
        cloned_profile = profile_service.clone_pricing_profile(
            source_profile_id=profile_id,
            new_name=clone_request.new_name,
            new_code=clone_request.new_code,
            include_rules=clone_request.include_rules,
            created_by=current_user.id
        )
        
        return create_response(
            data=cloned_profile.model_dump(),
            message="Profile cloned successfully",
            status_code=status.HTTP_201_CREATED,
            meta={
                "source_profile_id": str(profile_id),
                "rules_copied": clone_request.include_rules,
                "created_by": str(current_user.id)
            }
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except BusinessLogicError as e:
        return create_error_response(
            message="Business logic error",
            errors=[str(e)],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return create_error_response(
            message="Failed to clone pricing profile",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{profile_id}/activate", response_model=Dict[str, Any])
async def activate_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Activate a pricing profile after validation.
    
    - **profile_id**: UUID of the pricing profile to activate
    
    Profile will be validated before activation to ensure it's ready for use.
    """
    try:
        activated_profile = profile_service.activate_profile(
            profile_id=profile_id,
            updated_by=current_user.id
        )
        
        return create_response(
            data=activated_profile.model_dump(),
            message="Profile activated successfully",
            meta={
                "activated_by": str(current_user.id),
                "activation_timestamp": activated_profile.updated_at.isoformat() if activated_profile.updated_at else None
            }
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except BusinessLogicError as e:
        return create_error_response(
            message="Cannot activate profile",
            errors=[str(e)],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return create_error_response(
            message="Failed to activate profile",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{profile_id}/deactivate", response_model=Dict[str, Any])
async def deactivate_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_pricing_profile_service)
):
    """
    Deactivate a pricing profile.
    
    - **profile_id**: UUID of the pricing profile to deactivate
    
    Profile will be checked for active usage before deactivation.
    """
    try:
        deactivated_profile = profile_service.deactivate_profile(
            profile_id=profile_id,
            updated_by=current_user.id
        )
        
        return create_response(
            data=deactivated_profile.model_dump(),
            message="Profile deactivated successfully",
            meta={
                "deactivated_by": str(current_user.id),
                "deactivation_timestamp": deactivated_profile.updated_at.isoformat() if deactivated_profile.updated_at else None
            }
        )
        
    except EntityNotFoundError as e:
        return create_error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND
        )
    except BusinessLogicError as e:
        return create_error_response(
            message="Cannot deactivate profile",
            errors=[str(e)],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return create_error_response(
            message="Failed to deactivate profile",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )