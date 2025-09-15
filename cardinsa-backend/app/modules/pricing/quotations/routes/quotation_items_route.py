# app/modules/insurance/quotations/routes/quotation_items_route.py

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
import logging

from app.core.dependencies import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import handle_exceptions
from app.core.responses import create_response, create_error_response
from ..services import QuotationItemService
from ..schemas import (
    QuotationItemCreate, QuotationItemUpdate, QuotationItemResponse,
    QuotationItemSummary, QuotationItemBulkCreate, QuotationItemLocalizedResponse,
    QuotationItemMetadataUpdate
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quotations/{quotation_id}/items", tags=["quotation-items"])


# ========== DEPENDENCY INJECTION ==========

def get_quotation_item_service(db: Session = Depends(get_db)) -> QuotationItemService:
    """Get quotation item service instance"""
    return QuotationItemService(db)


# ========== CREATE ENDPOINTS ==========

@router.post("/",
             response_model=QuotationItemResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create quotation item",
             description="Add a new coverage item to a quotation")
@handle_exceptions
async def create_quotation_item(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    item_data: QuotationItemCreate = Body(...),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Create a new coverage item for a quotation.
    
    **Parameters:**
    - **quotation_id**: UUID of the parent quotation
    - **item_data**: Coverage item data including names in multiple languages
    
    **Returns:**
    - **201**: Successfully created item
    - **400**: Validation error
    - **404**: Quotation not found
    - **409**: Coverage already exists or quotation locked
    """
    try:
        # Ensure item belongs to the specified quotation
        item_data.quotation_id = quotation_id
        
        item = await item_service.create_item(
            item_data=item_data,
            created_by=current_user.id
        )
        
        return create_response(
            data=item,
            message="Coverage item created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating quotation item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create coverage item"
        )


@router.post("/bulk",
             response_model=List[QuotationItemResponse],
             status_code=status.HTTP_201_CREATED,
             summary="Create multiple quotation items",
             description="Add multiple coverage items to a quotation in bulk")
@handle_exceptions
async def create_bulk_quotation_items(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    bulk_data: QuotationItemBulkCreate = Body(...),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Create multiple coverage items in bulk.
    
    **Request Body:**
    ```json
    {
        "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
        "items": [
            {
                "coverage_name": "Third Party Liability",
                "coverage_name_ar": "تأمين الطرف الثالث",
                "limit_amount": 100000.00
            },
            {
                "coverage_name": "Comprehensive Coverage",
                "coverage_name_ar": "التغطية الشاملة",
                "limit_amount": 200000.00
            }
        ]
    }
    ```
    """
    try:
        # Ensure all items belong to the specified quotation
        bulk_data.quotation_id = quotation_id
        
        items = await item_service.create_bulk_items(
            bulk_data=bulk_data,
            created_by=current_user.id
        )
        
        return create_response(
            data=items,
            message=f"Created {len(items)} coverage items successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating bulk quotation items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create coverage items"
        )


# ========== READ ENDPOINTS ==========

@router.get("/",
            response_model=List[QuotationItemResponse],
            summary="Get quotation items",
            description="Retrieve all coverage items for a quotation")
@handle_exceptions
async def get_quotation_items(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    active_only: bool = Query(True, description="Include only active (non-archived) items"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Get all coverage items for a quotation.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **active_only**: Whether to include only active items (default: true)
    
    **Returns:**
    - **200**: List of coverage items ordered by display_order
    """
    try:
        items = await item_service.get_quotation_items(
            quotation_id=quotation_id,
            active_only=active_only
        )
        
        return create_response(
            data=items,
            message=f"Retrieved {len(items)} coverage items"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving quotation items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve coverage items"
        )


@router.get("/localized",
            response_model=List[QuotationItemLocalizedResponse],
            summary="Get localized quotation items",
            description="Retrieve coverage items with localized content")
@handle_exceptions
async def get_localized_quotation_items(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    language: str = Query("en", regex="^(en|ar)$", description="Language code (en/ar)"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Get coverage items with localized content.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **language**: Language code ('en' for English, 'ar' for Arabic)
    
    **Returns:**
    - **200**: List of items with content in specified language
    """
    try:
        items = await item_service.get_localized_items(
            quotation_id=quotation_id,
            language=language
        )
        
        return create_response(
            data=items,
            message=f"Retrieved {len(items)} items in {language}"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving localized items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve localized items"
        )


@router.get("/search",
            response_model=List[QuotationItemResponse],
            summary="Search quotation items",
            description="Search coverage items by name or notes")
@handle_exceptions
async def search_quotation_items(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    search_term: str = Query(..., min_length=2, description="Search term (minimum 2 characters)"),
    language: Optional[str] = Query(None, regex="^(en|ar)$", description="Search in specific language"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Search coverage items by coverage name or notes.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **search_term**: Text to search for
    - **language**: Language to search in (optional, searches both if not specified)
    
    **Returns:**
    - **200**: List of matching coverage items
    """
    try:
        items = await item_service.search_items(
            quotation_id=quotation_id,
            search_term=search_term,
            language=language
        )
        
        return create_response(
            data=items,
            message=f"Found {len(items)} items matching '{search_term}'"
        )
        
    except Exception as e:
        logger.error(f"Error searching quotation items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search coverage items"
        )


@router.get("/summary",
            response_model=Dict[str, Any],
            summary="Get items summary",
            description="Get summary statistics for quotation items")
@handle_exceptions
async def get_quotation_items_summary(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Get summary statistics for quotation items.
    
    **Returns:**
    - **200**: Summary including total items, limits, completion rates
    """
    try:
        summary = await item_service.get_items_summary(quotation_id)
        
        return create_response(
            data=summary,
            message="Items summary retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving items summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve items summary"
        )


@router.get("/{item_id}",
            response_model=QuotationItemResponse,
            summary="Get quotation item by ID",
            description="Retrieve a specific coverage item")
@handle_exceptions
async def get_quotation_item(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    item_id: UUID = Path(..., description="Item ID"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Get a specific coverage item by ID.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **item_id**: UUID of the item
    
    **Returns:**
    - **200**: Coverage item details
    - **404**: Item not found
    """
    try:
        item = await item_service.get_item(item_id)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coverage item not found"
            )
        
        # Verify item belongs to the specified quotation
        if str(item.quotation_id) != str(quotation_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coverage item not found in this quotation"
            )
        
        return create_response(
            data=item,
            message="Coverage item retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quotation item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve coverage item"
        )


# ========== UPDATE ENDPOINTS ==========

@router.put("/{item_id}",
            response_model=QuotationItemResponse,
            summary="Update quotation item",
            description="Update coverage item details")
@handle_exceptions
async def update_quotation_item(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    item_id: UUID = Path(..., description="Item ID"),
    item_data: QuotationItemUpdate = Body(...),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Update coverage item details.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **item_id**: UUID of the item to update
    - **item_data**: Updated item data
    
    **Returns:**
    - **200**: Updated coverage item
    - **404**: Item not found
    - **409**: Quotation locked or validation error
    """
    try:
        updated_item = await item_service.update_item(
            item_id=item_id,
            item_data=item_data,
            updated_by=current_user.id
        )
        
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coverage item not found"
            )
        
        return create_response(
            data=updated_item,
            message="Coverage item updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating quotation item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update coverage item"
        )


@router.patch("/{item_id}/display-order",
              response_model=QuotationItemResponse,
              summary="Update item display order",
              description="Update the display order of a coverage item")
@handle_exceptions
async def update_item_display_order(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    item_id: UUID = Path(..., description="Item ID"),
    order_data: Dict[str, int] = Body(..., description="Order data with new_order value"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Update the display order of a coverage item.
    
    **Request Body:**
    ```json
    {
        "new_order": 3
    }
    ```
    
    **Returns:**
    - **200**: Item with updated display order
    - **400**: Invalid order value
    - **404**: Item not found
    """
    try:
        new_order = order_data.get("new_order")
        if new_order is None or new_order < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="new_order must be a positive integer"
            )
        
        updated_item = await item_service.update_display_order(
            item_id=item_id,
            new_order=new_order,
            updated_by=current_user.id
        )
        
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coverage item not found"
            )
        
        return create_response(
            data=updated_item,
            message=f"Display order updated to {new_order}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating display order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update display order"
        )


@router.patch("/reorder",
              response_model=List[QuotationItemResponse],
              summary="Reorder multiple items",
              description="Update display order for multiple items at once")
@handle_exceptions
async def reorder_quotation_items(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    reorder_data: Dict[str, Dict[str, int]] = Body(..., description="Reorder data with item_orders"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Reorder multiple coverage items at once.
    
    **Request Body:**
    ```json
    {
        "item_orders": {
            "item_id_1": 1,
            "item_id_2": 2,
            "item_id_3": 3
        }
    }
    ```
    
    **Returns:**
    - **200**: List of reordered items
    - **400**: Invalid order values or duplicate orders
    """
    try:
        item_orders_str = reorder_data.get("item_orders", {})
        
        # Convert string UUIDs to UUID objects
        item_orders = {}
        for item_id_str, order in item_orders_str.items():
            try:
                item_orders[UUID(item_id_str)] = order
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid UUID format: {item_id_str}"
                )
        
        updated_items = await item_service.reorder_items(
            quotation_id=quotation_id,
            item_orders=item_orders,
            updated_by=current_user.id
        )
        
        return create_response(
            data=updated_items,
            message=f"Reordered {len(updated_items)} items successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder items"
        )


@router.patch("/{item_id}/coverage-names",
              response_model=QuotationItemResponse,
              summary="Update coverage names",
              description="Update coverage names in multiple languages")
@handle_exceptions
async def update_coverage_names(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    item_id: UUID = Path(..., description="Item ID"),
    names_data: Dict[str, Optional[str]] = Body(..., description="Coverage names data"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Update coverage names in multiple languages.
    
    **Request Body:**
    ```json
    {
        "coverage_name": "Comprehensive Motor Insurance",
        "coverage_name_ar": "تأمين شامل للسيارات"
    }
    ```
    
    **Returns:**
    - **200**: Item with updated coverage names
    """
    try:
        updated_item = await item_service.update_coverage_names(
            item_id=item_id,
            coverage_name=names_data.get("coverage_name"),
            coverage_name_ar=names_data.get("coverage_name_ar"),
            updated_by=current_user.id
        )
        
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coverage item not found"
            )
        
        return create_response(
            data=updated_item,
            message="Coverage names updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating coverage names: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update coverage names"
        )


@router.patch("/{item_id}/metadata",
              response_model=QuotationItemResponse,
              summary="Update item metadata",
              description="Update item metadata with flexible JSON structure")
@handle_exceptions
async def update_item_metadata(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    item_id: UUID = Path(..., description="Item ID"),
    metadata_update: QuotationItemMetadataUpdate = Body(...),
    merge: bool = Query(True, description="Merge with existing metadata or replace"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Update item metadata.
    
    **Parameters:**
    - **merge**: Whether to merge with existing metadata (true) or replace entirely (false)
    
    **Request Body:**
    ```json
    {
        "meta_data": {
            "category": "motor",
            "sub_category": "comprehensive",
            "risk_level": "medium",
            "custom_fields": {
                "vehicle_type": "sedan",
                "coverage_period": "annual"
            }
        }
    }
    ```
    """
    try:
        updated_item = await item_service.update_metadata(
            item_id=item_id,
            metadata=metadata_update.meta_data,
            merge=merge,
            updated_by=current_user.id
        )
        
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coverage item not found"
            )
        
        return create_response(
            data=updated_item,
            message="Metadata updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating metadata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update metadata"
        )


# ========== DELETE ENDPOINTS ==========

@router.delete("/{item_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete quotation item",
               description="Soft delete a coverage item")
@handle_exceptions
async def delete_quotation_item(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    item_id: UUID = Path(..., description="Item ID"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Soft delete a coverage item.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **item_id**: UUID of the item to delete
    
    **Returns:**
    - **204**: Item deleted successfully
    - **404**: Item not found
    - **409**: Cannot delete (last item, quotation locked, etc.)
    """
    try:
        success = await item_service.delete_item(
            item_id=item_id,
            deleted_by=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coverage item not found"
            )
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting quotation item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete coverage item"
        )


# ========== UTILITY ENDPOINTS ==========

@router.post("/duplicate-from/{source_quotation_id}",
             response_model=List[QuotationItemResponse],
             status_code=status.HTTP_201_CREATED,
             summary="Duplicate items from another quotation",
             description="Copy all items from another quotation")
@handle_exceptions
async def duplicate_items_from_quotation(
    quotation_id: UUID = Path(..., description="Target quotation ID"),
    source_quotation_id: UUID = Path(..., description="Source quotation ID"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Duplicate all items from another quotation.
    
    **Parameters:**
    - **quotation_id**: Target quotation where items will be copied
    - **source_quotation_id**: Source quotation to copy items from
    
    **Returns:**
    - **201**: List of duplicated items
    - **404**: Source or target quotation not found
    """
    try:
        duplicated_items = await item_service.duplicate_items_to_quotation(
            source_quotation_id=source_quotation_id,
            target_quotation_id=quotation_id,
            created_by=current_user.id
        )
        
        return create_response(
            data=duplicated_items,
            message=f"Duplicated {len(duplicated_items)} items successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error duplicating items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate items"
        )


@router.post("/validate-orders",
             response_model=Dict[str, Any],
             summary="Validate display orders",
             description="Validate display order integrity for items")
@handle_exceptions
async def validate_display_orders(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Validate display order integrity.
    
    **Returns:**
    - **200**: Validation results with any issues found
    """
    try:
        validation_result = await item_service.validate_display_orders(quotation_id)
        
        return create_response(
            data=validation_result,
            message="Display order validation completed"
        )
        
    except Exception as e:
        logger.error(f"Error validating display orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate display orders"
        )


@router.post("/fix-orders",
             response_model=List[QuotationItemResponse],
             summary="Fix display orders",
             description="Fix display order issues by compacting orders")
@handle_exceptions
async def fix_display_orders(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    current_user = Depends(get_current_user),
    item_service: QuotationItemService = Depends(get_quotation_item_service)
):
    """
    Fix display order issues by reassigning sequential orders.
    
    **Returns:**
    - **200**: List of items with corrected display orders
    """
    try:
        fixed_items = await item_service.fix_display_orders(
            quotation_id=quotation_id,
            updated_by=current_user.id
        )
        
        return create_response(
            data=fixed_items,
            message=f"Fixed display orders for {len(fixed_items)} items"
        )
        
    except Exception as e:
        logger.error(f"Error fixing display orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fix display orders"
        )