# app/modules/pricing/quotations/repositories/quotation_item_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime

from ..models import QuotationItem
from ..schemas import QuotationItemCreate, QuotationItemUpdate
from app.core.base_repository import BaseRepository


class QuotationItemRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """
    Repository class for QuotationItem operations
    
    Provides data access methods for quotation items including
    multilingual support, ordering, and coverage management.
    """

    def __init__(self, db: Session):
        super().__init__(QuotationItem, db)

    # ========== CREATE OPERATIONS ==========

    def create_item(self, item_data: QuotationItemCreate, created_by: UUID = None) -> QuotationItem:
        """Create a new quotation item with audit tracking"""
        # Convert Pydantic model to dict
        if hasattr(item_data, 'model_dump'):
            item_dict = item_data.model_dump(exclude_unset=True)
        else:
            item_dict = item_data.dict(exclude_unset=True)
        
        item = QuotationItem(**item_dict)
        item.created_by = created_by
        
        # Auto-assign display order if not provided
        if item.display_order is None or item.display_order == 0:
            item.display_order = self._get_next_display_order(item.quotation_id)
        
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_bulk_items(self, items_data: List[QuotationItemCreate], 
                         created_by: UUID = None) -> List[QuotationItem]:
        """Create multiple quotation items in bulk"""
        created_items = []
        
        for item_data in items_data:
            item = self.create_item(item_data, created_by)
            created_items.append(item)
        
        return created_items

    # ========== READ OPERATIONS ==========

    def get_by_quotation(self, quotation_id: UUID, active_only: bool = True) -> List[QuotationItem]:
        """Get all items for a quotation"""
        query = self.db.query(self.model).filter(
            self.model.quotation_id == quotation_id
        )
        
        if active_only:
            query = query.filter(self.model.archived_at.is_(None))
        
        return query.order_by(asc(self.model.display_order)).all()

    def get_by_quotation_ordered(self, quotation_id: UUID) -> List[QuotationItem]:
        """Get quotation items ordered by display_order"""
        return self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.archived_at.is_(None)
            )
        ).order_by(asc(self.model.display_order), asc(self.model.created_at)).all()

    def get_by_coverage_name(self, quotation_id: UUID, coverage_name: str, 
                           language: str = 'en') -> Optional[QuotationItem]:
        """Get item by coverage name and language"""
        if language == 'ar':
            return self.db.query(self.model).filter(
                and_(
                    self.model.quotation_id == quotation_id,
                    self.model.coverage_name_ar == coverage_name,
                    self.model.archived_at.is_(None)
                )
            ).first()
        else:
            return self.db.query(self.model).filter(
                and_(
                    self.model.quotation_id == quotation_id,
                    self.model.coverage_name == coverage_name,
                    self.model.archived_at.is_(None)
                )
            ).first()

    def search_items(self, quotation_id: UUID, search_term: str, 
                    language: str = None) -> List[QuotationItem]:
        """Search items by coverage name or notes"""
        search_pattern = f"%{search_term}%"
        
        query = self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.archived_at.is_(None)
            )
        )
        
        if language == 'ar':
            query = query.filter(
                or_(
                    self.model.coverage_name_ar.ilike(search_pattern),
                    self.model.notes_ar.ilike(search_pattern)
                )
            )
        elif language == 'en':
            query = query.filter(
                or_(
                    self.model.coverage_name.ilike(search_pattern),
                    self.model.notes.ilike(search_pattern)
                )
            )
        else:
            # Search in both languages
            query = query.filter(
                or_(
                    self.model.coverage_name.ilike(search_pattern),
                    self.model.coverage_name_ar.ilike(search_pattern),
                    self.model.notes.ilike(search_pattern),
                    self.model.notes_ar.ilike(search_pattern)
                )
            )
        
        return query.order_by(asc(self.model.display_order)).all()

    def get_items_with_limits_above(self, quotation_id: UUID, 
                                   min_limit: float) -> List[QuotationItem]:
        """Get items with limit amounts above specified value"""
        return self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.limit_amount >= min_limit,
                self.model.archived_at.is_(None)
            )
        ).order_by(desc(self.model.limit_amount)).all()

    def get_items_by_metadata_field(self, quotation_id: UUID, 
                                   field_key: str, field_value: Any) -> List[QuotationItem]:
        """Get items by metadata field value"""
        return self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.meta_data[field_key].as_string() == str(field_value),
                self.model.archived_at.is_(None)
            )
        ).order_by(asc(self.model.display_order)).all()

    # ========== UPDATE OPERATIONS ==========

    def update_display_order(self, item_id: UUID, new_order: int, 
                           updated_by: UUID = None) -> Optional[QuotationItem]:
        """Update item display order"""
        item = self.get(item_id)
        if not item:
            return None
        
        old_order = item.display_order
        item.display_order = new_order
        item.updated_by = updated_by
        
        # Reorder other items if necessary
        if old_order != new_order:
            self._reorder_items(item.quotation_id, old_order, new_order)
        
        self.db.commit()
        return item

    def reorder_items(self, quotation_id: UUID, item_orders: Dict[UUID, int],
                     updated_by: UUID = None) -> List[QuotationItem]:
        """Reorder multiple items at once"""
        items = []
        
        for item_id, new_order in item_orders.items():
            item = self.get(item_id)
            if item and item.quotation_id == quotation_id:
                item.display_order = new_order
                item.updated_by = updated_by
                items.append(item)
        
        self.db.commit()
        return items

    def update_coverage_name(self, item_id: UUID, coverage_name: str = None,
                           coverage_name_ar: str = None, updated_by: UUID = None) -> Optional[QuotationItem]:
        """Update coverage names"""
        item = self.get(item_id)
        if not item:
            return None
        
        if coverage_name is not None:
            item.coverage_name = coverage_name
        if coverage_name_ar is not None:
            item.coverage_name_ar = coverage_name_ar
        
        item.updated_by = updated_by
        self.db.commit()
        return item

    def update_limit_amount(self, item_id: UUID, limit_amount: float,
                          updated_by: UUID = None) -> Optional[QuotationItem]:
        """Update item limit amount"""
        item = self.get(item_id)
        if not item:
            return None
        
        item.limit_amount = limit_amount
        item.updated_by = updated_by
        self.db.commit()
        return item

    def update_metadata(self, item_id: UUID, metadata: Dict[str, Any],
                       merge: bool = True, updated_by: UUID = None) -> Optional[QuotationItem]:
        """Update item metadata"""
        item = self.get(item_id)
        if not item:
            return None
        
        if merge and item.meta_data:
            # Merge with existing metadata
            updated_metadata = item.meta_data.copy()
            updated_metadata.update(metadata)
            item.meta_data = updated_metadata
        else:
            # Replace metadata entirely
            item.meta_data = metadata
        
        item.updated_by = updated_by
        self.db.commit()
        return item

    def add_metadata_field(self, item_id: UUID, key: str, value: Any,
                          updated_by: UUID = None) -> Optional[QuotationItem]:
        """Add single metadata field"""
        item = self.get(item_id)
        if not item:
            return None
        
        if not item.meta_data:
            item.meta_data = {}
        
        item.meta_data[key] = value
        item.updated_by = updated_by
        self.db.commit()
        return item

    def remove_metadata_field(self, item_id: UUID, key: str,
                             updated_by: UUID = None) -> Optional[QuotationItem]:
        """Remove single metadata field"""
        item = self.get(item_id)
        if not item or not item.meta_data or key not in item.meta_data:
            return None
        
        del item.meta_data[key]
        item.updated_by = updated_by
        self.db.commit()
        return item

    # ========== DELETE OPERATIONS ==========

    def soft_delete(self, item_id: UUID, deleted_by: UUID = None) -> bool:
        """Soft delete item by setting archived_at"""
        item = self.get(item_id)
        if not item:
            return False
        
        item.archived_at = datetime.utcnow()
        item.updated_by = deleted_by
        self.db.commit()
        
        # Reorder remaining items
        self._compact_display_orders(item.quotation_id)
        
        return True

    def restore_item(self, item_id: UUID, restored_by: UUID = None) -> Optional[QuotationItem]:
        """Restore a soft-deleted item"""
        item = self.db.query(self.model).filter(
            and_(
                self.model.id == item_id,
                self.model.archived_at.isnot(None)
            )
        ).first()
        
        if item:
            item.archived_at = None
            item.updated_by = restored_by
            
            # Assign new display order
            item.display_order = self._get_next_display_order(item.quotation_id)
            
            self.db.commit()
        
        return item

    def delete_all_by_quotation(self, quotation_id: UUID, 
                               hard_delete: bool = False) -> int:
        """Delete all items for a quotation"""
        if hard_delete:
            count = self.db.query(self.model).filter(
                self.model.quotation_id == quotation_id
            ).count()
            
            self.db.query(self.model).filter(
                self.model.quotation_id == quotation_id
            ).delete()
        else:
            items = self.db.query(self.model).filter(
                and_(
                    self.model.quotation_id == quotation_id,
                    self.model.archived_at.is_(None)
                )
            ).all()
            
            count = len(items)
            for item in items:
                item.archived_at = datetime.utcnow()
        
        self.db.commit()
        return count

    # ========== QUERY OPERATIONS ==========

    def get_items_summary(self, quotation_id: UUID) -> Dict[str, Any]:
        """Get summary statistics for quotation items"""
        query = self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.archived_at.is_(None)
            )
        )
        
        total_items = query.count()
        
        # Sum of all limits
        total_limit = self.db.query(
            func.coalesce(func.sum(self.model.limit_amount), 0)
        ).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.archived_at.is_(None)
            )
        ).scalar()
        
        # Average limit
        avg_limit = self.db.query(
            func.avg(self.model.limit_amount)
        ).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.limit_amount.isnot(None),
                self.model.archived_at.is_(None)
            )
        ).scalar()
        
        # Items with metadata count
        items_with_metadata = query.filter(
            self.model.meta_data.isnot(None)
        ).count()
        
        # Items with both language names
        bilingual_items = query.filter(
            and_(
                self.model.coverage_name.isnot(None),
                self.model.coverage_name_ar.isnot(None)
            )
        ).count()
        
        return {
            'total_items': total_items,
            'total_limit_amount': float(total_limit),
            'average_limit_amount': float(avg_limit) if avg_limit else 0,
            'items_with_metadata': items_with_metadata,
            'bilingual_items': bilingual_items,
            'completion_rate': (bilingual_items / total_items * 100) if total_items > 0 else 0
        }

    def get_localized_items(self, quotation_id: UUID, language: str = 'en') -> List[Dict[str, Any]]:
        """Get items with localized content"""
        items = self.get_by_quotation_ordered(quotation_id)
        
        localized_items = []
        for item in items:
            if language == 'ar':
                coverage_name = item.coverage_name_ar or item.coverage_name
                notes = item.notes_ar or item.notes
            else:
                coverage_name = item.coverage_name or item.coverage_name_ar
                notes = item.notes or item.notes_ar
            
            localized_items.append({
                'id': item.id,
                'coverage_name': coverage_name,
                'notes': notes,
                'limit_amount': item.limit_amount,
                'display_order': item.display_order,
                'meta_data': item.meta_data,
                'language': language
            })
        
        return localized_items

    # ========== HELPER METHODS ==========

    def _get_next_display_order(self, quotation_id: UUID) -> int:
        """Get the next available display order"""
        max_order = self.db.query(
            func.max(self.model.display_order)
        ).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.archived_at.is_(None)
            )
        ).scalar()
        
        return (max_order or 0) + 1

    def _reorder_items(self, quotation_id: UUID, old_order: int, new_order: int) -> None:
        """Reorder items after display order change"""
        if old_order == new_order:
            return
        
        if new_order > old_order:
            # Moving down - shift items up
            self.db.query(self.model).filter(
                and_(
                    self.model.quotation_id == quotation_id,
                    self.model.display_order > old_order,
                    self.model.display_order <= new_order,
                    self.model.archived_at.is_(None)
                )
            ).update({
                self.model.display_order: self.model.display_order - 1
            })
        else:
            # Moving up - shift items down
            self.db.query(self.model).filter(
                and_(
                    self.model.quotation_id == quotation_id,
                    self.model.display_order >= new_order,
                    self.model.display_order < old_order,
                    self.model.archived_at.is_(None)
                )
            ).update({
                self.model.display_order: self.model.display_order + 1
            })

    def _compact_display_orders(self, quotation_id: UUID) -> None:
        """Compact display orders after item deletion"""
        items = self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.archived_at.is_(None)
            )
        ).order_by(asc(self.model.display_order)).all()
        
        for index, item in enumerate(items, 1):
            item.display_order = index
        
        self.db.commit()

    def get_items_count_by_quotation(self, quotation_id: UUID, active_only: bool = True) -> int:
        """Get count of items for a quotation"""
        query = self.db.query(func.count(self.model.id)).filter(
            self.model.quotation_id == quotation_id
        )
        
        if active_only:
            query = query.filter(self.model.archived_at.is_(None))
        
        return query.scalar()

    def duplicate_items_to_quotation(self, source_quotation_id: UUID, 
                                   target_quotation_id: UUID,
                                   created_by: UUID = None) -> List[QuotationItem]:
        """Duplicate items from one quotation to another"""
        source_items = self.get_by_quotation_ordered(source_quotation_id)
        
        duplicated_items = []
        for source_item in source_items:
            # Create new item with same data
            item_data = {
                'quotation_id': target_quotation_id,
                'coverage_name': source_item.coverage_name,
                'coverage_name_ar': source_item.coverage_name_ar,
                'limit_amount': source_item.limit_amount,
                'notes': source_item.notes,
                'notes_ar': source_item.notes_ar,
                'display_order': source_item.display_order,
                'meta_data': source_item.meta_data
            }
            
            new_item = QuotationItem(**item_data)
            new_item.created_by = created_by
            
            self.db.add(new_item)
            duplicated_items.append(new_item)
        
        self.db.commit()
        return duplicated_items

    def validate_display_orders(self, quotation_id: UUID) -> Dict[str, Any]:
        """Validate and report on display order integrity"""
        items = self.get_by_quotation_ordered(quotation_id)
        
        issues = []
        duplicates = []
        gaps = []
        
        orders = [item.display_order for item in items]
        
        # Check for duplicates
        seen_orders = set()
        for order in orders:
            if order in seen_orders:
                duplicates.append(order)
            seen_orders.add(order)
        
        # Check for gaps
        if orders:
            expected_orders = set(range(1, len(orders) + 1))
            actual_orders = set(orders)
            gaps = list(expected_orders - actual_orders)
        
        if duplicates:
            issues.append(f"Duplicate display orders: {duplicates}")
        if gaps:
            issues.append(f"Missing display orders: {gaps}")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'total_items': len(items),
            'order_range': f"1-{max(orders)}" if orders else "None"
        }