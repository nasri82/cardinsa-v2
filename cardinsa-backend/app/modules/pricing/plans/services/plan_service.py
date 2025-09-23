# app/modules/pricing/plans/services/plan_service.py

"""
Plan Service - Production Ready

Business logic layer for Plan management.
Handles complex operations, validations, and orchestration.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.modules.pricing.plans.repositories.plan_repository import PlanRepository
from app.modules.pricing.plans.models.plan_model import Plan, PlanStatus, PlanType
from app.modules.pricing.plans.schemas.plan_schema import (
    PlanCreate,
    PlanUpdate,
    PlanResponse,
    PlanDetailResponse,
    PlanSearchFilters,
    PlanComparisonRequest,
    PlanEligibilityCheck,
    PlanPricingRequest
)

# Import the function-based repository functions instead of class
from app.modules.pricing.product.repositories import product_catalog_repository
from app.core.exceptions import (
    BusinessLogicError,
    ValidationError,
    EntityNotFoundError,
    UnauthorizedError
)
import logging

logger = logging.getLogger(__name__)


class PlanService:
    """Service layer for Plan management"""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.repository = PlanRepository(db)
    
    # ================================================================
    # PLAN CREATION & MANAGEMENT
    # ================================================================
    
    def create_plan(
        self,
        plan_data: PlanCreate,
        created_by: UUID
    ) -> PlanResponse:
        """
        Create a new plan with validation
        
        Args:
            plan_data: Plan creation data
            created_by: User ID creating the plan
            
        Returns:
            Created plan response
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules violated
        """
        try:
            # Validate product exists and is active using function-based approach
            product = product_catalog_repository.get_product_catalog_by_id(
                self.db, plan_data.product_id
            )
            if not product:
                raise EntityNotFoundError(f"Product {plan_data.product_id} not found")
            
            if not product.is_active:
                raise BusinessLogicError("Cannot create plan for inactive product")
            
            # Validate plan code uniqueness
            existing = self.repository.get_by_code(
                plan_data.plan_code,
                plan_data.company_id
            )
            if existing:
                raise ValidationError(f"Plan code {plan_data.plan_code} already exists")
            
            # Validate business rules
            self._validate_plan_data(plan_data)
            
            # Check for default plan conflict
            if plan_data.is_default:
                self._handle_default_plan(plan_data.product_id, plan_data.company_id)
            
            # Create plan
            plan_dict = plan_data.dict(exclude_unset=True)
            plan = self.repository.create(plan_dict, created_by)
            
            logger.info(f"Plan created: {plan.id} by user {created_by}")
            
            return PlanResponse.from_orm(plan)
            
        except (EntityNotFoundError, ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}")
            raise BusinessLogicError(f"Failed to create plan: {str(e)}")
    
    def _validate_plan_data(self, plan_data: PlanCreate) -> None:
        """Validate plan data against business rules"""
        
        # Premium validation
        if plan_data.premium_amount < 0:
            raise ValidationError("Premium amount cannot be negative")
        
        # Age validation
        if plan_data.minimum_age and plan_data.maximum_issue_age:
            if plan_data.minimum_age > plan_data.maximum_issue_age:
                raise ValidationError("Minimum age cannot exceed maximum age")
        
        # Date validation
        if plan_data.effective_date and plan_data.expiry_date:
            if plan_data.effective_date >= plan_data.expiry_date:
                raise ValidationError("Effective date must be before expiry date")
        
        # Coverage period validation
        if plan_data.coverage_period_months <= 0:
            raise ValidationError("Coverage period must be positive")
        
        # Group size validation
        if plan_data.plan_type == PlanType.GROUP.value:
            if not plan_data.minimum_group_size:
                raise ValidationError("Group plans require minimum group size")
    
    def _handle_default_plan(self, product_id: UUID, company_id: UUID) -> None:
        """Handle default plan designation"""
        # Remove default from existing plans
        existing_defaults = self.db.query(Plan).filter(
            Plan.product_id == product_id,
            Plan.company_id == company_id,
            Plan.is_default == True,
            Plan.archived_at.is_(None)
        ).all()
        
        for plan in existing_defaults:
            plan.is_default = False
        
        self.db.commit()
    
    # ================================================================
    # PLAN RETRIEVAL & SEARCH
    # ================================================================
    
    def get_plan(
        self,
        plan_id: UUID,
        include_details: bool = False
    ) -> PlanResponse:
        """
        Get plan by ID
        
        Args:
            plan_id: Plan UUID
            include_details: Include related data
            
        Returns:
            Plan response
            
        Raises:
            EntityNotFoundError: If plan not found
        """
        plan = self.repository.get_by_id(plan_id, load_relationships=include_details)
        
        if not plan:
            raise EntityNotFoundError(f"Plan {plan_id} not found")
        
        if include_details:
            return PlanDetailResponse.from_orm(plan)
        
        return PlanResponse.from_orm(plan)
    
    def search_plans(
        self,
        filters: PlanSearchFilters,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Search plans with filters
        
        Args:
            filters: Search filters
            page: Page number
            page_size: Items per page
            
        Returns:
            Paginated search results
        """
        offset = (page - 1) * page_size
        
        # Convert filters to dict
        filter_dict = filters.dict(exclude_unset=True, exclude_none=True)
        
        # Execute search
        plans, total = self.repository.search(
            filter_dict,
            limit=page_size,
            offset=offset
        )
        
        # Build response
        return {
            'plans': [PlanResponse.from_orm(p) for p in plans],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }
    
    def get_active_plans(
        self,
        product_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None
    ) -> List[PlanResponse]:
        """
        Get active plans
        
        Args:
            product_id: Filter by product
            company_id: Filter by company
            
        Returns:
            List of active plans
        """
        plans = self.repository.get_active_plans(
            company_id=company_id,
            product_id=product_id
        )
        
        return [PlanResponse.from_orm(p) for p in plans]
    
    # ================================================================
    # PLAN UPDATE & LIFECYCLE
    # ================================================================
    
    def update_plan(
        self,
        plan_id: UUID,
        update_data: PlanUpdate,
        updated_by: UUID
    ) -> PlanResponse:
        """
        Update plan with validation
        
        Args:
            plan_id: Plan UUID
            update_data: Update data
            updated_by: User ID
            
        Returns:
            Updated plan response
            
        Raises:
            EntityNotFoundError: If plan not found
            ValidationError: If validation fails
        """
        # Get existing plan
        plan = self.repository.get_by_id(plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan {plan_id} not found")
        
        # Check if plan can be updated
        if plan.status == PlanStatus.DISCONTINUED.value:
            raise BusinessLogicError("Cannot update discontinued plan")
        
        # Validate update data
        update_dict = update_data.dict(exclude_unset=True, exclude_none=True)
        
        # Handle special updates
        if 'is_default' in update_dict and update_dict['is_default']:
            self._handle_default_plan(plan.product_id, plan.company_id)
        
        # Update plan
        updated_plan = self.repository.update(plan_id, update_dict, updated_by)
        
        if not updated_plan:
            raise BusinessLogicError("Failed to update plan")
        
        logger.info(f"Plan {plan_id} updated by user {updated_by}")
        
        return PlanResponse.from_orm(updated_plan)
    
    def activate_plan(
        self,
        plan_id: UUID,
        activated_by: UUID,
        effective_date: Optional[date] = None
    ) -> PlanResponse:
        """
        Activate a plan
        
        Args:
            plan_id: Plan UUID
            activated_by: User ID
            effective_date: Activation date
            
        Returns:
            Activated plan response
        """
        plan = self.repository.get_by_id(plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan {plan_id} not found")
        
        # Validate plan can be activated
        if plan.status not in [PlanStatus.DRAFT.value, PlanStatus.APPROVED.value]:
            raise BusinessLogicError(f"Cannot activate plan in {plan.status} status")
        
        # Check required fields
        if not plan.premium_amount or plan.premium_amount <= 0:
            raise ValidationError("Plan must have valid premium amount")
        
        # Update status
        updated_plan = self.repository.update_status(
            plan_id,
            PlanStatus.ACTIVE.value,
            activated_by,
            notes=f"Activated on {effective_date or date.today()}"
        )
        
        logger.info(f"Plan {plan_id} activated by user {activated_by}")
        
        return PlanResponse.from_orm(updated_plan)
    
    def suspend_plan(
        self,
        plan_id: UUID,
        suspended_by: UUID,
        reason: str,
        effective_date: Optional[date] = None
    ) -> PlanResponse:
        """
        Suspend a plan
        
        Args:
            plan_id: Plan UUID
            suspended_by: User ID
            reason: Suspension reason
            effective_date: Suspension date
            
        Returns:
            Suspended plan response
        """
        plan = self.repository.get_by_id(plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan {plan_id} not found")
        
        if plan.status != PlanStatus.ACTIVE.value:
            raise BusinessLogicError("Can only suspend active plans")
        
        # Update status
        updated_plan = self.repository.update_status(
            plan_id,
            PlanStatus.SUSPENDED.value,
            suspended_by,
            notes=f"Suspended: {reason}"
        )
        
        logger.warning(f"Plan {plan_id} suspended by user {suspended_by}: {reason}")
        
        return PlanResponse.from_orm(updated_plan)
    
    def discontinue_plan(
        self,
        plan_id: UUID,
        discontinued_by: UUID,
        reason: str,
        end_date: Optional[date] = None
    ) -> PlanResponse:
        """
        Discontinue a plan
        
        Args:
            plan_id: Plan UUID
            discontinued_by: User ID
            reason: Discontinuation reason
            end_date: End date
            
        Returns:
            Discontinued plan response
        """
        plan = self.repository.get_by_id(plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan {plan_id} not found")
        
        # Update status and end date
        update_data = {
            'status': PlanStatus.DISCONTINUED.value,
            'end_date': end_date or date.today(),
            'is_active': False
        }
        
        updated_plan = self.repository.update(
            plan_id,
            update_data,
            discontinued_by
        )
        
        logger.warning(f"Plan {plan_id} discontinued by user {discontinued_by}: {reason}")
        
        return PlanResponse.from_orm(updated_plan)
    
    # ================================================================
    # PLAN DELETION
    # ================================================================
    
    def delete_plan(
        self,
        plan_id: UUID,
        deleted_by: UUID,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete a plan
        
        Args:
            plan_id: Plan UUID
            deleted_by: User ID
            soft_delete: Use soft delete
            
        Returns:
            Success status
            
        Raises:
            BusinessLogicError: If plan has dependencies
        """
        plan = self.repository.get_by_id(plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan {plan_id} not found")
        
        # Check for active policies
        # TODO: Check if plan has active policies
        
        # Delete plan
        success = self.repository.delete(plan_id, soft_delete, deleted_by)
        
        if success:
            logger.info(f"Plan {plan_id} deleted by user {deleted_by}")
        
        return success
    
    # ================================================================
    # PLAN COMPARISON & ELIGIBILITY
    # ================================================================
    
    def compare_plans(
        self,
        comparison_request: PlanComparisonRequest
    ) -> Dict[str, Any]:
        """
        Compare multiple plans
        
        Args:
            comparison_request: Comparison request
            
        Returns:
            Comparison results
        """
        if len(comparison_request.plan_ids) < 2:
            raise ValidationError("At least 2 plans required for comparison")
        
        if len(comparison_request.plan_ids) > 5:
            raise ValidationError("Maximum 5 plans can be compared")
        
        # Get comparison data
        comparison_data = self.repository.compare_plans(comparison_request.plan_ids)
        
        # Add additional analysis
        for plan_data in comparison_data:
            plan_id = UUID(plan_data['id'])
            
            # Add value score (simplified)
            coverage_score = plan_data['coverage_count'] * 10
            benefit_score = plan_data['benefit_count'] * 5
            price_score = 10000 / plan_data['premium_amount'] if plan_data['premium_amount'] > 0 else 0
            
            plan_data['value_score'] = round(
                (coverage_score + benefit_score + price_score) / 3, 2
            )
        
        # Sort by value score
        comparison_data.sort(key=lambda x: x['value_score'], reverse=True)
        
        return {
            'plans': comparison_data,
            'recommendation': comparison_data[0] if comparison_data else None,
            'comparison_date': datetime.utcnow().isoformat()
        }
    
    def check_eligibility(
        self,
        plan_id: UUID,
        eligibility_check: PlanEligibilityCheck
    ) -> Dict[str, Any]:
        """
        Check eligibility for a plan
        
        Args:
            plan_id: Plan UUID
            eligibility_check: Eligibility data
            
        Returns:
            Eligibility results
        """
        plan = self.repository.get_by_id(plan_id, load_relationships=True)
        if not plan:
            raise EntityNotFoundError(f"Plan {plan_id} not found")
        
        results = {
            'plan_id': str(plan_id),
            'eligible': True,
            'reasons': [],
            'warnings': [],
            'requirements': []
        }
        
        # Check age eligibility
        if eligibility_check.age:
            if plan.minimum_age and eligibility_check.age < plan.minimum_age:
                results['eligible'] = False
                results['reasons'].append(f"Age {eligibility_check.age} below minimum {plan.minimum_age}")
            
            if plan.maximum_issue_age and eligibility_check.age > plan.maximum_issue_age:
                results['eligible'] = False
                results['reasons'].append(f"Age {eligibility_check.age} above maximum {plan.maximum_issue_age}")
        
        # Check group size for group plans
        if plan.plan_type == PlanType.GROUP.value:
            if eligibility_check.group_size:
                if plan.minimum_group_size and eligibility_check.group_size < plan.minimum_group_size:
                    results['eligible'] = False
                    results['reasons'].append(f"Group size below minimum {plan.minimum_group_size}")
            else:
                results['eligible'] = False
                results['reasons'].append("Group size required for group plans")
        
        # Check location eligibility
        if eligibility_check.location and plan.territories:
            territory_codes = [t.territory_code for t in plan.territories if t.is_active]
            if eligibility_check.location not in territory_codes:
                results['eligible'] = False
                results['reasons'].append(f"Location {eligibility_check.location} not covered")
        
        # Check pre-existing conditions
        if eligibility_check.pre_existing_conditions:
            for condition in eligibility_check.pre_existing_conditions:
                # Check if condition is excluded
                for exclusion in plan.exclusions:
                    if exclusion.exclusion_type == 'pre_existing':
                        results['warnings'].append(f"Pre-existing condition: {condition}")
                        if exclusion.exclusion_severity == 'absolute':
                            results['eligible'] = False
                            results['reasons'].append(f"Pre-existing condition not covered: {condition}")
        
        # Add waiting periods as requirements
        if plan.waiting_periods:
            for benefit, days in plan.waiting_periods.items():
                results['requirements'].append(f"{benefit}: {days} days waiting period")
        
        return results
    
    # ================================================================
    # PRICING OPERATIONS
    # ================================================================
    
    def calculate_premium(
        self,
        plan_id: UUID,
        pricing_request: PlanPricingRequest
    ) -> Dict[str, Any]:
        """
        Calculate premium for a plan
        
        Args:
            plan_id: Plan UUID
            pricing_request: Pricing request data
            
        Returns:
            Premium calculation results
        """
        plan = self.repository.get_by_id(plan_id, load_relationships=True)
        if not plan:
            raise EntityNotFoundError(f"Plan {plan_id} not found")
        
        # Base premium
        base_premium = Decimal(str(plan.premium_amount))
        adjustments = []
        
        # Age adjustment
        if pricing_request.age:
            age_factor = self._calculate_age_factor(
                pricing_request.age,
                plan.minimum_age,
                plan.maximum_issue_age
            )
            if age_factor != Decimal('1'):
                age_adjustment = base_premium * (age_factor - Decimal('1'))
                adjustments.append({
                    'type': 'age',
                    'factor': float(age_factor),
                    'amount': float(age_adjustment)
                })
                base_premium *= age_factor
        
        # Group discount
        if pricing_request.group_size and plan.plan_type == PlanType.GROUP.value:
            group_discount = self._calculate_group_discount(pricing_request.group_size)
            if group_discount > 0:
                discount_amount = base_premium * Decimal(str(group_discount))
                adjustments.append({
                    'type': 'group_discount',
                    'rate': group_discount,
                    'amount': float(discount_amount)
                })
                base_premium -= discount_amount
        
        # Territory adjustment
        if pricing_request.territory_code and plan.territories:
            for territory in plan.territories:
                if territory.territory_code == pricing_request.territory_code:
                    if territory.rate_adjustment:
                        territory_factor = Decimal('1') + (Decimal(str(territory.rate_adjustment)) / Decimal('100'))
                        territory_adjustment = base_premium * (territory_factor - Decimal('1'))
                        adjustments.append({
                            'type': 'territory',
                            'factor': float(territory_factor),
                            'amount': float(territory_adjustment)
                        })
                        base_premium *= territory_factor
                    break
        
        # Calculate totals
        final_premium = base_premium
        
        return {
            'plan_id': str(plan_id),
            'base_premium': float(plan.premium_amount),
            'adjustments': adjustments,
            'final_premium': float(final_premium),
            'currency': plan.currency,
            'coverage_period_months': plan.coverage_period_months,
            'calculation_date': datetime.utcnow().isoformat()
        }
    
    def _calculate_age_factor(
        self,
        age: int,
        min_age: Optional[int],
        max_age: Optional[int]
    ) -> Decimal:
        """Calculate age-based pricing factor"""
        if age < 25:
            return Decimal('0.8')
        elif age < 35:
            return Decimal('1.0')
        elif age < 45:
            return Decimal('1.2')
        elif age < 55:
            return Decimal('1.5')
        elif age < 65:
            return Decimal('2.0')
        else:
            return Decimal('2.5')
    
    def _calculate_group_discount(self, group_size: int) -> float:
        """Calculate group size discount"""
        if group_size >= 100:
            return 0.15  # 15% discount
        elif group_size >= 50:
            return 0.10  # 10% discount
        elif group_size >= 20:
            return 0.05  # 5% discount
        else:
            return 0.0
    
    # ================================================================
    # STATISTICS & ANALYTICS
    # ================================================================
    
    def get_plan_statistics(
        self,
        company_id: Optional[UUID] = None,
        product_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get plan statistics
        
        Args:
            company_id: Filter by company
            product_id: Filter by product
            
        Returns:
            Statistics dictionary
        """
        return self.repository.get_statistics(company_id, product_id)