# app/modules/benefits/schemas/benefit_translation_schema.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum


# =====================================================
# ENUMS FOR VALIDATION
# =====================================================

class EntityTypeEnum(str, Enum):
    """Enumeration of entity types that can be translated"""
    BENEFIT_CATEGORY = "BENEFIT_CATEGORY"
    BENEFIT_TYPE = "BENEFIT_TYPE"
    COVERAGE = "COVERAGE"
    COVERAGE_OPTION = "COVERAGE_OPTION"
    BENEFIT_LIMIT = "BENEFIT_LIMIT"
    CALCULATION_RULE = "CALCULATION_RULE"
    PLAN_SCHEDULE = "PLAN_SCHEDULE"
    BENEFIT_TERM = "BENEFIT_TERM"
    MEMBER_COMMUNICATION = "MEMBER_COMMUNICATION"
    PREAPPROVAL_RULE = "PREAPPROVAL_RULE"
    BENEFIT_CONDITION = "BENEFIT_CONDITION"


class TranslationStatusEnum(str, Enum):
    """Enumeration of translation status values"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"


class TranslationQualityEnum(str, Enum):
    """Enumeration of translation quality levels"""
    MACHINE = "MACHINE"
    HUMAN = "HUMAN"
    PROFESSIONAL = "PROFESSIONAL"
    CERTIFIED = "CERTIFIED"
    NATIVE_SPEAKER = "NATIVE_SPEAKER"


class TranslationSourceEnum(str, Enum):
    """Enumeration of translation sources"""
    MANUAL = "MANUAL"
    GOOGLE_TRANSLATE = "GOOGLE_TRANSLATE"
    AZURE_TRANSLATOR = "AZURE_TRANSLATOR"
    PROFESSIONAL_SERVICE = "PROFESSIONAL_SERVICE"
    INTERNAL_TEAM = "INTERNAL_TEAM"


class LanguageCode(str, Enum):
    """Enumeration of supported language codes (ISO 639-1)"""
    EN = "en"  # English
    AR = "ar"  # Arabic
    FR = "fr"  # French
    ES = "es"  # Spanish
    DE = "de"  # German
    IT = "it"  # Italian
    PT = "pt"  # Portuguese
    RU = "ru"  # Russian
    ZH = "zh"  # Chinese
    JA = "ja"  # Japanese
    KO = "ko"  # Korean
    HI = "hi"  # Hindi
    UR = "ur"  # Urdu
    FA = "fa"  # Persian/Farsi
    HE = "he"  # Hebrew


# =====================================================
# BASE SCHEMA
# =====================================================

class BenefitTranslationBase(BaseModel):
    """Base schema for benefit translation with common fields"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "entity_type": "BENEFIT_CATEGORY",
                "entity_id": "123e4567-e89b-12d3-a456-426614174000",
                "language_code": "ar",
                "language_name": "Arabic",
                "locale_code": "ar-SA",
                "translated_name": "الفوائد الطبية",
                "translated_description": "تغطية طبية شاملة تشمل جميع الخدمات الصحية",
                "member_friendly_name": "الفوائد الطبية الأساسية",
                "translation_quality": "PROFESSIONAL",
                "translation_source": "PROFESSIONAL_SERVICE"
            }
        }
    )
    
    # Entity reference
    entity_type: EntityTypeEnum = Field(
        ...,
        description="Type of entity being translated"
    )
    entity_id: UUID = Field(
        ...,
        description="ID of the entity being translated"
    )
    
    # Language information
    language_code: LanguageCode = Field(
        ...,
        description="ISO 639-1 language code"
    )
    language_name: str = Field(
        ...,
        max_length=50,
        description="Full language name"
    )
    locale_code: Optional[str] = Field(
        None,
        max_length=10,
        description="Full locale code (e.g., 'ar-SA', 'fr-CA')"
    )
    
    # Basic translated fields
    translated_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Translated name/title"
    )
    translated_description: Optional[str] = Field(
        None,
        description="Translated description"
    )
    translated_short_description: Optional[str] = Field(
        None,
        max_length=500,
        description="Translated short description"
    )
    
    # Additional translated content
    translated_summary: Optional[str] = Field(
        None,
        description="Translated summary"
    )
    translated_details: Optional[str] = Field(
        None,
        description="Translated detailed information"
    )
    translated_notes: Optional[str] = Field(
        None,
        description="Translated notes"
    )
    
    # Member-facing translations
    member_friendly_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Member-friendly translated name"
    )
    member_description: Optional[str] = Field(
        None,
        description="Member-friendly translated description"
    )
    member_summary: Optional[str] = Field(
        None,
        description="Member-friendly translated summary"
    )
    
    # Marketing and communication translations
    marketing_title: Optional[str] = Field(
        None,
        max_length=200,
        description="Marketing title translation"
    )
    marketing_description: Optional[str] = Field(
        None,
        description="Marketing description translation"
    )
    key_benefits: Optional[str] = Field(
        None,
        description="Translated key benefits"
    )
    
    # Translation quality and metadata
    translation_status: TranslationStatusEnum = Field(
        default=TranslationStatusEnum.PENDING,
        description="Current translation status"
    )
    translation_quality: Optional[TranslationQualityEnum] = Field(
        None,
        description="Quality level of translation"
    )
    translation_source: Optional[TranslationSourceEnum] = Field(
        None,
        description="Source of translation"
    )
    confidence_score: Optional[str] = Field(
        None,
        max_length=10,
        description="Confidence score for machine translations"
    )
    
    # Status and control
    is_active: bool = Field(
        default=True,
        description="Whether translation is currently active"
    )
    is_published: bool = Field(
        default=False,
        description="Whether translation is published"
    )
    is_default: bool = Field(
        default=False,
        description="Whether this is the default translation for the language"
    )
    
    # Effective periods
    effective_from: datetime = Field(
        default_factory=datetime.utcnow,
        description="When translation becomes effective"
    )
    effective_to: Optional[datetime] = Field(
        None,
        description="When translation expires"
    )

    @field_validator('language_code')
    @classmethod
    def validate_language_code(cls, v: LanguageCode) -> LanguageCode:
        """Validate language code format"""
        return v

    @field_validator('effective_to')
    @classmethod
    def validate_effective_to(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate effective_to is after effective_from"""
        if v and hasattr(info, 'data') and 'effective_from' in info.data:
            effective_from = info.data['effective_from']
            if v <= effective_from:
                raise ValueError('Effective to date must be after effective from date')
        return v


# =====================================================
# CREATE SCHEMA
# =====================================================

class BenefitTranslationCreate(BenefitTranslationBase):
    """Schema for creating a new benefit translation"""
    
    # Structured translations (JSON format for complex content)
    translated_fields: Optional[Dict[str, Any]] = Field(
        None,
        description="Complex structured translations"
    )
    
    # UI/UX translations
    ui_labels: Optional[Dict[str, Any]] = Field(
        None,
        description="User interface element translations"
    )
    
    # Form and validation translations
    form_labels: Optional[Dict[str, str]] = Field(
        None,
        description="Form field label translations"
    )
    validation_messages: Optional[Dict[str, str]] = Field(
        None,
        description="Validation message translations"
    )
    help_text: Optional[Dict[str, str]] = Field(
        None,
        description="Help text translations"
    )
    
    # Document-specific translations
    document_title: Optional[str] = Field(
        None,
        max_length=300,
        description="Document title translation"
    )
    document_subtitle: Optional[str] = Field(
        None,
        max_length=300,
        description="Document subtitle translation"
    )
    
    # Section headings and content
    section_translations: Optional[Dict[str, Dict[str, str]]] = Field(
        None,
        description="Section-wise translations"
    )
    
    # Legal and regulatory text
    legal_disclaimers: Optional[str] = Field(
        None,
        description="Legal disclaimer translations"
    )
    terms_and_conditions: Optional[str] = Field(
        None,
        description="Terms and conditions translations"
    )
    privacy_notices: Optional[str] = Field(
        None,
        description="Privacy notice translations"
    )
    
    # Cultural and regional adaptations
    cultural_adaptations: Optional[Dict[str, Any]] = Field(
        None,
        description="Cultural adaptation settings"
    )
    regional_variations: Optional[Dict[str, Any]] = Field(
        None,
        description="Regional variation settings"
    )
    
    # Usage context
    usage_context: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Usage context for translations"
    )
    
    # Display preferences
    display_preferences: Optional[Dict[str, Any]] = Field(
        None,
        description="Display preferences for the language"
    )
    
    # Fallback translations
    fallback_language: Optional[LanguageCode] = Field(
        None,
        description="Fallback language if translation not available"
    )
    fallback_content: Optional[str] = Field(
        None,
        description="Fallback content"
    )
    
    # Translator information
    translator_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Name of translator"
    )
    translator_email: Optional[str] = Field(
        None,
        max_length=100,
        description="Email of translator"
    )
    
    # Version tracking
    source_version: Optional[str] = Field(
        None,
        max_length=20,
        description="Version of source content"
    )
    translation_version: str = Field(
        default="1.0",
        max_length=20,
        description="Version of this translation"
    )


# =====================================================
# UPDATE SCHEMA
# =====================================================

class BenefitTranslationUpdate(BaseModel):
    """Schema for updating an existing benefit translation"""
    
    model_config = ConfigDict(from_attributes=True)
    
    translated_name: Optional[str] = Field(None, max_length=200)
    translated_description: Optional[str] = Field(None)
    translated_short_description: Optional[str] = Field(None, max_length=500)
    translated_summary: Optional[str] = Field(None)
    translated_details: Optional[str] = Field(None)
    translated_notes: Optional[str] = Field(None)
    
    # Member-facing updates
    member_friendly_name: Optional[str] = Field(None, max_length=200)
    member_description: Optional[str] = Field(None)
    member_summary: Optional[str] = Field(None)
    
    # Marketing updates
    marketing_title: Optional[str] = Field(None, max_length=200)
    marketing_description: Optional[str] = Field(None)
    key_benefits: Optional[str] = Field(None)
    
    # Quality and source updates
    translation_status: Optional[TranslationStatusEnum] = Field(None)
    translation_quality: Optional[TranslationQualityEnum] = Field(None)
    translation_source: Optional[TranslationSourceEnum] = Field(None)
    confidence_score: Optional[str] = Field(None, max_length=10)
    
    # Structured content updates
    translated_fields: Optional[Dict[str, Any]] = Field(None)
    ui_labels: Optional[Dict[str, Any]] = Field(None)
    form_labels: Optional[Dict[str, str]] = Field(None)
    validation_messages: Optional[Dict[str, str]] = Field(None)
    help_text: Optional[Dict[str, str]] = Field(None)
    
    # Document updates
    document_title: Optional[str] = Field(None, max_length=300)
    document_subtitle: Optional[str] = Field(None, max_length=300)
    section_translations: Optional[Dict[str, Dict[str, str]]] = Field(None)
    
    # Legal text updates
    legal_disclaimers: Optional[str] = Field(None)
    terms_and_conditions: Optional[str] = Field(None)
    privacy_notices: Optional[str] = Field(None)
    
    # Cultural adaptation updates
    cultural_adaptations: Optional[Dict[str, Any]] = Field(None)
    regional_variations: Optional[Dict[str, Any]] = Field(None)
    
    # Display updates
    display_preferences: Optional[Dict[str, Any]] = Field(None)
    usage_context: Optional[Dict[str, List[str]]] = Field(None)
    
    # Fallback updates
    fallback_language: Optional[LanguageCode] = Field(None)
    fallback_content: Optional[str] = Field(None)
    
    # Status updates
    is_active: Optional[bool] = Field(None)
    is_published: Optional[bool] = Field(None)
    is_default: Optional[bool] = Field(None)
    effective_to: Optional[datetime] = Field(None)
    
    # Version updates
    translation_version: Optional[str] = Field(None, max_length=20)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class BenefitTranslationResponse(BenefitTranslationBase):
    """Schema for benefit translation responses"""
    
    id: UUID = Field(..., description="Unique identifier for the translation")
    
    # Extended translation content
    translated_fields: Optional[Dict[str, Any]] = Field(None, description="Structured translations")
    ui_labels: Optional[Dict[str, Any]] = Field(None, description="UI element translations")
    form_labels: Optional[Dict[str, str]] = Field(None, description="Form label translations")
    validation_messages: Optional[Dict[str, str]] = Field(None, description="Validation message translations")
    help_text: Optional[Dict[str, str]] = Field(None, description="Help text translations")
    
    # Document translations
    document_title: Optional[str] = Field(None, description="Document title translation")
    document_subtitle: Optional[str] = Field(None, description="Document subtitle translation")
    section_translations: Optional[Dict[str, Dict[str, str]]] = Field(None, description="Section translations")
    
    # Legal text translations
    legal_disclaimers: Optional[str] = Field(None, description="Legal disclaimer translations")
    terms_and_conditions: Optional[str] = Field(None, description="Terms and conditions translations")
    privacy_notices: Optional[str] = Field(None, description="Privacy notice translations")
    
    # Cultural adaptations
    cultural_adaptations: Optional[Dict[str, Any]] = Field(None, description="Cultural adaptations")
    regional_variations: Optional[Dict[str, Any]] = Field(None, description="Regional variations")
    
    # Usage and display
    usage_context: Optional[Dict[str, List[str]]] = Field(None, description="Usage context")
    display_preferences: Optional[Dict[str, Any]] = Field(None, description="Display preferences")
    
    # Fallback information
    fallback_language: Optional[LanguageCode] = Field(None, description="Fallback language")
    fallback_content: Optional[str] = Field(None, description="Fallback content")
    
    # Workflow information
    translator_id: Optional[UUID] = Field(None, description="Translator user ID")
    translator_name: Optional[str] = Field(None, description="Translator name")
    translator_email: Optional[str] = Field(None, description="Translator email")
    
    # Review and approval
    reviewer_id: Optional[UUID] = Field(None, description="Reviewer user ID")
    reviewed_date: Optional[datetime] = Field(None, description="Review date")
    review_notes: Optional[str] = Field(None, description="Review notes")
    
    approver_id: Optional[UUID] = Field(None, description="Approver user ID")
    approved_date: Optional[datetime] = Field(None, description="Approval date")
    approval_notes: Optional[str] = Field(None, description="Approval notes")
    
    # Version and synchronization
    source_version: Optional[str] = Field(None, description="Source content version")
    translation_version: str = Field(..., description="Translation version")
    source_last_modified: Optional[datetime] = Field(None, description="Source last modified date")
    needs_update: bool = Field(default=False, description="Whether translation needs update")
    last_sync_date: Optional[datetime] = Field(None, description="Last synchronization date")
    change_summary: Optional[str] = Field(None, description="Summary of changes")
    
    # Error tracking
    translation_errors: Optional[Dict[str, List[str]]] = Field(None, description="Translation errors")
    
    # Completeness metrics
    completeness_score: Optional[float] = Field(None, ge=0, le=100, description="Translation completeness percentage")
    
    # Audit fields
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="ID of user who created the translation")
    updated_by: Optional[UUID] = Field(None, description="ID of user who last updated the translation")


class BenefitTranslationSummary(BaseModel):
    """Lightweight summary schema for benefit translations"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "entity_type": "BENEFIT_CATEGORY",
                "entity_id": "123e4567-e89b-12d3-a456-426614174001",
                "language_code": "ar",
                "language_name": "Arabic",
                "translated_name": "الفوائد الطبية",
                "translation_status": "APPROVED",
                "translation_quality": "PROFESSIONAL",
                "is_active": True,
                "is_published": True,
                "is_default": True,
                "completeness_score": 95.0
            }
        }
    )
    
    id: UUID
    entity_type: EntityTypeEnum
    entity_id: UUID
    language_code: LanguageCode
    language_name: str
    translated_name: Optional[str] = None
    translation_status: TranslationStatusEnum
    translation_quality: Optional[TranslationQualityEnum] = None
    is_active: bool
    is_published: bool
    is_default: bool
    completeness_score: Optional[float] = None


# =====================================================
# SPECIALIZED SCHEMAS
# =====================================================

class TranslationValidationRequest(BaseModel):
    """Schema for translation validation requests"""
    
    model_config = ConfigDict(from_attributes=True)
    
    translation_id: UUID = Field(..., description="Translation ID to validate")
    validation_rules: List[str] = Field(
        default=["completeness", "consistency", "cultural_appropriateness", "terminology"],
        description="Validation rules to apply"
    )
    strict_validation: bool = Field(default=False, description="Enable strict validation")


class TranslationValidationResult(BaseModel):
    """Schema for translation validation results"""
    
    model_config = ConfigDict(from_attributes=True)
    
    translation_id: UUID
    entity_type: EntityTypeEnum
    language_code: LanguageCode
    is_valid: bool = Field(..., description="Overall validation status")
    
    # Validation details
    validation_errors: List[Dict[str, str]] = Field(default_factory=list, description="Validation errors")
    validation_warnings: List[Dict[str, str]] = Field(default_factory=list, description="Validation warnings")
    validation_info: List[Dict[str, str]] = Field(default_factory=list, description="Validation information")
    
    # Completeness analysis
    completeness_score: float = Field(..., ge=0, le=100, description="Translation completeness score")
    missing_translations: List[str] = Field(default_factory=list, description="Missing translation fields")
    
    # Quality assessment
    quality_score: Optional[float] = Field(None, ge=0, le=100, description="Translation quality score")
    quality_issues: List[str] = Field(default_factory=list, description="Quality issues identified")
    
    # Cultural appropriateness
    cultural_score: Optional[float] = Field(None, ge=0, le=100, description="Cultural appropriateness score")
    cultural_issues: List[str] = Field(default_factory=list, description="Cultural issues identified")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    
    validated_at: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")


# =====================================================
# LIST AND FILTER SCHEMAS
# =====================================================

class BenefitTranslationFilter(BaseModel):
    """Schema for filtering benefit translations"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entity_type": "BENEFIT_CATEGORY",
                "language_code": "ar",
                "translation_status": "APPROVED",
                "translation_quality": "PROFESSIONAL",
                "is_active": True,
                "is_published": True,
                "completeness_min": 80.0,
                "search_term": "medical"
            }
        }
    )
    
    entity_type: Optional[EntityTypeEnum] = Field(None, description="Filter by entity type")
    entity_id: Optional[UUID] = Field(None, description="Filter by specific entity")
    language_code: Optional[LanguageCode] = Field(None, description="Filter by language")
    locale_code: Optional[str] = Field(None, description="Filter by locale")
    
    translation_status: Optional[TranslationStatusEnum] = Field(None, description="Filter by translation status")
    translation_quality: Optional[TranslationQualityEnum] = Field(None, description="Filter by quality level")
    translation_source: Optional[TranslationSourceEnum] = Field(None, description="Filter by translation source")
    
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_published: Optional[bool] = Field(None, description="Filter by published status")
    is_default: Optional[bool] = Field(None, description="Filter by default status")
    
    # Completeness filters
    completeness_min: Optional[float] = Field(None, ge=0, le=100, description="Minimum completeness score")
    needs_update: Optional[bool] = Field(None, description="Filter by update requirement")
    
    # Date filters
    effective_date_from: Optional[datetime] = Field(None, description="Effective from date")
    effective_date_to: Optional[datetime] = Field(None, description="Effective to date")
    
    # Workflow filters
    translator_id: Optional[UUID] = Field(None, description="Filter by translator")
    reviewer_id: Optional[UUID] = Field(None, description="Filter by reviewer")
    approver_id: Optional[UUID] = Field(None, description="Filter by approver")
    
    # Search fields
    search_term: Optional[str] = Field(None, max_length=100, description="Search in translated content")


class BenefitTranslationListResponse(BaseModel):
    """Schema for paginated list of benefit translations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[BenefitTranslationResponse] = Field(..., description="List of translations")
    total_count: int = Field(..., ge=0, description="Total number of translations matching filter")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")
    
    # Summary statistics
    summary: Optional[Dict[str, Any]] = Field(None, description="Summary statistics for filtered results")


# =====================================================
# BULK OPERATION SCHEMAS
# =====================================================

class BenefitTranslationBulkCreate(BaseModel):
    """Schema for bulk creating benefit translations"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "translations": [
                    {
                        "entity_type": "BENEFIT_CATEGORY",
                        "entity_id": "123e4567-e89b-12d3-a456-426614174000",
                        "language_code": "ar",
                        "language_name": "Arabic",
                        "translated_name": "الفوائد الطبية",
                        "translation_quality": "PROFESSIONAL"
                    }
                ],
                "skip_duplicates": True,
                "auto_translate": False
            }
        }
    )
    
    translations: List[BenefitTranslationCreate] = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="List of translations to create"
    )
    
    # Bulk operation settings
    skip_duplicates: bool = Field(default=False, description="Skip translations for existing entity-language combinations")
    auto_translate: bool = Field(default=False, description="Auto-translate missing content using machine translation")
    target_quality: TranslationQualityEnum = Field(default=TranslationQualityEnum.HUMAN, description="Target quality level")


class BenefitTranslationBulkUpdate(BaseModel):
    """Schema for bulk updating benefit translations"""
    
    model_config = ConfigDict(from_attributes=True)
    
    translation_ids: List[UUID] = Field(..., min_length=1, max_length=100)
    updates: BenefitTranslationUpdate = Field(..., description="Fields to update")
    
    # Update options
    preserve_custom_content: bool = Field(default=True, description="Preserve custom translated content")
    update_version: bool = Field(default=True, description="Increment translation version")


class BenefitTranslationBulkResponse(BaseModel):
    """Schema for bulk operation responses"""
    
    model_config = ConfigDict(from_attributes=True)
    
    successful_operations: int = Field(..., ge=0, description="Number of successful operations")
    failed_operations: int = Field(..., ge=0, description="Number of failed operations")
    total_operations: int = Field(..., ge=0, description="Total number of operations attempted")
    
    success_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of successful operations")
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="Details of failed operations")
    
    # Additional results
    auto_translations_created: Optional[int] = Field(None, description="Number of auto-translations created")
    versions_updated: Optional[int] = Field(None, description="Number of versions updated")