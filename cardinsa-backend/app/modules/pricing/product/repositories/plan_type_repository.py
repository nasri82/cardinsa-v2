# app/modules/pricing/product/repositories/plan_type_repository.py

"""
Plan Type Repository

Data access layer for Plan Type entities.
Handles all database operations for insurance plan management.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select, case
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.modules.pricing.product.models.plan_type_model import PlanType
from app.modules.pricing.product.schemas.plan_type_schema import (
    PlanTypeCreate,
    PlanTypeUpdate,
    PlanTypeFilter,
    PlanStatus,
    PlanTier,
    PlanCategory,
    NetworkType,
    PlanEligibilityRequest
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

class ConflictException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ================================================================
# CREATE OPERATIONS
# ================================================================

def create_plan_type(
    db: Session,
    plan_data: PlanTypeCreate,
    created_by: Optional[UUID] = None
) -> PlanType:
    """
    Create a new plan type
    
    Args:
        db: Database session
        plan_data: Plan type creation data
        created_by: ID of the user creating the plan
        
    Returns:
        Created PlanType instance
        
    Raises:
        ConflictException: If plan code already exists for product
        BadRequestException: If data validation fails
    """
    try:
        # Check for duplicate plan code within the same product
        existing = db.query(PlanType).filter(
            and_(
                PlanType.product_id == plan_data.product_id,
                PlanType.plan_code == plan_data.plan_code,
                PlanType.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ConflictException(
                f"Plan with code '{plan_data.plan_code}' already exists for this product"
            )
        
        # Create new plan
        plan = PlanType(
            **plan_data.model_dump(exclude={'tags'}),
            created_by=created_by,
            created_at=datetime.utcnow(),
            status=PlanStatus.ACTIVE
        )
        
        # Handle tags if provided
        if plan_data.tags:
            plan.tags = plan_data.tags
        
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        logger.info(f"Created plan type: {plan.id}")
        return plan
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        raise ConflictException("Plan creation failed due to data conflict")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating plan type: {str(e)}")
        raise BadRequestException(f"Failed to create plan: {str(e)}")


def bulk_create_plans(
    db: Session,
    plans_data: List[PlanTypeCreate],
    created_by: Optional[UUID] = None
) -> List[PlanType]:
    """
    Create multiple plan types in bulk
    
    Args:
        db: Database session
        plans_data: List of plan creation data
        created_by: ID of the user creating the plans
        
    Returns:
        List of created PlanType instances
    """
    created_plans = []
    
    try:
        for plan_data in plans_data:
            plan = create_plan_type(db, plan_data, created_by)
            created_plans.append(plan)
        
        logger.info(f"Bulk created {len(created_plans)} plans")
        return created_plans
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk plan creation: {str(e)}")
        raise BadRequestException(f"Bulk creation failed: {str(e)}")


# ================================================================
# READ OPERATIONS
# ================================================================

def get_plan_type_by_id(
    db: Session,
    plan_id: UUID,
    include_deleted: bool = False
) -> Optional[PlanType]:
    """
    Get plan type by ID
    
    Args:
        db: Database session
        plan_id: Plan UUID
        include_deleted: Include soft-deleted records
        
    Returns:
        PlanType instance or None
    """
    query = db.query(PlanType).filter(PlanType.id == plan_id)
    
    if not include_deleted:
        query = query.filter(PlanType.is_deleted == False)
    
    return query.first()


def get_plans_by_product(
    db: Session,
    product_id: UUID,
    plan_tier: Optional[PlanTier] = None,
    include_inactive: bool = False
) -> List[PlanType]:
    """
    Get all plans for a specific product
    
    Args:
        db: Database session
        product_id: Product UUID
        plan_tier: Optional plan tier filter
        include_inactive: Include inactive plans
        
    Returns:
        List of PlanType instances
    """
    query = db.query(PlanType).filter(
        and_(
            PlanType.product_id == product_id,
            PlanType.is_deleted == False
        )
    )
    
    if not include_inactive:
        query = query.filter(PlanType.status == PlanStatus.ACTIVE)
    
    if plan_tier:
        query = query.filter(PlanType.plan_tier == plan_tier)
    
    # Order by tier hierarchy
    tier_order = case(
        (PlanType.plan_tier == PlanTier.BRONZE, 1),
        (PlanType.plan_tier == PlanTier.SILVER, 2),
        (PlanType.plan_tier == PlanTier.GOLD, 3),
        (PlanType.plan_tier == PlanTier.PLATINUM, 4),
        (PlanType.plan_tier == PlanTier.DIAMOND, 5),
        else_=6
    )
    
    return query.order_by(tier_order, PlanType.plan_code).all()


def get_plan_by_code(
    db: Session,
    product_id: UUID,
    plan_code: str
) -> Optional[PlanType]:
    """
    Get plan by product ID and plan code
    
    Args:
        db: Database session
        product_id: Product UUID
        plan_code: Plan code
        
    Returns:
        PlanType instance or None
    """
    return db.query(PlanType).filter(
        and_(
            PlanType.product_id == product_id,
            PlanType.plan_code == plan_code.upper(),
            PlanType.is_deleted == False
        )
    ).first()


def get_plans_list(
    db: Session,
    filters: Optional[PlanTypeFilter] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Get paginated list of plans with filters
    
    Args:
        db: Database session
        filters: Filter criteria
        skip: Number of records to skip
        limit: Maximum number of records to return
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        Dictionary containing plans list and pagination info
    """
    query = db.query(PlanType).filter(PlanType.is_deleted == False)
    
    # Apply filters
    if filters:
        if filters.product_id:
            query = query.filter(PlanType.product_id == filters.product_id)
        
        if filters.plan_tier:
            query = query.filter(PlanType.plan_tier == filters.plan_tier)
        
        if filters.plan_category:
            query = query.filter(PlanType.plan_category == filters.plan_category)
        
        if filters.network_type:
            query = query.filter(PlanType.network_type == filters.network_type)
        
        if filters.status:
            query = query.filter(PlanType.status == filters.status)
        
        if filters.is_renewable is not None:
            query = query.filter(PlanType.is_renewable == filters.is_renewable)
        
        if filters.requires_medical_exam is not None:
            query = query.filter(
                PlanType.requires_medical_exam == filters.requires_medical_exam
            )
        
        if filters.allows_dependents is not None:
            query = query.filter(PlanType.allows_dependents == filters.allows_dependents)
        
        if filters.international_coverage is not None:
            query = query.filter(
                PlanType.international_coverage == filters.international_coverage
            )
        
        if filters.min_premium is not None:
            query = query.filter(PlanType.base_premium >= filters.min_premium)
        
        if filters.max_premium is not None:
            query = query.filter(PlanType.base_premium <= filters.max_premium)
        
        if filters.min_deductible is not None:
            query = query.filter(
                PlanType.individual_deductible >= filters.min_deductible
            )
        
        if filters.max_deductible is not None:
            query = query.filter(
                PlanType.individual_deductible <= filters.max_deductible
            )
        
        if filters.search_term:
            search_pattern = f"%{filters.search_term}%"
            query = query.filter(
                or_(
                    PlanType.plan_code.ilike(search_pattern),
                    PlanType.plan_name.ilike(search_pattern),
                    PlanType.description.ilike(search_pattern)
                )
            )
        
        if filters.tags:
            query = query.filter(PlanType.tags.contains(filters.tags))
        
        if filters.effective_date_from:
            query = query.filter(PlanType.effective_date >= filters.effective_date_from)
        
        if filters.effective_date_to:
            query = query.filter(PlanType.effective_date <= filters.effective_date_to)
    
    # Get total count
    total_count = query.count()
    
    # Apply sorting
    if hasattr(PlanType, sort_by):
        order_column = getattr(PlanType, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    
    # Apply pagination
    plans = query.offset(skip).limit(limit).all()
    
    return {
        "plans": plans,
        "total_count": total_count,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "total_pages": (total_count + limit - 1) // limit
    }


# ================================================================
# UPDATE OPERATIONS
# ================================================================

def update_plan_type(
    db: Session,
    plan_id: UUID,
    update_data: PlanTypeUpdate,
    updated_by: Optional[UUID] = None
) -> PlanType:
    """
    Update plan type
    
    Args:
        db: Database session
        plan_id: Plan UUID
        update_data: Update data
        updated_by: ID of the user updating the plan
        
    Returns:
        Updated PlanType instance
        
    Raises:
        NotFoundException: If plan not found
        BadRequestException: If update fails
    """
    plan = get_plan_type_by_id(db, plan_id)
    
    if not plan:
        raise NotFoundException(f"Plan with ID {plan_id} not found")
    
    try:
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(plan, field, value)
        
        plan.updated_at = datetime.utcnow()
        plan.updated_by = updated_by
        
        db.commit()
        db.refresh(plan)
        
        logger.info(f"Updated plan type: {plan_id}")
        return plan
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating plan: {str(e)}")
        raise BadRequestException(f"Failed to update plan: {str(e)}")


def bulk_update_plans(
    db: Session,
    plan_ids: List[UUID],
    update_data: PlanTypeUpdate,
    updated_by: Optional[UUID] = None
) -> List[PlanType]:
    """
    Update multiple plans in bulk
    
    Args:
        db: Database session
        plan_ids: List of plan UUIDs
        update_data: Update data to apply
        updated_by: ID of the user updating the plans
        
    Returns:
        List of updated PlanType instances
    """
    updated_plans = []
    
    try:
        for plan_id in plan_ids:
            plan = update_plan_type(db, plan_id, update_data, updated_by)
            updated_plans.append(plan)
        
        logger.info(f"Bulk updated {len(updated_plans)} plans")
        return updated_plans
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk update: {str(e)}")
        raise BadRequestException(f"Bulk update failed: {str(e)}")


# ================================================================
# DELETE OPERATIONS
# ================================================================

def delete_plan_type(
    db: Session,
    plan_id: UUID,
    soft_delete: bool = True,
    deleted_by: Optional[UUID] = None
) -> bool:
    """
    Delete plan type (soft or hard delete)
    
    Args:
        db: Database session
        plan_id: Plan UUID
        soft_delete: If True, perform soft delete
        deleted_by: ID of the user deleting the plan
        
    Returns:
        True if deleted successfully
        
    Raises:
        NotFoundException: If plan not found
    """
    plan = get_plan_type_by_id(db, plan_id, include_deleted=False)
    
    if not plan:
        raise NotFoundException(f"Plan with ID {plan_id} not found")
    
    try:
        if soft_delete:
            plan.is_deleted = True
            plan.deleted_at = datetime.utcnow()
            plan.deleted_by = deleted_by
            plan.status = PlanStatus.DISCONTINUED
        else:
            db.delete(plan)
        
        db.commit()
        
        logger.info(f"{'Soft' if soft_delete else 'Hard'} deleted plan: {plan_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting plan: {str(e)}")
        raise BadRequestException(f"Failed to delete plan: {str(e)}")


def delete_plans_by_product(
    db: Session,
    product_id: UUID,
    soft_delete: bool = True,
    deleted_by: Optional[UUID] = None
) -> int:
    """
    Delete all plans for a product
    
    Args:
        db: Database session
        product_id: Product UUID
        soft_delete: If True, perform soft delete
        deleted_by: ID of the user deleting the plans
        
    Returns:
        Number of plans deleted
    """
    try:
        if soft_delete:
            result = db.query(PlanType).filter(
                and_(
                    PlanType.product_id == product_id,
                    PlanType.is_deleted == False
                )
            ).update({
                'is_deleted': True,
                'deleted_at': datetime.utcnow(),
                'deleted_by': deleted_by,
                'status': PlanStatus.DISCONTINUED
            })
        else:
            result = db.query(PlanType).filter(
                PlanType.product_id == product_id
            ).delete()
        
        db.commit()
        
        logger.info(f"Deleted {result} plans for product {product_id}")
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting plans: {str(e)}")
        raise BadRequestException(f"Failed to delete plans: {str(e)}")


# ================================================================
# COMPARISON OPERATIONS
# ================================================================

def compare_plans(
    db: Session,
    plan_ids: List[UUID]
) -> Dict[str, Any]:
    """
    Compare multiple plan types
    
    Args:
        db: Database session
        plan_ids: List of plan UUIDs to compare
        
    Returns:
        Dictionary containing comparison data
        
    Raises:
        NotFoundException: If any plan not found
    """
    plans = []
    
    for plan_id in plan_ids:
        plan = get_plan_type_by_id(db, plan_id)
        if not plan:
            raise NotFoundException(f"Plan with ID {plan_id} not found")
        plans.append(plan)
    
    # Create comparison matrix
    comparison = {
        "plans": [],
        "premium_comparison": {},
        "coverage_comparison": {},
        "deductible_comparison": {},
        "waiting_period_comparison": {},
        "feature_comparison": {}
    }
    
    for plan in plans:
        plan_data = {
            "id": plan.id,
            "name": plan.plan_name,
            "code": plan.plan_code,
            "tier": plan.plan_tier,
            "category": plan.plan_category
        }
        comparison["plans"].append(plan_data)
        
        # Premium comparison
        comparison["premium_comparison"][str(plan.id)] = {
            "base_premium": float(plan.base_premium) if plan.base_premium else 0,
            "currency": plan.currency,
            "payment_frequency": plan.payment_frequency
        }
        
        # Coverage comparison
        comparison["coverage_comparison"][str(plan.id)] = {
            "annual_limit": float(plan.annual_limit) if plan.annual_limit else None,
            "lifetime_limit": float(plan.lifetime_limit) if plan.lifetime_limit else None,
            "out_of_pocket_max": float(plan.out_of_pocket_max) if plan.out_of_pocket_max else None
        }
        
        # Deductible comparison
        comparison["deductible_comparison"][str(plan.id)] = {
            "individual": float(plan.individual_deductible) if plan.individual_deductible else 0,
            "family": float(plan.family_deductible) if plan.family_deductible else 0
        }
        
        # Waiting period comparison
        comparison["waiting_period_comparison"][str(plan.id)] = {
            "general": plan.general_waiting_period,
            "pre_existing": plan.pre_existing_waiting_period
        }
        
        # Feature comparison
        comparison["feature_comparison"][str(plan.id)] = {
            "is_renewable": plan.is_renewable,
            "requires_medical_exam": plan.requires_medical_exam,
            "allows_dependents": plan.allows_dependents,
            "international_coverage": plan.international_coverage,
            "network_type": plan.network_type
        }
    
    # Add recommendation based on comparison
    comparison["recommendation"] = _generate_plan_recommendation(plans)
    
    return comparison


def _generate_plan_recommendation(plans: List[PlanType]) -> str:
    """
    Generate recommendation based on plan comparison
    
    Args:
        plans: List of PlanType instances
        
    Returns:
        Recommendation string
    """
    if not plans:
        return "No plans to compare"
    
    # Find best value plan (lowest premium)
    best_value = min(plans, key=lambda p: p.base_premium or Decimal('999999'))
    
    # Find most comprehensive plan (highest coverage)
    most_comprehensive = max(
        plans, 
        key=lambda p: (p.annual_limit or 0) + (p.lifetime_limit or 0)
    )
    
    recommendation = f"Best Value: {best_value.plan_name} "
    recommendation += f"(Premium: {best_value.base_premium} {best_value.currency}). "
    recommendation += f"Most Comprehensive: {most_comprehensive.plan_name}."
    
    return recommendation


# ================================================================
# ELIGIBILITY OPERATIONS
# ================================================================

def check_plan_eligibility(
    db: Session,
    eligibility_request: PlanEligibilityRequest,
    product_id: Optional[UUID] = None
) -> Dict[str, Any]:
    """
    Check plan eligibility based on criteria
    
    Args:
        db: Database session
        eligibility_request: Eligibility criteria
        product_id: Optional product filter
        
    Returns:
        Dictionary containing eligible and ineligible plans
    """
    query = db.query(PlanType).filter(
        and_(
            PlanType.is_deleted == False,
            PlanType.status == PlanStatus.ACTIVE
        )
    )
    
    if product_id:
        query = query.filter(PlanType.product_id == product_id)
    
    all_plans = query.all()
    
    eligible_plans = []
    ineligible_plans = []
    
    for plan in all_plans:
        ineligibility_reasons = []
        
        # Check age eligibility
        if plan.min_enrollment_age and eligibility_request.age < plan.min_enrollment_age:
            ineligibility_reasons.append(
                f"Age {eligibility_request.age} below minimum {plan.min_enrollment_age}"
            )
        
        if plan.max_enrollment_age and eligibility_request.age > plan.max_enrollment_age:
            ineligibility_reasons.append(
                f"Age {eligibility_request.age} above maximum {plan.max_enrollment_age}"
            )
        
        # Check member count
        if plan.min_members and eligibility_request.member_count < plan.min_members:
            ineligibility_reasons.append(
                f"Member count {eligibility_request.member_count} below minimum {plan.min_members}"
            )
        
        if plan.max_members and eligibility_request.member_count > plan.max_members:
            ineligibility_reasons.append(
                f"Member count {eligibility_request.member_count} above maximum {plan.max_members}"
            )
        
        # Check dependents
        if not plan.allows_dependents and eligibility_request.dependent_count > 0:
            ineligibility_reasons.append("Plan does not allow dependents")
        
        if plan.max_dependents and eligibility_request.dependent_count > plan.max_dependents:
            ineligibility_reasons.append(
                f"Dependent count {eligibility_request.dependent_count} exceeds maximum {plan.max_dependents}"
            )
        
        # Check medical exam requirement
        if (plan.requires_medical_exam and 
            eligibility_request.pre_existing_conditions and 
            len(eligibility_request.pre_existing_conditions) > 0):
            ineligibility_reasons.append(
                "Medical exam required due to pre-existing conditions"
            )
        
        # Add to appropriate list
        if ineligibility_reasons:
            ineligible_plans.append({
                "plan_id": plan.id,
                "plan_name": plan.plan_name,
                "plan_tier": plan.plan_tier,
                "reasons": ineligibility_reasons
            })
        else:
            eligible_plans.append(plan.id)
    
    # Generate recommendations
    recommendations = []
    
    if not eligible_plans:
        recommendations.append("No eligible plans found. Consider adjusting criteria.")
    else:
        recommendations.append(f"Found {len(eligible_plans)} eligible plans")
        
        if eligibility_request.pre_existing_conditions:
            recommendations.append(
                "Plans may have waiting periods for pre-existing conditions"
            )
    
    return {
        "eligible_plans": eligible_plans,
        "ineligible_plans": ineligible_plans,
        "recommendations": recommendations
    }


# ================================================================
# PRICING OPERATIONS
# ================================================================

def calculate_plan_premium(
    db: Session,
    plan_id: UUID,
    member_count: int = 1,
    dependent_count: int = 0,
    age: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate premium for a plan based on parameters
    
    Args:
        db: Database session
        plan_id: Plan UUID
        member_count: Number of members
        dependent_count: Number of dependents
        age: Primary member age
        
    Returns:
        Dictionary containing premium calculation
        
    Raises:
        NotFoundException: If plan not found
    """
    plan = get_plan_type_by_id(db, plan_id)
    
    if not plan:
        raise NotFoundException(f"Plan with ID {plan_id} not found")
    
    # Validate member counts
    if plan.min_members and member_count < plan.min_members:
        raise BadRequestException(
            f"Member count {member_count} below minimum {plan.min_members}"
        )
    
    if plan.max_members and member_count > plan.max_members:
        raise BadRequestException(
            f"Member count {member_count} above maximum {plan.max_members}"
        )
    
    if not plan.allows_dependents and dependent_count > 0:
        raise BadRequestException("Plan does not allow dependents")
    
    if plan.max_dependents and dependent_count > plan.max_dependents:
        raise BadRequestException(
            f"Dependent count {dependent_count} exceeds maximum {plan.max_dependents}"
        )
    
    # Calculate premium
    base_premium = plan.base_premium or Decimal('0')
    
    # Member multiplier
    member_multiplier = Decimal(str(member_count))
    
    # Dependent multiplier (usually discounted)
    dependent_multiplier = Decimal(str(dependent_count * 0.75))  # 75% of base for dependents
    
    # Age factor
    age_factor = Decimal('1.0')
    if age:
        if age > 60:
            age_factor = Decimal('1.5')
        elif age > 50:
            age_factor = Decimal('1.3')
        elif age > 40:
            age_factor = Decimal('1.1')
    
    # Calculate total premium
    total_multiplier = member_multiplier + dependent_multiplier
    subtotal = base_premium * total_multiplier * age_factor
    
    # Payment frequency adjustment
    payment_frequency_factor = {
        'monthly': Decimal('1'),
        'quarterly': Decimal('2.9'),  # Small discount for quarterly
        'semi-annual': Decimal('5.8'),  # Small discount for semi-annual
        'annual': Decimal('11.5')  # Discount for annual payment
    }
    
    frequency_factor = payment_frequency_factor.get(
        plan.payment_frequency, 
        Decimal('1')
    )
    
    adjusted_premium = subtotal * frequency_factor
    
    return {
        "plan_id": plan_id,
        "plan_name": plan.plan_name,
        "plan_tier": plan.plan_tier,
        "base_premium": float(base_premium),
        "member_count": member_count,
        "dependent_count": dependent_count,
        "subtotal": float(subtotal),
        "payment_frequency": plan.payment_frequency,
        "frequency_factor": float(frequency_factor),
        "adjusted_premium": float(adjusted_premium),
        "currency": plan.currency,
        "factors": {
            "member_multiplier": float(member_multiplier),
            "dependent_multiplier": float(dependent_multiplier),
            "age_factor": float(age_factor)
        }
    }


def get_plan_price_range(
    db: Session,
    product_id: UUID
) -> Dict[str, Any]:
    """
    Get price range for all plans in a product
    
    Args:
        db: Database session
        product_id: Product UUID
        
    Returns:
        Dictionary containing price range information
    """
    plans = get_plans_by_product(db, product_id)
    
    if not plans:
        return {
            "min_premium": 0,
            "max_premium": 0,
            "average_premium": 0,
            "plan_count": 0
        }
    
    premiums = [float(plan.base_premium) for plan in plans if plan.base_premium]
    
    return {
        "min_premium": min(premiums) if premiums else 0,
        "max_premium": max(premiums) if premiums else 0,
        "average_premium": sum(premiums) / len(premiums) if premiums else 0,
        "plan_count": len(plans),
        "by_tier": _get_premium_by_tier(plans)
    }


def _get_premium_by_tier(plans: List[PlanType]) -> Dict[str, Dict[str, float]]:
    """
    Get premium statistics by tier
    
    Args:
        plans: List of PlanType instances
        
    Returns:
        Dictionary of premium stats by tier
    """
    tier_premiums = {}
    
    for plan in plans:
        tier = plan.plan_tier
        premium = float(plan.base_premium) if plan.base_premium else 0
        
        if tier not in tier_premiums:
            tier_premiums[tier] = {
                "min": premium,
                "max": premium,
                "total": premium,
                "count": 1
            }
        else:
            tier_premiums[tier]["min"] = min(tier_premiums[tier]["min"], premium)
            tier_premiums[tier]["max"] = max(tier_premiums[tier]["max"], premium)
            tier_premiums[tier]["total"] += premium
            tier_premiums[tier]["count"] += 1
    
    # Calculate averages
    for tier in tier_premiums:
        tier_data = tier_premiums[tier]
        tier_data["average"] = tier_data["total"] / tier_data["count"]
        del tier_data["total"]  # Remove total from response
    
    return tier_premiums


# ================================================================
# STATISTICS OPERATIONS
# ================================================================

def get_plan_statistics(
    db: Session,
    product_id: Optional[UUID] = None
) -> Dict[str, Any]:
    """
    Get plan type statistics
    
    Args:
        db: Database session
        product_id: Optional product filter
        
    Returns:
        Dictionary containing plan statistics
    """
    try:
        query = db.query(PlanType).filter(PlanType.is_deleted == False)
        
        if product_id:
            query = query.filter(PlanType.product_id == product_id)
        
        total_plans = query.count()
        
        active_plans = query.filter(
            PlanType.status == PlanStatus.ACTIVE
        ).count()
        
        renewable_plans = query.filter(
            PlanType.is_renewable == True
        ).count()
        
        plans_by_tier = db.query(
            PlanType.plan_tier,
            func.count(PlanType.id),
            func.avg(PlanType.base_premium)
        ).filter(
            PlanType.is_deleted == False
        )
        
        if product_id:
            plans_by_tier = plans_by_tier.filter(
                PlanType.product_id == product_id
            )
        
        plans_by_tier = plans_by_tier.group_by(PlanType.plan_tier).all()
        
        plans_by_category = db.query(
            PlanType.plan_category,
            func.count(PlanType.id)
        ).filter(
            PlanType.is_deleted == False
        )
        
        if product_id:
            plans_by_category = plans_by_category.filter(
                PlanType.product_id == product_id
            )
        
        plans_by_category = plans_by_category.group_by(PlanType.plan_category).all()
        
        # Network type distribution
        network_distribution = db.query(
            PlanType.network_type,
            func.count(PlanType.id)
        ).filter(
            and_(
                PlanType.is_deleted == False,
                PlanType.network_type != None
            )
        )
        
        if product_id:
            network_distribution = network_distribution.filter(
                PlanType.product_id == product_id
            )
        
        network_distribution = network_distribution.group_by(PlanType.network_type).all()
        
        return {
            "total_plans": total_plans,
            "active_plans": active_plans,
            "inactive_plans": total_plans - active_plans,
            "renewable_plans": renewable_plans,
            "by_tier": [
                {
                    "tier": tier,
                    "count": count,
                    "avg_premium": float(avg_premium) if avg_premium else 0
                }
                for tier, count, avg_premium in plans_by_tier
            ],
            "by_category": dict(plans_by_category),
            "by_network": dict(network_distribution) if network_distribution else {}
        }
        
    except Exception as e:
        logger.error(f"Error getting plan statistics: {str(e)}")
        raise BadRequestException(f"Failed to get statistics: {str(e)}")


# ================================================================
# RENEWAL OPERATIONS
# ================================================================

def get_renewable_plans(
    db: Session,
    expiry_date_threshold: date,
    product_id: Optional[UUID] = None
) -> List[PlanType]:
    """
    Get plans that are due for renewal
    
    Args:
        db: Database session
        expiry_date_threshold: Date threshold for expiry
        product_id: Optional product filter
        
    Returns:
        List of PlanType instances due for renewal
    """
    query = db.query(PlanType).filter(
        and_(
            PlanType.is_deleted == False,
            PlanType.status == PlanStatus.ACTIVE,
            PlanType.is_renewable == True,
            PlanType.expiry_date != None,
            PlanType.expiry_date <= expiry_date_threshold
        )
    )
    
    if product_id:
        query = query.filter(PlanType.product_id == product_id)
    
    return query.order_by(PlanType.expiry_date).all()


# ================================================================
# END OF REPOSITORY
# ================================================================