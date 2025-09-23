# app/modules/providers/services/provider_network_member_service.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime, timedelta

from app.core.base_service import BaseService
from app.modules.providers.repositories import create_provider_network_member_repository
from app.modules.providers.models.provider_network_member_model import ProviderNetworkMember
from app.modules.providers.schemas.provider_network_member_schema import (
    ProviderNetworkMemberCreate, 
    ProviderNetworkMemberUpdate,
    ProviderNetworkMemberOut,
    ProviderNetworkMemberSearch
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError, BusinessLogicError

class ProviderNetworkMemberService(BaseService):
    """Provider Network Member Service for managing network memberships"""
    
    def __init__(self, db: Session):
        repository = create_provider_network_member_repository(db)
        super().__init__(repository, db)
        self.member_repo = repository
    
    # ==================== CRUD OPERATIONS ====================
    
    def get_network_member(self, id: UUID) -> ProviderNetworkMemberOut:
        """Get network member by ID"""
        member = self.get_by_id(id)
        return ProviderNetworkMemberOut.model_validate(member)
    
    def create_network_member(self, obj_in: ProviderNetworkMemberCreate) -> ProviderNetworkMemberOut:
        """Create new network membership with validation"""
        # Business logic validation
        self._validate_member_create(obj_in)
        
        # Check for duplicate membership
        if self.member_repo.check_membership_exists(obj_in.provider_id, obj_in.network_id):
            raise ConflictError(
                f"Provider is already a member of this network"
            )
        
        # Create the membership
        member = self.create(obj_in)
        
        self._log_operation(
            "create_network_member", 
            member.id,
            {
                "provider_id": str(obj_in.provider_id),
                "network_id": str(obj_in.network_id),
                "tier_level": obj_in.tier_level
            }
        )
        
        return ProviderNetworkMemberOut.model_validate(member)
    
    def update_network_member(self, id: UUID, obj_in: ProviderNetworkMemberUpdate) -> ProviderNetworkMemberOut:
        """Update network membership with validation"""
        # Get existing member
        existing = self.member_repo.get(id)
        if not existing:
            raise NotFoundError(f"Network member not found with ID: {id}")
        
        # Business logic validation
        self._validate_member_update(obj_in, existing)
        
        # Update the membership
        member = self.update(id, obj_in)
        
        self._log_operation(
            "update_network_member", 
            id,
            {"updated_fields": obj_in.model_dump(exclude_unset=True)}
        )
        
        return ProviderNetworkMemberOut.model_validate(member)
    
    def delete_network_member(self, id: UUID) -> bool:
        """Delete network membership"""
        # Get existing member
        existing = self.member_repo.get(id)
        if not existing:
            raise NotFoundError(f"Network member not found with ID: {id}")
        
        # Business logic validation
        self._validate_member_delete(existing)
        
        # Delete the membership
        success = self.delete(id)
        
        if success:
            self._log_operation(
                "delete_network_member", 
                id, 
                {
                    "provider_id": str(existing.provider_id),
                    "network_id": str(existing.network_id)
                }
            )
        
        return success
    
    # ==================== MEMBERSHIP MANAGEMENT ====================
    
    def get_provider_memberships(
        self, 
        provider_id: UUID,
        active_only: bool = True,
        include_expired: bool = False
    ) -> List[ProviderNetworkMemberOut]:
        """Get all network memberships for a provider"""
        memberships = self.member_repo.get_provider_memberships(
            provider_id=provider_id,
            active_only=active_only,
            include_expired=include_expired
        )
        
        return [ProviderNetworkMemberOut.model_validate(m) for m in memberships]
    
    def get_network_members(
        self, 
        network_id: UUID,
        active_only: bool = True,
        tier_level: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderNetworkMemberOut]:
        """Get all members of a network"""
        members = self.member_repo.get_network_members(
            network_id=network_id,
            active_only=active_only,
            tier_level=tier_level,
            skip=skip,
            limit=limit
        )
        
        return [ProviderNetworkMemberOut.model_validate(m) for m in members]
    
    def search_memberships(
        self, 
        search_params: ProviderNetworkMemberSearch,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderNetworkMemberOut]:
        """Advanced search for memberships"""
        memberships = self.member_repo.search_memberships(
            network_id=search_params.network_id,
            provider_id=search_params.provider_id,
            tier_level=search_params.tier_level,
            is_active=search_params.is_active,
            skip=skip,
            limit=limit
        )
        
        return [ProviderNetworkMemberOut.model_validate(m) for m in memberships]
    
    def get_membership_by_provider_and_network(
        self, 
        provider_id: UUID,
        network_id: UUID
    ) -> Optional[ProviderNetworkMemberOut]:
        """Get specific membership by provider and network"""
        membership = self.member_repo.get_by_provider_and_network(provider_id, network_id)
        if membership:
            return ProviderNetworkMemberOut.model_validate(membership)
        return None
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    
    def expire_memberships(
        self, 
        membership_ids: List[UUID],
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Expire multiple memberships"""
        if not membership_ids:
            raise ValidationError("Membership IDs cannot be empty")
        
        # Validate all IDs exist
        for membership_id in membership_ids:
            if not self.member_repo.exists(membership_id):
                raise NotFoundError(f"Membership not found with ID: {membership_id}")
        
        expired_count = self.member_repo.expire_memberships(membership_ids, end_date)
        
        self._log_operation(
            "expire_memberships",
            details={
                "expired_count": expired_count,
                "total_requested": len(membership_ids),
                "end_date": end_date.isoformat() if end_date else None
            }
        )
        
        return {
            "expired_count": expired_count,
            "total_requested": len(membership_ids),
            "success_rate": expired_count / len(membership_ids) if membership_ids else 0
        }
    
    def get_expiring_memberships(
        self, 
        days_ahead: int = 30,
        network_id: Optional[UUID] = None
    ) -> List[ProviderNetworkMemberOut]:
        """Get memberships expiring within specified days"""
        if days_ahead < 1 or days_ahead > 365:
            raise ValidationError("Days ahead must be between 1 and 365")
        
        expiring = self.member_repo.get_expiring_memberships(
            days_ahead=days_ahead,
            network_id=network_id
        )
        
        return [ProviderNetworkMemberOut.model_validate(m) for m in expiring]
    
    def renew_membership(
        self, 
        membership_id: UUID,
        new_end_date: Optional[date] = None,
        extend_months: Optional[int] = None
    ) -> ProviderNetworkMemberOut:
        """Renew a membership by extending end date"""
        # Get existing membership
        existing = self.member_repo.get(membership_id)
        if not existing:
            raise NotFoundError(f"Membership not found with ID: {membership_id}")
        
        # Calculate new end date
        if new_end_date:
            calculated_end_date = new_end_date
        elif extend_months:
            if extend_months < 1 or extend_months > 60:
                raise ValidationError("Extension months must be between 1 and 60")
            
            base_date = existing.end_date if existing.end_date else date.today()
            calculated_end_date = base_date + timedelta(days=extend_months * 30)
        else:
            # Default to 12 months extension
            base_date = existing.end_date if existing.end_date else date.today()
            calculated_end_date = base_date + timedelta(days=365)
        
        # Update membership
        update_data = ProviderNetworkMemberUpdate(
            end_date=calculated_end_date,
            is_active=True
        )
        
        renewed = self.update_network_member(membership_id, update_data)
        
        self._log_operation(
            "renew_membership",
            membership_id,
            {
                "old_end_date": existing.end_date.isoformat() if existing.end_date else None,
                "new_end_date": calculated_end_date.isoformat()
            }
        )
        
        return renewed
    
    # ==================== TIER MANAGEMENT ====================
    
    def bulk_update_tier_levels(
        self, 
        membership_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk update tier levels for memberships"""
        if not membership_updates:
            raise ValidationError("Membership updates cannot be empty")
        
        # Validate update data
        for update_data in membership_updates:
            if 'membership_id' not in update_data or 'new_tier_level' not in update_data:
                raise ValidationError("Each update must include membership_id and new_tier_level")
            
            if not isinstance(update_data['new_tier_level'], int) or update_data['new_tier_level'] < 1:
                raise ValidationError("Tier level must be a positive integer")
        
        updated_count = self.member_repo.bulk_update_tier_levels(membership_updates)
        
        self._log_operation(
            "bulk_update_tier_levels",
            details={
                "updated_count": updated_count,
                "total_requested": len(membership_updates)
            }
        )
        
        return {
            "updated_count": updated_count,
            "total_requested": len(membership_updates),
            "success_rate": updated_count / len(membership_updates) if membership_updates else 0
        }
    
    def change_member_tier(
        self, 
        membership_id: UUID,
        new_tier_level: int,
        effective_date: Optional[date] = None
    ) -> ProviderNetworkMemberOut:
        """Change tier level for a specific membership"""
        if new_tier_level < 1:
            raise ValidationError("Tier level must be a positive integer")
        
        # Get existing membership
        existing = self.member_repo.get(membership_id)
        if not existing:
            raise NotFoundError(f"Membership not found with ID: {membership_id}")
        
        # Update tier level
        update_data = ProviderNetworkMemberUpdate(
            tier_level=new_tier_level,
            tier_change_date=effective_date or date.today()
        )
        
        updated = self.update_network_member(membership_id, update_data)
        
        self._log_operation(
            "change_member_tier",
            membership_id,
            {
                "old_tier_level": existing.tier_level,
                "new_tier_level": new_tier_level,
                "effective_date": (effective_date or date.today()).isoformat()
            }
        )
        
        return updated
    
    # ==================== ANALYTICS AND STATISTICS ====================
    
    def get_membership_statistics(
        self, 
        network_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get membership statistics"""
        return self.member_repo.get_membership_statistics(
            network_id=network_id,
            provider_id=provider_id
        )
    
    def get_paginated_memberships(
        self,
        page: int = 1,
        page_size: int = 20,
        network_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None,
        tier_level: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get paginated memberships with metadata"""
        result = self.member_repo.get_paginated_memberships(
            page=page,
            page_size=page_size,
            network_id=network_id,
            provider_id=provider_id,
            tier_level=tier_level,
            is_active=is_active
        )
        
        # Convert items to response schemas
        result["items"] = [ProviderNetworkMemberOut.model_validate(m) for m in result["items"]]
        
        return result
    
    # ==================== VALIDATION METHODS ====================
    
    def _validate_member_create(self, obj_in: ProviderNetworkMemberCreate) -> None:
        """Validate membership creation"""
        if obj_in.tier_level < 1:
            raise ValidationError("Tier level must be a positive integer")
        
        # Validate dates
        if obj_in.join_date and obj_in.end_date:
            if obj_in.end_date <= obj_in.join_date:
                raise ValidationError("End date must be after join date")
    
    def _validate_member_update(self, obj_in: ProviderNetworkMemberUpdate, existing: ProviderNetworkMember) -> None:
        """Validate membership update"""
        if obj_in.tier_level is not None and obj_in.tier_level < 1:
            raise ValidationError("Tier level must be a positive integer")
        
        # Validate dates
        join_date = obj_in.join_date if obj_in.join_date is not None else existing.join_date
        end_date = obj_in.end_date if obj_in.end_date is not None else existing.end_date
        
        if join_date and end_date and end_date <= join_date:
            raise ValidationError("End date must be after join date")
    
    def _validate_member_delete(self, existing: ProviderNetworkMember) -> None:
        """Validate membership deletion"""
        # Additional business logic validation can be added here
        pass
    
    # ==================== LIFECYCLE HOOKS ====================
    
    def _post_create_operations(self, entity: ProviderNetworkMember) -> None:
        """Operations after membership creation"""
        self.logger.info(f"Network membership created: Provider {entity.provider_id} joined Network {entity.network_id}")
    
    def _post_update_operations(self, entity: ProviderNetworkMember) -> None:
        """Operations after membership update"""
        self.logger.info(f"Network membership updated: {entity.id}")
    
    def _post_delete_operations(self, entity_id: UUID) -> None:
        """Operations after membership deletion"""
        self.logger.info(f"Network membership deleted: {entity_id}")


# ==================== SERVICE FACTORY ====================

def create_provider_network_member_service(db: Session) -> ProviderNetworkMemberService:
    """Create provider network member service instance"""
    return ProviderNetworkMemberService(db)


# ==================== LEGACY COMPATIBILITY ====================
# For backward compatibility with existing routes

def get_network_member(db: Session, id: UUID):
    """Legacy function for existing routes"""
    service = create_provider_network_member_service(db)
    return service.get_network_member(id)

def create_network_member(db: Session, obj_in: ProviderNetworkMemberCreate):
    """Legacy function for existing routes"""
    service = create_provider_network_member_service(db)
    return service.create_network_member(obj_in)

def update_network_member(db: Session, id: UUID, obj_in: ProviderNetworkMemberUpdate):
    """Legacy function for existing routes"""
    service = create_provider_network_member_service(db)
    return service.update_network_member(id, obj_in)

def delete_network_member(db: Session, id: UUID):
    """Legacy function for existing routes"""
    service = create_provider_network_member_service(db)
    return service.delete_network_member(id)