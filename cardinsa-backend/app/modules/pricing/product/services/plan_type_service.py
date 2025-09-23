# app/modules/pricing/product/services/plan_type_service.py

"""
Plan Type Service

Business logic layer for Plan Type management.
Handles plan configuration, comparison, and eligibility.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.modules.pricing.product.repositories import plan_type_repository as repo
from app.modules.pricing.product.repositories import product_catalog_repository as product_repo
from app.modules.pricing.product.repositories import product_feature_repository as feature_repo
from app.modules.pricing.product.schemas.plan_type_schema import (
    PlanTypeCreate,
    PlanTypeUpdate,
    PlanTypeFilter,
    PlanTypeResponse,
    PlanTypeListResponse,
    PlanComparison,
    PlanComparisonResponse,
    PlanEligibilityRequest,
    PlanEligibilityResponse,
    PlanStatus,
    PlanTier,
    PlanCategory,
    NetworkType
)
from app.core.database import get_db
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Define custom exceptions
class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class ConflictException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ================================================================
# PLAN CREATION & MANAGEMENT
# ================================================================

def create_plan_with_validation(
    db: Session,
    plan_data: PlanTypeCreate,
    created_by: Optional[UUID] = None
) -> PlanTypeResponse:
    """
    Create a new plan type with comprehensive validation
    
    Args:
        db: Database session
        plan_data: Plan creation data
        created_by: User ID creating the plan
        
    Returns:
        Created plan response
        
    Raises:
        ValidationException: If validation fails
        ConflictException: If plan code exists
    """
    try:
        # Verify product exists
        product = product_repo.get_product_catalog_by_id(db, plan_data.product_id)
        if not product:
            raise NotFoundException(
                f"Product with ID {plan_data.product_id} not found"
            )
        
        # Validate plan data
        _validate_plan_data(plan_data, product)
        
        # Check for duplicate plan code
        existing = repo.get_plan_by_code(
            db, plan_data.product_id, plan_data.plan_code
        )
        if existing:
            raise ConflictException(
                f"Plan with code '{plan_data.plan_code}' "
                f"already exists for this product"
            )
        
        # Create the plan
        plan = repo.create_plan_type(db, plan_data, created_by)
        
        logger.info(
            f"Plan created: {plan.id} - {plan.plan_name} "
            f"for product {plan_data.product_id} by user {created_by}"
        )
        
        return PlanTypeResponse.model_validate(plan)
        
    except (ConflictException, ValidationException, NotFoundException) as e:
        logger.warning(f"Plan creation validation failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating plan: {str(e)}")
        raise BadRequestException(f"Failed to create plan: {str(e)}")


def _validate_plan_data(plan_data: PlanTypeCreate, product: Any) -> None:
    """
    Validate plan data against product configuration
    
    Args:
        plan_data: Plan data to validate
        product: Parent product
        
    Raises:
        ValidationException: If validation fails
    """
    # Validate age limits against product
    if product.min_age_limit and plan_data.min_enrollment_age:
        if plan_data.min_enrollment_age < product.min_age_limit:
            raise ValidationException(
                f"Plan minimum age {plan_data.min_enrollment_age} "
                f"is below product minimum {product.min_age_limit}"
            )
    
    if product.max_age_limit and plan_data.max_enrollment_age:
        if plan_data.max_enrollment_age > product.max_age_limit:
            raise ValidationException(
                f"Plan maximum age {plan_data.max_enrollment_age} "
                f"exceeds product maximum {product.max_age_limit}"
            )
    
    # Validate deductibles
    if plan_data.family_deductible and plan_data.individual_deductible:
        if plan_data.family_deductible < plan_data.individual_deductible:
            raise ValidationException(
                "Family deductible cannot be less than individual deductible"
            )
    
    # Validate limits
    if plan_data.annual_limit and plan_data.lifetime_limit:
        if plan_data.annual_limit > plan_data.lifetime_limit:
            raise ValidationException(
                "Annual limit cannot exceed lifetime limit"
            )
    
    # Validate member limits
    if plan_data.min_members and plan_data.max_members:
        if plan_data.min_members > plan_data.max_members:
            raise ValidationException(
                "Minimum members cannot exceed maximum members"
            )
    
    # Validate premium
    if plan_data.base_premium <= 0:
        raise ValidationException("Base premium must be greater than zero")
    
    # Validate dates
    if plan_data.effective_date and plan_data.expiry_date:
        if plan_data.expiry_date <= plan_data.effective_date:
            raise ValidationException("Expiry date must be after effective date")


def create_plan_tier_structure(
    db: Session,
    product_id: UUID,
    base_premium: Decimal,
    created_by: Optional[UUID] = None
) -> List[PlanTypeResponse]:
    """
    Create a standard tier structure for a product
    
    Args:
        db: Database session
        product_id: Product UUID
        base_premium: Base premium for bronze tier
        created_by: User creating plans
        
    Returns:
        List of created plans
    """
    # Verify product exists
    product = product_repo.get_product_catalog_by_id(db, product_id)
    if not product:
        raise NotFoundException(f"Product {product_id} not found")
    
    # Define tier multipliers
    tier_config = [
        (PlanTier.BRONZE, "Bronze", 1.0, 5000, 10000),
        (PlanTier.SILVER, "Silver", 1.3, 3000, 20000),
        (PlanTier.GOLD, "Gold", 1.6, 1500, 50000),
        (PlanTier.PLATINUM, "Platinum", 2.0, 500, 100000)
    ]
    
    created_plans = []
    
    for tier, name, multiplier, deductible, limit in tier_config:
        plan_data = PlanTypeCreate(
            product_id=product_id,
            plan_code=f"{product.product_code}_{tier.value.upper()}",
            plan_name=f"{product.product_name} - {name}",
            description=f"{name} tier plan for {product.product_name}",
            plan_tier=tier,
            plan_category=PlanCategory.INDIVIDUAL,
            base_premium=base_premium * Decimal(str(multiplier)),
            individual_deductible=Decimal(str(deductible)),
            annual_limit=Decimal(str(limit)),
            out_of_pocket_max=Decimal(str(limit * 0.2)),
            is_renewable=True,
            allows_dependents=True,
            currency="USD"
        )
        
        try:
            plan = create_plan_with_validation(db, plan_data, created_by)
            created_plans.append(plan)
        except Exception as e:
            logger.error(f"Failed to create {tier} plan: {e}")
    
    return created_plans


# ================================================================
# PLAN RETRIEVAL & SEARCH
# ================================================================

def get_plan_details(
    db: Session,
    plan_id: UUID,
    include_features: bool = True
) -> Dict[str, Any]:
    """
    Get comprehensive plan details
    
    Args:
        db: Database session
        plan_id: Plan UUID
        include_features: Include applicable features
        
    Returns:
        Plan details with additional information
    """
    plan = repo.get_plan_type_by_id(db, plan_id)
    
    if not plan:
        raise NotFoundException(f"Plan with ID {plan_id} not found")
    
    result = {
        "plan": PlanTypeResponse.model_validate(plan),
        "coverage": {
            "annual_limit": float(plan.annual_limit) if plan.annual_limit else None,
            "lifetime_limit": float(plan.lifetime_limit) if plan.lifetime_limit else None,
            "out_of_pocket_max": float(plan.out_of_pocket_max) if plan.out_of_pocket_max else None,
            "individual_deductible": float(plan.individual_deductible) if plan.individual_deductible else None,
            "family_deductible": float(plan.family_deductible) if plan.family_deductible else None
        },
        "enrollment": {
            "min_age": plan.min_enrollment_age,
            "max_age": plan.max_enrollment_age,
            "min_members": plan.min_members,
            "max_members": plan.max_members,
            "allows_dependents": plan.allows_dependents,
            "max_dependents": plan.max_dependents
        }
    }
    
    # Add features if requested
    if include_features:
        features = feature_repo.get_features_by_product(db, plan.product_id)
        
        # Categorize features for the plan
        included_features = []
        optional_features = []
        
        for feature in features:
            if feature.is_mandatory:
                included_features.append({
                    "id": str(feature.id),
                    "name": feature.feature_name,
                    "category": feature.feature_category
                })
            else:
                optional_features.append({
                    "id": str(feature.id),
                    "name": feature.feature_name,
                    "category": feature.feature_category,
                    "additional_cost": float(feature.base_price) if feature.base_price else 0
                })
        
        result["features"] = {
            "included": included_features,
            "optional": optional_features,
            "total_included": len(included_features),
            "total_optional": len(optional_features)
        }
    
    return result


def get_plans_by_product(
    db: Session,
    product_id: UUID,
    active_only: bool = True
) -> List[PlanTypeResponse]:
    """
    Get all plans for a product
    
    Args:
        db: Database session
        product_id: Product UUID
        active_only: Only return active plans
        
    Returns:
        List of plans
    """
    plans = repo.get_plans_by_product(
        db, product_id, 
        include_inactive=not active_only
    )
    
    return [PlanTypeResponse.model_validate(p) for p in plans]


def search_plans(
    db: Session,
    filters: Optional[PlanTypeFilter] = None,
    page: int = 1,
    page_size: int = 50
) -> PlanTypeListResponse:
    """
    Search plans with filtering and pagination
    
    Args:
        db: Database session
        filters: Search filters
        page: Page number
        page_size: Items per page
        
    Returns:
        Paginated plan list
    """
    skip = (page - 1) * page_size
    
    result = repo.get_plans_list(
        db, filters, skip, page_size
    )
    
    plans = [
        PlanTypeResponse.model_validate(p)
        for p in result["plans"]
    ]
    
    return PlanTypeListResponse(
        plans=plans,
        total_count=result["total_count"],
        page=page,
        page_size=page_size,
        total_pages=result["total_pages"]
    )


# ================================================================
# PLAN COMPARISON
# ================================================================

def compare_plans(
    db: Session,
    comparison_request: PlanComparison
) -> PlanComparisonResponse:
    """
    Compare multiple plans side by side
    
    Args:
        db: Database session
        comparison_request: Comparison request
        
    Returns:
        Detailed plan comparison
    """
    if len(comparison_request.plan_ids) < 2:
        raise ValidationException("At least 2 plans required for comparison")
    
    if len(comparison_request.plan_ids) > 5:
        raise ValidationException("Maximum 5 plans can be compared at once")
    
    # Get comparison data from repository
    comparison_data = repo.compare_plans(db, comparison_request.plan_ids)
    
    # Enhance with additional analysis
    plans = []
    for plan_id in comparison_request.plan_ids:
        plan = repo.get_plan_type_by_id(db, plan_id)
        if plan:
            plans.append(PlanTypeResponse.model_validate(plan))
    
    # Add feature comparison if requested
    feature_comparison = None
    if comparison_request.include_features:
        feature_comparison = _compare_plan_features(db, plans)
    
    # Add pricing comparison if requested
    pricing_comparison = None
    if comparison_request.include_pricing:
        pricing_comparison = _compare_plan_pricing(plans)
    
    # Add coverage comparison if requested
    coverage_comparison = None
    if comparison_request.include_coverage:
        coverage_comparison = comparison_data.get("coverage_comparison")
    
    # Generate recommendation
    recommendation = _generate_plan_recommendation(plans, comparison_data)
    
    return PlanComparisonResponse(
        plans=plans,
        feature_comparison=feature_comparison,
        pricing_comparison=pricing_comparison,
        coverage_comparison=coverage_comparison,
        recommendation=recommendation
    )


def _compare_plan_features(
    db: Session,
    plans: List[PlanTypeResponse]
) -> Dict[str, Any]:
    """
    Compare features across plans
    
    Args:
        db: Database session
        plans: List of plans to compare
        
    Returns:
        Feature comparison data
    """
    feature_comparison = {}
    
    for plan in plans:
        # Get features for the plan's product
        features = feature_repo.get_features_by_product(db, plan.product_id)
        
        mandatory_count = sum(1 for f in features if f.is_mandatory)
        optional_count = sum(1 for f in features if not f.is_mandatory)
        
        feature_comparison[str(plan.id)] = {
            "total_features": len(features),
            "mandatory_features": mandatory_count,
            "optional_features": optional_count,
            "categories": list(set(f.feature_category for f in features))
        }
    
    return feature_comparison


def _compare_plan_pricing(plans: List[PlanTypeResponse]) -> Dict[str, Any]:
    """
    Compare pricing across plans
    
    Args:
        plans: List of plans to compare
        
    Returns:
        Pricing comparison data
    """
    pricing_comparison = {
        "base_premiums": {},
        "payment_frequencies": {},
        "value_analysis": {}
    }
    
    premiums = []
    for plan in plans:
        premium = float(plan.base_premium)
        premiums.append(premium)
        
        pricing_comparison["base_premiums"][str(plan.id)] = {
            "amount": premium,
            "currency": plan.currency,
            "tier": plan.plan_tier
        }
        
        pricing_comparison["payment_frequencies"][str(plan.id)] = plan.payment_frequency
        
        # Calculate value score (coverage/price ratio)
        coverage_value = 0
        if plan.annual_limit:
            coverage_value = float(plan.annual_limit) / premium if premium > 0 else 0
        
        pricing_comparison["value_analysis"][str(plan.id)] = {
            "coverage_per_dollar": coverage_value,
            "deductible_to_premium_ratio": (
                float(plan.individual_deductible) / premium 
                if plan.individual_deductible and premium > 0 else 0
            )
        }
    
    # Add summary statistics
    pricing_comparison["summary"] = {
        "average_premium": sum(premiums) / len(premiums) if premiums else 0,
        "price_range": max(premiums) - min(premiums) if premiums else 0,
        "best_value_plan": max(
            pricing_comparison["value_analysis"].items(),
            key=lambda x: x[1]["coverage_per_dollar"]
        )[0] if pricing_comparison["value_analysis"] else None
    }
    
    return pricing_comparison


def _generate_plan_recommendation(
    plans: List[PlanTypeResponse],
    comparison_data: Dict[str, Any]
) -> str:
    """
    Generate intelligent plan recommendation
    
    Args:
        plans: List of plans
        comparison_data: Comparison data
        
    Returns:
        Recommendation text
    """
    if not plans:
        return "No plans available for comparison"
    
    recommendations = []
    
    # Find best value plan
    best_value_premium = min(plans, key=lambda p: p.base_premium)
    recommendations.append(
        f"Best Value: {best_value_premium.plan_name} "
        f"({best_value_premium.plan_tier} tier) at "
        f"{best_value_premium.base_premium} {best_value_premium.currency}"
    )
    
    # Find most comprehensive plan
    best_coverage = max(
        plans,
        key=lambda p: (p.annual_limit or 0) + (p.lifetime_limit or 0)
    )
    if best_coverage != best_value_premium:
        recommendations.append(
            f"Most Comprehensive: {best_coverage.plan_name} "
            f"with highest coverage limits"
        )
    
    # Find balanced option
    if len(plans) >= 3:
        mid_tier_plans = [
            p for p in plans 
            if p.plan_tier in [PlanTier.SILVER, PlanTier.GOLD]
        ]
        if mid_tier_plans:
            balanced = mid_tier_plans[0]
            recommendations.append(
                f"Balanced Choice: {balanced.plan_name} "
                f"offers good coverage at moderate cost"
            )
    
    return " | ".join(recommendations)


# ================================================================
# ELIGIBILITY CHECKING
# ================================================================

def check_plan_eligibility(
    db: Session,
    eligibility_request: PlanEligibilityRequest,
    product_id: Optional[UUID] = None
) -> PlanEligibilityResponse:
    """
    Check eligibility for plans based on criteria
    
    Args:
        db: Database session
        eligibility_request: Eligibility criteria
        product_id: Optional product filter
        
    Returns:
        Eligibility response with eligible/ineligible plans
    """
    # Get eligibility results from repository
    results = repo.check_plan_eligibility(db, eligibility_request, product_id)
    
    # Convert to response schema
    eligible_plans = results["eligible_plans"]
    ineligible_plans = results["ineligible_plans"]
    
    # Add recommendations based on eligibility
    recommendations = results.get("recommendations", [])
    
    if eligible_plans:
        # Get details of eligible plans for better recommendations
        plan_details = []
        for plan_id in eligible_plans[:3]:  # Get top 3 for recommendations
            plan = repo.get_plan_type_by_id(db, plan_id)
            if plan:
                plan_details.append(plan)
        
        if plan_details:
            # Recommend based on profile
            if eligibility_request.member_count == 1:
                individual_plans = [
                    p for p in plan_details 
                    if p.plan_category == PlanCategory.INDIVIDUAL
                ]
                if individual_plans:
                    recommendations.append(
                        f"Recommended: {individual_plans[0].plan_name} "
                        f"for individual coverage"
                    )
            elif eligibility_request.dependent_count > 0:
                family_plans = [
                    p for p in plan_details 
                    if p.plan_category == PlanCategory.FAMILY
                ]
                if family_plans:
                    recommendations.append(
                        f"Recommended: {family_plans[0].plan_name} "
                        f"for family coverage"
                    )
    
    return PlanEligibilityResponse(
        eligible_plans=eligible_plans,
        ineligible_plans=ineligible_plans,
        recommendations=recommendations
    )


# ================================================================
# PREMIUM CALCULATIONS
# ================================================================

def calculate_plan_premium(
    db: Session,
    plan_id: UUID,
    member_count: int = 1,
    dependent_count: int = 0,
    ages: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Calculate detailed premium for a plan
    
    Args:
        db: Database session
        plan_id: Plan UUID
        member_count: Number of primary members
        dependent_count: Number of dependents
        ages: List of ages for members
        
    Returns:
        Detailed premium calculation
    """
    # Get base calculation from repository
    base_calc = repo.calculate_plan_premium(
        db, plan_id, member_count, dependent_count,
        ages[0] if ages else None
    )
    
    # Enhance with additional calculations
    plan = repo.get_plan_type_by_id(db, plan_id)
    
    if not plan:
        raise NotFoundException(f"Plan {plan_id} not found")
    
    # Calculate age-based adjustments for all members
    age_adjustments = []
    if ages:
        for age in ages:
            adjustment = _calculate_age_adjustment(age)
            age_adjustments.append({
                "age": age,
                "adjustment_factor": float(adjustment)
            })
    
    # Calculate total with all factors
    base_premium = base_calc["base_premium"]
    total_adjustment = sum(a["adjustment_factor"] for a in age_adjustments) if age_adjustments else 1.0
    
    # Apply group discount if applicable
    group_discount = Decimal('0')
    if member_count + dependent_count >= 5:
        group_discount = Decimal('0.1')  # 10% group discount
    
    # Calculate final premium
    adjusted_premium = Decimal(str(base_premium)) * Decimal(str(total_adjustment))
    discount_amount = adjusted_premium * group_discount
    final_premium = adjusted_premium - discount_amount
    
    # Calculate payment schedule
    payment_schedule = _calculate_payment_schedule(
        final_premium, plan.payment_frequency
    )
    
    return {
        **base_calc,
        "age_adjustments": age_adjustments,
        "group_discount": {
            "applicable": group_discount > 0,
            "rate": float(group_discount),
            "amount": float(discount_amount)
        },
        "final_premium": float(final_premium),
        "payment_schedule": payment_schedule,
        "effective_date": date.today().isoformat(),
        "next_payment_due": payment_schedule[0]["due_date"] if payment_schedule else None
    }


def _calculate_age_adjustment(age: int) -> Decimal:
    """
    Calculate age-based premium adjustment
    
    Args:
        age: Member age
        
    Returns:
        Adjustment factor
    """
    if age < 25:
        return Decimal('0.8')
    elif age < 35:
        return Decimal('1.0')
    elif age < 45:
        return Decimal('1.2')
    elif age < 55:
        return Decimal('1.5')
    elif age < 65:
        return Decimal('1.8')
    else:
        return Decimal('2.2')


def _calculate_payment_schedule(
    annual_premium: Decimal,
    frequency: str
) -> List[Dict[str, Any]]:
    """
    Calculate payment schedule based on frequency
    
    Args:
        annual_premium: Annual premium amount
        frequency: Payment frequency
        
    Returns:
        Payment schedule
    """
    schedule = []
    today = date.today()
    
    if frequency == "monthly":
        payment_amount = annual_premium / 12
        for month in range(12):
            due_date = today + timedelta(days=30 * month)
            schedule.append({
                "payment_number": month + 1,
                "due_date": due_date.isoformat(),
                "amount": float(payment_amount)
            })
    elif frequency == "quarterly":
        payment_amount = annual_premium / 4
        for quarter in range(4):
            due_date = today + timedelta(days=90 * quarter)
            schedule.append({
                "payment_number": quarter + 1,
                "due_date": due_date.isoformat(),
                "amount": float(payment_amount)
            })
    elif frequency == "semi-annual":
        payment_amount = annual_premium / 2
        for half in range(2):
            due_date = today + timedelta(days=180 * half)
            schedule.append({
                "payment_number": half + 1,
                "due_date": due_date.isoformat(),
                "amount": float(payment_amount)
            })
    else:  # annual
        schedule.append({
            "payment_number": 1,
            "due_date": today.isoformat(),
            "amount": float(annual_premium)
        })
    
    return schedule


# ================================================================
# ANALYTICS & REPORTING
# ================================================================

def get_plan_analytics(
    db: Session,
    product_id: UUID
) -> Dict[str, Any]:
    """
    Get analytics for plans in a product
    
    Args:
        db: Database session
        product_id: Product UUID
        
    Returns:
        Plan analytics
    """
    plans = repo.get_plans_by_product(db, product_id)
    stats = repo.get_plan_statistics(db, product_id)
    price_range = repo.get_plan_price_range(db, product_id)
    
    analytics = {
        "product_id": str(product_id),
        "statistics": stats,
        "pricing": price_range,
        "tier_distribution": {},
        "network_analysis": {},
        "enrollment_capacity": {}
    }
    
    # Analyze tier distribution
    tier_counts = {}
    for plan in plans:
        tier = plan.plan_tier
        if tier not in tier_counts:
            tier_counts[tier] = 0
        tier_counts[tier] += 1
    
    analytics["tier_distribution"] = tier_counts
    
    # Analyze network types
    network_counts = {}
    for plan in plans:
        if plan.network_type:
            network = plan.network_type
            if network not in network_counts:
                network_counts[network] = 0
            network_counts[network] += 1
    
    analytics["network_analysis"] = network_counts
    
    # Calculate enrollment capacity
    total_capacity = sum(
        plan.max_members or 100 
        for plan in plans 
        if plan.status == PlanStatus.ACTIVE
    )
    
    analytics["enrollment_capacity"] = {
        "total_plans": len(plans),
        "active_plans": sum(1 for p in plans if p.status == PlanStatus.ACTIVE),
        "estimated_capacity": total_capacity,
        "plans_allowing_dependents": sum(1 for p in plans if p.allows_dependents)
    }
    
    return analytics


def get_plan_performance_metrics(
    db: Session,
    plan_id: UUID,
    period_days: int = 30
) -> Dict[str, Any]:
    """
    Get performance metrics for a plan (mock implementation)
    
    Args:
        db: Database session
        plan_id: Plan UUID
        period_days: Analysis period in days
        
    Returns:
        Performance metrics
    """
    plan = repo.get_plan_type_by_id(db, plan_id)
    
    if not plan:
        raise NotFoundException(f"Plan {plan_id} not found")
    
    # Mock metrics - in production would come from enrollment data
    metrics = {
        "plan_id": str(plan_id),
        "plan_name": plan.plan_name,
        "period_days": period_days,
        "performance": {
            "enrollment_rate": 75.5,  # Percentage
            "retention_rate": 92.3,
            "satisfaction_score": 4.2,  # Out of 5
            "claims_ratio": 68.5  # Percentage
        },
        "enrollment": {
            "new_enrollments": 45,
            "renewals": 120,
            "cancellations": 8,
            "net_growth": 37
        },
        "financial": {
            "premium_collected": 125000.00,
            "claims_paid": 85625.00,
            "profit_margin": 31.5
        },
        "trends": {
            "enrollment_trend": "increasing",
            "premium_trend": "stable",
            "claims_trend": "decreasing"
        }
    }
    
    return metrics


# ================================================================
# END OF SERVICE
# ================================================================