# app/modules/pricing/modifiers/repositories/pricing_deductible_repository.py

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, and_, or_, func, desc, asc
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from app.core.base_repository import BaseRepository
from app.core.exceptions import NotFoundError, ValidationError, DatabaseOperationError
from app.modules.pricing.modifiers.models.pricing_deductible_model import PricingDeductible
from app.modules.pricing.modifiers.schemas.pricing_deductible_schema import (
    PricingDeductibleCreate,
    PricingDeductibleUpdate,
)
from app.core.logging import get_app_logger

logger = get_app_logger("pricing.deductible.repository")

class PricingDeductibleRepository(BaseRepository):
    """
    Repository for Pricing Deductible operations.
    
    Provides comprehensive data access methods for deductible management
    including business-specific queries, validation, and performance optimization.
    
    Key Features:
    - Full CRUD operations with validation
    - Business-specific query methods
    - Performance-optimized queries with eager loading
    - Service category and type filtering
    - Integration with pricing profiles
    - Audit trail support
    - Caching-ready architecture
    """
    
    def __init__(self, db: Session):
        super().__init__(PricingDeductible, db)

    # =====================================================
    # ENHANCED CRUD OPERATIONS
    # =====================================================
    
    def create_deductible(self, deductible_data: PricingDeductibleCreate, created_by: UUID = None) -> PricingDeductible:
        """
        Create a new pricing deductible with validation and audit logging.
        
        Args:
            deductible_data: Deductible creation data
            created_by: User ID creating the deductible
            
        Returns:
            Created PricingDeductible instance
            
        Raises:
            ValidationError: If validation fails
            DatabaseOperationError: If database operation fails
        """
        try:
            # Convert Pydantic model to dict
            deductible_dict = deductible_data.model_dump(exclude_unset=True)
            
            # Add audit information
            if created_by:
                deductible_dict['created_by'] = created_by
            
            # Validate business rules before creation
            self._validate_deductible_data(deductible_dict)
            
            # Create the deductible
            deductible = self.create(deductible_dict)
            
            logger.info(f"Created deductible: {deductible.code} by user: {created_by}")
            return deductible
            
        except Exception as e:
            logger.error(f"Failed to create deductible: {str(e)}")
            raise DatabaseOperationError(f"Failed to create deductible: {str(e)}")
    
    def update_deductible(self, deductible_id: UUID, deductible_data: PricingDeductibleUpdate, 
                         updated_by: UUID = None) -> PricingDeductible:
        """
        Update an existing pricing deductible with validation and audit logging.
        
        Args:
            deductible_id: ID of deductible to update
            deductible_data: Updated deductible data
            updated_by: User ID updating the deductible
            
        Returns:
            Updated PricingDeductible instance
            
        Raises:
            NotFoundError: If deductible not found
            ValidationError: If validation fails
        """
        try:
            # Get existing deductible
            existing_deductible = self.get(deductible_id)
            if not existing_deductible:
                raise NotFoundError(f"Deductible not found with ID: {deductible_id}")
            
            # Convert update data to dict
            update_dict = deductible_data.model_dump(exclude_unset=True, exclude_none=True)
            
            # Add audit information
            if updated_by:
                update_dict['updated_by'] = updated_by
            
            # Validate business rules
            merged_data = {**existing_deductible.to_dict(), **update_dict}
            self._validate_deductible_data(merged_data)
            
            # Update the deductible
            updated_deductible = self.update(deductible_id, update_dict)
            
            logger.info(f"Updated deductible: {existing_deductible.code} by user: {updated_by}")
            return updated_deductible
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update deductible {deductible_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update deductible: {str(e)}")

    # =====================================================
    # BUSINESS-SPECIFIC QUERY METHODS
    # =====================================================
    
    def get_by_code(self, code: str) -> Optional[PricingDeductible]:
        """Get deductible by unique code."""
        try:
            return self.get_by_field('code', code)
        except Exception as e:
            logger.error(f"Failed to get deductible by code {code}: {str(e)}")
            return None
    
    def get_by_service_category(self, service_category: str, include_global: bool = True) -> List[PricingDeductible]:
        """
        Get all deductibles for a specific service category.
        
        Args:
            service_category: Service category to filter by
            include_global: Whether to include global deductibles (no specific category)
            
        Returns:
            List of applicable deductibles
        """
        try:
            query = select(PricingDeductible).where(
                and_(
                    PricingDeductible.is_active == True,
                    or_(
                        PricingDeductible.service_category == service_category,
                        PricingDeductible.service_category.is_(None) if include_global else False
                    )
                )
            ).order_by(PricingDeductible.calculation_order, PricingDeductible.priority)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get deductibles for service category {service_category}: {str(e)}")
            return []
    
    def get_by_profile_id(self, profile_id: UUID) -> List[PricingDeductible]:
        """Get all deductibles associated with a pricing profile."""
        try:
            return self.get_multi(filters={'profile_id': profile_id, 'is_active': True})
        except Exception as e:
            logger.error(f"Failed to get deductibles for profile {profile_id}: {str(e)}")
            return []
    
    def get_active_deductibles(self, as_of_date: datetime = None) -> List[PricingDeductible]:
        """
        Get all active deductibles, optionally as of a specific date.
        
        Args:
            as_of_date: Date to check for validity (defaults to now)
            
        Returns:
            List of active deductibles
        """
        try:
            if not as_of_date:
                as_of_date = datetime.utcnow()
            
            query = select(PricingDeductible).where(
                and_(
                    PricingDeductible.is_active == True,
                    PricingDeductible.effective_date <= as_of_date,
                    or_(
                        PricingDeductible.expiration_date.is_(None),
                        PricingDeductible.expiration_date > as_of_date
                    )
                )
            ).order_by(PricingDeductible.service_category, PricingDeductible.deductible_type)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get active deductibles: {str(e)}")
            return []
    
    def get_deductibles_by_type(self, deductible_type: str) -> List[PricingDeductible]:
        """Get deductibles filtered by type (individual, family, etc.)."""
        try:
            return self.get_multi(
                filters={'deductible_type': deductible_type, 'is_active': True},
                order_by='amount'
            )
        except Exception as e:
            logger.error(f"Failed to get deductibles by type {deductible_type}: {str(e)}")
            return []
    
    def get_hierarchical_deductibles(self, parent_id: UUID = None) -> List[PricingDeductible]:
        """
        Get deductibles in hierarchical order.
        
        Args:
            parent_id: Parent deductible ID (None for root level)
            
        Returns:
            List of deductibles at the specified hierarchy level
        """
        try:
            query = select(PricingDeductible).where(
                and_(
                    PricingDeductible.is_active == True,
                    PricingDeductible.parent_id == parent_id
                )
            ).order_by(PricingDeductible.priority, PricingDeductible.amount)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get hierarchical deductibles for parent {parent_id}: {str(e)}")
            return []

    # =====================================================
    # BUSINESS LOGIC QUERIES
    # =====================================================
    
    def find_applicable_deductibles(self, service_type: str, amount: Decimal, 
                                  customer_type: str = "individual") -> List[PricingDeductible]:
        """
        Find deductibles applicable to a specific service and amount.
        
        Args:
            service_type: Type of service
            amount: Service amount
            customer_type: Customer type (individual, family, etc.)
            
        Returns:
            List of applicable deductibles
        """
        try:
            query = select(PricingDeductible).where(
                and_(
                    PricingDeductible.is_active == True,
                    or_(
                        PricingDeductible.service_category == service_type,
                        PricingDeductible.service_category.is_(None)
                    ),
                    or_(
                        PricingDeductible.deductible_type == customer_type,
                        PricingDeductible.deductible_type == "global"
                    ),
                    or_(
                        PricingDeductible.min_amount.is_(None),
                        PricingDeductible.min_amount <= amount
                    ),
                    or_(
                        PricingDeductible.max_amount.is_(None),
                        PricingDeductible.max_amount >= amount
                    )
                )
            ).order_by(PricingDeductible.calculation_order, PricingDeductible.priority)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to find applicable deductibles: {str(e)}")
            return []
    
    def get_default_deductibles(self, service_category: str = None) -> List[PricingDeductible]:
        """Get default deductibles, optionally filtered by service category."""
        try:
            filters = {'is_default': True, 'is_active': True}
            if service_category:
                filters['service_category'] = service_category
            
            return self.get_multi(
                filters=filters,
                order_by='service_category'
            )
        except Exception as e:
            logger.error(f"Failed to get default deductibles: {str(e)}")
            return []
    
    def get_deductibles_needing_approval(self) -> List[PricingDeductible]:
        """Get deductibles that need approval."""
        try:
            return self.get_multi(
                filters={'approval_status': 'pending'},
                order_by='created_at'
            )
        except Exception as e:
            logger.error(f"Failed to get deductibles needing approval: {str(e)}")
            return []
    
    def get_expiring_deductibles(self, days_ahead: int = 30) -> List[PricingDeductible]:
        """
        Get deductibles that will expire within the specified number of days.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of expiring deductibles
        """
        try:
            future_date = datetime.utcnow().replace(hour=23, minute=59, second=59)
            future_date = future_date.replace(day=future_date.day + days_ahead)
            
            query = select(PricingDeductible).where(
                and_(
                    PricingDeductible.is_active == True,
                    PricingDeductible.expiration_date.is_not(None),
                    PricingDeductible.expiration_date <= future_date,
                    PricingDeductible.expiration_date > datetime.utcnow()
                )
            ).order_by(PricingDeductible.expiration_date)
            
            return list(self.db.scalars(query))
            
        except Exception as e:
            logger.error(f"Failed to get expiring deductibles: {str(e)}")
            return []

    # =====================================================
    # STATISTICS AND ANALYTICS
    # =====================================================
    
    def get_deductible_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about deductibles."""
        try:
            # Total counts
            total_count = self.count()
            active_count = self.count({'is_active': True})
            
            # Count by service category
            category_query = select(
                PricingDeductible.service_category,
                func.count(PricingDeductible.id).label('count')
            ).where(
                PricingDeductible.is_active == True
            ).group_by(PricingDeductible.service_category)
            
            category_counts = {}
            for row in self.db.execute(category_query):
                category_counts[row.service_category or 'global'] = row.count
            
            # Count by deductible type
            type_query = select(
                PricingDeductible.deductible_type,
                func.count(PricingDeductible.id).label('count')
            ).where(
                PricingDeductible.is_active == True
            ).group_by(PricingDeductible.deductible_type)
            
            type_counts = {}
            for row in self.db.execute(type_query):
                type_counts[row.deductible_type] = row.count
            
            # Amount statistics
            amount_query = select(
                func.min(PricingDeductible.amount).label('min_amount'),
                func.max(PricingDeductible.amount).label('max_amount'),
                func.avg(PricingDeductible.amount).label('avg_amount')
            ).where(PricingDeductible.is_active == True)
            
            amount_stats = self.db.execute(amount_query).first()
            
            return {
                'total_deductibles': total_count,
                'active_deductibles': active_count,
                'inactive_deductibles': total_count - active_count,
                'by_service_category': category_counts,
                'by_deductible_type': type_counts,
                'amount_statistics': {
                    'min_amount': float(amount_stats.min_amount) if amount_stats.min_amount else 0,
                    'max_amount': float(amount_stats.max_amount) if amount_stats.max_amount else 0,
                    'avg_amount': float(amount_stats.avg_amount) if amount_stats.avg_amount else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get deductible statistics: {str(e)}")
            return {}

    # =====================================================
    # BULK OPERATIONS
    # =====================================================
    
    def bulk_update_status(self, deductible_ids: List[UUID], is_active: bool, 
                          updated_by: UUID = None) -> int:
        """
        Bulk update the active status of multiple deductibles.
        
        Args:
            deductible_ids: List of deductible IDs to update
            is_active: New active status
            updated_by: User performing the update
            
        Returns:
            Number of deductibles updated
        """
        try:
            update_data = {'is_active': is_active}
            if updated_by:
                update_data['updated_by'] = updated_by
                update_data['updated_at'] = datetime.utcnow()
            
            updated_count = 0
            for deductible_id in deductible_ids:
                if self.update(deductible_id, update_data):
                    updated_count += 1
            
            logger.info(f"Bulk updated {updated_count} deductibles status to {is_active}")
            return updated_count
            
        except Exception as e:
            logger.error(f"Failed to bulk update deductible status: {str(e)}")
            return 0
    
    def bulk_approve_deductibles(self, deductible_ids: List[UUID], 
                               approved_by: UUID) -> int:
        """
        Bulk approve multiple deductibles.
        
        Args:
            deductible_ids: List of deductible IDs to approve
            approved_by: User performing the approval
            
        Returns:
            Number of deductibles approved
        """
        try:
            update_data = {
                'approval_status': 'approved',
                'approved_by': approved_by,
                'approved_at': datetime.utcnow(),
                'updated_by': approved_by,
                'updated_at': datetime.utcnow()
            }
            
            approved_count = 0
            for deductible_id in deductible_ids:
                if self.update(deductible_id, update_data):
                    approved_count += 1
            
            logger.info(f"Bulk approved {approved_count} deductibles by user {approved_by}")
            return approved_count
            
        except Exception as e:
            logger.error(f"Failed to bulk approve deductibles: {str(e)}")
            return 0

    # =====================================================
    # VALIDATION METHODS
    # =====================================================
    
    def _validate_deductible_data(self, deductible_data: Dict[str, Any]) -> None:
        """
        Validate deductible data according to business rules.
        
        Args:
            deductible_data: Deductible data to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Check required fields
        required_fields = ['code', 'label', 'amount', 'deductible_type']
        for field in required_fields:
            if field not in deductible_data or not deductible_data[field]:
                raise ValidationError(f"Required field missing: {field}")
        
        # Validate amount
        amount = deductible_data.get('amount')
        if amount is not None and amount <= 0:
            raise ValidationError("Deductible amount must be greater than 0")
        
        # Validate min/max amounts
        min_amount = deductible_data.get('min_amount')
        max_amount = deductible_data.get('max_amount')
        if min_amount is not None and max_amount is not None and min_amount >= max_amount:
            raise ValidationError("Minimum amount must be less than maximum amount")
        
        # Validate code uniqueness (if it's a new deductible or code changed)
        code = deductible_data.get('code')
        if code:
            existing = self.get_by_code(code)
            deductible_id = deductible_data.get('id')
            if existing and str(existing.id) != str(deductible_id):
                raise ValidationError(f"Deductible code '{code}' already exists")
        
        # Validate currency code
        currency = deductible_data.get('currency', 'USD')
        if len(currency) != 3:
            raise ValidationError("Currency must be a 3-letter ISO code")
        
        # Validate effective/expiration dates
        effective_date = deductible_data.get('effective_date')
        expiration_date = deductible_data.get('expiration_date')
        if effective_date and expiration_date and effective_date >= expiration_date:
            raise ValidationError("Effective date must be before expiration date")

    # =====================================================
    # CACHING SUPPORT
    # =====================================================
    
    def get_cached_active_deductibles(self, cache_key: str = "active_deductibles") -> List[PricingDeductible]:
        """
        Get active deductibles with caching support.
        Note: Actual caching implementation would be added here.
        
        Args:
            cache_key: Cache key for storing results
            
        Returns:
            List of active deductibles
        """
        # TODO: Implement caching logic with Redis or similar
        return self.get_active_deductibles()
    
    def invalidate_deductible_cache(self, cache_keys: List[str] = None) -> None:
        """
        Invalidate deductible-related cache entries.
        
        Args:
            cache_keys: Specific cache keys to invalidate (None for all)
        """
        # TODO: Implement cache invalidation logic
        logger.info("Deductible cache invalidated")

    # =====================================================
    # SEARCH AND FILTERING
    # =====================================================
    
    def search_deductibles(self, search_term: str, filters: Dict[str, Any] = None) -> List[PricingDeductible]:
        """
        Search deductibles by multiple criteria.
        
        Args:
            search_term: Text to search for in code, label, and description
            filters: Additional filters to apply
            
        Returns:
            List of matching deductibles
        """
        try:
            search_fields = ['code', 'label', 'description']
            results = self.search(search_term, search_fields)
            
            # Apply additional filters if provided
            if filters:
                filtered_results = []
                for deductible in results:
                    match = True
                    for field, value in filters.items():
                        if hasattr(deductible, field):
                            if getattr(deductible, field) != value:
                                match = False
                                break
                    if match:
                        filtered_results.append(deductible)
                results = filtered_results
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search deductibles: {str(e)}")
            return []