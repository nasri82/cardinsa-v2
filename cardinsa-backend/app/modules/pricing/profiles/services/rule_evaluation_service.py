# app/modules/pricing/profiles/services/rule_evaluation_service.py
from typing import List, Optional, Dict, Any, Union, Tuple
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.pricing.profiles.repositories.quotation_pricing_profile_rule_repository import QuotationPricingProfileRuleRepository
from app.modules.pricing.profiles.repositories.quotation_pricing_rule_repository import QuotationPricingRuleRepository
from app.modules.pricing.profiles.services.pricing_rules_service import PricingRulesService
from app.modules.pricing.profiles.schemas.pricing_rule_schema import (
    RuleEvaluationRequest,
    RuleEvaluationResult,
    BatchEvaluationRequest,
    BatchEvaluationResult
)
from app.core.exceptions import (
    EntityNotFoundError,
    BusinessLogicError,
    ValidationError,
    DatabaseOperationError
)
from app.core.logging import get_logger
from app.core.cache import get_cache_client


logger = get_logger(__name__)


class RuleEvaluationService:
    """
    Advanced service for rule evaluation with caching, batch processing, and performance optimization.
    Handles complex rule orchestration and evaluation strategies.
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.profile_rule_repo = QuotationPricingProfileRuleRepository(self.db)
        self.rule_repo = QuotationPricingRuleRepository(self.db)
        self.rules_service = PricingRulesService(self.db)
        self.cache = get_cache_client()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
    
    # ============================================================================
    # ADVANCED EVALUATION METHODS
    # ============================================================================
    
    async def evaluate_profile_async(
        self,
        profile_id: UUID,
        input_data: Dict[str, Any],
        evaluation_strategy: str = 'sequential',
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Asynchronously evaluate all rules for a pricing profile with advanced strategies.
        
        Args:
            profile_id: ID of the pricing profile
            input_data: Input data for rule evaluation
            evaluation_strategy: Strategy for evaluation ('sequential', 'parallel', 'optimized')
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with comprehensive evaluation results
        """
        try:
            logger.info(f"Starting async evaluation for profile {profile_id}")
            
            # Check cache first
            if use_cache:
                cached_result = await self._get_cached_evaluation(profile_id, input_data)
                if cached_result:
                    logger.info(f"Returning cached evaluation for profile {profile_id}")
                    return cached_result
            
            # Get profile rules
            profile_rules = self.profile_rule_repo.get_profile_rules_ordered(
                profile_id=profile_id,
                active_only=True
            )
            
            if not profile_rules:
                return self._empty_evaluation_result(profile_id)
            
            # Choose evaluation strategy
            if evaluation_strategy == 'parallel':
                evaluation_result = await self._evaluate_rules_parallel(profile_rules, input_data)
            elif evaluation_strategy == 'optimized':
                evaluation_result = await self._evaluate_rules_optimized(profile_rules, input_data)
            else:  # sequential
                evaluation_result = await self._evaluate_rules_sequential(profile_rules, input_data)
            
            # Add profile metadata
            evaluation_result.update({
                'profile_id': str(profile_id),
                'evaluation_strategy': evaluation_strategy,
                'cache_used': False,
                'evaluation_timestamp': datetime.utcnow().isoformat()
            })
            
            # Cache the result
            if use_cache:
                await self._cache_evaluation_result(profile_id, input_data, evaluation_result)
            
            logger.info(f"Completed async evaluation for profile {profile_id}")
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error in async profile evaluation: {str(e)}")
            raise
    
    def evaluate_batch_profiles(
        self,
        batch_request: BatchEvaluationRequest
    ) -> BatchEvaluationResult:
        """
        Evaluate multiple profiles in batch with optimized processing.
        
        Args:
            batch_request: Batch evaluation request
            
        Returns:
            Batch evaluation results
        """
        try:
            logger.info(f"Starting batch evaluation for {len(batch_request.profile_evaluations)} profiles")
            
            batch_results = []
            total_processing_time = 0
            successful_evaluations = 0
            failed_evaluations = 0
            
            start_time = datetime.utcnow()
            
            # Process each profile evaluation
            for profile_eval in batch_request.profile_evaluations:
                try:
                    eval_start = datetime.utcnow()
                    
                    # Evaluate profile
                    result = self.rules_service.evaluate_profile_rules(
                        profile_id=profile_eval.profile_id,
                        input_data=profile_eval.input_data
                    )
                    
                    eval_time = (datetime.utcnow() - eval_start).total_seconds()
                    
                    batch_results.append({
                        'profile_id': str(profile_eval.profile_id),
                        'evaluation_successful': True,
                        'evaluation_time_seconds': eval_time,
                        'result': result,
                        'error': None
                    })
                    
                    total_processing_time += eval_time
                    successful_evaluations += 1
                    
                except Exception as e:
                    batch_results.append({
                        'profile_id': str(profile_eval.profile_id),
                        'evaluation_successful': False,
                        'evaluation_time_seconds': 0,
                        'result': None,
                        'error': str(e)
                    })
                    failed_evaluations += 1
            
            total_time = (datetime.utcnow() - start_time).total_seconds()
            
            return BatchEvaluationResult(
                batch_id=batch_request.batch_id,
                total_profiles=len(batch_request.profile_evaluations),
                successful_evaluations=successful_evaluations,
                failed_evaluations=failed_evaluations,
                total_processing_time=total_processing_time,
                total_elapsed_time=total_time,
                average_processing_time=total_processing_time / len(batch_request.profile_evaluations) if batch_request.profile_evaluations else 0,
                results=batch_results,
                batch_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error in batch evaluation: {str(e)}")
            raise
    
    def evaluate_with_simulation(
        self,
        profile_id: UUID,
        base_input_data: Dict[str, Any],
        simulation_parameters: Dict[str, List[Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate a profile with multiple simulation scenarios.
        
        Args:
            profile_id: ID of the pricing profile
            base_input_data: Base input data
            simulation_parameters: Parameters to vary in simulation
            
        Returns:
            Dictionary with simulation results
        """
        try:
            logger.info(f"Starting simulation evaluation for profile {profile_id}")
            
            # Generate simulation scenarios
            scenarios = self._generate_simulation_scenarios(base_input_data, simulation_parameters)
            
            simulation_results = []
            
            for i, scenario in enumerate(scenarios):
                try:
                    result = self.rules_service.evaluate_profile_rules(
                        profile_id=profile_id,
                        input_data=scenario
                    )
                    
                    simulation_results.append({
                        'scenario_number': i + 1,
                        'scenario_parameters': {k: v for k, v in scenario.items() if k in simulation_parameters},
                        'evaluation_result': result,
                        'total_impact': result.get('total_impact', 0),
                        'rules_applied': result.get('rules_applied', 0)
                    })
                    
                except Exception as e:
                    simulation_results.append({
                        'scenario_number': i + 1,
                        'scenario_parameters': {k: v for k, v in scenario.items() if k in simulation_parameters},
                        'evaluation_result': None,
                        'error': str(e)
                    })
            
            # Analyze simulation results
            analysis = self._analyze_simulation_results(simulation_results)
            
            return {
                'profile_id': str(profile_id),
                'simulation_parameters': simulation_parameters,
                'total_scenarios': len(scenarios),
                'successful_scenarios': len([r for r in simulation_results if 'error' not in r]),
                'simulation_results': simulation_results,
                'analysis': analysis,
                'simulation_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in simulation evaluation: {str(e)}")
            raise
    
    # ============================================================================
    # PERFORMANCE OPTIMIZATION METHODS
    # ============================================================================
    
    def optimize_rule_execution_order(
        self,
        profile_id: UUID,
        sample_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize the execution order of rules based on performance analysis.
        
        Args:
            profile_id: ID of the pricing profile
            sample_data: Sample data for performance testing
            
        Returns:
            Dictionary with optimization recommendations
        """
        try:
            logger.info(f"Optimizing rule execution order for profile {profile_id}")
            
            # Get current rule order
            profile_rules = self.profile_rule_repo.get_profile_rules_ordered(profile_id)
            
            if len(profile_rules) <= 1:
                return {
                    'optimization_needed': False,
                    'message': 'Profile has 1 or fewer rules - no optimization needed'
                }
            
            # Generate sample data if not provided
            if not sample_data:
                sample_data = self._generate_sample_data(profile_rules)
            
            # Analyze rule performance
            rule_performance = []
            
            for rule_data in profile_rules:
                rule_id = UUID(rule_data['rule']['id'])
                
                # Test rule performance
                performance_metrics = self._measure_rule_performance(rule_id, sample_data)
                
                rule_performance.append({
                    'rule_id': str(rule_id),
                    'rule_name': rule_data['rule']['name'],
                    'current_order': rule_data['order_index'],
                    'average_execution_time': performance_metrics['avg_execution_time'],
                    'success_rate': performance_metrics['success_rate'],
                    'condition_match_rate': performance_metrics['condition_match_rate'],
                    'complexity_score': performance_metrics['complexity_score']
                })
            
            # Calculate optimal order
            optimal_order = self._calculate_optimal_rule_order(rule_performance)
            
            # Generate recommendations
            recommendations = []
            current_order = {rp['rule_id']: rp['current_order'] for rp in rule_performance}
            
            for new_index, rule_id in enumerate(optimal_order):
                current_index = current_order[rule_id]
                if current_index != new_index:
                    recommendations.append({
                        'rule_id': rule_id,
                        'rule_name': next(rp['rule_name'] for rp in rule_performance if rp['rule_id'] == rule_id),
                        'current_order': current_index,
                        'recommended_order': new_index,
                        'reason': self._get_optimization_reason(rule_id, rule_performance)
                    })
            
            return {
                'profile_id': str(profile_id),
                'optimization_needed': len(recommendations) > 0,
                'current_performance': {
                    'total_rules': len(rule_performance),
                    'average_execution_time': sum(rp['average_execution_time'] for rp in rule_performance) / len(rule_performance),
                    'total_complexity_score': sum(rp['complexity_score'] for rp in rule_performance)
                },
                'rule_performance_analysis': rule_performance,
                'optimization_recommendations': recommendations,
                'optimal_execution_order': optimal_order,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing rule execution order: {str(e)}")
            raise
    
    def get_evaluation_statistics(
        self,
        profile_id: UUID = None,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get evaluation statistics and performance metrics.
        
        Args:
            profile_id: Profile ID for specific stats (optional)
            time_period_days: Time period for statistics
            
        Returns:
            Dictionary with evaluation statistics
        """
        try:
            # This would integrate with monitoring/metrics system
            # For now, return structure for implementation
            
            stats = {
                'time_period_days': time_period_days,
                'evaluation_metrics': {
                    'total_evaluations': 0,
                    'successful_evaluations': 0,
                    'failed_evaluations': 0,
                    'average_evaluation_time': 0.0,
                    'cache_hit_rate': 0.0
                },
                'performance_metrics': {
                    'fastest_evaluation_time': 0.0,
                    'slowest_evaluation_time': 0.0,
                    'average_rules_per_evaluation': 0.0,
                    'most_used_rules': [],
                    'performance_trends': []
                }
            }
            
            if profile_id:
                stats['profile_id'] = str(profile_id)
                stats['profile_specific_metrics'] = {
                    'profile_evaluation_count': 0,
                    'profile_average_time': 0.0,
                    'profile_success_rate': 0.0
                }
            
            # TODO: Implement actual metrics collection when monitoring is set up
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting evaluation statistics: {str(e)}")
            raise
    
    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    async def _evaluate_rules_sequential(
        self,
        profile_rules: List[Dict[str, Any]],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate rules sequentially."""
        rule_ids = [UUID(rule_data['rule']['id']) for rule_data in profile_rules]
        
        return await asyncio.get_event_loop().run_in_executor(
            self.thread_pool,
            lambda: self.rules_service.evaluate_rule_set(rule_ids, input_data, 'sequential')
        )
    
    async def _evaluate_rules_parallel(
        self,
        profile_rules: List[Dict[str, Any]],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate rules in parallel."""
        rule_ids = [UUID(rule_data['rule']['id']) for rule_data in profile_rules]
        
        # Create evaluation tasks
        tasks = []
        for rule_id in rule_ids:
            task = asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                lambda rid=rule_id: self.rules_service.evaluate_single_rule(rid, input_data)
            )
            tasks.append(task)
        
        # Wait for all evaluations to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        evaluation_results = []
        total_impact = 0.0
        rules_applied = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exceptions
                evaluation_results.append(RuleEvaluationResult(
                    rule_id=rule_ids[i],
                    rule_name="Unknown",
                    condition_met=False,
                    impact_applied=False,
                    result_value=None,
                    evaluation_details={'error': str(result)}
                ))
            else:
                evaluation_results.append(result)
                if result.impact_applied and result.result_value is not None:
                    total_impact += float(result.result_value)
                    rules_applied += 1
        
        return {
            'total_rules_evaluated': len(rule_ids),
            'rules_with_conditions_met': sum(1 for r in evaluation_results if r.condition_met),
            'rules_applied': rules_applied,
            'total_impact': total_impact,
            'average_impact': total_impact / rules_applied if rules_applied > 0 else 0,
            'evaluation_order': 'parallel',
            'individual_results': evaluation_results,
            'evaluation_timestamp': datetime.utcnow()
        }
    
    async def _evaluate_rules_optimized(
        self,
        profile_rules: List[Dict[str, Any]],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate rules with optimization strategies."""
        # Pre-filter rules based on input data
        applicable_rules = self._filter_applicable_rules(profile_rules, input_data)
        
        if len(applicable_rules) < len(profile_rules):
            logger.info(f"Optimized evaluation: filtered to {len(applicable_rules)} applicable rules")
        
        # Use parallel evaluation for applicable rules
        return await self._evaluate_rules_parallel(applicable_rules, input_data)
    
    def _filter_applicable_rules(
        self,
        profile_rules: List[Dict[str, Any]],
        input_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter rules that could potentially apply to the input data."""
        applicable_rules = []
        
        for rule_data in profile_rules:
            rule = rule_data['rule']
            field_name = rule['field_name']
            
            # Check if required field exists in input data
            if field_name in input_data:
                # Additional pre-filtering logic can be added here
                applicable_rules.append(rule_data)
        
        return applicable_rules
    
    async def _get_cached_evaluation(
        self,
        profile_id: UUID,
        input_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached evaluation result if available."""
        try:
            cache_key = self._generate_cache_key(profile_id, input_data)
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.warning(f"Error getting cached evaluation: {str(e)}")
            return None
    
    async def _cache_evaluation_result(
        self,
        profile_id: UUID,
        input_data: Dict[str, Any],
        evaluation_result: Dict[str, Any]
    ) -> None:
        """Cache evaluation result."""
        try:
            cache_key = self._generate_cache_key(profile_id, input_data)
            cache_data = json.dumps(evaluation_result, default=str)
            
            # Cache for 1 hour
            await self.cache.setex(cache_key, 3600, cache_data)
            
        except Exception as e:
            logger.warning(f"Error caching evaluation result: {str(e)}")
    
    def _generate_cache_key(
        self,
        profile_id: UUID,
        input_data: Dict[str, Any]
    ) -> str:
        """Generate cache key for evaluation result."""
        # Create deterministic key from profile_id and input_data
        import hashlib
        
        data_str = json.dumps(input_data, sort_keys=True, default=str)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        
        return f"rule_eval:{profile_id}:{data_hash}"
    
    def _empty_evaluation_result(self, profile_id: UUID) -> Dict[str, Any]:
        """Generate empty evaluation result."""
        return {
            'profile_id': str(profile_id),
            'total_rules_evaluated': 0,
            'rules_with_conditions_met': 0,
            'rules_applied': 0,
            'total_impact': 0.0,
            'average_impact': 0.0,
            'individual_results': [],
            'evaluation_timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_simulation_scenarios(
        self,
        base_data: Dict[str, Any],
        parameters: Dict[str, List[Any]]
    ) -> List[Dict[str, Any]]:
        """Generate simulation scenarios from parameter combinations."""
        scenarios = []
        
        # Simple cartesian product for now - can be optimized for large parameter sets
        import itertools
        
        param_names = list(parameters.keys())
        param_values = [parameters[name] for name in param_names]
        
        for combination in itertools.product(*param_values):
            scenario = base_data.copy()
            for i, value in enumerate(combination):
                scenario[param_names[i]] = value
            scenarios.append(scenario)
        
        return scenarios
    
    def _analyze_simulation_results(
        self,
        simulation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze simulation results for insights."""
        successful_results = [r for r in simulation_results if 'error' not in r]
        
        if not successful_results:
            return {'error': 'No successful simulation scenarios'}
        
        total_impacts = [r['total_impact'] for r in successful_results]
        
        return {
            'total_scenarios': len(simulation_results),
            'successful_scenarios': len(successful_results),
            'impact_statistics': {
                'min_impact': min(total_impacts),
                'max_impact': max(total_impacts),
                'average_impact': sum(total_impacts) / len(total_impacts),
                'impact_range': max(total_impacts) - min(total_impacts)
            },
            'scenario_insights': {
                'best_scenario': max(successful_results, key=lambda x: x['total_impact']),
                'worst_scenario': min(successful_results, key=lambda x: x['total_impact'])
            }
        }
    
    def _generate_sample_data(
        self,
        profile_rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate sample data for performance testing."""
        # Extract field names from rules
        field_names = set()
        for rule_data in profile_rules:
            field_names.add(rule_data['rule']['field_name'])
        
        # Generate sample data sets
        sample_data = []
        for i in range(10):  # Generate 10 sample data sets
            data = {}
            for field_name in field_names:
                # Generate appropriate sample values based on field name
                if 'age' in field_name.lower():
                    data[field_name] = 25 + (i * 5)
                elif 'premium' in field_name.lower():
                    data[field_name] = 1000.0 + (i * 100)
                elif 'percentage' in field_name.lower():
                    data[field_name] = 0.1 + (i * 0.05)
                else:
                    data[field_name] = i + 1
            
            sample_data.append(data)
        
        return sample_data
    
    def _measure_rule_performance(
        self,
        rule_id: UUID,
        sample_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Measure performance metrics for a rule."""
        execution_times = []
        successes = 0
        condition_matches = 0
        
        for data in sample_data:
            start_time = datetime.utcnow()
            
            try:
                result = self.rules_service.evaluate_single_rule(rule_id, data)
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                execution_times.append(execution_time)
                successes += 1
                
                if result.condition_met:
                    condition_matches += 1
                    
            except Exception:
                execution_times.append(0.1)  # Default penalty time for failures
        
        return {
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'success_rate': successes / len(sample_data),
            'condition_match_rate': condition_matches / len(sample_data),
            'complexity_score': self._calculate_rule_complexity_score(rule_id)
        }
    
    def _calculate_rule_complexity_score(self, rule_id: UUID) -> int:
        """Calculate complexity score for a rule."""
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            return 0
        
        complexity = 1
        
        # Add complexity based on operator
        if rule.operator in ['IN', 'BETWEEN']:
            complexity += 2
        
        # Add complexity for formula
        if rule.formula:
            complexity += 3
        
        return complexity
    
    def _calculate_optimal_rule_order(
        self,
        rule_performance: List[Dict[str, Any]]
    ) -> List[str]:
        """Calculate optimal execution order based on performance metrics."""
        # Sort rules by performance score (lower is better)
        def performance_score(rule_perf):
            # Weight: execution time (40%), complexity (30%), condition match rate (30%)
            score = (
                rule_perf['average_execution_time'] * 0.4 +
                rule_perf['complexity_score'] * 0.3 +
                (1 - rule_perf['condition_match_rate']) * 0.3  # Lower match rate = higher score
            )
            return score
        
        sorted_rules = sorted(rule_performance, key=performance_score)
        return [rule['rule_id'] for rule in sorted_rules]
    
    def _get_optimization_reason(
        self,
        rule_id: str,
        rule_performance: List[Dict[str, Any]]
    ) -> str:
        """Get reason for rule order optimization."""
        rule_perf = next(rp for rp in rule_performance if rp['rule_id'] == rule_id)
        
        if rule_perf['average_execution_time'] > 0.1:
            return "High execution time - move later"
        elif rule_perf['condition_match_rate'] < 0.3:
            return "Low condition match rate - move later"
        elif rule_perf['complexity_score'] > 5:
            return "High complexity - optimize position"
        else:
            return "Performance optimization"