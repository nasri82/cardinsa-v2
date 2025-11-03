# app/modules/benefits/models/benefit_translation_model.py
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

from app.core.database import Base


class BenefitTranslation(Base):
    """
    Model for storing translations of benefit information across multiple languages.
    Supports multilingual benefit descriptions, terms, and member communications.
    """
    
    __tablename__ = "benefit_translations"
    
    # =====================================================
    # PRIMARY FIELDS
    # =====================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Reference to the original entity being translated
    entity_type = Column(String(50), nullable=False, index=True)
    # Options: BENEFIT_CATEGORY, BENEFIT_TYPE, COVERAGE, COVERAGE_OPTION, BENEFIT_LIMIT, 
    #          CALCULATION_RULE, PLAN_SCHEDULE, BENEFIT_TERM, MEMBER_COMMUNICATION
    
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Language information
    language_code = Column(String(5), nullable=False, index=True)  # ISO 639-1 (e.g., 'ar', 'fr', 'es')
    language_name = Column(String(50), nullable=False)  # Full language name
    locale_code = Column(String(10), nullable=True)  # Full locale (e.g., 'ar-SA', 'fr-CA')
    
    # =====================================================
    # TRANSLATION CONTENT
    # =====================================================
    
    # Basic translated fields
    translated_name = Column(String(200), nullable=True)
    translated_description = Column(Text, nullable=True)
    translated_short_description = Column(String(500), nullable=True)
    
    # Additional translated content
    translated_summary = Column(Text, nullable=True)
    translated_details = Column(Text, nullable=True)
    translated_notes = Column(Text, nullable=True)
    
    # Member-facing translations
    member_friendly_name = Column(String(200), nullable=True)
    member_description = Column(Text, nullable=True)
    member_summary = Column(Text, nullable=True)
    
    # Marketing and communication translations
    marketing_title = Column(String(200), nullable=True)
    marketing_description = Column(Text, nullable=True)
    key_benefits = Column(Text, nullable=True)
    
    # =====================================================
    # STRUCTURED TRANSLATIONS
    # =====================================================
    
    # For complex structured content (JSON format)
    translated_fields = Column(JSONB, nullable=True)
    # Example: {
    #   "coverage_levels": {
    #     "basic": "الأساسي",
    #     "standard": "المعيار", 
    #     "premium": "المتميز"
    #   },
    #   "benefit_terms": {
    #     "deductible": "الخصم القابل للتطبيق",
    #     "copay": "المبلغ المشترك",
    #     "coinsurance": "التأمين المشترك"
    #   }
    # }
    
    # UI/UX translations
    ui_labels = Column(JSONB, nullable=True)
    # Example: {
    #   "buttons": {"apply": "تطبيق", "cancel": "إلغاء"},
    #   "headers": {"benefits": "الفوائد", "coverage": "التغطية"},
    #   "messages": {"not_covered": "غير مغطى", "covered": "مغطى"}
    # }
    
    # Form and validation translations
    form_labels = Column(JSONB, nullable=True)
    validation_messages = Column(JSONB, nullable=True)
    help_text = Column(JSONB, nullable=True)
    
    # =====================================================
    # DOCUMENT TRANSLATIONS
    # =====================================================
    
    # Document-specific translations
    document_title = Column(String(300), nullable=True)
    document_subtitle = Column(String(300), nullable=True)
    
    # Section headings and content
    section_translations = Column(JSONB, nullable=True)
    # Example: {
    #   "preventive_care": {
    #     "title": "الرعاية الوقائية",
    #     "description": "خدمات الفحص والوقاية المغطاة 100%"
    #   }
    # }
    
    # Legal and regulatory text
    legal_disclaimers = Column(Text, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    privacy_notices = Column(Text, nullable=True)
    
    # =====================================================
    # TRANSLATION QUALITY & METADATA
    # =====================================================
    
    # Translation status and quality
    translation_status = Column(String(20), default='PENDING')
    # Options: PENDING, IN_PROGRESS, COMPLETED, REVIEWED, APPROVED, PUBLISHED, REJECTED
    
    translation_quality = Column(String(20), nullable=True)
    # Options: MACHINE, HUMAN, PROFESSIONAL, CERTIFIED, NATIVE_SPEAKER
    
    # Translation source
    translation_source = Column(String(30), nullable=True)
    # Options: MANUAL, GOOGLE_TRANSLATE, AZURE_TRANSLATOR, PROFESSIONAL_SERVICE, INTERNAL_TEAM
    
    confidence_score = Column(String(10), nullable=True)  # For machine translations
    
    # =====================================================
    # WORKFLOW & APPROVAL
    # =====================================================
    
    # Translator information
    translator_id = Column(UUID(as_uuid=True), nullable=True)
    translator_name = Column(String(100), nullable=True)
    translator_email = Column(String(100), nullable=True)
    
    # Review and approval
    reviewer_id = Column(UUID(as_uuid=True), nullable=True)
    reviewed_date = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    approver_id = Column(UUID(as_uuid=True), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # =====================================================
    # VERSIONING & SYNCHRONIZATION
    # =====================================================
    
    # Version tracking
    source_version = Column(String(20), nullable=True)  # Version of source content
    translation_version = Column(String(20), default='1.0')
    
    # Synchronization tracking
    source_last_modified = Column(DateTime, nullable=True)
    needs_update = Column(Boolean, default=False)
    
    # Change tracking
    last_sync_date = Column(DateTime, nullable=True)
    change_summary = Column(Text, nullable=True)
    
    # =====================================================
    # CULTURAL & REGIONAL ADAPTATIONS
    # =====================================================
    
    # Cultural considerations
    cultural_adaptations = Column(JSONB, nullable=True)
    # Example: {
    #   "currency_format": "ريال سعودي",
    #   "date_format": "dd/mm/yyyy",
    #   "number_format": "arabic_numerals",
    #   "reading_direction": "rtl"
    # }
    
    # Regional variations
    regional_variations = Column(JSONB, nullable=True)
    # Example: {
    #   "terminology": "gulf_arabic",
    #   "currency": "SAR",
    #   "regulations": "saudi_insurance_law"
    # }
    
    # =====================================================
    # USAGE & CONTEXT
    # =====================================================
    
    # Context where translation is used
    usage_context = Column(JSONB, nullable=True)
    # Example: {
    #   "channels": ["web", "mobile", "print", "email"],
    #   "audiences": ["members", "brokers", "providers"],
    #   "purposes": ["enrollment", "claims", "customer_service"]
    # }
    
    # Display preferences
    display_preferences = Column(JSONB, nullable=True)
    # Example: {
    #   "font_family": "arabic_font",
    #   "text_alignment": "right",
    #   "line_height": 1.6
    # }
    
    # =====================================================
    # FALLBACK & ERROR HANDLING
    # =====================================================
    
    # Fallback translations
    fallback_language = Column(String(5), nullable=True)
    fallback_content = Column(Text, nullable=True)
    
    # Error handling
    translation_errors = Column(JSONB, nullable=True)
    # Example: {
    #   "missing_terms": ["deductible", "copay"],
    #   "formatting_issues": ["rtl_alignment"],
    #   "validation_errors": ["character_encoding"]
    # }
    
    # =====================================================
    # STATUS & CONTROL
    # =====================================================
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_published = Column(Boolean, default=False, index=True)
    is_default = Column(Boolean, default=False)  # Default translation for the language
    
    # Effective periods
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)
    
    # =====================================================
    # METADATA & AUDIT
    # =====================================================
    
    # Internal notes
    internal_notes = Column(Text, nullable=True)
    translator_notes = Column(Text, nullable=True)
    
    # Source information
    source_system = Column(String(50), nullable=True)
    external_id = Column(String(50), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # =====================================================
    # CONSTRAINTS & INDEXES
    # =====================================================
    
    __table_args__ = (
        # Unique constraint for entity + language combination
        UniqueConstraint('entity_type', 'entity_id', 'language_code', name='uq_benefit_translation_entity_lang'),
        
        # Indexes
        Index('idx_benefit_translations_entity', 'entity_type', 'entity_id'),
        Index('idx_benefit_translations_language', 'language_code', 'locale_code'),
        Index('idx_benefit_translations_status', 'translation_status', 'is_published'),
        Index('idx_benefit_translations_effective', 'effective_from', 'effective_to', 'is_active'),
        Index('idx_benefit_translations_workflow', 'translator_id', 'reviewer_id', 'approver_id'),
    )
    
    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def get_translated_field(self, field_name: str, fallback: str = None) -> Optional[str]:
        """
        Get a specific translated field with fallback logic.
        """
        # Try direct field mapping
        field_mapping = {
            'name': self.translated_name,
            'description': self.translated_description,
            'short_description': self.translated_short_description,
            'summary': self.translated_summary,
            'member_name': self.member_friendly_name,
            'member_description': self.member_description,
            'marketing_title': self.marketing_title
        }
        
        value = field_mapping.get(field_name)
        if value:
            return value
        
        # Check structured translations
        if self.translated_fields and field_name in self.translated_fields:
            return self.translated_fields[field_name]
        
        # Return fallback if provided
        return fallback
    
    def get_ui_label(self, label_key: str, fallback: str = None) -> Optional[str]:
        """Get UI label translation with fallback"""
        if not self.ui_labels:
            return fallback
        
        # Support nested keys like "buttons.apply"
        keys = label_key.split('.')
        value = self.ui_labels
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return fallback
    
    def get_section_translation(self, section_key: str) -> Dict[str, Any]:
        """Get section translation with all related content"""
        if not self.section_translations:
            return {}
        
        return self.section_translations.get(section_key, {})
    
    def is_translation_current(self) -> bool:
        """Check if translation is current with source content"""
        if not self.source_last_modified or not self.last_sync_date:
            return False
        
        return self.last_sync_date >= self.source_last_modified and not self.needs_update
    
    def mark_for_update(self, reason: str = None):
        """Mark translation as needing update"""
        self.needs_update = True
        self.translation_status = 'PENDING'
        if reason:
            self.change_summary = reason
        self.updated_at = datetime.utcnow()
    
    def approve_translation(self, approver_id: UUID, notes: str = None):
        """Approve the translation"""
        self.translation_status = 'APPROVED'
        self.approver_id = approver_id
        self.approved_date = datetime.utcnow()
        if notes:
            self.approval_notes = notes
    
    def publish_translation(self):
        """Publish the approved translation"""
        if self.translation_status != 'APPROVED':
            raise ValueError("Translation must be approved before publishing")
        
        self.translation_status = 'PUBLISHED'
        self.is_published = True
        self.updated_at = datetime.utcnow()
    
    def get_display_preferences(self) -> Dict[str, Any]:
        """Get display preferences for the language"""
        defaults = {
            'text_direction': 'ltr',
            'text_alignment': 'left',
            'font_family': 'default',
            'line_height': 1.4
        }
        
        # Special handling for RTL languages
        if self.language_code in ['ar', 'he', 'fa', 'ur']:
            defaults.update({
                'text_direction': 'rtl',
                'text_alignment': 'right',
                'font_family': 'arabic_font',
                'line_height': 1.6
            })
        
        if self.display_preferences:
            defaults.update(self.display_preferences)
        
        return defaults
    
    def validate_translation_completeness(self) -> Dict[str, Any]:
        """Validate that translation is complete and consistent"""
        issues = []
        warnings = []
        
        # Check required fields
        if not self.translated_name:
            issues.append("Missing translated name")
        
        if not self.translated_description:
            issues.append("Missing translated description")
        
        # Check for RTL language requirements
        if self.language_code in ['ar', 'he', 'fa', 'ur']:
            if not self.display_preferences or self.display_preferences.get('text_direction') != 'rtl':
                warnings.append("RTL language should have RTL display preferences")
        
        # Check translation quality
        if self.translation_quality == 'MACHINE' and not self.reviewer_id:
            warnings.append("Machine translation should be reviewed by human")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'completeness_score': self._calculate_completeness_score()
        }
    
    def _calculate_completeness_score(self) -> float:
        """Calculate completeness score based on filled fields"""
        total_fields = 8  # Key translation fields
        filled_fields = 0
        
        if self.translated_name: filled_fields += 1
        if self.translated_description: filled_fields += 1
        if self.translated_short_description: filled_fields += 1
        if self.member_friendly_name: filled_fields += 1
        if self.member_description: filled_fields += 1
        if self.translated_fields: filled_fields += 1
        if self.ui_labels: filled_fields += 1
        if self.section_translations: filled_fields += 1
        
        return (filled_fields / total_fields) * 100
    
    def __repr__(self):
        return f"<BenefitTranslation(id={self.id}, entity_type='{self.entity_type}', language='{self.language_code}')>"