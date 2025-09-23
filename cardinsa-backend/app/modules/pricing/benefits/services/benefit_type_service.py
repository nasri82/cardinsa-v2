"""
app/modules/benefits/services/benefit_type_service.py

Service for managing benefit types and cost-sharing structures.
Handles deductibles, copays, coinsurance, and benefit calculations.
"""

from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from app.modules.pricing.benefits.repositories.benefit_type_repository import BenefitTypeRepository
from app.modules.pricing.benefits.models.benefit_type_model import BenefitType, CoverageLevel
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.core.base_service import BaseService
from app.core.logging import get_logger
from datetime import datetime

logger = get_logger(__name__)


class BenefitTypeService(BaseService):
    """Service for managing benefit types and cost-sharing"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = BenefitTypeRepository(db)
    
    async def create_benefit_type(self, benefit_data: Dict[str, Any]) -> BenefitType:
        """Create benefit type with cost-sharing validation"""
        try:
            # Validate benefit type data
            await self._validate_benefit_type_data(benefit_data)
            
            # Validate cost-sharing structure
            await self._validate_cost_sharing(benefit_data)
            
            # Set defaults
            benefit_data = await self._set_benefit_defaults(benefit_data)
            
            # Create benefit type
            benefit_type = BenefitType(**benefit_data)
            created_benefit = await self.repository.create(benefit_type)
            
            logger.info(f"Created benefit type: {created_benefit.name}")
            return created_benefit
            
        except Exception as e:
            logger.error(f"Error creating benefit type: {str(e)}")
            raise
    
    async def calculate_member_cost(self, benefit_type_id: str, 
                                 service_amount: Decimal,
                                 member_context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate member cost based on benefit structure"""
        try:
            benefit_type = await self.repository.get_with_cost_sharing(benefit_type_id)
            if not benefit_type:
                raise NotFoundError(f"Benefit type {benefit_type_id} not found")
            
            # Initialize calculation result
            calculation = {
                'service_amount': service_amount,
                'member_cost': Decimal('0'),
                'insurance_cost': Decimal('0'),
                'deductible_applied': Decimal('0'),
                'copay_applied': Decimal('0'),
                'coinsurance_applied': Decimal('0'),
                'calculation_breakdown': []
            }
            
            # Get member's current deductible status
            remaining_deductible = await self._get_remaining_deductible(
                benefit_type, member_context
            )
            
            # Calculate costs step by step
            remaining_amount = service_amount
            
            # 1. Apply deductible first
            if remaining_deductible > 0 and benefit_type.deductible > 0:
                deductible_to_apply = min(remaining_amount, remaining_deductible)
                calculation['deductible_applied'] = deductible_to_apply
                calculation['member_cost'] += deductible_to_apply
                remaining_amount -= deductible_to_apply
                
                calculation['calculation_breakdown'].append({
                    'step': 'deductible',
                    'amount': deductible_to_apply,
                    'description': f"Deductible applied (${remaining_deductible} remaining)"
                })
            
            # 2. Apply copay (if applicable)
            if remaining_amount > 0 and benefit_type.copay > 0:
                copay_amount = benefit_type.copay
                calculation['copay_applied'] = copay_amount
                calculation['member_cost'] += copay_amount
                calculation['insurance_cost'] += max(Decimal('0'), remaining_amount - copay_amount)
                
                calculation['calculation_breakdown'].append({
                    'step': 'copay',
                    'amount': copay_amount,
                    'description': f"Fixed copay amount"
                })
            
            # 3. Apply coinsurance (if no copay)
            elif remaining_amount > 0 and benefit_type.coinsurance_percentage > 0:
                member_coinsurance = remaining_amount * (benefit_type.coinsurance_percentage / 100)
                insurance_coinsurance = remaining_amount - member_coinsurance
                
                calculation['coinsurance_applied'] = member_coinsurance
                calculation['member_cost'] += member_coinsurance
                calculation['insurance_cost'] += insurance_coinsurance
                
                calculation['calculation_breakdown'].append({
                    'step': 'coinsurance',
                    'amount': member_coinsurance,
                    'description': f"{benefit_type.coinsurance_percentage}% coinsurance"
                })
            
            # 4. Check out-of-pocket maximum
            calculation = await self._apply_out_of_pocket_max(
                calculation, benefit_type, member_context
            )
            
            # Round to currency precision
            calculation['member_cost'] = round(calculation['member_cost'], 2)
            calculation['insurance_cost'] = round(calculation['insurance_cost'], 2)
            
            return calculation
            
        except Exception as e:
            logger.error(f"Error calculating member cost: {str(e)}")
            raise
    
    async def get_benefit_type_comparison(self, benefit_type_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple benefit types side by side"""
        try:
            comparison = {
                'benefit_types': [],
                'comparison_matrix': {},
                'recommendations': []
            }
            
            for benefit_id in benefit_type_ids:
                benefit_type = await self.repository.get_with_cost_sharing(benefit_id)
                if benefit_type:
                    comparison['benefit_types'].append(benefit_type)
            
            # Build comparison matrix
            comparison['comparison_matrix'] = await self._build_comparison_matrix(
                comparison['benefit_types']
            )
            
            # Generate recommendations
            comparison['recommendations'] = await self._generate_benefit_recommendations(
                comparison['benefit_types']
            )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing benefit types: {str(e)}")
            raise
    
    async def estimate_annual_costs(self, benefit_type_id: str, 
                                  usage_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate annual costs based on usage scenarios"""
        try:
            benefit_type = await self.repository.get_with_cost_sharing(benefit_type_id)
            if not benefit_type:
                raise NotFoundError(f"Benefit type {benefit_type_id} not found")
            
            estimates = {
                'benefit_type': benefit_type,
                'scenarios': [],
                'annual_summary': {}
            }
            
            total_member_cost = Decimal('0')
            total_insurance_cost = Decimal('0')
            
            for scenario in usage_scenarios:
                scenario_cost = await self.calculate_member_cost(
                    benefit_type_id,
                    scenario['service_amount'],
                    scenario.get('member_context', {})
                )
                
                # Multiply by frequency
                frequency = scenario.get('annual_frequency', 1)
                annual_member_cost = scenario_cost['member_cost'] * frequency
                annual_insurance_cost = scenario_cost['insurance_cost'] * frequency
                
                scenario_result = {
                    'scenario_name': scenario.get('name', 'Unnamed scenario'),
                    'service_amount': scenario['service_amount'],
                    'frequency': frequency,
                    'per_service_member_cost': scenario_cost['member_cost'],
                    'annual_member_cost': annual_member_cost,
                    'annual_insurance_cost': annual_insurance_cost
                }
                
                estimates['scenarios'].append(scenario_result)
                total_member_cost += annual_member_cost
                total_insurance_cost += annual_insurance_cost
            
            estimates['annual_summary'] = {
                'total_member_cost': total_member_cost,
                'total_insurance_cost': total_insurance_cost,
                'total_cost': total_member_cost + total_insurance_cost,
                'member_cost_percentage': (total_member_cost / (total_member_cost + total_insurance_cost)) * 100
            }
            
            return estimates
            
        except Exception as e:
            logger.error(f"Error estimating annual costs: {str(e)}")
            raise
    
    async def get_preventive_benefits_summary(self) -> Dict[str, Any]:
        """Get summary of all preventive benefits"""
        try:
            preventive_benefits = await self.repository.get_preventive_benefits()
            
            summary = {
                'total_count': len(preventive_benefits),
                'by_category': {},
                'benefits': [],
                'coverage_highlights': []
            }
            
            # Group by category
            for benefit in preventive_benefits:
                category_name = benefit.category.name if benefit.category else 'Uncategorized'
                if category_name not in summary['by_category']:
                    summary['by_category'][category_name] = []
                summary['by_category'][category_name].append(benefit)
            
            # Add coverage highlights for marketing
            summary['coverage_highlights'] = [
                "100% coverage for preventive care",
                "No deductible required",
                "Annual wellness visits included",
                "Preventive screenings covered"
            ]
            
            summary['benefits'] = preventive_benefits
            return summary
            
        except Exception as e:
            logger.error(f"Error getting preventive benefits summary: {str(e)}")
            raise
    
    # Private helper methods
    async def _validate_benefit_type_data(self, data: Dict[str, Any]) -> None:
        """Validate benefit type data"""
        required_fields = ['name', 'category_id', 'coverage_level']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate coverage level
        if data['coverage_level'] not in [cl.value for cl in CoverageLevel]:
            raise ValidationError(f"Invalid coverage level: {data['coverage_level']}")
    
    async def _validate_cost_sharing(self, data: Dict[str, Any]) -> None:
        """Validate cost-sharing structure makes business sense"""
        # Can't have both copay and coinsurance
        if data.get('copay', 0) > 0 and data.get('coinsurance_percentage', 0) > 0:
            raise ValidationError("Cannot have both copay and coinsurance")
        
        # Validate percentage ranges
        if 'coinsurance_percentage' in data:
            percentage = data['coinsurance_percentage']
            if percentage < 0 or percentage > 100:
                raise ValidationError("Coinsurance percentage must be between 0 and 100")
    
    async def _set_benefit_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for benefit type"""
        defaults = {
            'is_active': True,
            'is_preventive': False,
            'requires_referral': False,
            'deductible': Decimal('0'),
            'copay': Decimal('0'),
            'coinsurance_percentage': Decimal('0'),
            'out_of_pocket_max': None,
            'display_order': 10
        }
        
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        return data
    
    async def _get_remaining_deductible(self, benefit_type: BenefitType, 
                                      member_context: Dict[str, Any]) -> Decimal:
        """Get member's remaining deductible amount"""
        # This would integrate with claims/usage tracking system
        # Simplified version for demonstration
        annual_deductible = benefit_type.deductible
        used_deductible = Decimal(member_context.get('used_deductible', '0'))
        
        return max(Decimal('0'), annual_deductible - used_deductible)
    
    async def _apply_out_of_pocket_max(self, calculation: Dict[str, Any],
                                     benefit_type: BenefitType,
                                     member_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply out-of-pocket maximum protection"""
        if not benefit_type.out_of_pocket_max:
            return calculation
        
        # Get current year's out-of-pocket spending
        current_oop_spending = Decimal(member_context.get('current_oop_spending', '0'))
        remaining_oop_limit = max(Decimal('0'), benefit_type.out_of_pocket_max - current_oop_spending)
        
        # Reduce member cost if it would exceed OOP max
        if calculation['member_cost'] > remaining_oop_limit:
            oop_savings = calculation['member_cost'] - remaining_oop_limit
            calculation['member_cost'] = remaining_oop_limit
            calculation['insurance_cost'] += oop_savings
            
            calculation['calculation_breakdown'].append({
                'step': 'out_of_pocket_max',
                'amount': -oop_savings,
                'description': f"Out-of-pocket maximum protection applied"
            })
        
        return calculation
    
    async def _build_comparison_matrix(self, benefit_types: List[BenefitType]) -> Dict[str, Any]:
        """Build comparison matrix for benefit types"""
        matrix = {
            'deductibles': [],
            'copays': [],
            'coinsurance': [],
            'out_of_pocket_max': [],
            'preventive_coverage': []
        }
        
        for bt in benefit_types:
            matrix['deductibles'].append({
                'benefit_id': bt.id,
                'name': bt.name,
                'value': bt.deductible
            })
            matrix['copays'].append({
                'benefit_id': bt.id,
                'name': bt.name,
                'value': bt.copay
            })
            # Add other comparisons...
        
        return matrix
    
    async def _generate_benefit_recommendations(self, benefit_types: List[BenefitType]) -> List[Dict[str, Any]]:
        """Generate recommendations based on benefit comparison"""
        recommendations = []
        
        # Find lowest cost options
        if benefit_types:
            lowest_deductible = min(benefit_types, key=lambda bt: bt.deductible)
            recommendations.append({
                'type': 'lowest_deductible',
                'benefit_id': lowest_deductible.id,
                'message': f"{lowest_deductible.name} has the lowest deductible at ${lowest_deductible.deductible}"
            })
        
        return recommendations