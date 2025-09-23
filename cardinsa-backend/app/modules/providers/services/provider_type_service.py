# app/modules/providers/services/provider_type_service.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.base_service import BaseService
from app.modules.providers.repositories import create_provider_type_repository
from app.modules.providers.models.provider_type_model import ProviderType
from app.modules.providers.schemas.provider_type_schema import (
    ProviderTypeCreate, 
    ProviderTypeUpdate,
    ProviderTypeOut,
    ProviderTypeSearch
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError, BusinessLogicError

class ProviderTypeService(BaseService):
    """Enhanced Provider Type Service with business logic"""
    
    def __init__(self, db: Session):
        repository = create_provider_type_repository(db)
        super().__init__(repository, db)
        self.provider_type_repo = repository
    
    # ==================== CRUD OPERATIONS ====================
    
    def get_provider_type(self, id: UUID) -> ProviderTypeOut:
        """Get provider type by ID"""
        provider_type = self.get_by_id(id)
        return ProviderTypeOut.model_validate(provider_type)
    
    def create_provider_type(self, obj_in: ProviderTypeCreate) -> ProviderTypeOut:
        """Create new provider type with validation"""
        # Business logic validation
        self._validate_provider_type_create(obj_in)
        
        # Check for duplicate code
        if not self.provider_type_repo.validate_code_unique(obj_in.code):
            raise ConflictError(f"Provider type with code '{obj_in.code}' already exists")
        
        # Create the provider type
        provider_type = self.create(obj_in)
        
        self._log_operation(
            "create_provider_type", 
            provider_type.id,
            {"code": obj_in.code, "label": obj_in.label, "category": obj_in.category}
        )
        
        return ProviderTypeOut.model_validate(provider_type)
    
    def update_provider_type(self, id: UUID, obj_in: ProviderTypeUpdate) -> ProviderTypeOut:
        """Update provider type with validation"""
        # Get existing provider type
        existing = self.provider_type_repo.get(id)
        if not existing:
            raise NotFoundError(f"Provider type not found with ID: {id}")
        
        # Business logic validation
        self._validate_provider_type_update(obj_in, existing)
        
        # Check for duplicate code if code is being changed
        if obj_in.code and obj_in.code != existing.code:
            if not self.provider_type_repo.validate_code_unique(obj_in.code, exclude_id=id):
                raise ConflictError(f"Provider type with code '{obj_in.code}' already exists")
        
        # Update the provider type
        provider_type = self.update(id, obj_in)
        
        self._log_operation(
            "update_provider_type", 
            id,
            {"updated_fields": obj_in.model_dump(exclude_unset=True)}
        )
        
        return ProviderTypeOut.model_validate(provider_type)
    
    def delete_provider_type(self, id: UUID) -> bool:
        """Delete provider type with business logic validation"""
        # Get existing provider type
        existing = self.provider_type_repo.get(id)
        if not existing:
            raise NotFoundError(f"Provider type not found with ID: {id}")
        
        # Business logic validation
        self._validate_provider_type_delete(existing)
        
        # Check if provider type is in use
        usage_stats = self.provider_type_repo.get_usage_stats(id)
        if usage_stats.get('provider_count', 0) > 0:
            raise BusinessLogicError(
                f"Cannot delete provider type '{existing.label}' because it is in use by {usage_stats['provider_count']} providers",
                code="PROVIDER_TYPE_IN_USE"
            )
        
        # Delete the provider type
        success = self.delete(id)
        
        if success:
            self._log_operation("delete_provider_type", id, {"code": existing.code, "label": existing.label})
        
        return success
    
    # ==================== BUSINESS LOGIC METHODS ====================
    
    def search_provider_types(
        self, 
        search_params: ProviderTypeSearch,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderTypeOut]:
        """Advanced search for provider types"""
        provider_types = self.provider_type_repo.search_provider_types(
            search_term=search_params.search,
            category=search_params.category,
            is_active=search_params.is_active,
            skip=skip,
            limit=limit
        )
        
        return [ProviderTypeOut.model_validate(pt) for pt in provider_types]
    
    def get_active_types(self, category: Optional[str] = None) -> List[ProviderTypeOut]:
        """Get all active provider types"""
        active_types = self.provider_type_repo.get_active_types(category=category)
        return [ProviderTypeOut.model_validate(pt) for pt in active_types]
    
    def get_provider_type_by_code(self, code: str) -> Optional[ProviderTypeOut]:
        """Get provider type by unique code"""
        provider_type = self.provider_type_repo.get_by_code(code)
        if provider_type:
            return ProviderTypeOut.model_validate(provider_type)
        return None
    
    def get_categories_with_stats(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get categories with provider type counts"""
        return self.provider_type_repo.get_categories_with_counts(active_only=active_only)
    
    def bulk_update_status(
        self, 
        provider_type_ids: List[UUID], 
        is_active: bool
    ) -> Dict[str, Any]:
        """Bulk update active status"""
        if not provider_type_ids:
            raise ValidationError("Provider type IDs cannot be empty")
        
        # Validate all IDs exist
        for pt_id in provider_type_ids:
            if not self.provider_type_repo.exists(pt_id):
                raise NotFoundError(f"Provider type not found with ID: {pt_id}")
        
        updated_count = self.provider_type_repo.bulk_update_status(provider_type_ids, is_active)
        
        self._log_operation(
            "bulk_update_status", 
            details={
                "updated_count": updated_count,
                "total_requested": len(provider_type_ids),
                "is_active": is_active
            }
        )
        
        return {
            "updated_count": updated_count,
            "total_requested": len(provider_type_ids),
            "success_rate": updated_count / len(provider_type_ids) if provider_type_ids else 0
        }
    
    def get_provider_type_usage(self, id: UUID) -> Dict[str, Any]:
        """Get usage statistics for a provider type"""
        if not self.provider_type_repo.exists(id):
            raise NotFoundError(f"Provider type not found with ID: {id}")
        
        return self.provider_type_repo.get_usage_stats(id)
    
    def get_paginated_provider_types(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        search_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated provider types with metadata"""
        result = self.provider_type_repo.get_paginated_provider_types(
            page=page,
            page_size=page_size,
            category=category,
            is_active=is_active,
            search_term=search_term
        )
        
        # Convert items to response schemas
        result["items"] = [ProviderTypeOut.model_validate(pt) for pt in result["items"]]
        
        return result
    
    # ==================== VALIDATION METHODS ====================
    
    def _validate_provider_type_create(self, obj_in: ProviderTypeCreate) -> None:
        """Validate provider type creation"""
        self._validate_string_length(obj_in.code, "code", min_length=2, max_length=50)
        self._validate_string_length(obj_in.label, "label", min_length=2, max_length=100)
        
        if obj_in.description and len(obj_in.description) > 500:
            raise ValidationError("Description cannot exceed 500 characters")
        
        # Validate category
        valid_categories = ["medical", "motor", "dental", "vision", "pharmacy"]
        if obj_in.category not in valid_categories:
            raise ValidationError(f"Category must be one of: {', '.join(valid_categories)}")
    
    def _validate_provider_type_update(self, obj_in: ProviderTypeUpdate, existing: ProviderType) -> None:
        """Validate provider type update"""
        if obj_in.code is not None:
            self._validate_string_length(obj_in.code, "code", min_length=2, max_length=50)
        
        if obj_in.label is not None:
            self._validate_string_length(obj_in.label, "label", min_length=2, max_length=100)
        
        if obj_in.description is not None and len(obj_in.description) > 500:
            raise ValidationError("Description cannot exceed 500 characters")
        
        # Validate category if provided
        if obj_in.category is not None:
            valid_categories = ["medical", "motor", "dental", "vision", "pharmacy"]
            if obj_in.category not in valid_categories:
                raise ValidationError(f"Category must be one of: {', '.join(valid_categories)}")
    
    def _validate_provider_type_delete(self, existing: ProviderType) -> None:
        """Validate provider type deletion"""
        # Additional business logic validation can be added here
        pass
    
    # ==================== LIFECYCLE HOOKS ====================
    
    def _post_create_operations(self, entity: ProviderType) -> None:
        """Operations after provider type creation"""
        # Could trigger events, notifications, etc.
        self.logger.info(f"Provider type created: {entity.code} - {entity.label}")
    
    def _post_update_operations(self, entity: ProviderType) -> None:
        """Operations after provider type update"""
        # Could trigger events, cache invalidation, etc.
        self.logger.info(f"Provider type updated: {entity.code} - {entity.label}")
    
    def _post_delete_operations(self, entity_id: UUID) -> None:
        """Operations after provider type deletion"""
        # Could trigger cleanup operations
        self.logger.info(f"Provider type deleted: {entity_id}")


# ==================== SERVICE FACTORY ====================

def create_provider_type_service(db: Session) -> ProviderTypeService:
    """Create provider type service instance"""
    return ProviderTypeService(db)


# ==================== LEGACY COMPATIBILITY ====================
# For backward compatibility with existing routes

def get_provider_type(db: Session, id: UUID):
    """Legacy function for existing routes"""
    service = create_provider_type_service(db)
    return service.get_provider_type(id)

def create_provider_type(db: Session, obj_in: ProviderTypeCreate):
    """Legacy function for existing routes"""
    service = create_provider_type_service(db)
    return service.create_provider_type(obj_in)

def update_provider_type(db: Session, id: UUID, obj_in: ProviderTypeUpdate):
    """Legacy function for existing routes"""
    service = create_provider_type_service(db)
    return service.update_provider_type(id, obj_in)

def delete_provider_type(db: Session, id: UUID):
    """Legacy function for existing routes"""
    service = create_provider_type_service(db)
    return service.delete_provider_type(id)