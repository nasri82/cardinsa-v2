"""
app/modules/benefits/repositories/benefit_category_repository.py

Repository for managing benefit categories (Medical, Dental, Vision, etc.)
Handles hierarchical category structures and category-based queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc
from app.modules.pricing.benefits.models.benefit_category_model import BenefitCategory
from app.core.base_repository import BaseRepository
from app.core.exceptions import ValidationError, NotFoundError
import logging

logger = logging.getLogger(__name__)


class BenefitCategoryRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """Repository for managing benefit categories"""
    
    def __init__(self, db: Session):
        super().__init__(BenefitCategory, db)
    
    async def get_active_categories(self) -> List[BenefitCategory]:
        """Get all active benefit categories"""
        try:
            return self.db.query(BenefitCategory).filter(
                BenefitCategory.is_active == True
            ).order_by(BenefitCategory.display_order, BenefitCategory.name).all()
        except Exception as e:
            logger.error(f"Error fetching active categories: {str(e)}")
            raise
    
    async def get_root_categories(self) -> List[BenefitCategory]:
        """Get top-level categories (no parent)"""
        try:
            return self.db.query(BenefitCategory).filter(
                and_(
                    BenefitCategory.parent_id.is_(None),
                    BenefitCategory.is_active == True
                )
            ).order_by(BenefitCategory.display_order).all()
        except Exception as e:
            logger.error(f"Error fetching root categories: {str(e)}")
            raise
    
    async def get_category_with_children(self, category_id: str) -> Optional[BenefitCategory]:
        """Get category with all its children"""
        try:
            return self.db.query(BenefitCategory).options(
                joinedload(BenefitCategory.children)
            ).filter(BenefitCategory.id == category_id).first()
        except Exception as e:
            logger.error(f"Error fetching category with children: {str(e)}")
            raise
    
    async def get_category_hierarchy(self, category_id: str) -> List[BenefitCategory]:
        """Get full hierarchy path for a category"""
        try:
            category = await self.get_by_id(category_id)
            if not category:
                raise NotFoundError(f"Category {category_id} not found")
            
            hierarchy = [category]
            current = category
            
            while current.parent_id:
                parent = await self.get_by_id(current.parent_id)
                if parent:
                    hierarchy.insert(0, parent)
                    current = parent
                else:
                    break
            
            return hierarchy
        except Exception as e:
            logger.error(f"Error building category hierarchy: {str(e)}")
            raise
    
    async def search_categories(self, search_term: str) -> List[BenefitCategory]:
        """Search categories by name or description"""
        try:
            return self.db.query(BenefitCategory).filter(
                and_(
                    BenefitCategory.is_active == True,
                    or_(
                        BenefitCategory.name.ilike(f"%{search_term}%"),
                        BenefitCategory.description.ilike(f"%{search_term}%")
                    )
                )
            ).order_by(BenefitCategory.display_order).all()
        except Exception as e:
            logger.error(f"Error searching categories: {str(e)}")
            raise
    
    async def get_by_category_type(self, category_type: str) -> List[BenefitCategory]:
        """Get categories by type"""
        try:
            return self.db.query(BenefitCategory).filter(
                and_(
                    BenefitCategory.category_type == category_type,
                    BenefitCategory.is_active == True
                )
            ).order_by(BenefitCategory.display_order).all()
        except Exception as e:
            logger.error(f"Error fetching categories by type: {str(e)}")
            raise