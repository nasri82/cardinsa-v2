"""
Plan Benefit Schedule Routes - Master Schedule Management & Versioning API
==========================================================================

Enterprise-grade REST API for plan benefit schedule management with comprehensive
versioning, effective date management, and schedule coordination.

Author: Assistant
Created: 2024
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from decimal import Decimal
import asyncio
import io

# Core imports - FIXED
from app.core.database import get_db
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.core.dependencies import get_current_user, require_role
from app.core.logging import get_logger
from app.core.responses import success_response, error_response
from app.utils.pagination import PaginatedResponse, PaginationParams

# Service imports
from app.modules.pricing.benefits.services.plan_benefit_schedule_service import PlanBenefitScheduleService
from app.modules.pricing.benefits.models.plan_benefit_schedule_model import PlanBenefitSchedule

# Schema imports - FIXED: Import enums from schema file
from app.modules.pricing.benefits.schemas.plan_benefit_schedule_schema import (
    PlanBenefitScheduleCreate,
    PlanBenefitScheduleUpdate,
    PlanBenefitScheduleResponse,
    PlanBenefitScheduleWithDetails,
    ScheduleVersion,
    ScheduleComparison,
    ScheduleDifference,
    ScheduleValidation,
    ScheduleTemplate,
    ScheduleTimeline,
    PlanScheduleAssociation,
    ScheduleMerge,
    ScheduleSearchFilter,
    BulkScheduleOperation,
    # Import enums from schema
    ScheduleStatusEnum,
    ScheduleTypeEnum,
    VersionStatusEnum,
    ApprovalStatusEnum
)

logger = get_logger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1/plan-benefit-schedules",
    tags=["Plan Benefit Schedules"],
    responses={
        404: {"description": "Schedule not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# =====================================================================
# CORE CRUD OPERATIONS
# =====================================================================

@router.post(
    "/",
    response_model=PlanBenefitScheduleResponse,
    status_code=201,
    summary="Create Benefit Schedule",
    description="Create a new plan benefit schedule with validation"
)
async def create_benefit_schedule(
    schedule_data: PlanBenefitScheduleCreate,
    validate_structure: bool = Query(True, description="Validate schedule structure"),
    create_version: bool = Query(True, description="Create initial version"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new plan benefit schedule"""
    try:
        if not current_user.has_any(["admin", "benefits_designer", "schedule_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = PlanBenefitScheduleService(db)
        schedule = await service.create_benefit_schedule(
            schedule_data.model_dump(),
            validate_structure=validate_structure,
            create_version=create_version,
            created_by=str(current_user.id)
        )
        
        logger.info(
            f"Benefit schedule created by {current_user.id}: {schedule.schedule_name}",
            extra={"schedule_id": str(schedule.id), "user_id": str(current_user.id)}
        )
        
        return PlanBenefitScheduleResponse.model_validate(schedule)
        
    except ValidationError as e:
        logger.error(f"Schedule creation validation failed: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Schedule creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create benefit schedule")


@router.get(
    "/{schedule_id}",
    response_model=PlanBenefitScheduleResponse,
    summary="Get Benefit Schedule",
    description="Retrieve a specific benefit schedule by ID"
)
async def get_benefit_schedule(
    schedule_id: str = Path(..., description="Schedule ID"),
    version_id: Optional[str] = Query(None, description="Specific version ID"),
    include_details: bool = Query(False, description="Include detailed configuration"),
    include_associations: bool = Query(False, description="Include plan associations"),
    as_of_date: Optional[date] = Query(None, description="Schedule as of specific date"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific benefit schedule"""
    try:
        service = PlanBenefitScheduleService(db)
        
        if include_details or include_associations:
            schedule = await service.get_schedule_with_details(
                schedule_id,
                version_id=version_id,
                include_associations=include_associations,
                as_of_date=as_of_date or date.today()
            )
            if not schedule:
                raise HTTPException(status_code=404, detail="Schedule not found")
            return PlanBenefitScheduleWithDetails.model_validate(schedule)
        else:
            schedule = await service.get_schedule_by_id(
                schedule_id,
                version_id=version_id,
                as_of_date=as_of_date
            )
            if not schedule:
                raise HTTPException(status_code=404, detail="Schedule not found")
            return PlanBenefitScheduleResponse.model_validate(schedule)
            
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    except Exception as e:
        logger.error(f"Failed to retrieve schedule {schedule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve schedule")


@router.put(
    "/{schedule_id}",
    response_model=PlanBenefitScheduleResponse,
    summary="Update Benefit Schedule",
    description="Update an existing benefit schedule with versioning"
)
async def update_benefit_schedule(
    schedule_id: str = Path(..., description="Schedule ID"),
    schedule_data: PlanBenefitScheduleUpdate = Body(...),
    create_new_version: bool = Query(True, description="Create new version for changes"),
    effective_date: Optional[date] = Body(None, description="Update effective date"),
    validate_changes: bool = Query(True, description="Validate schedule changes"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing benefit schedule"""
    try:
        if not current_user.has_any(["admin", "benefits_designer", "schedule_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = PlanBenefitScheduleService(db)
        schedule = await service.update_benefit_schedule(
            schedule_id,
            schedule_data.model_dump(exclude_unset=True),
            create_new_version=create_new_version,
            effective_date=effective_date or date.today(),
            validate_changes=validate_changes,
            updated_by=str(current_user.id)
        )
        
        logger.info(
            f"Schedule updated by {current_user.id}: {schedule.schedule_name}",
            extra={"schedule_id": str(schedule.id), "user_id": str(current_user.id)}
        )
        
        return PlanBenefitScheduleResponse.model_validate(schedule)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Schedule update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update schedule")


@router.delete(
    "/{schedule_id}",
    status_code=204,
    summary="Delete Benefit Schedule",
    description="Delete a benefit schedule and handle dependencies"
)
async def delete_benefit_schedule(
    schedule_id: str = Path(..., description="Schedule ID"),
    force: bool = Query(False, description="Force delete with active associations"),
    archive_versions: bool = Query(True, description="Archive versions before deletion"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a benefit schedule"""
    try:
        if not current_user.has_any(["admin"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = PlanBenefitScheduleService(db)
        await service.delete_benefit_schedule(
            schedule_id,
            force=force,
            archive_versions=archive_versions,
            deleted_by=str(current_user.id)
        )
        
        logger.info(
            f"Schedule deleted by {current_user.id}: {schedule_id}",
            extra={"schedule_id": schedule_id, "user_id": str(current_user.id)}
        )
        
        return JSONResponse(status_code=204, content=None)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Schedule deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete schedule")

# =====================================================================
# VERSION MANAGEMENT
# =====================================================================

@router.get(
    "/{schedule_id}/versions",
    response_model=List[ScheduleVersion],
    summary="Get Schedule Versions",
    description="Get version history for a benefit schedule"
)
async def get_schedule_versions(
    schedule_id: str = Path(..., description="Schedule ID"),
    include_archived: bool = Query(False, description="Include archived versions"),
    effective_date_start: Optional[date] = Query(None, description="Effective date range start"),
    effective_date_end: Optional[date] = Query(None, description="Effective date range end"),
    limit: int = Query(50, description="Maximum versions to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get schedule version history"""
    try:
        service = PlanBenefitScheduleService(db)
        
        # Build effective date range if provided
        effective_date_range = None
        if effective_date_start or effective_date_end:
            effective_date_range = {}
            if effective_date_start:
                effective_date_range['start'] = effective_date_start
            if effective_date_end:
                effective_date_range['end'] = effective_date_end
        
        versions = await service.get_schedule_versions(
            schedule_id=schedule_id,
            include_archived=include_archived,
            effective_date_range=effective_date_range,
            limit=limit
        )
        
        return versions
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    except Exception as e:
        logger.error(f"Failed to get schedule versions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get versions")


@router.post(
    "/{schedule_id}/versions",
    response_model=ScheduleVersion,
    summary="Create Schedule Version",
    description="Create a new version of an existing schedule"
)
async def create_schedule_version(
    schedule_id: str = Path(..., description="Schedule ID"),
    version_data: Dict[str, Any] = Body(..., description="Version configuration"),
    effective_date: date = Body(..., description="Version effective date"),
    copy_from_version: Optional[str] = Body(None, description="Version ID to copy from"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new schedule version"""
    try:
        if not current_user.has_any(["admin", "benefits_designer", "schedule_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = PlanBenefitScheduleService(db)
        version = await service.create_schedule_version(
            schedule_id=schedule_id,
            version_data=version_data,
            effective_date=effective_date,
            copy_from_version=copy_from_version,
            created_by=str(current_user.id)
        )
        
        logger.info(
            f"Schedule version created by {current_user.id}: {schedule_id} v{version.version_number}",
            extra={
                "schedule_id": schedule_id,
                "version_id": str(version.id),
                "user_id": str(current_user.id)
            }
        )
        
        return version
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Schedule version creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create version")


@router.post(
    "/{schedule_id}/versions/{version_id}/activate",
    response_model=ScheduleVersion,
    summary="Activate Schedule Version",
    description="Activate a specific schedule version"
)
async def activate_schedule_version(
    schedule_id: str = Path(..., description="Schedule ID"),
    version_id: str = Path(..., description="Version ID to activate"),
    activation_date: Optional[date] = Body(None, description="Activation effective date"),
    validate_activation: bool = Query(True, description="Validate before activation"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Activate a schedule version"""
    try:
        if not current_user.has_any(["admin", "benefits_designer"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = PlanBenefitScheduleService(db)
        activated_version = await service.activate_schedule_version(
            schedule_id=schedule_id,
            version_id=version_id,
            activation_date=activation_date or date.today(),
            validate_activation=validate_activation,
            activated_by=str(current_user.id)
        )
        
        logger.info(
            f"Schedule version activated by {current_user.id}: {schedule_id} v{activated_version.version_number}",
            extra={
                "schedule_id": schedule_id,
                "version_id": version_id,
                "user_id": str(current_user.id)
            }
        )
        
        return activated_version
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Schedule or version not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Schedule version activation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Version activation failed")


# =====================================================================
# SCHEDULE COMPARISON
# =====================================================================

@router.post(
    "/compare",
    response_model=ScheduleComparison,
    summary="Compare Schedules",
    description="Compare two benefit schedules or versions"
)
async def compare_schedules(
    schedule_a: Dict[str, Any] = Body(..., description="First schedule reference"),
    schedule_b: Dict[str, Any] = Body(..., description="Second schedule reference"),
    comparison_criteria: Optional[List[str]] = Body(None, description="Specific comparison criteria"),
    include_differences_only: bool = Query(False, description="Include only differences"),
    detailed_analysis: bool = Query(True, description="Include detailed difference analysis"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Compare two schedules or versions"""
    try:
        service = PlanBenefitScheduleService(db)
        comparison = await service.compare_schedules(
            schedule_a=schedule_a,
            schedule_b=schedule_b,
            criteria=comparison_criteria,
            differences_only=include_differences_only,
            detailed_analysis=detailed_analysis
        )
        
        logger.info(
            f"Schedule comparison completed: {comparison.difference_count} differences found",
            extra={"difference_count": comparison.difference_count}
        )
        
        return comparison
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Schedule comparison failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Schedule comparison failed")


@router.get(
    "/{schedule_id}/differences/{other_schedule_id}",
    response_model=List[ScheduleDifference],
    summary="Get Schedule Differences",
    description="Get specific differences between two schedules"
)
async def get_schedule_differences(
    schedule_id: str = Path(..., description="First schedule ID"),
    other_schedule_id: str = Path(..., description="Second schedule ID"),
    version_a: Optional[str] = Query(None, description="First schedule version"),
    version_b: Optional[str] = Query(None, description="Second schedule version"),
    difference_types: Optional[List[str]] = Query(None, description="Filter by difference types"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get differences between two schedules"""
    try:
        service = PlanBenefitScheduleService(db)
        differences = await service.get_schedule_differences(
            schedule_a_id=schedule_id,
            schedule_b_id=other_schedule_id,
            version_a=version_a,
            version_b=version_b,
            difference_types=difference_types
        )
        
        return differences
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get schedule differences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get differences")


# =====================================================================
# SCHEDULE VALIDATION
# =====================================================================

@router.post(
    "/{schedule_id}/validate",
    response_model=ScheduleValidation,
    summary="Validate Schedule",
    description="Validate schedule structure and configuration"
)
async def validate_schedule(
    schedule_id: str = Path(..., description="Schedule ID"),
    version_id: Optional[str] = Body(None, description="Specific version to validate"),
    validation_rules: Optional[List[str]] = Body(None, description="Specific validation rules"),
    comprehensive: bool = Query(True, description="Comprehensive validation"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Validate schedule structure and configuration"""
    try:
        service = PlanBenefitScheduleService(db)
        validation_result = await service.validate_schedule(
            schedule_id=schedule_id,
            version_id=version_id,
            validation_rules=validation_rules,
            comprehensive=comprehensive
        )
        
        logger.info(
            f"Schedule validation completed: {schedule_id}, valid={validation_result.is_valid}",
            extra={
                "schedule_id": schedule_id,
                "is_valid": validation_result.is_valid,
                "error_count": len(validation_result.errors)
            }
        )
        
        return validation_result
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    except Exception as e:
        logger.error(f"Schedule validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Schedule validation failed")


# =====================================================================
# PLAN ASSOCIATIONS
# =====================================================================

@router.post(
    "/{schedule_id}/plans/{plan_id}/associate",
    response_model=PlanScheduleAssociation,
    summary="Associate Schedule with Plan",
    description="Associate a schedule with a plan with effective dates"
)
async def associate_schedule_with_plan(
    schedule_id: str = Path(..., description="Schedule ID"),
    plan_id: str = Path(..., description="Plan ID"),
    effective_date: date = Body(..., description="Association effective date"),
    termination_date: Optional[date] = Body(None, description="Association termination date"),
    association_metadata: Optional[Dict[str, Any]] = Body(None, description="Association metadata"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Associate schedule with plan"""
    try:
        if not current_user.has_any(["admin", "benefits_designer", "plan_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = PlanBenefitScheduleService(db)
        association = await service.associate_schedule_with_plan(
            schedule_id=schedule_id,
            plan_id=plan_id,
            effective_date=effective_date,
            termination_date=termination_date,
            metadata=association_metadata or {},
            created_by=str(current_user.id)
        )
        
        logger.info(
            f"Schedule associated with plan by {current_user.id}: {schedule_id} -> {plan_id}",
            extra={
                "schedule_id": schedule_id,
                "plan_id": plan_id,
                "user_id": str(current_user.id)
            }
        )
        
        return association
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Schedule-plan association failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Association failed")


@router.get(
    "/{schedule_id}/plans",
    response_model=List[PlanScheduleAssociation],
    summary="Get Schedule Plan Associations",
    description="Get all plan associations for a schedule"
)
async def get_schedule_plan_associations(
    schedule_id: str = Path(..., description="Schedule ID"),
    active_only: bool = Query(True, description="Include only active associations"),
    as_of_date: Optional[date] = Query(None, description="Associations as of date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get plan associations for a schedule"""
    try:
        service = PlanBenefitScheduleService(db)
        associations = await service.get_schedule_plan_associations(
            schedule_id=schedule_id,
            active_only=active_only,
            as_of_date=as_of_date or date.today()
        )
        
        return associations
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    except Exception as e:
        logger.error(f"Failed to get schedule associations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get associations")


# =====================================================================
# SCHEDULE TEMPLATES
# =====================================================================

@router.post(
    "/templates",
    response_model=ScheduleTemplate,
    summary="Create Schedule Template",
    description="Create a reusable schedule template"
)
async def create_schedule_template(
    template_data: Dict[str, Any] = Body(..., description="Template configuration"),
    base_schedule_id: Optional[str] = Body(None, description="Base schedule to create template from"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a schedule template"""
    try:
        if not current_user.has_any(["admin", "benefits_designer"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = PlanBenefitScheduleService(db)
        template = await service.create_schedule_template(
            template_data=template_data,
            base_schedule_id=base_schedule_id,
            created_by=str(current_user.id)
        )
        
        logger.info(
            f"Schedule template created by {current_user.id}: {template.template_name}",
            extra={"template_id": str(template.id), "user_id": str(current_user.id)}
        )
        
        return template
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Schedule template creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template creation failed")


@router.post(
    "/templates/{template_id}/apply",
    response_model=PlanBenefitScheduleResponse,
    summary="Apply Schedule Template",
    description="Apply a template to create a new schedule"
)
async def apply_schedule_template(
    template_id: str = Path(..., description="Template ID"),
    schedule_name: str = Body(..., description="New schedule name"),
    customizations: Optional[Dict[str, Any]] = Body(None, description="Template customizations"),
    effective_date: Optional[date] = Body(None, description="Schedule effective date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Apply template to create new schedule"""
    try:
        if not current_user.has_any(["admin", "benefits_designer", "schedule_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = PlanBenefitScheduleService(db)
        schedule = await service.apply_schedule_template(
            template_id=template_id,
            schedule_name=schedule_name,
            customizations=customizations or {},
            effective_date=effective_date or date.today(),
            created_by=str(current_user.id)
        )
        
        logger.info(
            f"Schedule template applied by {current_user.id}: {template_id} -> {schedule.schedule_name}",
            extra={
                "template_id": template_id,
                "schedule_id": str(schedule.id),
                "user_id": str(current_user.id)
            }
        )
        
        return PlanBenefitScheduleResponse.model_validate(schedule)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Template not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Template application failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Template application failed")


# =====================================================================
# SCHEDULE TIMELINE
# =====================================================================

@router.get(
    "/{schedule_id}/timeline",
    response_model=ScheduleTimeline,
    summary="Get Schedule Timeline",
    description="Get timeline of schedule changes and versions"
)
async def get_schedule_timeline(
    schedule_id: str = Path(..., description="Schedule ID"),
    start_date: Optional[date] = Query(None, description="Timeline start date"),
    end_date: Optional[date] = Query(None, description="Timeline end date"),
    include_future: bool = Query(False, description="Include future scheduled changes"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get schedule timeline"""
    try:
        service = PlanBenefitScheduleService(db)
        timeline = await service.get_schedule_timeline(
            schedule_id=schedule_id,
            start_date=start_date,
            end_date=end_date,
            include_future=include_future
        )
        
        return timeline
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    except Exception as e:
        logger.error(f"Failed to get schedule timeline: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get timeline")


# =====================================================================
# SEARCH AND FILTERING
# =====================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[PlanBenefitScheduleResponse],
    summary="List Benefit Schedules",
    description="List and search benefit schedules with advanced filtering"
)
async def list_benefit_schedules(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    
    # Basic filters
    search: Optional[str] = Query(None, description="Search term"),
    schedule_type: Optional[ScheduleTypeEnum] = Query(None, description="Filter by schedule type"),
    status: Optional[ScheduleStatusEnum] = Query(None, description="Filter by status"),
    
    # Date filters
    effective_after: Optional[date] = Query(None, description="Effective after date"),
    effective_before: Optional[date] = Query(None, description="Effective before date"),
    
    # Advanced filters
    plan_id: Optional[str] = Query(None, description="Filter by associated plan"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    has_active_version: Optional[bool] = Query(None, description="Filter by active version presence"),
    
    # Sorting
    sort_by: str = Query("schedule_name", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List benefit schedules with advanced filtering"""
    try:
        service = PlanBenefitScheduleService(db)
        
        # Build filter dictionary
        filters = ScheduleSearchFilter(
            search=search,
            schedule_type=schedule_type,
            status=status,
            effective_after=effective_after,
            effective_before=effective_before,
            plan_id=plan_id,
            created_by=created_by,
            has_active_version=has_active_version
        )
        
        # Get paginated results
        result = await service.search_benefit_schedules(
            filters=filters.model_dump(exclude_unset=True),
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return PaginatedResponse(
            items=[PlanBenefitScheduleResponse.model_validate(schedule) for schedule in result.items],
            total=result.total,
            page=page,
            size=size,
            pages=result.pages
        )
        
    except Exception as e:
        logger.error(f"Schedule search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search schedules")


# =====================================================================
# BULK OPERATIONS
# =====================================================================

@router.post(
    "/bulk/operations",
    response_model=Dict[str, Any],
    summary="Bulk Schedule Operations",
    description="Perform bulk operations on multiple schedules"
)
async def bulk_schedule_operations(
    operation: BulkScheduleOperation = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Perform bulk operations on schedules"""
    try:
        if not current_user.has_any(["admin", "benefits_designer"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = PlanBenefitScheduleService(db)
        result = await service.bulk_operations(operation.model_dump())
        
        logger.info(
            f"Bulk schedule operation performed by {current_user.id}: {operation.operation_type}",
            extra={
                "operation_type": operation.operation_type,
                "schedule_count": len(operation.schedule_ids),
                "user_id": str(current_user.id)
            }
        )
        
        return result
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Bulk schedule operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Bulk operation failed")


# =====================================================================
# ANALYTICS AND REPORTING
# =====================================================================

@router.get(
    "/analytics/usage-patterns",
    response_model=Dict[str, Any],
    summary="Schedule Usage Analytics",
    description="Get analytics on schedule usage patterns"
)
async def get_schedule_usage_analytics(
    period: str = Query("90d", description="Analysis period"),
    schedule_types: Optional[List[ScheduleTypeEnum]] = Query(None, description="Specific schedule types"),
    include_comparisons: bool = Query(True, description="Include version comparisons"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get schedule usage analytics"""
    try:
        service = PlanBenefitScheduleService(db)
        analytics = await service.get_schedule_usage_analytics(
            period=period,
            schedule_types=schedule_types,
            include_comparisons=include_comparisons
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Schedule usage analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get usage analytics")


# =====================================================================
# HEALTH CHECK
# =====================================================================

@router.get(
    "/health",
    response_model=Dict[str, str],
    summary="Schedule Service Health Check",
    description="Check the health status of the schedule service"
)
async def schedule_service_health(
    db: Session = Depends(get_db)
):
    """Health check for schedule service"""
    try:
        service = PlanBenefitScheduleService(db)
        health_status = await service.health_check()
        
        return {
            "status": "healthy" if health_status else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "PlanBenefitScheduleService"
        }
        
    except Exception as e:
        logger.error(f"Schedule service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "PlanBenefitScheduleService",
            "error": str(e)
        }