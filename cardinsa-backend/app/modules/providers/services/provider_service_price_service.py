# app/modules/providers/services/provider_service_price_service.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.core.base_service import BaseService
from app.modules.providers.repositories import create_provider_service_price_repository
from app.modules.providers.models.provider_service_price_model import ProviderServicePrice
from app.modules.providers.schemas.provider_service_price_schema import (
    ProviderServicePriceCreate, 
    ProviderServicePriceUpdate,
    ProviderServicePriceOut,
    ProviderServicePriceSearch
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError, BusinessLogicError

class ProviderServicePriceService(BaseService):
    """Provider Service Price Service for managing provider pricing"""
    
    def __init__(self, db: Session):
        repository = create_provider_service_price_repository(db)
        super().__init__(repository, db)
        self.price_repo = repository
    
    # ==================== CRUD OPERATIONS ====================
    
    def get_service_price(self, id: UUID) -> ProviderServicePriceOut:
        """Get service price by ID"""
        price = self.get_by_id(id)
        return ProviderServicePriceOut.model_validate(price)
    
    def create_service_price(self, obj_in: ProviderServicePriceCreate) -> ProviderServicePriceOut:
        """Create new service price with validation"""
        # Business logic validation
        self._validate_price_create(obj_in)
        
        # Check for duplicate service for provider
        if self.price_repo.check_duplicate_service(obj_in.provider_id, obj_in.service_code):
            raise ConflictError(
                f"Service '{obj_in.service_code}' already exists for this provider"
            )
        
        # Create the service price
        price = self.create(obj_in)
        
        self._log_operation(
            "create_service_price", 
            price.id,
            {
                "provider_id": str(obj_in.provider_id),
                "service_code": obj_in.service_code,
                "base_price": float(obj_in.base_price),
                "currency": obj_in.currency
            }
        )
        
        return ProviderServicePriceOut.model_validate(price)
    
    def update_service_price(self, id: UUID, obj_in: ProviderServicePriceUpdate) -> ProviderServicePriceOut:
        """Update service price with validation"""
        # Get existing price
        existing = self.price_repo.get(id)
        if not existing:
            raise NotFoundError(f"Service price not found with ID: {id}")
        
        # Business logic validation
        self._validate_price_update(obj_in, existing)
        
        # Check for duplicate service code if being changed
        if (obj_in.service_code and obj_in.service_code != existing.service_code and
            self.price_repo.check_duplicate_service(existing.provider_id, obj_in.service_code, exclude_id=id)):
            raise ConflictError(
                f"Service '{obj_in.service_code}' already exists for this provider"
            )
        
        # Update the service price
        price = self.update(id, obj_in)
        
        self._log_operation(
            "update_service_price", 
            id,
            {"updated_fields": obj_in.model_dump(exclude_unset=True)}
        )
        
        return ProviderServicePriceOut.model_validate(price)
    
    def delete_service_price(self, id: UUID) -> bool:
        """Delete service price"""
        # Get existing price
        existing = self.price_repo.get(id)
        if not existing:
            raise NotFoundError(f"Service price not found with ID: {id}")
        
        # Business logic validation
        self._validate_price_delete(existing)
        
        # Delete the service price
        success = self.delete(id)
        
        if success:
            self._log_operation(
                "delete_service_price", 
                id, 
                {
                    "provider_id": str(existing.provider_id),
                    "service_code": existing.service_code
                }
            )
        
        return success
    
    # ==================== PRICING OPERATIONS ====================
    
    def get_provider_services(
        self, 
        provider_id: UUID,
        active_only: bool = True,
        category: Optional[str] = None
    ) -> List[ProviderServicePriceOut]:
        """Get all services and prices for a provider"""
        services = self.price_repo.get_provider_services(
            provider_id=provider_id,
            active_only=active_only,
            category=category
        )
        
        return [ProviderServicePriceOut.model_validate(s) for s in services]
    
    def get_service_by_code(
        self, 
        provider_id: UUID,
        service_code: str
    ) -> Optional[ProviderServicePriceOut]:
        """Get specific service price by provider and service code"""
        service_price = self.price_repo.get_by_provider_and_service(provider_id, service_code)
        if service_price:
            return ProviderServicePriceOut.model_validate(service_price)
        return None
    
    def search_service_prices(
        self, 
        search_params: ProviderServicePriceSearch,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderServicePriceOut]:
        """Advanced search for service prices"""
        service_prices = self.price_repo.search_service_prices(
            service_code=search_params.service_code,
            service_name=search_params.service_name,
            provider_id=search_params.provider_id,
            category=search_params.category,
            currency=search_params.currency,
            is_active=search_params.is_active,
            skip=skip,
            limit=limit
        )
        
        return [ProviderServicePriceOut.model_validate(sp) for sp in service_prices]
    
    def get_price_comparison(
        self, 
        service_code: str,
        provider_ids: Optional[List[UUID]] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Compare prices for a service across providers"""
        if not service_code:
            raise ValidationError("Service code is required for price comparison")
        
        return self.price_repo.get_service_price_comparison(
            service_code=service_code,
            provider_ids=provider_ids,
            active_only=active_only
        )
    
    def find_lowest_price(
        self, 
        service_code: str,
        currency: str = "USD",
        active_only: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Find the lowest price for a specific service"""
        comparison_data = self.get_price_comparison(
            service_code=service_code,
            active_only=active_only
        )
        
        # Filter by currency and find minimum
        currency_prices = [
            item for item in comparison_data 
            if item['currency'].upper() == currency.upper()
        ]
        
        if currency_prices:
            return min(currency_prices, key=lambda x: x['base_price'])
        
        return None
    
    # ==================== PRICE MANAGEMENT ====================
    
    def bulk_update_prices(
        self, 
        price_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk update service prices"""
        if not price_updates:
            raise ValidationError("Price updates cannot be empty")
        
        # Validate update data
        for update_data in price_updates:
            required_fields = ['service_price_id', 'new_price']
            for field in required_fields:
                if field not in update_data:
                    raise ValidationError(f"Each update must include {field}")
            
            if not isinstance(update_data['new_price'], (int, float, Decimal)) or update_data['new_price'] <= 0:
                raise ValidationError("Price must be a positive number")
        
        updated_count = self.price_repo.bulk_update_prices(price_updates)
        
        self._log_operation(
            "bulk_update_prices",
            details={
                "updated_count": updated_count,
                "total_requested": len(price_updates)
            }
        )
        
        return {
            "updated_count": updated_count,
            "total_requested": len(price_updates),
            "success_rate": updated_count / len(price_updates) if price_updates else 0
        }
    
    def apply_price_adjustment(
        self,
        provider_id: Optional[UUID] = None,
        category: Optional[str] = None,
        service_codes: Optional[List[str]] = None,
        adjustment_type: str = "percentage",  # "percentage" or "fixed"
        adjustment_value: float = 0.0,
        effective_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Apply price adjustment to multiple services"""
        if adjustment_type not in ["percentage", "fixed"]:
            raise ValidationError("Adjustment type must be 'percentage' or 'fixed'")
        
        if adjustment_type == "percentage" and (adjustment_value < -100 or adjustment_value > 1000):
            raise ValidationError("Percentage adjustment must be between -100 and 1000")
        
        # Get services to update
        search_params = ProviderServicePriceSearch(
            provider_id=provider_id,
            category=category,
            is_active=True
        )
        
        services = self.search_service_prices(search_params, limit=1000)
        
        if service_codes:
            services = [s for s in services if s.service_code in service_codes]
        
        if not services:
            return {"updated_count": 0, "total_requested": 0, "success_rate": 0}
        
        # Calculate price updates
        price_updates = []
        for service in services:
            if adjustment_type == "percentage":
                new_price = float(service.base_price) * (1 + adjustment_value / 100)
            else:  # fixed
                new_price = float(service.base_price) + adjustment_value
            
            if new_price > 0:  # Ensure price remains positive
                price_updates.append({
                    "service_price_id": service.id,
                    "new_price": round(new_price, 2),
                    "valid_from": effective_date,
                })
        
        if price_updates:
            result = self.bulk_update_prices(price_updates)
            
            self._log_operation(
                "apply_price_adjustment",
                details={
                    "adjustment_type": adjustment_type,
                    "adjustment_value": adjustment_value,
                    "affected_services": len(price_updates),
                    "provider_id": str(provider_id) if provider_id else None,
                    "category": category
                }
            )
            
            return result
        
        return {"updated_count": 0, "total_requested": len(services), "success_rate": 0}
    
    def get_expiring_prices(
        self, 
        days_ahead: int = 30,
        provider_id: Optional[UUID] = None
    ) -> List[ProviderServicePriceOut]:
        """Get prices expiring within specified days"""
        if days_ahead < 1 or days_ahead > 365:
            raise ValidationError("Days ahead must be between 1 and 365")
        
        expiring = self.price_repo.get_expiring_prices(
            days_ahead=days_ahead,
            provider_id=provider_id
        )
        
        return [ProviderServicePriceOut.model_validate(p) for p in expiring]
    
    def extend_price_validity(
        self,
        service_price_id: UUID,
        extend_days: int = 365
    ) -> ProviderServicePriceOut:
        """Extend the validity period for a service price"""
        if extend_days < 1 or extend_days > 1095:  # Max 3 years
            raise ValidationError("Extension days must be between 1 and 1095")
        
        # Get existing price
        existing = self.price_repo.get(service_price_id)
        if not existing:
            raise NotFoundError(f"Service price not found with ID: {service_price_id}")
        
        # Calculate new validity date
        base_date = existing.valid_until if existing.valid_until else date.today()
        new_valid_until = base_date + timedelta(days=extend_days)
        
        # Update price validity
        update_data = ProviderServicePriceUpdate(valid_until=new_valid_until)
        updated = self.update_service_price(service_price_id, update_data)
        
        self._log_operation(
            "extend_price_validity",
            service_price_id,
            {
                "old_valid_until": existing.valid_until.isoformat() if existing.valid_until else None,
                "new_valid_until": new_valid_until.isoformat(),
                "extended_days": extend_days
            }
        )
        
        return updated
    
    # ==================== ANALYTICS AND STATISTICS ====================
    
    def get_pricing_statistics(
        self, 
        service_code: Optional[str] = None,
        category: Optional[str] = None,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """Get pricing statistics for services"""
        return self.price_repo.get_pricing_statistics(
            service_code=service_code,
            category=category,
            currency=currency
        )
    
    def get_services_by_category(
        self, 
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get services grouped by category with statistics"""
        return self.price_repo.get_services_by_category(active_only=active_only)
    
    def get_price_trends(
        self,
        service_code: str,
        provider_ids: Optional[List[UUID]] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get price trends for a service (simplified version)"""
        # This is a simplified implementation
        # In a real system, you'd track price history
        
        current_prices = self.get_price_comparison(
            service_code=service_code,
            provider_ids=provider_ids,
            active_only=True
        )
        
        if not current_prices:
            return {"service_code": service_code, "trends": [], "summary": {}}
        
        prices = [p['base_price'] for p in current_prices]
        
        return {
            "service_code": service_code,
            "current_prices": current_prices,
            "summary": {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "price_variance": max(prices) - min(prices),
                "provider_count": len(current_prices)
            }
        }
    
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
        """Get paginated service prices with metadata"""
        result = self.price_repo.get_paginated_service_prices(
            page=page,
            page_size=page_size,
            provider_id=provider_id,
            category=category,
            currency=currency,
            is_active=is_active,
            search_term=search_term
        )
        
        # Convert items to response schemas
        result["items"] = [ProviderServicePriceOut.model_validate(sp) for sp in result["items"]]
        
        return result
    
    # ==================== VALIDATION METHODS ====================
    
    def _validate_price_create(self, obj_in: ProviderServicePriceCreate) -> None:
        """Validate service price creation"""
        self._validate_string_length(obj_in.service_code, "service_code", min_length=2, max_length=50)
        self._validate_string_length(obj_in.service_name, "service_name", min_length=2, max_length=200)
        
        if obj_in.base_price <= 0:
            raise ValidationError("Base price must be greater than zero")
        
        if obj_in.base_price > Decimal('999999.99'):
            raise ValidationError("Base price cannot exceed 999,999.99")
        
        # Validate currency
        valid_currencies = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY"]
        if obj_in.currency not in valid_currencies:
            raise ValidationError(f"Currency must be one of: {', '.join(valid_currencies)}")
        
        # Validate dates
        if obj_in.valid_from and obj_in.valid_until:
            if obj_in.valid_until <= obj_in.valid_from:
                raise ValidationError("Valid until date must be after valid from date")
        
        if obj_in.category:
            self._validate_string_length(obj_in.category, "category", min_length=2, max_length=50)
    
    def _validate_price_update(self, obj_in: ProviderServicePriceUpdate, existing: ProviderServicePrice) -> None:
        """Validate service price update"""
        if obj_in.service_code is not None:
            self._validate_string_length(obj_in.service_code, "service_code", min_length=2, max_length=50)
        
        if obj_in.service_name is not None:
            self._validate_string_length(obj_in.service_name, "service_name", min_length=2, max_length=200)
        
        if obj_in.base_price is not None:
            if obj_in.base_price <= 0:
                raise ValidationError("Base price must be greater than zero")
            
            if obj_in.base_price > Decimal('999999.99'):
                raise ValidationError("Base price cannot exceed 999,999.99")
        
        # Validate currency if provided
        if obj_in.currency is not None:
            valid_currencies = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY"]
            if obj_in.currency not in valid_currencies:
                raise ValidationError(f"Currency must be one of: {', '.join(valid_currencies)}")
        
        # Validate dates
        valid_from = obj_in.valid_from if obj_in.valid_from is not None else existing.valid_from
        valid_until = obj_in.valid_until if obj_in.valid_until is not None else existing.valid_until
        
        if valid_from and valid_until and valid_until <= valid_from:
            raise ValidationError("Valid until date must be after valid from date")
        
        if obj_in.category is not None:
            self._validate_string_length(obj_in.category, "category", min_length=2, max_length=50)
    
    def _validate_price_delete(self, existing: ProviderServicePrice) -> None:
        """Validate service price deletion"""
        # Additional business logic validation can be added here
        pass
    
    # ==================== LIFECYCLE HOOKS ====================
    
    def _post_create_operations(self, entity: ProviderServicePrice) -> None:
        """Operations after service price creation"""
        self.logger.info(f"Service price created: {entity.service_code} for provider {entity.provider_id}")
    
    def _post_update_operations(self, entity: ProviderServicePrice) -> None:
        """Operations after service price update"""
        self.logger.info(f"Service price updated: {entity.service_code} ({entity.id})")
    
    def _post_delete_operations(self, entity_id: UUID) -> None:
        """Operations after service price deletion"""
        self.logger.info(f"Service price deleted: {entity_id}")


# ==================== SERVICE FACTORY ====================

def create_provider_service_price_service(db: Session) -> ProviderServicePriceService:
    """Create provider service price service instance"""
    return ProviderServicePriceService(db)


# ==================== LEGACY COMPATIBILITY ====================
# For backward compatibility with existing routes

def get_service_price(db: Session, id: UUID):
    """Legacy function for existing routes"""
    service = create_provider_service_price_service(db)
    return service.get_service_price(id)

def create_service_price(db: Session, obj_in: ProviderServicePriceCreate):
    """Legacy function for existing routes"""
    service = create_provider_service_price_service(db)
    return service.create_service_price(obj_in)

def update_service_price(db: Session, id: UUID, obj_in: ProviderServicePriceUpdate):
    """Legacy function for existing routes"""
    service = create_provider_service_price_service(db)
    return service.update_service_price(id, obj_in)

def delete_service_price(db: Session, id: UUID):
    """Legacy function for existing routes"""
    service = create_provider_service_price_service(db)
    return service.delete_service_price(id)