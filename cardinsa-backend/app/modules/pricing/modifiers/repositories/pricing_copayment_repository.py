# app/modules/pricing/modifiers/repositories/pricing_copayment_repository.py

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, and_, or_, func, desc, asc, case
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from app.core.base_repository import BaseRepository
from app.core.exceptions import NotFoundError, ValidationError, DatabaseOperationError
from app.modules.pricing.modifiers.models.pricing_copayment_model import (
    PricingCopayment, CopaymentType, ServiceTier
)
from app.modules.pricing.modifiers.schemas.pricing_copayment_schema import (
    PricingCopaymentCreate,
    PricingCopaymentUpdate,
)
from app.core.logging import get_app_logger

logger = get_app_logger("pricing.copayment.repository")

class PricingCopaymentRepository(BaseRepository):
    """
    Repository for Pricing Copayment operations.
    
    Provides comprehensive data access methods for copayment management
    including tiered copayments, service-specific configurations,
    and network tier integrations.
    
    Key Features:
    - Full CRUD operations with validation
    - Tiered copayment structure queries
    - Service category and network filtering
    - Performance-optimized queries
    - Business rule validation
    - Statistical analysis methods
    """
    
    def __init__(self, db: Session):
        super().__init__(PricingCopayment, db)

    # =====================================================
    # ENHANCED CRUD OPERATIONS
    # =====================================================
    
    def create_copayment(self, copayment_data: PricingCopaymentCreate, created_by: UUID = None) -> PricingCopayment:
        """
        Create a new pricing copayment with validation and audit logging.
        
        Args:
            copayment_data: Copayment creation data
            created_by: User ID creating the copayment
            
        Returns:
            Created PricingCopayment instance
            
        Raises:
            ValidationError: If validation fails
            DatabaseOperationError: If database operation fails
        """
        try:
            # Convert Pydantic model to dict
            copayment_dict = copayment_data.model_dump(exclude_unset=True)
            
            # Add audit information
            if created_by:
                copayment_dict['created_by'] = created_by
            
            # Validate business rules before creation
            self._validate_copayment_data(copayment_dict)
            
            # Create the copayment
            copayment = self.create(copayment_dict)
            
            logger.info(f"Created copayment: {copayment.code} by user: {created_by}")
            return copayment
            
        except Exception as e:
            logger.error(f"Failed to create copayment: {str(e)}")
            raise DatabaseOperationError(f"Failed to create copayment: {str(e)}")
    
    def update_copayment(self, copayment_id: UUID, copayment_data: PricingCopaymentUpdate, 
                        updated_by: UUID = None) -> PricingCopayment:
        """
        Update an existing pricing copayment with validation and audit logging.
        
        Args:
            copayment_id: ID of copayment to update
            copayment_data: Updated copayment data
            updated_by: User ID updating the copayment
            
        Returns:
            Updated PricingCopayment instance
            
        Raises:
            NotFoundError: If copayment not found
            ValidationError: If validation fails
        """
        try:
            # Get existing copayment
            existing_copayment = self.get(copayment_id)
            if not existing_copayment:
                raise NotFoundError(f"Copayment not found with ID: {copayment_id}")
            
            # Convert update data to dict
            update_dict = copayment_data.model_dump(exclude_unset=True, exclude_none=True)
            
            # Add audit information
            if updated_by:
                update_dict['updated_by'] = updated_by
            
            # Validate business rules
            merged_data = {**existing_copayment.to_dict(), **update_dict}
            self._validate_copayment_data(merged_data)
            
            # Update the copayment
            updated_copayment = self.update(copayment_id, update_dict)
            
            logger.info(f"Updated copayment: {existing_copayment.code} by user: {updated_by}")
            return updated_copayment
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update copayment {copayment_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update copayment: {str(e)}")

    # =====================================================
    # BUSINESS-SPECIFIC QUERY METHODS
    # =====================================================
    
    def get_by_code(self, code: str) -> Optional[PricingCopayment]:
        """Get copayment by unique code."""
        try:
            return self.get_by_field('code', code)
        except Exception as e:
            logger.error(f"Failed to get copayment by code {code}: {str(e)}")
            return None
    
    def get_by_service_category(self, service_category: str, network_tier: str = None) -> List[PricingCopayment]:
        """
        Get copayments for a specific service category and optional network tier.
        
        Args:
            service_category: Service category to filter by
            network_tier: Optional network tier filter
            
        Returns:
            List of applicable copayments
        """
        try:
            filters = [
                PricingCopayment.is_active == True,
                PricingCopayment.service_category == service_category
            ]
            
            if network_tier:
                filters.append(
                    or_(
                        PricingCopayment.network_tier == network_tier,
                        PricingCopayment.network_tier.is_(None)
                    )
                )
            
            query = select(PricingCopayment).where(
                and_(*filters)
            ).order_by(PricingCopayment.calculation_order, PricingCopayment.priority)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get copayments for service category {service_category}: {str(e)}")
            return []
    
    def get_tiered_copayments(self, service_category: str = None) -> List[PricingCopayment]:
        """
        Get all tiered copayment structures.
        
        Args:
            service_category: Optional service category filter
            
        Returns:
            List of tiered copayments
        """
        try:
            filters = [
                PricingCopayment.is_active == True,
                PricingCopayment.copayment_type == CopaymentType.TIERED
            ]
            
            if service_category:
                filters.append(PricingCopayment.service_category == service_category)
            
            query = select(PricingCopayment).where(
                and_(*filters)
            ).order_by(PricingCopayment.service_category, PricingCopayment.priority)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get tiered copayments: {str(e)}")
            return []
    
    def get_by_copayment_type(self, copayment_type: CopaymentType) -> List[PricingCopayment]:
        """Get copayments filtered by type."""
        try:
            return self.get_multi(
                filters={'copayment_type': copayment_type, 'is_active': True},
                order_by='service_category'
            )
        except Exception as e:
            logger.error(f"Failed to get copayments by type {copayment_type.value}: {str(e)}")
            return []
    
    def get_by_profile_id(self, profile_id: UUID) -> List[PricingCopayment]:
        """Get all copayments associated with a pricing profile."""
        try:
            return self.get_multi(filters={'profile_id': profile_id, 'is_active': True})
        except Exception as e:
            logger.error(f"Failed to get copayments for profile {profile_id}: {str(e)}")
            return []
    
    def get_percentage_copayments(self, min_percentage: float = None, max_percentage: float = None) -> List[PricingCopayment]:
        """
        Get percentage-based copayments with optional percentage range filtering.
        
        Args:
            min_percentage: Minimum percentage filter
            max_percentage: Maximum percentage filter
            
        Returns:
            List of percentage-based copayments
        """
        try:
            filters = [
                PricingCopayment.is_active == True,
                PricingCopayment.copayment_type == CopaymentType.PERCENTAGE
            ]
            
            if min_percentage is not None:
                filters.append(PricingCopayment.percentage >= min_percentage)
            
            if max_percentage is not None:
                filters.append(PricingCopayment.percentage <= max_percentage)
            
            query = select(PricingCopayment).where(
                and_(*filters)
            ).order_by(PricingCopayment.percentage, PricingCopayment.service_category)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get percentage copayments: {str(e)}")
            return []
    
    def get_fixed_amount_copayments(self, currency: str = "USD") -> List[PricingCopayment]:
        """Get fixed amount copayments for a specific currency."""
        try:
            filters = {
                'copayment_type': CopaymentType.FIXED_AMOUNT,
                'currency': currency,
                'is_active': True
            }
            
            return self.get_multi(
                filters=filters,
                order_by='fixed_amount'
            )
        except Exception as e:
            logger.error(f"Failed to get fixed amount copayments for {currency}: {str(e)}")
            return []

    # =====================================================
    # BUSINESS LOGIC QUERIES
    # =====================================================
    
    def find_applicable_copayments(self, service_type: str, network_tier: str = None,
                                 service_tier: str = None) -> List[PricingCopayment]:
        """
        Find copayments applicable to specific service and network criteria.
        
        Args:
            service_type: Type of service
            network_tier: Network tier (in_network, out_of_network, etc.)
            service_tier: Service tier for tiered copayments
            
        Returns:
            List of applicable copayments
        """
        try:
            filters = [
                PricingCopayment.is_active == True,
                PricingCopayment.service_category == service_type
            ]
            
            # Network tier filtering
            if network_tier:
                filters.append(
                    or_(
                        PricingCopayment.network_tier == network_tier,
                        PricingCopayment.network_tier.is_(None)
                    )
                )
            
            # Service tier filtering for tiered copayments
            if service_tier:
                filters.append(
                    or_(
                        PricingCopayment.service_tier.is_(None),
                        PricingCopayment.service_tier == ServiceTier(service_tier)
                    )
                )
            
            query = select(PricingCopayment).where(
                and_(*filters)
            ).order_by(PricingCopayment.calculation_order, PricingCopayment.priority)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to find applicable copayments: {str(e)}")
            return []
    
    def get_copayments_with_limits(self, has_min_limit: bool = None, has_max_limit: bool = None) -> List[PricingCopayment]:
        """
        Get copayments filtered by whether they have min/max limits.
        
        Args:
            has_min_limit: Filter by presence of minimum copay limit
            has_max_limit: Filter by presence of maximum copay limit
            
        Returns:
            List of copayments matching criteria
        """
        try:
            filters = [PricingCopayment.is_active == True]
            
            if has_min_limit is not None:
                if has_min_limit:
                    filters.append(PricingCopayment.min_copay.is_not(None))
                else:
                    filters.append(PricingCopayment.min_copay.is_(None))
            
            if has_max_limit is not None:
                if has_max_limit:
                    filters.append(PricingCopayment.max_copay.is_not(None))
                else:
                    filters.append(PricingCopayment.max_copay.is_(None))
            
            query = select(PricingCopayment).where(
                and_(*filters)
            ).order_by(PricingCopayment.service_category)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get copayments with limits: {str(e)}")
            return []
    
    def get_copayments_by_deductible_interaction(self, applies_to_deductible: bool = None,
                                               applies_after_deductible: bool = None) -> List[PricingCopayment]:
        """
        Get copayments based on their deductible interaction settings.
        
        Args:
            applies_to_deductible: Filter by whether copay counts toward deductible
            applies_after_deductible: Filter by whether copay applies after deductible
            
        Returns:
            List of copayments matching criteria
        """
        try:
            filters = [PricingCopayment.is_active == True]
            
            if applies_to_deductible is not None:
                filters.append(PricingCopayment.applies_to_deductible == applies_to_deductible)
            
            if applies_after_deductible is not None:
                filters.append(PricingCopayment.applies_after_deductible == applies_after_deductible)
            
            query = select(PricingCopayment).where(
                and_(*filters)
            ).order_by(PricingCopayment.calculation_order)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get copayments by deductible interaction: {str(e)}")
            return []

    # =====================================================
    # STATISTICS AND ANALYTICS
    # =====================================================
    
    def get_copayment_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about copayments."""
        try:
            # Total counts
            total_count = self.count()
            active_count = self.count({'is_active': True})
            
            # Count by copayment type
            type_query = select(
                PricingCopayment.copayment_type,
                func.count(PricingCopayment.id).label('count')
            ).where(
                PricingCopayment.is_active == True
            ).group_by(PricingCopayment.copayment_type)
            
            type_counts = {}
            for row in self.db.execute(type_query):
                type_counts[row.copayment_type.value if row.copayment_type else 'unknown'] = row.count
            
            # Count by service category
            category_query = select(
                PricingCopayment.service_category,
                func.count(PricingCopayment.id).label('count')
            ).where(
                PricingCopayment.is_active == True
            ).group_by(PricingCopayment.service_category)
            
            category_counts = {}
            for row in self.db.execute(category_query):
                category_counts[row.service_category or 'unspecified'] = row.count
            
            # Fixed amount statistics
            fixed_amount_query = select(
                func.min(PricingCopayment.fixed_amount).label('min_amount'),
                func.max(PricingCopayment.fixed_amount).label('max_amount'),
                func.avg(PricingCopayment.fixed_amount).label('avg_amount')
            ).where(
                and_(
                    PricingCopayment.is_active == True,
                    PricingCopayment.copayment_type == CopaymentType.FIXED_AMOUNT,
                    PricingCopayment.fixed_amount.is_not(None)
                )
            )
            
            fixed_stats = self.db.execute(fixed_amount_query).first()
            
            # Percentage statistics
            percentage_query = select(
                func.min(PricingCopayment.percentage).label('min_percentage'),
                func.max(PricingCopayment.percentage).label('max_percentage'),
                func.avg(PricingCopayment.percentage).label('avg_percentage')
            ).where(
                and_(
                    PricingCopayment.is_active == True,
                    PricingCopayment.copayment_type == CopaymentType.PERCENTAGE,
                    PricingCopayment.percentage.is_not(None)
                )
            )
            
            percentage_stats = self.db.execute(percentage_query).first()
            
            return {
                'total_copayments': total_count,
                'active_copayments': active_count,
                'inactive_copayments': total_count - active_count,
                'by_copayment_type': type_counts,
                'by_service_category': category_counts,
                'fixed_amount_statistics': {
                    'min_amount': float(fixed_stats.min_amount) if fixed_stats.min_amount else 0,
                    'max_amount': float(fixed_stats.max_amount) if fixed_stats.max_amount else 0,
                    'avg_amount': float(fixed_stats.avg_amount) if fixed_stats.avg_amount else 0
                },
                'percentage_statistics': {
                    'min_percentage': float(percentage_stats.min_percentage) if percentage_stats.min_percentage else 0,
                    'max_percentage': float(percentage_stats.max_percentage) if percentage_stats.max_percentage else 0,
                    'avg_percentage': float(percentage_stats.avg_percentage) if percentage_stats.avg_percentage else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get copayment statistics: {str(e)}")
            return {}
    
    def get_tier_distribution_analysis(self) -> Dict[str, Any]:
        """Analyze distribution of tiered copayment structures."""
        try:
            # Get all tiered copayments
            tiered_copayments = self.get_tiered_copayments()
            
            tier_analysis = {
                'total_tiered_copayments': len(tiered_copayments),
                'tiers_used': {'tier_1': 0, 'tier_2': 0, 'tier_3': 0, 'tier_4': 0},
                'service_categories_with_tiers': set(),
                'average_tier_amounts': {}
            }
            
            tier_amounts = {'tier_1': [], 'tier_2': [], 'tier_3': [], 'tier_4': []}
            
            for copayment in tiered_copayments:
                tier_analysis['service_categories_with_tiers'].add(copayment.service_category)
                
                for tier_num in range(1, 5):
                    tier_amount = getattr(copayment, f'tier_{tier_num}_amount')
                    if tier_amount is not None:
                        tier_analysis['tiers_used'][f'tier_{tier_num}'] += 1
                        tier_amounts[f'tier_{tier_num}'].append(float(tier_amount))
            
            # Calculate average amounts per tier
            for tier, amounts in tier_amounts.items():
                if amounts:
                    tier_analysis['average_tier_amounts'][tier] = sum(amounts) / len(amounts)
                else:
                    tier_analysis['average_tier_amounts'][tier] = 0
            
            tier_analysis['service_categories_with_tiers'] = list(tier_analysis['service_categories_with_tiers'])
            
            return tier_analysis
            
        except Exception as e:
            logger.error(f"Failed to get tier distribution analysis: {str(e)}")
            return {}

    # =====================================================
    # BULK OPERATIONS
    # =====================================================
    
    def bulk_update_network_tier(self, service_category: str, old_network_tier: str,
                                new_network_tier: str, updated_by: UUID = None) -> int:
        """
        Bulk update network tier for copayments in a specific service category.
        
        Args:
            service_category: Service category to filter by
            old_network_tier: Current network tier to replace
            new_network_tier: New network tier
            updated_by: User performing the update
            
        Returns:
            Number of copayments updated
        """
        try:
            filters = {
                'service_category': service_category,
                'network_tier': old_network_tier,
                'is_active': True
            }
            
            update_data = {'network_tier': new_network_tier}
            if updated_by:
                update_data['updated_by'] = updated_by
                update_data['updated_at'] = datetime.utcnow()
            
            copayments_to_update = self.get_multi(filters=filters)
            updated_count = 0
            
            for copayment in copayments_to_update:
                if self.update(copayment.id, update_data):
                    updated_count += 1
            
            logger.info(f"Bulk updated {updated_count} copayments network tier from {old_network_tier} to {new_network_tier}")
            return updated_count
            
        except Exception as e:
            logger.error(f"Failed to bulk update network tier: {str(e)}")
            return 0
    
    def bulk_adjust_fixed_amounts(self, service_category: str, adjustment_percentage: float,
                                 updated_by: UUID = None) -> int:
        """
        Bulk adjust fixed amounts for copayments by a percentage.
        
        Args:
            service_category: Service category to filter by
            adjustment_percentage: Percentage to adjust amounts (e.g., 5.0 for 5% increase)
            updated_by: User performing the update
            
        Returns:
            Number of copayments updated
        """
        try:
            filters = {
                'service_category': service_category,
                'copayment_type': CopaymentType.FIXED_AMOUNT,
                'is_active': True
            }
            
            copayments_to_update = self.get_multi(filters=filters)
            updated_count = 0
            adjustment_factor = 1 + (adjustment_percentage / 100)
            
            for copayment in copayments_to_update:
                if copayment.fixed_amount:
                    new_amount = copayment.fixed_amount * Decimal(str(adjustment_factor))
                    update_data = {
                        'fixed_amount': new_amount,
                        'updated_by': updated_by,
                        'updated_at': datetime.utcnow()
                    }
                    
                    if self.update(copayment.id, update_data):
                        updated_count += 1
            
            logger.info(f"Bulk adjusted {updated_count} copayment amounts by {adjustment_percentage}%")
            return updated_count
            
        except Exception as e:
            logger.error(f"Failed to bulk adjust fixed amounts: {str(e)}")
            return 0

    # =====================================================
    # VALIDATION METHODS
    # =====================================================
    
    def _validate_copayment_data(self, copayment_data: Dict[str, Any]) -> None:
        """
        Validate copayment data according to business rules.
        
        Args:
            copayment_data: Copayment data to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Check required fields
        required_fields = ['code', 'label', 'copayment_type', 'service_category']
        for field in required_fields:
            if field not in copayment_data or not copayment_data[field]:
                raise ValidationError(f"Required field missing: {field}")
        
        copayment_type = copayment_data.get('copayment_type')
        
        # Validate based on copayment type
        if copayment_type == CopaymentType.FIXED_AMOUNT:
            fixed_amount = copayment_data.get('fixed_amount')
            if not fixed_amount or fixed_amount <= 0:
                raise ValidationError("Fixed amount must be greater than 0")
        
        elif copayment_type == CopaymentType.PERCENTAGE:
            percentage = copayment_data.get('percentage')
            if not percentage or percentage <= 0 or percentage > 100:
                raise ValidationError("Percentage must be between 0 and 100")
        
        elif copayment_type == CopaymentType.TIERED:
            # Validate at least one tier has an amount
            tier_amounts = [
                copayment_data.get('tier_1_amount'),
                copayment_data.get('tier_2_amount'),
                copayment_data.get('tier_3_amount'),
                copayment_data.get('tier_4_amount')
            ]
            if not any(amount and amount > 0 for amount in tier_amounts):
                raise ValidationError("At least one tier amount must be specified and greater than 0")
        
        # Validate min/max limits for percentage copayments
        min_copay = copayment_data.get('min_copay')
        max_copay = copayment_data.get('max_copay')
        if min_copay is not None and max_copay is not None and min_copay >= max_copay:
            raise ValidationError("Minimum copay must be less than maximum copay")
        
        # Validate code uniqueness
        code = copayment_data.get('code')
        if code:
            existing = self.get_by_code(code)
            copayment_id = copayment_data.get('id')
            if existing and str(existing.id) != str(copayment_id):
                raise ValidationError(f"Copayment code '{code}' already exists")
        
        # Validate currency code
        currency = copayment_data.get('currency', 'USD')
        if len(currency) != 3:
            raise ValidationError("Currency must be a 3-letter ISO code")
        
        # Validate effective/expiration dates
        effective_date = copayment_data.get('effective_date')
        expiration_date = copayment_data.get('expiration_date')
        if effective_date and expiration_date and effective_date >= expiration_date:
            raise ValidationError("Effective date must be before expiration date")

    # =====================================================
    # SEARCH AND FILTERING
    # =====================================================
    
    def search_copayments(self, search_term: str, filters: Dict[str, Any] = None) -> List[PricingCopayment]:
        """
        Search copayments by multiple criteria.
        
        Args:
            search_term: Text to search for in code, label, and description
            filters: Additional filters to apply
            
        Returns:
            List of matching copayments
        """
        try:
            search_fields = ['code', 'label', 'description']
            results = self.search(search_term, search_fields)
            
            # Apply additional filters if provided
            if filters:
                filtered_results = []
                for copayment in results:
                    match = True
                    for field, value in filters.items():
                        if hasattr(copayment, field):
                            if getattr(copayment, field) != value:
                                match = False
                                break
                    if match:
                        filtered_results.append(copayment)
                results = filtered_results
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search copayments: {str(e)}")
            return []
    
    def get_copayments_by_amount_range(self, min_amount: Decimal = None, max_amount: Decimal = None,
                                     copayment_type: CopaymentType = CopaymentType.FIXED_AMOUNT) -> List[PricingCopayment]:
        """
        Get copayments within a specific amount range.
        
        Args:
            min_amount: Minimum amount filter
            max_amount: Maximum amount filter
            copayment_type: Type of copayment to filter by
            
        Returns:
            List of copayments within the specified range
        """
        try:
            filters = [
                PricingCopayment.is_active == True,
                PricingCopayment.copayment_type == copayment_type
            ]
            
            if copayment_type == CopaymentType.FIXED_AMOUNT:
                if min_amount is not None:
                    filters.append(PricingCopayment.fixed_amount >= min_amount)
                if max_amount is not None:
                    filters.append(PricingCopayment.fixed_amount <= max_amount)
                    
                query = select(PricingCopayment).where(
                    and_(*filters)
                ).order_by(PricingCopayment.fixed_amount)
                
            elif copayment_type == CopaymentType.PERCENTAGE:
                if min_amount is not None:
                    filters.append(PricingCopayment.percentage >= min_amount)
                if max_amount is not None:
                    filters.append(PricingCopayment.percentage <= max_amount)
                    
                query = select(PricingCopayment).where(
                    and_(*filters)
                ).order_by(PricingCopayment.percentage)
            else:
                query = select(PricingCopayment).where(and_(*filters))
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get copayments by amount range: {str(e)}")
            return []