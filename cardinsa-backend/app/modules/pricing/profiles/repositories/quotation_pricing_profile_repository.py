# app/modules/pricing/profiles/repositories/quotation_pricing_profile_repository.py
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.core.database import get_db
from app.modules.pricing.profiles.models.quotation_pricing_profile_model import QuotationPricingProfile
from app.core.exceptions import (
    NotFoundError as EntityNotFoundError, 
    BusinessLogicError, 
    ValidationError,
    BaseAppException as DatabaseOperationError
)

# Try to import history model, but don't fail if it doesn't exist
try:
    from app.modules.pricing.profiles.models.quotation_pricing_profile_history_model import QuotationPricingProfileHistory
    HISTORY_MODEL_AVAILABLE = True
except ImportError:
    QuotationPricingProfileHistory = None
    HISTORY_MODEL_AVAILABLE = False


class QuotationPricingProfileRepository:
    """
    Repository for managing QuotationPricingProfile entities.
    Handles all database operations for pricing profiles.
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def create_profile(self, profile_data: Dict[str, Any], created_by: UUID = None) -> QuotationPricingProfile:
        """Create a new pricing profile."""
        try:
            profile = QuotationPricingProfile(
                **profile_data,
                created_by=created_by,
                updated_by=created_by
            )
            
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            
            return profile
            
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to create profile: {str(e)}")
    
    def get_by_id(self, profile_id: UUID) -> Optional[QuotationPricingProfile]:
        """Get profile by ID."""
        return self.db.query(QuotationPricingProfile)\
            .filter(
                and_(
                    QuotationPricingProfile.id == profile_id,
                    QuotationPricingProfile.archived_at.is_(None)
                )
            ).first()
    
    def get_by_code(self, code: str) -> Optional[QuotationPricingProfile]:
        """Get profile by code."""
        return self.db.query(QuotationPricingProfile)\
            .filter(
                and_(
                    QuotationPricingProfile.code == code,
                    QuotationPricingProfile.archived_at.is_(None)
                )
            ).first()
    
    def update_profile(
        self, 
        profile_id: UUID, 
        profile_data: Dict[str, Any], 
        updated_by: UUID = None
    ) -> Optional[QuotationPricingProfile]:
        """Update an existing profile."""
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                return None
            
            for field, value in profile_data.items():
                if hasattr(profile, field) and value is not None:
                    setattr(profile, field, value)
            
            profile.updated_by = updated_by
            profile.updated_at = func.now()
            
            self.db.commit()
            self.db.refresh(profile)
            
            return profile
            
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to update profile: {str(e)}")
    
    def delete_profile(
        self, 
        profile_id: UUID, 
        updated_by: UUID = None, 
        hard_delete: bool = False
    ) -> bool:
        """Delete a profile (soft or hard delete)."""
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                return False
            
            if hard_delete:
                self.db.delete(profile)
            else:
                profile.archived_at = func.now()
                profile.updated_by = updated_by
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationError(f"Failed to delete profile: {str(e)}")
    
    def search_profiles(
        self,
        name: str = None,
        code: str = None,
        insurance_type: str = None,
        is_active: bool = None,
        currency: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search profiles with filters."""
        query = self.db.query(QuotationPricingProfile)\
            .filter(QuotationPricingProfile.archived_at.is_(None))
        
        # Apply filters
        if name:
            query = query.filter(QuotationPricingProfile.name.ilike(f"%{name}%"))
        if code:
            query = query.filter(QuotationPricingProfile.code == code)
        if insurance_type:
            query = query.filter(QuotationPricingProfile.insurance_type == insurance_type)
        if is_active is not None:
            query = query.filter(QuotationPricingProfile.is_active == is_active)
        if currency:
            query = query.filter(QuotationPricingProfile.currency == currency)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        profiles = query.order_by(QuotationPricingProfile.name)\
            .offset(offset).limit(limit).all()
        
        return {
            'profiles': profiles,
            'pagination': {
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_next': (offset + limit) < total_count,
                'has_previous': offset > 0
            },
            'filters_applied': {
                'name': name,
                'code': code,
                'insurance_type': insurance_type,
                'is_active': is_active,
                'currency': currency
            }
        }
    
    def get_by_insurance_type(
        self, 
        insurance_type: str, 
        active_only: bool = True
    ) -> List[QuotationPricingProfile]:
        """Get profiles by insurance type."""
        query = self.db.query(QuotationPricingProfile)\
            .filter(
                and_(
                    QuotationPricingProfile.insurance_type == insurance_type,
                    QuotationPricingProfile.archived_at.is_(None)
                )
            )
        
        if active_only:
            query = query.filter(QuotationPricingProfile.is_active == True)
        
        return query.order_by(QuotationPricingProfile.name).all()
    
    def create_profile_version(
        self, 
        profile_id: UUID, 
        version_reason: str = None,
        created_by: UUID = None
    ) -> bool:
        """Create a version history entry for a profile (if history model is available)."""
        if not HISTORY_MODEL_AVAILABLE:
            # History model not available, skip versioning
            return True
            
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                return False
            
            # Create history entry
            history_entry = QuotationPricingProfileHistory(
                profile_id=profile_id,
                operation="UPDATE",
                changed_at=datetime.utcnow(),
                changed_by=created_by,
                new_data=self._profile_to_dict(profile),
                change_reason=version_reason
            )
            
            self.db.add(history_entry)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            # Don't fail the main operation if history fails
            return False
    
    def _profile_to_dict(self, profile: QuotationPricingProfile) -> Dict[str, Any]:
        """Convert profile to dictionary for history storage."""
        return {
            'id': str(profile.id),
            'name': profile.name,
            'description': profile.description,
            'code': profile.code,
            'insurance_type': profile.insurance_type,
            'currency': profile.currency,
            'min_premium': float(profile.min_premium) if profile.min_premium else None,
            'max_premium': float(profile.max_premium) if profile.max_premium else None,
            'risk_formula': profile.risk_formula,
            'enable_benefit_exposure': profile.enable_benefit_exposure,
            'benefit_exposure_factor': float(profile.benefit_exposure_factor) if profile.benefit_exposure_factor else None,
            'enable_network_costs': profile.enable_network_costs,
            'network_cost_factor': float(profile.network_cost_factor) if profile.network_cost_factor else None,
            'is_active': profile.is_active,
            'profile_metadata': profile.profile_metadata
        }