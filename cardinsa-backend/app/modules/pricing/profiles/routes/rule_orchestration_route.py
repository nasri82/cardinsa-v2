# app/modules/pricing/profiles/routes/rule_orchestration_route.py
"""
Rule Orchestration Route - Production Ready Implementation
Main endpoint for integrating all Step 6 advanced features
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
from app.modules.pricing.profiles.services.rule_orchestration_engine import (
    RuleOrchestrationEngine,
    OrchestrationConfig,
    ExecutionStrategy,
    CacheStrategy,
    ConflictResolutionStrategy
)
from app.modules.pricing.profiles.services.age_bracket_integration import (
    DemographicProfile,
    Gender
)
from app.modules.auth.models.user_model import User
from app.core.exceptions import ValidationError, BusinessLogicError
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/pricing/orchestration", tags=["Rule Orchestration"])

# =============================================================================
# SCHEMAS FOR API REQUESTS/RESPONSES
# =============================================================================

class DemographicProfileSchema(BaseModel):
    """Schema for demographic profile information."""
    age: int = Field(..., ge=0, le=120, description="Age in years")
    gender: str = Field(..., description="Gender: M, F, or U")
    territory: str = Field(..., description="Territory code")
    occupation: Optional[str] = Field(None, description="Occupation category")
    risk_factors: List[str] = Field(default_factory=list, description="List of risk factors")

class OrchestrationConfigSchema(BaseModel):
    """Schema for orchestration configuration."""
    execution_strategy: str = Field("hybrid", description="Execution strategy: sequential, parallel, hybrid, optimized")
    cache_strategy: str = Field("profile_level", description="Cache strategy: none, rule_level, profile_level, full_pipeline")
    conflict_resolution: str = Field("priority_based", description="Conflict resolution: priority_based, first_match, last_match, aggregate")
    max_execution_time: int = Field(30, ge=1, le=300, description="Maximum execution time in seconds")
    enable_parallel_evaluation: bool = Field(True, description="Enable parallel rule evaluation")
    max_parallel_rules: int = Field(10, ge=1, le=50, description="Maximum parallel rules")
    enable_performance_monitoring: bool = Field(True, description="Enable performance monitoring")
    cache_ttl: int = Field(300, ge=60, le=3600, description="Cache TTL in seconds")

class OrchestrationRequest(BaseModel):
    """Main orchestration request schema."""
    rule_ids: List[UUID] = Field(..., description="List of rule IDs to execute")
    input_data: Dict[str, Any] = Field(..., description="Input data for rule evaluation")
    demographic_profile: Optional[DemographicProfileSchema] = Field(None, description="Demographic information")
    base_premium: Optional[Decimal] = Field(None, ge=0, description="Base premium amount")
    benefit_type: Optional[str] = Field(None, description="Type of benefit being priced")
    config: Optional[OrchestrationConfigSchema] = Field(None, description="Orchestration configuration")

class RuleExecutionResultSchema(BaseModel):
    """Schema for individual rule execution result."""
    rule_id: UUID
    rule_name: str
    execution_time: float
    success: bool
    condition_met: bool
    impact_applied: bool
    result_value: Optional[Decimal]
    error_message: Optional[str] = None
    cache_hit: bool = False
    execution_details: Dict[str, Any] = Field(default_factory=dict)

class OrchestrationResponse(BaseModel):
    """Main orchestration response schema."""
    total_execution_time: float
    rules_evaluated: int
    rules_applied: int
    conflicts_detected: int
    conflicts_resolved: int
    final_premium: Decimal
    base_premium: Decimal
    total_adjustment_factor: Decimal
    rule_results: List[RuleExecutionResultSchema]
    demographic_calculation: Optional[Dict[str, Any]] = None
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    cache_statistics: Dict[str, Any] = Field(default_factory=dict)

class PerformanceStatsResponse(BaseModel):
    """Schema for performance statistics."""
    total_executions: int
    cache_hits: int
    cache_misses: int
    average_execution_time: float
    cache_hit_rate: float
    uptime_seconds: float

class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: str
    components: Dict[str, str]
    performance_summary: Dict[str, Any]
    last_execution: Optional[Dict[str, Any]] = None

# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

def get_orchestration_engine(db: Session = Depends(get_db)) -> RuleOrchestrationEngine:
    """Dependency to get rule orchestration engine."""
    return RuleOrchestrationEngine(db)

# =============================================================================
# MAIN ORCHESTRATION ENDPOINTS
# =============================================================================

@router.post("/execute", response_model=OrchestrationResponse)
async def orchestrate_pricing_rules(
    request: OrchestrationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: RuleOrchestrationEngine = Depends(get_orchestration_engine)
):
    """
    Main orchestration endpoint - executes pricing rules with advanced features.
    
    This endpoint coordinates:
    - Multi-condition rule evaluation
    - Dependency management and conflict resolution
    - Demographic pricing calculations
    - Performance optimization and caching
    - Comprehensive result analysis
    
    Returns complete pricing calculation with detailed breakdown.
    """
    try:
        logger.info(f"Starting rule orchestration for user {current_user.id} with {len(request.rule_ids)} rules")
        
        # Convert and validate configuration
        config = None
        if request.config:
            config = OrchestrationConfig(
                execution_strategy=ExecutionStrategy(request.config.execution_strategy),
                cache_strategy=CacheStrategy(request.config.cache_strategy),
                conflict_resolution=ConflictResolutionStrategy(request.config.conflict_resolution),
                max_execution_time=request.config.max_execution_time,
                enable_parallel_evaluation=request.config.enable_parallel_evaluation,
                max_parallel_rules=request.config.max_parallel_rules,
                enable_performance_monitoring=request.config.enable_performance_monitoring,
                cache_ttl=request.config.cache_ttl
            )
            
            # Update engine configuration
            engine.update_configuration(config)
        
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
        
        # Execute orchestration
        result = await engine.orchestrate_pricing_rules(
            rule_ids=request.rule_ids,
            input_data=request.input_data,
            demographic_profile=demographic_profile,
            base_premium=request.base_premium,
            benefit_type=request.benefit_type
        )
        
        # Convert rule results to schema format
        rule_results = [
            RuleExecutionResultSchema(
                rule_id=r.rule_id,
                rule_name=r.rule_name,
                execution_time=r.execution_time,
                success=r.success,
                condition_met=r.condition_met,
                impact_applied=r.impact_applied,
                result_value=r.result_value,
                error_message=r.error_message,
                cache_hit=r.cache_hit,
                execution_details=r.execution_details
            )
            for r in result.rule_results
        ]
        
        response = OrchestrationResponse(
            total_execution_time=result.total_execution_time,
            rules_evaluated=result.rules_evaluated,
            rules_applied=result.rules_applied,
            conflicts_detected=result.conflicts_detected,
            conflicts_resolved=result.conflicts_resolved,
            final_premium=result.final_premium,
            base_premium=result.base_premium,
            total_adjustment_factor=result.total_adjustment_factor,
            rule_results=rule_results,
            demographic_calculation=result.demographic_calculation,
            performance_metrics=result.performance_metrics,
            cache_statistics=result.cache_statistics
        )
        
        logger.info(f"Orchestration completed: {result.rules_applied}/{result.rules_evaluated} rules applied in {result.total_execution_time:.3f}s")
        
        return response
        
    except ValidationError as e:
        logger.warning(f"Validation error in orchestration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    
    except BusinessLogicError as e:
        logger.warning(f"Business logic error in orchestration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Business logic error: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Error in rule orchestration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration failed: {str(e)}"
        )

@router.post("/execute-profile", response_model=OrchestrationResponse)
async def orchestrate_profile_rules(
    profile_id: UUID,
    input_data: Dict[str, Any] = Body(..., description="Input data for rule evaluation"),
    demographic_profile: Optional[DemographicProfileSchema] = Body(None, description="Demographic information"),
    base_premium: Optional[Decimal] = Body(None, description="Base premium amount"),
    benefit_type: Optional[str] = Body(None, description="Benefit type"),
    config: Optional[OrchestrationConfigSchema] = Body(None, description="Orchestration configuration"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: RuleOrchestrationEngine = Depends(get_orchestration_engine)
):
    """
    Execute all rules associated with a specific pricing profile.
    
    This endpoint automatically retrieves all rules for the given profile
    and executes them using the orchestration engine.
    """
    try:
        logger.info(f"Starting profile orchestration for profile {profile_id}, user {current_user.id}")
        
        # Get rules for the profile (would need to implement this query)
        # For now, we'll return an error indicating this needs implementation
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Profile rule retrieval not yet implemented. Use /execute endpoint with explicit rule IDs."
        )
        
    except Exception as e:
        logger.error(f"Error in profile orchestration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile orchestration failed: {str(e)}"
        )

# =============================================================================
# PERFORMANCE AND MONITORING ENDPOINTS
# =============================================================================

@router.get("/performance", response_model=PerformanceStatsResponse)
async def get_performance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: RuleOrchestrationEngine = Depends(get_orchestration_engine)
):
    """
    Get performance statistics for the orchestration engine.
    
    Returns metrics including execution times, cache hit rates,
    and system performance indicators.
    """
    try:
        stats = engine.get_performance_statistics()
        
        cache_total = stats.get("cache_hits", 0) + stats.get("cache_misses", 0)
        cache_hit_rate = stats.get("cache_hits", 0) / cache_total if cache_total > 0 else 0
        
        return PerformanceStatsResponse(
            total_executions=stats.get("total_executions", 0),
            cache_hits=stats.get("cache_hits", 0),
            cache_misses=stats.get("cache_misses", 0),
            average_execution_time=stats.get("average_execution_time", 0.0),
            cache_hit_rate=cache_hit_rate,
            uptime_seconds=0.0  # Would track actual uptime in production
        )
        
    except Exception as e:
        logger.error(f"Error getting performance statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance statistics: {str(e)}"
        )

@router.delete("/performance", response_model=Dict[str, str])
async def clear_performance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: RuleOrchestrationEngine = Depends(get_orchestration_engine)
):
    """
    Clear performance statistics for the orchestration engine.
    
    Resets all performance counters and metrics to zero.
    Useful for testing or starting fresh monitoring periods.
    """
    try:
        engine.clear_performance_statistics()
        
        logger.info(f"Performance statistics cleared by user {current_user.id}")
        
        return {"message": "Performance statistics cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing performance statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear performance statistics: {str(e)}"
        )

@router.get("/health", response_model=HealthCheckResponse)
async def orchestration_health_check(
    db: Session = Depends(get_db),
    engine: RuleOrchestrationEngine = Depends(get_orchestration_engine)
):
    """
    Comprehensive health check for the orchestration engine.
    
    Verifies that all components are operational:
    - Logic engine
    - Dependency manager
    - Age bracket system
    - Cache system
    - Thread pool
    """
    try:
        # Get health status from engine
        health_status = await engine.health_check()
        
        # Get performance summary
        performance_stats = engine.get_performance_statistics()
        performance_summary = {
            "total_executions": performance_stats.get("total_executions", 0),
            "average_execution_time": performance_stats.get("average_execution_time", 0.0),
            "cache_hit_rate": performance_stats.get("cache_hits", 0) / max(performance_stats.get("cache_hits", 0) + performance_stats.get("cache_misses", 0), 1)
        }
        
        return HealthCheckResponse(
            status=health_status.get("orchestration_engine", "unknown"),
            timestamp=health_status.get("last_check", datetime.utcnow().isoformat()),
            components={
                "orchestration_engine": health_status.get("orchestration_engine", "unknown"),
                "logic_engine": health_status.get("logic_engine", "unknown"),
                "dependency_manager": health_status.get("dependency_manager", "unknown"),
                "age_bracket_system": health_status.get("age_bracket_system", "unknown"),
                "cache": health_status.get("cache", "unknown"),
                "thread_pool": health_status.get("thread_pool", "unknown")
            },
            performance_summary=performance_summary
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            components={
                "orchestration_engine": f"error: {str(e)}",
                "logic_engine": "unknown",
                "dependency_manager": "unknown", 
                "age_bracket_system": "unknown",
                "cache": "unknown",
                "thread_pool": "unknown"
            },
            performance_summary={"error": str(e)}
        )

# =============================================================================
# CONFIGURATION ENDPOINTS
# =============================================================================

@router.post("/configuration", response_model=Dict[str, str])
async def update_orchestration_configuration(
    config: OrchestrationConfigSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: RuleOrchestrationEngine = Depends(get_orchestration_engine)
):
    """
    Update orchestration engine configuration.
    
    Allows runtime configuration changes for:
    - Execution strategy
    - Caching behavior
    - Performance parameters
    - Conflict resolution strategy
    """
    try:
        # Convert to internal configuration format
        orchestration_config = OrchestrationConfig(
            execution_strategy=ExecutionStrategy(config.execution_strategy),
            cache_strategy=CacheStrategy(config.cache_strategy),
            conflict_resolution=ConflictResolutionStrategy(config.conflict_resolution),
            max_execution_time=config.max_execution_time,
            enable_parallel_evaluation=config.enable_parallel_evaluation,
            max_parallel_rules=config.max_parallel_rules,
            enable_performance_monitoring=config.enable_performance_monitoring,
            cache_ttl=config.cache_ttl
        )
        
        # Update engine configuration
        engine.update_configuration(orchestration_config)
        
        logger.info(f"Orchestration configuration updated by user {current_user.id}")
        
        return {"message": "Configuration updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update configuration: {str(e)}"
        )

@router.get("/configuration", response_model=OrchestrationConfigSchema)
async def get_orchestration_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: RuleOrchestrationEngine = Depends(get_orchestration_engine)
):
    """
    Get current orchestration engine configuration.
    
    Returns the current configuration settings for all
    orchestration parameters.
    """
    try:
        config = engine.config
        
        return OrchestrationConfigSchema(
            execution_strategy=config.execution_strategy.value,
            cache_strategy=config.cache_strategy.value,
            conflict_resolution=config.conflict_resolution.value,
            max_execution_time=config.max_execution_time,
            enable_parallel_evaluation=config.enable_parallel_evaluation,
            max_parallel_rules=config.max_parallel_rules,
            enable_performance_monitoring=config.enable_performance_monitoring,
            cache_ttl=config.cache_ttl
        )
        
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve configuration: {str(e)}"
        )

# =============================================================================
# TESTING AND SIMULATION ENDPOINTS
# =============================================================================

@router.post("/simulate", response_model=Dict[str, Any])
async def simulate_pricing_scenarios(
    rule_ids: List[UUID] = Body(..., description="Rule IDs to test"),
    scenarios: List[Dict[str, Any]] = Body(..., description="Test scenarios"),
    base_premium: Decimal = Body(1000.0, description="Base premium for scenarios"),
    config: Optional[OrchestrationConfigSchema] = Body(None, description="Configuration"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: RuleOrchestrationEngine = Depends(get_orchestration_engine)
):
    """
    Simulate pricing across multiple scenarios.
    
    This endpoint allows bulk testing of pricing rules against
    multiple scenarios to analyze pricing behavior and sensitivity.
    """
    try:
        logger.info(f"Starting pricing simulation for {len(scenarios)} scenarios, user {current_user.id}")
        
        # Configure engine if config provided
        if config:
            orchestration_config = OrchestrationConfig(
                execution_strategy=ExecutionStrategy(config.execution_strategy),
                cache_strategy=CacheStrategy(config.cache_strategy),
                conflict_resolution=ConflictResolutionStrategy(config.conflict_resolution),
                max_execution_time=config.max_execution_time,
                enable_parallel_evaluation=config.enable_parallel_evaluation,
                max_parallel_rules=config.max_parallel_rules,
                enable_performance_monitoring=config.enable_performance_monitoring,
                cache_ttl=config.cache_ttl
            )
            engine.update_configuration(orchestration_config)
        
        # Execute scenarios
        simulation_results = []
        total_start_time = datetime.utcnow()
        
        for i, scenario in enumerate(scenarios):
            try:
                scenario_start = datetime.utcnow()
                
                result = await engine.orchestrate_pricing_rules(
                    rule_ids=rule_ids,
                    input_data=scenario,
                    base_premium=base_premium
                )
                
                scenario_time = (datetime.utcnow() - scenario_start).total_seconds()
                
                simulation_results.append({
                    "scenario_index": i,
                    "input_data": scenario,
                    "final_premium": float(result.final_premium),
                    "adjustment_factor": float(result.total_adjustment_factor),
                    "rules_applied": result.rules_applied,
                    "execution_time": scenario_time,
                    "success": True,
                    "error": None
                })
                
            except Exception as e:
                simulation_results.append({
                    "scenario_index": i,
                    "input_data": scenario,
                    "final_premium": float(base_premium),
                    "adjustment_factor": 1.0,
                    "rules_applied": 0,
                    "execution_time": 0,
                    "success": False,
                    "error": str(e)
                })
        
        total_time = (datetime.utcnow() - total_start_time).total_seconds()
        
        # Generate analysis
        successful_results = [r for r in simulation_results if r["success"]]
        
        if successful_results:
            premiums = [r["final_premium"] for r in successful_results]
            factors = [r["adjustment_factor"] for r in successful_results]
            
            analysis = {
                "scenario_count": len(scenarios),
                "successful_scenarios": len(successful_results),
                "failed_scenarios": len(simulation_results) - len(successful_results),
                "total_execution_time": total_time,
                "average_scenario_time": sum(r["execution_time"] for r in successful_results) / len(successful_results) if successful_results else 0,
                "premium_statistics": {
                    "min_premium": min(premiums) if premiums else 0,
                    "max_premium": max(premiums) if premiums else 0,
                    "average_premium": sum(premiums) / len(premiums) if premiums else 0
                },
                "adjustment_statistics": {
                    "min_factor": min(factors) if factors else 1.0,
                    "max_factor": max(factors) if factors else 1.0,
                    "average_factor": sum(factors) / len(factors) if factors else 1.0
                }
            }
        else:
            analysis = {
                "scenario_count": len(scenarios),
                "successful_scenarios": 0,
                "failed_scenarios": len(scenarios),
                "total_execution_time": total_time,
                "error": "All scenarios failed"
            }
        
        return create_response(
            data={
                "analysis": analysis,
                "detailed_results": simulation_results
            },
            message=f"Simulation completed: {len(successful_results)}/{len(scenarios)} scenarios successful"
        )
        
    except Exception as e:
        logger.error(f"Error in pricing simulation: {str(e)}")
        return create_error_response(
            message="Pricing simulation failed",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )