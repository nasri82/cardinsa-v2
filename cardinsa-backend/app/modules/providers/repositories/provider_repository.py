# app/modules/providers/repositories/provider_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select, text
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from app.modules.providers.models.provider_model import Provider
from app.core.base_repository import BaseRepository

class ProviderRepository(BaseRepository):
    """Enhanced Provider Repository with geospatial and advanced querying"""
    
    def __init__(self, db: Session):
        super().__init__(Provider, db)
    
    def get_by_email(self, email: str) -> Optional[Provider]:
        """Get provider by email address"""
        return self.db.scalar(
            select(self.model).where(
                func.lower(self.model.email) == email.lower()
            )
        )
    
    def search_providers(
        self, 
        search_term: Optional[str] = None,
        provider_type_id: Optional[UUID] = None,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
        has_coordinates: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Provider]:
        """Advanced provider search with multiple filters"""
        filters = {}
        
        if provider_type_id:
            filters['provider_type_id'] = provider_type_id
        if city:
            filters['city'] = city
        if is_active is not None:
            filters['is_active'] = is_active
        
        if search_term:
            # Use base class search functionality
            search_fields = ['name', 'email', 'address', 'phone']
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
                order_by='name'
            )
    
    def find_nearby(
        self, 
        latitude: float,
        longitude: float,
        radius_km: float = 50.0,
        provider_type_id: Optional[UUID] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find providers within specified radius using Haversine formula"""
        # Haversine formula for distance calculation
        haversine_sql = text(f"""
            (6371 * acos(
                cos(radians({latitude})) * 
                cos(radians(latitude)) * 
                cos(radians(longitude) - radians({longitude})) + 
                sin(radians({latitude})) * 
                sin(radians(latitude))
            ))
        """)
        
        query = select(
            self.model,
            haversine_sql.label('distance_km')
        ).where(
            and_(
                self.model.latitude.isnot(None),
                self.model.longitude.isnot(None),
                self.model.is_active == True,
                haversine_sql <= radius_km
            )
        )
        
        if provider_type_id:
            query = query.where(self.model.provider_type_id == provider_type_id)
        
        query = query.order_by('distance_km').limit(limit)
        
        result = self.db.execute(query)
        
        return [
            {
                'provider': row[0],
                'distance_km': float(row[1]) if row[1] else None
            }
            for row in result
        ]
    
    def get_by_city(
        self, 
        city: str,
        provider_type_id: Optional[UUID] = None,
        active_only: bool = True
    ) -> List[Provider]:
        """Get providers by city"""
        filters = {'city': city}
        
        if active_only:
            filters['is_active'] = True
        if provider_type_id:
            filters['provider_type_id'] = provider_type_id
        
        return self.get_multi(
            filters=filters,
            order_by='name'
        )
    
    def get_cities_with_counts(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get cities with provider counts"""
        query = select(
            self.model.city,
            func.count(self.model.id).label('provider_count')
        ).where(
            self.model.city.isnot(None)
        ).group_by(self.model.city)
        
        if active_only:
            query = query.where(self.model.is_active == True)
        
        query = query.order_by(self.model.city)
        
        result = self.db.execute(query)
        return [
            {
                'city': row.city,
                'provider_count': row.provider_count
            }
            for row in result
        ]
    
    def get_providers_without_coordinates(self, limit: int = 100) -> List[Provider]:
        """Get providers that don't have coordinates for geocoding"""
        query = select(self.model).where(
            and_(
                or_(
                    self.model.latitude.is_(None),
                    self.model.longitude.is_(None)
                ),
                self.model.address.isnot(None),
                self.model.is_active == True
            )
        ).order_by(self.model.created_at.desc()).limit(limit)
        
        return list(self.db.scalars(query))
    
    def validate_email_unique(
        self, 
        email: str,
        exclude_id: Optional[UUID] = None
    ) -> bool:
        """Validate if email is unique (excluding specified ID)"""
        existing = self.get_by_email(email)
        if not existing:
            return True
        if exclude_id and existing.id == exclude_id:
            return True
        return False
    
    def bulk_update_coordinates(
        self, 
        coordinates_data: List[Dict[str, Any]]
    ) -> int:
        """Bulk update coordinates for providers"""
        updated_count = 0
        for coord_data in coordinates_data:
            provider_id = coord_data['provider_id']
            update_data = {
                'latitude': coord_data['latitude'],
                'longitude': coord_data['longitude']
            }
            
            if self.update(provider_id, update_data):
                updated_count += 1
        
        return updated_count
    
    def get_provider_summary(self, provider_id: UUID) -> Optional[Dict[str, Any]]:
        """Get comprehensive provider summary with all related data"""
        provider = self.get(provider_id)
        if not provider:
            return None
        
        return {
            'provider': provider,
            'has_coordinates': provider.latitude is not None and provider.longitude is not None,
            'network_count': 0,  # TODO: Implement
            'service_count': 0,  # TODO: Implement
            'review_count': 0,   # TODO: Implement
            'average_rating': None  # TODO: Implement
        }
    
    def get_paginated_providers(
        self,
        page: int = 1,
        page_size: int = 20,
        provider_type_id: Optional[UUID] = None,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
        search_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated providers with search and filters"""
        filters = {}
        
        if provider_type_id:
            filters['provider_type_id'] = provider_type_id
        if city:
            filters['city'] = city
        if is_active is not None:
            filters['is_active'] = is_active
        
        return self.get_paginated(
            page=page,
            page_size=page_size,
            filters=filters,
            order_by='name'
        )

# Factory function to create repository instance
def create_provider_repository(db: Session) -> ProviderRepository:
    """Create a provider repository instance"""
    return ProviderRepository(db)