# app/modules/insurance/quotations/routes/quotations_route.py


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
from ..services import QuotationService
from ..schemas import (
    QuotationCreate, QuotationUpdate, QuotationResponse, QuotationSummary,
    QuotationStatusUpdate, QuotationCalculationRequest, QuotationStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quotations", tags=["quotations"])


# ========== DEPENDENCY INJECTION ==========

def get_quotation_service(db: Session = Depends(get_db)) -> QuotationService:
    """Get quotation service instance"""
    return QuotationService(db)


# ========== CREATE ENDPOINTS ==========

@router.post("/", 
             response_model=QuotationResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create a new quotation",
             description="Create a new insurance quotation with basic information")
@handle_exceptions
async def create_quotation(
    quotation_data: QuotationCreate,
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Create a new quotation.
    
    **Parameters:**
    - **quotation_data**: Quotation creation data including customer info and product details
    
    **Returns:**
    - **201**: Successfully created quotation
    - **400**: Validation error in request data
    - **409**: Conflict (duplicate quote number)
    - **422**: Business logic error
    """
    try:
        quotation = await quotation_service.create_quotation(
            quotation_data=quotation_data,
            created_by=current_user.id
        )
        
        return create_response(
            data=quotation,
            message="Quotation created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating quotation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quotation"
        )


@router.post("/with-items",
             response_model=QuotationResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create quotation with coverage items",
             description="Create a new quotation including coverage items in a single transaction")
@handle_exceptions
async def create_quotation_with_items(
    request_data: Dict[str, Any],  # Contains quotation_data and items_data
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Create a quotation with coverage items.
    
    **Request Body:**
    ```json
    {
        "quotation_data": {
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "product_code": "MOTOR_COMP"
        },
        "items_data": [
            {
                "coverage_name": "Third Party Liability",
                "limit_amount": 100000.00
            }
        ]
    }
    ```
    """
    try:
        quotation_data = QuotationCreate(**request_data.get("quotation_data", {}))
        items_data = request_data.get("items_data", [])
        
        quotation = await quotation_service.create_quotation_with_items(
            quotation_data=quotation_data,
            items_data=items_data,
            created_by=current_user.id
        )
        
        return create_response(
            data=quotation,
            message="Quotation with items created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating quotation with items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quotation with items"
        )


# ========== READ ENDPOINTS ==========

@router.get("/",
            response_model=Dict[str, Any],
            summary="Get paginated quotations",
            description="Retrieve quotations with pagination and filtering options")
@handle_exceptions
async def get_quotations(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[QuotationStatus] = Query(None, description="Filter by status"),
    customer_email: Optional[str] = Query(None, description="Filter by customer email"),
    product_code: Optional[str] = Query(None, description="Filter by product code"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by assigned user"),
    min_premium: Optional[float] = Query(None, ge=0, description="Minimum premium amount"),
    max_premium: Optional[float] = Query(None, ge=0, description="Maximum premium amount"),
    created_from: Optional[str] = Query(None, description="Filter from creation date (YYYY-MM-DD)"),
    created_to: Optional[str] = Query(None, description="Filter to creation date (YYYY-MM-DD)"),
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Get paginated list of quotations with optional filters.
    
    **Query Parameters:**
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 50, max: 100)
    - **status**: Filter by quotation status
    - **customer_email**: Filter by customer email (partial match)
    - **product_code**: Filter by product code
    - **assigned_to**: Filter by assigned user ID
    - **min_premium/max_premium**: Filter by premium range
    - **created_from/created_to**: Filter by creation date range
    
    **Returns:**
    - **200**: Paginated quotations list with metadata
    """
    try:
        # Build filters from query parameters
        filters = {}
        if status:
            filters['status'] = status.value
        if customer_email:
            filters['customer_email'] = customer_email
        if product_code:
            filters['product_code'] = product_code
        if assigned_to:
            filters['assigned_to'] = assigned_to
        if min_premium:
            filters['min_premium'] = min_premium
        if max_premium:
            filters['max_premium'] = max_premium
        if created_from:
            filters['created_from'] = created_from
        if created_to:
            filters['created_to'] = created_to
        
        quotations, total = await quotation_service.get_quotations_paginated(
            page=page,
            per_page=per_page,
            filters=filters
        )
        
        # Calculate pagination metadata
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return create_response(
            data={
                "quotations": quotations,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev
                },
                "filters_applied": filters
            },
            message=f"Retrieved {len(quotations)} quotations"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving quotations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quotations"
        )


@router.get("/{quotation_id}",
            response_model=QuotationResponse,
            summary="Get quotation by ID",
            description="Retrieve a specific quotation by its ID")
@handle_exceptions
async def get_quotation(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    load_relations: bool = Query(False, description="Load related data (items, factors, etc.)"),
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Get a specific quotation by ID.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **load_relations**: Whether to load related entities (items, factors, logs, etc.)
    
    **Returns:**
    - **200**: Quotation details
    - **404**: Quotation not found
    """
    try:
        quotation = await quotation_service.get_quotation(
            quotation_id=quotation_id,
            load_relations=load_relations
        )
        
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        return create_response(
            data=quotation,
            message="Quotation retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quotation {quotation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quotation"
        )


@router.get("/quote-number/{quote_number}",
            response_model=QuotationResponse,
            summary="Get quotation by quote number",
            description="Retrieve a quotation by its quote number")
@handle_exceptions
async def get_quotation_by_quote_number(
    quote_number: str = Path(..., description="Quote number"),
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Get quotation by quote number.
    
    **Parameters:**
    - **quote_number**: The quote number to search for
    
    **Returns:**
    - **200**: Quotation details
    - **404**: Quotation not found
    """
    try:
        quotation = await quotation_service.get_quotation_by_quote_number(quote_number)
        
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quotation with quote number '{quote_number}' not found"
            )
        
        return create_response(
            data=quotation,
            message="Quotation retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quotation by quote number {quote_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quotation"
        )


@router.get("/customer/{customer_identifier}",
            response_model=List[QuotationSummary],
            summary="Get quotations by customer",
            description="Retrieve all quotations for a specific customer")
@handle_exceptions
async def get_customer_quotations(
    customer_identifier: str = Path(..., description="Customer ID (UUID) or email address"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of quotations to return"),
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Get quotations for a customer by ID or email.
    
    **Parameters:**
    - **customer_identifier**: Customer UUID or email address
    - **limit**: Maximum number of quotations to return
    
    **Returns:**
    - **200**: List of customer quotations
    """
    try:
        # Try to parse as UUID first, fallback to email
        try:
            customer_id = UUID(customer_identifier)
            quotations = await quotation_service.get_customer_quotations(
                customer_id=customer_id,
                limit=limit
            )
        except ValueError:
            # Not a valid UUID, treat as email
            quotations = await quotation_service.get_customer_quotations(
                customer_email=customer_identifier,
                limit=limit
            )
        
        return create_response(
            data=quotations,
            message=f"Retrieved {len(quotations)} quotations for customer"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving customer quotations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer quotations"
        )


@router.get("/search/{search_term}",
            response_model=List[QuotationSummary],
            summary="Search quotations",
            description="Search quotations across multiple fields")
@handle_exceptions
async def search_quotations(
    search_term: str = Path(..., min_length=2, description="Search term (minimum 2 characters)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results to return"),
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Search quotations by quote number, customer name, email, phone, or national ID.
    
    **Parameters:**
    - **search_term**: Text to search for (searches across multiple fields)
    - **limit**: Maximum number of results
    
    **Returns:**
    - **200**: List of matching quotations
    """
    try:
        quotations = await quotation_service.search_quotations(
            search_term=search_term,
            limit=limit
        )
        
        return create_response(
            data=quotations,
            message=f"Found {len(quotations)} quotations matching '{search_term}'"
        )
        
    except Exception as e:
        logger.error(f"Error searching quotations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search quotations"
        )


# ========== UPDATE ENDPOINTS ==========

@router.put("/{quotation_id}",
            response_model=QuotationResponse,
            summary="Update quotation",
            description="Update quotation details")
@handle_exceptions
async def update_quotation(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    quotation_data: QuotationUpdate = ...,
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Update quotation details.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation to update
    - **quotation_data**: Updated quotation data
    
    **Returns:**
    - **200**: Updated quotation
    - **404**: Quotation not found
    - **409**: Quotation locked or in invalid state
    - **422**: Business validation error
    """
    try:
        updated_quotation = await quotation_service.update_quotation(
            quotation_id=quotation_id,
            quotation_data=quotation_data,
            updated_by=current_user.id
        )
        
        if not updated_quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        return create_response(
            data=updated_quotation,
            message="Quotation updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating quotation {quotation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update quotation"
        )


@router.patch("/{quotation_id}/status",
              response_model=QuotationResponse,
              summary="Update quotation status",
              description="Update the status of a quotation with workflow validation")
@handle_exceptions
async def update_quotation_status(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    status_update: QuotationStatusUpdate = ...,
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Update quotation status with workflow validation.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **status_update**: New status and optional notes
    
    **Returns:**
    - **200**: Quotation with updated status
    - **400**: Invalid status transition
    - **404**: Quotation not found
    - **409**: Business rule violation
    """
    try:
        updated_quotation = await quotation_service.update_status(
            quotation_id=quotation_id,
            status_update=status_update,
            updated_by=current_user.id
        )
        
        if not updated_quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        return create_response(
            data=updated_quotation,
            message=f"Quotation status updated to {status_update.status}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating quotation status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update quotation status"
        )


@router.post("/{quotation_id}/calculate",
             response_model=QuotationResponse,
             summary="Calculate quotation premium",
             description="Calculate premium for a quotation using all factors")
@handle_exceptions
async def calculate_quotation_premium(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    calculation_request: QuotationCalculationRequest = QuotationCalculationRequest(),
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Calculate quotation premium with all factors applied.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **calculation_request**: Calculation options and override factors
    
    **Returns:**
    - **200**: Quotation with calculated premium
    - **400**: Missing required data for calculation
    - **404**: Quotation not found
    """
    try:
        calculated_quotation = await quotation_service.calculate_premium(
            quotation_id=quotation_id,
            calculation_request=calculation_request,
            calculated_by=current_user.id
        )
        
        if not calculated_quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        return create_response(
            data=calculated_quotation,
            message="Premium calculated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating premium: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate premium"
        )


@router.post("/{quotation_id}/lock",
             response_model=QuotationResponse,
             summary="Lock quotation",
             description="Lock a quotation to prevent modifications")
@handle_exceptions
async def lock_quotation(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    lock_request: Dict[str, str]  = Body(..., description="Lock request with reason"),
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Lock quotation to prevent modifications.
    
    **Request Body:**
    ```json
    {
        "reason": "Under review by underwriter"
    }
    ```
    
    **Returns:**
    - **200**: Locked quotation
    - **404**: Quotation not found
    - **409**: Quotation already locked
    """
    try:
        lock_reason = lock_request.get("reason", "Locked by user")
        
        locked_quotation = await quotation_service.lock_quotation(
            quotation_id=quotation_id,
            lock_reason=lock_reason,
            locked_by=current_user.id
        )
        
        if not locked_quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        return create_response(
            data=locked_quotation,
            message="Quotation locked successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error locking quotation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to lock quotation"
        )


@router.post("/{quotation_id}/unlock",
             response_model=QuotationResponse,
             summary="Unlock quotation",
             description="Unlock a quotation to allow modifications")
@handle_exceptions
async def unlock_quotation(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Unlock quotation to allow modifications.
    
    **Returns:**
    - **200**: Unlocked quotation
    - **404**: Quotation not found
    - **409**: Quotation not locked
    """
    try:
        unlocked_quotation = await quotation_service.unlock_quotation(
            quotation_id=quotation_id,
            unlocked_by=current_user.id
        )
        
        if not unlocked_quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        return create_response(
            data=unlocked_quotation,
            message="Quotation unlocked successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlocking quotation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlock quotation"
        )


# ========== DELETE ENDPOINTS ==========

@router.delete("/{quotation_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete quotation",
               description="Soft delete a quotation (archive)")
@handle_exceptions
async def delete_quotation(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Soft delete (archive) a quotation.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation to delete
    
    **Returns:**
    - **204**: Quotation deleted successfully
    - **404**: Quotation not found
    - **409**: Cannot delete (converted quotation, etc.)
    """
    try:
        success = await quotation_service.delete_quotation(
            quotation_id=quotation_id,
            deleted_by=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting quotation {quotation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete quotation"
        )


# ========== ANALYTICS ENDPOINTS ==========

@router.get("/analytics/statistics",
            response_model=Dict[str, Any],
            summary="Get quotation statistics",
            description="Retrieve comprehensive quotation analytics and statistics")
@handle_exceptions
async def get_quotation_statistics(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user = Depends(get_current_user),
    quotation_service: QuotationService = Depends(get_quotation_service)
):
    """
    Get comprehensive quotation statistics and analytics.
    
    **Query Parameters:**
    - **date_from**: Start date for statistics (optional)
    - **date_to**: End date for statistics (optional)
    
    **Returns:**
    - **200**: Statistics including counts, conversion rates, premium analytics
    """
    try:
        from datetime import datetime
        
        parsed_date_from = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
        parsed_date_to = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None
        
        statistics = await quotation_service.get_quotation_statistics(
            date_from=parsed_date_from,
            date_to=parsed_date_to
        )
        
        return create_response(
            data=statistics,
            message="Statistics retrieved successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )