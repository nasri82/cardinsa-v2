# app/modules/pricing/modifiers/repositories/pricing_discount_repository.py

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, and_, or_, func, desc, asc, case, text
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.core.base_repository import BaseRepository
from app.core.exceptions import NotFoundError, ValidationError, DatabaseOperationError
from app.modules.pricing.modifiers.models.pricing_discount_model import (
    PricingDiscount, DiscountType, DiscountScope, EligibilityType
)
from app.modules.pricing.modifiers.schemas.pricing_discount_schema import (
    PricingDiscountCreate,
    PricingDiscountUpdate,
)
from app.core.logging import get_app_logger

logger = get_app_logger("pricing.discount.repository")

class PricingDiscountRepository(BaseRepository):
    """
    Repository for Pricing Discount operations.
    
    Provides comprehensive data access methods for discount and promotion management
    including complex eligibility validation, stacking rules, campaign management,
    and usage tracking.
    
    Key Features:
    - Full CRUD operations with validation
    - Complex eligibility criteria queries
    - Promotional campaign management
    - Discount stacking and exclusion rules
    - Usage tracking and limits
    - Performance-optimized queries
    - Statistical analysis and reporting
    """
    
    def __init__(self, db: Session):
        super().__init__(PricingDiscount, db)

    # =====================================================
    # ENHANCED CRUD OPERATIONS
    # =====================================================
    
    def create_discount(self, discount_data: PricingDiscountCreate, created_by: UUID = None) -> PricingDiscount:
        """
        Create a new pricing discount with validation and audit logging.
        
        Args:
            discount_data: Discount creation data
            created_by: User ID creating the discount
            
        Returns:
            Created PricingDiscount instance
            
        Raises:
            ValidationError: If validation fails
            DatabaseOperationError: If database operation fails
        """
        try:
            # Convert Pydantic model to dict
            discount_dict = discount_data.model_dump(exclude_unset=True)
            
            # Add audit information
            if created_by:
                discount_dict['created_by'] = created_by
            
            # Validate business rules before creation
            self._validate_discount_data(discount_dict)
            
            # Create the discount
            discount = self.create(discount_dict)
            
            logger.info(f"Created discount: {discount.code} by user: {created_by}")
            return discount
            
        except Exception as e:
            logger.error(f"Failed to create discount: {str(e)}")
            raise DatabaseOperationError(f"Failed to create discount: {str(e)}")
    
    def update_discount(self, discount_id: UUID, discount_data: PricingDiscountUpdate, 
                       updated_by: UUID = None) -> PricingDiscount:
        """
        Update an existing pricing discount with validation and audit logging.
        
        Args:
            discount_id: ID of discount to update
            discount_data: Updated discount data
            updated_by: User ID updating the discount
            
        Returns:
            Updated PricingDiscount instance
            
        Raises:
            NotFoundError: If discount not found
            ValidationError: If validation fails
        """
        try:
            # Get existing discount
            existing_discount = self.get(discount_id)
            if not existing_discount:
                raise NotFoundError(f"Discount not found with ID: {discount_id}")
            
            # Convert update data to dict
            update_dict = discount_data.model_dump(exclude_unset=True, exclude_none=True)
            
            # Add audit information
            if updated_by:
                update_dict['updated_by'] = updated_by
            
            # Validate business rules
            merged_data = {**existing_discount.to_dict(), **update_dict}
            self._validate_discount_data(merged_data)
            
            # Update the discount
            updated_discount = self.update(discount_id, update_dict)
            
            logger.info(f"Updated discount: {existing_discount.code} by user: {updated_by}")
            return updated_discount
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update discount {discount_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update discount: {str(e)}")

    # =====================================================
    # BUSINESS-SPECIFIC QUERY METHODS
    # =====================================================
    
    def get_by_code(self, code: str) -> Optional[PricingDiscount]:
        """Get discount by unique code."""
        try:
            return self.get_by_field('code', code)
        except Exception as e:
            logger.error(f"Failed to get discount by code {code}: {str(e)}")
            return None
    
    def get_by_campaign_code(self, campaign_code: str) -> List[PricingDiscount]:
        """Get all discounts associated with a campaign code."""
        try:
            return self.get_multi(
                filters={'campaign_code': campaign_code, 'is_active': True},
                order_by='priority'
            )
        except Exception as e:
            logger.error(f"Failed to get discounts for campaign {campaign_code}: {str(e)}")
            return []
    
    def get_active_discounts(self, as_of_date: datetime = None, auto_apply_only: bool = False) -> List[PricingDiscount]:
        """
        Get all active discounts, optionally as of a specific date.
        
        Args:
            as_of_date: Date to check for validity (defaults to now)
            auto_apply_only: Whether to return only auto-apply discounts
            
        Returns:
            List of active discounts
        """
        try:
            if not as_of_date:
                as_of_date = datetime.utcnow()
            
            filters = [
                PricingDiscount.is_active == True,
                PricingDiscount.effective_date <= as_of_date,
                or_(
                    PricingDiscount.expiration_date.is_(None),
                    PricingDiscount.expiration_date > as_of_date
                )
            ]
            
            # Check promotional date ranges
            filters.append(
                or_(
                    PricingDiscount.is_promotional == False,
                    and_(
                        or_(
                            PricingDiscount.promotion_start_date.is_(None),
                            PricingDiscount.promotion_start_date <= as_of_date
                        ),
                        or_(
                            PricingDiscount.promotion_end_date.is_(None),
                            PricingDiscount.promotion_end_date > as_of_date
                        )
                    )
                )
            )
            
            if auto_apply_only:
                filters.append(PricingDiscount.is_auto_apply == True)
            
            query = select(PricingDiscount).where(
                and_(*filters)
            ).order_by(PricingDiscount.priority, PricingDiscount.stack_priority)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get active discounts: {str(e)}")
            return []
    
    def get_stackable_discounts(self, exclude_discount_codes: List[str] = None) -> List[PricingDiscount]:
        """
        Get all stackable discounts, optionally excluding specific discount codes.
        
        Args:
            exclude_discount_codes: List of discount codes to exclude
            
        Returns:
            List of stackable discounts
        """
        try:
            filters = [
                PricingDiscount.is_active == True,
                PricingDiscount.is_stackable == True
            ]
            
            if exclude_discount_codes:
                filters.append(~PricingDiscount.code.in_(exclude_discount_codes))
            
            query = select(PricingDiscount).where(
                and_(*filters)
            ).order_by(PricingDiscount.stack_priority, PricingDiscount.priority)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get stackable discounts: {str(e)}")
            return []
    
    def get_promotional_discounts(self, active_only: bool = True) -> List[PricingDiscount]:
        """Get promotional discounts."""
        try:
            filters = {'is_promotional': True}
            if active_only:
                filters['is_active'] = True
            
            return self.get_multi(
                filters=filters,
                order_by='promotion_end_date'
            )
        except Exception as e:
            logger.error(f"Failed to get promotional discounts: {str(e)}")
            return []
    
    def get_by_discount_type(self, discount_type: DiscountType) -> List[PricingDiscount]:
        """Get discounts filtered by type."""
        try:
            return self.get_multi(
                filters={'discount_type': discount_type, 'is_active': True},
                order_by='priority'
            )
        except Exception as e:
            logger.error(f"Failed to get discounts by type {discount_type.value}: {str(e)}")
            return []
    
    def get_by_discount_scope(self, discount_scope: DiscountScope) -> List[PricingDiscount]:
        """Get discounts filtered by scope."""
        try:
            return self.get_multi(
                filters={'discount_scope': discount_scope, 'is_active': True},
                order_by='priority'
            )
        except Exception as e:
            logger.error(f"Failed to get discounts by scope {discount_scope.value}: {str(e)}")
            return []

    # =====================================================
    # ELIGIBILITY AND FILTERING QUERIES
    # =====================================================
    
    def find_eligible_discounts(self, customer_data: Dict[str, Any], 
                               exclude_used: bool = True) -> List[PricingDiscount]:
        """
        Find discounts eligible for a specific customer based on their data.
        
        Args:
            customer_data: Customer information for eligibility checking
            exclude_used: Whether to exclude discounts already used by customer
            
        Returns:
            List of eligible discounts
        """
        try:
            # Start with active discounts
            eligible_discounts = self.get_active_discounts(auto_apply_only=False)
            
            # Filter by eligibility criteria
            filtered_discounts = []
            for discount in eligible_discounts:
                if discount.is_eligible(customer_data):
                    # Check usage limits if customer ID provided
                    customer_id = customer_data.get('customer_id')
                    if customer_id and exclude_used:
                        if self._check_customer_usage_limit(discount, customer_id):
                            filtered_discounts.append(discount)
                    else:
                        filtered_discounts.append(discount)
            
            return sorted(filtered_discounts, key=lambda d: (d.priority or 100, d.stack_priority or 100))
            
        except Exception as e:
            logger.error(f"Failed to find eligible discounts: {str(e)}")
            return []
    
    def get_discounts_by_age_range(self, min_age: int = None, max_age: int = None) -> List[PricingDiscount]:
        """
        Get discounts that apply to specific age ranges.
        
        Args:
            min_age: Minimum age filter
            max_age: Maximum age filter
            
        Returns:
            List of age-appropriate discounts
        """
        try:
            filters = [PricingDiscount.is_active == True]
            
            if min_age is not None:
                filters.append(
                    or_(
                        PricingDiscount.min_age.is_(None),
                        PricingDiscount.min_age <= min_age
                    )
                )
            
            if max_age is not None:
                filters.append(
                    or_(
                        PricingDiscount.max_age.is_(None),
                        PricingDiscount.max_age >= max_age
                    )
                )
            
            query = select(PricingDiscount).where(
                and_(*filters)
            ).order_by(PricingDiscount.priority)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get discounts by age range: {str(e)}")
            return []
    
    def get_discounts_by_premium_threshold(self, premium_amount: Decimal) -> List[PricingDiscount]:
        """Get discounts applicable to a specific premium amount."""
        try:
            filters = [
                PricingDiscount.is_active == True,
                or_(
                    PricingDiscount.min_premium_amount.is_(None),
                    PricingDiscount.min_premium_amount <= premium_amount
                )
            ]
            
            query = select(PricingDiscount).where(
                and_(*filters)
            ).order_by(PricingDiscount.priority)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get discounts by premium threshold: {str(e)}")
            return []

    # =====================================================
    # CAMPAIGN AND USAGE MANAGEMENT
    # =====================================================
    
    def get_expiring_campaigns(self, days_ahead: int = 7) -> List[PricingDiscount]:
        """
        Get promotional campaigns that will expire within the specified number of days.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of expiring promotional discounts
        """
        try:
            future_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            query = select(PricingDiscount).where(
                and_(
                    PricingDiscount.is_active == True,
                    PricingDiscount.is_promotional == True,
                    PricingDiscount.promotion_end_date.is_not(None),
                    PricingDiscount.promotion_end_date <= future_date,
                    PricingDiscount.promotion_end_date > datetime.utcnow()
                )
            ).order_by(PricingDiscount.promotion_end_date)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get expiring campaigns: {str(e)}")
            return []
    
    def get_overused_discounts(self) -> List[PricingDiscount]:
        """Get discounts that have exceeded their usage limits."""
        try:
            query = select(PricingDiscount).where(
                and_(
                    PricingDiscount.is_active == True,
                    PricingDiscount.max_uses_total.is_not(None),
                    PricingDiscount.current_use_count >= PricingDiscount.max_uses_total
                )
            ).order_by(desc(PricingDiscount.current_use_count))
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get overused discounts: {str(e)}")
            return []
    
    def increment_usage_count(self, discount_id: UUID, customer_id: str = None) -> bool:
        """
        Increment usage count for a discount.
        
        Args:
            discount_id: ID of discount to increment usage for
            customer_id: ID of customer using the discount
            
        Returns:
            True if usage was incremented successfully
        """
        try:
            discount = self.get(discount_id)
            if not discount:
                return False
            
            # Check if usage limit would be exceeded
            if discount.max_uses_total:
                current_count = discount.current_use_count or 0
                if current_count >= discount.max_uses_total:
                    logger.warning(f"Cannot increment usage for discount {discount.code}: limit exceeded")
                    return False
            
            # TODO: Check per-customer usage limit (would need usage tracking table)
            
            # Increment usage count
            new_count = (discount.current_use_count or 0) + 1
            self.update(discount_id, {'current_use_count': new_count})
            
            logger.info(f"Incremented usage count for discount {discount.code} to {new_count}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to increment usage count for discount {discount_id}: {str(e)}")
            return False

    # =====================================================
    # STATISTICS AND ANALYTICS
    # =====================================================
    
    def get_discount_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about discounts."""
        try:
            # Total counts
            total_count = self.count()
            active_count = self.count({'is_active': True})
            promotional_count = self.count({'is_promotional': True, 'is_active': True})
            
            # Count by discount type
            type_query = select(
                PricingDiscount.discount_type,
                func.count(PricingDiscount.id).label('count')
            ).where(
                PricingDiscount.is_active == True
            ).group_by(PricingDiscount.discount_type)
            
            type_counts = {}
            for row in self.db.execute(type_query):
                type_counts[row.discount_type.value if row.discount_type else 'unknown'] = row.count
            
            # Count by discount scope
            scope_query = select(
                PricingDiscount.discount_scope,
                func.count(PricingDiscount.id).label('count')
            ).where(
                PricingDiscount.is_active == True
            ).group_by(PricingDiscount.discount_scope)
            
            scope_counts = {}
            for row in self.db.execute(scope_query):
                scope_counts[row.discount_scope.value if row.discount_scope else 'unknown'] = row.count
            
            # Usage statistics
            usage_query = select(
                func.sum(PricingDiscount.current_use_count).label('total_uses'),
                func.avg(PricingDiscount.current_use_count).label('avg_uses'),
                func.max(PricingDiscount.current_use_count).label('max_uses')
            ).where(
                and_(
                    PricingDiscount.is_active == True,
                    PricingDiscount.current_use_count.is_not(None)
                )
            )
            
            usage_stats = self.db.execute(usage_query).first()
            
            # Stackability analysis
            stackable_count = self.count({'is_stackable': True, 'is_active': True})
            non_stackable_count = active_count - stackable_count
            
            return {
                'total_discounts': total_count,
                'active_discounts': active_count,
                'inactive_discounts': total_count - active_count,
                'promotional_discounts': promotional_count,
                'by_discount_type': type_counts,
                'by_discount_scope': scope_counts,
                'usage_statistics': {
                    'total_uses': int(usage_stats.total_uses) if usage_stats.total_uses else 0,
                    'average_uses': float(usage_stats.avg_uses) if usage_stats.avg_uses else 0,
                    'max_uses': int(usage_stats.max_uses) if usage_stats.max_uses else 0
                },
                'stackability': {
                    'stackable_discounts': stackable_count,
                    'non_stackable_discounts': non_stackable_count,
                    'stackable_percentage': (stackable_count / active_count * 100) if active_count > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get discount statistics: {str(e)}")
            return {}
    
    def get_campaign_performance_report(self, start_date: datetime = None, 
                                      end_date: datetime = None) -> Dict[str, Any]:
        """
        Generate a performance report for promotional campaigns.
        
        Args:
            start_date: Start date for report period
            end_date: End date for report period
            
        Returns:
            Campaign performance data
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)  # Last 30 days
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get promotional campaigns in the period
            filters = [
                PricingDiscount.is_promotional == True,
                or_(
                    and_(
                        PricingDiscount.promotion_start_date >= start_date,
                        PricingDiscount.promotion_start_date <= end_date
                    ),
                    and_(
                        PricingDiscount.promotion_end_date >= start_date,
                        PricingDiscount.promotion_end_date <= end_date
                    )
                )
            ]
            
            query = select(PricingDiscount).where(and_(*filters))
            campaigns = list(self.db.scalars(query))
            
            campaign_data = []
            total_usage = 0
            
            for campaign in campaigns:
                usage_count = campaign.current_use_count or 0
                usage_limit = campaign.max_uses_total
                
                campaign_info = {
                    'campaign_name': campaign.campaign_name,
                    'campaign_code': campaign.campaign_code,
                    'discount_code': campaign.code,
                    'discount_type': campaign.discount_type.value,
                    'start_date': campaign.promotion_start_date.isoformat() if campaign.promotion_start_date else None,
                    'end_date': campaign.promotion_end_date.isoformat() if campaign.promotion_end_date else None,
                    'usage_count': usage_count,
                    'usage_limit': usage_limit,
                    'usage_percentage': (usage_count / usage_limit * 100) if usage_limit else None,
                    'is_active': campaign.is_active
                }
                
                campaign_data.append(campaign_info)
                total_usage += usage_count
            
            return {
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_campaigns': len(campaigns),
                    'active_campaigns': len([c for c in campaigns if c.is_active]),
                    'total_usage': total_usage,
                    'average_usage_per_campaign': total_usage / len(campaigns) if campaigns else 0
                },
                'campaigns': campaign_data
            }
            
        except Exception as e:
            logger.error(f"Failed to generate campaign performance report: {str(e)}")
            return {}

    # =====================================================
    # BULK OPERATIONS
    # =====================================================
    
    def bulk_extend_campaign_dates(self, campaign_codes: List[str], extension_days: int,
                                  updated_by: UUID = None) -> int:
        """
        Bulk extend campaign end dates by specified number of days.
        
        Args:
            campaign_codes: List of campaign codes to extend
            extension_days: Number of days to extend campaigns
            updated_by: User performing the update
            
        Returns:
            Number of campaigns extended
        """
        try:
            extended_count = 0
            
            for campaign_code in campaign_codes:
                campaigns = self.get_by_campaign_code(campaign_code)
                for campaign in campaigns:
                    if campaign.promotion_end_date:
                        new_end_date = campaign.promotion_end_date + timedelta(days=extension_days)
                        update_data = {
                            'promotion_end_date': new_end_date,
                            'updated_by': updated_by,
                            'updated_at': datetime.utcnow()
                        }
                        
                        if self.update(campaign.id, update_data):
                            extended_count += 1
            
            logger.info(f"Extended {extended_count} campaigns by {extension_days} days")
            return extended_count
            
        except Exception as e:
            logger.error(f"Failed to bulk extend campaign dates: {str(e)}")
            return 0
    
    def bulk_deactivate_expired_campaigns(self, updated_by: UUID = None) -> int:
        """
        Bulk deactivate campaigns that have passed their end date.
        
        Args:
            updated_by: User performing the update
            
        Returns:
            Number of campaigns deactivated
        """
        try:
            now = datetime.utcnow()
            
            query = select(PricingDiscount).where(
                and_(
                    PricingDiscount.is_active == True,
                    PricingDiscount.is_promotional == True,
                    PricingDiscount.promotion_end_date.is_not(None),
                    PricingDiscount.promotion_end_date <= now
                )
            )
            
            expired_campaigns = list(self.db.scalars(query))
            deactivated_count = 0
            
            update_data = {
                'is_active': False,
                'updated_by': updated_by,
                'updated_at': now
            }
            
            for campaign in expired_campaigns:
                if self.update(campaign.id, update_data):
                    deactivated_count += 1
            
            logger.info(f"Deactivated {deactivated_count} expired campaigns")
            return deactivated_count
            
        except Exception as e:
            logger.error(f"Failed to bulk deactivate expired campaigns: {str(e)}")
            return 0

    # =====================================================
    # VALIDATION METHODS
    # =====================================================
    
    def _validate_discount_data(self, discount_data: Dict[str, Any]) -> None:
        """
        Validate discount data according to business rules.
        
        Args:
            discount_data: Discount data to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Check required fields
        required_fields = ['code', 'name', 'discount_type', 'discount_scope']
        for field in required_fields:
            if field not in discount_data or not discount_data[field]:
                raise ValidationError(f"Required field missing: {field}")
        
        discount_type = discount_data.get('discount_type')
        
        # Validate based on discount type
        if discount_type == DiscountType.PERCENTAGE:
            percentage_value = discount_data.get('percentage_value')
            if not percentage_value or percentage_value <= 0 or percentage_value > 100:
                raise ValidationError("Percentage value must be between 0 and 100")
        
        elif discount_type == DiscountType.FIXED_AMOUNT:
            fixed_amount = discount_data.get('fixed_amount')
            if not fixed_amount or fixed_amount <= 0:
                raise ValidationError("Fixed amount must be greater than 0")
        
        elif discount_type == DiscountType.TIERED:
            tier_structure = discount_data.get('tier_structure')
            if not tier_structure or 'tiers' not in tier_structure:
                raise ValidationError("Tiered discount must have tier structure defined")
        
        # Validate promotional date ranges
        promotion_start = discount_data.get('promotion_start_date')
        promotion_end = discount_data.get('promotion_end_date')
        if promotion_start and promotion_end and promotion_start >= promotion_end:
            raise ValidationError("Promotion start date must be before end date")
        
        # Validate usage limits
        max_uses_total = discount_data.get('max_uses_total')
        max_uses_per_customer = discount_data.get('max_uses_per_customer')
        if max_uses_total and max_uses_per_customer:
            if max_uses_per_customer > max_uses_total:
                raise ValidationError("Max uses per customer cannot exceed total max uses")
        
        # Validate code uniqueness
        code = discount_data.get('code')
        if code:
            existing = self.get_by_code(code)
            discount_id = discount_data.get('id')
            if existing and str(existing.id) != str(discount_id):
                raise ValidationError(f"Discount code '{code}' already exists")
        
        # Validate min/max discount amounts
        min_discount = discount_data.get('min_discount_amount')
        max_discount = discount_data.get('max_discount_amount')
        if min_discount and max_discount and min_discount >= max_discount:
            raise ValidationError("Minimum discount amount must be less than maximum discount amount")
    
    def _check_customer_usage_limit(self, discount: PricingDiscount, customer_id: str) -> bool:
        """
        Check if customer has not exceeded usage limit for the discount.
        Note: This is a placeholder - actual implementation would require usage tracking table.
        
        Args:
            discount: Discount to check
            customer_id: Customer ID
            
        Returns:
            True if customer can use the discount
        """
        # TODO: Implement actual customer usage tracking
        # This would require a separate table to track discount usage by customer
        return True

    # =====================================================
    # SEARCH AND FILTERING
    # =====================================================
    
    def search_discounts(self, search_term: str, filters: Dict[str, Any] = None) -> List[PricingDiscount]:
        """
        Search discounts by multiple criteria.
        
        Args:
            search_term: Text to search for in code, name, and description
            filters: Additional filters to apply
            
        Returns:
            List of matching discounts
        """
        try:
            search_fields = ['code', 'name', 'description']
            results = self.search(search_term, search_fields)
            
            # Apply additional filters if provided
            if filters:
                filtered_results = []
                for discount in results:
                    match = True
                    for field, value in filters.items():
                        if hasattr(discount, field):
                            if getattr(discount, field) != value:
                                match = False
                                break
                    if match:
                        filtered_results.append(discount)
                results = filtered_results
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search discounts: {str(e)}")
            return []