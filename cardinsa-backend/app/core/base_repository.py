# app/core/base_repository.py

from typing import TypeVar, Generic, Optional, List, Dict, Any, Type, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.exc import NoResultFound
from app.core.database import Base
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseRepository:
    """
    Base repository class for common database operations.
    Provides CRUD operations and common query patterns.
    
    Note: We use a non-generic base class to avoid typing issues,
    then let subclasses handle the generic typing as needed.
    """
    
    def __init__(self, model: Type[Any], db: Session):
        """
        Initialize the repository with a model class and database session.
        
        Args:
            model: The SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    # ==================== CREATE OPERATIONS ====================
    
    def create(self, obj_in: Union[Dict[str, Any], Any]) -> Any:
        """
        Create a new record from a dictionary or Pydantic schema.
        
        Args:
            obj_in: Dictionary of field values or Pydantic schema instance
            
        Returns:
            Created model instance
        """
        if hasattr(obj_in, 'model_dump') or hasattr(obj_in, 'dict'):
            # It's a Pydantic model
            if hasattr(obj_in, 'model_dump'):
                # Pydantic v2
                obj_data = obj_in.model_dump(exclude_unset=True)
            else:
                # Pydantic v1 fallback
                obj_data = obj_in.dict(exclude_unset=True)
        else:
            # It's already a dictionary
            obj_data = obj_in
        
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        logger.info(f"Created {self.model.__name__} with ID: {db_obj.id}")
        return db_obj

    def create_from_schema(self, obj_in: Any) -> Any:
        """
        Create a new record from a Pydantic schema.
        
        Args:
            obj_in: Pydantic schema instance
            
        Returns:
            Created model instance
        """
        return self.create(obj_in)

    def create_batch(self, objects_in: List[Union[Dict[str, Any], Any]]) -> List[Any]:
        """
        Create multiple records in batch.
        
        Args:
            objects_in: List of dictionaries or Pydantic schemas
            
        Returns:
            List of created model instances
        """
        db_objects = []
        for obj_data in objects_in:
            if hasattr(obj_data, 'model_dump') or hasattr(obj_data, 'dict'):
                # It's a Pydantic model
                if hasattr(obj_data, 'model_dump'):
                    obj_dict = obj_data.model_dump(exclude_unset=True)
                else:
                    obj_dict = obj_data.dict(exclude_unset=True)
            else:
                obj_dict = obj_data
            
            db_objects.append(self.model(**obj_dict))
        
        self.db.add_all(db_objects)
        self.db.commit()
        for obj in db_objects:
            self.db.refresh(obj)
        logger.info(f"Created batch of {len(db_objects)} {self.model.__name__} records")
        return db_objects

    # ==================== READ OPERATIONS ====================
    
    def get(self, id: Union[UUID, int]) -> Optional[Any]:
        """
        Get a single record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        return self.db.get(self.model, id)

    def get_by_field(self, field_name: str, field_value: Any) -> Optional[Any]:
        """
        Get a single record by a specific field.
        
        Args:
            field_name: Field name to search by
            field_value: Field value to match
            
        Returns:
            Model instance or None if not found
        """
        return self.db.scalar(
            select(self.model).where(getattr(self.model, field_name) == field_value)
        )

    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[Any]:
        """
        Get multiple records with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field:value filters
            order_by: Field name to order by
            order_desc: Whether to order in descending order
            
        Returns:
            List of model instances
        """
        query = select(self.model)
        
        # Apply filters
        if filters:
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name):
                    query = query.where(getattr(self.model, field_name) == field_value)
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            query = query.order_by(order_column.desc() if order_desc else order_column)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return list(self.db.scalars(query))

    def get_all(self) -> List[Any]:
        """
        Get all records.
        
        Returns:
            List of all model instances
        """
        return list(self.db.scalars(select(self.model)))

    def exists(self, id: Union[UUID, int]) -> bool:
        """
        Check if a record exists by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if record exists, False otherwise
        """
        return self.db.get(self.model, id) is not None

    def exists_by_field(self, field_name: str, field_value: Any) -> bool:
        """
        Check if a record exists by a specific field.
        
        Args:
            field_name: Field name to check
            field_value: Field value to match
            
        Returns:
            True if record exists, False otherwise
        """
        return self.db.scalar(
            select(func.count(self.model.id))
            .where(getattr(self.model, field_name) == field_value)
        ) > 0

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering.
        
        Args:
            filters: Dictionary of field:value filters
            
        Returns:
            Number of records matching filters
        """
        query = select(func.count(self.model.id))
        
        if filters:
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name):
                    query = query.where(getattr(self.model, field_name) == field_value)
        
        return self.db.scalar(query) or 0

    # ==================== UPDATE OPERATIONS ====================
    
    def update(self, id: Union[UUID, int], obj_in: Union[Dict[str, Any], Any]) -> Optional[Any]:
        """
        Update a record by ID from a dictionary or Pydantic schema.
        
        Args:
            id: Record ID
            obj_in: Dictionary of field values or Pydantic schema instance
            
        Returns:
            Updated model instance or None if not found
        """
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        if hasattr(obj_in, 'model_dump') or hasattr(obj_in, 'dict'):
            # It's a Pydantic model
            if hasattr(obj_in, 'model_dump'):
                # Pydantic v2
                obj_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)
            else:
                # Pydantic v1 fallback
                obj_data = obj_in.dict(exclude_unset=True, exclude_none=True)
        else:
            # It's already a dictionary
            obj_data = obj_in
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        logger.info(f"Updated {self.model.__name__} with ID: {id}")
        return db_obj

    def update_from_schema(self, id: Union[UUID, int], obj_in: Any) -> Optional[Any]:
        """
        Update a record from a Pydantic schema.
        
        Args:
            id: Record ID
            obj_in: Pydantic schema instance
            
        Returns:
            Updated model instance or None if not found
        """
        return self.update(id, obj_in)

    def update_by_field(
        self, 
        field_name: str, 
        field_value: Any, 
        obj_in: Union[Dict[str, Any], Any]
    ) -> Optional[Any]:
        """
        Update a record by a specific field.
        
        Args:
            field_name: Field name to search by
            field_value: Field value to match
            obj_in: Dictionary of field values or Pydantic schema to update
            
        Returns:
            Updated model instance or None if not found
        """
        db_obj = self.get_by_field(field_name, field_value)
        if not db_obj:
            return None
        
        return self.update(db_obj.id, obj_in)

    def update_multi(self, filters: Dict[str, Any], obj_in: Dict[str, Any]) -> int:
        """
        Update multiple records matching filters.
        
        Args:
            filters: Dictionary of field:value filters
            obj_in: Dictionary of field values to update
            
        Returns:
            Number of records updated
        """
        query = update(self.model)
        
        for field_name, field_value in filters.items():
            if hasattr(self.model, field_name):
                query = query.where(getattr(self.model, field_name) == field_value)
        
        query = query.values(**obj_in)
        result = self.db.execute(query)
        self.db.commit()
        
        rows_updated = result.rowcount
        logger.info(f"Updated {rows_updated} {self.model.__name__} records")
        return rows_updated

    # ==================== DELETE OPERATIONS ====================
    
    def delete(self, id: Union[UUID, int]) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if record was deleted, False if not found
        """
        db_obj = self.get(id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        logger.info(f"Deleted {self.model.__name__} with ID: {id}")
        return True

    def delete_by_field(self, field_name: str, field_value: Any) -> bool:
        """
        Delete a record by a specific field.
        
        Args:
            field_name: Field name to search by
            field_value: Field value to match
            
        Returns:
            True if record was deleted, False if not found
        """
        db_obj = self.get_by_field(field_name, field_value)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        logger.info(f"Deleted {self.model.__name__} by {field_name}: {field_value}")
        return True

    def delete_multi(self, filters: Dict[str, Any]) -> int:
        """
        Delete multiple records matching filters.
        
        Args:
            filters: Dictionary of field:value filters
            
        Returns:
            Number of records deleted
        """
        query = delete(self.model)
        
        for field_name, field_value in filters.items():
            if hasattr(self.model, field_name):
                query = query.where(getattr(self.model, field_name) == field_value)
        
        result = self.db.execute(query)
        self.db.commit()
        
        rows_deleted = result.rowcount
        logger.info(f"Deleted {rows_deleted} {self.model.__name__} records")
        return rows_deleted

    # ==================== SOFT DELETE OPERATIONS ====================
    
    def soft_delete(self, id: Union[UUID, int]) -> Optional[Any]:
        """
        Soft delete a record (set archived_at or is_deleted field).
        
        Args:
            id: Record ID
            
        Returns:
            Updated model instance or None if not found
        """
        from datetime import datetime, timezone
        
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        # Try different soft delete patterns
        if hasattr(db_obj, 'archived_at'):
            db_obj.archived_at = datetime.now(timezone.utc)
        elif hasattr(db_obj, 'deleted_at'):
            db_obj.deleted_at = datetime.now(timezone.utc)
        elif hasattr(db_obj, 'is_deleted'):
            db_obj.is_deleted = True
        elif hasattr(db_obj, 'is_active'):
            db_obj.is_active = False
        else:
            # Fallback to hard delete if no soft delete fields
            return self.delete(id)
        
        self.db.commit()
        self.db.refresh(db_obj)
        logger.info(f"Soft deleted {self.model.__name__} with ID: {id}")
        return db_obj

    # ==================== UTILITY METHODS ====================
    
    def refresh(self, db_obj: Any) -> Any:
        """
        Refresh a model instance from the database.
        
        Args:
            db_obj: Model instance to refresh
            
        Returns:
            Refreshed model instance
        """
        self.db.refresh(db_obj)
        return db_obj

    def flush(self) -> None:
        """
        Flush the current transaction.
        """
        self.db.flush()

    def commit(self) -> None:
        """
        Commit the current transaction.
        """
        self.db.commit()

    def rollback(self) -> None:
        """
        Rollback the current transaction.
        """
        self.db.rollback()

    # ==================== SEARCH METHODS ====================
    
    def search(
        self, 
        search_term: str, 
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """
        Search records across multiple text fields.
        
        Args:
            search_term: Term to search for
            search_fields: List of field names to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching model instances
        """
        if not search_term or not search_fields:
            return []
        
        query = select(self.model)
        search_conditions = []
        
        for field_name in search_fields:
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                search_conditions.append(field.ilike(f"%{search_term}%"))
        
        if search_conditions:
            query = query.where(or_(*search_conditions))
        
        query = query.offset(skip).limit(limit)
        return list(self.db.scalars(query))

    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Dict[str, Any]:
        """
        Get paginated results with metadata.
        
        Args:
            page: Page number (1-based)
            page_size: Items per page
            filters: Dictionary of field:value filters
            order_by: Field name to order by
            order_desc: Whether to order in descending order
            
        Returns:
            Dictionary with items and pagination metadata
        """
        skip = (page - 1) * page_size
        
        # Get items
        items = self.get_multi(
            skip=skip,
            limit=page_size,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
        
        # Get total count
        total_items = self.count(filters=filters)
        total_pages = (total_items + page_size - 1) // page_size
        
        return {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }


# Type-safe repository class for those who want explicit typing
class TypedRepository(BaseRepository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    A typed version of BaseRepository that provides explicit generic typing.
    This is for repositories that want strong typing support.
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        super().__init__(model, db)
    
    def create(self, obj_in: Union[Dict[str, Any], CreateSchemaType]) -> ModelType:
        return super().create(obj_in)
    
    def update(self, id: Union[UUID, int], obj_in: Union[Dict[str, Any], UpdateSchemaType]) -> Optional[ModelType]:
        return super().update(id, obj_in)