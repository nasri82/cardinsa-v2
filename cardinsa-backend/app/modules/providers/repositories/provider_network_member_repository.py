# app/modules/providers/repositories/provider_network_member_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select, text
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date

from app.modules.providers.models.provider_network_member_model import ProviderNetworkMember
from app.core.base_repository import BaseRepository

class ProviderNetworkMemberRepository(BaseRepository):
    """Repository for managing provider network memberships"""
    
    def __init__(self, db: Session):
        super().__init__(ProviderNetworkMember, db)
    
    def get_by_provider_and_network(
        self, 
        provider_id: UUID,
        network_id: UUID
    ) -> Optional[ProviderNetworkMember]:
        """Get membership by provider and network combination"""
        return self.db.scalar(
            select(self.model).where(
                and_(
                    self.model.provider_id == provider_id,
                    self.model.network_id == network_id
                )
            )
        )
    
    def get_provider_memberships(
        self, 
        provider_id: UUID,
        active_only: bool = True,
        include_expired: bool = False
    ) -> List[ProviderNetworkMember]:
        """Get all network memberships for a provider"""
        filters = {'provider_id': provider_id}
        
        if active_only:
            filters['is_active'] = True
        
        memberships = self.get_multi(
            filters=filters,
            order_by='tier_level'
        )
        
        # Filter expired memberships if requested
        if not include_expired:
            current_date = date.today()
            memberships = [
                m for m in memberships 
                if m.end_date is None or m.end_date >= current_date
            ]
        
        return memberships
    
    def get_network_members(
        self, 
        network_id: UUID,
        active_only: bool = True,
        tier_level: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderNetworkMember]:
        """Get all members of a network"""
        filters = {'network_id': network_id}
        
        if active_only:
            filters['is_active'] = True
        if tier_level is not None:
            filters['tier_level'] = tier_level
        
        members = self.get_multi(
            filters=filters,
            skip=skip,
            limit=limit,
            order_by='tier_level'
        )
        
        # Filter expired memberships if active_only
        if active_only:
            current_date = date.today()
            members = [
                m for m in members 
                if m.end_date is None or m.end_date >= current_date
            ]
        
        return members
    
    def search_memberships(
        self, 
        network_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None,
        tier_level: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderNetworkMember]:
        """Advanced membership search"""
        filters = {}
        
        if network_id:
            filters['network_id'] = network_id
        if provider_id:
            filters['provider_id'] = provider_id
        if tier_level is not None:
            filters['tier_level'] = tier_level
        if is_active is not None:
            filters['is_active'] = is_active
        
        return self.get_multi(
            filters=filters,
            skip=skip,
            limit=limit,
            order_by='join_date',
            order_desc=True
        )
    
    def get_membership_statistics(
        self, 
        network_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get membership statistics"""
        filters = {}
        if network_id:
            filters['network_id'] = network_id
        if provider_id:
            filters['provider_id'] = provider_id
        
        # Total memberships
        total_count = self.count(filters=filters)
        
        # Active memberships
        active_filters = {**filters, 'is_active': True}
        active_count = self.count(filters=active_filters)
        
        # Tier distribution
        if filters:
            query = select(
                self.model.tier_level,
                func.count(self.model.id).label('count')
            ).where(self.model.is_active == True)
            
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
            
            query = query.group_by(self.model.tier_level).order_by(self.model.tier_level)
            
            result = self.db.execute(query)
            tier_distribution = [
                {'tier_level': row.tier_level, 'count': row.count}
                for row in result
            ]
        else:
            tier_distribution = []
        
        return {
            'total_memberships': total_count,
            'active_memberships': active_count,
            'inactive_memberships': total_count - active_count,
            'tier_distribution': tier_distribution
        }
    
    def check_membership_exists(
        self, 
        provider_id: UUID,
        network_id: UUID,
        exclude_id: Optional[UUID] = None
    ) -> bool:
        """Check if membership already exists"""
        existing = self.get_by_provider_and_network(provider_id, network_id)
        if not existing:
            return False
        if exclude_id and existing.id == exclude_id:
            return False
        return True
    
    def bulk_update_tier_levels(
        self, 
        membership_updates: List[Dict[str, Any]]
    ) -> int:
        """Bulk update tier levels for memberships"""
        updated_count = 0
        for update_data in membership_updates:
            membership_id = update_data['membership_id']
            new_tier_level = update_data['new_tier_level']
            
            if self.update(membership_id, {'tier_level': new_tier_level}):
                updated_count += 1
        
        return updated_count
    
    def expire_memberships(
        self, 
        membership_ids: List[UUID],
        end_date: Optional[date] = None
    ) -> int:
        """Expire memberships by setting end date"""
        if end_date is None:
            end_date = date.today()
        
        updated_count = 0
        for membership_id in membership_ids:
            update_data = {
                'end_date': end_date,
                'is_active': False
            }
            
            if self.update(membership_id, update_data):
                updated_count += 1
        
        return updated_count
    
    def get_expiring_memberships(
        self, 
        days_ahead: int = 30,
        network_id: Optional[UUID] = None
    ) -> List[ProviderNetworkMember]:
        """Get memberships expiring within specified days"""
        from datetime import timedelta
        
        expiry_date = date.today() + timedelta(days=days_ahead)
        current_date = date.today()
        
        query = select(self.model).where(
            and_(
                self.model.end_date.isnot(None),
                self.model.end_date <= expiry_date,
                self.model.end_date >= current_date,
                self.model.is_active == True
            )
        )
        
        if network_id:
            query = query.where(self.model.network_id == network_id)
        
        query = query.order_by(self.model.end_date.asc())
        
        return list(self.db.scalars(query))
    
    def get_paginated_memberships(
        self,
        page: int = 1,
        page_size: int = 20,
        network_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None,
        tier_level: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get paginated memberships with filters"""
        filters = {}
        
        if network_id:
            filters['network_id'] = network_id
        if provider_id:
            filters['provider_id'] = provider_id
        if tier_level is not None:
            filters['tier_level'] = tier_level
        if is_active is not None:
            filters['is_active'] = is_active
        
        return self.get_paginated(
            page=page,
            page_size=page_size,
            filters=filters,
            order_by='join_date',
            order_desc=True
        )

# Factory function to create repository instance
def create_provider_network_member_repository(db: Session) -> ProviderNetworkMemberRepository:
    """Create a provider network member repository instance"""
    return ProviderNetworkMemberRepository(db)