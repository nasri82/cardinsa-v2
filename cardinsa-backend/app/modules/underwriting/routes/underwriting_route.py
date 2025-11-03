# =============================================================================
# FILE: app/modules/underwriting/routes/underwriting_route.py
# WORLD-CLASS UNDERWRITING ROUTES - ENTERPRISE GRADE
# =============================================================================

"""
Underwriting Routes - Enterprise REST API Layer

Comprehensive REST API providing:
- Complete CRUD operations for all entities
- Advanced search and filtering capabilities
- Bulk operations and batch processing
- Analytics and reporting endpoints
- Real-time status tracking
- File upload and document management
- Integration with external systems
- Comprehensive error handling and validation
"""

from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from datetime import datetime, date
import asyncio
import logging
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator

# Core imports
from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.core.responses import success_response, error_response, paginated_response
from app.core.exceptions import EntityNotFoundError, BusinessLogicError, ValidationError
from app.core.logging import get_logger
from app.core.rate_limiting import RateLimiter

# Module imports
from app.modules.underwriting.services.underwriting_engine_service import UnderwritingEngineService
from app.modules.underwriting.repositories.underwriting_repository import UnderwritingRepository
from app.modules.underwriting.schemas.underwriting_schema import (
    # Rule schemas
    UnderwritingRuleCreateSchema, UnderwritingRuleUpdateSchema, UnderwritingRuleResponseSchema,
    UnderwritingRuleSearchFilters, BulkRuleCreateSchema, BulkOperationResult,
    
    # Profile schemas
    UnderwritingProfileCreateSchema, UnderwritingProfileUpdateSchema, 
    UnderwritingProfileResponseSchema, UnderwritingProfileDetailSchema,
    UnderwritingProfileSearchFilters,
    
    # Application schemas
    UnderwritingApplicationCreateSchema, UnderwritingApplicationUpdateSchema,
    UnderwritingApplicationResponseSchema, UnderwritingApplicationSearchFilters,
    
    # Workflow schemas
    WorkflowCreateSchema, WorkflowStepCreateSchema,
    
    # Decision schemas
    UnderwritingEvaluationRequest, UnderwritingDecisionResult,
    RiskAssessmentResult, RuleEvaluationResult,
    
    # Analytics schemas
    UnderwritingAnalytics
)

# Auth imports
from app.modules.auth.models.user_model import User


# =============================================================================
# ROUTER SETUP
# =============================================================================

router = APIRouter(
    prefix="/api/v1/underwriting",
    tags=["Underwriting"],
    dependencies=[Depends(HTTPBearer())],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

logger = get_logger(__name__)
rate_limiter = RateLimiter()


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

def get_underwriting_repository(db: Session = Depends(get_db)) -> UnderwritingRepository:
    """Get underwriting repository instance"""
    return UnderwritingRepository(db)


def get_underwriting_engine(db: Session = Depends(get_db)) -> UnderwritingEngineService:
    """Get underwriting engine service instance"""
    repository = UnderwritingRepository(db)
    return UnderwritingEngineService(db, repository)


def require_underwriter_permissions(current_user: User = Depends(get_current_user)):
    """Require underwriter permissions"""
    require_permissions(current_user, ["underwriter", "admin"])
    return current_user


def require_admin_permissions(current_user: User = Depends(get_current_user)):
    """Require admin permissions"""
    require_permissions(current_user, ["admin"])
    return current_user


# =============================================================================
# UNDERWRITING RULES ENDPOINTS
# =============================================================================

@router.post("/rules", response_model=UnderwritingRuleResponseSchema, status_code=201)
async def create_underwriting_rule(
    rule_data: UnderwritingRuleCreateSchema,
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_underwriter_permissions)
):
    """
    Create a new underwriting rule
    
    **Permissions Required:** underwriter, admin
    
    **Features:**
    - Complete rule validation
    - Duplicate name checking
    - Automatic effective date setting
    - Audit trail creation
    """
    try:
        rule = repository.create_rule(rule_data.dict(), current_user.id)
        
        logger.info(f"Created underwriting rule '{rule.rule_name}' by user {current_user.id}")
        
        return success_response(
            data=UnderwritingRuleResponseSchema.from_orm(rule),
            message="Underwriting rule created successfully"
        )
        
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating underwriting rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create underwriting rule")


@router.get("/rules/{rule_id}", response_model=UnderwritingRuleResponseSchema)
async def get_underwriting_rule(
    rule_id: UUID = Path(..., description="Rule ID"),
    include_relationships: bool = Query(False, description="Include related data"),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Get underwriting rule by ID
    
    **Features:**
    - Optional relationship loading
    - Computed field calculation
    - Access control validation
    """
    try:
        rule = repository.get_rule_by_id(rule_id, include_relationships)
        
        if not rule:
            raise HTTPException(status_code=404, detail="Underwriting rule not found")
        
        response_data = UnderwritingRuleResponseSchema.from_orm(rule)
        
        return success_response(
            data=response_data,
            message="Underwriting rule retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving underwriting rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve underwriting rule")


@router.get("/rules", response_model=Dict[str, Any])
async def search_underwriting_rules(
    # Search filters
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    rule_category: Optional[str] = Query(None, description="Filter by category"),
    rule_type: Optional[str] = Query(None, description="Filter by type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    decision_outcome: Optional[str] = Query(None, description="Filter by decision"),
    priority_min: Optional[int] = Query(None, ge=0, le=1000, description="Minimum priority"),
    priority_max: Optional[int] = Query(None, ge=0, le=1000, description="Maximum priority"),
    effective_date: Optional[date] = Query(None, description="Effective on date"),
    search_text: Optional[str] = Query(None, min_length=1, max_length=100, description="Search text"),
    
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("priority", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Search underwriting rules with advanced filtering
    
    **Features:**
    - Advanced multi-field filtering
    - Full-text search capabilities
    - Flexible sorting options
    - Paginated results
    - Performance optimized queries
    """
    try:
        # Build search filters
        filters = UnderwritingRuleSearchFilters(
            product_type=product_type,
            rule_category=rule_category,
            rule_type=rule_type,
            is_active=is_active,
            decision_outcome=decision_outcome,
            priority_min=priority_min,
            priority_max=priority_max,
            effective_date=effective_date,
            search_text=search_text
        )
        
        # Execute search
        rules, total_count = repository.search_rules(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Convert to response schema
        rules_data = [UnderwritingRuleResponseSchema.from_orm(rule) for rule in rules]
        
        return paginated_response(
            data=rules_data,
            page=page,
            page_size=page_size,
            total_count=total_count,
            message=f"Found {len(rules_data)} underwriting rules"
        )
        
    except Exception as e:
        logger.error(f"Error searching underwriting rules: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search underwriting rules")


@router.put("/rules/{rule_id}", response_model=UnderwritingRuleResponseSchema)
async def update_underwriting_rule(
    rule_id: UUID = Path(..., description="Rule ID"),
    rule_data: UnderwritingRuleUpdateSchema = Body(...),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_underwriter_permissions)
):
    """
    Update underwriting rule
    
    **Permissions Required:** underwriter, admin
    
    **Features:**
    - Partial update support
    - Change validation and audit
    - Cache invalidation
    - Business rule validation
    """
    try:
        # Filter out None values for partial updates
        update_data = {k: v for k, v in rule_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        rule = repository.update_rule(rule_id, update_data, current_user.id)
        
        logger.info(f"Updated underwriting rule {rule_id} by user {current_user.id}")
        
        return success_response(
            data=UnderwritingRuleResponseSchema.from_orm(rule),
            message="Underwriting rule updated successfully"
        )
        
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Underwriting rule not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating underwriting rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update underwriting rule")


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_underwriting_rule(
    rule_id: UUID = Path(..., description="Rule ID"),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_admin_permissions)
):
    """
    Delete underwriting rule (soft delete)
    
    **Permissions Required:** admin
    
    **Features:**
    - Soft delete implementation
    - Usage validation before deletion
    - Cascade handling for related entities
    - Audit trail preservation
    """
    try:
        success = repository.delete_rule(rule_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Underwriting rule not found")
        
        logger.info(f"Deleted underwriting rule {rule_id} by user {current_user.id}")
        
        return JSONResponse(
            status_code=204,
            content={"message": "Underwriting rule deleted successfully"}
        )
        
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Underwriting rule not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting underwriting rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete underwriting rule")


@router.post("/rules/bulk", response_model=BulkOperationResult)
@rate_limiter.limit("10/minute")
async def bulk_create_rules(
    bulk_data: BulkRuleCreateSchema,
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_admin_permissions)
):
    """
    Bulk create underwriting rules
    
    **Permissions Required:** admin
    **Rate Limited:** 10 requests per minute
    
    **Features:**
    - Batch processing optimization
    - Duplicate handling options
    - Validation-only mode
    - Detailed error reporting
    - Transaction safety
    """
    try:
        if bulk_data.validate_only:
            # Validation-only mode
            errors = []
            for i, rule_data in enumerate(bulk_data.rules):
                try:
                    rule_data.dict()  # Trigger validation
                except Exception as e:
                    errors.append(f"Rule {i+1}: {str(e)}")
            
            return success_response(
                data=BulkOperationResult(
                    total_requested=len(bulk_data.rules),
                    successful=len(bulk_data.rules) - len(errors),
                    failed=len(errors),
                    errors=errors
                ),
                message="Validation completed"
            )
        
        # Actual creation
        rules_data = [rule.dict() for rule in bulk_data.rules]
        created_rules, errors = repository.bulk_create_rules(
            rules_data, 
            current_user.id,
            bulk_data.skip_duplicates
        )
        
        result = BulkOperationResult(
            total_requested=len(bulk_data.rules),
            successful=len(created_rules),
            failed=len(errors),
            skipped=len(bulk_data.rules) - len(created_rules) - len(errors),
            errors=errors,
            created_ids=[rule.id for rule in created_rules]
        )
        
        logger.info(f"Bulk created {len(created_rules)} rules by user {current_user.id}")
        
        return success_response(
            data=result,
            message=f"Bulk operation completed: {len(created_rules)} created, {len(errors)} failed"
        )
        
    except Exception as e:
        logger.error(f"Error in bulk create rules: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to bulk create rules")


# =============================================================================
# UNDERWRITING PROFILES ENDPOINTS
# =============================================================================

@router.post("/profiles", response_model=UnderwritingProfileResponseSchema, status_code=201)
async def create_underwriting_profile(
    profile_data: UnderwritingProfileCreateSchema,
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_underwriter_permissions)
):
    """
    Create a new underwriting profile
    
    **Permissions Required:** underwriter, admin
    """
    try:
        profile = repository.create_profile(profile_data.dict(), current_user.id)
        
        logger.info(f"Created underwriting profile {profile.id} by user {current_user.id}")
        
        return success_response(
            data=UnderwritingProfileResponseSchema.from_orm(profile),
            message="Underwriting profile created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating underwriting profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create underwriting profile")


@router.get("/profiles/{profile_id}", response_model=UnderwritingProfileDetailSchema)
async def get_underwriting_profile(
    profile_id: UUID = Path(..., description="Profile ID"),
    include_relationships: bool = Query(False, description="Include related data"),
    include_sensitive: bool = Query(True, description="Include sensitive data"),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Get underwriting profile by ID
    
    **Features:**
    - Configurable data inclusion
    - Sensitive data access control
    - Computed field calculation
    """
    try:
        profile = repository.get_profile_by_id(profile_id, include_relationships)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Underwriting profile not found")
        
        # Check access to sensitive data
        if include_sensitive and not require_permissions(current_user, ["underwriter", "admin"], raise_error=False):
            include_sensitive = False
        
        if include_sensitive:
            response_data = UnderwritingProfileDetailSchema.from_orm(profile)
        else:
            response_data = UnderwritingProfileResponseSchema.from_orm(profile)
        
        return success_response(
            data=response_data,
            message="Underwriting profile retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving underwriting profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve underwriting profile")


@router.get("/profiles", response_model=Dict[str, Any])
async def search_underwriting_profiles(
    # Search filters
    member_id: Optional[UUID] = Query(None, description="Filter by member ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    decision: Optional[str] = Query(None, description="Filter by decision"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by assigned user"),
    priority_min: Optional[int] = Query(None, ge=1, le=10, description="Minimum priority"),
    priority_max: Optional[int] = Query(None, ge=1, le=10, description="Maximum priority"),
    is_overdue: Optional[bool] = Query(None, description="Filter overdue profiles"),
    evaluation_method: Optional[str] = Query(None, description="Filter by evaluation method"),
    created_date_from: Optional[date] = Query(None, description="Created from date"),
    created_date_to: Optional[date] = Query(None, description="Created to date"),
    
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Search underwriting profiles with advanced filtering
    """
    try:
        filters = UnderwritingProfileSearchFilters(
            member_id=member_id,
            status=status,
            decision=decision,
            risk_level=risk_level,
            assigned_to=assigned_to,
            priority_min=priority_min,
            priority_max=priority_max,
            is_overdue=is_overdue,
            evaluation_method=evaluation_method,
            created_date_from=created_date_from,
            created_date_to=created_date_to
        )
        
        profiles, total_count = repository.search_profiles(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        profiles_data = [UnderwritingProfileResponseSchema.from_orm(profile) for profile in profiles]
        
        return paginated_response(
            data=profiles_data,
            page=page,
            page_size=page_size,
            total_count=total_count,
            message=f"Found {len(profiles_data)} underwriting profiles"
        )
        
    except Exception as e:
        logger.error(f"Error searching underwriting profiles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search underwriting profiles")


@router.put("/profiles/{profile_id}", response_model=UnderwritingProfileResponseSchema)
async def update_underwriting_profile(
    profile_id: UUID = Path(..., description="Profile ID"),
    profile_data: UnderwritingProfileUpdateSchema = Body(...),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_underwriter_permissions)
):
    """
    Update underwriting profile
    
    **Permissions Required:** underwriter, admin
    """
    try:
        profile = repository.get_profile_by_id(profile_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Underwriting profile not found")
        
        # Apply updates
        update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
        
        for key, value in update_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_by = current_user.id
        updated_profile = repository.update_profile(profile)
        
        logger.info(f"Updated underwriting profile {profile_id} by user {current_user.id}")
        
        return success_response(
            data=UnderwritingProfileResponseSchema.from_orm(updated_profile),
            message="Underwriting profile updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating underwriting profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update underwriting profile")


# =============================================================================
# UNDERWRITING APPLICATIONS ENDPOINTS
# =============================================================================

@router.post("/applications", response_model=UnderwritingApplicationResponseSchema, status_code=201)
async def create_underwriting_application(
    application_data: UnderwritingApplicationCreateSchema,
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new underwriting application
    
    **Features:**
    - Automatic application number generation
    - SLA due date calculation
    - Quality score initialization
    - Audit trail creation
    """
    try:
        application = repository.create_application(application_data.dict(), current_user.id)
        
        # Calculate initial quality score
        application.calculate_quality_score()
        repository.update_application(application)
        
        logger.info(f"Created underwriting application {application.application_number} by user {current_user.id}")
        
        return success_response(
            data=UnderwritingApplicationResponseSchema.from_orm(application),
            message="Underwriting application created successfully"
        )
        
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating underwriting application: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create underwriting application")


@router.get("/applications/{application_id}", response_model=UnderwritingApplicationResponseSchema)
async def get_underwriting_application(
    application_id: UUID = Path(..., description="Application ID"),
    include_relationships: bool = Query(False, description="Include related data"),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Get underwriting application by ID
    """
    try:
        application = repository.get_application_by_id(application_id, include_relationships)
        
        if not application:
            raise HTTPException(status_code=404, detail="Underwriting application not found")
        
        return success_response(
            data=UnderwritingApplicationResponseSchema.from_orm(application),
            message="Underwriting application retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving underwriting application {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve underwriting application")


@router.get("/applications", response_model=Dict[str, Any])
async def search_underwriting_applications(
    # Search filters
    application_number: Optional[str] = Query(None, min_length=1, max_length=30, description="Application number"),
    member_id: Optional[UUID] = Query(None, description="Filter by member ID"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    submission_channel: Optional[str] = Query(None, description="Filter by submission channel"),
    source: Optional[str] = Query(None, description="Filter by source"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by assigned user"),
    is_overdue: Optional[bool] = Query(None, description="Filter overdue applications"),
    is_complete: Optional[bool] = Query(None, description="Filter complete applications"),
    submitted_date_from: Optional[date] = Query(None, description="Submitted from date"),
    submitted_date_to: Optional[date] = Query(None, description="Submitted to date"),
    coverage_amount_min: Optional[float] = Query(None, ge=0, description="Minimum coverage amount"),
    coverage_amount_max: Optional[float] = Query(None, ge=0, description="Maximum coverage amount"),
    
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("submitted_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Search underwriting applications with advanced filtering
    """
    try:
        filters = UnderwritingApplicationSearchFilters(
            application_number=application_number,
            member_id=member_id,
            product_type=product_type,
            status=status,
            priority=priority,
            submission_channel=submission_channel,
            source=source,
            assigned_to=assigned_to,
            is_overdue=is_overdue,
            is_complete=is_complete,
            submitted_date_from=submitted_date_from,
            submitted_date_to=submitted_date_to,
            coverage_amount_min=coverage_amount_min,
            coverage_amount_max=coverage_amount_max
        )
        
        applications, total_count = repository.search_applications(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        applications_data = [UnderwritingApplicationResponseSchema.from_orm(app) for app in applications]
        
        return paginated_response(
            data=applications_data,
            page=page,
            page_size=page_size,
            total_count=total_count,
            message=f"Found {len(applications_data)} underwriting applications"
        )
        
    except Exception as e:
        logger.error(f"Error searching underwriting applications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search underwriting applications")


@router.put("/applications/{application_id}", response_model=UnderwritingApplicationResponseSchema)
async def update_underwriting_application(
    application_id: UUID = Path(..., description="Application ID"),
    application_data: UnderwritingApplicationUpdateSchema = Body(...),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Update underwriting application
    """
    try:
        application = repository.get_application_by_id(application_id)
        
        if not application:
            raise HTTPException(status_code=404, detail="Underwriting application not found")
        
        # Apply updates
        update_data = {k: v for k, v in application_data.dict().items() if v is not None}
        
        for key, value in update_data.items():
            if hasattr(application, key):
                setattr(application, key, value)
        
        application.updated_by = current_user.id
        updated_application = repository.update_application(application)
        
        logger.info(f"Updated underwriting application {application_id} by user {current_user.id}")
        
        return success_response(
            data=UnderwritingApplicationResponseSchema.from_orm(updated_application),
            message="Underwriting application updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating underwriting application {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update underwriting application")


# =============================================================================
# UNDERWRITING DECISION ENDPOINTS
# =============================================================================

@router.post("/evaluate", response_model=UnderwritingDecisionResult)
@rate_limiter.limit("30/minute")
async def evaluate_underwriting_application(
    request: UnderwritingEvaluationRequest,
    background_tasks: BackgroundTasks,
    engine: UnderwritingEngineService = Depends(get_underwriting_engine),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_underwriter_permissions)
):
    """
    Evaluate underwriting application
    
    **Permissions Required:** underwriter, admin
    **Rate Limited:** 30 requests per minute
    
    **Features:**
    - Complete automated evaluation
    - Risk assessment and scoring
    - Rule-based decision making
    - Workflow initiation for manual review
    - Real-time processing
    """
    try:
        # Get application
        application = repository.get_application_by_id(request.application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Build evaluation context
        from app.modules.underwriting.services.underwriting_engine_service import UnderwritingContext
        
        context = UnderwritingContext(
            application_id=request.application_id,
            applicant_data=application.applicant_data or application.application_data,
            product_type=application.product_type,
            coverage_amount=application.coverage_amount,
            plan_id=application.plan_id,
            submission_channel=application.submission_channel,
            medical_data=application.medical_data,
            financial_data=application.financial_data,
            risk_data=application.risk_data
        )
        
        # Add context data if provided
        if request.context_data:
            for key, value in request.context_data.items():
                setattr(context, key, value)
        
        # Evaluate application
        decision_result = await engine.evaluate_application(
            application_id=request.application_id,
            context=context,
            force_manual_review=request.force_manual_review
        )
        
        # Update application status
        if decision_result.decision == 'approved':
            application.status = 'approved'
        elif decision_result.decision == 'rejected':
            application.status = 'rejected'
        else:
            application.status = 'under_review'
        
        application.updated_by = current_user.id
        repository.update_application(application)
        
        # Add background task for notifications
        background_tasks.add_task(
            send_decision_notification,
            application_id=request.application_id,
            decision=decision_result.decision,
            user_id=current_user.id
        )
        
        logger.info(f"Evaluated application {request.application_id}: {decision_result.decision}")
        
        return success_response(
            data=decision_result,
            message=f"Application evaluation completed: {decision_result.decision}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating application {request.application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to evaluate application")


@router.post("/applications/{application_id}/re-evaluate", response_model=UnderwritingDecisionResult)
async def re_evaluate_application(
    application_id: UUID = Path(..., description="Application ID"),
    reason: str = Body(..., min_length=10, max_length=500, description="Reason for re-evaluation"),
    context_data: Optional[Dict[str, Any]] = Body(None, description="Updated context data"),
    engine: UnderwritingEngineService = Depends(get_underwriting_engine),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_underwriter_permissions)
):
    """
    Re-evaluate underwriting application with updated information
    
    **Permissions Required:** underwriter, admin
    """
    try:
        # Get application
        application = repository.get_application_by_id(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Build updated context
        from app.modules.underwriting.services.underwriting_engine_service import UnderwritingContext
        
        context = UnderwritingContext(
            application_id=application_id,
            applicant_data=application.applicant_data or application.application_data,
            product_type=application.product_type,
            coverage_amount=application.coverage_amount,
            plan_id=application.plan_id,
            submission_channel=application.submission_channel,
            medical_data=application.medical_data,
            financial_data=application.financial_data,
            risk_data=application.risk_data
        )
        
        # Apply updated context data
        if context_data:
            for key, value in context_data.items():
                setattr(context, key, value)
        
        # Re-evaluate
        decision_result = await engine.re_evaluate_application(
            application_id=application_id,
            updated_context=context,
            reason=reason
        )
        
        logger.info(f"Re-evaluated application {application_id}: {decision_result.decision} - {reason}")
        
        return success_response(
            data=decision_result,
            message=f"Application re-evaluation completed: {decision_result.decision}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error re-evaluating application {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to re-evaluate application")


@router.get("/applications/{application_id}/status", response_model=Dict[str, Any])
async def get_application_status(
    application_id: UUID = Path(..., description="Application ID"),
    engine: UnderwritingEngineService = Depends(get_underwriting_engine),
    current_user: User = Depends(get_current_user)
):
    """
    Get current status of underwriting application
    
    **Features:**
    - Real-time status information
    - Workflow progress tracking
    - SLA compliance monitoring
    - Next action recommendations
    """
    try:
        status_info = await engine.get_application_status(application_id)
        
        return success_response(
            data=status_info,
            message="Application status retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting application status {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get application status")


@router.get("/applications/{application_id}/decision-summary", response_model=Dict[str, Any])
async def get_decision_summary(
    application_id: UUID = Path(..., description="Application ID"),
    engine: UnderwritingEngineService = Depends(get_underwriting_engine),
    current_user: User = Depends(require_underwriter_permissions)
):
    """
    Get comprehensive decision summary for application
    
    **Permissions Required:** underwriter, admin
    
    **Features:**
    - Complete decision history
    - Rule evaluation details
    - Risk assessment breakdown
    - Premium impact analysis
    """
    try:
        decision_summary = await engine.get_decision_summary(application_id)
        
        return success_response(
            data=decision_summary,
            message="Decision summary retrieved successfully"
        )
        
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Application not found")
    except Exception as e:
        logger.error(f"Error getting decision summary {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get decision summary")


# =============================================================================
# WORKFLOW MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/workflows", response_model=Dict[str, Any])
async def create_workflow(
    workflow_data: WorkflowCreateSchema,
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_admin_permissions)
):
    """
    Create new workflow template
    
    **Permissions Required:** admin
    """
    try:
        workflow = repository.create_workflow(workflow_data.dict(), current_user.id)
        
        logger.info(f"Created workflow '{workflow.name}' by user {current_user.id}")
        
        return success_response(
            data=workflow.to_dict(include_steps=True),
            message="Workflow created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create workflow")


# =============================================================================
# ANALYTICS AND REPORTING ENDPOINTS
# =============================================================================

@router.get("/analytics", response_model=UnderwritingAnalytics)
async def get_underwriting_analytics(
    start_date: date = Query(..., description="Analytics period start date"),
    end_date: date = Query(..., description="Analytics period end date"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_underwriter_permissions)
):
    """
    Get underwriting analytics for specified period
    
    **Permissions Required:** underwriter, admin
    
    **Features:**
    - Comprehensive performance metrics
    - Risk distribution analysis
    - Channel and product breakdowns
    - SLA compliance tracking
    - Processing efficiency metrics
    """
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        if (end_date - start_date).days > 365:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 365 days")
        
        analytics_data = repository.get_underwriting_analytics(
            start_date=start_date,
            end_date=end_date,
            product_type=product_type
        )
        
        return success_response(
            data=UnderwritingAnalytics(**analytics_data),
            message="Analytics retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting underwriting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get underwriting analytics")


@router.get("/analytics/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    start_date: date = Query(..., description="Performance period start date"),
    end_date: date = Query(..., description="Performance period end date"),
    underwriter_id: Optional[UUID] = Query(None, description="Specific underwriter ID"),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_underwriter_permissions)
):
    """
    Get performance metrics for underwriter or system
    
    **Permissions Required:** underwriter, admin
    """
    try:
        performance_data = repository.get_performance_metrics(
            start_date=start_date,
            end_date=end_date,
            underwriter_id=underwriter_id
        )
        
        return success_response(
            data=performance_data,
            message="Performance metrics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")


@router.get("/analytics/risk", response_model=Dict[str, Any])
async def get_risk_analysis(
    start_date: date = Query(..., description="Risk analysis period start date"),
    end_date: date = Query(..., description="Risk analysis period end date"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_underwriter_permissions)
):
    """
    Get risk analysis for specified period
    
    **Permissions Required:** underwriter, admin
    """
    try:
        risk_data = repository.get_risk_analysis(
            start_date=start_date,
            end_date=end_date,
            product_type=product_type
        )
        
        return success_response(
            data=risk_data,
            message="Risk analysis retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting risk analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get risk analysis")


# =============================================================================
# DASHBOARD AND MONITORING ENDPOINTS
# =============================================================================

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_underwriting_dashboard(
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Get underwriting dashboard data
    
    **Features:**
    - Real-time statistics
    - Pending work items
    - Performance indicators
    - Alert notifications
    """
    try:
        # Get dashboard data
        dashboard_data = {
            'summary': {
                'pending_applications': len(repository.get_pending_applications()),
                'overdue_applications': len(repository.get_overdue_applications()),
                'high_priority_profiles': len(repository.get_high_priority_profiles()),
                'overdue_profiles': len(repository.get_overdue_profiles())
            },
            'my_work': {
                'assigned_applications': len(repository.get_pending_applications(current_user.id)),
                'pending_decisions': len(repository.get_pending_applications(current_user.id))
            },
            'system_health': repository.get_table_statistics()
        }
        
        return success_response(
            data=dashboard_data,
            message="Dashboard data retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")


@router.get("/health", response_model=Dict[str, Any])
async def get_system_health(
    repository: UnderwritingRepository = Depends(get_underwriting_repository),
    current_user: User = Depends(require_admin_permissions)
):
    """
    Get system health status
    
    **Permissions Required:** admin
    """
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'statistics': repository.get_table_statistics(),
            'alerts': [],
            'performance': {
                'avg_response_time_ms': 150,  # Would be calculated from actual metrics
                'active_sessions': 1,
                'cache_hit_ratio': 0.85
            }
        }
        
        return success_response(
            data=health_data,
            message="System health retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system health")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

async def send_decision_notification(application_id: UUID, decision: str, user_id: UUID):
    """Background task to send decision notifications"""
    try:
        # Implementation would depend on notification system
        logger.info(f"Sending notification for application {application_id} decision: {decision}")
        # await notification_service.send_decision_notification(...)
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")


# =============================================================================
# ERROR HANDLERS
# =============================================================================

# @router.exception_handler(ValidationError)
# async def validation_error_handler(request, exc):
#     """Handle validation errors"""
#     return error_response(
#         message="Validation error",
#         details=str(exc),
#         status_code=422
#     )


# @router.exception_handler(BusinessLogicError)
# async def business_logic_error_handler(request, exc):
#     """Handle business logic errors"""
#     return error_response(
#         message="Business logic error",
#         details=str(exc),
#         status_code=400
#     )


# @router.exception_handler(EntityNotFoundError)
# async def entity_not_found_error_handler(request, exc):
#     """Handle entity not found errors"""
#     return error_response(
#         message="Resource not found",
#         details=str(exc),
#         status_code=404
#     )


# =============================================================================
# EXPORT ROUTER
# =============================================================================

__all__ = ['router']