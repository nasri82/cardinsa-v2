"""
app/modules/benefits/services/coverage_service.py

Service for managing insurance coverage plans.
Handles coverage validation, eligibility, and plan management.
"""

from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from app.modules.pricing.benefits.repositories.coverage_repository import CoverageRepository
from app.modules.pricing.benefits.models.coverage_model import Coverage, CoverageType
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.core.base_service import BaseService
from app.core.logging import get_logger
from datetime import datetime, date, timedelta

logger = get_logger(__name__)


class CoverageService(BaseService):
    """Service for managing insurance coverage"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CoverageRepository(db)
    
    async def create_coverage_plan(self, coverage_data: Dict[str, Any]) -> Coverage:
        """Create new coverage plan with validation"""
        try:
            # Validate coverage data
            await self._validate_coverage_data(coverage_data)
            
            # Set effective dates
            coverage_data = await self._set_coverage_dates(coverage_data)
            
            # Validate network compatibility
            await self._validate_network_compatibility(coverage_data)
            
            # Create coverage
            coverage = Coverage(**coverage_data)
            created_coverage = await self.repository.create(coverage)
            
            logger.info(f"Created coverage plan: {created_coverage.name}")
            return created_coverage
            
        except Exception as e:
            logger.error(f"Error creating coverage plan: {str(e)}")
            raise
    
    async def check_member_eligibility(self, coverage_id: str, 
                                     member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if member is eligible for coverage"""
        try:
            coverage = await self.repository.get_by_id(coverage_id)
            if not coverage:
                raise NotFoundError(f"Coverage {coverage_id} not found")
            
            eligibility_result = {
                'eligible': True,
                'coverage': coverage,
                'eligibility_details': {},
                'restrictions': [],
                'waiting_periods': []
            }
            
            # Check basic eligibility criteria
            eligibility_checks = [
                self._check_age_eligibility(coverage, member_data),
                self._check_coverage_period(coverage, member_data),
                self._check_geographic_eligibility(coverage, member_data),
                self._check_enrollment_period(coverage, member_data)
            ]
            
            for check_result in eligibility_checks:
                check_data = await check_result
                if not check_data['passed']:
                    eligibility_result['eligible'] = False
                    eligibility_result['restrictions'].append(check_data)
                else:
                    eligibility_result['eligibility_details'][check_data['check_type']] = check_data
            
            return eligibility_result
            
        except Exception as e:
            logger.error(f"Error checking member eligibility: {str(e)}")
            raise
    
    async def get_coverage_options_for_member(self, member_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get available coverage options based on member profile"""
        try:
            # Get all active coverages
            all_coverages = await self.repository.get_active_coverages()
            
            options = {
                'available_coverages': [],
                'recommended_coverages': [],
                'member_profile': member_profile,
                'filtering_criteria': {}
            }
            
            # Filter coverages based on member profile
            for coverage in all_coverages:
                eligibility = await self.check_member_eligibility(coverage.id, member_profile)
                
                if eligibility['eligible']:
                    options['available_coverages'].append({
                        'coverage': coverage,
                        'eligibility_details': eligibility['eligibility_details']
                    })
            
            # Generate recommendations
            options['recommended_coverages'] = await self._generate_coverage_recommendations(
                options['available_coverages'], member_profile
            )
            
            return options
            
        except Exception as e:
            logger.error(f"Error getting coverage options: {str(e)}")
            raise
    
    async def calculate_coverage_costs(self, coverage_id: str, 
                                     member_profile: Dict[str, Any],
                                     usage_scenarios: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Calculate total coverage costs including premiums and out-of-pocket"""
        try:
            coverage = await self.repository.get_coverage_with_options(coverage_id)
            if not coverage:
                raise NotFoundError(f"Coverage {coverage_id} not found")
            
            cost_calculation = {
                'coverage': coverage,
                'premium_costs': {},
                'estimated_out_of_pocket': {},
                'total_estimated_annual_cost': Decimal('0'),
                'cost_breakdown': []
            }
            
            # Calculate premium costs
            premium_costs = await self._calculate_premium_costs(coverage, member_profile)
            cost_calculation['premium_costs'] = premium_costs
            cost_calculation['total_estimated_annual_cost'] += premium_costs['annual_premium']
            
            # Calculate estimated out-of-pocket costs
            if usage_scenarios:
                oop_costs = await self._calculate_estimated_oop_costs(
                    coverage, member_profile, usage_scenarios
                )
                cost_calculation['estimated_out_of_pocket'] = oop_costs
                cost_calculation['total_estimated_annual_cost'] += oop_costs['estimated_annual_oop']
            
            # Build detailed cost breakdown
            cost_calculation['cost_breakdown'] = await self._build_cost_breakdown(
                premium_costs, cost_calculation.get('estimated_out_of_pocket', {})
            )
            
            return cost_calculation
            
        except Exception as e:
            logger.error(f"Error calculating coverage costs: {str(e)}")
            raise
    
    async def get_coverage_network_details(self, coverage_id: str) -> Dict[str, Any]:
        """Get detailed network information for coverage"""
        try:
            coverage = await self.repository.get_by_id(coverage_id)
            if not coverage:
                raise NotFoundError(f"Coverage {coverage_id} not found")
            
            network_details = {
                'coverage': coverage,
                'network_info': {},
                'provider_counts': {},
                'geographic_coverage': {},
                'restrictions': []
            }
            
            if coverage.network_id:
                # This would integrate with provider network service
                network_details['network_info'] = await self._get_network_information(coverage.network_id)
                network_details['provider_counts'] = await self._get_provider_counts(coverage.network_id)
                network_details['geographic_coverage'] = await self._get_geographic_coverage(coverage.network_id)
            
            return network_details
            
        except Exception as e:
            logger.error(f"Error getting network details: {str(e)}")
            raise
    
    async def renew_coverage(self, coverage_id: str, renewal_data: Dict[str, Any]) -> Coverage:
        """Renew existing coverage for new term"""
        try:
            current_coverage = await self.repository.get_by_id(coverage_id)
            if not current_coverage:
                raise NotFoundError(f"Coverage {coverage_id} not found")
            
            # Validate renewal eligibility
            await self._validate_renewal_eligibility(current_coverage, renewal_data)
            
            # Create renewal coverage
            renewal_coverage_data = await self._prepare_renewal_data(current_coverage, renewal_data)
            renewal_coverage = Coverage(**renewal_coverage_data)
            
            # Set termination date on current coverage
            if 'new_effective_date' in renewal_data:
                current_coverage.termination_date = renewal_data['new_effective_date'] - timedelta(days=1)
                await self.repository.update(current_coverage)
            
            # Create new coverage
            new_coverage = await self.repository.create(renewal_coverage)
            
            logger.info(f"Renewed coverage: {current_coverage.name} -> {new_coverage.id}")
            return new_coverage
            
        except Exception as e:
            logger.error(f"Error renewing coverage: {str(e)}")
            raise
    
    async def get_expiring_coverages_report(self, days_ahead: int = 60) -> Dict[str, Any]:
        """Get report of coverages expiring soon"""
        try:
            expiring_coverages = await self.repository.get_expiring_coverages(days_ahead)
            
            report = {
                'total_expiring': len(expiring_coverages),
                'days_ahead': days_ahead,
                'coverages_by_month': {},
                'action_required': [],
                'renewal_candidates': []
            }
            
            # Group by expiration month
            for coverage in expiring_coverages:
                if coverage.termination_date:
                    month_key = coverage.termination_date.strftime('%Y-%m')
                    if month_key not in report['coverages_by_month']:
                        report['coverages_by_month'][month_key] = []
                    report['coverages_by_month'][month_key].append(coverage)
                    
                    # Determine action needed
                    days_until_expiry = (coverage.termination_date - date.today()).days
                    if days_until_expiry <= 30:
                        report['action_required'].append({
                            'coverage': coverage,
                            'days_remaining': days_until_expiry,
                            'urgency': 'high' if days_until_expiry <= 10 else 'medium'
                        })
                    else:
                        report['renewal_candidates'].append(coverage)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating expiring coverages report: {str(e)}")
            raise
    
    # Private helper methods
    async def _validate_coverage_data(self, data: Dict[str, Any]) -> None:
        """Validate coverage data"""
        required_fields = ['name', 'coverage_type', 'effective_date']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate coverage type
        if data['coverage_type'] not in [ct.value for ct in CoverageType]:
            raise ValidationError(f"Invalid coverage type: {data['coverage_type']}")
    
    async def _set_coverage_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Set and validate coverage effective dates"""
        if isinstance(data['effective_date'], str):
            data['effective_date'] = datetime.fromisoformat(data['effective_date']).date()
        
        # Set default termination date if not provided (1 year from effective)
        if 'termination_date' not in data or not data['termination_date']:
            data['termination_date'] = data['effective_date'].replace(
                year=data['effective_date'].year + 1
            )
        
        return data
    
    async def _validate_network_compatibility(self, data: Dict[str, Any]) -> None:
        """Validate network is compatible with coverage type"""
        # This would involve checking network service
        # Simplified validation for demonstration
        pass
    
    async def _check_age_eligibility(self, coverage: Coverage, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check age eligibility for coverage"""
        return {
            'check_type': 'age_eligibility',
            'passed': True,  # Simplified - would check actual age requirements
            'details': 'Age requirements met',
            'member_age': member_data.get('age', 0)
        }
    
    async def _check_coverage_period(self, coverage: Coverage, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if coverage is currently active"""
        today = date.today()
        is_active = (coverage.effective_date <= today and 
                    (not coverage.termination_date or coverage.termination_date > today))
        
        return {
            'check_type': 'coverage_period',
            'passed': is_active,
            'details': 'Coverage period active' if is_active else 'Coverage period inactive',
            'effective_date': coverage.effective_date,
            'termination_date': coverage.termination_date
        }
    
    async def _check_geographic_eligibility(self, coverage: Coverage, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check geographic eligibility"""
        # This would involve checking service area
        return {
            'check_type': 'geographic_eligibility',
            'passed': True,  # Simplified
            'details': 'Service area requirements met'
        }
    
    async def _check_enrollment_period(self, coverage: Coverage, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if enrollment period is open"""
        return {
            'check_type': 'enrollment_period',
            'passed': True,  # Simplified - would check actual enrollment windows
            'details': 'Enrollment period open'
        }
    
    async def _generate_coverage_recommendations(self, available_coverages: List[Dict[str, Any]],
                                               member_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized coverage recommendations"""
        recommendations = []
        
        # Simple recommendation logic - can be enhanced with ML
        for coverage_option in available_coverages:
            coverage = coverage_option['coverage']
            score = await self._calculate_recommendation_score(coverage, member_profile)
            
            if score > 70:  # Threshold for recommendation
                recommendations.append({
                    'coverage': coverage,
                    'recommendation_score': score,
                    'reasons': await self._get_recommendation_reasons(coverage, member_profile)
                })
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return recommendations[:3]  # Top 3 recommendations
    
    async def _calculate_recommendation_score(self, coverage: Coverage, member_profile: Dict[str, Any]) -> int:
        """Calculate recommendation score for coverage"""
        score = 50  # Base score
        
        # Add scoring logic based on member profile
        if member_profile.get('age', 0) > 50 and coverage.coverage_type == CoverageType.COMPREHENSIVE:
            score += 20
        
        if member_profile.get('family_size', 1) > 2 and coverage.coverage_type == CoverageType.FAMILY:
            score += 15
        
        return min(100, score)
    
    async def _get_recommendation_reasons(self, coverage: Coverage, member_profile: Dict[str, Any]) -> List[str]:
        """Get reasons for recommending this coverage"""
        reasons = []
        
        if coverage.coverage_type == CoverageType.COMPREHENSIVE:
            reasons.append("Comprehensive coverage for all medical needs")
        
        if coverage.max_out_of_pocket and coverage.max_out_of_pocket < 10000:
            reasons.append("Low out-of-pocket maximum provides financial protection")
        
        return reasons
    
    async def _calculate_premium_costs(self, coverage: Coverage, member_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate premium costs for coverage"""
        # This would involve complex rating algorithms
        base_premium = Decimal('500.00')  # Simplified base premium
        
        return {
            'monthly_premium': base_premium,
            'annual_premium': base_premium * 12,
            'premium_factors': {
                'base_rate': base_premium,
                'age_factor': Decimal('1.0'),
                'family_factor': Decimal('1.0'),
                'geographic_factor': Decimal('1.0')
            }
        }
    
    async def _calculate_estimated_oop_costs(self, coverage: Coverage, 
                                           member_profile: Dict[str, Any],
                                           usage_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate estimated out-of-pocket costs"""
        # This would involve complex utilization modeling
        estimated_annual_oop = Decimal('2000.00')  # Simplified
        
        return {
            'estimated_annual_oop': estimated_annual_oop,
            'scenario_costs': [],
            'cost_categories': {
                'doctor_visits': Decimal('500.00'),
                'prescriptions': Decimal('800.00'),
                'emergency_care': Decimal('700.00')
            }
        }
    
    async def _build_cost_breakdown(self, premium_costs: Dict[str, Any],
                                   oop_costs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build detailed cost breakdown"""
        breakdown = []
        
        breakdown.append({
            'category': 'Monthly Premium',
            'amount': premium_costs.get('monthly_premium', 0),
            'annual_amount': premium_costs.get('annual_premium', 0),
            'description': 'Fixed monthly insurance premium'
        })
        
        if oop_costs:
            breakdown.append({
                'category': 'Estimated Out-of-Pocket',
                'amount': oop_costs.get('estimated_annual_oop', 0) / 12,
                'annual_amount': oop_costs.get('estimated_annual_oop', 0),
                'description': 'Estimated annual out-of-pocket costs'
            })
        
        return breakdown
    
    async def _get_network_information(self, network_id: str) -> Dict[str, Any]:
        """Get network information from network service"""
        # This would call external network service
        return {
            'network_id': network_id,
            'network_name': 'Sample Network',
            'network_type': 'PPO',
            'coverage_area': 'National'
        }
    
    async def _get_provider_counts(self, network_id: str) -> Dict[str, Any]:
        """Get provider counts for network"""
        return {
            'primary_care': 1500,
            'specialists': 3000,
            'hospitals': 50,
            'urgent_care': 200
        }
    
    async def _get_geographic_coverage(self, network_id: str) -> Dict[str, Any]:
        """Get geographic coverage for network"""
        return {
            'states_covered': ['CA', 'NY', 'TX', 'FL'],
            'metro_areas': 25,
            'rural_coverage': True
        }
    
    async def _validate_renewal_eligibility(self, coverage: Coverage, renewal_data: Dict[str, Any]) -> None:
        """Validate coverage can be renewed"""
        if not coverage.is_active:
            raise BusinessLogicError("Cannot renew inactive coverage")
        
        if coverage.termination_date and coverage.termination_date < date.today():
            raise BusinessLogicError("Cannot renew expired coverage")
    
    async def _prepare_renewal_data(self, current_coverage: Coverage, 
                                   renewal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for renewal coverage"""
        renewal_coverage_data = {
            'name': f"{current_coverage.name} (Renewal)",
            'coverage_type': current_coverage.coverage_type,
            'network_id': current_coverage.network_id,
            'effective_date': renewal_data.get('new_effective_date', date.today()),
            'is_active': True,
            'max_out_of_pocket': current_coverage.max_out_of_pocket,
            'deductible': renewal_data.get('new_deductible', current_coverage.deductible)
        }
        
        # Set new termination date (1 year from new effective date)
        renewal_coverage_data['termination_date'] = renewal_coverage_data['effective_date'].replace(
            year=renewal_coverage_data['effective_date'].year + 1
        )
        
        return renewal_coverage_data
