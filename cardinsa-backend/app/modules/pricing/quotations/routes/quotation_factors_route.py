# app/modules/insurance/quotations/routes/quotation_factors_route.py

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
import logging

from app.core.dependencies import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import handle_exceptions
from app.core.responses import create_response, create_error_response
from ..services import QuotationFactorService
from ..schemas import (
    QuotationFactorCreate, QuotationFactorUpdate, QuotationFactorResponse,
    QuotationFactorSummary, QuotationFactorBulkCreate, FactorType,
    QuotationFactorNumericRequest, QuotationFactorBooleanRequest,
    QuotationFactorComplexRequest, QuotationFactorsGrouped,
    QuotationFactorImpactAnalysis
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quotations/{quotation_id}/factors", tags=["quotation-factors"])


# ========== DEPENDENCY INJECTION ==========

def get_quotation_factor_service(db: Session = Depends(get_db)) -> QuotationFactorService:
    """Get quotation factor service instance"""
    return QuotationFactorService(db)


# ========== CREATE ENDPOINTS ==========

@router.post("/",
             response_model=QuotationFactorResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create quotation factor",
             description="Add a new pricing factor to a quotation")
@handle_exceptions
async def create_quotation_factor(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_data: QuotationFactorCreate = Body(...),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Create a new pricing factor for a quotation.
    
    **Parameters:**
    - **quotation_id**: UUID of the parent quotation
    - **factor_data**: Factor data including key, value, type, and impact description
    
    **Returns:**
    - **201**: Successfully created factor
    - **400**: Validation error
    - **404**: Quotation not found
    - **409**: Factor key already exists or quotation locked
    """
    try:
        # Ensure factor belongs to the specified quotation
        factor_data.quotation_id = quotation_id
        
        factor = await factor_service.create_factor(
            quotation_id=quotation_id,
            key=factor_data.key,
            value=factor_data.value,
            factor_type=factor_data.factor_type,
            impact_description=factor_data.impact_description,
            created_by=current_user.id
        )
        
        return create_response(
            data=factor,
            message="Pricing factor created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating quotation factor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create pricing factor"
        )


@router.post("/numeric",
             response_model=QuotationFactorResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create numeric factor",
             description="Create a numeric pricing factor with type validation")
@handle_exceptions
async def create_numeric_factor(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_request: QuotationFactorNumericRequest = Body(...),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Create a numeric pricing factor.
    
    **Request Body:**
    ```json
    {
        "key": "age_factor",
        "numeric_value": 1.25,
        "factor_type": "demographic",
        "impact_description": "25% loading for driver under 25"
    }
    ```
    """
    try:
        factor = await factor_service.create_numeric_factor(
            request=factor_request,
            quotation_id=quotation_id,
            created_by=current_user.id
        )
        
        return create_response(
            data=factor,
            message="Numeric factor created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating numeric factor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create numeric factor"
        )


@router.post("/boolean",
             response_model=QuotationFactorResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create boolean factor",
             description="Create a boolean pricing factor")
@handle_exceptions
async def create_boolean_factor(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_request: QuotationFactorBooleanRequest = Body(...),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Create a boolean pricing factor.
    
    **Request Body:**
    ```json
    {
        "key": "has_anti_theft",
        "boolean_value": true,
        "factor_type": "discount",
        "impact_description": "Anti-theft device installed"
    }
    ```
    """
    try:
        factor = await factor_service.create_boolean_factor(
            request=factor_request,
            quotation_id=quotation_id,
            created_by=current_user.id
        )
        
        return create_response(
            data=factor,
            message="Boolean factor created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating boolean factor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create boolean factor"
        )


@router.post("/complex",
             response_model=QuotationFactorResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create complex factor",
             description="Create a complex pricing factor with JSON value")
@handle_exceptions
async def create_complex_factor(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_request: QuotationFactorComplexRequest = Body(...),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Create a complex pricing factor with JSON value.
    
    **Request Body:**
    ```json
    {
        "key": "vehicle_modifications",
        "complex_value": {
            "engine_modifications": ["turbo", "exhaust"],
            "safety_features": ["abs", "airbags"],
            "modification_count": 2
        },
        "factor_type": "risk",
        "impact_description": "Vehicle has performance and safety modifications"
    }
    ```
    """
    try:
        factor = await factor_service.create_complex_factor(
            request=factor_request,
            quotation_id=quotation_id,
            created_by=current_user.id
        )
        
        return create_response(
            data=factor,
            message="Complex factor created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating complex factor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create complex factor"
        )


@router.post("/bulk",
             response_model=List[QuotationFactorResponse],
             status_code=status.HTTP_201_CREATED,
             summary="Create multiple factors",
             description="Create multiple pricing factors in bulk")
@handle_exceptions
async def create_bulk_factors(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    bulk_data: QuotationFactorBulkCreate = Body(...),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Create multiple pricing factors in bulk.
    
    **Request Body:**
    ```json
    {
        "quotation_id": "123e4567-e89b-12d3-a456-426614174000",
        "factors": [
            {
                "key": "age_factor",
                "value": "1.2",
                "factor_type": "demographic"
            },
            {
                "key": "location_risk",
                "value": "0.9",
                "factor_type": "geographic"
            }
        ]
    }
    ```
    """
    try:
        # Ensure all factors belong to the specified quotation
        bulk_data.quotation_id = quotation_id
        
        factors = await factor_service.create_bulk_factors(
            bulk_data=bulk_data,
            created_by=current_user.id
        )
        
        return create_response(
            data=factors,
            message=f"Created {len(factors)} pricing factors successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating bulk factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create pricing factors"
        )


# ========== READ ENDPOINTS ==========

@router.get("/",
            response_model=List[QuotationFactorResponse],
            summary="Get quotation factors",
            description="Retrieve all pricing factors for a quotation")
@handle_exceptions
async def get_quotation_factors(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    active_only: bool = Query(True, description="Include only active (non-archived) factors"),
    factor_type: Optional[FactorType] = Query(None, description="Filter by factor type"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Get all pricing factors for a quotation.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **active_only**: Whether to include only active factors (default: true)
    - **factor_type**: Filter by specific factor type (optional)
    
    **Returns:**
    - **200**: List of pricing factors
    """
    try:
        if factor_type:
            factors = await factor_service.get_factors_by_type(quotation_id, factor_type)
        else:
            factors = await factor_service.get_quotation_factors(quotation_id, active_only)
        
        return create_response(
            data=factors,
            message=f"Retrieved {len(factors)} pricing factors"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving quotation factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pricing factors"
        )


@router.get("/grouped",
            response_model=QuotationFactorsGrouped,
            summary="Get factors grouped by type",
            description="Retrieve factors organized by factor type")
@handle_exceptions
async def get_factors_grouped_by_type(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Get pricing factors grouped by type.
    
    **Returns:**
    - **200**: Factors organized by type with summary statistics
    """
    try:
        grouped_factors = await factor_service.get_factors_grouped_by_type(quotation_id)
        
        return create_response(
            data=grouped_factors,
            message="Factors grouped by type retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving grouped factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve grouped factors"
        )


@router.get("/numeric",
            response_model=List[QuotationFactorResponse],
            summary="Get numeric factors",
            description="Retrieve only numeric pricing factors")
@handle_exceptions
async def get_numeric_factors(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Get all numeric pricing factors for calculation purposes.
    
    **Returns:**
    - **200**: List of numeric factors with parsed values
    """
    try:
        factors = await factor_service.get_numeric_factors(quotation_id)
        
        return create_response(
            data=factors,
            message=f"Retrieved {len(factors)} numeric factors"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving numeric factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve numeric factors"
        )


@router.get("/search",
            response_model=List[QuotationFactorResponse],
            summary="Search factors",
            description="Search factors by key, value, or impact description")
@handle_exceptions
async def search_factors(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    search_term: str = Query(..., min_length=2, description="Search term (minimum 2 characters)"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Search pricing factors by key, value, or impact description.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **search_term**: Text to search for
    
    **Returns:**
    - **200**: List of matching factors
    """
    try:
        factors = await factor_service.search_factors(quotation_id, search_term)
        
        return create_response(
            data=factors,
            message=f"Found {len(factors)} factors matching '{search_term}'"
        )
        
    except Exception as e:
        logger.error(f"Error searching factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search factors"
        )


@router.get("/summary",
            response_model=Dict[str, Any],
            summary="Get factors summary",
            description="Get summary statistics for pricing factors")
@handle_exceptions
async def get_factors_summary(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Get summary statistics for pricing factors.
    
    **Returns:**
    - **200**: Summary including counts, types, business insights
    """
    try:
        summary = await factor_service.get_factors_summary(quotation_id)
        
        return create_response(
            data=summary,
            message="Factors summary retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving factors summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve factors summary"
        )


@router.get("/key/{factor_key}",
            response_model=QuotationFactorResponse,
            summary="Get factor by key",
            description="Retrieve a specific factor by its key")
@handle_exceptions
async def get_factor_by_key(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_key: str = Path(..., description="Factor key"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Get a specific factor by its key.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **factor_key**: The factor key to lookup
    
    **Returns:**
    - **200**: Factor details
    - **404**: Factor not found
    """
    try:
        factor = await factor_service.get_factor_by_key(quotation_id, factor_key)
        
        if not factor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factor with key '{factor_key}' not found"
            )
        
        return create_response(
            data=factor,
            message="Factor retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving factor by key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve factor"
        )


@router.get("/{factor_id}",
            response_model=QuotationFactorResponse,
            summary="Get factor by ID",
            description="Retrieve a specific factor by its ID")
@handle_exceptions
async def get_factor(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_id: UUID = Path(..., description="Factor ID"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Get a specific factor by ID.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **factor_id**: UUID of the factor
    
    **Returns:**
    - **200**: Factor details
    - **404**: Factor not found
    """
    try:
        factor = await factor_service.get_factor(factor_id)
        
        if not factor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing factor not found"
            )
        
        # Verify factor belongs to the specified quotation
        if str(factor.quotation_id) != str(quotation_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factor not found in this quotation"
            )
        
        return create_response(
            data=factor,
            message="Factor retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving factor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve factor"
        )


# ========== UPDATE ENDPOINTS ==========

@router.put("/{factor_id}",
            response_model=QuotationFactorResponse,
            summary="Update factor",
            description="Update pricing factor details")
@handle_exceptions
async def update_factor(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_id: UUID = Path(..., description="Factor ID"),
    factor_data: QuotationFactorUpdate = Body(...),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Update pricing factor details.
    
    **Parameters:**
    - **quotation_id**: UUID of the quotation
    - **factor_id**: UUID of the factor to update
    - **factor_data**: Updated factor data
    
    **Returns:**
    - **200**: Updated factor
    - **404**: Factor not found
    - **409**: Key conflict or quotation locked
    """
    try:
        updated_factor = await factor_service.update_factor(
            factor_id=factor_id,
            factor_data=factor_data,
            updated_by=current_user.id
        )
        
        if not updated_factor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing factor not found"
            )
        
        return create_response(
            data=updated_factor,
            message="Factor updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating factor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update factor"
        )


@router.patch("/{factor_id}/value",
              response_model=QuotationFactorResponse,
              summary="Update factor value",
              description="Update only the value of a pricing factor")
@handle_exceptions
async def update_factor_value(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_id: UUID = Path(..., description="Factor ID"),
    value_data: Dict[str, Any] = Body(..., description="Value update data"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Update factor value and optionally impact description.
    
    **Request Body:**
    ```json
    {
        "value": 1.35,
        "impact_description": "Updated loading factor"
    }
    ```
    
    **Returns:**
    - **200**: Factor with updated value
    """
    try:
        updated_factor = await factor_service.update_factor_value(
            factor_id=factor_id,
            value=value_data.get("value"),
            impact_description=value_data.get("impact_description"),
            updated_by=current_user.id
        )
        
        if not updated_factor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing factor not found"
            )
        
        return create_response(
            data=updated_factor,
            message="Factor value updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating factor value: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update factor value"
        )


@router.put("/upsert",
            response_model=QuotationFactorResponse,
            summary="Upsert factor",
            description="Insert or update factor by key")
@handle_exceptions
async def upsert_factor(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    upsert_data: Dict[str, Any] = Body(..., description="Upsert factor data"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Insert or update a factor by key.
    
    **Request Body:**
    ```json
    {
        "key": "age_factor",
        "value": 1.25,
        "factor_type": "demographic",
        "impact_description": "Age-based loading factor"
    }
    ```
    
    **Returns:**
    - **200**: Upserted factor
    """
    try:
        factor = await factor_service.upsert_factor(
            quotation_id=quotation_id,
            key=upsert_data.get("key"),
            value=upsert_data.get("value"),
            factor_type=upsert_data.get("factor_type"),
            impact_description=upsert_data.get("impact_description"),
            updated_by=current_user.id
        )
        
        return create_response(
            data=factor,
            message="Factor upserted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error upserting factor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upsert factor"
        )


@router.put("/bulk-upsert",
            response_model=List[QuotationFactorResponse],
            summary="Bulk upsert factors",
            description="Insert or update multiple factors by key")
@handle_exceptions
async def bulk_upsert_factors(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    upsert_data: Dict[str, Any] = Body(..., description="Bulk upsert data"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Bulk insert or update factors by key.
    
    **Request Body:**
    ```json
    {
        "factors": {
            "age_factor": 1.25,
            "location_factor": 0.9,
            "vehicle_type": "sedan"
        },
        "factor_type": "demographic"
    }
    ```
    
    **Returns:**
    - **200**: List of upserted factors
    """
    try:
        factors = await factor_service.bulk_upsert_factors(
            quotation_id=quotation_id,
            factors=upsert_data.get("factors", {}),
            factor_type=upsert_data.get("factor_type"),
            updated_by=current_user.id
        )
        
        return create_response(
            data=factors,
            message=f"Bulk upserted {len(factors)} factors successfully"
        )
        
    except Exception as e:
        logger.error(f"Error bulk upserting factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk upsert factors"
        )


# ========== DELETE ENDPOINTS ==========

@router.delete("/{factor_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete factor",
               description="Soft delete a pricing factor")
@handle_exceptions
async def delete_factor(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_id: UUID = Path(..., description="Factor ID"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Soft delete a pricing factor.
    
    **Returns:**
    - **204**: Factor deleted successfully
    - **404**: Factor not found
    - **409**: Cannot delete required factor or quotation locked
    """
    try:
        success = await factor_service.delete_factor(
            factor_id=factor_id,
            deleted_by=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing factor not found"
            )
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting factor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete factor"
        )


@router.delete("/key/{factor_key}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete factor by key",
               description="Delete a pricing factor by its key")
@handle_exceptions
async def delete_factor_by_key(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_key: str = Path(..., description="Factor key"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Delete a pricing factor by its key.
    
    **Returns:**
    - **204**: Factor deleted successfully
    - **404**: Factor not found
    """
    try:
        success = await factor_service.delete_factor_by_key(quotation_id, factor_key)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factor with key '{factor_key}' not found"
            )
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting factor by key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete factor"
        )


@router.delete("/type/{factor_type}",
               summary="Delete factors by type",
               description="Delete all factors of a specific type")
@handle_exceptions
async def delete_factors_by_type(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    factor_type: FactorType = Path(..., description="Factor type to delete"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Delete all factors of a specific type.
    
    **Returns:**
    - **200**: Number of factors deleted
    """
    try:
        deleted_count = await factor_service.delete_factors_by_type(
            quotation_id=quotation_id,
            factor_type=factor_type,
            deleted_by=current_user.id
        )
        
        return create_response(
            data={"deleted_count": deleted_count},
            message=f"Deleted {deleted_count} factors of type {factor_type}"
        )
        
    except Exception as e:
        logger.error(f"Error deleting factors by type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete factors by type"
        )


# ========== ANALYTICS ENDPOINTS ==========

@router.get("/impact-analysis",
            response_model=List[QuotationFactorImpactAnalysis],
            summary="Get factor impact analysis",
            description="Analyze the impact of all factors on pricing")
@handle_exceptions
async def get_factor_impact_analysis(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Get detailed impact analysis for all pricing factors.
    
    **Returns:**
    - **200**: List of factors with impact analysis
    """
    try:
        analysis = await factor_service.get_factor_impact_analysis(quotation_id)
        
        return create_response(
            data=analysis,
            message="Factor impact analysis completed"
        )
        
    except Exception as e:
        logger.error(f"Error analyzing factor impacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze factor impacts"
        )


@router.post("/validate",
             response_model=Dict[str, Any],
             summary="Validate factors",
             description="Validate all factors for business rules compliance")
@handle_exceptions
async def validate_factors(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Validate all factors for business rule compliance.
    
    **Returns:**
    - **200**: Validation results with errors, warnings, and suggestions
    """
    try:
        validation_result = await factor_service.validate_factors(quotation_id)
        
        return create_response(
            data=validation_result,
            message="Factor validation completed"
        )
        
    except Exception as e:
        logger.error(f"Error validating factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate factors"
        )


@router.post("/recalculate-impacts",
             response_model=List[Dict[str, Any]],
             summary="Recalculate factor impacts",
             description="Recalculate factor impacts based on base premium")
@handle_exceptions
async def recalculate_factor_impacts(
    quotation_id: UUID = Path(..., description="Quotation ID"),
    base_premium_data: Dict[str, float] = Body(..., description="Base premium data"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Recalculate factor impacts based on a base premium amount.
    
    **Request Body:**
    ```json
    {
        "base_premium": 1000.00
    }
    ```
    
    **Returns:**
    - **200**: List of factors with recalculated impacts
    """
    try:
        base_premium = base_premium_data.get("base_premium", 0.0)
        
        impacts = await factor_service.recalculate_factor_impacts(
            quotation_id=quotation_id,
            base_premium=base_premium
        )
        
        return create_response(
            data=impacts,
            message="Factor impacts recalculated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error recalculating impacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to recalculate factor impacts"
        )


# ========== UTILITY ENDPOINTS ==========

@router.post("/duplicate-from/{source_quotation_id}",
             response_model=List[QuotationFactorResponse],
             status_code=status.HTTP_201_CREATED,
             summary="Duplicate factors from another quotation",
             description="Copy all factors from another quotation")
@handle_exceptions
async def duplicate_factors_from_quotation(
    quotation_id: UUID = Path(..., description="Target quotation ID"),
    source_quotation_id: UUID = Path(..., description="Source quotation ID"),
    current_user = Depends(get_current_user),
    factor_service: QuotationFactorService = Depends(get_quotation_factor_service)
):
    """
    Duplicate all factors from another quotation.
    
    **Parameters:**
    - **quotation_id**: Target quotation where factors will be copied
    - **source_quotation_id**: Source quotation to copy factors from
    
    **Returns:**
    - **201**: List of duplicated factors
    - **404**: Source or target quotation not found
    """
    try:
        duplicated_factors = await factor_service.duplicate_factors_to_quotation(
            source_quotation_id=source_quotation_id,
            target_quotation_id=quotation_id,
            created_by=current_user.id
        )
        
        return create_response(
            data=duplicated_factors,
            message=f"Duplicated {len(duplicated_factors)} factors successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error duplicating factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate factors"
        )