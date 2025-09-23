"""
Benefit Limit Routes - Limits Tracking & Compliance Monitoring API
==================================================================

Enterprise-grade REST API for benefit limit management with comprehensive
tracking, usage monitoring, and compliance checking capabilities.

Author: Assistant
Created: 2024
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from decimal import Decimal
import asyncio
import io

# Core imports - FIXED
from app.core.database import get_db
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.core.dependencies import get_current_user, require_role
from app.core.logging import get_logger
from app.utils.response import success_response, error_response
from app.utils.pagination import PaginatedResponse, PaginationParams

# Service imports
from app.modules.pricing.benefits.services.benefit_limit_service import BenefitLimitService
from app.modules.pricing.benefits.models.benefit_limit_model import BenefitLimit, LimitType, LimitPeriod, LimitStatus

# Schema imports
from app.modules.pricing.benefits.schemas.benefit_limit_schema import (
    BenefitLimitCreate,
    BenefitLimitUpdate,
    BenefitLimitResponse,
    BenefitLimitWithDetails,
    LimitUsageTracking,
    ComplianceCheck,
    LimitBreach,
    AccumulatorStatus,
    LimitOverride,
    UsageProjection,
    ComplianceReport,
    LimitHierarchy,
    LimitResetCycle,
    BenefitLimitSearchFilter,
    BulkLimitOperation
)

logger = get_logger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1/benefit-limits",
    tags=["Benefit Limits"],
    responses={
        404: {"description": "Benefit limit not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# =====================================================================
# CORE CRUD OPERATIONS
# =====================================================================

@router.post(
    "/",
    response_model=BenefitLimitResponse,
    status_code=201,
    summary="Create Benefit Limit",
    description="Create a new benefit limit with tracking configuration"
)
async def create_benefit_limit(
    limit_data: BenefitLimitCreate,
    validate_hierarchy: bool = Query(True, description="Validate limit hierarchy relationships"),
    initialize_tracking: bool = Query(True, description="Initialize usage tracking"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new benefit limit"""
    try:
        if not current_user.has_any(["admin", "benefits_manager", "compliance_officer"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitLimitService(db)
        limit = await service.create_benefit_limit(
            limit_data.dict(),
            validate_hierarchy=validate_hierarchy,
            initialize_tracking=initialize_tracking
        )
        
        logger.info(
            f"Benefit limit created by {current_user.id}: {limit.name}",
            extra={"limit_id": str(limit.id), "user_id": str(current_user.id)}
        )
        
        return BenefitLimitResponse.from_orm(limit)
        
    except ValidationError as e:
        logger.error(f"Benefit limit creation validation failed: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Benefit limit creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create benefit limit")


@router.get(
    "/{limit_id}",
    response_model=BenefitLimitResponse,
    summary="Get Benefit Limit",
    description="Retrieve a specific benefit limit by ID"
)
async def get_benefit_limit(
    limit_id: str = Path(..., description="Benefit limit ID"),
    include_usage: bool = Query(False, description="Include current usage information"),
    include_hierarchy: bool = Query(False, description="Include hierarchy relationships"),
    member_id: Optional[str] = Query(None, description="Member-specific limit information"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific benefit limit"""
    try:
        service = BenefitLimitService(db)
        
        if include_usage or include_hierarchy:
            limit = await service.get_limit_with_details(
                limit_id,
                include_usage=include_usage,
                include_hierarchy=include_hierarchy,
                member_id=member_id
            )
            if not limit:
                raise HTTPException(status_code=404, detail="Benefit limit not found")
            return BenefitLimitWithDetails.from_orm(limit)
        else:
            limit = await service.get_by_id(limit_id)
            if not limit:
                raise HTTPException(status_code=404, detail="Benefit limit not found")
            return BenefitLimitResponse.from_orm(limit)
            
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit limit not found")
    except Exception as e:
        logger.error(f"Failed to retrieve benefit limit {limit_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve benefit limit")


@router.put(
    "/{limit_id}",
    response_model=BenefitLimitResponse,
    summary="Update Benefit Limit",
    description="Update an existing benefit limit"
)
async def update_benefit_limit(
    limit_id: str = Path(..., description="Benefit limit ID"),
    limit_data: BenefitLimitUpdate = Body(...),
    validate_impact: bool = Query(True, description="Validate impact on existing usage"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing benefit limit"""
    try:
        if not current_user.has_any(["admin", "benefits_manager", "compliance_officer"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitLimitService(db)
        limit = await service.update_benefit_limit(
            limit_id, 
            limit_data.dict(exclude_unset=True),
            validate_impact=validate_impact
        )
        
        logger.info(
            f"Benefit limit updated by {current_user.id}: {limit.name}",
            extra={"limit_id": str(limit.id), "user_id": str(current_user.id)}
        )
        
        return BenefitLimitResponse.from_orm(limit)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit limit not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Benefit limit update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update benefit limit")


@router.delete(
    "/{limit_id}",
    status_code=204,
    summary="Delete Benefit Limit",
    description="Delete a benefit limit and handle dependencies"
)
async def delete_benefit_limit(
    limit_id: str = Path(..., description="Benefit limit ID"),
    force: bool = Query(False, description="Force delete with active usage"),
    cleanup_usage: bool = Query(True, description="Clean up associated usage data"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a benefit limit"""
    try:
        if not current_user.has_any(["admin"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitLimitService(db)
        await service.delete_benefit_limit(
            limit_id, 
            force=force,
            cleanup_usage=cleanup_usage
        )
        
        logger.info(
            f"Benefit limit deleted by {current_user.id}: {limit_id}",
            extra={"limit_id": limit_id, "user_id": str(current_user.id)}
        )
        
        return JSONResponse(status_code=204, content=None)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit limit not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Benefit limit deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete benefit limit")

# =====================================================================
# USAGE TRACKING AND MONITORING
# =====================================================================

@router.post(
    "/{limit_id}/track-usage",
    response_model=LimitUsageTracking,
    summary="Track Limit Usage",
    description="Track usage against a specific benefit limit"
)
async def track_limit_usage(
    limit_id: str = Path(..., description="Benefit limit ID"),
    member_id: str = Body(..., description="Member ID"),
    usage_amount: Decimal = Body(..., description="Usage amount to track"),
    service_date: date = Body(..., description="Date of service"),
    service_details: Optional[Dict[str, Any]] = Body(None, description="Service details"),
    validate_compliance: bool = Query(True, description="Validate compliance after tracking"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Track usage against a benefit limit"""
    try:
        service = BenefitLimitService(db)
        tracking_result = await service.track_limit_usage(
            limit_id=limit_id,
            member_id=member_id,
            usage_amount=usage_amount,
            service_date=service_date,
            service_details=service_details or {},
            validate_compliance=validate_compliance
        )
        
        logger.info(
            f"Limit usage tracked: {usage_amount} for member {member_id}",
            extra={
                "limit_id": limit_id,
                "member_id": member_id,
                "usage_amount": float(usage_amount),
                "remaining": float(tracking_result.remaining_amount)
            }
        )
        
        return tracking_result
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit limit not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Usage tracking failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track usage")


@router.get(
    "/member/{member_id}/usage-summary",
    response_model=List[LimitUsageTracking],
    summary="Get Member Usage Summary",
    description="Get comprehensive usage summary for a member across all limits"
)
@cache_response(ttl=300)
async def get_member_usage_summary(
    member_id: str = Path(..., description="Member ID"),
    limit_types: Optional[List[LimitType]] = Query(None, description="Filter by limit types"),
    period: Optional[str] = Query("current", description="Usage period"),
    include_projections: bool = Query(False, description="Include usage projections"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get member usage summary across all limits"""
    try:
        service = BenefitLimitService(db)
        usage_summary = await service.get_member_usage_summary(
            member_id=member_id,
            limit_types=limit_types,
            period=period,
            include_projections=include_projections
        )
        
        return usage_summary
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Member not found")
    except Exception as e:
        logger.error(f"Failed to get member usage summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get usage summary")


@router.get(
    "/{limit_id}/accumulators",
    response_model=List[AccumulatorStatus],
    summary="Get Limit Accumulators",
    description="Get accumulator status for a benefit limit"
)
@cache_response(ttl=300)
async def get_limit_accumulators(
    limit_id: str = Path(..., description="Benefit limit ID"),
    member_id: Optional[str] = Query(None, description="Specific member ID"),
    accumulator_types: Optional[List[str]] = Query(None, description="Filter by accumulator types"),
    as_of_date: Optional[date] = Query(None, description="Accumulator status as of date"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get accumulator status for a limit"""
    try:
        service = BenefitLimitService(db)
        accumulators = await service.get_limit_accumulators(
            limit_id=limit_id,
            member_id=member_id,
            accumulator_types=accumulator_types,
            as_of_date=as_of_date or date.today()
        )
        
        return accumulators
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit limit not found")
    except Exception as e:
        logger.error(f"Failed to get limit accumulators: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get accumulators")


# =====================================================================
# COMPLIANCE CHECKING
# =====================================================================

@router.post(
    "/compliance/check",
    response_model=ComplianceCheck,
    summary="Check Compliance",
    description="Check compliance against benefit limits for a proposed service"
)
@rate_limit(requests=500, window=3600)
async def check_compliance(
    member_id: str = Body(..., description="Member ID"),
    service_request: Dict[str, Any] = Body(..., description="Service request details"),
    limit_ids: Optional[List[str]] = Body(None, description="Specific limit IDs to check"),
    include_warnings: bool = Query(True, description="Include compliance warnings"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Check compliance against benefit limits"""
    try:
        service = BenefitLimitService(db)
        compliance_result = await service.check_compliance(
            member_id=member_id,
            service_request=service_request,
            limit_ids=limit_ids,
            include_warnings=include_warnings
        )
        
        logger.info(
            f"Compliance check completed for member {member_id}: compliant={compliance_result.is_compliant}",
            extra={
                "member_id": member_id,
                "is_compliant": compliance_result.is_compliant,
                "violation_count": len(compliance_result.violations)
            }
        )
        
        return compliance_result
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Compliance check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Compliance check failed")


@router.get(
    "/compliance/breaches",
    response_model=PaginatedResponse[LimitBreach],
    summary="Get Limit Breaches",
    description="Get limit breaches with filtering and pagination"
)
async def get_limit_breaches(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    
    # Filters
    member_id: Optional[str] = Query(None, description="Filter by member ID"),
    limit_id: Optional[str] = Query(None, description="Filter by limit ID"),
    breach_date_after: Optional[date] = Query(None, description="Breaches after date"),
    breach_date_before: Optional[date] = Query(None, description="Breaches before date"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    
    # Sorting
    sort_by: str = Query("breach_date", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get limit breaches with filtering"""
    try:
        require_permissions(current_user, ["admin", "benefits_manager", "compliance_officer"])
        
        service = BenefitLimitService(db)
        
        # Build filters
        filters = {
            "member_id": member_id,
            "limit_id": limit_id,
            "breach_date_after": breach_date_after,
            "breach_date_before": breach_date_before,
            "resolved": resolved
        }
        
        result = await service.get_limit_breaches(
            filters={k: v for k, v in filters.items() if v is not None},
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return PaginatedResponse(
            items=[LimitBreach.from_orm(breach) for breach in result.items],
            total=result.total,
            page=page,
            size=size,
            pages=result.pages
        )
        
    except Exception as e:
        logger.error(f"Failed to get limit breaches: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get breaches")


@router.post(
    "/compliance/report",
    response_model=ComplianceReport,
    summary="Generate Compliance Report",
    description="Generate comprehensive compliance report"
)
async def generate_compliance_report(
    report_period: Dict[str, date] = Body(..., description="Report period"),
    limit_ids: Optional[List[str]] = Body(None, description="Specific limit IDs"),
    member_groups: Optional[List[str]] = Body(None, description="Member groups to include"),
    include_trends: bool = Query(True, description="Include trend analysis"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Generate compliance report"""
    try:
        require_permissions(current_user, ["admin", "compliance_officer", "analyst"])
        
        service = BenefitLimitService(db)
        report = await service.generate_compliance_report(
            period=report_period,
            limit_ids=limit_ids,
            member_groups=member_groups,
            include_trends=include_trends,
            include_recommendations=include_recommendations
        )
        
        logger.info(
            f"Compliance report generated by {current_user.get('user_id')}",
            extra={"user_id": current_user.get('user_id'), "report_id": str(report.report_id)}
        )
        
        return report
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Compliance report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Report generation failed")


# =====================================================================
# LIMIT OVERRIDES
# =====================================================================

@router.post(
    "/{limit_id}/overrides",
    response_model=LimitOverride,
    summary="Create Limit Override",
    description="Create a limit override with proper authorization"
)
async def create_limit_override(
    limit_id: str = Path(..., description="Benefit limit ID"),
    member_id: str = Body(..., description="Member ID"),
    override_amount: Decimal = Body(..., description="Override amount"),
    justification: str = Body(..., description="Override justification"),
    expiry_date: Optional[date] = Body(None, description="Override expiry date"),
    approval_required: bool = Query(True, description="Require approval workflow"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Create a limit override"""
    try:
        require_permissions(current_user, ["admin", "benefits_manager", "medical_director"])
        
        service = BenefitLimitService(db)
        override = await service.create_limit_override(
            limit_id=limit_id,
            member_id=member_id,
            override_amount=override_amount,
            justification=justification,
            expiry_date=expiry_date,
            created_by=current_user.get('user_id'),
            approval_required=approval_required
        )
        
        logger.info(
            f"Limit override created by {current_user.get('user_id')}: {override_amount} for member {member_id}",
            extra={
                "limit_id": limit_id,
                "member_id": member_id,
                "override_amount": float(override_amount),
                "user_id": current_user.get('user_id')
            }
        )
        
        return override
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit limit not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Limit override creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create override")


@router.get(
    "/{limit_id}/overrides",
    response_model=List[LimitOverride],
    summary="Get Limit Overrides",
    description="Get overrides for a specific limit"
)
@cache_response(ttl=300)
async def get_limit_overrides(
    limit_id: str = Path(..., description="Benefit limit ID"),
    member_id: Optional[str] = Query(None, description="Filter by member ID"),
    active_only: bool = Query(True, description="Only active overrides"),
    include_expired: bool = Query(False, description="Include expired overrides"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get overrides for a limit"""
    try:
        service = BenefitLimitService(db)
        overrides = await service.get_limit_overrides(
            limit_id=limit_id,
            member_id=member_id,
            active_only=active_only,
            include_expired=include_expired
        )
        
        return overrides
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit limit not found")
    except Exception as e:
        logger.error(f"Failed to get limit overrides: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get overrides")


# =====================================================================
# PREDICTIVE ANALYSIS
# =====================================================================

@router.post(
    "/{limit_id}/project-usage",
    response_model=UsageProjection,
    summary="Project Usage",
    description="Project future usage against a benefit limit"
)
async def project_usage(
    limit_id: str = Path(..., description="Benefit limit ID"),
    member_id: str = Body(..., description="Member ID"),
    projection_period: int = Body(..., description="Projection period in months"),
    historical_data: Optional[Dict[str, Any]] = Body(None, description="Historical usage data"),
    factors: Optional[Dict[str, Any]] = Body(None, description="Projection factors"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Project future usage against a limit"""
    try:
        service = BenefitLimitService(db)
        projection = await service.project_usage(
            limit_id=limit_id,
            member_id=member_id,
            projection_period=projection_period,
            historical_data=historical_data or {},
            factors=factors or {}
        )
        
        logger.info(
            f"Usage projection generated for limit {limit_id}, member {member_id}",
            extra={
                "limit_id": limit_id,
                "member_id": member_id,
                "projected_usage": float(projection.projected_usage)
            }
        )
        
        return projection
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit limit not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Usage projection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Usage projection failed")


# =====================================================================
# LIMIT HIERARCHIES
# =====================================================================

@router.get(
    "/{limit_id}/hierarchy",
    response_model=LimitHierarchy,
    summary="Get Limit Hierarchy",
    description="Get hierarchical structure for a benefit limit"
)
@cache_response(ttl=600)
async def get_limit_hierarchy(
    limit_id: str = Path(..., description="Benefit limit ID"),
    include_children: bool = Query(True, description="Include child limits"),
    include_ancestors: bool = Query(True, description="Include parent limits"),
    max_depth: Optional[int] = Query(None, description="Maximum hierarchy depth"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get limit hierarchy structure"""
    try:
        service = BenefitLimitService(db)
        hierarchy = await service.get_limit_hierarchy(
            limit_id=limit_id,
            include_children=include_children,
            include_ancestors=include_ancestors,
            max_depth=max_depth
        )
        
        return hierarchy
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit limit not found")
    except Exception as e:
        logger.error(f"Failed to get limit hierarchy: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get hierarchy")


# =====================================================================
# RESET CYCLES
# =====================================================================

@router.post(
    "/{limit_id}/reset-cycle",
    response_model=LimitResetCycle,
    summary="Configure Reset Cycle",
    description="Configure or update limit reset cycle"
)
async def configure_reset_cycle(
    limit_id: str = Path(..., description="Benefit limit ID"),
    reset_config: Dict[str, Any] = Body(..., description="Reset cycle configuration"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Configure limit reset cycle"""
    try:
        require_permissions(current_user, ["admin", "benefits_manager"])
        
        service = BenefitLimitService(db)
        reset_cycle = await service.configure_reset_cycle(
            limit_id=limit_id,
            config=reset_config
        )
        
        logger.info(
            f"Reset cycle configured for limit {limit_id} by {current_user.get('user_id')}",
            extra={"limit_id": limit_id, "user_id": current_user.get('user_id')}
        )
        
        return reset_cycle
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Benefit limit not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Reset cycle configuration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to configure reset cycle")


@router.post(
    "/reset-cycles/execute",
    response_model=Dict[str, Any],
    summary="Execute Reset Cycles",
    description="Execute scheduled reset cycles for limits"
)
async def execute_reset_cycles(
    limit_ids: Optional[List[str]] = Body(None, description="Specific limit IDs"),
    reset_date: Optional[date] = Body(None, description="Reset effective date"),
    dry_run: bool = Query(False, description="Perform dry run without actual reset"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Execute reset cycles"""
    try:
        require_permissions(current_user, ["admin", "system_operator"])
        
        service = BenefitLimitService(db)
        result = await service.execute_reset_cycles(
            limit_ids=limit_ids,
            reset_date=reset_date or date.today(),
            dry_run=dry_run
        )
        
        logger.info(
            f"Reset cycles executed by {current_user.get('user_id')}: {result.get('processed_count', 0)} limits",
            extra={
                "user_id": current_user.get('user_id'),
                "processed_count": result.get('processed_count', 0),
                "dry_run": dry_run
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Reset cycle execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Reset cycle execution failed")


# =====================================================================
# SEARCH AND FILTERING
# =====================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[BenefitLimitResponse],
    summary="List Benefit Limits",
    description="List and search benefit limits with advanced filtering"
)
async def list_benefit_limits(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    
    # Basic filters
    search: Optional[str] = Query(None, description="Search term"),
    limit_type: Optional[LimitType] = Query(None, description="Filter by limit type"),
    limit_period: Optional[LimitPeriod] = Query(None, description="Filter by limit period"),
    status: Optional[LimitStatus] = Query(None, description="Filter by status"),
    
    # Advanced filters
    benefit_type_id: Optional[str] = Query(None, description="Filter by benefit type"),
    min_amount: Optional[Decimal] = Query(None, description="Minimum limit amount"),
    max_amount: Optional[Decimal] = Query(None, description="Maximum limit amount"),
    has_overrides: Optional[bool] = Query(None, description="Filter by override presence"),
    
    # Sorting
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """List benefit limits with advanced filtering"""
    try:
        service = BenefitLimitService(db)
        
        # Build filter dictionary
        filters = BenefitLimitSearchFilter(
            search=search,
            limit_type=limit_type,
            limit_period=limit_period,
            status=status,
            benefit_type_id=benefit_type_id,
            min_amount=min_amount,
            max_amount=max_amount,
            has_overrides=has_overrides
        )
        
        # Get paginated results
        result = await service.search_benefit_limits(
            filters=filters.dict(exclude_unset=True),
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return PaginatedResponse(
            items=[BenefitLimitResponse.from_orm(limit) for limit in result.items],
            total=result.total,
            page=page,
            size=size,
            pages=result.pages
        )
        
    except Exception as e:
        logger.error(f"Benefit limit search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search benefit limits")


# =====================================================================
# BULK OPERATIONS
# =====================================================================

@router.post(
    "/bulk/operations",
    response_model=Dict[str, Any],
    summary="Bulk Limit Operations",
    description="Perform bulk operations on multiple benefit limits"
)
async def bulk_limit_operations(
    operation: BulkLimitOperation = Body(...),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Perform bulk operations on benefit limits"""
    try:
        require_permissions(current_user, ["admin", "benefits_manager"])
        
        service = BenefitLimitService(db)
        result = await service.bulk_operations(operation.dict())
        
        logger.info(
            f"Bulk limit operation performed by {current_user.get('user_id')}: {operation.operation_type}",
            extra={
                "operation_type": operation.operation_type,
                "limit_count": len(operation.limit_ids),
                "user_id": current_user.get('user_id')
            }
        )
        
        return result
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Bulk limit operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Bulk operation failed")


# =====================================================================
# ANALYTICS AND REPORTING
# =====================================================================

@router.get(
    "/analytics/utilization",
    response_model=Dict[str, Any],
    summary="Limit Utilization Analytics",
    description="Get analytics on limit utilization patterns"
)
@cache_response(ttl=3600)
async def get_limit_utilization_analytics(
    period: str = Query("90d", description="Analysis period"),
    limit_types: Optional[List[LimitType]] = Query(None, description="Specific limit types"),
    demographic_breakdown: bool = Query(False, description="Include demographic breakdown"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get limit utilization analytics"""
    try:
        service = BenefitLimitService(db)
        analytics = await service.get_utilization_analytics(
            period=period,
            limit_types=limit_types,
            demographic_breakdown=demographic_breakdown
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Limit utilization analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get utilization analytics")


# =====================================================================
# HEALTH CHECK
# =====================================================================

@router.get(
    "/health",
    response_model=Dict[str, str],
    summary="Benefit Limit Service Health Check",
    description="Check the health status of the benefit limit service"
)
async def benefit_limit_service_health(
    db: Session = Depends(get_db_session)
):
    """Health check for benefit limit service"""
    try:
        service = BenefitLimitService(db)
        health_status = await service.health_check()
        
        return {
            "status": "healthy" if health_status else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "BenefitLimitService"
        }
        
    except Exception as e:
        logger.error(f"Benefit limit service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "BenefitLimitService",
            "error": str(e)
        }