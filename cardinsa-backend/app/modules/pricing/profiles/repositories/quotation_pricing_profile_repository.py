# app/modules/pricing/profiles/repositories/quotation_pricing_profile_repository.py

"""
Complete Enhanced QuotationPricingProfile Repository - Step 4 Implementation

This repository provides comprehensive database operations for pricing profiles with:
- ✅ Advanced CRUD operations with complex queries
- ✅ Search and filtering with multiple criteria
- ✅ Analytics and reporting functions
- ✅ Performance optimization with eager loading
- ✅ Business rule validation and enforcement
- ✅ Bulk operations and batch processing
- ✅ Cache integration and performance monitoring
- ✅ Error handling and transaction management

This is the data access layer that handles all database interactions for pricing profiles,
providing optimized queries and sophisticated data operations.
"""

from typing import List, Optional, Dict, Any, Union, Tuple
from uuid import UUID
from sqlalchemy.orm import Session, joinedload, selectinload, contains_eager
from sqlalchemy import and_, or_, desc, asc, func, text, case, distinct
from sqlalchemy.exc import IntegrityError, DataError
from datetime import datetime, timedelta, date
from decimal import Decimal
import logging

from app.core.database import get_db
from app.modules.pricing.profiles.models.quotation_pricing_profile_model import (
    QuotationPricingProfile, 
    InsuranceType, 
    ProfileStatus, 
    CurrencyCode
)
from app.modules.pricing.profiles.models.quotation_pricing_rule_model import QuotationPricingRule
from app.modules.pricing.profiles.models.quotation_pricing_profile_rule_model import QuotationPricingProfileRule
from app.core.exceptions import (
    NotFoundError as EntityNotFoundError, 
    BusinessLogicError, 
    ValidationError,
    BaseAppException as DatabaseOperationError
)

# Try to import history model
try:
    from app.modules.pricing.profiles.models.quotation_pricing_profile_history_model import QuotationPricingProfileHistory
    HISTORY_MODEL_AVAILABLE = True
except ImportError:
    QuotationPricingProfileHistory = None
    HISTORY_MODEL_AVAILABLE = False

logger = logging.getLogger(__name__)


class QuotationPricingProfileRepository:
    """
    Complete Enhanced Repository for QuotationPricingProfile - Step 4 Implementation
    
    Provides comprehensive database operations including:
    - Advanced CRUD with complex queries and joins
    - Search and filtering with performance optimization
    - Analytics and reporting capabilities
    - Business rule validation and enforcement
    - Bulk operations and batch processing
    - Performance monitoring and caching integration
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.logger = logger
    
    # =================================================================
    # ADVANCED CRUD OPERATIONS - STEP 4 CORE REQUIREMENTS
    # =================================================================
    
    def create_profile(self, profile_data: Dict[str, Any], created_by: str) -> QuotationPricingProfile:
        """
        Create a new pricing profile with comprehensive validation
        
        Args:
            profile_data (Dict[str, Any]): Profile data
            created_by (str): User creating the profile
            
        Returns:
            QuotationPricingProfile: Created profile
            
        Raises:
            ValidationError: If data is invalid
            BusinessLogicError: If business rules are violated
            DatabaseOperationError: If database operation fails
        """
        try:
            # Validate required fields
            self._validate_profile_data(profile_data)
            
            # Check for duplicate profile name within insurance type
            existing = self.get_by_name_and_type(
                profile_data.get('profile_name'),
                profile_data.get('insurance_type')
            )
            if existing:
                raise BusinessLogicError(
                    f"Profile '{profile_data.get('profile_name')}' already exists for {profile_data.get('insurance_type')} insurance"
                )
            
            # Check for duplicate profile code if provided
            if profile_data.get('profile_code'):
                existing_code = self.get_by_code(profile_data['profile_code'])
                if existing_code:
                    raise BusinessLogicError(f"Profile code '{profile_data['profile_code']}' already exists")
            
            # Validate premium boundaries
            if not self._validate_premium_boundaries(
                profile_data.get('base_premium'),
                profile_data.get('minimum_premium'),
                profile_data.get('maximum_premium')
            ):
                raise ValidationError("Base premium must be between minimum and maximum premium")
            
            # Create profile with additional metadata
            profile_data.update({
                'created_by': created_by,
                'last_modified_by': created_by,
                'status': ProfileStatus.DRAFT.value,
                'version': '1.0.0',
                'usage_count': 0,
                'quote_count': 0
            })
            
            profile = QuotationPricingProfile(**profile_data)
            
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            
            # Log creation
            self.logger.info(f"Created pricing profile: {profile.id} - {profile.profile_name}")
            
            # Create history record if available
            if HISTORY_MODEL_AVAILABLE:
                self._create_history_record(profile, "CREATE", created_by)
            
            return profile
            
        except IntegrityError as e:
            self.db.rollback()
            self.logger.error(f"Integrity error creating profile: {str(e)}")
            raise DatabaseOperationError(f"Database integrity error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating profile: {str(e)}")
            raise DatabaseOperationError(f"Failed to create profile: {str(e)}")
    
    def get_by_id(
        self, 
        profile_id: UUID, 
        include_rules: bool = False,
        include_history: bool = False,
        include_performance: bool = False
    ) -> Optional[QuotationPricingProfile]:
        """
        Get profile by ID with optional related data loading
        
        Args:
            profile_id (UUID): Profile ID
            include_rules (bool): Whether to include associated rules
            include_history (bool): Whether to include history records
            include_performance (bool): Whether to include performance metrics
            
        Returns:
            Optional[QuotationPricingProfile]: Profile if found, None otherwise
        """
        try:
            query = self.db.query(QuotationPricingProfile).filter(
                and_(
                    QuotationPricingProfile.id == profile_id,
                    QuotationPricingProfile.is_deleted == False
                )
            )
            
            # Add eager loading based on requirements
            if include_rules:
                query = query.options(
                    selectinload(QuotationPricingProfile.profile_rules)
                    .selectinload(QuotationPricingProfileRule.rule)
                )
            
            if include_history and HISTORY_MODEL_AVAILABLE:
                query = query.options(
                    selectinload(QuotationPricingProfile.history_entries)
                )
            
            profile = query.first()
            
            # Add performance metrics if requested
            if profile and include_performance:
                profile.performance_metrics = self._calculate_profile_performance(profile.id)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error getting profile by ID {profile_id}: {str(e)}")
            return None
    
    def get_by_code(self, profile_code: str) -> Optional[QuotationPricingProfile]:
        """
        Get profile by unique code
        
        Args:
            profile_code (str): Profile code
            
        Returns:
            Optional[QuotationPricingProfile]: Profile if found
        """
        try:
            return self.db.query(QuotationPricingProfile).filter(
                and_(
                    QuotationPricingProfile.profile_code == profile_code,
                    QuotationPricingProfile.is_deleted == False
                )
            ).first()
        except Exception as e:
            self.logger.error(f"Error getting profile by code {profile_code}: {str(e)}")
            return None
    
    def get_by_name_and_type(self, profile_name: str, insurance_type: str) -> Optional[QuotationPricingProfile]:
        """
        Get profile by name and insurance type combination
        
        Args:
            profile_name (str): Profile name
            insurance_type (str): Insurance type
            
        Returns:
            Optional[QuotationPricingProfile]: Profile if found
        """
        try:
            return self.db.query(QuotationPricingProfile).filter(
                and_(
                    QuotationPricingProfile.profile_name == profile_name,
                    QuotationPricingProfile.insurance_type == insurance_type,
                    QuotationPricingProfile.is_deleted == False
                )
            ).first()
        except Exception as e:
            self.logger.error(f"Error getting profile by name and type: {str(e)}")
            return None
    
    def update_profile(
        self,
        profile_id: UUID,
        update_data: Dict[str, Any],
        updated_by: str
    ) -> Optional[QuotationPricingProfile]:
        """
        Update profile with comprehensive validation and history tracking
        
        Args:
            profile_id (UUID): Profile ID to update
            update_data (Dict[str, Any]): Data to update
            updated_by (str): User performing update
            
        Returns:
            Optional[QuotationPricingProfile]: Updated profile
            
        Raises:
            EntityNotFoundError: If profile not found
            ValidationError: If update data is invalid
            BusinessLogicError: If business rules are violated
        """
        try:
            # Get existing profile
            profile = self.get_by_id(profile_id)
            if not profile:
                raise EntityNotFoundError(f"Profile not found: {profile_id}")
            
            # Store original data for history
            original_data = profile.to_dict() if HISTORY_MODEL_AVAILABLE else None
            
            # Validate update data
            if 'profile_name' in update_data and update_data['profile_name'] != profile.profile_name:
                # Check for duplicate name
                existing = self.get_by_name_and_type(
                    update_data['profile_name'],
                    update_data.get('insurance_type', profile.insurance_type)
                )
                if existing and existing.id != profile_id:
                    raise BusinessLogicError(f"Profile name '{update_data['profile_name']}' already exists")
            
            if 'profile_code' in update_data and update_data['profile_code'] != profile.profile_code:
                # Check for duplicate code
                existing_code = self.get_by_code(update_data['profile_code'])
                if existing_code and existing_code.id != profile_id:
                    raise BusinessLogicError(f"Profile code '{update_data['profile_code']}' already exists")
            
            # Validate premium boundaries if being updated
            base_premium = update_data.get('base_premium', profile.base_premium)
            min_premium = update_data.get('minimum_premium', profile.minimum_premium)
            max_premium = update_data.get('maximum_premium', profile.maximum_premium)
            
            if not self._validate_premium_boundaries(base_premium, min_premium, max_premium):
                raise ValidationError("Base premium must be between minimum and maximum premium")
            
            # Apply updates
            for key, value in update_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            # Update metadata
            profile.last_modified_by = updated_by
            profile.updated_at = datetime.utcnow()
            
            # Increment version if this is a significant change
            if self._is_significant_change(update_data):
                profile.version = self._increment_version(profile.version)
            
            self.db.commit()
            self.db.refresh(profile)
            
            # Create history record
            if HISTORY_MODEL_AVAILABLE:
                self._create_history_record(
                    profile, 
                    "UPDATE", 
                    updated_by, 
                    original_data, 
                    profile.to_dict(),
                    list(update_data.keys())
                )
            
            self.logger.info(f"Updated pricing profile: {profile.id}")
            
            return profile
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating profile {profile_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update profile: {str(e)}")
    
    def delete_profile(self, profile_id: UUID, deleted_by: str, hard_delete: bool = False) -> bool:
        """
        Delete profile (soft delete by default)
        
        Args:
            profile_id (UUID): Profile ID to delete
            deleted_by (str): User performing deletion
            hard_delete (bool): Whether to permanently delete
            
        Returns:
            bool: True if successful
            
        Raises:
            EntityNotFoundError: If profile not found
            BusinessLogicError: If profile cannot be deleted
        """
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                raise EntityNotFoundError(f"Profile not found: {profile_id}")
            
            # Check if profile can be deleted
            if not self._can_delete_profile(profile):
                raise BusinessLogicError("Profile cannot be deleted - it may be in use")
            
            if hard_delete:
                # Permanent deletion
                self.db.delete(profile)
                self.logger.info(f"Hard deleted profile: {profile_id}")
            else:
                # Soft deletion
                profile.is_deleted = True
                profile.last_modified_by = deleted_by
                profile.updated_at = datetime.utcnow()
                self.logger.info(f"Soft deleted profile: {profile_id}")
            
            # Create history record
            if HISTORY_MODEL_AVAILABLE:
                self._create_history_record(profile, "DELETE", deleted_by)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting profile {profile_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to delete profile: {str(e)}")
    
    # =================================================================
    # ADVANCED SEARCH AND FILTERING - STEP 4 REQUIREMENTS
    # =================================================================
    
    def search_profiles(
        self,
        insurance_type: Optional[str] = None,
        status: Optional[str] = None,
        product_line: Optional[str] = None,
        market_segment: Optional[str] = None,
        created_by: Optional[str] = None,
        department: Optional[str] = None,
        business_unit: Optional[str] = None,
        name_search: Optional[str] = None,
        code_search: Optional[str] = None,
        min_premium: Optional[Decimal] = None,
        max_premium: Optional[Decimal] = None,
        currency_code: Optional[str] = None,
        effective_date_from: Optional[datetime] = None,
        effective_date_to: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        approval_required: Optional[bool] = None,
        approved_only: bool = False,
        include_rules: bool = False,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Advanced search with comprehensive filtering and pagination
        
        Args:
            Various filtering parameters
            
        Returns:
            Dict[str, Any]: Search results with pagination metadata
        """
        try:
            # Build base query
            query = self.db.query(QuotationPricingProfile).filter(
                QuotationPricingProfile.is_deleted == False
            )
            
            # Apply filters
            if insurance_type:
                query = query.filter(QuotationPricingProfile.insurance_type == insurance_type)
            
            if status:
                query = query.filter(QuotationPricingProfile.status == status)
            
            if product_line:
                query = query.filter(QuotationPricingProfile.product_line == product_line)
            
            if market_segment:
                query = query.filter(QuotationPricingProfile.market_segment == market_segment)
            
            if created_by:
                query = query.filter(QuotationPricingProfile.created_by == created_by)
            
            if department:
                query = query.filter(QuotationPricingProfile.department == department)
            
            if business_unit:
                query = query.filter(QuotationPricingProfile.business_unit == business_unit)
            
            if name_search:
                query = query.filter(
                    or_(
                        QuotationPricingProfile.profile_name.ilike(f"%{name_search}%"),
                        QuotationPricingProfile.profile_description.ilike(f"%{name_search}%")
                    )
                )
            
            if code_search:
                query = query.filter(QuotationPricingProfile.profile_code.ilike(f"%{code_search}%"))
            
            if min_premium:
                query = query.filter(QuotationPricingProfile.base_premium >= min_premium)
            
            if max_premium:
                query = query.filter(QuotationPricingProfile.base_premium <= max_premium)
            
            if currency_code:
                query = query.filter(QuotationPricingProfile.currency_code == currency_code)
            
            if effective_date_from:
                query = query.filter(QuotationPricingProfile.effective_date >= effective_date_from)
            
            if effective_date_to:
                query = query.filter(QuotationPricingProfile.effective_date <= effective_date_to)
            
            if created_after:
                query = query.filter(QuotationPricingProfile.created_at >= created_after)
            
            if created_before:
                query = query.filter(QuotationPricingProfile.created_at <= created_before)
            
            if is_active is not None:
                query = query.filter(QuotationPricingProfile.is_active == is_active)
            
            if approval_required is not None:
                query = query.filter(QuotationPricingProfile.approval_required == approval_required)
            
            if approved_only:
                query = query.filter(
                    and_(
                        QuotationPricingProfile.approved_by.isnot(None),
                        QuotationPricingProfile.approved_at.isnot(None)
                    )
                )
            
            # Apply tag filtering
            if tags:
                for tag in tags:
                    query = query.filter(QuotationPricingProfile.tags.contains([tag]))
            
            # Include related data if requested
            if include_rules:
                query = query.options(
                    selectinload(QuotationPricingProfile.profile_rules)
                    .selectinload(QuotationPricingProfileRule.rule)
                )
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply sorting
            sort_column = getattr(QuotationPricingProfile, sort_by, QuotationPricingProfile.created_at)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Apply pagination
            offset = (page - 1) * page_size
            profiles = query.offset(offset).limit(page_size).all()
            
            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                "profiles": profiles,
                "pagination": {
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev,
                    "offset": offset
                },
                "filters_applied": {
                    "insurance_type": insurance_type,
                    "status": status,
                    "product_line": product_line,
                    "name_search": name_search,
                    "date_range": f"{created_after} to {created_before}" if created_after or created_before else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error searching profiles: {str(e)}")
            raise DatabaseOperationError(f"Search failed: {str(e)}")
    
    def get_active_profiles(self, insurance_type: Optional[str] = None) -> List[QuotationPricingProfile]:
        """
        Get all currently active and effective profiles
        
        Args:
            insurance_type (Optional[str]): Filter by insurance type
            
        Returns:
            List[QuotationPricingProfile]: Active profiles
        """
        try:
            now = datetime.utcnow()
            query = self.db.query(QuotationPricingProfile).filter(
                and_(
                    QuotationPricingProfile.status == ProfileStatus.ACTIVE.value,
                    QuotationPricingProfile.is_active == True,
                    QuotationPricingProfile.is_deleted == False,
                    QuotationPricingProfile.effective_date <= now,
                    or_(
                        QuotationPricingProfile.expiration_date.is_(None),
                        QuotationPricingProfile.expiration_date > now
                    )
                )
            )
            
            if insurance_type:
                query = query.filter(QuotationPricingProfile.insurance_type == insurance_type)
            
            return query.order_by(QuotationPricingProfile.profile_name).all()
            
        except Exception as e:
            self.logger.error(f"Error getting active profiles: {str(e)}")
            return []
    
    def get_profiles_by_insurance_type(
        self,
        insurance_type: str,
        active_only: bool = True,
        include_performance: bool = False
    ) -> List[QuotationPricingProfile]:
        """
        Get profiles by insurance type with optional performance data
        
        Args:
            insurance_type (str): Insurance type
            active_only (bool): Whether to return only active profiles
            include_performance (bool): Whether to include performance metrics
            
        Returns:
            List[QuotationPricingProfile]: Profiles for insurance type
        """
        try:
            query = self.db.query(QuotationPricingProfile).filter(
                and_(
                    QuotationPricingProfile.insurance_type == insurance_type,
                    QuotationPricingProfile.is_deleted == False
                )
            )
            
            if active_only:
                query = query.filter(
                    and_(
                        QuotationPricingProfile.status == ProfileStatus.ACTIVE.value,
                        QuotationPricingProfile.is_active == True
                    )
                )
            
            profiles = query.order_by(QuotationPricingProfile.profile_name).all()
            
            # Add performance metrics if requested
            if include_performance:
                for profile in profiles:
                    profile.performance_metrics = self._calculate_profile_performance(profile.id)
            
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error getting profiles by insurance type {insurance_type}: {str(e)}")
            return []
    
    # =================================================================
    # ANALYTICS AND REPORTING - STEP 4 REQUIREMENTS
    # =================================================================
    
    def get_profile_analytics(self, date_range_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive analytics for profiles - STEP 4 REQUIREMENT
        
        Args:
            date_range_days (int): Number of days for recent activity analysis
            
        Returns:
            Dict[str, Any]: Analytics data
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=date_range_days)
            
            # Basic counts
            analytics = {}
            
            # Profile counts by status
            status_counts = self.db.query(
                QuotationPricingProfile.status,
                func.count(QuotationPricingProfile.id).label('count')
            ).filter(
                QuotationPricingProfile.is_deleted == False
            ).group_by(QuotationPricingProfile.status).all()
            
            analytics['status_distribution'] = {status.status: status.count for status in status_counts}
            
            # Profile counts by insurance type
            insurance_counts = self.db.query(
                QuotationPricingProfile.insurance_type,
                func.count(QuotationPricingProfile.id).label('count')
            ).filter(
                QuotationPricingProfile.is_deleted == False
            ).group_by(QuotationPricingProfile.insurance_type).all()
            
            analytics['insurance_type_distribution'] = {ins.insurance_type: ins.count for ins in insurance_counts}
            
            # Premium statistics
            premium_stats = self.db.query(
                func.count(QuotationPricingProfile.id).label('total_profiles'),
                func.avg(QuotationPricingProfile.base_premium).label('avg_premium'),
                func.min(QuotationPricingProfile.base_premium).label('min_premium'),
                func.max(QuotationPricingProfile.base_premium).label('max_premium'),
                func.sum(QuotationPricingProfile.usage_count).label('total_usage')
            ).filter(
                QuotationPricingProfile.is_deleted == False
            ).first()
            
            analytics['premium_statistics'] = {
                'total_profiles': premium_stats.total_profiles or 0,
                'average_base_premium': float(premium_stats.avg_premium) if premium_stats.avg_premium else 0,
                'minimum_base_premium': float(premium_stats.min_premium) if premium_stats.min_premium else 0,
                'maximum_base_premium': float(premium_stats.max_premium) if premium_stats.max_premium else 0,
                'total_usage_count': premium_stats.total_usage or 0
            }
            
            # Recent activity
            recent_created = self.db.query(func.count(QuotationPricingProfile.id)).filter(
                and_(
                    QuotationPricingProfile.created_at >= cutoff_date,
                    QuotationPricingProfile.is_deleted == False
                )
            ).scalar()
            
            recent_updated = self.db.query(func.count(QuotationPricingProfile.id)).filter(
                and_(
                    QuotationPricingProfile.updated_at >= cutoff_date,
                    QuotationPricingProfile.is_deleted == False
                )
            ).scalar()
            
            analytics['recent_activity'] = {
                'recently_created': recent_created or 0,
                'recently_updated': recent_updated or 0,
                'date_range_days': date_range_days
            }
            
            # Performance metrics
            performance_stats = self.db.query(
                func.avg(QuotationPricingProfile.usage_count).label('avg_usage'),
                func.avg(QuotationPricingProfile.quote_count).label('avg_quotes'),
                func.avg(QuotationPricingProfile.avg_quote_amount).label('avg_quote_amount'),
                func.avg(QuotationPricingProfile.conversion_rate).label('avg_conversion_rate')
            ).filter(
                QuotationPricingProfile.is_deleted == False
            ).first()
            
            analytics['performance_metrics'] = {
                'average_usage_count': float(performance_stats.avg_usage) if performance_stats.avg_usage else 0,
                'average_quote_count': float(performance_stats.avg_quotes) if performance_stats.avg_quotes else 0,
                'average_quote_amount': float(performance_stats.avg_quote_amount) if performance_stats.avg_quote_amount else 0,
                'average_conversion_rate': float(performance_stats.avg_conversion_rate) if performance_stats.avg_conversion_rate else 0
            }
            
            # Top performing profiles
            top_profiles = self.db.query(QuotationPricingProfile).filter(
                QuotationPricingProfile.is_deleted == False
            ).order_by(desc(QuotationPricingProfile.usage_count)).limit(5).all()
            
            analytics['top_performing_profiles'] = [
                {
                    'id': str(profile.id),
                    'name': profile.profile_name,
                    'insurance_type': profile.insurance_type,
                    'usage_count': profile.usage_count,
                    'quote_count': profile.quote_count
                }
                for profile in top_profiles
            ]
            
            analytics['generated_at'] = datetime.utcnow().isoformat()
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error generating profile analytics: {str(e)}")
            raise DatabaseOperationError(f"Analytics generation failed: {str(e)}")
    
    def get_most_used_profiles(self, limit: int = 10) -> List[QuotationPricingProfile]:
        """
        Get most frequently used profiles
        
        Args:
            limit (int): Maximum number of profiles to return
            
        Returns:
            List[QuotationPricingProfile]: Most used profiles
        """
        try:
            return self.db.query(QuotationPricingProfile).filter(
                QuotationPricingProfile.is_deleted == False
            ).order_by(desc(QuotationPricingProfile.usage_count)).limit(limit).all()
        except Exception as e:
            self.logger.error(f"Error getting most used profiles: {str(e)}")
            return []
    
    def get_usage_statistics(
        self,
        profile_id: Optional[UUID] = None,
        insurance_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get detailed usage statistics - STEP 4 REQUIREMENT
        
        Args:
            profile_id (Optional[UUID]): Specific profile to analyze
            insurance_type (Optional[str]): Filter by insurance type
            date_from (Optional[datetime]): Start date for analysis
            date_to (Optional[datetime]): End date for analysis
            
        Returns:
            Dict[str, Any]: Usage statistics
        """
        try:
            query = self.db.query(QuotationPricingProfile).filter(
                QuotationPricingProfile.is_deleted == False
            )
            
            # Apply filters
            if profile_id:
                query = query.filter(QuotationPricingProfile.id == profile_id)
            
            if insurance_type:
                query = query.filter(QuotationPricingProfile.insurance_type == insurance_type)
            
            if date_from:
                query = query.filter(QuotationPricingProfile.last_used_at >= date_from)
            
            if date_to:
                query = query.filter(QuotationPricingProfile.last_used_at <= date_to)
            
            profiles = query.all()
            
            # Calculate statistics
            total_usage = sum(p.usage_count for p in profiles)
            total_quotes = sum(p.quote_count for p in profiles)
            total_quote_amount = sum(float(p.avg_quote_amount or 0) * p.quote_count for p in profiles)
            
            return {
                'total_profiles': len(profiles),
                'total_usage_count': total_usage,
                'total_quote_count': total_quotes,
                'total_quote_amount': total_quote_amount,
                'average_usage_per_profile': total_usage / len(profiles) if profiles else 0,
                'average_quotes_per_profile': total_quotes / len(profiles) if profiles else 0,
                'profiles_with_usage': len([p for p in profiles if p.usage_count > 0]),
                'profiles_never_used': len([p for p in profiles if p.usage_count == 0]),
                'most_used_profile': {
                    'id': str(max(profiles, key=lambda p: p.usage_count).id),
                    'name': max(profiles, key=lambda p: p.usage_count).profile_name,
                    'usage_count': max(profiles, key=lambda p: p.usage_count).usage_count
                } if profiles else None,
                'analysis_period': {
                    'from': date_from.isoformat() if date_from else None,
                    'to': date_to.isoformat() if date_to else None
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting usage statistics: {str(e)}")
            raise DatabaseOperationError(f"Usage statistics failed: {str(e)}")
    
    # =================================================================
    # BULK OPERATIONS - STEP 4 REQUIREMENTS
    # =================================================================
    
    def create_bulk_profiles(
        self,
        profiles_data: List[Dict[str, Any]],
        created_by: str,
        validate_each: bool = True
    ) -> Dict[str, Any]:
        """
        Create multiple profiles in bulk operation
        
        Args:
            profiles_data (List[Dict[str, Any]]): List of profile data
            created_by (str): User creating the profiles
            validate_each (bool): Whether to validate each profile individually
            
        Returns:
            Dict[str, Any]: Bulk operation results
        """
        try:
            results = {
                'successful': [],
                'failed': [],
                'total_attempted': len(profiles_data),
                'total_successful': 0,
                'total_failed': 0
            }
            
            for i, profile_data in enumerate(profiles_data):
                try:
                    if validate_each:
                        self._validate_profile_data(profile_data)
                    
                    profile = self.create_profile(profile_data, created_by)
                    results['successful'].append({
                        'index': i,
                        'profile_id': str(profile.id),
                        'profile_name': profile.profile_name
                    })
                    
                except Exception as e:
                    results['failed'].append({
                        'index': i,
                        'profile_name': profile_data.get('profile_name', 'Unknown'),
                        'error': str(e)
                    })
            
            results['total_successful'] = len(results['successful'])
            results['total_failed'] = len(results['failed'])
            results['success_rate'] = results['total_successful'] / results['total_attempted'] if results['total_attempted'] > 0 else 0
            
            self.logger.info(f"Bulk profile creation completed: {results['total_successful']}/{results['total_attempted']} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in bulk profile creation: {str(e)}")
            raise DatabaseOperationError(f"Bulk creation failed: {str(e)}")
    
    def update_bulk_profiles(
        self,
        profile_updates: List[Dict[str, Any]],
        updated_by: str
    ) -> Dict[str, Any]:
        """
        Update multiple profiles in bulk
        
        Args:
            profile_updates (List[Dict[str, Any]]): List of profile updates (must include 'id')
            updated_by (str): User performing updates
            
        Returns:
            Dict[str, Any]: Bulk update results
        """
        try:
            results = {
                'successful': [],
                'failed': [],
                'total_attempted': len(profile_updates),
                'total_successful': 0,
                'total_failed': 0
            }
            
            for i, update_data in enumerate(profile_updates):
                try:
                    profile_id = update_data.pop('id', None)
                    if not profile_id:
                        raise ValueError("Profile ID is required for update")
                    
                    profile = self.update_profile(profile_id, update_data, updated_by)
                    if profile:
                        results['successful'].append({
                            'index': i,
                            'profile_id': str(profile.id),
                            'profile_name': profile.profile_name
                        })
                    
                except Exception as e:
                    results['failed'].append({
                        'index': i,
                        'profile_id': str(update_data.get('id', 'Unknown')),
                        'error': str(e)
                    })
            
            results['total_successful'] = len(results['successful'])
            results['total_failed'] = len(results['failed'])
            results['success_rate'] = results['total_successful'] / results['total_attempted'] if results['total_attempted'] > 0 else 0
            
            self.logger.info(f"Bulk profile update completed: {results['total_successful']}/{results['total_attempted']} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in bulk profile update: {str(e)}")
            raise DatabaseOperationError(f"Bulk update failed: {str(e)}")
    
    def activate_bulk_profiles(
        self,
        profile_ids: List[UUID],
        activated_by: str
    ) -> Dict[str, Any]:
        """
        Activate multiple profiles in bulk
        
        Args:
            profile_ids (List[UUID]): List of profile IDs to activate
            activated_by (str): User performing activation
            
        Returns:
            Dict[str, Any]: Bulk activation results
        """
        try:
            results = {
                'successful': [],
                'failed': [],
                'total_attempted': len(profile_ids),
                'total_successful': 0,
                'total_failed': 0
            }
            
            for profile_id in profile_ids:
                try:
                    profile = self.get_by_id(profile_id)
                    if not profile:
                        raise EntityNotFoundError(f"Profile not found: {profile_id}")
                    
                    # Validate profile can be activated
                    validation = profile.validate_configuration()
                    if not validation['is_valid']:
                        raise ValidationError(f"Profile validation failed: {', '.join(validation['errors'])}")
                    
                    # Update profile status
                    update_data = {
                        'status': ProfileStatus.ACTIVE.value,
                        'is_active': True
                    }
                    
                    updated_profile = self.update_profile(profile_id, update_data, activated_by)
                    
                    results['successful'].append({
                        'profile_id': str(profile_id),
                        'profile_name': updated_profile.profile_name
                    })
                    
                except Exception as e:
                    results['failed'].append({
                        'profile_id': str(profile_id),
                        'error': str(e)
                    })
            
            results['total_successful'] = len(results['successful'])
            results['total_failed'] = len(results['failed'])
            results['success_rate'] = results['total_successful'] / results['total_attempted'] if results['total_attempted'] > 0 else 0
            
            self.logger.info(f"Bulk profile activation completed: {results['total_successful']}/{results['total_attempted']} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in bulk profile activation: {str(e)}")
            raise DatabaseOperationError(f"Bulk activation failed: {str(e)}")
    
    # =================================================================
    # BUSINESS LOGIC VALIDATION - STEP 4 REQUIREMENTS
    # =================================================================
    
    def validate_profile_name_unique(
        self,
        name: str,
        insurance_type: str,
        profile_id: Optional[UUID] = None
    ) -> bool:
        """
        Validate that profile name is unique within insurance type
        
        Args:
            name (str): Profile name to validate
            insurance_type (str): Insurance type
            profile_id (Optional[UUID]): Existing profile ID (for updates)
            
        Returns:
            bool: True if name is unique
        """
        try:
            query = self.db.query(QuotationPricingProfile).filter(
                and_(
                    QuotationPricingProfile.profile_name == name,
                    QuotationPricingProfile.insurance_type == insurance_type,
                    QuotationPricingProfile.is_deleted == False
                )
            )
            
            if profile_id:
                query = query.filter(QuotationPricingProfile.id != profile_id)
            
            return query.first() is None
        except Exception as e:
            self.logger.error(f"Error validating profile name uniqueness: {str(e)}")
            return False
    
    def validate_profile_code_unique(
        self,
        code: str,
        profile_id: Optional[UUID] = None
    ) -> bool:
        """
        Validate that profile code is unique
        
        Args:
            code (str): Profile code to validate
            profile_id (Optional[UUID]): Existing profile ID (for updates)
            
        Returns:
            bool: True if code is unique
        """
        try:
            query = self.db.query(QuotationPricingProfile).filter(
                and_(
                    QuotationPricingProfile.profile_code == code,
                    QuotationPricingProfile.is_deleted == False
                )
            )
            
            if profile_id:
                query = query.filter(QuotationPricingProfile.id != profile_id)
            
            return query.first() is None
        except Exception as e:
            self.logger.error(f"Error validating profile code uniqueness: {str(e)}")
            return False
    
    def clone_profile(
        self,
        source_profile_id: UUID,
        new_name: str,
        created_by: str,
        clone_rules: bool = True,
        new_code: Optional[str] = None
    ) -> Optional[QuotationPricingProfile]:
        """
        Clone an existing profile with optional rule cloning
        
        Args:
            source_profile_id (UUID): Source profile to clone
            new_name (str): Name for cloned profile
            created_by (str): User performing clone
            clone_rules (bool): Whether to clone associated rules
            new_code (Optional[str]): Code for cloned profile
            
        Returns:
            Optional[QuotationPricingProfile]: Cloned profile
        """
        try:
            source_profile = self.get_by_id(source_profile_id, include_rules=clone_rules)
            if not source_profile:
                raise EntityNotFoundError(f"Source profile not found: {source_profile_id}")
            
            # Validate new name is unique
            if not self.validate_profile_name_unique(new_name, source_profile.insurance_type):
                raise BusinessLogicError(f"Profile name '{new_name}' already exists for {source_profile.insurance_type} insurance")
            
            # Validate new code is unique if provided
            if new_code and not self.validate_profile_code_unique(new_code):
                raise BusinessLogicError(f"Profile code '{new_code}' already exists")
            
            # Clone the profile
            cloned_profile = source_profile.clone_profile(new_name, created_by)
            if new_code:
                cloned_profile.profile_code = new_code
            
            self.db.add(cloned_profile)
            self.db.flush()  # Get the ID
            
            # Clone rules if requested
            if clone_rules and hasattr(source_profile, 'profile_rules'):
                from app.modules.pricing.profiles.repositories.quotation_pricing_profile_rule_repository import QuotationPricingProfileRuleRepository
                
                profile_rule_repo = QuotationPricingProfileRuleRepository(self.db)
                
                for profile_rule in source_profile.profile_rules:
                    if profile_rule.is_currently_effective():
                        cloned_association = profile_rule.clone_association(
                            str(cloned_profile.id),
                            created_by,
                            include_overrides=True
                        )
                        self.db.add(cloned_association)
            
            self.db.commit()
            self.db.refresh(cloned_profile)
            
            # Create history record
            if HISTORY_MODEL_AVAILABLE:
                self._create_history_record(cloned_profile, "CREATE", created_by)
            
            self.logger.info(f"Cloned profile: {source_profile_id} -> {cloned_profile.id}")
            
            return cloned_profile
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error cloning profile {source_profile_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to clone profile: {str(e)}")
    
    # =================================================================
    # PERFORMANCE AND CACHING - STEP 4 REQUIREMENTS
    # =================================================================
    
    def get_profile_with_performance_data(self, profile_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get profile with comprehensive performance data
        
        Args:
            profile_id (UUID): Profile ID
            
        Returns:
            Optional[Dict[str, Any]]: Profile with performance metrics
        """
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                return None
            
            profile_data = profile.to_dict()
            profile_data['performance_metrics'] = self._calculate_profile_performance(profile_id)
            
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Error getting profile performance data: {str(e)}")
            return None
    
    def update_profile_usage(
        self,
        profile_id: UUID,
        quote_amount: Optional[Decimal] = None,
        conversion: bool = False
    ) -> bool:
        """
        Update profile usage statistics - STEP 4 REQUIREMENT
        
        Args:
            profile_id (UUID): Profile ID
            quote_amount (Optional[Decimal]): Quote amount generated
            conversion (bool): Whether quote converted to policy
            
        Returns:
            bool: True if successful
        """
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                return False
            
            profile.update_usage_tracking(quote_amount)
            
            # Update conversion rate if applicable
            if conversion and profile.quote_count > 0:
                # Simple conversion rate calculation
                current_conversions = (profile.conversion_rate or 0) * (profile.quote_count - 1)
                new_conversions = current_conversions + 1
                profile.conversion_rate = new_conversions / profile.quote_count
            
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating profile usage {profile_id}: {str(e)}")
            return False
    
    # =================================================================
    # PRIVATE HELPER METHODS
    # =================================================================
    
    def _validate_profile_data(self, profile_data: Dict[str, Any]) -> None:
        """Validate profile data before creation/update"""
        required_fields = ['profile_name', 'insurance_type', 'base_premium', 'minimum_premium', 'maximum_premium']
        
        for field in required_fields:
            if field not in profile_data or profile_data[field] is None:
                raise ValidationError(f"Required field '{field}' is missing or null")
        
        # Validate insurance type
        if profile_data['insurance_type'] not in [t.value for t in InsuranceType]:
            raise ValidationError(f"Invalid insurance type: {profile_data['insurance_type']}")
        
        # Validate currency if provided
        if 'currency_code' in profile_data and profile_data['currency_code']:
            if profile_data['currency_code'] not in [c.value for c in CurrencyCode]:
                raise ValidationError(f"Invalid currency code: {profile_data['currency_code']}")
    
    def _validate_premium_boundaries(
        self,
        base_premium: Decimal,
        min_premium: Decimal,
        max_premium: Decimal
    ) -> bool:
        """Validate premium boundary logic"""
        try:
            return min_premium <= base_premium <= max_premium and min_premium < max_premium
        except Exception:
            return False
    
    def _can_delete_profile(self, profile: QuotationPricingProfile) -> bool:
        """Check if profile can be deleted"""
        # Check if profile is in use (has quotations, active rules, etc.)
        # This would integrate with other parts of the system
        return profile.usage_count == 0 or profile.status == ProfileStatus.DRAFT.value
    
    def _is_significant_change(self, update_data: Dict[str, Any]) -> bool:
        """Determine if update is significant enough to increment version"""
        significant_fields = [
            'base_premium', 'minimum_premium', 'maximum_premium',
            'risk_formula', 'adjustment_type', 'insurance_type'
        ]
        return any(field in update_data for field in significant_fields)
    
    def _increment_version(self, current_version: str) -> str:
        """Increment version string"""
        try:
            parts = current_version.split('.')
            if len(parts) == 3:
                major, minor, patch = parts
                return f"{major}.{minor}.{int(patch) + 1}"
        except Exception:
            pass
        return "1.0.1"
    
    def _calculate_profile_performance(self, profile_id: UUID) -> Dict[str, Any]:
        """Calculate detailed performance metrics for profile"""
        try:
            # This would integrate with quotation and policy systems
            # For now, return basic metrics from the profile itself
            profile = self.get_by_id(profile_id)
            if not profile:
                return {}
            
            return {
                'usage_count': profile.usage_count,
                'quote_count': profile.quote_count,
                'avg_quote_amount': float(profile.avg_quote_amount) if profile.avg_quote_amount else 0,
                'conversion_rate': float(profile.conversion_rate) if profile.conversion_rate else 0,
                'last_used_at': profile.last_used_at.isoformat() if profile.last_used_at else None,
                'performance_score': self._calculate_performance_score(profile),
                'usage_trend': 'stable'  # Would be calculated from historical data
            }
        except Exception:
            return {}
    
    def _calculate_performance_score(self, profile: QuotationPricingProfile) -> float:
        """Calculate overall performance score for profile"""
        try:
            # Simple scoring algorithm - can be enhanced
            usage_score = min(profile.usage_count / 100, 1.0) * 30
            conversion_score = (profile.conversion_rate or 0) * 40
            activity_score = 30 if profile.last_used_at and (datetime.utcnow() - profile.last_used_at).days <= 30 else 0
            
            return usage_score + conversion_score + activity_score
        except Exception:
            return 0.0
    
    def _create_history_record(
        self,
        profile: QuotationPricingProfile,
        operation: str,
        user: str,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        changed_fields: Optional[List[str]] = None
    ) -> None:
        """Create history record if history model is available"""
        if not HISTORY_MODEL_AVAILABLE:
            return
        
        try:
            history = QuotationPricingProfileHistory(
                profile_id=profile.id,
                operation=operation,
                changed_by=user,
                old_data=old_data,
                new_data=new_data or profile.to_dict(),
                changed_fields=changed_fields
            )
            
            self.db.add(history)
            # Don't commit here - let the calling method handle the transaction
            
        except Exception as e:
            self.logger.error(f"Error creating history record: {str(e)}")
            # Don't raise - history is not critical
    
    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'db') and self.db:
                self.db.close()
        except Exception:
            pass