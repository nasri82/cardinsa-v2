# app/modules/providers/repositories/provider_network_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.modules.providers.models.provider_network_model import ProviderNetwork
from app.core.base_repository import BaseRepository

class ProviderNetworkRepository(BaseRepository):
    """Enhanced Provider Network Repository with membership management"""
    
    def __init__(self, db: Session):
        super().__init__(ProviderNetwork, db)
    
    def get_by_code(
        self, 
        code: str,
        company_id: Optional[UUID] = None
    ) -> Optional[ProviderNetwork]:
        """Get network by unique code within company scope"""
        query = select(self.model).where(
            func.upper(self.model.code) == code.upper()
        )
        
        if company_id:
            query = query.where(self.model.company_id == company_id)
        
        return self.db.scalar(query)
    
    def search_networks(
        self, 
        search_term: Optional[str] = None,
        company_id: Optional[UUID] = None,
        tier: Optional[str] = None,
        is_active: Optional[bool] = None,
        coverage_area: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderNetwork]:
        """Advanced network search with filtering"""
        filters = {}
        
        if company_id:
            filters['company_id'] = company_id
        if tier:
            filters['tier'] = tier
        if is_active is not None:
            filters['is_active'] = is_active
        if coverage_area:
            filters['coverage_area'] = coverage_area
        
        if search_term:
            # Use base class search functionality
            search_fields = ['code', 'name', 'description']
            return self.search(
                search_term=search_term,
                search_fields=search_fields,
                skip=skip,
                limit=limit
            )
        else:
            return self.get_multi(
                filters=filters,
                skip=skip,
                limit=limit,
                order_by='tier'
            )
    
    def get_active_networks(
        self, 
        company_id: Optional[UUID] = None,
        tier: Optional[str] = None
    ) -> List[ProviderNetwork]:
        """Get all active networks"""
        filters = {'is_active': True}
        
        if company_id:
            filters['company_id'] = company_id
        if tier:
            filters['tier'] = tier
        
        return self.get_multi(
            filters=filters,
            order_by='tier'
        )
    
    def get_networks_by_coverage_area(
        self, 
        coverage_area: str,
        active_only: bool = True
    ) -> List[ProviderNetwork]:
        """Get networks by coverage area"""
        filters = {'coverage_area': coverage_area}
        
        if active_only:
            filters['is_active'] = True
        
        return self.get_multi(
            filters=filters,
            order_by='tier'
        )
    
    def get_tier_distribution(
        self, 
        company_id: Optional[UUID] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get network distribution by tier"""
        query = select(
            self.model.tier,
            func.count(self.model.id).label('network_count')
        ).group_by(self.model.tier)
        
        conditions = []
        if company_id:
            conditions.append(self.model.company_id == company_id)
        if active_only:
            conditions.append(self.model.is_active == True)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(self.model.tier)
        
        result = self.db.execute(query)
        return [
            {
                'tier': row.tier,
                'network_count': row.network_count
            }
            for row in result
        ]
    
    def get_coverage_areas_with_counts(
        self, 
        company_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get coverage areas with network counts"""
        query = select(
            self.model.coverage_area,
            func.count(self.model.id).label('network_count'),
            func.count(
                func.case(
                    (self.model.is_active == True, 1)
                )
            ).label('active_count')
        ).where(
            self.model.coverage_area.isnot(None)
        ).group_by(self.model.coverage_area)
        
        if company_id:
            query = query.where(self.model.company_id == company_id)
        
        query = query.order_by(self.model.coverage_area)
        
        result = self.db.execute(query)
        return [
            {
                'coverage_area': row.coverage_area,
                'network_count': row.network_count,
                'active_count': row.active_count
            }
            for row in result
        ]
    
    def validate_code_unique(
        self, 
        code: str,
        company_id: UUID,
        exclude_id: Optional[UUID] = None
    ) -> bool:
        """Validate if network code is unique within company"""
        existing = self.get_by_code(code, company_id)
        if not existing:
            return True
        if exclude_id and existing.id == exclude_id:
            return True
        return False
    
    def bulk_update_status(
        self, 
        network_ids: List[UUID],
        is_active: bool,
        company_id: Optional[UUID] = None
    ) -> int:
        """Bulk update active status for networks"""
        updated_count = 0
        for network_id in network_ids:
            # Verify company ownership if specified
            if company_id:
                network = self.get(network_id)
                if not network or network.company_id != company_id:
                    continue
            
            if self.update(network_id, {'is_active': is_active}):
                updated_count += 1
        
        return updated_count
    
    def find_overlapping_networks(
        self, 
        coverage_area: str,
        tier: str,
        company_id: UUID,
        exclude_id: Optional[UUID] = None
    ) -> List[ProviderNetwork]:
        """Find networks with overlapping coverage and tier"""
        query = select(self.model).where(
            and_(
                func.lower(self.model.coverage_area) == coverage_area.lower(),
                self.model.tier == tier,
                self.model.company_id == company_id
            )
        )
        
        if exclude_id:
            query = query.where(self.model.id != exclude_id)
        
        query = query.order_by(self.model.name)
        
        return list(self.db.scalars(query))
    
    def get_network_statistics(self, network_id: UUID) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        network = self.get(network_id)
        
        if not network:
            return {}
        
        # TODO: Implement when ProviderNetworkMember model is ready
        return {
            'network_id': network_id,
            'code': network.code,
            'name': network.name,
            'tier': network.tier,
            'coverage_area': network.coverage_area,
            'is_active': network.is_active,
            'created_at': network.created_at,
            'member_count': 0,  # TODO: Count from ProviderNetworkMember
            'active_member_count': 0,  # TODO: Count active members
            'provider_types': [],  # TODO: Get distinct provider types
            'coverage_cities': []  # TODO: Get cities covered by network
        }
    
    def get_paginated_networks(
        self,
        page: int = 1,
        page_size: int = 20,
        company_id: Optional[UUID] = None,
        tier: Optional[str] = None,
        is_active: Optional[bool] = None,
        search_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated networks with search and filters"""
        filters = {}
        
        if company_id:
            filters['company_id'] = company_id
        if tier:
            filters['tier'] = tier
        if is_active is not None:
            filters['is_active'] = is_active
        
        return self.get_paginated(
            page=page,
            page_size=page_size,
            filters=filters,
            order_by='tier'
        )

# Factory function to create repository instance
def create_provider_network_repository(db: Session) -> ProviderNetworkRepository:
    """Create a provider network repository instance"""
    return ProviderNetworkRepository(db)