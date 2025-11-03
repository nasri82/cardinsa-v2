# app/modules/providers/services/provider_service.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from app.core.base_service import BaseService
from app.modules.providers.repositories import create_provider_repository
from app.modules.providers.models.provider_model import Provider
from app.modules.providers.schemas.provider_schema import (
    ProviderCreate, 
    ProviderUpdate,
    ProviderOut,
    ProviderSearch
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError, BusinessLogicError

class ProviderService(BaseService):
    """Enhanced Provider Service with business logic and geospatial features"""
    
    def __init__(self, db: Session):
        repository = create_provider_repository(db)
        super().__init__(repository, db)
        self.provider_repo = repository
    
    # ==================== CRUD OPERATIONS ====================
    
    def get_provider(self, id: UUID) -> ProviderOut:
        """Get provider by ID"""
        provider = self.get_by_id(id)
        return ProviderOut.model_validate(provider)
    
    def create_provider(self, obj_in: ProviderCreate) -> ProviderOut:
        """Create new provider with validation"""
        # Business logic validation
        self._validate_provider_create(obj_in)
        
        # Check for duplicate email
        if obj_in.email and not self.provider_repo.validate_email_unique(obj_in.email):
            raise ConflictError(f"Provider with email '{obj_in.email}' already exists")
        
        # Create the provider
        provider = self.create(obj_in)
        
        self._log_operation(
            "create_provider", 
            provider.id,
            {"name": obj_in.name, "email": obj_in.email, "city": obj_in.city}
        )
        
        return ProviderOut.model_validate(provider)
    
    def update_provider(self, id: UUID, obj_in: ProviderUpdate) -> ProviderOut:
        """Update provider with validation"""
        # Get existing provider
        existing = self.provider_repo.get(id)
        if not existing:
            raise NotFoundError(f"Provider not found with ID: {id}")
        
        # Business logic validation
        self._validate_provider_update(obj_in, existing)
        
        # Check for duplicate email if email is being changed
        if obj_in.email and obj_in.email != existing.email:
            if not self.provider_repo.validate_email_unique(obj_in.email, exclude_id=id):
                raise ConflictError(f"Provider with email '{obj_in.email}' already exists")
        
        # Update the provider
        provider = self.update(id, obj_in)
        
        self._log_operation(
            "update_provider", 
            id,
            {"updated_fields": obj_in.model_dump(exclude_unset=True)}
        )
        
        return ProviderOut.model_validate(provider)
    
    def delete_provider(self, id: UUID) -> bool:
        """Delete provider with business logic validation"""
        # Get existing provider
        existing = self.provider_repo.get(id)
        if not existing:
            raise NotFoundError(f"Provider not found with ID: {id}")
        
        # Business logic validation
        self._validate_provider_delete(existing)
        
        # Check if provider has active relationships
        summary = self.provider_repo.get_provider_summary(id)
        if summary and (summary.get('network_count', 0) > 0 or summary.get('service_count', 0) > 0):
            raise BusinessLogicError(
                f"Cannot delete provider '{existing.name}' because it has active network memberships or services",
                code="PROVIDER_HAS_DEPENDENCIES"
            )
        
        # Delete the provider
        success = self.delete(id)
        
        if success:
            self._log_operation("delete_provider", id, {"name": existing.name, "email": existing.email})
        
        return success
    
    # ==================== SEARCH AND FILTERING ====================
    
    def search_providers(
        self, 
        search_params: ProviderSearch,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderOut]:
        """Advanced search for providers"""
        providers = self.provider_repo.search_providers(
            search_term=search_params.search,
            provider_type_id=search_params.provider_type_id,
            city=search_params.city,
            is_active=search_params.is_active,
            has_coordinates=search_params.has_coordinates,
            skip=skip,
            limit=limit
        )
        
        return [ProviderOut.model_validate(p) for p in providers]
    
    def get_providers_by_city(
        self, 
        city: str,
        provider_type_id: Optional[UUID] = None,
        active_only: bool = True
    ) -> List[ProviderOut]:
        """Get providers by city"""
        providers = self.provider_repo.get_by_city(
            city=city,
            provider_type_id=provider_type_id,
            active_only=active_only
        )
        
        return [ProviderOut.model_validate(p) for p in providers]
    
    def get_provider_by_email(self, email: str) -> Optional[ProviderOut]:
        """Get provider by email"""
        provider = self.provider_repo.get_by_email(email)
        if provider:
            return ProviderOut.model_validate(provider)
        return None
    
    # ==================== GEOSPATIAL OPERATIONS ====================
    
    def find_nearby_providers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50.0,
        provider_type_id: Optional[UUID] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find providers within specified radius"""
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValidationError("Latitude must be between -90 and 90 degrees")
        if not (-180 <= longitude <= 180):
            raise ValidationError("Longitude must be between -180 and 180 degrees")
        if radius_km <= 0 or radius_km > 1000:
            raise ValidationError("Radius must be between 0 and 1000 kilometers")
        
        nearby_providers = self.provider_repo.find_nearby(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            provider_type_id=provider_type_id,
            limit=limit
        )
        
        # Convert to response format
        result = []
        for item in nearby_providers:
            provider_data = ProviderOut.model_validate(item['provider']).model_dump()
            provider_data['distance_km'] = item['distance_km']
            result.append(provider_data)
        
        return result
    
    def get_providers_without_coordinates(self, limit: int = 100) -> List[ProviderOut]:
        """Get providers that need geocoding"""
        providers = self.provider_repo.get_providers_without_coordinates(limit=limit)
        return [ProviderOut.model_validate(p) for p in providers]
    
    def bulk_update_coordinates(
        self, 
        coordinates_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk update provider coordinates"""
        if not coordinates_data:
            raise ValidationError("Coordinates data cannot be empty")
        
        # Validate coordinate data
        for coord_data in coordinates_data:
            if 'provider_id' not in coord_data or 'latitude' not in coord_data or 'longitude' not in coord_data:
                raise ValidationError("Each coordinate data must include provider_id, latitude, and longitude")
            
            if not (-90 <= coord_data['latitude'] <= 90):
                raise ValidationError(f"Invalid latitude for provider {coord_data['provider_id']}")
            
            if not (-180 <= coord_data['longitude'] <= 180):
                raise ValidationError(f"Invalid longitude for provider {coord_data['provider_id']}")
        
        updated_count = self.provider_repo.bulk_update_coordinates(coordinates_data)
        
        self._log_operation(
            "bulk_update_coordinates",
            details={
                "updated_count": updated_count,
                "total_requested": len(coordinates_data)
            }
        )
        
        return {
            "updated_count": updated_count,
            "total_requested": len(coordinates_data),
            "success_rate": updated_count / len(coordinates_data) if coordinates_data else 0
        }
    
    # ==================== ANALYTICS AND STATISTICS ====================
    
    def get_cities_with_counts(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get cities with provider counts"""
        return self.provider_repo.get_cities_with_counts(active_only=active_only)
    
    def get_provider_summary(self, id: UUID) -> Dict[str, Any]:
        """Get comprehensive provider summary"""
        if not self.provider_repo.exists(id):
            raise NotFoundError(f"Provider not found with ID: {id}")
        
        summary = self.provider_repo.get_provider_summary(id)
        if summary and summary.get('provider'):
            summary['provider'] = ProviderOut.model_validate(summary['provider']).model_dump()
        
        return summary
    
    def get_paginated_providers(
        self,
        page: int = 1,
        page_size: int = 20,
        provider_type_id: Optional[UUID] = None,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
        search_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated providers with metadata"""
        result = self.provider_repo.get_paginated_providers(
            page=page,
            page_size=page_size,
            provider_type_id=provider_type_id,
            city=city,
            is_active=is_active,
            search_term=search_term
        )
        
        # Convert items to response schemas
        result["items"] = [ProviderOut.model_validate(p) for p in result["items"]]
        
        return result
    
    # ==================== VALIDATION METHODS ====================
    
    def _validate_provider_create(self, obj_in: ProviderCreate) -> None:
        """Validate provider creation"""
        self._validate_string_length(obj_in.name, "name", min_length=2, max_length=200)
        
        if obj_in.email:
            self._validate_email_format(obj_in.email)
        
        if obj_in.phone:
            self._validate_phone_format(obj_in.phone)
        
        if obj_in.website:
            self._validate_url_format(obj_in.website)
        
        # Validate coordinates if provided
        if obj_in.latitude is not None:
            if not (-90 <= obj_in.latitude <= 90):
                raise ValidationError("Latitude must be between -90 and 90 degrees")
        
        if obj_in.longitude is not None:
            if not (-180 <= obj_in.longitude <= 180):
                raise ValidationError("Longitude must be between -180 and 180 degrees")
    
    def _validate_provider_update(self, obj_in: ProviderUpdate, existing: Provider) -> None:
        """Validate provider update"""
        if obj_in.name is not None:
            self._validate_string_length(obj_in.name, "name", min_length=2, max_length=200)
        
        if obj_in.email is not None:
            self._validate_email_format(obj_in.email)
        
        if obj_in.phone is not None:
            self._validate_phone_format(obj_in.phone)
        
        if obj_in.website is not None:
            self._validate_url_format(obj_in.website)
        
        # Validate coordinates if provided
        if obj_in.latitude is not None:
            if not (-90 <= obj_in.latitude <= 90):
                raise ValidationError("Latitude must be between -90 and 90 degrees")
        
        if obj_in.longitude is not None:
            if not (-180 <= obj_in.longitude <= 180):
                raise ValidationError("Longitude must be between -180 and 180 degrees")
    
    def _validate_provider_delete(self, existing: Provider) -> None:
        """Validate provider deletion"""
        # Additional business logic validation can be added here
        pass
    
    def _validate_email_format(self, email: str) -> None:
        """Validate email format"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
    
    def _validate_phone_format(self, phone: str) -> None:
        """Validate phone format"""
        import re
        # Basic phone validation - can be enhanced
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        cleaned_phone = re.sub(r'[^\d\+]', '', phone)
        if not re.match(phone_pattern, cleaned_phone):
            raise ValidationError("Invalid phone format")
    
    def _validate_url_format(self, url: str) -> None:
        """Validate URL format"""
        import re
        url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        if not re.match(url_pattern, url):
            raise ValidationError("Invalid URL format")
    
    # ==================== LIFECYCLE HOOKS ====================
    
    def _post_create_operations(self, entity: Provider) -> None:
        """Operations after provider creation"""
        # Could trigger events, notifications, geocoding, etc.
        self.logger.info(f"Provider created: {entity.name} ({entity.email})")
    
    def _post_update_operations(self, entity: Provider) -> None:
        """Operations after provider update"""
        # Could trigger events, cache invalidation, etc.
        self.logger.info(f"Provider updated: {entity.name} ({entity.email})")
    
    def _post_delete_operations(self, entity_id: UUID) -> None:
        """Operations after provider deletion"""
        # Could trigger cleanup operations
        self.logger.info(f"Provider deleted: {entity_id}")


# ==================== SERVICE FACTORY ====================

def create_provider_service(db: Session) -> ProviderService:
    """Create provider service instance"""
    return ProviderService(db)


# ==================== LEGACY COMPATIBILITY ====================
# For backward compatibility with existing routes

def get_provider(db: Session, id: UUID):
    """Legacy function for existing routes"""
    service = create_provider_service(db)
    return service.get_provider(id)

def create_provider(db: Session, obj_in: ProviderCreate):
    """Legacy function for existing routes"""
    service = create_provider_service(db)
    return service.create_provider(obj_in)

def update_provider(db: Session, id: UUID, obj_in: ProviderUpdate):
    """Legacy function for existing routes"""
    service = create_provider_service(db)
    return service.update_provider(id, obj_in)

def delete_provider(db: Session, id: UUID):
    """Legacy function for existing routes"""
    service = create_provider_service(db)
    return service.delete_provider(id)