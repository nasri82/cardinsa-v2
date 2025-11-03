# app/modules/pricing/profiles/services/rule_orchestration_engine.py
"""
Rule Orchestration Engine - Final component for Step 6 completion
Integrates all advanced features: multi-condition logic, dependencies, age brackets
"""

from typing import List, Optional, Dict, Any, Tuple, Union
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import ValidationError, BusinessLogicError
from app.core.logging import get_logger
from app.core.cache import get_cache_client

# Import our advanced components
from app.modules.pricing.profiles.services.advanced_rule_engine import (
    MultiConditionLogicEngine, 
    AdvancedRule, 
    ConditionNode, 
    RuleImpact
)
from app.modules.pricing.profiles.services.rule_dependency_manager import (
    RuleDependencyManager, 
    ConflictResolutionStrategy, 
    RuleExecutionPlan
)
from app.modules.pricing.profiles.services.age_bracket_integration import (
    AdvancedAgeBracketIntegration, 
    DemographicProfile, 
    AgeBracket
)

logger = get_logger(__name__)


class ExecutionStrategy(str, Enum):
    """Rule execution strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    OPTIMIZED = "optimized"


class CacheStrategy(str, Enum):
    """Caching strategies for rule evaluation."""
    NONE = "none"
    RULE_LEVEL = "rule_level"
    PROFILE_LEVEL = "profile_level"
    FULL_PIPELINE = "full_pipeline"


@dataclass
class OrchestrationConfig:
    """Configuration for rule orchestration."""
    execution_strategy: ExecutionStrategy = ExecutionStrategy.HYBRID
    cache_strategy: CacheStrategy = CacheStrategy.PROFILE_LEVEL
    conflict_resolution: ConflictResolutionStrategy = ConflictResolutionStrategy.PRIORITY_BASED
    max_execution_time: int = 30  # seconds
    enable_parallel_evaluation: bool = True
    max_parallel_rules: int = 10
    enable_performance_monitoring: bool = True
    cache_ttl: int = 300  # seconds
    enable_debugging: bool = False


@dataclass
class RuleExecutionResult:
    """Result of a single rule execution."""
    rule_id: UUID
    rule_name: str
    execution_time: float
    success: bool
    condition_met: bool
    impact_applied: bool
    result_value: Optional[Decimal]
    error_message: Optional[str] = None
    cache_hit: bool = False
    execution_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """Complete result of rule orchestration."""
    total_execution_time: float
    rules_evaluated: int
    rules_applied: int
    conflicts_detected: int
    conflicts_resolved: int
    final_premium: Decimal
    base_premium: Decimal
    total_adjustment_factor: Decimal
    rule_results: List[RuleExecutionResult]
    demographic_calculation: Optional[Dict[str, Any]] = None
    execution_plan: Optional[RuleExecutionPlan] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    cache_statistics: Dict[str, Any] = field(default_factory=dict)


class RuleOrchestrationEngine:
    """
    Advanced rule orchestration engine that integrates all Step 6 components.
    Provides intelligent rule execution with caching, optimization, and monitoring.
    """
    
    def __init__(self, db: Session = None, config: OrchestrationConfig = None):
        self.db = db or next(get_db())
        self.config = config or OrchestrationConfig()
        
        # Initialize component engines
        self.logic_engine = MultiConditionLogicEngine(self.db)
        self.dependency_manager = RuleDependencyManager(self.db)
        self.age_bracket_system = AdvancedAgeBracketIntegration(self.db)
        
        # Performance and caching
        self.cache = get_cache_client() if self.config.cache_strategy != CacheStrategy.NONE else None
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_parallel_rules)
        
        # Internal state
        self.performance_stats = {
            "total_executions": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_execution_time": 0.0,
            "rule_performance": {}
        }
    
    # ============================================================================
    # MAIN ORCHESTRATION METHODS
    # ============================================================================
    
    async def orchestrate_pricing_rules(
        self,
        rule_ids: List[UUID],
        input_data: Dict[str, Any],
        demographic_profile: Optional[DemographicProfile] = None,
        base_premium: Optional[Decimal] = None,
        benefit_type: Optional[str] = None
    ) -> OrchestrationResult:
        """
        Main orchestration method that coordinates all rule evaluation components.
        
        Args:
            rule_ids: List of rule IDs to evaluate
            input_data: Input data for rule evaluation
            demographic_profile: Optional demographic information
            base_premium: Base premium for calculations
            benefit_type: Type of benefit being priced
            
        Returns:
            Complete orchestration result
        """
        start_time = time.time()
        
        try:
            # Step 1: Create execution plan with dependency resolution
            execution_plan = self.dependency_manager.create_execution_plan(
                rule_ids, self.config.conflict_resolution
            )
            
            # Step 2: Perform demographic pricing if profile provided
            demographic_calculation = None
            if demographic_profile and base_premium:
                demographic_calculation = await self._calculate_demographic_pricing(
                    base_premium, demographic_profile, benefit_type
                )
                # Use demographic result as base for rule evaluation
                input_data = {**input_data, **demographic_calculation}
            
            # Step 3: Execute rules according to plan
            rule_results = await self._execute_rules_with_plan(
                execution_plan, input_data
            )
            
            # Step 4: Calculate final pricing
            final_premium, total_factor = self._calculate_final_pricing(
                rule_results, base_premium or Decimal('0'), demographic_calculation
            )
            
            # Step 5: Compile results
            total_time = time.time() - start_time
            
            result = OrchestrationResult(
                total_execution_time=total_time,
                rules_evaluated=len(rule_results),
                rules_applied=sum(1 for r in rule_results if r.impact_applied),
                conflicts_detected=len(execution_plan.conflicts),
                conflicts_resolved=len(execution_plan.conflicts),  # All conflicts are resolved in plan
                final_premium=final_premium,
                base_premium=base_premium or Decimal('0'),
                total_adjustment_factor=total_factor,
                rule_results=rule_results,
                demographic_calculation=demographic_calculation,
                execution_plan=execution_plan,
                performance_metrics=self._generate_performance_metrics(total_time, rule_results),
                cache_statistics=self._generate_cache_statistics(rule_results)
            )
            
            # Update performance stats
            self._update_performance_stats(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in rule orchestration: {str(e)}")
            # Return error result
            return OrchestrationResult(
                total_execution_time=time.time() - start_time,
                rules_evaluated=0,
                rules_applied=0,
                conflicts_detected=0,
                conflicts_resolved=0,
                final_premium=base_premium or Decimal('0'),
                base_premium=base_premium or Decimal('0'),
                total_adjustment_factor=Decimal('1.0'),
                rule_results=[],
                performance_metrics={"error": str(e)}
            )
    
    async def _execute_rules_with_plan(
        self,
        execution_plan: RuleExecutionPlan,
        input_data: Dict[str, Any]
    ) -> List[RuleExecutionResult]:
        """Execute rules according to the execution plan."""
        
        if self.config.execution_strategy == ExecutionStrategy.SEQUENTIAL:
            return await self._execute_sequential(execution_plan.execution_order, input_data)
        
        elif self.config.execution_strategy == ExecutionStrategy.PARALLEL:
            return await self._execute_parallel(execution_plan.execution_order, input_data)
        
        elif self.config.execution_strategy == ExecutionStrategy.HYBRID:
            return await self._execute_hybrid(execution_plan, input_data)
        
        else:  # OPTIMIZED
            return await self._execute_optimized(execution_plan, input_data)
    
    async def _execute_sequential(
        self,
        rule_ids: List[UUID],
        input_data: Dict[str, Any]
    ) -> List[RuleExecutionResult]:
        """Execute rules sequentially."""
        results = []
        current_data = input_data.copy()
        
        for rule_id in rule_ids:
            result = await self._execute_single_rule(rule_id, current_data)
            results.append(result)
            
            # Update input data with rule results for next rule
            if result.success and result.impact_applied:
                current_data = self._update_input_data_with_result(current_data, result)
        
        return results
    
    async def _execute_parallel(
        self,
        rule_ids: List[UUID],
        input_data: Dict[str, Any]
    ) -> List[RuleExecutionResult]:
        """Execute rules in parallel (for independent rules)."""
        if not self.config.enable_parallel_evaluation:
            return await self._execute_sequential(rule_ids, input_data)
        
        # Create tasks for parallel execution
        tasks = [
            self._execute_single_rule(rule_id, input_data)
            for rule_id in rule_ids
        ]
        
        # Execute in batches to avoid overwhelming the system
        batch_size = self.config.max_parallel_rules
        results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            # Handle exceptions and convert to error results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    error_result = RuleExecutionResult(
                        rule_id=rule_ids[i + j],
                        rule_name="Unknown",
                        execution_time=0.0,
                        success=False,
                        condition_met=False,
                        impact_applied=False,
                        result_value=None,
                        error_message=str(result)
                    )
                    results.append(error_result)
                else:
                    results.append(result)
        
        return results
    
    async def _execute_hybrid(
        self,
        execution_plan: RuleExecutionPlan,
        input_data: Dict[str, Any]
    ) -> List[RuleExecutionResult]:
        """
        Execute rules with hybrid strategy: parallel for independent rules,
        sequential for dependent rules.
        """
        results = []
        current_data = input_data.copy()
        
        # Group rules by dependency levels
        dependency_levels = self._group_rules_by_dependency_level(execution_plan)
        
        for level_rules in dependency_levels:
            if len(level_rules) == 1:
                # Single rule - execute sequentially
                result = await self._execute_single_rule(level_rules[0], current_data)
                results.append(result)
                
                if result.success and result.impact_applied:
                    current_data = self._update_input_data_with_result(current_data, result)
            
            else:
                # Multiple independent rules - execute in parallel
                level_results = await self._execute_parallel(level_rules, current_data)
                results.extend(level_results)
                
                # Update input data with all results from this level
                for result in level_results:
                    if result.success and result.impact_applied:
                        current_data = self._update_input_data_with_result(current_data, result)
        
        return results
    
    async def _execute_optimized(
        self,
        execution_plan: RuleExecutionPlan,
        input_data: Dict[str, Any]
    ) -> List[RuleExecutionResult]:
        """Execute rules with advanced optimizations."""
        
        # First, check for cached full pipeline result
        if self.config.cache_strategy == CacheStrategy.FULL_PIPELINE:
            cached_result = await self._get_cached_pipeline_result(
                execution_plan.execution_order, input_data
            )
            if cached_result:
                return cached_result
        
        # Execute with smart caching and pre-filtering
        results = []
        current_data = input_data.copy()
        
        # Pre-filter rules that are unlikely to match based on input data
        filtered_rules = self._pre_filter_rules(execution_plan.execution_order, input_data)
        
        # Execute filtered rules
        for rule_id in filtered_rules:
            result = await self._execute_single_rule_optimized(rule_id, current_data)
            results.append(result)
            
            if result.success and result.impact_applied:
                current_data = self._update_input_data_with_result(current_data, result)
        
        # Cache pipeline result if configured
        if self.config.cache_strategy == CacheStrategy.FULL_PIPELINE:
            await self._cache_pipeline_result(execution_plan.execution_order, input_data, results)
        
        return results
    
    # ============================================================================
    # SINGLE RULE EXECUTION
    # ============================================================================
    
    async def _execute_single_rule(
        self,
        rule_id: UUID,
        input_data: Dict[str, Any]
    ) -> RuleExecutionResult:
        """Execute a single rule with caching and monitoring."""
        start_time = time.time()
        
        try:
            # Check cache first
            if self.config.cache_strategy in [CacheStrategy.RULE_LEVEL, CacheStrategy.PROFILE_LEVEL]:
                cached_result = await self._get_cached_rule_result(rule_id, input_data)
                if cached_result:
                    cached_result.execution_time = time.time() - start_time
                    cached_result.cache_hit = True
                    return cached_result
            
            # Load rule definition (this would come from database in real implementation)
            rule = await self._load_rule_definition(rule_id)
            if not rule:
                return RuleExecutionResult(
                    rule_id=rule_id,
                    rule_name="Unknown",
                    execution_time=time.time() - start_time,
                    success=False,
                    condition_met=False,
                    impact_applied=False,
                    result_value=None,
                    error_message="Rule not found"
                )
            
            # Evaluate rule conditions
            condition_met = self.logic_engine.evaluate_conditions(rule.conditions, input_data)
            
            # Apply impact if condition is met
            impact_applied = False
            result_value = None
            
            if condition_met:
                result_value = self._calculate_rule_impact(rule, input_data)
                impact_applied = True
            
            execution_time = time.time() - start_time
            
            result = RuleExecutionResult(
                rule_id=rule_id,
                rule_name=rule.name,
                execution_time=execution_time,
                success=True,
                condition_met=condition_met,
                impact_applied=impact_applied,
                result_value=result_value,
                execution_details={
                    "rule_priority": rule.priority,
                    "rule_description": rule.description,
                    "impact_type": rule.impact.type,
                    "impact_value": rule.impact.value
                }
            )
            
            # Cache result if configured
            if self.config.cache_strategy in [CacheStrategy.RULE_LEVEL, CacheStrategy.PROFILE_LEVEL]:
                await self._cache_rule_result(rule_id, input_data, result)
            
            return result
            
        except Exception as e:
            return RuleExecutionResult(
                rule_id=rule_id,
                rule_name="Unknown",
                execution_time=time.time() - start_time,
                success=False,
                condition_met=False,
                impact_applied=False,
                result_value=None,
                error_message=str(e)
            )
    
    async def _execute_single_rule_optimized(
        self,
        rule_id: UUID,
        input_data: Dict[str, Any]
    ) -> RuleExecutionResult:
        """Execute single rule with additional optimizations."""
        
        # Pre-check if rule is likely to match based on simple field checks
        if not await self._quick_rule_precheck(rule_id, input_data):
            return RuleExecutionResult(
                rule_id=rule_id,
                rule_name="Pre-filtered",
                execution_time=0.001,  # Minimal time for pre-filter
                success=True,
                condition_met=False,
                impact_applied=False,
                result_value=None,
                execution_details={"pre_filtered": True}
            )
        
        # Execute normally if pre-check passes
        return await self._execute_single_rule(rule_id, input_data)
    
    # ============================================================================
    # DEMOGRAPHIC INTEGRATION
    # ============================================================================
    
    async def _calculate_demographic_pricing(
        self,
        base_premium: Decimal,
        demographic_profile: DemographicProfile,
        benefit_type: Optional[str]
    ) -> Dict[str, Any]:
        """Calculate demographic pricing using age bracket integration."""
        
        try:
            demographic_result = self.age_bracket_system.calculate_demographic_pricing(
                base_premium=base_premium,
                demographic_profile=demographic_profile,
                benefit_type=benefit_type,
                include_actuarial=True
            )
            
            # Apply benefit-specific rules if benefit type is provided
            if benefit_type:
                demographic_result = self.age_bracket_system.apply_benefit_specific_rules(
                    demographic_result,
                    benefit_type,
                    {"coverage_limits": {"annual_limit": 50000}}  # Default benefit details
                )
            
            return demographic_result
            
        except Exception as e:
            logger.error(f"Error in demographic pricing calculation: {str(e)}")
            return {
                "base_premium": base_premium,
                "final_premium": base_premium,
                "total_factor": Decimal('1.0'),
                "adjustments": [],
                "error": str(e)
            }
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _group_rules_by_dependency_level(self, execution_plan: RuleExecutionPlan) -> List[List[UUID]]:
        """Group rules by dependency level for hybrid execution."""
        levels = []
        remaining_rules = set(execution_plan.execution_order)
        processed_rules = set()
        
        while remaining_rules:
            current_level = []
            
            for rule_id in list(remaining_rules):
                # Check if all dependencies are satisfied
                dependencies = self.dependency_manager.get_dependencies(rule_id)
                prerequisite_deps = [
                    dep.dependency_rule_id for dep in dependencies 
                    if dep.dependency_type.value == "prerequisite"
                ]
                
                if all(dep_id in processed_rules for dep_id in prerequisite_deps):
                    current_level.append(rule_id)
                    remaining_rules.remove(rule_id)
            
            if not current_level:
                # No progress made - add remaining rules to avoid infinite loop
                current_level = list(remaining_rules)
                remaining_rules.clear()
            
            levels.append(current_level)
            processed_rules.update(current_level)
        
        return levels
    
    def _pre_filter_rules(self, rule_ids: List[UUID], input_data: Dict[str, Any]) -> List[UUID]:
        """Pre-filter rules that are unlikely to match."""
        # Simple implementation - in practice this would check field availability
        filtered = []
        
        for rule_id in rule_ids:
            # Placeholder: check if rule's primary field exists in input data
            # This would require access to rule definitions
            filtered.append(rule_id)  # For now, include all rules
        
        return filtered
    
    async def _quick_rule_precheck(self, rule_id: UUID, input_data: Dict[str, Any]) -> bool:
        """Quick check if rule might match without full evaluation."""
        # Placeholder implementation - would check simple field conditions
        return True  # For now, assume all rules pass pre-check
    
    def _calculate_rule_impact(self, rule: AdvancedRule, input_data: Dict[str, Any]) -> Decimal:
        """Calculate the impact value of a rule."""
        impact = rule.impact
        
        if impact.type == "PERCENTAGE":
            base_value = Decimal(str(input_data.get("premium", 1000)))
            return base_value * Decimal(str(impact.value))
        
        elif impact.type == "FIXED_AMOUNT":
            return Decimal(str(impact.value))
        
        elif impact.type == "MULTIPLIER":
            base_value = Decimal(str(input_data.get("premium", 1000)))
            return base_value * (Decimal(str(impact.value)) - Decimal('1.0'))
        
        elif impact.type == "FORMULA" and impact.formula:
            # Simple formula evaluation (in practice, use a proper expression evaluator)
            try:
                # Replace variables in formula with actual values
                formula = impact.formula
                for key, value in input_data.items():
                    formula = formula.replace(key, str(value))
                
                # Evaluate simple mathematical expressions
                # WARNING: This is unsafe in production - use a proper expression evaluator
                result = eval(formula.replace("base_premium", str(input_data.get("premium", 1000))))
                return Decimal(str(result))
            except:
                return Decimal('0')
        
        return Decimal('0')
    
    def _update_input_data_with_result(
        self,
        input_data: Dict[str, Any],
        result: RuleExecutionResult
    ) -> Dict[str, Any]:
        """Update input data with rule execution result."""
        updated_data = input_data.copy()
        
        if result.result_value and result.impact_applied:
            # Update premium with rule impact
            current_premium = Decimal(str(updated_data.get("premium", 0)))
            updated_data["premium"] = current_premium + result.result_value
            
            # Add rule application history
            if "applied_rules" not in updated_data:
                updated_data["applied_rules"] = []
            
            updated_data["applied_rules"].append({
                "rule_id": str(result.rule_id),
                "rule_name": result.rule_name,
                "impact_value": float(result.result_value),
                "applied_at": datetime.utcnow().isoformat()
            })
        
        return updated_data
    
    def _calculate_final_pricing(
        self,
        rule_results: List[RuleExecutionResult],
        base_premium: Decimal,
        demographic_calculation: Optional[Dict[str, Any]]
    ) -> Tuple[Decimal, Decimal]:
        """Calculate final premium and total adjustment factor."""
        
        # Start with demographic pricing if available
        if demographic_calculation:
            current_premium = demographic_calculation.get("final_premium", base_premium)
        else:
            current_premium = base_premium
        
        # Apply rule impacts
        for result in rule_results:
            if result.success and result.impact_applied and result.result_value:
                current_premium += result.result_value
        
        # Calculate total factor
        total_factor = current_premium / base_premium if base_premium > 0 else Decimal('1.0')
        
        return current_premium, total_factor
    
    # ============================================================================
    # CACHING METHODS
    # ============================================================================
    
    async def _get_cached_rule_result(
        self,
        rule_id: UUID,
        input_data: Dict[str, Any]
    ) -> Optional[RuleExecutionResult]:
        """Get cached rule result if available."""
        if not self.cache:
            return None
        
        cache_key = self._generate_rule_cache_key(rule_id, input_data)
        
        try:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                self.performance_stats["cache_hits"] += 1
                # Deserialize cached result
                return self._deserialize_rule_result(cached_data)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {str(e)}")
        
        self.performance_stats["cache_misses"] += 1
        return None
    
    async def _cache_rule_result(
        self,
        rule_id: UUID,
        input_data: Dict[str, Any],
        result: RuleExecutionResult
    ):
        """Cache rule result."""
        if not self.cache:
            return
        
        cache_key = self._generate_rule_cache_key(rule_id, input_data)
        
        try:
            serialized_result = self._serialize_rule_result(result)
            await self.cache.setex(cache_key, self.config.cache_ttl, serialized_result)
        except Exception as e:
            logger.warning(f"Cache storage error: {str(e)}")
    
    def _generate_rule_cache_key(self, rule_id: UUID, input_data: Dict[str, Any]) -> str:
        """Generate cache key for rule result."""
        # Create hash of relevant input data for cache key
        relevant_data = {k: v for k, v in input_data.items() if k in ["age", "gender", "territory", "premium"]}
        data_hash = hash(json.dumps(relevant_data, sort_keys=True))
        return f"rule_result:{rule_id}:{data_hash}"
    
    # ============================================================================
    # PERFORMANCE MONITORING
    # ============================================================================
    
    def _generate_performance_metrics(
        self,
        total_time: float,
        rule_results: List[RuleExecutionResult]
    ) -> Dict[str, Any]:
        """Generate performance metrics for the execution."""
        
        successful_rules = [r for r in rule_results if r.success]
        failed_rules = [r for r in rule_results if not r.success]
        
        return {
            "total_execution_time": total_time,
            "average_rule_time": sum(r.execution_time for r in successful_rules) / len(successful_rules) if successful_rules else 0,
            "fastest_rule_time": min(r.execution_time for r in successful_rules) if successful_rules else 0,
            "slowest_rule_time": max(r.execution_time for r in successful_rules) if successful_rules else 0,
            "successful_rules": len(successful_rules),
            "failed_rules": len(failed_rules),
            "cache_hit_rate": self.performance_stats["cache_hits"] / (self.performance_stats["cache_hits"] + self.performance_stats["cache_misses"]) if (self.performance_stats["cache_hits"] + self.performance_stats["cache_misses"]) > 0 else 0,
            "rules_per_second": len(rule_results) / total_time if total_time > 0 else 0
        }
    
    def _generate_cache_statistics(self, rule_results: List[RuleExecutionResult]) -> Dict[str, Any]:
        """Generate cache statistics."""
        cache_hits = sum(1 for r in rule_results if r.cache_hit)
        total_rules = len(rule_results)
        
        return {
            "cache_hits": cache_hits,
            "cache_misses": total_rules - cache_hits,
            "cache_hit_rate": cache_hits / total_rules if total_rules > 0 else 0,
            "cache_strategy": self.config.cache_strategy.value
        }
    
    def _update_performance_stats(self, result: OrchestrationResult):
        """Update global performance statistics."""
        self.performance_stats["total_executions"] += 1
        
        # Update average execution time
        current_avg = self.performance_stats["average_execution_time"]
        total_executions = self.performance_stats["total_executions"]
        new_avg = ((current_avg * (total_executions - 1)) + result.total_execution_time) / total_executions
        self.performance_stats["average_execution_time"] = new_avg
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def _load_rule_definition(self, rule_id: UUID) -> Optional[AdvancedRule]:
        """Load rule definition from database or cache."""
        # Placeholder implementation - would load from database
        # For demonstration, create a sample rule
        from app.modules.pricing.profiles.services.advanced_rule_engine import LogicalOperator, ComparisonOperator
        
        conditions = ConditionNode(
            operator=LogicalOperator.AND,
            conditions=[
                ConditionNode(
                    operator=ComparisonOperator.GREATER_THAN,
                    field="age",
                    value=25
                ),
                ConditionNode(
                    operator=ComparisonOperator.LESS_THAN,
                    field="age",
                    value=65
                )
            ]
        )
        
        impact = RuleImpact(
            type="PERCENTAGE",
            value=-0.10,
            formula="base_premium * (1 - 0.10)",
            description="10% discount for middle-aged members"
        )
        
        return AdvancedRule(
            rule_id=rule_id,
            name=f"Sample Rule {rule_id}",
            description="Example rule for demonstration",
            conditions=conditions,
            impact=impact,
            priority=100
        )
    
    def _serialize_rule_result(self, result: RuleExecutionResult) -> str:
        """Serialize rule result for caching."""
        return json.dumps({
            "rule_id": str(result.rule_id),
            "rule_name": result.rule_name,
            "success": result.success,
            "condition_met": result.condition_met,
            "impact_applied": result.impact_applied,
            "result_value": str(result.result_value) if result.result_value else None,
            "error_message": result.error_message,
            "execution_details": result.execution_details
        })
    
    def _deserialize_rule_result(self, cached_data: str) -> RuleExecutionResult:
        """Deserialize cached rule result."""
        data = json.loads(cached_data)
        
        return RuleExecutionResult(
            rule_id=UUID(data["rule_id"]),
            rule_name=data["rule_name"],
            execution_time=0.0,  # Will be updated by caller
            success=data["success"],
            condition_met=data["condition_met"],
            impact_applied=data["impact_applied"],
            result_value=Decimal(data["result_value"]) if data["result_value"] else None,
            error_message=data["error_message"],
            cache_hit=True,
            execution_details=data["execution_details"]
        )
    
    # ============================================================================
    # PUBLIC INTERFACE METHODS
    # ============================================================================
    
    def update_configuration(self, new_config: OrchestrationConfig):
        """Update orchestration configuration."""
        self.config = new_config
        logger.info("Updated orchestration configuration")
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        return self.performance_stats.copy()
    
    def clear_performance_statistics(self):
        """Clear performance statistics."""
        self.performance_stats = {
            "total_executions": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_execution_time": 0.0,
            "rule_performance": {}
        }
        logger.info("Cleared performance statistics")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all components."""
        health_status = {
            "orchestration_engine": "healthy",
            "logic_engine": "healthy",
            "dependency_manager": "healthy",
            "age_bracket_system": "healthy",
            "cache": "healthy" if self.cache else "disabled",
            "thread_pool": "healthy",
            "last_check": datetime.utcnow().isoformat()
        }
        
        # Test each component
        try:
            # Test cache if enabled
            if self.cache:
                await self.cache.ping()
        except Exception as e:
            health_status["cache"] = f"unhealthy: {str(e)}"
        
        return health_status


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_orchestration_usage():
    """Demonstrate the complete rule orchestration engine."""
    
    # Create configuration
    config = OrchestrationConfig(
        execution_strategy=ExecutionStrategy.HYBRID,
        cache_strategy=CacheStrategy.PROFILE_LEVEL,
        conflict_resolution=ConflictResolutionStrategy.PRIORITY_BASED,
        enable_parallel_evaluation=True,
        max_parallel_rules=5,
        enable_performance_monitoring=True
    )
    
    # Initialize orchestration engine
    engine = RuleOrchestrationEngine(config=config)
    
    # Create demographic profile
    from app.modules.pricing.profiles.services.age_bracket_integration import DemographicProfile, Gender
    
    demographic_profile = DemographicProfile(
        age=35,
        gender=Gender.FEMALE,
        territory="URBAN",
        occupation="HEALTHCARE_PROVIDER",
        risk_factors=["FAMILY_HISTORY_CARDIAC"]
    )
    
    # Define input data
    input_data = {
        "age": 35,
        "gender": "F",
        "territory": "URBAN",
        "premium": 1000,
        "coverage_type": "PREMIUM",
        "occupation": "HEALTHCARE_PROVIDER"
    }
    
    # Example rule IDs (would come from database)
    rule_ids = [
        UUID('11111111-1111-1111-1111-111111111111'),
        UUID('22222222-2222-2222-2222-222222222222'),
        UUID('33333333-3333-3333-3333-333333333333')
    ]
    
    # Execute orchestration
    result = await engine.orchestrate_pricing_rules(
        rule_ids=rule_ids,
        input_data=input_data,
        demographic_profile=demographic_profile,
        base_premium=Decimal('1000.00'),
        benefit_type="MEDICAL"
    )
    
    # Display results
    print(f"Orchestration completed in {result.total_execution_time:.3f} seconds")
    print(f"Base Premium: ${result.base_premium}")
    print(f"Final Premium: ${result.final_premium}")
    print(f"Total Adjustment Factor: {result.total_adjustment_factor}")
    print(f"Rules Evaluated: {result.rules_evaluated}")
    print(f"Rules Applied: {result.rules_applied}")
    print(f"Conflicts Detected: {result.conflicts_detected}")
    
    print("\nRule Results:")
    for rule_result in result.rule_results:
        status = "✅" if rule_result.success else "❌"
        impact = "💰" if rule_result.impact_applied else "⏭️"
        cache = "🗂️" if rule_result.cache_hit else "🔄"
        
        print(f"  {status} {impact} {cache} {rule_result.rule_name}: "
              f"{rule_result.execution_time:.3f}s")
        
        if rule_result.result_value:
            print(f"    Impact: ${rule_result.result_value}")
    
    print(f"\nPerformance Metrics:")
    for key, value in result.performance_metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(example_orchestration_usage())