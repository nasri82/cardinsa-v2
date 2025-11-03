# app/modules/benefits/models/benefit_preapproval_rule_model.py
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List
import uuid

from app.core.database import Base


class BenefitPreapprovalRule(Base):
    """
    Model for benefit pre-approval rules and prior authorization requirements.
    Defines when services require prior authorization and the approval process.
    """
    
    __tablename__ = "benefit_preapproval_rules"
    
    # =====================================================
    # PRIMARY FIELDS
    # =====================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    rule_name = Column(String(150), nullable=False)
    rule_name_ar = Column(String(150), nullable=True)
    
    # =====================================================
    # RULE CLASSIFICATION
    # =====================================================
    
    approval_type = Column(String(30), nullable=False, index=True)
    # Options: PRIOR_AUTH, PRE_CERTIFICATION, REFERRAL, STEP_THERAPY, QUANTITY_LIMIT, 
    #          MEDICAL_NECESSITY, EXPERIMENTAL_REVIEW, CONCURRENT_REVIEW
    
    rule_category = Column(String(30), nullable=False, default='MEDICAL')
    # Options: MEDICAL, SURGICAL, DIAGNOSTIC, THERAPEUTIC, PHARMACEUTICAL, 
    #          DURABLE_MEDICAL_EQUIPMENT, HOME_HEALTH, MENTAL_HEALTH
    
    urgency_level = Column(String(20), nullable=False, default='STANDARD')
    # Options: EMERGENCY, URGENT, STANDARD, ELECTIVE
    
    # =====================================================
    # SERVICE & COVERAGE SCOPE
    # =====================================================
    
    # Service identification
    applicable_services = Column(JSONB, nullable=True)
    # Example: {
    #   "procedure_codes": ["12345", "67890"],
    #   "service_categories": ["MRI", "CT_SCAN"],
    #   "diagnosis_codes": ["Z12.11", "Z12.31"]
    # }
    
    service_types = Column(ARRAY(String(50)), nullable=True)
    # Example: ["INPATIENT_SURGERY", "OUTPATIENT_IMAGING", "SPECIALTY_DRUGS"]
    
    excluded_services = Column(JSONB, nullable=True)
    # Services that are explicitly excluded from this rule
    
    # Provider and facility requirements
    provider_types = Column(ARRAY(String(30)), nullable=True)
    # Example: ["SPECIALIST", "HOSPITAL", "IMAGING_CENTER"]
    
    facility_requirements = Column(JSONB, nullable=True)
    # Example: {
    #   "accreditation_required": true,
    #   "certification_types": ["JCI", "CBAHI"],
    #   "minimum_volume": 50
    # }
    
    # =====================================================
    # APPROVAL CRITERIA & THRESHOLDS
    # =====================================================
    
    # Financial thresholds
    cost_threshold = Column(Numeric(15, 2), nullable=True)
    cost_threshold_currency = Column(String(3), default='USD')
    
    # Quantity and frequency limits
    quantity_threshold = Column(Integer, nullable=True)
    frequency_threshold = Column(Integer, nullable=True)
    frequency_period = Column(String(20), nullable=True)  # DAILY, WEEKLY, MONTHLY, ANNUALLY
    
    # Duration limits
    max_treatment_days = Column(Integer, nullable=True)
    max_sessions = Column(Integer, nullable=True)
    
    # Age-based criteria
    age_criteria = Column(JSONB, nullable=True)
    # Example: {
    #   "min_age": 18,
    #   "max_age": 65,
    #   "pediatric_special_rules": true
    # }
    
    # Gender-specific rules
    gender_specific = Column(Boolean, default=False)
    applicable_genders = Column(ARRAY(String(10)), nullable=True)
    
    # =====================================================
    # CLINICAL CRITERIA
    # =====================================================
    
    # Medical necessity criteria
    medical_criteria = Column(JSONB, nullable=True)
    # Example: {
    #   "required_diagnoses": ["M79.3", "M25.511"],
    #   "contraindications": ["Z87.891"],
    #   "lab_requirements": {
    #     "creatinine": {"max": 1.5, "units": "mg/dL"},
    #     "hemoglobin": {"min": 10, "units": "g/dL"}
    #   }
    # }
    
    # Conservative treatment requirements
    step_therapy_required = Column(Boolean, default=False)
    step_therapy_criteria = Column(JSONB, nullable=True)
    # Example: {
    #   "required_treatments": ["physical_therapy", "nsaids"],
    #   "trial_duration": 90,
    #   "failure_criteria": "no_improvement"
    # }
    
    # Documentation requirements
    documentation_requirements = Column(JSONB, nullable=True)
    # Example: {
    #   "clinical_notes": true,
    #   "imaging_results": ["MRI", "CT"],
    #   "lab_results": ["CBC", "BMP"],
    #   "specialist_consultation": true,
    #   "treatment_history": 6  # months
    # }
    
    # =====================================================
    # APPROVAL PROCESS & WORKFLOW
    # =====================================================
    
    # Review levels
    review_level = Column(String(30), nullable=False, default='MEDICAL_DIRECTOR')
    # Options: AUTO_APPROVED, NURSE_REVIEWER, MEDICAL_DIRECTOR, 
    #          SPECIALIST_CONSULTANT, EXTERNAL_REVIEW, COMMITTEE_REVIEW
    
    requires_specialist_review = Column(Boolean, default=False)
    specialist_type = Column(String(50), nullable=True)
    
    # Review timeline
    review_timeframe_hours = Column(Integer, default=72)
    emergency_review_hours = Column(Integer, default=2)
    
    # Approval validity
    approval_validity_days = Column(Integer, default=90)
    retroactive_approval_allowed = Column(Boolean, default=False)
    retroactive_days_limit = Column(Integer, nullable=True)
    
    # =====================================================
    # SUBMISSION REQUIREMENTS
    # =====================================================
    
    # Required forms and documents
    required_forms = Column(JSONB, nullable=True)
    # Example: {
    #   "prior_auth_form": "PA-001",
    #   "clinical_assessment": "CA-MRI-001",
    #   "physician_statement": true
    # }
    
    # Information requirements
    required_information = Column(JSONB, nullable=True)
    # Example: {
    #   "diagnosis": {"primary": true, "secondary": false},
    #   "symptom_duration": true,
    #   "previous_treatments": true,
    #   "treatment_plan": true,
    #   "expected_outcomes": true
    # }
    
    # Submission methods
    submission_methods = Column(ARRAY(String(20)), nullable=True)
    # Example: ["ONLINE_PORTAL", "FAX", "PHONE", "EMAIL"]
    
    preferred_submission_method = Column(String(20), default='ONLINE_PORTAL')
    
    # =====================================================
    # DECISION CRITERIA & OUTCOMES
    # =====================================================
    
    # Auto-approval criteria
    auto_approval_criteria = Column(JSONB, nullable=True)
    # Example: {
    #   "emergency_services": true,
    #   "cost_under": 1000,
    #   "routine_procedures": ["annual_physical", "mammogram"]
    # }
    
    # Denial criteria
    common_denial_reasons = Column(JSONB, nullable=True)
    # Example: {
    #   "experimental": "Treatment is considered experimental",
    #   "not_medically_necessary": "Not medically necessary",
    #   "alternative_available": "Less costly alternative available"
    # }
    
    # Appeal process
    appeals_allowed = Column(Boolean, default=True)
    appeal_timeframe_days = Column(Integer, default=60)
    appeal_levels = Column(Integer, default=2)
    
    # =====================================================
    # NOTIFICATION & COMMUNICATION
    # =====================================================
    
    # Notification requirements
    notify_member = Column(Boolean, default=True)
    notify_provider = Column(Boolean, default=True)
    notify_referral_source = Column(Boolean, default=False)
    
    # Communication templates
    approval_template = Column(String(100), nullable=True)
    denial_template = Column(String(100), nullable=True)
    pending_template = Column(String(100), nullable=True)
    
    # Communication methods
    communication_methods = Column(ARRAY(String(20)), nullable=True)
    # Example: ["EMAIL", "SMS", "PHONE", "MAIL", "PORTAL_MESSAGE"]
    
    # Language preferences
    multilingual_support = Column(Boolean, default=False)
    supported_languages = Column(ARRAY(String(5)), nullable=True)
    
    # =====================================================
    # EXCEPTIONS & OVERRIDES
    # =====================================================
    
    # Emergency exceptions
    emergency_override_allowed = Column(Boolean, default=True)
    emergency_criteria = Column(JSONB, nullable=True)
    # Example: {
    #   "life_threatening": true,
    #   "limb_threatening": true,
    #   "severe_pain": true,
    #   "imminent_deterioration": true
    # }
    
    # Manual override permissions
    override_allowed = Column(Boolean, default=False)
    override_authorization_levels = Column(ARRAY(String(30)), nullable=True)
    # Example: ["MEDICAL_DIRECTOR", "VP_MEDICAL", "CHIEF_MEDICAL_OFFICER"]
    
    # Special circumstances
    special_circumstances = Column(JSONB, nullable=True)
    # Example: {
    #   "rare_disease": {"auto_approve": true},
    #   "clinical_trial": {"expedite": true},
    #   "second_opinion": {"waive_step_therapy": true}
    # }
    
    # =====================================================
    # RELATIONSHIPS & DEPENDENCIES
    # =====================================================
    
    # Links to other benefit entities
    coverage_id = Column(UUID(as_uuid=True), ForeignKey('coverages.id'), nullable=True, index=True)
    benefit_type_id = Column(UUID(as_uuid=True), ForeignKey('benefit_types.id'), nullable=True, index=True)
    limit_id = Column(UUID(as_uuid=True), ForeignKey('benefit_limits.id'), nullable=True, index=True)
    
    # Rule dependencies
    parent_rule_id = Column(UUID(as_uuid=True), ForeignKey('benefit_preapproval_rules.id'), nullable=True)
    prerequisite_rules = Column(JSONB, nullable=True)  # List of rule IDs that must be satisfied first
    
    # Related approval rules
    related_rules = Column(JSONB, nullable=True)
    
    # =====================================================
    # PERFORMANCE & ANALYTICS
    # =====================================================
    
    # Processing metrics
    average_processing_time = Column(Numeric(5, 2), nullable=True)  # Hours
    approval_rate = Column(Numeric(5, 2), nullable=True)  # Percentage
    denial_rate = Column(Numeric(5, 2), nullable=True)  # Percentage
    
    # Volume tracking
    monthly_volume_avg = Column(Integer, nullable=True)
    peak_volume_capacity = Column(Integer, nullable=True)
    
    # Performance targets
    target_processing_time = Column(Integer, default=24)  # Hours
    target_approval_rate = Column(Numeric(5, 2), nullable=True)
    
    # =====================================================
    # REGULATORY & COMPLIANCE
    # =====================================================
    
    # Regulatory requirements
    regulatory_source = Column(String(100), nullable=True)
    regulatory_reference = Column(String(200), nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
    # State-specific requirements
    state_specific = Column(Boolean, default=False)
    applicable_states = Column(ARRAY(String(2)), nullable=True)
    
    # Accreditation requirements
    accreditation_requirements = Column(JSONB, nullable=True)
    # Example: {
    #   "NCQA": {"standards": ["UM-1", "UM-2"]},
    #   "URAC": {"requirements": ["prior_auth_process"]}
    # }
    
    # =====================================================
    # STATUS & CONTROL
    # =====================================================
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_mandatory = Column(Boolean, default=True)
    is_system_generated = Column(Boolean, default=False)
    
    # Effective periods
    effective_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    effective_to = Column(DateTime, nullable=True)
    
    # Testing and deployment
    is_pilot_rule = Column(Boolean, default=False)
    pilot_end_date = Column(DateTime, nullable=True)
    
    # =====================================================
    # METADATA & DOCUMENTATION
    # =====================================================
    
    description = Column(Text, nullable=True)
    business_rationale = Column(Text, nullable=True)
    clinical_rationale = Column(Text, nullable=True)
    
    # Implementation guidance
    implementation_notes = Column(Text, nullable=True)
    training_materials = Column(JSONB, nullable=True)
    
    # Examples and scenarios
    example_scenarios = Column(JSONB, nullable=True)
    # Example: {
    #   "approved_case": "65-year-old with chronic knee pain, failed PT and NSAIDs",
    #   "denied_case": "35-year-old with minor strain, no conservative treatment trial"
    # }
    
    # =====================================================
    # AUDIT & VERSIONING
    # =====================================================
    
    version = Column(String(20), default='1.0')
    change_reason = Column(String(255), nullable=True)
    
    # Source tracking
    source_system = Column(String(50), nullable=True)
    external_id = Column(String(50), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # =====================================================
    # RELATIONSHIPS
    # =====================================================
    
    # Parent-child relationships
    child_rules = relationship("BenefitPreapprovalRule", backref="parent_rule", remote_side=[id])
    
    # Related entities (will be defined when other models exist)
    # coverage = relationship("Coverage", back_populates="preapproval_rules")
    # benefit_type = relationship("BenefitType", back_populates="preapproval_rules")
    # limit = relationship("BenefitLimit", back_populates="preapproval_rules")
    
    # =====================================================
    # INDEXES
    # =====================================================
    
    __table_args__ = (
        Index('idx_preapproval_type_category', 'approval_type', 'rule_category'),
        Index('idx_preapproval_urgency_level', 'urgency_level', 'review_level'),
        Index('idx_preapproval_active_effective', 'is_active', 'effective_from', 'effective_to'),
        Index('idx_preapproval_relationships', 'coverage_id', 'benefit_type_id', 'limit_id'),
        Index('idx_preapproval_cost_threshold', 'cost_threshold'),
        Index('idx_preapproval_processing', 'review_timeframe_hours', 'approval_validity_days'),
    )
    
    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def requires_preapproval(
        self, 
        service_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine if a service request requires pre-approval based on this rule.
        """
        # Check if rule is active and effective
        if not self.is_active or not self.is_effective_for_date():
            return {
                'required': False,
                'reason': 'Rule not active or effective'
            }
        
        # Check service applicability
        if not self._service_matches_criteria(service_request):
            return {
                'required': False,
                'reason': 'Service not covered by this rule'
            }
        
        # Check thresholds
        threshold_check = self._check_thresholds(service_request)
        if not threshold_check['exceeds_threshold']:
            return {
                'required': False,
                'reason': f"Below threshold: {threshold_check['reason']}"
            }
        
        # Check for auto-approval criteria
        if self._meets_auto_approval_criteria(service_request):
            return {
                'required': False,
                'reason': 'Meets auto-approval criteria',
                'auto_approved': True
            }
        
        # Check for emergency override
        if self._is_emergency_case(service_request):
            return {
                'required': True,
                'urgency': 'EMERGENCY',
                'review_hours': self.emergency_review_hours,
                'reason': 'Emergency case - expedited review'
            }
        
        return {
            'required': True,
            'urgency': self.urgency_level,
            'review_hours': self.review_timeframe_hours,
            'review_level': self.review_level,
            'required_documents': self.required_forms,
            'submission_methods': self.submission_methods
        }
    
    def _service_matches_criteria(self, service_request: Dict[str, Any]) -> bool:
        """Check if service matches the rule's applicable criteria"""
        
        # Check service types
        if self.service_types:
            service_type = service_request.get('service_type')
            if service_type not in self.service_types:
                return False
        
        # Check procedure codes
        if self.applicable_services and 'procedure_codes' in self.applicable_services:
            procedure_code = service_request.get('procedure_code')
            if procedure_code not in self.applicable_services['procedure_codes']:
                return False
        
        # Check diagnosis codes
        if self.applicable_services and 'diagnosis_codes' in self.applicable_services:
            diagnosis_codes = service_request.get('diagnosis_codes', [])
            rule_diagnoses = self.applicable_services['diagnosis_codes']
            if not any(code in rule_diagnoses for code in diagnosis_codes):
                return False
        
        # Check exclusions
        if self.excluded_services:
            if service_request.get('procedure_code') in self.excluded_services.get('procedure_codes', []):
                return False
        
        return True
    
    def _check_thresholds(self, service_request: Dict[str, Any]) -> Dict[str, Any]:
        """Check if service exceeds approval thresholds"""
        
        # Cost threshold
        if self.cost_threshold:
            service_cost = Decimal(str(service_request.get('estimated_cost', 0)))
            if service_cost < self.cost_threshold:
                return {
                    'exceeds_threshold': False,
                    'reason': f'Cost ${service_cost} below threshold ${self.cost_threshold}'
                }
        
        # Quantity threshold
        if self.quantity_threshold:
            quantity = service_request.get('quantity', 1)
            if quantity < self.quantity_threshold:
                return {
                    'exceeds_threshold': False,
                    'reason': f'Quantity {quantity} below threshold {self.quantity_threshold}'
                }
        
        # Age criteria
        if self.age_criteria:
            age = service_request.get('member_age')
            if age is not None:
                min_age = self.age_criteria.get('min_age')
                max_age = self.age_criteria.get('max_age')
                
                if min_age and age < min_age:
                    return {'exceeds_threshold': False, 'reason': f'Age {age} below minimum {min_age}'}
                if max_age and age > max_age:
                    return {'exceeds_threshold': False, 'reason': f'Age {age} above maximum {max_age}'}
        
        return {'exceeds_threshold': True, 'reason': 'Meets all thresholds'}
    
    def _meets_auto_approval_criteria(self, service_request: Dict[str, Any]) -> bool:
        """Check if request meets auto-approval criteria"""
        if not self.auto_approval_criteria:
            return False
        
        # Emergency services auto-approval
        if self.auto_approval_criteria.get('emergency_services') and service_request.get('is_emergency'):
            return True
        
        # Cost-based auto-approval
        cost_under = self.auto_approval_criteria.get('cost_under')
        if cost_under:
            service_cost = Decimal(str(service_request.get('estimated_cost', 0)))
            if service_cost <= cost_under:
                return True
        
        # Routine procedures auto-approval
        routine_procedures = self.auto_approval_criteria.get('routine_procedures', [])
        if service_request.get('procedure_code') in routine_procedures:
            return True
        
        return False
    
    def _is_emergency_case(self, service_request: Dict[str, Any]) -> bool:
        """Check if this is an emergency case requiring expedited review"""
        if not self.emergency_criteria:
            return service_request.get('is_emergency', False)
        
        # Check specific emergency criteria
        if self.emergency_criteria.get('life_threatening') and service_request.get('life_threatening'):
            return True
        
        if self.emergency_criteria.get('limb_threatening') and service_request.get('limb_threatening'):
            return True
        
        return service_request.get('is_emergency', False)
    
    def get_required_documentation(self) -> List[str]:
        """Get list of required documentation for approval"""
        docs = []
        
        if self.required_forms:
            docs.extend(self.required_forms.keys())
        
        if self.documentation_requirements:
            for doc_type, required in self.documentation_requirements.items():
                if required:
                    docs.append(doc_type)
        
        return docs
    
    def calculate_approval_deadline(self, submission_date: datetime = None) -> datetime:
        """Calculate when approval decision is due"""
        if not submission_date:
            submission_date = datetime.utcnow()
        
        hours_to_add = self.emergency_review_hours if self.urgency_level == 'EMERGENCY' else self.review_timeframe_hours
        
        return submission_date + timedelta(hours=hours_to_add)
    
    def is_effective_for_date(self, check_date: datetime = None) -> bool:
        """Check if rule is effective for a specific date"""
        if not check_date:
            check_date = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if check_date < self.effective_from:
            return False
        
        if self.effective_to and check_date > self.effective_to:
            return False
        
        return True
    
    def get_appeal_deadline(self, decision_date: datetime) -> datetime:
        """Calculate appeal deadline based on decision date"""
        return decision_date + timedelta(days=self.appeal_timeframe_days)
    
    def __repr__(self):
        return f"<BenefitPreapprovalRule(id={self.id}, code='{self.rule_code}', type='{self.approval_type}')>"