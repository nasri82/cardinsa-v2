# app/modules/providers/repositories/provider_type_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.modules.providers.models.provider_type_model import ProviderType
from app.core.base_repository import BaseRepository

class ProviderTypeRepository(BaseRepository):
    """Enhanced Provider Type Repository with advanced querying capabilities"""
    
    def __init__(self, db: Session):
        super().__init__(ProviderType, db)
    
    def get_by_code(self, code: str) -> Optional[ProviderType]:
        """Get provider type by unique code"""
        return self.get_by_field('code', code.upper())
    
    def get_active_types(self, category: Optional[str] = None) -> List[ProviderType]:
        """Get all active provider types, optionally filtered by category"""
        filters = {'is_active': True}
        if category:
            filters['category'] = category
            
        return self.get_multi(
            filters=filters,
            order_by='category'
        )
    
    def search_provider_types(
        self, 
        search_term: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderType]:
        """Advanced search with filtering"""
        filters = {}
        
        if category:
            filters['category'] = category
        if is_active is not None:
            filters['is_active'] = is_active
        
        if search_term:
            # Use base class search functionality
            search_fields = ['code', 'label', 'description']
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
                order_by='category'
            )
    
    def get_categories_with_counts(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get categories with provider type counts"""
        query = select(
            self.model.category,
            func.count(self.model.id).label('count')
        ).group_by(self.model.category)
        
        if active_only:
            query = query.where(self.model.is_active == True)
        
        query = query.order_by(self.model.category)
        
        result = self.db.execute(query)
        return [
            {
                'category': row.category,
                'count': row.count
            }
            for row in result
        ]
    
    def bulk_update_status(
        self, 
        provider_type_ids: List[UUID],
        is_active: bool
    ) -> int:
        """Bulk update active status for multiple provider types"""
        updated_count = 0
        for pt_id in provider_type_ids:
            if self.update(pt_id, {'is_active': is_active}):
                updated_count += 1
        return updated_count
    
    def get_usage_stats(self, provider_type_id: UUID) -> Dict[str, Any]:
        """Get usage statistics for a provider type"""
        provider_type = self.get(provider_type_id)
        
        if not provider_type:
            return {}
        
        # TODO: Add provider count when Provider model is ready
        return {
            'provider_type_id': provider_type_id,
            'code': provider_type.code,
            'label': provider_type.label,
            'category': provider_type.category,
            'is_active': provider_type.is_active,
            'provider_count': 0,  # TODO: Implement when Provider model is ready
            'created_at': provider_type.created_at,
            'updated_at': provider_type.updated_at
        }
    
    def validate_code_unique(
        self, 
        code: str, 
        exclude_id: Optional[UUID] = None
    ) -> bool:
        """Validate if code is unique (excluding specified ID)"""
        existing = self.get_by_code(code)
        if not existing:
            return True
        if exclude_id and existing.id == exclude_id:
            return True
        return False
    
    def get_paginated_provider_types(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        search_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated provider types with search and filters"""
        filters = {}
        
        if category:
            filters['category'] = category
        if is_active is not None:
            filters['is_active'] = is_active
        
        return self.get_paginated(
            page=page,
            page_size=page_size,
            filters=filters,
            order_by='category'
        )

# Factory function to create repository instance
def create_provider_type_repository(db: Session) -> ProviderTypeRepository:
    """Create a provider type repository instance"""
    return ProviderTypeRepository(db)