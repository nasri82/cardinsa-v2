# app/core/base_service.py

"""
Base Service Class

Provides common functionality and patterns for all service layer classes.
Includes CRUD operations, validation, caching, and error handling.
"""

from typing import List, Optional, Dict, Any, Union, Type, TypeVar, Generic
from uuid import UUID
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timedelta
import logging
from decimal import Decimal

from app.core.base_repository import BaseRepository
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ConflictError,
    BusinessLogicError,
    DatabaseOperationError
)

# Type variables for generics
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
ResponseSchemaType = TypeVar("ResponseSchemaType")

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Abstract base service class providing common functionality for all services.
    
    This class provides:
    - Standard CRUD operations
    - Validation patterns
    - Error handling
    - Logging
    - Common business logic patterns
    """
    
    def __init__(self, repository: BaseRepository, db: Session):
        """
        Initialize the base service.
        
        Args:
            repository: Repository instance for data access
            db: Database session
        """
        self.repository = repository
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)
    
    # ==================== CRUD OPERATIONS ====================
    
    def get_by_id(self, id: Union[UUID, int]) -> Optional[Any]:
        """Get entity by ID"""
        try:
            entity = self.repository.get(id)
            if not entity:
                raise NotFoundError(f"Entity not found with ID: {id}")
            return entity
        except Exception as e:
            self.logger.error(f"Error getting entity by ID {id}: {str(e)}")
            raise
    
    def get_all(self, skip: int = 0, limit: int = 100, 
                filters: Optional[Dict[str, Any]] = None,
                order_by: Optional[str] = None,
                order_desc: bool = False) -> List[Any]:
        """Get all entities with pagination and filtering"""
        try:
            return self.repository.get_multi(
                skip=skip,
                limit=limit,
                filters=filters,
                order_by=order_by,
                order_desc=order_desc
            )
        except Exception as e:
            self.logger.error(f"Error getting entities: {str(e)}")
            raise
    
    def create(self, create_data: Any) -> Any:
        """Create new entity"""
        try:
            # Pre-creation validation
            self._validate_create_data(create_data)
            
            # Create entity
            entity = self.repository.create(create_data)
            
            # Post-creation operations
            self._post_create_operations(entity)
            
            self.logger.info(f"Created entity with ID: {entity.id}")
            return entity
            
        except IntegrityError as e:
            self.logger.error(f"Integrity error creating entity: {str(e)}")
            self.db.rollback()
            raise ConflictError("Entity creation failed due to constraint violation")
        except SQLAlchemyError as e:
            self.logger.error(f"Database error creating entity: {str(e)}")
            self.db.rollback()
            raise DatabaseOperationError("Failed to create entity")
        except Exception as e:
            self.logger.error(f"Unexpected error creating entity: {str(e)}")
            self.db.rollback()
            raise
    
    def update(self, id: Union[UUID, int], update_data: Any) -> Any:
        """Update existing entity"""
        try:
            # Check if entity exists
            existing_entity = self.get_by_id(id)
            
            # Pre-update validation
            self._validate_update_data(update_data, existing_entity)
            
            # Update entity
            updated_entity = self.repository.update(id, update_data)
            if not updated_entity:
                raise NotFoundError(f"Entity not found for update with ID: {id}")
            
            # Post-update operations
            self._post_update_operations(updated_entity, existing_entity)
            
            self.logger.info(f"Updated entity with ID: {id}")
            return updated_entity
            
        except IntegrityError as e:
            self.logger.error(f"Integrity error updating entity {id}: {str(e)}")
            self.db.rollback()
            raise ConflictError("Entity update failed due to constraint violation")
        except SQLAlchemyError as e:
            self.logger.error(f"Database error updating entity {id}: {str(e)}")
            self.db.rollback()
            raise DatabaseOperationError("Failed to update entity")
        except Exception as e:
            self.logger.error(f"Unexpected error updating entity {id}: {str(e)}")
            self.db.rollback()
            raise
    
    def delete(self, id: Union[UUID, int], soft_delete: bool = True) -> bool:
        """Delete entity (soft delete by default)"""
        try:
            # Check if entity exists
            entity = self.get_by_id(id)
            
            # Pre-delete validation
            self._validate_delete(entity)
            
            # Perform delete
            if soft_delete and hasattr(entity, 'is_deleted'):
                # Soft delete
                entity.is_deleted = True
                entity.deleted_at = datetime.utcnow()
                self.db.commit()
            else:
                # Hard delete
                self.repository.delete(id)
            
            # Post-delete operations
            self._post_delete_operations(entity)
            
            self.logger.info(f"Deleted entity with ID: {id}")
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error deleting entity {id}: {str(e)}")
            self.db.rollback()
            raise DatabaseOperationError("Failed to delete entity")
        except Exception as e:
            self.logger.error(f"Unexpected error deleting entity {id}: {str(e)}")
            self.db.rollback()
            raise
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters"""
        try:
            return self.repository.count(filters=filters)
        except Exception as e:
            self.logger.error(f"Error counting entities: {str(e)}")
            raise
    
    def exists(self, id: Union[UUID, int]) -> bool:
        """Check if entity exists"""
        try:
            entity = self.repository.get(id)
            return entity is not None
        except Exception as e:
            self.logger.error(f"Error checking entity existence {id}: {str(e)}")
            raise
    
    # ==================== BULK OPERATIONS ====================
    
    def create_bulk(self, create_data_list: List[Any]) -> List[Any]:
        """Create multiple entities in bulk"""
        try:
            # Validate all data first
            for create_data in create_data_list:
                self._validate_create_data(create_data)
            
            # Create entities
            entities = self.repository.create_batch(create_data_list)
            
            # Post-creation operations for each
            for entity in entities:
                self._post_create_operations(entity)
            
            self.logger.info(f"Created {len(entities)} entities in bulk")
            return entities
            
        except Exception as e:
            self.logger.error(f"Error in bulk create: {str(e)}")
            self.db.rollback()
            raise
    
    def update_bulk(self, updates: List[Dict[str, Any]]) -> List[Any]:
        """Update multiple entities in bulk"""
        try:
            updated_entities = []
            
            for update_item in updates:
                entity_id = update_item.get('id')
                update_data = update_item.get('data', {})
                
                if not entity_id:
                    raise ValidationError("Entity ID required for bulk update")
                
                updated_entity = self.update(entity_id, update_data)
                updated_entities.append(updated_entity)
            
            self.logger.info(f"Updated {len(updated_entities)} entities in bulk")
            return updated_entities
            
        except Exception as e:
            self.logger.error(f"Error in bulk update: {str(e)}")
            self.db.rollback()
            raise
    
    # ==================== SEARCH AND FILTERING ====================
    
    def search(self, query: str, fields: Optional[List[str]] = None,
              limit: int = 50) -> List[Any]:
        """Search entities by query string"""
        try:
            # This is a basic implementation
            # Override in child classes for specific search logic
            return self.repository.get_multi(limit=limit)
        except Exception as e:
            self.logger.error(f"Error in search: {str(e)}")
            raise
    
    def filter_by_field(self, field_name: str, field_value: Any) -> List[Any]:
        """Filter entities by specific field"""
        try:
            filters = {field_name: field_value}
            return self.repository.get_multi(filters=filters)
        except Exception as e:
            self.logger.error(f"Error filtering by {field_name}: {str(e)}")
            raise
    
    def get_by_field(self, field_name: str, field_value: Any) -> Optional[Any]:
        """Get single entity by field value"""
        try:
            return self.repository.get_by_field(field_name, field_value)
        except Exception as e:
            self.logger.error(f"Error getting by {field_name}: {str(e)}")
            raise
    
    # ==================== PAGINATION ====================
    
    def get_paginated(self, page: int = 1, page_size: int = 20,
                     filters: Optional[Dict[str, Any]] = None,
                     order_by: Optional[str] = None,
                     order_desc: bool = False) -> Dict[str, Any]:
        """Get paginated results"""
        try:
            return self.repository.get_paginated(
                page=page,
                page_size=page_size,
                filters=filters,
                order_by=order_by,
                order_desc=order_desc
            )
        except Exception as e:
            self.logger.error(f"Error in pagination: {str(e)}")
            raise
    
    # ==================== VALIDATION HOOKS ====================
    
    def _validate_create_data(self, create_data: Any) -> None:
        """
        Validate data before creation.
        Override in child classes for specific validation.
        """
        if not create_data:
            raise ValidationError("Create data cannot be empty")
    
    def _validate_update_data(self, update_data: Any, existing_entity: Any) -> None:
        """
        Validate data before update.
        Override in child classes for specific validation.
        """
        if not update_data:
            raise ValidationError("Update data cannot be empty")
    
    def _validate_delete(self, entity: Any) -> None:
        """
        Validate before deletion.
        Override in child classes for specific validation.
        """
        pass
    
    # ==================== LIFECYCLE HOOKS ====================
    
    def _post_create_operations(self, entity: Any) -> None:
        """
        Operations to perform after entity creation.
        Override in child classes for specific operations.
        """
        pass
    
    def _post_update_operations(self, updated_entity: Any, 
                               original_entity: Any) -> None:
        """
        Operations to perform after entity update.
        Override in child classes for specific operations.
        """
        pass
    
    def _post_delete_operations(self, entity: Any) -> None:
        """
        Operations to perform after entity deletion.
        Override in child classes for specific operations.
        """
        pass
    
    # ==================== UTILITY METHODS ====================
    
    def _format_decimal(self, value: Union[Decimal, float, str]) -> Decimal:
        """Format decimal values consistently"""
        if value is None:
            return Decimal('0.00')
        return Decimal(str(value)).quantize(Decimal('0.01'))
    
    def _validate_uuid(self, value: Union[str, UUID]) -> UUID:
        """Validate and convert UUID"""
        try:
            if isinstance(value, str):
                return UUID(value)
            return value
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid UUID format: {value}")
    
    def _validate_positive_decimal(self, value: Union[Decimal, float], 
                                  field_name: str) -> Decimal:
        """Validate positive decimal value"""
        decimal_value = self._format_decimal(value)
        if decimal_value <= 0:
            raise ValidationError(f"{field_name} must be greater than zero")
        return decimal_value
    
    def _validate_non_negative_decimal(self, value: Union[Decimal, float],
                                      field_name: str) -> Decimal:
        """Validate non-negative decimal value"""
        decimal_value = self._format_decimal(value)
        if decimal_value < 0:
            raise ValidationError(f"{field_name} cannot be negative")
        return decimal_value
    
    def _validate_date_range(self, start_date: datetime, end_date: datetime,
                           start_field: str, end_field: str) -> None:
        """Validate date range"""
        if end_date <= start_date:
            raise ValidationError(f"{end_field} must be after {start_field}")
    
    def _validate_string_length(self, value: str, field_name: str,
                               min_length: int = None,
                               max_length: int = None) -> None:
        """Validate string length"""
        if not value:
            raise ValidationError(f"{field_name} cannot be empty")
        
        if min_length and len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters")
        
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name} cannot exceed {max_length} characters")
    
    def _log_operation(self, operation: str, entity_id: Union[UUID, int] = None,
                      details: Dict[str, Any] = None) -> None:
        """Log service operations"""
        log_data = {
            'service': self.__class__.__name__,
            'operation': operation,
            'entity_id': str(entity_id) if entity_id else None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            log_data.update(details)
        
        self.logger.info(f"Service operation: {operation}", extra=log_data)
    
    # ==================== ERROR HANDLING ====================
    
    def _handle_database_error(self, error: SQLAlchemyError, 
                              operation: str) -> None:
        """Handle database errors consistently"""
        self.logger.error(f"Database error in {operation}: {str(error)}")
        self.db.rollback()
        
        if isinstance(error, IntegrityError):
            raise ConflictError(f"Constraint violation in {operation}")
        else:
            raise DatabaseOperationError(f"Database error in {operation}")
    
    def _raise_not_found(self, entity_name: str, identifier: Any) -> None:
        """Raise standardized not found error"""
        raise NotFoundError(f"{entity_name} not found with identifier: {identifier}")
    
    def _raise_validation_error(self, message: str, field: str = None,
                               details: Dict[str, Any] = None) -> None:
        """Raise standardized validation error"""
        error_details = details or {}
        if field:
            error_details['field'] = field
        raise ValidationError(message, details=error_details)
    
    def _raise_business_logic_error(self, message: str, code: str = None,
                                   details: Dict[str, Any] = None) -> None:
        """Raise standardized business logic error"""
        raise BusinessLogicError(message, code=code, details=details)


class CRUDService(BaseService):
    """
    Concrete service class providing full CRUD functionality.
    Use this for simple entities that don't need custom business logic.
    """
    pass


# ==================== SERVICE FACTORY ====================

def create_service(repository_class: Type[BaseRepository], 
                  model_class: Type[Any],
                  db: Session) -> BaseService:
    """
    Factory function to create service instances.
    
    Args:
        repository_class: Repository class to instantiate
        model_class: Model class for the repository
        db: Database session
        
    Returns:
        Service instance
    """
    repository = repository_class(model_class, db)
    return CRUDService(repository, db)


# ==================== EXPORTS ====================

__all__ = [
    'BaseService',
    'CRUDService',
    'create_service',
    'ModelType',
    'CreateSchemaType',
    'UpdateSchemaType',
    'ResponseSchemaType'
]