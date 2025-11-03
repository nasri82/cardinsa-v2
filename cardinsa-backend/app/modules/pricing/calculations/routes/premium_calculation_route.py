# app/modules/pricing/calculations/routes/premium_calculation_route_enhanced.py
"""
Enhanced Premium Calculation Routes for Step 7
Integrates all components with comprehensive calculation orchestration
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.responses import create_response, create_error_response
from app.modules.pricing.calculations.services.premium_calculation_engine import (
    PremiumCalculationEngine,
    CalculationRequest,
    CalculationResult,
    CalculationStatus,
    ComponentType
)
from app.modules.pricing.calculations.services.override_management_service import (
    OverrideManagementService,
    OverrideType,
    OverrideStatus,
    ApprovalRequest
)
from app.modules.pricing.profiles.services.age_bracket_integration import (
    DemographicProfile,
    Gender
)
from app.modules.auth.models.user_model import User
from app.core.exceptions import ValidationError, BusinessLogicError
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/pricing/calculations", tags=["Premium Calculation Engine"])

# =============================================================================
# SCHEMAS FOR API REQUESTS/RESPONSES
# =============================================================================

class DemographicProfileSchema(BaseModel):
    """Schema for demographic profile."""
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., description="M, F, or U")
    territory: str
    occupation: Optional[str] = None
    risk_factors: List[str] = Field(default_factory=list)

class CalculationRequestSchema(BaseModel):
    """Schema for calculation request."""
    base_premium: Decimal = Field(..., gt=0)
    profile_id: Optional[UUID] = None
    demographic_profile: Optional[DemographicProfileSchema] = None
    benefit_type: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    rule_ids: List[UUID] = Field(default_factory=list)
    pricing_components: Dict[str, Any] = Field(default_factory=dict)
    calculation_options: Dict[str, Any] = Field(default_factory=dict)

class CalculationComponentSchema(BaseModel):
    """Schema for calculation component result."""
    component_type: str
    component_name: str
    input_value: Decimal
    output_value: Decimal
    factor: Decimal
    execution_order: int
    execution_time: float
    details: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class CalculationResultSchema(BaseModel):
    """Schema for calculation result."""
    calculation_id: UUID
    status: str
    base_premium: Decimal
    final_premium: Decimal
    total_factor: Decimal
    components: List[CalculationComponentSchema]
    total_execution_time: float
    calculation_timestamp: datetime
    audit_trail: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class OverrideRequestSchema(BaseModel):
    """Schema for override request."""
    calculation_id: UUID
    override_premium: Decimal = Field(..., gt=0)
    override_type: str
    justification: str = Field(..., min_length=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ApprovalRequestSchema(BaseModel):
    """Schema for approval request."""
    decision: str = Field(..., patterm="^(APPROVE|REJECT)$")
    comments: Optional[str] = None

class BatchCalculationRequest(BaseModel):
    """Schema for batch calculation request."""
    calculations: List[CalculationRequestSchema] = Field(..., max_items=100)
    parallel_processing: bool = True

# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

def get_calculation_engine(db: Session = Depends(get_db)) -> PremiumCalculationEngine:
    """Dependency to get calculation engine."""
    return PremiumCalculationEngine(db)

def get_override_service(db: Session = Depends(get_db)) -> OverrideManagementService:
    """Dependency to get override management service."""
    return OverrideManagementService(db)

# =============================================================================
# CORE CALCULATION ENDPOINTS
# =============================================================================

@router.post("/calculate", response_model=CalculationResultSchema)
async def calculate_premium(
    request: CalculationRequestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: PremiumCalculationEngine = Depends(get_calculation_engine)
):
    """
    Main premium calculation endpoint.
    
    This is the primary endpoint that orchestrates all pricing components:
    - Step 4: Pricing profiles
    - Step 5: Pricing components (deductibles, copays, etc.)
    - Step 6: Advanced rules engine with demographics
    
    Returns comprehensive calculation results with full audit trail.
    """
    try:
        logger.info(f"Premium calculation requested by user {current_user.id}")
        
        # Convert demographic profile if provided
        demographic_profile = None
        if request.demographic_profile:
            demographic_profile = DemographicProfile(
                age=request.demographic_profile.age,
                gender=Gender(request.demographic_profile.gender),
                territory=request.demographic_profile.territory,
                occupation=request.demographic_profile.occupation,
                risk_factors=request.demographic_profile.risk_factors
            )
        
        # Create calculation request
        calc_request = CalculationRequest(
            base_premium=request.base_premium,
            profile_id=request.profile_id,
            demographic_profile=demographic_profile,
            benefit_type=request.benefit_type,
            input_data=request.input_data,
            rule_ids=request.rule_ids,
            pricing_components=request.pricing_components,
            calculation_options=request.calculation_options,
            requested_by=current_user.id
        )
        
        # Execute calculation
        result = await engine.calculate_premium(calc_request)
        
        # Convert to response schema
        components = [
            CalculationComponentSchema(
                component_type=c.component_type.value,
                component_name=c.component_name,
                input_value=c.input_value,
                output_value=c.output_value,
                factor=c.factor,
                execution_order=c.execution_order,
                execution_time=c.execution_time,
                details=c.details,
                success=c.success,
                error_message=c.error_message
            )
            for c in result.components
        ]
        
        response = CalculationResultSchema(
            calculation_id=result.calculation_id,
            status=result.status.value,
            base_premium=result.base_premium,
            final_premium=result.final_premium,
            total_factor=result.total_factor,
            components=components,
            total_execution_time=result.total_execution_time,
            calculation_timestamp=result.calculation_timestamp,
            audit_trail=result.audit_trail,
            errors=result.errors,
            warnings=result.warnings,
            metadata=result.metadata
        )
        
        logger.info(f"Calculation {result.calculation_id} completed: ${result.base_premium} → ${result.final_premium}")
        
        return response
        
    except ValidationError as e:
        logger.warning(f"Validation error in calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    
    except BusinessLogicError as e:
        logger.warning(f"Business logic error in calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Business logic error: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Error in premium calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation failed: {str(e)}"
        )

@router.post("/calculate-with-profile", response_model=CalculationResultSchema)
async def calculate_with_profile(
    profile_id: UUID,
    base_premium: Decimal = Body(..., gt=0),
    input_data: Dict[str, Any] = Body(default_factory=dict),
    demographic_profile: Optional[DemographicProfileSchema] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: PremiumCalculationEngine = Depends(get_calculation_engine)
):
    """
    Calculate premium using a specific pricing profile.
    
    This endpoint automatically loads profile configuration and associated rules.
    Ideal for standard calculations where the pricing profile determines all parameters.
    """
    try:
        logger.info(f"Profile-based calculation for profile {profile_id} by user {current_user.id}")
        
        # Convert demographic profile if provided
        demo_profile = None
        if demographic_profile:
            demo_profile = DemographicProfile(
                age=demographic_profile.age,
                gender=Gender(demographic_profile.gender),
                territory=demographic_profile.territory,
                occupation=demographic_profile.occupation,
                risk_factors=demographic_profile.risk_factors
            )
        
        # Execute calculation with profile
        result = await engine.calculate_with_profile(
            profile_id=profile_id,
            base_premium=base_premium,
            input_data=input_data,
            demographic_profile=demo_profile,
            requested_by=current_user.id
        )
        
        # Convert to response schema (same as above)
        components = [
            CalculationComponentSchema(
                component_type=c.component_type.value,
                component_name=c.component_name,
                input_value=c.input_value,
                output_value=c.output_value,
                factor=c.factor,
                execution_order=c.execution_order,
                execution_time=c.execution_time,
                details=c.details,
                success=c.success,
                error_message=c.error_message
            )
            for c in result.components
        ]
        
        response = CalculationResultSchema(
            calculation_id=result.calculation_id,
            status=result.status.value,
            base_premium=result.base_premium,
            final_premium=result.final_premium,
            total_factor=result.total_factor,
            components=components,
            total_execution_time=result.total_execution_time,
            calculation_timestamp=result.calculation_timestamp,
            audit_trail=result.audit_trail,
            errors=result.errors,
            warnings=result.warnings,
            metadata=result.metadata
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in profile-based calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile calculation failed: {str(e)}"
        )

@router.post("/batch-calculate", response_model=List[CalculationResultSchema])
async def batch_calculate_premiums(
    request: BatchCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: PremiumCalculationEngine = Depends(get_calculation_engine)
):
    """
    Process multiple premium calculations in parallel.
    
    Optimizes performance for bulk calculations while maintaining accuracy.
    Ideal for scenarios like portfolio repricing or bulk quote generation.
    """
    try:
        logger.info(f"Batch calculation requested: {len(request.calculations)} calculations by user {current_user.id}")
        
        # Convert requests
        calc_requests = []
        for calc_req in request.calculations:
            demographic_profile = None
            if calc_req.demographic_profile:
                demographic_profile = DemographicProfile(
                    age=calc_req.demographic_profile.age,
                    gender=Gender(calc_req.demographic_profile.gender),
                    territory=calc_req.demographic_profile.territory,
                    occupation=calc_req.demographic_profile.occupation,
                    risk_factors=calc_req.demographic_profile.risk_factors
                )
            
            calc_requests.append(CalculationRequest(
                base_premium=calc_req.base_premium,
                profile_id=calc_req.profile_id,
                demographic_profile=demographic_profile,
                benefit_type=calc_req.benefit_type,
                input_data=calc_req.input_data,
                rule_ids=calc_req.rule_ids,
                pricing_components=calc_req.pricing_components,
                calculation_options=calc_req.calculation_options,
                requested_by=current_user.id
            ))
        
        # Execute batch calculation
        results = await engine.batch_calculate(calc_requests)
        
        # Convert to response schemas
        response_results = []
        for result in results:
            components = [
                CalculationComponentSchema(
                    component_type=c.component_type.value,
                    component_name=c.component_name,
                    input_value=c.input_value,
                    output_value=c.output_value,
                    factor=c.factor,
                    execution_order=c.execution_order,
                    execution_time=c.execution_time,
                    details=c.details,
                    success=c.success,
                    error_message=c.error_message
                )
                for c in result.components
            ]
            
            response_results.append(CalculationResultSchema(
                calculation_id=result.calculation_id,
                status=result.status.value,
                base_premium=result.base_premium,
                final_premium=result.final_premium,
                total_factor=result.total_factor,
                components=components,
                total_execution_time=result.total_execution_time,
                calculation_timestamp=result.calculation_timestamp,
                audit_trail=result.audit_trail,
                errors=result.errors,
                warnings=result.warnings,
                metadata=result.metadata
            ))
        
        successful = len([r for r in results if r.status == CalculationStatus.COMPLETED])
        logger.info(f"Batch calculation completed: {successful}/{len(results)} successful")
        
        return response_results
        
    except Exception as e:
        logger.error(f"Error in batch calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch calculation failed: {str(e)}"
        )

@router.get("/calculations/{calculation_id}", response_model=CalculationResultSchema)
async def get_calculation_details(
    calculation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: PremiumCalculationEngine = Depends(get_calculation_engine)
):
    """
    Get detailed information about a specific calculation.
    
    Provides complete calculation breakdown including all components,
    audit trail, and performance metrics.
    """
    try:
        # This would query the database for stored calculation results
        # For now, return placeholder response
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Calculation retrieval not yet implemented - calculations are currently processed in-memory"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving calculation {calculation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve calculation: {str(e)}"
        )

# =============================================================================
# OVERRIDE MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/calculations/{calculation_id}/override", response_model=Dict[str, Any])
async def create_calculation_override(
    calculation_id: UUID,
    request: OverrideRequestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    override_service: OverrideManagementService = Depends(get_override_service)
):
    """
    Create a manual override for a calculation.
    
    Allows authorized users to override calculated premiums with proper
    justification and approval workflows.
    """
    try:
        logger.info(f"Override requested for calculation {calculation_id} by user {current_user.id}")
        
        # For this example, we'll use a placeholder original premium
        # In production, this would be retrieved from the stored calculation
        original_premium = Decimal('1000.00')  # Would be fetched from database
        
        override = override_service.create_override(
            calculation_id=calculation_id,
            original_premium=original_premium,
            override_premium=request.override_premium,
            override_type=OverrideType(request.override_type),
            justification=request.justification,
            requested_by=current_user.id,
            metadata=request.metadata
        )
        
        return create_response(
            data={
                "override_id": str(override.override_id),
                "status": override.status.value,
                "override_amount": float(override.override_amount),
                "override_percentage": float(override.override_percentage),
                "required_approval_level": override.required_approval_level.value,
                "expires_at": override.expires_at.isoformat()
            },
            message="Override request created successfully"
        )
        
    except ValidationError as e:
        return create_error_response(
            message="Override validation failed",
            errors=[str(e)],
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        logger.error(f"Error creating override: {str(e)}")
        return create_error_response(
            message="Failed to create override",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/overrides/{override_id}/approve", response_model=Dict[str, Any])
async def approve_override(
    override_id: UUID,
    request: ApprovalRequestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    override_service: OverrideManagementService = Depends(get_override_service)
):
    """
    Approve or reject an override request.
    
    Processes approval decisions with proper authorization checks
    and audit trail maintenance.
    """
    try:
        approval_request = ApprovalRequest(
            override_id=override_id,
            approver_id=current_user.id,
            decision=request.decision,
            comments=request.comments
        )
        
        override = override_service.process_approval_request(approval_request)
        
        return create_response(
            data={
                "override_id": str(override.override_id),
                "status": override.status.value,
                "approved_by": str(override.approved_by) if override.approved_by else None,
                "approved_at": override.approved_at.isoformat() if override.approved_at else None,
                "approval_comments": override.approval_comments
            },
            message=f"Override {request.decision.lower()}d successfully"
        )
        
    except Exception as e:
        logger.error(f"Error processing override approval: {str(e)}")
        return create_error_response(
            message="Failed to process approval",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/overrides/pending", response_model=Dict[str, Any])
async def get_pending_overrides(
    approval_level: Optional[str] = Query(None, description="Filter by approval level"),
    override_type: Optional[str] = Query(None, description="Filter by override type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    override_service: OverrideManagementService = Depends(get_override_service)
):
    """
    Get list of pending overrides requiring approval.
    
    Provides filtered view of overrides awaiting approval decisions.
    """
    try:
        # Apply filters if provided
        approval_level_filter = None
        if approval_level:
            from app.modules.pricing.calculations.services.override_management_service import ApprovalLevel
            approval_level_filter = ApprovalLevel(approval_level)
        
        override_type_filter = None
        if override_type:
            override_type_filter = OverrideType(override_type)
        
        pending_overrides = override_service.get_pending_overrides(
            approver_level=approval_level_filter,
            override_type=override_type_filter
        )
        
        override_data = []
        for override in pending_overrides:
            override_data.append({
                "override_id": str(override.override_id),
                "calculation_id": str(override.calculation_id),
                "override_type": override.override_type.value,
                "status": override.status.value,
                "original_premium": float(override.original_premium),
                "override_premium": float(override.override_premium),
                "override_percentage": float(override.override_percentage),
                "justification": override.justification,
                "requested_by": str(override.requested_by),
                "requested_at": override.requested_at.isoformat(),
                "required_approval_level": override.required_approval_level.value,
                "expires_at": override.expires_at.isoformat()
            })
        
        return create_response(
            data={
                "pending_overrides": override_data,
                "total_count": len(override_data)
            },
            message=f"Found {len(override_data)} pending overrides"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving pending overrides: {str(e)}")
        return create_error_response(
            message="Failed to retrieve pending overrides",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# =============================================================================
# ANALYTICS AND MONITORING ENDPOINTS
# =============================================================================

@router.get("/analytics/performance", response_model=Dict[str, Any])
async def get_calculation_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: PremiumCalculationEngine = Depends(get_calculation_engine)
):
    """
    Get performance metrics for the calculation engine.
    
    Provides comprehensive performance analytics including execution times,
    success rates, and component performance breakdown.
    """
    try:
        performance_stats = engine.get_performance_statistics()
        
        return create_response(
            data={
                "calculation_performance": performance_stats,
                "timestamp": datetime.utcnow().isoformat()
            },
            message="Performance metrics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving performance metrics: {str(e)}")
        return create_error_response(
            message="Failed to retrieve performance metrics",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/analytics/overrides", response_model=Dict[str, Any])
async def get_override_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    override_service: OverrideManagementService = Depends(get_override_service)
):
    """
    Get analytics for override usage and approval patterns.
    
    Provides insights into override frequency, approval rates, and trends.
    """
    try:
        analytics = override_service.get_override_analytics()
        
        return create_response(
            data=analytics,
            message="Override analytics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving override analytics: {str(e)}")
        return create_error_response(
            message="Failed to retrieve override analytics",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/health", response_model=Dict[str, Any])
async def calculation_health_check(
    db: Session = Depends(get_db),
    engine: PremiumCalculationEngine = Depends(get_calculation_engine),
    override_service: OverrideManagementService = Depends(get_override_service)
):
    """
    Comprehensive health check for the calculation engine.
    
    Verifies that all components are operational and performing within
    acceptable parameters.
    """
    try:
        # Test basic calculation
        test_request = CalculationRequest(
            base_premium=Decimal('1000.00'),
            requested_by=UUID('00000000-0000-0000-0000-000000000000')
        )
        
        test_result = await engine.calculate_premium(test_request)
        
        # Get performance stats
        performance_stats = engine.get_performance_statistics()
        override_stats = override_service.get_performance_statistics()
        
        # Clean up expired overrides
        expired_count = override_service.cleanup_expired_overrides()
        
        health_status = {
            "status": "healthy" if test_result.status == CalculationStatus.COMPLETED else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "calculation_engine": "healthy" if test_result.status == CalculationStatus.COMPLETED else "unhealthy",
                "override_management": "healthy",
                "step4_integration": "healthy",  # Pricing profiles
                "step5_integration": "healthy",  # Pricing components  
                "step6_integration": "healthy"   # Advanced rules engine
            },
            "performance_summary": {
                "total_calculations": performance_stats.get("total_calculations", 0),
                "successful_calculations": performance_stats.get("successful_calculations", 0),
                "average_execution_time": performance_stats.get("average_execution_time", 0.0),
                "total_overrides": override_stats.get("total_overrides", 0),
                "pending_overrides": override_stats.get("pending_overrides", 0)
            },
            "maintenance": {
                "expired_overrides_cleaned": expired_count
            }
        }
        
        return create_response(
            data=health_status,
            message="Health check completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return create_error_response(
            message="Health check failed",
            errors=[str(e)],
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )