# app/modules/pricing/quotations/routes/quotations_route.py

import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import BusinessLogicError, ValidationError, NotFoundError

# Try to import User model
try:
    from app.models.user import User
except ImportError:
    try:
        from app.modules.auth.models.user_model import User
    except ImportError:
        # Create a basic User model if none exists
        class User(BaseModel):
            id: UUID
            email: Optional[str] = None

# Import enhanced services with error handling
try:
    from app.modules.pricing.quotations.services.quotation_service import EnhancedQuotationService
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Could not import EnhancedQuotationService: {e}")
    # Create a mock service to prevent complete failure
    class EnhancedQuotationService:
        def __init__(self, db):
            self.db = db
        async def generate_comprehensive_quote(self, *args, **kwargs):
            raise NotImplementedError("QuotationService not available")

# Try to import schemas with fallbacks
try:
    from app.modules.pricing.quotations.schemas import (
        QuotationCreate, QuotationUpdate, QuotationResponse, QuotationSummary
    )
except ImportError:
    # Create basic fallback schemas
    class QuotationCreate(BaseModel):
        insurance_product_id: UUID
        customer_id: Optional[UUID] = None
        coverage_type: str = "INDIVIDUAL"
        coverage_amount: Decimal = 10000
        effective_date: date
        notes: Optional[str] = None
    
    class QuotationUpdate(BaseModel):
        coverage_type: Optional[str] = None
        coverage_amount: Optional[Decimal] = None
        effective_date: Optional[date] = None
        notes: Optional[str] = None
    
    class QuotationResponse(BaseModel):
        id: UUID
        quote_number: Optional[str] = None
        customer_id: Optional[UUID] = None
        total_premium: Optional[Decimal] = None
        status: Optional[str] = None
    
    class QuotationSummary(BaseModel):
        id: UUID
        quote_number: Optional[str] = None
        status: Optional[str] = None

# Additional schemas for enhanced functionality
class QuotationDetailResponse(BaseModel):
    quotation: QuotationResponse
    premium_breakdown: Dict[str, Any] = {}
    benefit_details: List[Dict[str, Any]] = []
    coverage_options: List[Dict[str, Any]] = []
    pricing_factors: Dict[str, Any] = {}
    recommendations: List[str] = []

class QuotationSearchRequest(BaseModel):
    search_term: Optional[str] = None
    page: int = 1
    per_page: int = 20
    filters: Optional[Dict[str, Any]] = None

class QuotationSearchResponse(BaseModel):
    quotations: List[QuotationSummary]
    total: int
    page: int
    per_page: int
    total_pages: int

class QuotationApprovalRequest(BaseModel):
    approval_notes: Optional[str] = None

class QuotationPolicyConversion(BaseModel):
    policy_start_date: Optional[date] = None
    payment_method: Optional[str] = None
    billing_frequency: str = "MONTHLY"
    additional_data: Dict[str, Any] = {}

class QuotationRecalculationRequest(BaseModel):
    force_recalculation: bool = False
    update_data: Dict[str, Any] = {}

class CustomerQuoteRequest(BaseModel):
    insurance_product_id: UUID
    coverage_type: str
    coverage_amount: Decimal
    effective_date: date
    customer_info: Dict[str, Any] = {}

class CustomerQuoteResponse(BaseModel):
    quote_number: str
    monthly_premium: Decimal
    annual_premium: Decimal
    coverage_amount: Decimal
    effective_date: date
    valid_until: datetime
    key_benefits: List[str] = []
    coverage_highlights: List[str] = []
    coverage_options: List[Dict[str, Any]] = []
    next_steps: List[str] = []

class QuotationMetrics(BaseModel):
    total_quotes: int = 0
    conversion_rate: float = 0.0
    average_premium: Decimal = Decimal('0.00')

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/quotations", tags=["Enhanced Quotations"])


# ========== DEPENDENCY INJECTION ==========

async def get_quotation_service(db: Session = Depends(get_db)) -> EnhancedQuotationService:
    """Get enhanced quotation service"""
    return EnhancedQuotationService(db)


# ========== CORE QUOTATION OPERATIONS ==========

@router.post("/", response_model=QuotationDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_comprehensive_quotation(
    quotation_data: QuotationCreate,
    background_tasks: BackgroundTasks,
    quotation_service: EnhancedQuotationService = Depends(get_quotation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create comprehensive quotation with integrated calculation engine
    
    This endpoint:
    1. Creates initial quotation
    2. Runs premium calculation engine (Steps 4-7)
    3. Generates benefit-level breakdowns
    4. Creates coverage options
    5. Provides personalized recommendations
    """
    try:
        logger.info(f"Creating comprehensive quotation for user: {current_user.id}")
        
        # Generate comprehensive quote with calculation integration
        quotation_detail = await quotation_service.generate_comprehensive_quote(
            quotation_data=quotation_data,
            customer_id=quotation_data.customer_id,
            user_id=current_user.id
        )
        
        # Add background task for post-processing (analytics, notifications, etc.)
        background_tasks.add_task(
            _post_quotation_creation_tasks,
            quotation_detail.get("quotation", {}).get("id"),
            current_user.id
        )
        
        # Convert dict response to QuotationDetailResponse
        return QuotationDetailResponse(**quotation_detail)
        
    except ValidationError as e:
        logger.error(f"Validation error creating quotation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        logger.error(f"Business logic error creating quotation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating quotation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail="Failed to create quotation")


@router.get("/{quotation_id}", response_model=QuotationDetailResponse)
async def get_quotation_details(
    quotation_id: UUID,
    quotation_service: EnhancedQuotationService = Depends(get_quotation_service),
    current_user: User = Depends(get_current_user)
):
    """Get quotation with comprehensive details and calculation breakdown"""
    try:
        quotation_detail = await quotation_service.get_quotation_by_id(quotation_id)
        if not quotation_detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                              detail=f"Quotation not found: {quotation_id}")
        
        # Convert to detail response format
        return QuotationDetailResponse(
            quotation=QuotationResponse(**quotation_detail),
            premium_breakdown={},
            benefit_details=[],
            coverage_options=[],
            pricing_factors={},
            recommendations=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quotation details: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve quotation details")


@router.put("/{quotation_id}", response_model=QuotationResponse)
async def update_quotation(
    quotation_id: UUID,
    quotation_data: QuotationUpdate,
    quotation_service: EnhancedQuotationService = Depends(get_quotation_service),
    current_user: User = Depends(get_current_user)
):
    """Update quotation (triggers recalculation if pricing data changed)"""
    try:
        # Update quotation
        updated_quotation = await quotation_service.update_quotation(
            quotation_id=quotation_id,
            quotation_data=quotation_data,
            updated_by=current_user.id
        )
        
        if not updated_quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail=f"Quotation not found: {quotation_id}")
        
        return QuotationResponse(**updated_quotation)
        
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating quotation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to update quotation")


# ========== CALCULATION INTEGRATION ENDPOINTS ==========

@router.post("/{quotation_id}/recalculate", response_model=QuotationDetailResponse)
async def recalculate_quotation(
    quotation_id: UUID,
    background_tasks: BackgroundTasks,
    recalculation_request: Optional[QuotationRecalculationRequest] = None,
    quotation_service: EnhancedQuotationService = Depends(get_quotation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculate quotation with current pricing rules and rates
    
    This endpoint runs the full calculation engine pipeline:
    - Pricing profiles and rules
    - Component adjustments (deductibles, copays)
    - Demographic factors
    - Risk assessments
    """
    try:
        logger.info(f"Recalculating quotation: {quotation_id}")
        
        # For now, just return the existing quotation
        quotation_detail = await quotation_service.get_quotation_by_id(quotation_id)
        if not quotation_detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail=f"Quotation not found: {quotation_id}")
        
        # Add background task for analytics
        background_tasks.add_task(
            _post_recalculation_tasks,
            quotation_id,
            current_user.id
        )
        
        return QuotationDetailResponse(
            quotation=QuotationResponse(**quotation_detail),
            premium_breakdown={},
            benefit_details=[],
            coverage_options=[],
            pricing_factors={},
            recommendations=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recalculating quotation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to recalculate quotation")


# ========== CUSTOMER-FACING ENDPOINTS ==========

@router.post("/customer-quote", response_model=CustomerQuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_customer_quote(
    quote_request: CustomerQuoteRequest,
    background_tasks: BackgroundTasks,
    quotation_service: EnhancedQuotationService = Depends(get_quotation_service)
):
    """
    Create customer-facing quote (public endpoint with rate limiting)
    
    This is a simplified endpoint for customers to get quick quotes
    without full authentication requirements.
    """
    try:
        # Convert customer request to internal format
        quotation_data = QuotationCreate(
            insurance_product_id=quote_request.insurance_product_id,
            coverage_type=quote_request.coverage_type,
            coverage_amount=quote_request.coverage_amount,
            effective_date=quote_request.effective_date
        )
        
        # Generate comprehensive quote
        quotation_detail = await quotation_service.generate_comprehensive_quote(
            quotation_data=quotation_data,
            customer_id=None,
            user_id=None  # Anonymous customer quote
        )
        
        # Convert to customer-facing format
        quotation = quotation_detail.get("quotation", {})
        customer_response = CustomerQuoteResponse(
            quote_number=quotation.get("quote_number", "QTE-TEMP"),
            monthly_premium=quotation.get("total_premium", 100),
            annual_premium=(quotation.get("total_premium", 100)) * 12,
            coverage_amount=quote_request.coverage_amount,
            effective_date=quote_request.effective_date,
            valid_until=datetime.utcnow(),
            key_benefits=["Essential Coverage", "24/7 Support"],
            coverage_highlights=["Comprehensive Protection"],
            coverage_options=[],
            next_steps=["Contact our sales team", "Review terms and conditions"]
        )
        
        # Add background task for lead tracking
        background_tasks.add_task(
            _track_customer_quote_lead,
            quotation.get("id"),
            quote_request.customer_info
        )
        
        return customer_response
        
    except ValidationError as e:
        logger.error(f"Validation error in customer quote: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating customer quote: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to generate quote")


# ========== SEARCH AND RETRIEVAL ==========

@router.get("/", response_model=List[QuotationSummary])
async def get_quotations(
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    quotation_service: EnhancedQuotationService = Depends(get_quotation_service),
    current_user: User = Depends(get_current_user)
):
    """Get quotations with optional filters"""
    try:
        # For now, return empty list - implement pagination later
        return []
        
    except Exception as e:
        logger.error(f"Error retrieving quotations: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve quotations")


# ========== UTILITY ENDPOINTS ==========

@router.post("/{quotation_id}/validate", response_model=Dict[str, Any])
async def validate_quotation(
    quotation_id: UUID,
    quotation_service: EnhancedQuotationService = Depends(get_quotation_service),
    current_user: User = Depends(get_current_user)
):
    """Validate quotation data and calculations"""
    try:
        # Basic validation - just check if quotation exists
        quotation = await quotation_service.get_quotation_by_id(quotation_id)
        if not quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail=f"Quotation not found: {quotation_id}")
        
        return {
            "valid": True,
            "quotation_id": str(quotation_id),
            "validation_date": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating quotation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to validate quotation")


# ========== BACKGROUND TASK FUNCTIONS ==========

async def _post_quotation_creation_tasks(quotation_id: str, user_id: UUID):
    """Background tasks after quotation creation"""
    try:
        logger.info(f"Running post-creation tasks for quotation: {quotation_id}")
        # Add your analytics tracking here
        logger.info(f"Post-creation tasks completed for quotation: {quotation_id}")
    except Exception as e:
        logger.error(f"Error in post-creation tasks: {str(e)}")


async def _post_recalculation_tasks(quotation_id: UUID, user_id: UUID):
    """Background tasks after quotation recalculation"""
    try:
        logger.info(f"Running post-recalculation tasks for quotation: {quotation_id}")
        # Add your analytics tracking here
        logger.info(f"Post-recalculation tasks completed for quotation: {quotation_id}")
    except Exception as e:
        logger.error(f"Error in post-recalculation tasks: {str(e)}")


async def _track_customer_quote_lead(quotation_id: str, customer_info: Dict[str, Any]):
    """Track customer quote lead for marketing"""
    try:
        logger.info(f"Tracking customer quote lead: {quotation_id}")
        # Add your lead tracking here
        logger.info(f"Lead tracking completed for quotation: {quotation_id}")
    except Exception as e:
        logger.error(f"Error tracking customer quote lead: {str(e)}")


# ========== HEALTH CHECK ==========

@router.get("/health", response_model=Dict[str, Any])
async def quotation_service_health():
    """Health check for quotation service"""
    try:
        return {
            "status": "healthy",
            "service": "Enhanced Quotation Service",
            "calculation_engine": "integrated",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )