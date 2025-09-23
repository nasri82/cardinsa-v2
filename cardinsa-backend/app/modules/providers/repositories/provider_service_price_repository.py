# app/modules/providers/repositories/provider_service_price_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select, text
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from app.modules.providers.models.provider_service_price_model import ProviderServicePrice
from app.core.base_repository import BaseRepository

class ProviderServicePriceRepository(BaseRepository):
    """Repository for managing provider service pricing"""
    
    def __init__(self, db: Session):
        super().__init__(ProviderServicePrice, db)
    
    def get_by_provider_and_service(
        self, 
        provider_id: UUID,
        service_code: str
    ) -> Optional[ProviderServicePrice]:
        """Get price by provider and service combination"""
        return self.db.scalar(
            select(self.model).where(
                and_(
                    self.model.provider_id == provider_id,
                    func.upper(self.model.service_code) == service_code.upper()
                )
            )
        )
    
    def get_provider_services(
        self, 
        provider_id: UUID,
        active_only: bool = True,
        category: Optional[str] = None
    ) -> List[ProviderServicePrice]:
        """Get all services and prices for a provider"""
        filters = {'provider_id': provider_id}
        
        if active_only:
            filters['is_active'] = True
        if category:
            filters['category'] = category
        
        services = self.get_multi(
            filters=filters,
            order_by='category'
        )
        
        # Filter expired pricing if active_only
        if active_only:
            current_date = date.today()
            services = [
                s for s in services 
                if s.valid_until is None or s.valid_until >= current_date
            ]
        
        return services
    
    def search_service_prices(
        self, 
        service_code: Optional[str] = None,
        service_name: Optional[str] = None,
        provider_id: Optional[UUID] = None,
        category: Optional[str] = None,
        currency: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderServicePrice]:
        """Advanced service price search"""
        filters = {}
        
        if provider_id:
            filters['provider_id'] = provider_id
        if category:
            filters['category'] = category
        if currency:
            filters['currency'] = currency
        if is_active is not None:
            filters['is_active'] = is_active
        
        if service_code:
            # Search by exact service code
            filters['service_code'] = service_code.upper()
            return self.get_multi(
                filters=filters,
                skip=skip,
                limit=limit,
                order_by='base_price'
            )
        elif service_name:
            # Use base class search functionality
            search_fields = ['service_name']
            return self.search(
                search_term=service_name,
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
    
    def get_service_price_comparison(
        self, 
        service_code: str,
        provider_ids: Optional[List[UUID]] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Compare prices for a specific service across providers"""
        query = select(self.model).where(
            func.upper(self.model.service_code) == service_code.upper()
        )
        
        if active_only:
            query = query.where(self.model.is_active == True)
        
        if provider_ids:
            query = query.where(self.model.provider_id.in_(provider_ids))
        
        query = query.order_by(self.model.base_price.asc())
        
        service_prices = list(self.db.scalars(query))
        
        # Filter expired pricing if active_only
        if active_only:
            current_date = date.today()
            service_prices = [
                sp for sp in service_prices 
                if sp.valid_until is None or sp.valid_until >= current_date
            ]
        
        return [
            {
                'provider_id': sp.provider_id,
                'service_code': sp.service_code,
                'service_name': sp.service_name,
                'base_price': float(sp.base_price),
                'currency': sp.currency,
                'billing_unit': sp.billing_unit,
                'valid_from': sp.valid_from,
                'valid_until': sp.valid_until
            }
            for sp in service_prices
        ]
    
    def get_pricing_statistics(
        self, 
        service_code: Optional[str] = None,
        category: Optional[str] = None,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """Get pricing statistics for services"""
        query = select(
            func.count(self.model.id).label('total_services'),
            func.min(self.model.base_price).label('min_price'),
            func.max(self.model.base_price).label('max_price'),
            func.avg(self.model.base_price).label('avg_price')
        ).where(
            and_(
                self.model.currency == currency,
                self.model.is_active == True
            )
        )
        
        if service_code:
            query = query.where(
                func.upper(self.model.service_code) == service_code.upper()
            )
        if category:
            query = query.where(
                func.lower(self.model.category) == category.lower()
            )
        
        result = self.db.execute(query).first()
        
        return {
            'total_services': result.total_services if result else 0,
            'min_price': float(result.min_price) if result and result.min_price else None,
            'max_price': float(result.max_price) if result and result.max_price else None,
            'avg_price': float(result.avg_price) if result and result.avg_price else None,
            'currency': currency
        }
    
    def get_services_by_category(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get services grouped by category"""
        query = select(
            self.model.category,
            func.count(func.distinct(self.model.service_code)).label('unique_services'),
            func.count(self.model.id).label('total_entries'),
            func.min(self.model.base_price).label('min_price'),
            func.max(self.model.base_price).label('max_price'),
            func.avg(self.model.base_price).label('avg_price')
        ).group_by(self.model.category)
        
        if active_only:
            query = query.where(self.model.is_active == True)
        
        query = query.order_by(self.model.category)
        
        result = self.db.execute(query)
        
        return [
            {
                'category': row.category,
                'unique_services': row.unique_services,
                'total_entries': row.total_entries,
                'min_price': float(row.min_price) if row.min_price else None,
                'max_price': float(row.max_price) if row.max_price else None,
                'avg_price': float(row.avg_price) if row.avg_price else None
            }
            for row in result
        ]
    
    def bulk_update_prices(self, price_updates: List[Dict[str, Any]]) -> int:
        """Bulk update service prices"""
        updated_count = 0
        for update_data in price_updates:
            service_price_id = update_data['service_price_id']
            update_fields = {
                'base_price': update_data['new_price']
            }
            
            if 'valid_from' in update_data:
                update_fields['valid_from'] = update_data['valid_from']
            if 'valid_until' in update_data:
                update_fields['valid_until'] = update_data['valid_until']
            
            if self.update(service_price_id, update_fields):
                updated_count += 1
        
        return updated_count
    
    def check_duplicate_service(
        self, 
        provider_id: UUID,
        service_code: str,
        exclude_id: Optional[UUID] = None
    ) -> bool:
        """Check if service already exists for provider"""
        existing = self.get_by_provider_and_service(provider_id, service_code)
        if not existing:
            return False
        if exclude_id and existing.id == exclude_id:
            return False
        return True
    
    def get_expiring_prices(
        self, 
        days_ahead: int = 30,
        provider_id: Optional[UUID] = None
    ) -> List[ProviderServicePrice]:
        """Get prices expiring within specified days"""
        from datetime import timedelta
        
        expiry_date = date.today() + timedelta(days=days_ahead)
        current_date = date.today()
        
        query = select(self.model).where(
            and_(
                self.model.valid_until.isnot(None),
                self.model.valid_until <= expiry_date,
                self.model.valid_until >= current_date,
                self.model.is_active == True
            )
        )
        
        if provider_id:
            query = query.where(self.model.provider_id == provider_id)
        
        query = query.order_by(self.model.valid_until.asc())
        
        return list(self.db.scalars(query))
    
    def get_paginated_service_prices(
        self,
        page: int = 1,
        page_size: int = 20,
        provider_id: Optional[UUID] = None,
        category: Optional[str] = None,
        currency: Optional[str] = None,
        is_active: Optional[bool] = None,
        search_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated service prices with search and filters"""
        filters = {}
        
        if provider_id:
            filters['provider_id'] = provider_id
        if category:
            filters['category'] = category
        if currency:
            filters['currency'] = currency
        if is_active is not None:
            filters['is_active'] = is_active
        
        return self.get_paginated(
            page=page,
            page_size=page_size,
            filters=filters,
            order_by='category'
        )

# Factory function to create repository instance
def create_provider_service_price_repository(db: Session) -> ProviderServicePriceRepository:
    """Create a provider service price repository instance"""
    return ProviderServicePriceRepository(db)