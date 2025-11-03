# app/modules/pricing/calculations/services/premium_calculation_engine.py
"""
Premium Calculation Engine - Core Orchestrator for Step 7
Integrates Steps 4-6 into unified premium calculation pipeline
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from dataclasses import dataclass, field
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import ValidationError, BusinessLogicError
from app.core.logging import get_logger

# Import Step 6 components
from app.modules.pricing.profiles.services.rule_orchestration_engine import (
    RuleOrchestrationEngine,
    OrchestrationConfig,
    ExecutionStrategy,
    CacheStrategy,
    ConflictResolutionStrategy
)
from app.modules.pricing.profiles.services.age_bracket_integration import (
    AdvancedAgeBracketIntegration,
    DemographicProfile,
    Gender
)

logger = get_logger(__name__)


class CalculationStatus(str, Enum):
    """Status of premium calculation."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    OVERRIDDEN = "OVERRIDDEN"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ComponentType(str, Enum):
    """Types of pricing components."""
    PROFILE_BASE = "PROFILE_BASE"
    DEMOGRAPHIC = "DEMOGRAPHIC"
    DEDUCTIBLE = "DEDUCTIBLE"
    COPAY = "COPAY"
    DISCOUNT = "DISCOUNT"
    COMMISSION = "COMMISSION"
    RULE_ENGINE = "RULE_ENGINE"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"


@dataclass
class CalculationComponent:
    """Represents a component in the calculation pipeline."""
    component_type: ComponentType
    component_name: str
    input_value: Decimal
    output_value: Decimal
    factor: Decimal
    execution_order: int
    execution_time: float
    details: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class CalculationRequest:
    """Request for premium calculation."""
    base_premium: Decimal
    profile_id: Optional[UUID] = None
    demographic_profile: Optional[DemographicProfile] = None
    benefit_type: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    rule_ids: List[UUID] = field(default_factory=list)
    pricing_components: Dict[str, Any] = field(default_factory=dict)
    calculation_options: Dict[str, Any] = field(default_factory=dict)
    requested_by: Optional[UUID] = None
    request_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CalculationResult:
    """Result of premium calculation."""
    calculation_id: UUID
    request: CalculationRequest
    status: CalculationStatus
    base_premium: Decimal
    final_premium: Decimal
    total_factor: Decimal
    components: List[CalculationComponent]
    total_execution_time: float
    calculation_timestamp: datetime
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OverrideRequest:
    """Request for manual calculation override."""
    calculation_id: UUID
    override_premium: Decimal
    justification: str
    override_type: str  # MANUAL, EMERGENCY, COMPETITIVE
    requested_by: UUID
    approval_required: bool = True
    expiry_date: Optional[datetime] = None


class PremiumCalculationEngine:
    """
    Core premium calculation engine that orchestrates all pricing components.
    Integrates Steps 4-6 into a unified calculation pipeline.
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        
        # Initialize integrated components
        self.rule_orchestrator = RuleOrchestrationEngine(self.db)
        self.age_bracket_system = AdvancedAgeBracketIntegration(self.db)
        
        # Configuration
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Performance tracking
        self.performance_stats = {
            "total_calculations": 0,
            "successful_calculations": 0,
            "failed_calculations": 0,
            "average_execution_time": 0.0,
            "component_performance": {}
        }
    
    # ============================================================================
    # MAIN CALCULATION METHODS
    # ============================================================================
    
    async def calculate_premium(
        self,
        request: CalculationRequest
    ) -> CalculationResult:
        """
        Main premium calculation method that orchestrates all components.
        
        This is the primary entry point for all premium calculations.
        Coordinates Steps 4-6 integration and produces comprehensive results.
        """
        calculation_id = uuid4()
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting premium calculation {calculation_id}")
            
            # Initialize result
            result = CalculationResult(
                calculation_id=calculation_id,
                request=request,
                status=CalculationStatus.IN_PROGRESS,
                base_premium=request.base_premium,
                final_premium=request.base_premium,
                total_factor=Decimal('1.0'),
                components=[],
                total_execution_time=0.0,
                calculation_timestamp=start_time
            )
            
            # Add audit trail entry
            self._add_audit_entry(result, "CALCULATION_STARTED", {
                "base_premium": float(request.base_premium),
                "profile_id": str(request.profile_id) if request.profile_id else None
            })
            
            # Step 1: Profile Base Configuration
            await self._apply_profile_base(result)
            
            # Step 2: Demographic Pricing (if profile provided)
            if request.demographic_profile:
                await self._apply_demographic_pricing(result)
            
            # Step 3: Pricing Components (Step 5 integration)
            await self._apply_pricing_components(result)
            
            # Step 4: Advanced Rules Engine (Step 6 integration)
            if request.rule_ids:
                await self._apply_rules_engine(result)
            
            # Step 5: Finalize calculation
            await self._finalize_calculation(result)
            
            # Update performance stats
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result.total_execution_time = execution_time
            result.status = CalculationStatus.COMPLETED
            
            self._update_performance_stats(result)
            
            logger.info(f"Premium calculation {calculation_id} completed in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Premium calculation {calculation_id} failed: {str(e)}")
            
            # Create error result
            result.status = CalculationStatus.FAILED
            result.total_execution_time = execution_time
            result.errors.append(str(e))
            
            self._add_audit_entry(result, "CALCULATION_FAILED", {
                "error": str(e),
                "execution_time": execution_time
            })
            
            return result
    
    async def calculate_with_profile(
        self,
        profile_id: UUID,
        base_premium: Decimal,
        input_data: Dict[str, Any],
        demographic_profile: Optional[DemographicProfile] = None,
        requested_by: Optional[UUID] = None
    ) -> CalculationResult:
        """
        Calculate premium using a specific pricing profile.
        
        This method loads profile configuration and executes associated rules.
        """
        try:
            # Load profile configuration (would implement database query)
            profile_config = await self._load_profile_configuration(profile_id)
            
            # Get rule IDs associated with profile
            rule_ids = await self._get_profile_rule_ids(profile_id)
            
            # Create calculation request
            request = CalculationRequest(
                base_premium=base_premium,
                profile_id=profile_id,
                demographic_profile=demographic_profile,
                input_data=input_data,
                rule_ids=rule_ids,
                pricing_components=profile_config.get("components", {}),
                calculation_options=profile_config.get("options", {}),
                requested_by=requested_by
            )
            
            return await self.calculate_premium(request)
            
        except Exception as e:
            logger.error(f"Error calculating with profile {profile_id}: {str(e)}")
            raise BusinessLogicError(f"Profile calculation failed: {str(e)}")
    
    async def batch_calculate(
        self,
        requests: List[CalculationRequest]
    ) -> List[CalculationResult]:
        """
        Process multiple calculation requests in parallel.
        
        Optimizes performance for bulk calculations while maintaining accuracy.
        """
        try:
            logger.info(f"Starting batch calculation for {len(requests)} requests")
            
            # Process requests in parallel
            tasks = [self.calculate_premium(request) for request in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in results
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error result for failed calculation
                    error_result = CalculationResult(
                        calculation_id=uuid4(),
                        request=requests[i],
                        status=CalculationStatus.FAILED,
                        base_premium=requests[i].base_premium,
                        final_premium=requests[i].base_premium,
                        total_factor=Decimal('1.0'),
                        components=[],
                        total_execution_time=0.0,
                        calculation_timestamp=datetime.utcnow(),
                        errors=[str(result)]
                    )
                    final_results.append(error_result)
                else:
                    final_results.append(result)
            
            successful = len([r for r in final_results if r.status == CalculationStatus.COMPLETED])
            logger.info(f"Batch calculation completed: {successful}/{len(requests)} successful")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Batch calculation failed: {str(e)}")
            raise
    
    # ============================================================================
    # COMPONENT APPLICATION METHODS
    # ============================================================================
    
    async def _apply_profile_base(self, result: CalculationResult):
        """Apply base profile configuration (Step 4 integration)."""
        start_time = datetime.utcnow()
        
        try:
            if not result.request.profile_id:
                # No profile specified, use base premium as-is
                component = CalculationComponent(
                    component_type=ComponentType.PROFILE_BASE,
                    component_name="Base Premium",
                    input_value=result.final_premium,
                    output_value=result.final_premium,
                    factor=Decimal('1.0'),
                    execution_order=1,
                    execution_time=0.001,
                    details={"source": "direct_input"}
                )
                result.components.append(component)
                return
            
            # Load profile configuration
            profile_config = await self._load_profile_configuration(result.request.profile_id)
            
            # Apply profile base factors
            base_factor = Decimal(str(profile_config.get("base_factor", 1.0)))
            currency_factor = Decimal(str(profile_config.get("currency_factor", 1.0)))
            risk_factor = Decimal(str(profile_config.get("risk_factor", 1.0)))
            
            # Calculate adjusted premium
            adjusted_premium = result.final_premium * base_factor * currency_factor * risk_factor
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            component = CalculationComponent(
                component_type=ComponentType.PROFILE_BASE,
                component_name=f"Profile: {profile_config.get('name', 'Unknown')}",
                input_value=result.final_premium,
                output_value=adjusted_premium,
                factor=base_factor * currency_factor * risk_factor,
                execution_order=1,
                execution_time=execution_time,
                details={
                    "profile_id": str(result.request.profile_id),
                    "base_factor": float(base_factor),
                    "currency_factor": float(currency_factor),
                    "risk_factor": float(risk_factor)
                }
            )
            
            result.components.append(component)
            result.final_premium = adjusted_premium
            
            self._add_audit_entry(result, "PROFILE_BASE_APPLIED", component.details)
            
        except Exception as e:
            logger.error(f"Error applying profile base: {str(e)}")
            result.errors.append(f"Profile base error: {str(e)}")
    
    async def _apply_demographic_pricing(self, result: CalculationResult):
        """Apply demographic pricing (Age bracket integration from Step 6)."""
        start_time = datetime.utcnow()
        
        try:
            demographic_calculation = self.age_bracket_system.calculate_demographic_pricing(
                base_premium=result.final_premium,
                demographic_profile=result.request.demographic_profile,
                benefit_type=result.request.benefit_type,
                include_actuarial=True
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            component = CalculationComponent(
                component_type=ComponentType.DEMOGRAPHIC,
                component_name="Demographic Pricing",
                input_value=result.final_premium,
                output_value=demographic_calculation["final_premium"],
                factor=demographic_calculation["total_factor"],
                execution_order=2,
                execution_time=execution_time,
                details={
                    "demographic_profile": {
                        "age": result.request.demographic_profile.age,
                        "gender": result.request.demographic_profile.gender.value,
                        "territory": result.request.demographic_profile.territory
                    },
                    "adjustments": demographic_calculation.get("adjustments", []),
                    "age_bracket": demographic_calculation.get("age_bracket", {})
                }
            )
            
            result.components.append(component)
            result.final_premium = demographic_calculation["final_premium"]
            
            self._add_audit_entry(result, "DEMOGRAPHIC_APPLIED", component.details)
            
        except Exception as e:
            logger.error(f"Error applying demographic pricing: {str(e)}")
            result.errors.append(f"Demographic pricing error: {str(e)}")
    
    async def _apply_pricing_components(self, result: CalculationResult):
        """Apply pricing components (Step 5 integration)."""
        start_time = datetime.utcnow()
        execution_order = len(result.components) + 1
        
        try:
            components_config = result.request.pricing_components
            
            # Apply deductibles
            if "deductibles" in components_config:
                await self._apply_deductibles(result, components_config["deductibles"], execution_order)
                execution_order += 1
            
            # Apply copays
            if "copays" in components_config:
                await self._apply_copays(result, components_config["copays"], execution_order)
                execution_order += 1
            
            # Apply discounts
            if "discounts" in components_config:
                await self._apply_discounts(result, components_config["discounts"], execution_order)
                execution_order += 1
            
            # Apply commission
            if "commission" in components_config:
                await self._apply_commission(result, components_config["commission"], execution_order)
            
            total_time = (datetime.utcnow() - start_time).total_seconds()
            self._add_audit_entry(result, "PRICING_COMPONENTS_APPLIED", {
                "execution_time": total_time,
                "components_count": len([c for c in result.components if c.execution_order >= len(result.components) - 4])
            })
            
        except Exception as e:
            logger.error(f"Error applying pricing components: {str(e)}")
            result.errors.append(f"Pricing components error: {str(e)}")
    
    async def _apply_rules_engine(self, result: CalculationResult):
        """Apply advanced rules engine (Step 6 integration)."""
        start_time = datetime.utcnow()
        
        try:
            # Prepare input data for rules engine
            rules_input_data = {
                **result.request.input_data,
                "premium": float(result.final_premium),
                "base_premium": float(result.request.base_premium)
            }
            
            # Add demographic data if available
            if result.request.demographic_profile:
                rules_input_data.update({
                    "age": result.request.demographic_profile.age,
                    "gender": result.request.demographic_profile.gender.value,
                    "territory": result.request.demographic_profile.territory,
                    "occupation": result.request.demographic_profile.occupation,
                    "risk_factors": result.request.demographic_profile.risk_factors
                })
            
            # Execute rules via orchestration engine
            orchestration_result = await self.rule_orchestrator.orchestrate_pricing_rules(
                rule_ids=result.request.rule_ids,
                input_data=rules_input_data,
                demographic_profile=result.request.demographic_profile,
                base_premium=result.final_premium,
                benefit_type=result.request.benefit_type
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            component = CalculationComponent(
                component_type=ComponentType.RULE_ENGINE,
                component_name="Advanced Rules Engine",
                input_value=result.final_premium,
                output_value=orchestration_result.final_premium,
                factor=orchestration_result.total_adjustment_factor,
                execution_order=len(result.components) + 1,
                execution_time=execution_time,
                details={
                    "rules_evaluated": orchestration_result.rules_evaluated,
                    "rules_applied": orchestration_result.rules_applied,
                    "conflicts_detected": orchestration_result.conflicts_detected,
                    "rule_results": [
                        {
                            "rule_id": str(r.rule_id),
                            "rule_name": r.rule_name,
                            "condition_met": r.condition_met,
                            "impact_applied": r.impact_applied,
                            "result_value": float(r.result_value) if r.result_value else None
                        }
                        for r in orchestration_result.rule_results[:10]  # Limit for performance
                    ]
                }
            )
            
            result.components.append(component)
            result.final_premium = orchestration_result.final_premium
            
            self._add_audit_entry(result, "RULES_ENGINE_APPLIED", component.details)
            
        except Exception as e:
            logger.error(f"Error applying rules engine: {str(e)}")
            result.errors.append(f"Rules engine error: {str(e)}")
    
    async def _finalize_calculation(self, result: CalculationResult):
        """Finalize calculation with validation and rounding."""
        try:
            # Calculate total factor
            if result.request.base_premium > 0:
                result.total_factor = result.final_premium / result.request.base_premium
            else:
                result.total_factor = Decimal('1.0')
            
            # Round final premium to 2 decimal places
            result.final_premium = result.final_premium.quantize(
                Decimal('0.01'), 
                rounding=ROUND_HALF_UP
            )
            
            # Validate result
            if result.final_premium < 0:
                result.warnings.append("Final premium is negative - review calculation logic")
            
            if result.total_factor > 10:
                result.warnings.append("Total adjustment factor is very high - review for accuracy")
            
            # Add final audit entry
            self._add_audit_entry(result, "CALCULATION_FINALIZED", {
                "final_premium": float(result.final_premium),
                "total_factor": float(result.total_factor),
                "components_count": len(result.components)
            })
            
        except Exception as e:
            logger.error(f"Error finalizing calculation: {str(e)}")
            result.errors.append(f"Finalization error: {str(e)}")
    
    # ============================================================================
    # COMPONENT-SPECIFIC METHODS
    # ============================================================================
    
    async def _apply_deductibles(
        self, 
        result: CalculationResult, 
        deductibles_config: Dict[str, Any], 
        execution_order: int
    ):
        """Apply deductible components."""
        deductible_factor = Decimal(str(deductibles_config.get("factor", 1.0)))
        adjusted_premium = result.final_premium * deductible_factor
        
        component = CalculationComponent(
            component_type=ComponentType.DEDUCTIBLE,
            component_name="Deductibles",
            input_value=result.final_premium,
            output_value=adjusted_premium,
            factor=deductible_factor,
            execution_order=execution_order,
            execution_time=0.001,
            details=deductibles_config
        )
        
        result.components.append(component)
        result.final_premium = adjusted_premium
    
    async def _apply_copays(
        self, 
        result: CalculationResult, 
        copays_config: Dict[str, Any], 
        execution_order: int
    ):
        """Apply copay components."""
        copay_factor = Decimal(str(copays_config.get("factor", 1.0)))
        adjusted_premium = result.final_premium * copay_factor
        
        component = CalculationComponent(
            component_type=ComponentType.COPAY,
            component_name="Copays",
            input_value=result.final_premium,
            output_value=adjusted_premium,
            factor=copay_factor,
            execution_order=execution_order,
            execution_time=0.001,
            details=copays_config
        )
        
        result.components.append(component)
        result.final_premium = adjusted_premium
    
    async def _apply_discounts(
        self, 
        result: CalculationResult, 
        discounts_config: Dict[str, Any], 
        execution_order: int
    ):
        """Apply discount components."""
        discount_factor = Decimal(str(discounts_config.get("factor", 1.0)))
        adjusted_premium = result.final_premium * discount_factor
        
        component = CalculationComponent(
            component_type=ComponentType.DISCOUNT,
            component_name="Discounts",
            input_value=result.final_premium,
            output_value=adjusted_premium,
            factor=discount_factor,
            execution_order=execution_order,
            execution_time=0.001,
            details=discounts_config
        )
        
        result.components.append(component)
        result.final_premium = adjusted_premium
    
    async def _apply_commission(
        self, 
        result: CalculationResult, 
        commission_config: Dict[str, Any], 
        execution_order: int
    ):
        """Apply commission components."""
        commission_factor = Decimal(str(commission_config.get("factor", 1.0)))
        adjusted_premium = result.final_premium * commission_factor
        
        component = CalculationComponent(
            component_type=ComponentType.COMMISSION,
            component_name="Commission",
            input_value=result.final_premium,
            output_value=adjusted_premium,
            factor=commission_factor,
            execution_order=execution_order,
            execution_time=0.001,
            details=commission_config
        )
        
        result.components.append(component)
        result.final_premium = adjusted_premium
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _add_audit_entry(
        self, 
        result: CalculationResult, 
        action: str, 
        details: Dict[str, Any]
    ):
        """Add entry to calculation audit trail."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "details": details,
            "calculation_id": str(result.calculation_id)
        }
        result.audit_trail.append(audit_entry)
    
    def _update_performance_stats(self, result: CalculationResult):
        """Update performance statistics."""
        self.performance_stats["total_calculations"] += 1
        
        if result.status == CalculationStatus.COMPLETED:
            self.performance_stats["successful_calculations"] += 1
        else:
            self.performance_stats["failed_calculations"] += 1
        
        # Update average execution time
        total = self.performance_stats["total_calculations"]
        current_avg = self.performance_stats["average_execution_time"]
        new_avg = ((current_avg * (total - 1)) + result.total_execution_time) / total
        self.performance_stats["average_execution_time"] = new_avg
    
    async def _load_profile_configuration(self, profile_id: UUID) -> Dict[str, Any]:
        """Load pricing profile configuration from database."""
        # Placeholder implementation - would query database
        return {
            "name": f"Profile {profile_id}",
            "base_factor": 1.0,
            "currency_factor": 1.0,
            "risk_factor": 1.0,
            "components": {
                "deductibles": {"factor": 0.95},
                "copays": {"factor": 1.02},
                "discounts": {"factor": 0.90}
            },
            "options": {}
        }
    
    async def _get_profile_rule_ids(self, profile_id: UUID) -> List[UUID]:
        """Get rule IDs associated with a pricing profile."""
        # Placeholder implementation - would query database
        return [
            UUID('12345678-1234-5678-9abc-123456789012'),
            UUID('87654321-4321-8765-cba9-210987654321')
        ]
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        return self.performance_stats.copy()
    
    def clear_performance_statistics(self):
        """Clear performance statistics."""
        self.performance_stats = {
            "total_calculations": 0,
            "successful_calculations": 0,
            "failed_calculations": 0,
            "average_execution_time": 0.0,
            "component_performance": {}
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_usage():
    """Demonstrate the premium calculation engine."""
    engine = PremiumCalculationEngine()
    
    # Create demographic profile
    demographic_profile = DemographicProfile(
        age=35,
        gender=Gender.FEMALE,
        territory="URBAN",
        occupation="TEACHER",
        risk_factors=["FAMILY_HISTORY_CARDIAC"]
    )
    
    # Create calculation request
    request = CalculationRequest(
        base_premium=Decimal('1000.00'),
        demographic_profile=demographic_profile,
        benefit_type="MEDICAL",
        input_data={
            "coverage_type": "PREMIUM",
            "policy_term": 12,
            "payment_frequency": "MONTHLY"
        },
        rule_ids=[
            UUID('12345678-1234-5678-9abc-123456789012'),
            UUID('87654321-4321-8765-cba9-210987654321')
        ],
        pricing_components={
            "deductibles": {"factor": 0.95},
            "copays": {"factor": 1.02},
            "discounts": {"factor": 0.90}
        }
    )
    
    # Execute calculation
    result = await engine.calculate_premium(request)
    
    # Display results
    print(f"Calculation ID: {result.calculation_id}")
    print(f"Status: {result.status.value}")
    print(f"Base Premium: ${result.base_premium}")
    print(f"Final Premium: ${result.final_premium}")
    print(f"Total Factor: {result.total_factor}")
    print(f"Execution Time: {result.total_execution_time:.3f}s")
    print(f"Components Applied: {len(result.components)}")
    
    for component in result.components:
        print(f"  - {component.component_name}: {component.factor} "
              f"(${component.input_value} → ${component.output_value})")


if __name__ == "__main__":
    asyncio.run(example_usage())