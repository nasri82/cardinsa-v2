# app/modules/pricing/profiles/routes/pricing_analytics_route.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.responses import create_response, create_error_response
from app.modules.pricing.profiles.services.pricing_profile_service import PricingProfileService
from app.modules.pricing.profiles.services.pricing_rules_service import PricingRulesService
from app.modules.pricing.profiles.services.rule_evaluation_service import RuleEvaluationService
from app.modules.pricing.profiles.repositories.quotation_pricing_profile_rule_repository import QuotationPricingProfileRuleRepository
from app.modules.auth.models.user_model import User
from app.core.exceptions import EntityNotFoundError


router = APIRouter(prefix="/pricing/analytics", tags=["Pricing Analytics"])


def get_profile_service(db: Session = Depends(get_db)) -> PricingProfileService:
    """Dependency to get pricing profile service."""
    return PricingProfileService(db)


def get_rules_service(db: Session = Depends(get_db)) -> PricingRulesService:
    """Dependency to get pricing rules service."""
    return PricingRulesService(db)


def get_evaluation_service(db: Session = Depends(get_db)) -> RuleEvaluationService:
    """Dependency to get rule evaluation service."""
    return RuleEvaluationService(db)


def get_profile_rule_repo(db: Session = Depends(get_db)) -> QuotationPricingProfileRuleRepository:
    """Dependency to get profile rule repository."""
    return QuotationPricingProfileRuleRepository(db)


# ============================================================================
# SYSTEM-WIDE ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_pricing_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_profile_service),
    rules_service: PricingRulesService = Depends(get_rules_service),
    profile_rule_repo: QuotationPricingProfileRuleRepository = Depends(get_profile_rule_repo)
):
    """
    Get comprehensive pricing dashboard analytics.
    
    Returns system-wide statistics and key metrics for pricing profiles and rules.
    """
    try:
        # Get profile statistics
        profile_stats = profile_service.search_pricing_profiles(limit=1)['pagination']
        
        # Get rule statistics  
        rule_stats = rules_service.search_pricing_rules(limit=1)['pagination']
        
        # Get profile-rule relationship statistics
        relationship_stats = profile_rule_repo.get_profile_statistics()
        
        # Calculate health scores
        active_profiles = profile_service.search_pricing_profiles(is_active=True, limit=1000)
        active_rules = rules_service.search_pricing_rules(is_active=True, limit=1000)
        
        dashboard_data = {
            "overview": {
                "total_profiles": profile_stats.get('total_count', 0),
                "total_rules": rule_stats.get('total_count', 0),
                "active_profiles": len(active_profiles['profiles']),
                "active_rules": len(active_rules['rules']),
                "total_relationships": relationship_stats.get('total_relationships', 0),
                "active_relationships": relationship_stats.get('active_relationships', 0)
            },
            "health_metrics": {
                "profile_activation_rate": (len(active_profiles['profiles']) / max(profile_stats.get('total_count', 1), 1)) * 100,
                "rule_activation_rate": (len(active_rules['rules']) / max(rule_stats.get('total_count', 1), 1)) * 100,
                "relationship_health": relationship_stats.get('active_relationships', 0) / max(relationship_stats.get('total_relationships', 1), 1) * 100,
                "average_rules_per_profile": relationship_stats.get('average_rules_per_profile', 0)
            },
            "usage_patterns": {
                "most_used_rules": relationship_stats.get('most_used_rules', []),
                "profiles_with_rules": relationship_stats.get('profiles_with_rules', 0),
                "rules_in_use": relationship_stats.get('rules_in_use', 0)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return create_response(
            data=dashboard_data,
            message="Pricing dashboard data retrieved successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to retrieve dashboard data",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/system-health", response_model=Dict[str, Any])
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_profile_service),
    rules_service: PricingRulesService = Depends(get_rules_service)
):
    """
    Get system health status for pricing module.
    
    Returns health indicators and potential issues across the pricing system.
    """
    try:
        health_status = {
            "overall_status": "healthy",
            "components": {
                "profiles": {"status": "healthy", "issues": []},
                "rules": {"status": "healthy", "issues": []},
                "relationships": {"status": "healthy", "issues": []}
            },
            "recommendations": [],
            "last_check": datetime.utcnow().isoformat()
        }
        
        # Check for profiles without rules
        all_profiles = profile_service.search_pricing_profiles(is_active=True, limit=1000)
        profiles_without_rules = []
        
        for profile in all_profiles['profiles']:
            try:
                analytics = profile_service.get_profile_analytics(UUID(profile.id))
                if analytics['rule_analytics']['total_rules'] == 0:
                    profiles_without_rules.append(profile.name)
            except:
                continue
        
        if profiles_without_rules:
            health_status["components"]["profiles"]["status"] = "warning"
            health_status["components"]["profiles"]["issues"].append(
                f"{len(profiles_without_rules)} active profiles have no rules assigned"
            )
            health_status["recommendations"].append(
                "Review profiles without rules and assign appropriate pricing rules"
            )
        
        # Check for unused rules
        try:
            unused_rules = []
            all_rules = rules_service.search_pricing_rules(is_active=True, limit=1000)
            
            for rule in all_rules['rules']:
                try:
                    usage = rules_service.check_rule_usage(UUID(rule.id))
                    if not usage['is_in_use']:
                        unused_rules.append(rule.name)
                except:
                    continue
            
            if unused_rules:
                health_status["components"]["rules"]["status"] = "warning"
                health_status["components"]["rules"]["issues"].append(
                    f"{len(unused_rules)} active rules are not being used"
                )
                health_status["recommendations"].append(
                    "Review unused rules and either assign them to profiles or deactivate them"
                )
        except Exception:
            pass
        
        # Determine overall status
        component_statuses = [comp["status"] for comp in health_status["components"].values()]
        if "error" in component_statuses:
            health_status["overall_status"] = "error"
        elif "warning" in component_statuses:
            health_status["overall_status"] = "warning"
        
        return create_response(
            data=health_status,
            message="System health check completed"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to check system health",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# PERFORMANCE ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/performance-metrics", response_model=Dict[str, Any])
async def get_performance_metrics(
    time_period_days: int = Query(30, ge=1, le=365, description="Time period for metrics"),
    profile_id: Optional[UUID] = Query(None, description="Specific profile for metrics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evaluation_service: RuleEvaluationService = Depends(get_evaluation_service)
):
    """
    Get performance metrics for rule evaluation system.
    
    - **time_period_days**: Time period for metrics (1-365 days)
    - **profile_id**: Optional specific profile for targeted metrics
    
    Returns comprehensive performance analytics and trends.
    """
    try:
        metrics = evaluation_service.get_evaluation_statistics(
            profile_id=profile_id,
            time_period_days=time_period_days
        )
        
        # Add computed metrics
        enhanced_metrics = {
            **metrics,
            "computed_metrics": {
                "success_rate_percentage": (
                    metrics["evaluation_metrics"]["successful_evaluations"] / 
                    max(metrics["evaluation_metrics"]["total_evaluations"], 1)
                ) * 100,
                "failure_rate_percentage": (
                    metrics["evaluation_metrics"]["failed_evaluations"] / 
                    max(metrics["evaluation_metrics"]["total_evaluations"], 1)
                ) * 100,
                "performance_grade": _calculate_performance_grade(metrics),
                "recommendations": _generate_performance_recommendations(metrics)
            }
        }
        
        return create_response(
            data=enhanced_metrics,
            message="Performance metrics retrieved successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to retrieve performance metrics",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/benchmark-profile/{profile_id}", response_model=Dict[str, Any])
async def benchmark_profile_performance(
    profile_id: UUID,
    test_scenarios: Optional[List[Dict[str, Any]]] = Body(None, description="Custom test scenarios"),
    iterations: int = Body(10, ge=1, le=100, description="Number of test iterations"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evaluation_service: RuleEvaluationService = Depends(get_evaluation_service)
):
    """
    Benchmark performance of a specific pricing profile.
    
    - **profile_id**: UUID of the profile to benchmark
    - **test_scenarios**: Optional custom test scenarios
    - **iterations**: Number of test iterations (1-100)
    
    Runs performance benchmarks and provides optimization recommendations.
    """
    try:
        # Generate test scenarios if not provided
        if not test_scenarios:
            test_scenarios = _generate_default_test_scenarios()
        
        benchmark_results = {
            "profile_id": str(profile_id),
            "test_configuration": {
                "scenarios_count": len(test_scenarios),
                "iterations": iterations,
                "total_tests": len(test_scenarios) * iterations
            },
            "performance_results": [],
            "summary_statistics": {},
            "recommendations": []
        }
        
        # Run benchmarks
        all_execution_times = []
        
        for i, scenario in enumerate(test_scenarios):
            scenario_times = []
            
            for iteration in range(iterations):
                start_time = datetime.utcnow()
                
                try:
                    # Evaluate the profile with scenario data
                    await evaluation_service.evaluate_profile_async(
                        profile_id=profile_id,
                        input_data=scenario,
                        evaluation_strategy="optimized",
                        use_cache=False  # Don't use cache for accurate timing
                    )
                    
                    execution_time = (datetime.utcnow() - start_time).total_seconds()
                    scenario_times.append(execution_time)
                    all_execution_times.append(execution_time)
                    
                except Exception as e:
                    # Record failed execution
                    scenario_times.append(None)
            
            # Calculate scenario statistics
            valid_times = [t for t in scenario_times if t is not None]
            if valid_times:
                scenario_result = {
                    "scenario_index": i,
                    "scenario_data": scenario,
                    "iterations_completed": len(valid_times),
                    "iterations_failed": len(scenario_times) - len(valid_times),
                    "avg_execution_time": sum(valid_times) / len(valid_times),
                    "min_execution_time": min(valid_times),
                    "max_execution_time": max(valid_times),
                    "success_rate": len(valid_times) / len(scenario_times) * 100
                }
                benchmark_results["performance_results"].append(scenario_result)
        
        # Calculate overall statistics
        if all_execution_times:
            benchmark_results["summary_statistics"] = {
                "total_successful_executions": len(all_execution_times),
                "overall_avg_time": sum(all_execution_times) / len(all_execution_times),
                "overall_min_time": min(all_execution_times),
                "overall_max_time": max(all_execution_times),
                "performance_variance": _calculate_variance(all_execution_times),
                "recommended_timeout": max(all_execution_times) * 1.5  # 50% buffer
            }
            
            # Generate recommendations
            avg_time = benchmark_results["summary_statistics"]["overall_avg_time"]
            if avg_time > 2.0:
                benchmark_results["recommendations"].append("Execution time exceeds 2 seconds - consider rule optimization")
            if avg_time > 5.0:
                benchmark_results["recommendations"].append("CRITICAL: Execution time exceeds 5 seconds - immediate optimization required")
            
            variance = benchmark_results["summary_statistics"]["performance_variance"]
            if variance > 1.0:
                benchmark_results["recommendations"].append("High performance variance detected - review rule complexity")
        
        benchmark_results["benchmark_completed_at"] = datetime.utcnow().isoformat()
        
        return create_response(
            data=benchmark_results,
            message="Profile performance benchmark completed"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to benchmark profile performance",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# REPORTING ENDPOINTS
# ============================================================================

@router.get("/usage-report", response_model=Dict[str, Any])
async def generate_usage_report(
    start_date: Optional[datetime] = Query(None, description="Start date for report"),
    end_date: Optional[datetime] = Query(None, description="End date for report"),
    include_details: bool = Query(False, description="Include detailed breakdowns"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_service: PricingProfileService = Depends(get_profile_service),
    rules_service: PricingRulesService = Depends(get_rules_service),
    profile_rule_repo: QuotationPricingProfileRuleRepository = Depends(get_profile_rule_repo)
):
    """
    Generate comprehensive usage report for pricing system.
    
    - **start_date**: Start date for report period
    - **end_date**: End date for report period  
    - **include_details**: Whether to include detailed breakdowns
    
    Returns detailed usage analytics and trends.
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get basic statistics
        profile_stats = profile_service.search_pricing_profiles(limit=10000)
        rule_stats = rules_service.search_pricing_rules(limit=10000)
        relationship_stats = profile_rule_repo.get_profile_statistics()
        
        usage_report = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "generated_by": str(current_user.id),
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "period_days": (end_date - start_date).days
                }
            },
            "executive_summary": {
                "total_profiles": len(profile_stats['profiles']),
                "total_rules": len(rule_stats['rules']),
                "active_profiles": len([p for p in profile_stats['profiles'] if p.is_active]),
                "active_rules": len([r for r in rule_stats['rules'] if r.is_active]),
                "total_rule_associations": relationship_stats.get('total_relationships', 0),
                "average_rules_per_profile": relationship_stats.get('average_rules_per_profile', 0)
            },
            "profile_analysis": {
                "by_insurance_type": _analyze_profiles_by_insurance_type(profile_stats['profiles']),
                "by_currency": _analyze_profiles_by_currency(profile_stats['profiles']),
                "activation_status": _analyze_profile_activation_status(profile_stats['profiles'])
            },
            "rule_analysis": {
                "by_impact_type": _analyze_rules_by_impact_type(rule_stats['rules']),
                "by_operator": _analyze_rules_by_operator(rule_stats['rules']),
                "usage_distribution": relationship_stats.get('most_used_rules', [])
            }
        }
        
        # Add detailed breakdowns if requested
        if include_details:
            usage_report["detailed_analysis"] = {
                "profile_details": [
                    {
                        "id": str(p.id),
                        "name": p.name,
                        "insurance_type": p.insurance_type,
                        "is_active": p.is_active,
                        "created_at": p.created_at.isoformat() if p.created_at else None
                    }
                    for p in profile_stats['profiles']
                ],
                "rule_details": [
                    {
                        "id": str(r.id),
                        "name": r.name,
                        "field_name": r.field_name,
                        "impact_type": r.impact_type,
                        "is_active": r.is_active,
                        "created_at": r.created_at.isoformat() if r.created_at else None
                    }
                    for r in rule_stats['rules']
                ]
            }
        
        return create_response(
            data=usage_report,
            message="Usage report generated successfully"
        )
        
    except Exception as e:
        return create_error_response(
            message="Failed to generate usage report",
            errors=[str(e)],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _calculate_performance_grade(metrics: Dict[str, Any]) -> str:
    """Calculate performance grade based on metrics."""
    try:
        avg_time = metrics["performance_metrics"]["average_evaluation_time"]
        success_rate = metrics["evaluation_metrics"]["successful_evaluations"] / max(
            metrics["evaluation_metrics"]["total_evaluations"], 1
        )
        
        if avg_time < 0.5 and success_rate > 0.95:
            return "A"
        elif avg_time < 1.0 and success_rate > 0.90:
            return "B"
        elif avg_time < 2.0 and success_rate > 0.85:
            return "C"
        elif avg_time < 5.0 and success_rate > 0.75:
            return "D"
        else:
            return "F"
    except:
        return "Unknown"


def _generate_performance_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Generate performance recommendations based on metrics."""
    recommendations = []
    
    try:
        avg_time = metrics["performance_metrics"]["average_evaluation_time"]
        cache_hit_rate = metrics["evaluation_metrics"]["cache_hit_rate"]
        
        if avg_time > 2.0:
            recommendations.append("Consider optimizing rule execution order to improve performance")
        
        if cache_hit_rate < 0.3:
            recommendations.append("Low cache hit rate - review caching strategy")
        
        if avg_time > 5.0:
            recommendations.append("CRITICAL: Execution times too high - immediate optimization required")
        
    except:
        recommendations.append("Unable to generate specific recommendations - review metrics manually")
    
    return recommendations


def _generate_default_test_scenarios() -> List[Dict[str, Any]]:
    """Generate default test scenarios for benchmarking."""
    return [
        {
            "age": 25,
            "base_premium": 1000.0,
            "sum_insured": 50000.0,
            "deductible": 500.0
        },
        {
            "age": 45,
            "base_premium": 1500.0,
            "sum_insured": 100000.0,
            "deductible": 1000.0
        },
        {
            "age": 65,
            "base_premium": 2000.0,
            "sum_insured": 75000.0,
            "deductible": 2000.0
        }
    ]


def _calculate_variance(values: List[float]) -> float:
    """Calculate variance of a list of values."""
    if not values:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance


def _analyze_profiles_by_insurance_type(profiles: List[Any]) -> Dict[str, int]:
    """Analyze profiles by insurance type."""
    analysis = {}
    for profile in profiles:
        insurance_type = profile.insurance_type or "Unknown"
        analysis[insurance_type] = analysis.get(insurance_type, 0) + 1
    return analysis


def _analyze_profiles_by_currency(profiles: List[Any]) -> Dict[str, int]:
    """Analyze profiles by currency."""
    analysis = {}
    for profile in profiles:
        currency = profile.currency or "Unknown"
        analysis[currency] = analysis.get(currency, 0) + 1
    return analysis


def _analyze_profile_activation_status(profiles: List[Any]) -> Dict[str, int]:
    """Analyze profile activation status."""
    return {
        "active": len([p for p in profiles if p.is_active]),
        "inactive": len([p for p in profiles if not p.is_active])
    }


def _analyze_rules_by_impact_type(rules: List[Any]) -> Dict[str, int]:
    """Analyze rules by impact type."""
    analysis = {}
    for rule in rules:
        impact_type = rule.impact_type or "Unknown"
        analysis[impact_type] = analysis.get(impact_type, 0) + 1
    return analysis


def _analyze_rules_by_operator(rules: List[Any]) -> Dict[str, int]:
    """Analyze rules by operator."""
    analysis = {}
    for rule in rules:
        operator = rule.operator or "Unknown"
        analysis[operator] = analysis.get(operator, 0) + 1
    return analysis