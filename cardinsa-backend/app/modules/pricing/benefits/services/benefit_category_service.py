"""
app/modules/benefits/services/benefit_category_service.py

Service layer for managing benefit categories.
Handles business logic for hierarchical category structures and category operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.base_service import BaseService
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.modules.pricing.benefits.models.benefit_category_model import BenefitCategory
from app.modules.pricing.benefits.repositories.benefit_category_repository import BenefitCategoryRepository
from app.modules.pricing.benefits.schemas.benefit_category_schema import (
    BenefitCategoryCreate,
    BenefitCategoryUpdate,
    BenefitCategoryResponse
)

import logging

logger = logging.getLogger(__name__)


class BenefitCategoryService(BaseService):  # ✅ Fixed: No generic parameters
    """Service for managing benefit categories with hierarchical support"""
    
    def __init__(self, repository: BenefitCategoryRepository, db: Session):
        super().__init__(repository, db)
    
    # ==================== VALIDATION HOOKS ====================
    
    def _validate_create_data(self, create_data: BenefitCategoryCreate) -> None:
        """Validate benefit category creation data"""
        super()._validate_create_data(create_data)
        
        # Validate required fields
        if not create_data.name or not create_data.name.strip():
            raise ValidationError("Category name is required")
        
        # Validate category code uniqueness
        if hasattr(create_data, 'code') and create_data.code:
            existing = self.repository.get_by_field('code', create_data.code)
            if existing:
                raise ValidationError(f"Category code '{create_data.code}' already exists")
        
        # Validate parent category exists if specified
        if hasattr(create_data, 'parent_id') and create_data.parent_id:
            parent = self.repository.get(create_data.parent_id)
            if not parent:
                raise ValidationError(f"Parent category not found: {create_data.parent_id}")
    
    def _validate_update_data(self, update_data: BenefitCategoryUpdate, existing_entity: BenefitCategory) -> None:
        """Validate benefit category update data"""
        super()._validate_update_data(update_data, existing_entity)
        
        # Validate name if provided
        if hasattr(update_data, 'name') and update_data.name is not None:
            if not update_data.name.strip():
                raise ValidationError("Category name cannot be empty")
        
        # Validate parent hierarchy to prevent circular references
        if hasattr(update_data, 'parent_id') and update_data.parent_id:
            if update_data.parent_id == existing_entity.id:
                raise ValidationError("Category cannot be its own parent")
            
            # Check for circular reference
            if self._would_create_circular_reference(existing_entity.id, update_data.parent_id):
                raise ValidationError("Update would create circular reference in category hierarchy")
    
    def _validate_delete(self, entity: BenefitCategory) -> None:
        """Validate category deletion"""
        super()._validate_delete(entity)
        
        # Check if category has children
        children = self.repository.db.query(BenefitCategory).filter(
            BenefitCategory.parent_id == entity.id
        ).count()
        
        if children > 0:
            raise BusinessLogicError(
                f"Cannot delete category with {children} child categories. "
                "Please delete or reassign child categories first."
            )
    
    # ==================== BUSINESS LOGIC METHODS ====================
    
    async def get_active_categories(self) -> List[BenefitCategory]:
        """Get all active categories"""
        try:
            return await self.repository.get_active_categories()
        except Exception as e:
            logger.error(f"Error getting active categories: {str(e)}")
            raise
    
    async def get_root_categories(self) -> List[BenefitCategory]:
        """Get top-level categories (no parent)"""
        try:
            return await self.repository.get_root_categories()
        except Exception as e:
            logger.error(f"Error getting root categories: {str(e)}")
            raise
    
    async def get_category_with_children(self, category_id: UUID) -> Optional[BenefitCategory]:
        """Get category with all its children"""
        try:
            category_id_str = str(category_id)
            return await self.repository.get_category_with_children(category_id_str)
        except Exception as e:
            logger.error(f"Error getting category with children: {str(e)}")
            raise
    
    async def get_category_hierarchy(self, category_id: UUID) -> List[BenefitCategory]:
        """Get full hierarchy path for a category"""
        try:
            category_id_str = str(category_id)
            return await self.repository.get_category_hierarchy(category_id_str)
        except Exception as e:
            logger.error(f"Error getting category hierarchy: {str(e)}")
            raise
    
    async def search_categories(self, search_term: str) -> List[BenefitCategory]:
        """Search categories by name or description"""
        try:
            if not search_term or not search_term.strip():
                raise ValidationError("Search term cannot be empty")
            
            return await self.repository.search_categories(search_term.strip())
        except Exception as e:
            logger.error(f"Error searching categories: {str(e)}")
            raise
    
    async def get_by_category_type(self, category_type: str) -> List[BenefitCategory]:
        """Get categories by type"""
        try:
            if not category_type:
                raise ValidationError("Category type is required")
            
            return await self.repository.get_by_category_type(category_type)
        except Exception as e:
            logger.error(f"Error getting categories by type: {str(e)}")
            raise
    
    def move_category(self, category_id: UUID, new_parent_id: Optional[UUID] = None) -> BenefitCategory:
        """Move category to a new parent"""
        try:
            # Get the category to move
            category = self.get_by_id(category_id)
            if not category:
                raise NotFoundError(f"Category not found: {category_id}")
            
            # Validate new parent if specified
            if new_parent_id:
                new_parent = self.get_by_id(new_parent_id)
                if not new_parent:
                    raise NotFoundError(f"New parent category not found: {new_parent_id}")
                
                # Prevent circular reference
                if self._would_create_circular_reference(category_id, new_parent_id):
                    raise BusinessLogicError("Move would create circular reference")
            
            # Update parent
            category.parent_id = new_parent_id
            self.db.commit()
            
            logger.info(f"Moved category {category_id} to parent {new_parent_id}")
            return category
            
        except Exception as e:
            logger.error(f"Error moving category: {str(e)}")
            self.db.rollback()
            raise
    
    def get_category_depth(self, category_id: UUID) -> int:
        """Get the depth of a category in the hierarchy"""
        try:
            depth = 0
            current_id = category_id
            
            while current_id:
                category = self.get_by_id(current_id)
                if not category:
                    break
                
                if category.parent_id:
                    current_id = category.parent_id
                    depth += 1
                else:
                    break
            
            return depth
            
        except Exception as e:
            logger.error(f"Error calculating category depth: {str(e)}")
            raise
    
    def get_category_tree(self, root_category_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get hierarchical tree structure of categories"""
        try:
            if root_category_id:
                root_categories = [self.get_by_id(root_category_id)]
            else:
                # Get all root categories
                root_categories = self.repository.db.query(BenefitCategory).filter(
                    BenefitCategory.parent_id.is_(None),
                    BenefitCategory.is_active == True
                ).order_by(BenefitCategory.display_order).all()
            
            def build_tree(category: BenefitCategory) -> Dict[str, Any]:
                children = self.repository.db.query(BenefitCategory).filter(
                    BenefitCategory.parent_id == category.id,
                    BenefitCategory.is_active == True
                ).order_by(BenefitCategory.display_order).all()
                
                return {
                    'id': str(category.id),
                    'name': category.name,
                    'code': getattr(category, 'code', None),
                    'display_order': getattr(category, 'display_order', 0),
                    'children': [build_tree(child) for child in children]
                }
            
            if root_category_id:
                return build_tree(root_categories[0])
            else:
                return {
                    'categories': [build_tree(cat) for cat in root_categories]
                }
                
        except Exception as e:
            logger.error(f"Error building category tree: {str(e)}")
            raise
    
    # ==================== HELPER METHODS ====================
    
    def _would_create_circular_reference(self, category_id: UUID, potential_parent_id: UUID) -> bool:
        """Check if setting potential_parent_id as parent would create circular reference"""
        try:
            current_id = potential_parent_id
            
            # Traverse up the hierarchy from potential parent
            visited = set()
            while current_id and current_id not in visited:
                visited.add(current_id)
                
                # If we reach the category we're trying to move, it's circular
                if current_id == category_id:
                    return True
                
                # Get parent of current category
                current_category = self.repository.get(current_id)
                if not current_category:
                    break
                    
                current_id = current_category.parent_id
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking circular reference: {str(e)}")
            return True  # Err on the side of caution
    
    # ==================== LIFECYCLE HOOKS ====================
    
    def _post_create_operations(self, entity: BenefitCategory) -> None:
        """Operations after category creation"""
        super()._post_create_operations(entity)
        logger.info(f"Created benefit category: {entity.name} (ID: {entity.id})")
    
    def _post_update_operations(self, updated_entity: BenefitCategory, 
                               original_entity: BenefitCategory) -> None:
        """Operations after category update"""
        super()._post_update_operations(updated_entity, original_entity)
        logger.info(f"Updated benefit category: {updated_entity.name} (ID: {updated_entity.id})")
    
    def _post_delete_operations(self, entity: BenefitCategory) -> None:
        """Operations after category deletion"""
        super()._post_delete_operations(entity)
        logger.info(f"Deleted benefit category: {entity.name} (ID: {entity.id})")


# ==================== SERVICE FACTORY ====================

def get_benefit_category_service(db: Session) -> BenefitCategoryService:
    """Factory function to create BenefitCategoryService instance"""
    repository = BenefitCategoryRepository(db)
    return BenefitCategoryService(repository, db)