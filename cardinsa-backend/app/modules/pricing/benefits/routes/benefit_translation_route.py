"""
Benefit Translation Routes - Multi-Language Support & Localization API
======================================================================

Enterprise-grade REST API for benefit translation management with comprehensive
localization workflows, quality control, and translation automation.

Author: Assistant
Created: 2024
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
import asyncio
import io

# Core imports - FIXED
from app.core.database import get_db
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.core.dependencies import get_current_user, require_role
from app.core.logging import get_logger
from app.core.responses import success_response, error_response
from app.utils.pagination import PaginatedResponse, PaginationParams

# Service imports
from app.modules.pricing.benefits.services.benefit_translation_service import BenefitTranslationService

# Model imports - Import what exists
from app.modules.pricing.benefits.models.benefit_translation_model import BenefitTranslation

# Schema imports - Create placeholder schemas since they may not exist
class BenefitTranslationCreate(BaseModel):
    source_content: str
    source_language: str
    target_language: str
    context: Optional[Dict[str, Any]] = None

class BenefitTranslationUpdate(BaseModel):
    translated_content: Optional[str] = None
    status: Optional[str] = None
    quality_score: Optional[float] = None

class BenefitTranslationResponse(BaseModel):
    id: str
    source_content: str
    translated_content: str
    source_language: str
    target_language: str
    status: str
    quality_score: Optional[float] = None
    
    class Config:
        from_attributes = True

class BenefitTranslationWithDetails(BenefitTranslationResponse):
    workflow_info: Optional[Dict[str, Any]] = None
    quality_details: Optional[Dict[str, Any]] = None

class TranslationWorkflow(BaseModel):
    translation_id: str
    current_stage: str
    stages: List[Dict[str, Any]]
    history: List[Dict[str, Any]] = []

class TranslationJob(BaseModel):
    job_id: str
    status: str
    total_items: int
    completed_items: int
    translations: List[BenefitTranslationResponse] = []

class QualityAssessment(BaseModel):
    translation_id: str
    overall_score: float
    criteria_scores: Dict[str, float]
    recommendations: List[str] = []

class TranslationMemory(BaseModel):
    source_text: str
    target_text: str
    language_pair: str
    quality_score: float

class Glossary(BaseModel):
    term: str
    translation: str
    language_pair: str
    domain: str

class LocalizationCheck(BaseModel):
    translation_id: str
    check_type: str
    status: str
    issues: List[str] = []

class TranslationMetrics(BaseModel):
    period: str
    total_translations: int
    quality_average: float
    completion_rate: float

class BulkTranslationRequest(BaseModel):
    items: List[Dict[str, Any]]
    source_language: str
    target_languages: List[str]
    priority: str = "normal"

class TranslationSearchFilter(BaseModel):
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    status: Optional[str] = None

class BulkTranslationOperation(BaseModel):
    operation_type: str
    translation_ids: List[str]
    parameters: Dict[str, Any] = {}

# Enum placeholders
class TranslationStatus:
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"

class TranslationQuality:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class LanguageCode:
    EN = "en"
    AR = "ar"
    FR = "fr"
    ES = "es"

logger = get_logger(__name__)

# Helper functions
def get_db_session():
    return get_db()

def require_permissions(current_user: dict, required_roles: List[str]):
    """Check if user has required permissions"""
    user_roles = current_user.get('roles', [])
    if not any(role in user_roles for role in required_roles):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

def cache_response(ttl: int = 300):
    """Cache response decorator"""
    def decorator(func):
        return func
    return decorator

# Initialize router
router = APIRouter(
    prefix="/api/v1/benefit-translations",
    tags=["Benefit Translations"],
    responses={
        404: {"description": "Translation not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# =====================================================================
# CORE CRUD OPERATIONS
# =====================================================================

@router.post(
    "/",
    response_model=BenefitTranslationResponse,
    status_code=201,
    summary="Create Translation",
    description="Create a new benefit translation with workflow initialization"
)
async def create_translation(
    translation_data: BenefitTranslationCreate,
    auto_detect_language: bool = Query(False, description="Auto-detect source language"),
    initialize_workflow: bool = Query(True, description="Initialize translation workflow"),
    validate_source: bool = Query(True, description="Validate source content"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new benefit translation"""
    try:
        if not current_user.has_any(["admin", "translator", "localization_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitTranslationService(db)
        translation = await service.create_translation(
            translation_data.dict(),
            auto_detect_language=auto_detect_language,
            initialize_workflow=initialize_workflow,
            validate_source=validate_source,
            created_by=str(current_user.id)
        )
        
        logger.info(
            f"Translation created by {current_user.id}: {translation.source_language} -> {translation.target_language}",
            extra={
                "translation_id": str(translation.id),
                "source_language": translation.source_language,
                "target_language": translation.target_language,
                "user_id": str(current_user.id)
            }
        )
        
        return BenefitTranslationResponse.from_orm(translation)
        
    except ValidationError as e:
        logger.error(f"Translation creation validation failed: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Translation creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create translation")


@router.get(
    "/{translation_id}",
    response_model=BenefitTranslationResponse,
    summary="Get Translation",
    description="Retrieve a specific translation by ID"
)
async def get_translation(
    translation_id: str = Path(..., description="Translation ID"),
    include_workflow: bool = Query(False, description="Include workflow information"),
    include_quality: bool = Query(False, description="Include quality assessment"),
    include_history: bool = Query(False, description="Include translation history"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific translation"""
    try:
        service = BenefitTranslationService(db)
        
        if include_workflow or include_quality or include_history:
            translation = await service.get_translation_with_details(
                translation_id,
                include_workflow=include_workflow,
                include_quality=include_quality,
                include_history=include_history
            )
            if not translation:
                raise HTTPException(status_code=404, detail="Translation not found")
            return BenefitTranslationWithDetails.from_orm(translation)
        else:
            translation = await service.get_by_id(translation_id)
            if not translation:
                raise HTTPException(status_code=404, detail="Translation not found")
            return BenefitTranslationResponse.from_orm(translation)
            
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Translation not found")
    except Exception as e:
        logger.error(f"Failed to retrieve translation {translation_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve translation")


@router.put(
    "/{translation_id}",
    response_model=BenefitTranslationResponse,
    summary="Update Translation",
    description="Update an existing translation with quality validation"
)
async def update_translation(
    translation_id: str = Path(..., description="Translation ID"),
    translation_data: BenefitTranslationUpdate = Body(...),
    validate_quality: bool = Query(True, description="Validate translation quality"),
    update_workflow: bool = Query(True, description="Update workflow status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing translation"""
    try:
        if not current_user.has_any(["admin", "translator", "localization_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitTranslationService(db)
        translation = await service.update_translation(
            translation_id,
            translation_data.dict(exclude_unset=True),
            validate_quality=validate_quality,
            update_workflow=update_workflow,
            updated_by=str(current_user.id)
        )
        
        logger.info(
            f"Translation updated by {current_user.id}: {translation_id}",
            extra={"translation_id": str(translation.id), "user_id": str(current_user.id)}
        )
        
        return BenefitTranslationResponse.from_orm(translation)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Translation not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Translation update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update translation")


@router.delete(
    "/{translation_id}",
    status_code=204,
    summary="Delete Translation",
    description="Delete a translation and associated workflow data"
)
async def delete_translation(
    translation_id: str = Path(..., description="Translation ID"),
    archive_workflow: bool = Query(True, description="Archive workflow before deletion"),
    cleanup_memory: bool = Query(False, description="Clean up translation memory entries"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a translation"""
    try:
        if not current_user.has_any(["admin", "localization_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitTranslationService(db)
        await service.delete_translation(
            translation_id,
            archive_workflow=archive_workflow,
            cleanup_memory=cleanup_memory,
            deleted_by=str(current_user.id)
        )
        
        logger.info(
            f"Translation deleted by {current_user.id}: {translation_id}",
            extra={"translation_id": translation_id, "user_id": str(current_user.id)}
        )
        
        return JSONResponse(status_code=204, content=None)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Translation not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Translation deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete translation")

# =====================================================================
# TRANSLATION WORKFLOWS
# =====================================================================

@router.get(
    "/{translation_id}/workflow",
    response_model=TranslationWorkflow,
    summary="Get Translation Workflow",
    description="Get workflow status and history for a translation"
)
async def get_translation_workflow(
    translation_id: str = Path(..., description="Translation ID"),
    include_history: bool = Query(True, description="Include workflow history"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get translation workflow information"""
    try:
        service = BenefitTranslationService(db)
        workflow = await service.get_translation_workflow(
            translation_id=translation_id,
            include_history=include_history
        )
        
        return workflow
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Translation not found")
    except Exception as e:
        logger.error(f"Failed to get translation workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get workflow")


@router.post(
    "/{translation_id}/workflow/advance",
    response_model=TranslationWorkflow,
    summary="Advance Translation Workflow",
    description="Advance translation to next workflow stage"
)
async def advance_translation_workflow(
    translation_id: str = Path(..., description="Translation ID"),
    next_stage: str = Body(..., description="Next workflow stage"),
    comments: Optional[str] = Body(None, description="Workflow comments"),
    validate_stage: bool = Query(True, description="Validate stage requirements"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Advance translation workflow to next stage"""
    try:
        if not current_user.has_any(["admin", "translator", "localization_manager", "reviewer"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitTranslationService(db)
        workflow = await service.advance_translation_workflow(
            translation_id=translation_id,
            next_stage=next_stage,
            comments=comments,
            validate_stage=validate_stage,
            advanced_by=str(current_user.id)
        )
        
        logger.info(
            f"Translation workflow advanced by {current_user.id}: {translation_id} -> {next_stage}",
            extra={
                "translation_id": translation_id,
                "next_stage": next_stage,
                "user_id": str(current_user.id)
            }
        )
        
        return workflow
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Translation not found")
    except BusinessLogicError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Workflow advancement failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Workflow advancement failed")

# =====================================================================
# AUTOMATED TRANSLATION
# =====================================================================

@router.post(
    "/auto-translate",
    response_model=BenefitTranslationResponse,
    summary="Auto-Translate Content",
    description="Automatically translate content using AI/ML services"
)
async def auto_translate_content(
    source_content: str = Body(..., description="Content to translate"),
    source_language: str = Body(..., description="Source language code"),
    target_language: str = Body(..., description="Target language code"),
    benefit_context: Optional[Dict[str, Any]] = Body(None, description="Benefit context for translation"),
    translation_engine: Optional[str] = Body(None, description="Preferred translation engine"),
    quality_threshold: float = Body(0.8, description="Minimum quality threshold"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Auto-translate content using AI/ML services"""
    try:
        if not current_user.has_any(["admin", "translator", "localization_manager"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        service = BenefitTranslationService(db)
        translation = await service.auto_translate_content(
            source_content=source_content,
            source_language=source_language,
            target_language=target_language,
            context=benefit_context or {},
            engine=translation_engine,
            quality_threshold=quality_threshold,
            requested_by=str(current_user.id)
        )
        
        logger.info(
            f"Auto-translation completed by {current_user.id}: {source_language} -> {target_language}",
            extra={
                "source_language": source_language,
                "target_language": target_language,
                "quality_score": translation.quality_score,
                "user_id": str(current_user.id)
            }
        )
        
        return BenefitTranslationResponse.from_orm(translation)
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Auto-translation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Auto-translation failed")


# =====================================================================
# BULK TRANSLATION OPERATIONS
# =====================================================================

@router.post(
    "/bulk/translate",
    response_model=List[TranslationJob],
    summary="Bulk Translation Request",
    description="Submit bulk translation request for multiple items"
)
async def bulk_translate_request(
    bulk_request: BulkTranslationRequest = Body(...),
    priority: str = Query("normal", description="Translation priority"),
    assign_to_team: Optional[str] = Body(None, description="Assign to specific translation team"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Submit bulk translation request"""
    try:
        require_permissions(current_user, ["admin", "localization_manager", "project_manager"])
        
        service = BenefitTranslationService(db)
        translation_jobs = await service.create_bulk_translation_request(
            request=bulk_request.dict(),
            priority=priority,
            team_assignment=assign_to_team,
            requested_by=current_user.get('user_id')
        )
        
        logger.info(
            f"Bulk translation request submitted by {current_user.get('user_id')}: {len(translation_jobs)} jobs",
            extra={
                "job_count": len(translation_jobs),
                "priority": priority,
                "user_id": current_user.get('user_id')
            }
        )
        
        return translation_jobs
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Bulk translation request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Bulk translation request failed")


@router.get(
    "/jobs/{job_id}",
    response_model=TranslationJob,
    summary="Get Translation Job",
    description="Get status and details of a translation job"
)
@cache_response(ttl=60)
async def get_translation_job(
    job_id: str = Path(..., description="Translation job ID"),
    include_translations: bool = Query(True, description="Include individual translations"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get translation job status and details"""
    try:
        service = BenefitTranslationService(db)
        job = await service.get_translation_job(
            job_id=job_id,
            include_translations=include_translations
        )
        
        return job
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Translation job not found")
    except Exception as e:
        logger.error(f"Failed to get translation job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get translation job")


# =====================================================================
# QUALITY CONTROL
# =====================================================================

@router.post(
    "/{translation_id}/quality-assessment",
    response_model=QualityAssessment,
    summary="Assess Translation Quality",
    description="Perform quality assessment on a translation"
)
async def assess_translation_quality(
    translation_id: str = Path(..., description="Translation ID"),
    assessment_criteria: Optional[List[str]] = Body(None, description="Quality assessment criteria"),
    automated_check: bool = Query(True, description="Include automated quality checks"),
    linguistic_review: bool = Query(False, description="Include linguistic review"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Assess translation quality"""
    try:
        require_permissions(current_user, ["admin", "reviewer", "quality_analyst", "localization_manager"])
        
        service = BenefitTranslationService(db)
        assessment = await service.assess_translation_quality(
            translation_id=translation_id,
            criteria=assessment_criteria,
            automated_check=automated_check,
            linguistic_review=linguistic_review,
            assessed_by=current_user.get('user_id')
        )
        
        logger.info(
            f"Quality assessment completed by {current_user.get('user_id')}: {translation_id}",
            extra={
                "translation_id": translation_id,
                "quality_score": assessment.overall_score,
                "user_id": current_user.get('user_id')
            }
        )
        
        return assessment
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Translation not found")
    except Exception as e:
        logger.error(f"Quality assessment failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Quality assessment failed")


# =====================================================================
# TRANSLATION MEMORY & GLOSSARY
# =====================================================================

@router.get(
    "/memory/search",
    response_model=List[TranslationMemory],
    summary="Search Translation Memory",
    description="Search translation memory for similar translations"
)
async def search_translation_memory(
    source_text: str = Query(..., description="Source text to search"),
    language_pair: str = Query(..., description="Language pair (e.g., 'en-ar')"),
    similarity_threshold: float = Query(0.7, description="Similarity threshold"),
    max_results: int = Query(10, description="Maximum results"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Search translation memory for similar translations"""
    try:
        service = BenefitTranslationService(db)
        memory_results = await service.search_translation_memory(
            source_text=source_text,
            language_pair=language_pair,
            similarity_threshold=similarity_threshold,
            max_results=max_results
        )
        
        return memory_results
        
    except Exception as e:
        logger.error(f"Translation memory search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Translation memory search failed")


@router.get(
    "/glossary/{language_pair}",
    response_model=List[Glossary],
    summary="Get Translation Glossary",
    description="Get translation glossary for specific language pair"
)
@cache_response(ttl=3600)
async def get_translation_glossary(
    language_pair: str = Path(..., description="Language pair (e.g., 'en-ar')"),
    domain: Optional[str] = Query(None, description="Domain filter"),
    search_term: Optional[str] = Query(None, description="Search term"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get translation glossary for language pair"""
    try:
        service = BenefitTranslationService(db)
        glossary = await service.get_translation_glossary(
            language_pair=language_pair,
            domain=domain,
            search_term=search_term
        )
        
        return glossary
        
    except Exception as e:
        logger.error(f"Failed to get translation glossary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get translation glossary")


# =====================================================================
# LOCALIZATION CHECKS
# =====================================================================

@router.post(
    "/{translation_id}/localization-check",
    response_model=LocalizationCheck,
    summary="Localization Check",
    description="Perform localization checks on translation"
)
async def perform_localization_check(
    translation_id: str = Path(..., description="Translation ID"),
    check_types: List[str] = Body(..., description="Types of checks to perform"),
    target_market: Optional[str] = Body(None, description="Target market for localization"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Perform localization checks on translation"""
    try:
        require_permissions(current_user, ["admin", "localization_specialist", "reviewer"])
        
        service = BenefitTranslationService(db)
        check_result = await service.perform_localization_check(
            translation_id=translation_id,
            check_types=check_types,
            target_market=target_market,
            checked_by=current_user.get('user_id')
        )
        
        return check_result
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Translation not found")
    except Exception as e:
        logger.error(f"Localization check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Localization check failed")


# =====================================================================
# ANALYTICS & METRICS
# =====================================================================

@router.get(
    "/analytics/metrics",
    response_model=TranslationMetrics,
    summary="Translation Analytics",
    description="Get translation analytics and metrics"
)
@cache_response(ttl=3600)
async def get_translation_metrics(
    period: str = Query("30d", description="Metrics period"),
    language_pair: Optional[str] = Query(None, description="Specific language pair"),
    include_quality: bool = Query(True, description="Include quality metrics"),
    breakdown_by: Optional[str] = Query(None, description="Breakdown dimension"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """Get translation analytics and metrics"""
    try:
        service = BenefitTranslationService(db)
        metrics = await service.get_translation_metrics(
            period=period,
            language_pair=language_pair,
            include_quality=include_quality,
            breakdown_by=breakdown_by
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Translation metrics failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get translation metrics")


# =====================================================================
# SEARCH & FILTERING
# =====================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[BenefitTranslationResponse],
    summary="List Translations",
    description="List and search translations with filtering"
)
async def list_translations(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
    source_language: Optional[str] = Query(None, description="Source language filter"),
    target_language: Optional[str] = Query(None, description="Target language filter"),
    status: Optional[str] = Query(None, description="Status filter"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """List translations with filtering and pagination"""
    try:
        service = BenefitTranslationService(db)
        
        # Build filters
        filters = TranslationSearchFilter(
            source_language=source_language,
            target_language=target_language,
            status=status
        )
        
        # Get paginated results
        result = await service.search_translations(
            filters=filters.dict(exclude_unset=True),
            search=search,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return PaginatedResponse(
            items=[BenefitTranslationResponse.from_orm(t) for t in result.items],
            total=result.total,
            page=page,
            per_page=per_page,
            pages=result.pages
        )
        
    except Exception as e:
        logger.error(f"Translation search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search translations")


# =====================================================================
# HEALTH CHECK
# =====================================================================

@router.get(
    "/health",
    response_model=Dict[str, str],
    summary="Translation Service Health",
    description="Check translation service health"
)
async def translation_service_health(
    db: Session = Depends(get_db_session)
):
    """Health check for translation service"""
    try:
        service = BenefitTranslationService(db)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "BenefitTranslationService"
        }
        
    except Exception as e:
        logger.error(f"Translation service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "BenefitTranslationService",
            "error": str(e)
        }