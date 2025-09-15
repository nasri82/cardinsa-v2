# app/modules/insurance/quotations/services/quotation_item_service.py

from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
import logging

from ..models import QuotationItem
from ..schemas import (
    QuotationItemCreate, QuotationItemUpdate, QuotationItemResponse,
    QuotationItemSummary, QuotationItemBulkCreate, QuotationItemLocalizedResponse
)
from ..repositories import QuotationItemRepository, QuotationRepository
from app.core.exceptions import BusinessLogicError, ValidationError, NotFoundError, ConflictError


logger = logging.getLogger(__name__)


class QuotationItemService:
    """
    Service class for QuotationItem business logic
    
    Handles coverage item operations including creation, multilingual support,
    display order management, and business rule validation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.item_repo = QuotationItemRepository(db)
        self.quotation_repo = QuotationRepository(db)

    # ========== CREATE OPERATIONS ==========

    async def create_item(self, item_data: QuotationItemCreate, 
                         created_by: UUID = None) -> QuotationItemResponse:
        """Create a new quotation item with business validations"""
        try:
            # Validate quotation exists and can be modified
            await self._validate_quotation_modifiable(item_data.quotation_id)
            
            # Validate item data
            await self._validate_item_creation(item_data)
            
            # Create item
            item = self.item_repo.create_item(item_data, created_by)
            
            logger.info(f"Created quotation item {item.id} for quotation {item_data.quotation_id}")
            
            return QuotationItemResponse.from_orm(item)
            
        except Exception as e:
            logger.error(f"Error creating quotation item: {str(e)}")
            raise BusinessLogicError(f"Failed to create quotation item: {str(e)}")

    async def create_bulk_items(self, bulk_data: QuotationItemBulkCreate,
                               created_by: UUID = None) -> List[QuotationItemResponse]:
        """Create multiple quotation items in bulk"""
        try:
            # Validate quotation exists and can be modified
            await self._validate_quotation_modifiable(bulk_data.quotation_id)
            
            # Validate all items data
            for item_data in bulk_data.items:
                await self._validate_item_creation(item_data)
            
            # Create items in bulk
            items = self.item_repo.create_bulk_items(bulk_data.items, created_by)
            
            logger.info(f"Created {len(items)} items for quotation {bulk_data.quotation_id}")
            
            return [QuotationItemResponse.from_orm(item) for item in items]
            
        except Exception as e:
            logger.error(f"Error creating bulk quotation items: {str(e)}")
            raise BusinessLogicError(f"Failed to create bulk items: {str(e)}")

    # ========== READ OPERATIONS ==========

    async def get_item(self, item_id: UUID) -> Optional[QuotationItemResponse]:
        """Get quotation item by ID"""
        try:
            item = self.item_repo.get(item_id)
            if not item:
                return None
            
            return QuotationItemResponse.from_orm(item)
            
        except Exception as e:
            logger.error(f"Error retrieving quotation item {item_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve quotation item: {str(e)}")

    async def get_quotation_items(self, quotation_id: UUID, 
                                 active_only: bool = True) -> List[QuotationItemResponse]:
        """Get all items for a quotation"""
        try:
            items = self.item_repo.get_by_quotation_ordered(quotation_id)
            
            if active_only:
                items = [item for item in items if not item.archived_at]
            
            return [QuotationItemResponse.from_orm(item) for item in items]
            
        except Exception as e:
            logger.error(f"Error retrieving quotation items: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve quotation items: {str(e)}")

    async def get_localized_items(self, quotation_id: UUID, 
                                 language: str = 'en') -> List[QuotationItemLocalizedResponse]:
        """Get items with localized content"""
        try:
            if language not in ['en', 'ar']:
                raise ValidationError("Language must be 'en' or 'ar'")
            
            localized_data = self.item_repo.get_localized_items(quotation_id, language)
            
            return [
                QuotationItemLocalizedResponse(
                    id=item['id'],
                    quotation_id=item['quotation_id'], 
                    coverage_name=item['coverage_name'],
                    notes=item['notes'],
                    limit_amount=item['limit_amount'],
                    display_order=item['display_order'],
                    meta_data=item['meta_data'],
                    language=language
                ) 
                for item in localized_data
            ]
            
        except Exception as e:
            logger.error(f"Error retrieving localized items: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve localized items: {str(e)}")

    async def search_items(self, quotation_id: UUID, search_term: str,
                          language: str = None) -> List[QuotationItemResponse]:
        """Search items by coverage name or notes"""
        try:
            items = self.item_repo.search_items(quotation_id, search_term, language)
            return [QuotationItemResponse.from_orm(item) for item in items]
            
        except Exception as e:
            logger.error(f"Error searching quotation items: {str(e)}")
            raise BusinessLogicError(f"Failed to search items: {str(e)}")

    async def get_items_summary(self, quotation_id: UUID) -> Dict[str, Any]:
        """Get summary statistics for quotation items"""
        try:
            summary = self.item_repo.get_items_summary(quotation_id)
            return summary
            
        except Exception as e:
            logger.error(f"Error retrieving items summary: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve items summary: {str(e)}")

    # ========== UPDATE OPERATIONS ==========

    async def update_item(self, item_id: UUID, item_data: QuotationItemUpdate,
                         updated_by: UUID = None) -> Optional[QuotationItemResponse]:
        """Update quotation item with business validations"""
        try:
            # Check if item exists and quotation can be modified
            item = await self._validate_item_update(item_id)
            
            # Validate update data
            await self._validate_item_update_data(item_data)
            
            # Update item
            updated_item = self.item_repo.update(item_id, item_data, updated_by)
            
            logger.info(f"Updated quotation item {item_id}")
            
            return QuotationItemResponse.from_orm(updated_item) if updated_item else None
            
        except Exception as e:
            logger.error(f"Error updating quotation item {item_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to update quotation item: {str(e)}")

    async def update_display_order(self, item_id: UUID, new_order: int,
                                  updated_by: UUID = None) -> Optional[QuotationItemResponse]:
        """Update item display order with reordering"""
        try:
            # Validate item can be updated
            item = await self._validate_item_update(item_id)
            
            if new_order < 1:
                raise ValidationError("Display order must be greater than 0")
            
            # Update display order (repository handles reordering)
            updated_item = self.item_repo.update_display_order(item_id, new_order, updated_by)
            
            logger.info(f"Updated display order for item {item_id} to {new_order}")
            
            return QuotationItemResponse.from_orm(updated_item) if updated_item else None
            
        except Exception as e:
            logger.error(f"Error updating item display order: {str(e)}")
            raise BusinessLogicError(f"Failed to update display order: {str(e)}")

    async def reorder_items(self, quotation_id: UUID, item_orders: Dict[UUID, int],
                           updated_by: UUID = None) -> List[QuotationItemResponse]:
        """Reorder multiple items at once"""
        try:
            # Validate quotation can be modified
            await self._validate_quotation_modifiable(quotation_id)
            
            # Validate all items belong to the quotation
            for item_id in item_orders.keys():
                item = self.item_repo.get(item_id)
                if not item or item.quotation_id != quotation_id:
                    raise ValidationError(f"Item {item_id} does not belong to quotation {quotation_id}")
            
            # Validate display orders
            orders = list(item_orders.values())
            if len(set(orders)) != len(orders):
                raise ValidationError("Display orders must be unique")
            
            if any(order < 1 for order in orders):
                raise ValidationError("All display orders must be greater than 0")
            
            # Reorder items
            updated_items = self.item_repo.reorder_items(quotation_id, item_orders, updated_by)
            
            logger.info(f"Reordered {len(updated_items)} items for quotation {quotation_id}")
            
            return [QuotationItemResponse.from_orm(item) for item in updated_items]
            
        except Exception as e:
            logger.error(f"Error reordering items: {str(e)}")
            raise BusinessLogicError(f"Failed to reorder items: {str(e)}")

    async def update_coverage_names(self, item_id: UUID, coverage_name: str = None,
                                   coverage_name_ar: str = None,
                                   updated_by: UUID = None) -> Optional[QuotationItemResponse]:
        """Update coverage names in multiple languages"""
        try:
            # Validate item can be updated
            item = await self._validate_item_update(item_id)
            
            # Validate at least one name is provided
            if not coverage_name and not coverage_name_ar:
                raise ValidationError("At least one coverage name must be provided")
            
            # Update coverage names
            updated_item = self.item_repo.update_coverage_name(
                item_id, coverage_name, coverage_name_ar, updated_by
            )
            
            logger.info(f"Updated coverage names for item {item_id}")
            
            return QuotationItemResponse.from_orm(updated_item) if updated_item else None
            
        except Exception as e:
            logger.error(f"Error updating coverage names: {str(e)}")
            raise BusinessLogicError(f"Failed to update coverage names: {str(e)}")

    async def update_metadata(self, item_id: UUID, metadata: Dict[str, Any],
                             merge: bool = True, updated_by: UUID = None) -> Optional[QuotationItemResponse]:
        """Update item metadata"""
        try:
            # Validate item can be updated
            item = await self._validate_item_update(item_id)
            
            # Validate metadata
            if not isinstance(metadata, dict):
                raise ValidationError("Metadata must be a dictionary")
            
            # Update metadata
            updated_item = self.item_repo.update_metadata(item_id, metadata, merge, updated_by)
            
            logger.info(f"Updated metadata for item {item_id}")
            
            return QuotationItemResponse.from_orm(updated_item) if updated_item else None
            
        except Exception as e:
            logger.error(f"Error updating item metadata: {str(e)}")
            raise BusinessLogicError(f"Failed to update metadata: {str(e)}")

    # ========== DELETE OPERATIONS ==========

    async def delete_item(self, item_id: UUID, deleted_by: UUID = None) -> bool:
        """Soft delete quotation item"""
        try:
            # Validate item can be deleted
            item = await self._validate_item_deletion(item_id)
            
            # Check if this is the last item in quotation
            items_count = self.item_repo.get_items_count_by_quotation(item.quotation_id)
            if items_count <= 1:
                raise ConflictError("Cannot delete the last item in a quotation")
            
            # Soft delete item
            success = self.item_repo.soft_delete(item_id, deleted_by)
            
            if success:
                logger.info(f"Deleted quotation item {item_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting quotation item {item_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to delete quotation item: {str(e)}")

    async def delete_all_items(self, quotation_id: UUID, deleted_by: UUID = None) -> int:
        """Delete all items for a quotation"""
        try:
            # Validate quotation can be modified
            await self._validate_quotation_modifiable(quotation_id)
            
            # Delete all items (soft delete)
            deleted_count = self.item_repo.delete_all_by_quotation(quotation_id, hard_delete=False)
            
            logger.info(f"Deleted {deleted_count} items for quotation {quotation_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting all items: {str(e)}")
            raise BusinessLogicError(f"Failed to delete all items: {str(e)}")

    # ========== UTILITY OPERATIONS ==========

    async def duplicate_items_to_quotation(self, source_quotation_id: UUID,
                                          target_quotation_id: UUID,
                                          created_by: UUID = None) -> List[QuotationItemResponse]:
        """Duplicate items from one quotation to another"""
        try:
            # Validate both quotations exist
            source_quotation = self.quotation_repo.get(source_quotation_id)
            target_quotation = self.quotation_repo.get(target_quotation_id)
            
            if not source_quotation:
                raise NotFoundError("Source quotation not found")
            if not target_quotation:
                raise NotFoundError("Target quotation not found")
            
            # Validate target quotation can be modified
            await self._validate_quotation_modifiable(target_quotation_id)
            
            # Duplicate items
            duplicated_items = self.item_repo.duplicate_items_to_quotation(
                source_quotation_id, target_quotation_id, created_by
            )
            
            logger.info(f"Duplicated {len(duplicated_items)} items from {source_quotation_id} to {target_quotation_id}")
            
            return [QuotationItemResponse.from_orm(item) for item in duplicated_items]
            
        except Exception as e:
            logger.error(f"Error duplicating items: {str(e)}")
            raise BusinessLogicError(f"Failed to duplicate items: {str(e)}")

    async def validate_display_orders(self, quotation_id: UUID) -> Dict[str, Any]:
        """Validate and report on display order integrity"""
        try:
            validation_result = self.item_repo.validate_display_orders(quotation_id)
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating display orders: {str(e)}")
            raise BusinessLogicError(f"Failed to validate display orders: {str(e)}")

    async def fix_display_orders(self, quotation_id: UUID, updated_by: UUID = None) -> List[QuotationItemResponse]:
        """Fix display order issues by compacting orders"""
        try:
            # Validate quotation can be modified
            await self._validate_quotation_modifiable(quotation_id)
            
            # Get all items and reassign sequential orders
            items = self.item_repo.get_by_quotation_ordered(quotation_id)
            
            item_orders = {}
            for index, item in enumerate(items, 1):
                item_orders[item.id] = index
            
            # Apply the corrected orders
            updated_items = self.item_repo.reorder_items(quotation_id, item_orders, updated_by)
            
            logger.info(f"Fixed display orders for {len(updated_items)} items in quotation {quotation_id}")
            
            return [QuotationItemResponse.from_orm(item) for item in updated_items]
            
        except Exception as e:
            logger.error(f"Error fixing display orders: {str(e)}")
            raise BusinessLogicError(f"Failed to fix display orders: {str(e)}")

    # ========== VALIDATION METHODS ==========

    async def _validate_quotation_modifiable(self, quotation_id: UUID) -> None:
        """Validate quotation exists and can be modified"""
        quotation = self.quotation_repo.get(quotation_id)
        if not quotation:
            raise NotFoundError("Quotation not found")
        
        if quotation.is_locked:
            raise ConflictError("Cannot modify items in locked quotation")
        
        if quotation.status in ['converted', 'expired']:
            raise ConflictError(f"Cannot modify items in {quotation.status} quotation")

    async def _validate_item_creation(self, item_data: QuotationItemCreate) -> None:
        """Validate item creation business rules"""
        # Check coverage name requirements
        if not item_data.coverage_name and not item_data.coverage_name_ar:
            raise ValidationError("At least one coverage name (English or Arabic) is required")
        
        # Validate limit amount
        if item_data.limit_amount is not None and item_data.limit_amount < 0:
            raise ValidationError("Limit amount cannot be negative")
        
        # Check for duplicate coverage names within quotation
        if item_data.coverage_name:
            existing_item = self.item_repo.get_by_coverage_name(
                item_data.quotation_id, item_data.coverage_name, 'en'
            )
            if existing_item:
                raise ConflictError(f"Coverage '{item_data.coverage_name}' already exists")

    async def _validate_item_update(self, item_id: UUID) -> QuotationItem:
        """Validate item can be updated"""
        item = self.item_repo.get(item_id)
        if not item:
            raise NotFoundError("Quotation item not found")
        
        await self._validate_quotation_modifiable(item.quotation_id)
        
        return item

    async def _validate_item_update_data(self, item_data: QuotationItemUpdate) -> None:
        """Validate item update data"""
        # Validate limit amount if provided
        if item_data.limit_amount is not None and item_data.limit_amount < 0:
            raise ValidationError("Limit amount cannot be negative")
        
        # Validate at least one coverage name remains
        if (item_data.coverage_name is not None and not item_data.coverage_name and 
            item_data.coverage_name_ar is not None and not item_data.coverage_name_ar):
            raise ValidationError("At least one coverage name must be provided")

    async def _validate_item_deletion(self, item_id: UUID) -> QuotationItem:
        """Validate item can be deleted"""
        item = self.item_repo.get(item_id)
        if not item:
            raise NotFoundError("Quotation item not found")
        
        await self._validate_quotation_modifiable(item.quotation_id)
        
        return item