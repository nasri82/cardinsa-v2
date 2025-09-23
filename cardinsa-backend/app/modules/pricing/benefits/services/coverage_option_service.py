"""
app/modules/benefits/services/coverage_option_service.py

Service for managing coverage options and variants.
Handles tiers, add-ons, alternatives, and option combinations.
"""

from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from app.modules.pricing.benefits.repositories.coverage_option_repository import CoverageOptionRepository
from app.modules.pricing.benefits.models.coverage_option_model import CoverageOption, OptionType
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.core.base_service import BaseService
from app.core.logging import get_logger
from datetime import datetime
import itertools

logger = get_logger(__name__)


class CoverageOptionService(BaseService):
    """Service for managing coverage options and variants"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CoverageOptionRepository(db)
    
    async def create_coverage_option(self, option_data: Dict[str, Any]) -> CoverageOption:
        """Create coverage option with validation"""
        try:
            # Validate option data
            await self._validate_option_data(option_data)
            
            # Check compatibility with base coverage
            await self._validate_coverage_compatibility(option_data)
            
            # Set option defaults
            option_data = await self._set_option_defaults(option_data)
            
            # Create option
            coverage_option = CoverageOption(**option_data)
            created_option = await self.repository.create(coverage_option)
            
            logger.info(f"Created coverage option: {created_option.name}")
            return created_option
            
        except Exception as e:
            logger.error(f"Error creating coverage option: {str(e)}")
            raise
    
    async def get_available_option_combinations(self, coverage_id: str, 
                                              member_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get all valid option combinations for coverage"""
        try:
            # Get all options for coverage
            all_options = await self.repository.get_by_coverage(coverage_id)
            
            # Separate by option type
            tiers = [opt for opt in all_options if opt.option_type == OptionType.TIER]
            addons = [opt for opt in all_options if opt.option_type == OptionType.ADDON]
            alternatives = [opt for opt in all_options if opt.option_type == OptionType.ALTERNATIVE]
            
            # Get mandatory options
            mandatory_options = await self.repository.get_mandatory_options(coverage_id)
            
            # Generate valid combinations
            combinations = {
                'mandatory_options': mandatory_options,
                'tier_options': tiers,
                'available_addons': addons,
                'alternatives': alternatives,
                'valid_combinations': [],
                'recommended_combinations': []
            }
            
            # Generate all valid combinations
            combinations['valid_combinations'] = await self._generate_valid_combinations(
                tiers, addons, alternatives, mandatory_options
            )
            
            # Generate recommendations based on member profile
            if member_profile:
                combinations['recommended_combinations'] = await self._recommend_combinations(
                    combinations['valid_combinations'], member_profile
                )
            
            return combinations
            
        except Exception as e:
            logger.error(f"Error getting option combinations: {str(e)}")
            raise
    
    async def calculate_option_costs(self, option_ids: List[str], 
                                   base_premium: Decimal,
                                   member_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total costs for selected options"""
        try:
            cost_calculation = {
                'base_premium': base_premium,
                'option_costs': [],
                'total_additional_premium': Decimal('0'),
                'total_premium': base_premium,
                'cost_breakdown': [],
                'savings_opportunities': []
            }
            
            # Get option details
            for option_id in option_ids:
                option = await self.repository.get_by_id(option_id)
                if option:
                    # Calculate option-specific costs
                    option_cost = await self._calculate_individual_option_cost(
                        option, member_profile
                    )
                    
                    cost_calculation['option_costs'].append(option_cost)
                    cost_calculation['total_additional_premium'] += option_cost['premium_adjustment']
            
            cost_calculation['total_premium'] = (
                base_premium + cost_calculation['total_additional_premium']
            )
            
            # Build detailed breakdown
            cost_calculation['cost_breakdown'] = await self._build_option_cost_breakdown(
                cost_calculation['option_costs']
            )
            
            # Identify savings opportunities
            cost_calculation['savings_opportunities'] = await self._identify_savings_opportunities(
                option_ids, cost_calculation
            )
            
            return cost_calculation
            
        except Exception as e:
            logger.error(f"Error calculating option costs: {str(e)}")
            raise
    
    async def get_option_comparison_matrix(self, coverage_id: str) -> Dict[str, Any]:
        """Get comparison matrix for all coverage options"""
        try:
            options = await self.repository.get_by_coverage(coverage_id)
            
            comparison = {
                'coverage_id': coverage_id,
                'total_options': len(options),
                'comparison_matrix': {},
                'feature_comparison': {},
                'cost_comparison': {},
                'recommendation_scores': {}
            }
            
            # Build comparison matrix
            comparison['comparison_matrix'] = await self._build_comparison_matrix(options)
            
            # Feature comparison
            comparison['feature_comparison'] = await self._compare_option_features(options)
            
            # Cost comparison
            comparison['cost_comparison'] = await self._compare_option_costs(options)
            
            # Calculate recommendation scores
            comparison['recommendation_scores'] = await self._calculate_option_scores(options)
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error building comparison matrix: {str(e)}")
            raise
    
    async def optimize_option_selection(self, coverage_id: str, 
                                      budget_limit: Decimal,
                                      member_priorities: Dict[str, int]) -> Dict[str, Any]:
        """Optimize option selection based on budget and priorities"""
        try:
            available_options = await self.repository.get_by_coverage(coverage_id)
            mandatory_options = await self.repository.get_mandatory_options(coverage_id)
            
            optimization = {
                'budget_limit': budget_limit,
                'member_priorities': member_priorities,
                'mandatory_cost': Decimal('0'),
                'optimization_results': [],
                'recommended_selection': {},
                'budget_analysis': {}
            }
            
            # Calculate mandatory costs
            for mandatory_option in mandatory_options:
                optimization['mandatory_cost'] += mandatory_option.additional_premium or Decimal('0')
            
            # Check if budget covers mandatory options
            remaining_budget = budget_limit - optimization['mandatory_cost']
            if remaining_budget < 0:
                raise BusinessLogicError("Budget insufficient to cover mandatory options")
            
            # Run optimization algorithm
            optimal_selection = await self._run_option_optimization(
                available_options, remaining_budget, member_priorities
            )
            
            optimization['recommended_selection'] = optimal_selection
            optimization['budget_analysis'] = await self._analyze_budget_utilization(
                optimal_selection, budget_limit
            )
            
            return optimization
            
        except Exception as e:
            logger.error(f"Error optimizing option selection: {str(e)}")
            raise
    
    async def validate_option_combination(self, option_ids: List[str]) -> Dict[str, Any]:
        """Validate that option combination is valid"""
        try:
            validation_result = {
                'is_valid': True,
                'validation_errors': [],
                'warnings': [],
                'combination_details': {},
                'total_cost_impact': Decimal('0')
            }
            
            options = []
            for option_id in option_ids:
                option = await self.repository.get_by_id(option_id)
                if option:
                    options.append(option)
                else:
                    validation_result['validation_errors'].append(
                        f"Option {option_id} not found"
                    )
            
            # Validate combination rules
            validation_checks = [
                self._check_mutually_exclusive_options(options),
                self._check_required_dependencies(options),
                self._check_tier_compatibility(options),
                self._check_addon_limits(options)
            ]
            
            for check_result in validation_checks:
                check_data = await check_result
                if not check_data['passed']:
                    validation_result['is_valid'] = False
                    validation_result['validation_errors'].extend(check_data['errors'])
                
                if check_data.get('warnings'):
                    validation_result['warnings'].extend(check_data['warnings'])
            
            # Calculate total cost impact
            for option in options:
                validation_result['total_cost_impact'] += option.additional_premium or Decimal('0')
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating option combination: {str(e)}")
            raise
    
    async def get_option_analytics(self, coverage_id: str, 
                                 date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """Get analytics for coverage options"""
        try:
            analytics = {
                'coverage_id': coverage_id,
                'analysis_period': date_range,
                'option_popularity': {},
                'cost_analysis': {},
                'combination_trends': {},
                'performance_metrics': {}
            }
            
            options = await self.repository.get_by_coverage(coverage_id)
            
            # Analyze option popularity
            analytics['option_popularity'] = await self._analyze_option_popularity(options)
            
            # Cost analysis
            analytics['cost_analysis'] = await self._analyze_option_costs(options)
            
            # Combination trends
            analytics['combination_trends'] = await self._analyze_combination_trends(coverage_id)
            
            # Performance metrics
            analytics['performance_metrics'] = await self._calculate_option_performance_metrics(
                options, date_range
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating option analytics: {str(e)}")
            raise
    
    # Private helper methods
    async def _validate_option_data(self, data: Dict[str, Any]) -> None:
        """Validate coverage option data"""
        required_fields = ['name', 'coverage_id', 'option_type']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate option type
        if data['option_type'] not in [ot.value for ot in OptionType]:
            raise ValidationError(f"Invalid option type: {data['option_type']}")
    
    async def _validate_coverage_compatibility(self, data: Dict[str, Any]) -> None:
        """Validate option is compatible with base coverage"""
        # This would involve checking business rules for compatibility
        # Simplified for demonstration
        pass
    
    async def _set_option_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for coverage option"""
        defaults = {
            'is_active': True,
            'is_available': True,
            'is_mandatory': False,
            'additional_premium': Decimal('0'),
            'display_order': 10
        }
        
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        return data
    
    async def _generate_valid_combinations(self, tiers: List[CoverageOption],
                                         addons: List[CoverageOption],
                                         alternatives: List[CoverageOption],
                                         mandatory: List[CoverageOption]) -> List[Dict[str, Any]]:
        """Generate all valid option combinations"""
        combinations = []
        
        # Start with mandatory options
        base_combination = {
            'mandatory': [opt.id for opt in mandatory],
            'tier': None,
            'addons': [],
            'alternatives': [],
            'total_cost': sum(opt.additional_premium or Decimal('0') for opt in mandatory)
        }
        
        # Add tier options (can only select one tier)
        tier_combinations = []
        if tiers:
            for tier in tiers:
                if tier.is_available:
                    tier_combo = base_combination.copy()
                    tier_combo['tier'] = tier.id
                    tier_combo['total_cost'] += tier.additional_premium or Decimal('0')
                    tier_combinations.append(tier_combo)
        else:
            tier_combinations.append(base_combination)
        
        # Add addon combinations
        available_addons = [addon for addon in addons if addon.is_available]
        for tier_combo in tier_combinations:
            # Generate all possible addon combinations
            for r in range(len(available_addons) + 1):
                for addon_combination in itertools.combinations(available_addons, r):
                    combo = tier_combo.copy()
                    combo['addons'] = [addon.id for addon in addon_combination]
                    combo['total_cost'] += sum(addon.additional_premium or Decimal('0') 
                                             for addon in addon_combination)
                    
                    # Validate combination
                    if await self._is_valid_combination(combo):
                        combinations.append(combo)
        
        return combinations[:50]  # Limit to prevent explosion
    
    async def _recommend_combinations(self, valid_combinations: List[Dict[str, Any]],
                                    member_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend combinations based on member profile"""
        recommendations = []
        
        for combination in valid_combinations:
            score = await self._score_combination(combination, member_profile)
            if score > 60:  # Threshold for recommendation
                recommendations.append({
                    'combination': combination,
                    'recommendation_score': score,
                    'reasons': await self._get_combination_reasons(combination, member_profile)
                })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return recommendations[:5]
    
    async def _calculate_individual_option_cost(self, option: CoverageOption,
                                              member_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cost for individual option"""
        base_premium_adjustment = option.additional_premium or Decimal('0')
        
        # Apply member-specific adjustments
        adjusted_premium = await self._apply_member_adjustments(
            base_premium_adjustment, option, member_profile
        )
        
        return {
            'option_id': option.id,
            'option_name': option.name,
            'base_premium_adjustment': base_premium_adjustment,
            'premium_adjustment': adjusted_premium,
            'cost_factors': await self._get_cost_factors(option, member_profile)
        }
    
    async def _build_option_cost_breakdown(self, option_costs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build detailed cost breakdown"""
        breakdown = []
        
        for option_cost in option_costs:
            breakdown.append({
                'item': option_cost['option_name'],
                'base_cost': option_cost['base_premium_adjustment'],
                'adjusted_cost': option_cost['premium_adjustment'],
                'adjustment_factors': option_cost['cost_factors']
            })
        
        return breakdown
    
    async def _identify_savings_opportunities(self, option_ids: List[str],
                                            cost_calculation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential savings opportunities"""
        opportunities = []
        
        # Check for bundle discounts
        if len(option_ids) >= 3:
            opportunities.append({
                'type': 'bundle_discount',
                'description': 'Multiple option bundle discount available',
                'potential_savings': Decimal('50.00')  # Simplified
            })
        
        return opportunities
    
    async def _build_comparison_matrix(self, options: List[CoverageOption]) -> Dict[str, Any]:
        """Build option comparison matrix"""
        matrix = {
            'options': [],
            'features': ['premium_cost', 'option_type', 'availability', 'mandatory'],
            'data': []
        }
        
        for option in options:
            option_data = {
                'id': option.id,
                'name': option.name,
                'premium_cost': option.additional_premium or Decimal('0'),
                'option_type': option.option_type,
                'availability': option.is_available,
                'mandatory': option.is_mandatory
            }
            matrix['data'].append(option_data)
        
        return matrix
    
    async def _compare_option_features(self, options: List[CoverageOption]) -> Dict[str, Any]:
        """Compare features across options"""
        feature_comparison = {
            'total_options': len(options),
            'by_type': {},
            'cost_ranges': {},
            'availability_summary': {}
        }
        
        # Group by type
        for option in options:
            option_type = option.option_type
            if option_type not in feature_comparison['by_type']:
                feature_comparison['by_type'][option_type] = []
            feature_comparison['by_type'][option_type].append(option)
        
        return feature_comparison
    
    async def _compare_option_costs(self, options: List[CoverageOption]) -> Dict[str, Any]:
        """Compare costs across options"""
        costs = [opt.additional_premium or Decimal('0') for opt in options if opt.additional_premium]
        
        if not costs:
            return {'message': 'No cost data available'}
        
        return {
            'min_cost': min(costs),
            'max_cost': max(costs),
            'average_cost': sum(costs) / len(costs),
            'cost_distribution': await self._analyze_cost_distribution(costs)
        }
    
    async def _calculate_option_scores(self, options: List[CoverageOption]) -> Dict[str, Any]:
        """Calculate recommendation scores for options"""
        scores = {}
        
        for option in options:
            score = 50  # Base score
            
            # Adjust based on various factors
            if option.is_mandatory:
                score += 30
            if option.option_type == OptionType.TIER:
                score += 20
            if option.additional_premium and option.additional_premium < 100:
                score += 15
            
            scores[option.id] = min(100, score)
        
        return scores
    
    async def _run_option_optimization(self, options: List[CoverageOption],
                                     budget: Decimal,
                                     priorities: Dict[str, int]) -> Dict[str, Any]:
        """Run optimization algorithm for option selection"""
        # This would implement a knapsack-style optimization
        # Simplified version for demonstration
        
        # Sort options by value/cost ratio
        scored_options = []
        for option in options:
            if option.is_available and not option.is_mandatory:
                cost = option.additional_premium or Decimal('0')
                priority_score = priorities.get(option.option_type, 1)
                
                if cost > 0:
                    value_ratio = priority_score / float(cost)
                    scored_options.append({
                        'option': option,
                        'cost': cost,
                        'priority_score': priority_score,
                        'value_ratio': value_ratio
                    })
        
        # Sort by value ratio
        scored_options.sort(key=lambda x: x['value_ratio'], reverse=True)
        
        # Select options within budget
        selected_options = []
        total_cost = Decimal('0')
        
        for scored_option in scored_options:
            if total_cost + scored_option['cost'] <= budget:
                selected_options.append(scored_option['option'])
                total_cost += scored_option['cost']
        
        return {
            'selected_options': selected_options,
            'total_cost': total_cost,
            'remaining_budget': budget - total_cost,
            'optimization_score': len(selected_options) * 10  # Simplified score
        }
    
    async def _analyze_budget_utilization(self, selection: Dict[str, Any],
                                        budget_limit: Decimal) -> Dict[str, Any]:
        """Analyze budget utilization"""
        total_cost = selection['total_cost']
        
        return {
            'budget_limit': budget_limit,
            'total_cost': total_cost,
            'utilization_percentage': (total_cost / budget_limit) * 100,
            'remaining_budget': selection['remaining_budget'],
            'cost_efficiency': selection['optimization_score'] / float(total_cost) if total_cost > 0 else 0
        }
    
    async def _check_mutually_exclusive_options(self, options: List[CoverageOption]) -> Dict[str, Any]:
        """Check for mutually exclusive options"""
        # Simplified check - tiers are mutually exclusive
        tiers = [opt for opt in options if opt.option_type == OptionType.TIER]
        
        if len(tiers) > 1:
            return {
                'passed': False,
                'errors': ['Cannot select multiple tier options'],
                'warnings': []
            }
        
        return {'passed': True, 'errors': [], 'warnings': []}
    
    async def _check_required_dependencies(self, options: List[CoverageOption]) -> Dict[str, Any]:
        """Check for required option dependencies"""
        # This would implement complex dependency checking
        return {'passed': True, 'errors': [], 'warnings': []}
    
    async def _check_tier_compatibility(self, options: List[CoverageOption]) -> Dict[str, Any]:
        """Check tier compatibility with other options"""
        return {'passed': True, 'errors': [], 'warnings': []}
    
    async def _check_addon_limits(self, options: List[CoverageOption]) -> Dict[str, Any]:
        """Check addon selection limits"""
        addons = [opt for opt in options if opt.option_type == OptionType.ADDON]
        
        if len(addons) > 5:  # Example limit
            return {
                'passed': False,
                'errors': ['Cannot select more than 5 add-ons'],
                'warnings': []
            }
        
        return {'passed': True, 'errors': [], 'warnings': []}
    
    async def _is_valid_combination(self, combination: Dict[str, Any]) -> bool:
        """Check if option combination is valid"""
        # Simplified validation
        return True
    
    async def _score_combination(self, combination: Dict[str, Any], 
                               member_profile: Dict[str, Any]) -> int:
        """Score combination based on member profile"""
        score = 50  # Base score
        
        # Adjust based on member profile
        if 'age' in member_profile and member_profile['age'] > 50:
            if combination.get('tier'):  # Has comprehensive tier
                score += 20
        
        return min(100, score)
    
    async def _get_combination_reasons(self, combination: Dict[str, Any],
                                     member_profile: Dict[str, Any]) -> List[str]:
        """Get reasons for recommending combination"""
        reasons = []
        
        if combination.get('tier'):
            reasons.append("Includes comprehensive tier coverage")
        
        if len(combination.get('addons', [])) > 0:
            reasons.append("Includes valuable add-on benefits")
        
        return reasons
    
    async def _apply_member_adjustments(self, base_premium: Decimal,
                                      option: CoverageOption,
                                      member_profile: Dict[str, Any]) -> Decimal:
        """Apply member-specific premium adjustments"""
        adjusted_premium = base_premium
        
        # Example adjustments based on member profile
        if 'age' in member_profile:
            age = member_profile['age']
            if age > 50:
                adjusted_premium *= Decimal('1.1')  # 10% increase for older members
        
        return adjusted_premium
    
    async def _get_cost_factors(self, option: CoverageOption,
                              member_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get cost factors for option"""
        factors = []
        
        factors.append({
            'factor': 'base_premium',
            'multiplier': 1.0,
            'description': 'Base option premium'
        })
        
        if 'age' in member_profile and member_profile['age'] > 50:
            factors.append({
                'factor': 'age_adjustment',
                'multiplier': 1.1,
                'description': 'Age-based premium adjustment'
            })
        
        return factors
    
    async def _analyze_cost_distribution(self, costs: List[Decimal]) -> Dict[str, Any]:
        """Analyze cost distribution"""
        sorted_costs = sorted(costs)
        
        return {
            'low_cost_count': len([c for c in costs if c < 100]),
            'medium_cost_count': len([c for c in costs if 100 <= c < 500]),
            'high_cost_count': len([c for c in costs if c >= 500]),
            'median': sorted_costs[len(sorted_costs) // 2] if sorted_costs else Decimal('0')
        }
    
    async def _analyze_option_popularity(self, options: List[CoverageOption]) -> Dict[str, Any]:
        """Analyze option popularity"""
        # This would involve querying actual usage data
        return {
            'most_popular': options[0].id if options else None,
            'least_popular': options[-1].id if options else None,
            'popularity_trends': {}
        }
    
    async def _analyze_option_costs(self, options: List[CoverageOption]) -> Dict[str, Any]:
        """Analyze option costs"""
        costs = [opt.additional_premium or Decimal('0') for opt in options]
        
        return {
            'average_cost': sum(costs) / len(costs) if costs else Decimal('0'),
            'cost_variance': await self._calculate_variance(costs),
            'cost_trends': {}
        }
    
    async def _analyze_combination_trends(self, coverage_id: str) -> Dict[str, Any]:
        """Analyze combination selection trends"""
        # This would involve complex analytics on historical data
        return {
            'popular_combinations': [],
            'trending_options': [],
            'seasonal_patterns': {}
        }
    
    async def _calculate_option_performance_metrics(self, options: List[CoverageOption],
                                                   date_range: Optional[Tuple[datetime, datetime]]) -> Dict[str, Any]:
        """Calculate performance metrics for options"""
        return {
            'total_options': len(options),
            'active_options': len([opt for opt in options if opt.is_active]),
            'adoption_rates': {},
            'revenue_impact': {}
        }
    
    async def _calculate_variance(self, values: List[Decimal]) -> Decimal:
        """Calculate variance of values"""
        if not values:
            return Decimal('0')
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance