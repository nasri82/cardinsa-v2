# app/modules/benefits/models/benefit_condition_model.py
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, Optional, List, Union
import uuid

from app.core.database import Base


class BenefitCondition(Base):
    """
    Model for benefit conditions and eligibility rules.
    Defines the conditions under which benefits apply, including member eligibility,
    service conditions, and benefit applicability rules.
    """
    
    __tablename__ = "benefit_conditions"
    
    # =====================================================
    # PRIMARY FIELDS
    # =====================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    condition_code = Column(String(50), unique=True, nullable=False, index=True)
    condition_name = Column(String(150), nullable=False)
    condition_name_ar = Column(String(150), nullable=True)
    
    # =====================================================
    # CONDITION CLASSIFICATION
    # =====================================================
    
    condition_type = Column(String(30), nullable=False, index=True)
    # Options: ELIGIBILITY, COVERAGE, EXCLUSION, LIMITATION, REQUIREMENT, 
    #          QUALIFICATION, PRE_EXISTING, WAITING_PERIOD, BENEFIT_TRIGGER
    
    condition_category = Column(String(30), nullable=False, default='GENERAL')
    # Options: MEMBER, SERVICE, PROVIDER, TEMPORAL, FINANCIAL, CLINICAL, 
    #          GEOGRAPHIC, REGULATORY, ADMINISTRATIVE
    
    application_scope = Column(String(30), nullable=False, default='BENEFIT')
    # Options: BENEFIT, COVERAGE, PLAN, MEMBER, SERVICE, PROVIDER, CLAIM
    
    # =====================================================
    # CONDITION LOGIC & RULES
    # =====================================================
    
    # Logical operator for complex conditions
    logical_operator = Column(String(10), default='AND')
    # Options: AND, OR, NOT, XOR
    
    # Condition expression (for complex logical conditions)
    condition_expression = Column(Text, nullable=True)
    # Example: "(age >= 18 AND state = 'TX') OR (member_type = 'STUDENT' AND age < 26)"
    
    # Evaluation priority
    evaluation_order = Column(Integer, default=1)
    is_mandatory = Column(Boolean, default=False)
    
    # =====================================================
    # MEMBER CONDITIONS
    # =====================================================
    
    # Age-based conditions
    age_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "min_age": 18,
    #   "max_age": 65,
    #   "specific_ages": [21, 26],
    #   "age_calculation": "at_policy_effective_date"
    # }
    
    # Gender conditions
    gender_conditions = Column(ARRAY(String(10)), nullable=True)
    # Example: ["M", "F", "OTHER"]
    
    # Marital status conditions
    marital_status_conditions = Column(ARRAY(String(20)), nullable=True)
    # Example: ["SINGLE", "MARRIED", "DIVORCED", "WIDOWED"]
    
    # Employment conditions
    employment_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "employment_status": ["ACTIVE", "COBRA"],
    #   "job_class": ["FULL_TIME", "PART_TIME"],
    #   "minimum_hours": 30,
    #   "waiting_period_days": 90
    # }
    
    # Dependent conditions
    dependent_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "relationship_types": ["SPOUSE", "CHILD"],
    #   "age_limit_children": 26,
    #   "student_age_limit": 23,
    #   "disabled_child_coverage": true
    # }
    
    # =====================================================
    # HEALTH & MEDICAL CONDITIONS
    # =====================================================
    
    # Pre-existing condition rules
    pre_existing_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "lookback_period_months": 12,
    #   "exclusion_period_months": 12,
    #   "creditable_coverage_reduces": true,
    #   "excluded_conditions": ["diabetes", "hypertension"],
    #   "waived_for_newborns": true
    # }
    
    # Health status conditions
    health_status_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "required_health_screening": true,
    #   "bmi_requirements": {"min": 18.5, "max": 40},
    #   "tobacco_use_impact": "premium_surcharge",
    #   "high_risk_conditions": ["diabetes", "heart_disease"]
    # }
    
    # Disability conditions
    disability_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "requires_disability_determination": true,
    #   "social_security_disability": true,
    #   "work_related_disability": false,
    #   "temporary_vs_permanent": "both"
    # }
    
    # =====================================================
    # SERVICE & TREATMENT CONDITIONS
    # =====================================================
    
    # Service-specific conditions
    service_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "covered_services": ["preventive", "diagnostic", "treatment"],
    #   "excluded_services": ["cosmetic", "experimental"],
    #   "requires_medical_necessity": true,
    #   "prior_authorization_required": ["surgery", "imaging"]
    # }
    
    # Diagnosis conditions
    diagnosis_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "covered_diagnoses": ["E11.9", "I10"],
    #   "excluded_diagnoses": ["Z41.1"],  # Cosmetic surgery
    #   "primary_diagnosis_only": false,
    #   "chronic_condition_coverage": true
    # }
    
    # Treatment conditions
    treatment_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "step_therapy_required": true,
    #   "generic_substitution": "mandatory",
    #   "quantity_limits": {"monthly": 30, "days_supply": 30},
    #   "specialty_pharmacy_required": ["biologics"]
    # }
    
    # =====================================================
    # PROVIDER & FACILITY CONDITIONS
    # =====================================================
    
    # Provider requirements
    provider_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "network_participation": "required",
    #   "provider_types": ["MD", "DO", "NP", "PA"],
    #   "specialization_required": ["cardiology", "oncology"],
    #   "board_certification": true,
    #   "experience_years_min": 5
    # }
    
    # Facility requirements
    facility_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "accreditation_required": true,
    #   "accrediting_bodies": ["JCI", "CBAHI", "NCQA"],
    #   "facility_types": ["hospital", "clinic", "imaging_center"],
    #   "geographic_restrictions": ["same_city", "within_50_miles"]
    # }
    
    # Referral requirements
    referral_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "pcp_referral_required": true,
    #   "self_referral_allowed": ["emergency", "preventive"],
    #   "referral_validity_days": 90,
    #   "specialist_to_specialist": false
    # }
    
    # =====================================================
    # TEMPORAL CONDITIONS
    # =====================================================
    
    # Time-based conditions
    temporal_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "waiting_period_days": 90,
    #   "elimination_period": 30,
    #   "benefit_period_days": 365,
    #   "coverage_effective_date": "first_of_month",
    #   "open_enrollment_only": false
    # }
    
    # Frequency conditions
    frequency_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "visits_per_year": 12,
    #   "treatments_per_condition": 20,
    #   "reset_period": "calendar_year",
    #   "carry_over_unused": false
    # }
    
    # Seasonal conditions
    seasonal_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "seasonal_coverage": "winter_months",
    #   "blackout_periods": ["december"],
    #   "peak_season_limits": {"summer": "reduced_coverage"}
    # }
    
    # =====================================================
    # FINANCIAL CONDITIONS
    # =====================================================
    
    # Cost-sharing conditions
    cost_sharing_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "deductible_applies": true,
    #   "counts_toward_oop": true,
    #   "different_network_rates": true,
    #   "cost_tier": "preferred"
    # }
    
    # Income-based conditions
    income_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "income_verification_required": true,
    #   "federal_poverty_level": {"min": 100, "max": 400},
    #   "household_size_factor": true,
    #   "annual_verification": true
    # }
    
    # Premium conditions
    premium_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "premium_payment_current": true,
    #   "grace_period_days": 31,
    #   "reinstatement_allowed": true,
    #   "partial_payment_accepted": false
    # }
    
    # =====================================================
    # GEOGRAPHIC CONDITIONS
    # =====================================================
    
    # Geographic restrictions
    geographic_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "covered_states": ["TX", "OK", "AR"],
    #   "covered_countries": ["US", "CA"],
    #   "emergency_worldwide": true,
    #   "travel_coverage_days": 90,
    #   "residence_requirement": true
    # }
    
    # Network geographic conditions
    network_geographic_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "service_area_required": true,
    #   "out_of_area_emergency_only": true,
    #   "cross_border_coverage": false,
    #   "telemedicine_geography": "no_restrictions"
    # }
    
    # =====================================================
    # REGULATORY & COMPLIANCE CONDITIONS
    # =====================================================
    
    # Regulatory requirements
    regulatory_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "state_mandated_benefits": true,
    #   "federal_requirements": ["ACA", "HIPAA"],
    #   "licensing_requirements": true,
    #   "reporting_obligations": ["state_insurance_dept"]
    # }
    
    # Legal conditions
    legal_conditions = Column(JSONB, nullable=True)
    # Example: {
    #   "court_ordered_coverage": true,
    #   "divorce_decree_requirements": true,
    #   "legal_separation_impact": "continues_coverage",
    #   "custody_requirements": true
    # }
    
    # =====================================================
    # CONDITION RELATIONSHIPS
    # =====================================================
    
    # Links to benefit entities
    coverage_id = Column(UUID(as_uuid=True), ForeignKey('coverages.id'), nullable=True, index=True)
    benefit_type_id = Column(UUID(as_uuid=True), ForeignKey('benefit_types.id'), nullable=True, index=True)
    limit_id = Column(UUID(as_uuid=True), ForeignKey('benefit_limits.id'), nullable=True, index=True)
    
    # Condition dependencies
    parent_condition_id = Column(UUID(as_uuid=True), ForeignKey('benefit_conditions.id'), nullable=True)
    prerequisite_conditions = Column(JSONB, nullable=True)  # List of condition IDs
    
    # Mutually exclusive conditions
    exclusive_with_conditions = Column(JSONB, nullable=True)
    
    # =====================================================
    # EVALUATION & PROCESSING
    # =====================================================
    
    # Evaluation settings
    evaluation_frequency = Column(String(20), default='ON_DEMAND')
    # Options: ON_DEMAND, DAILY, WEEKLY, MONTHLY, ANNUALLY, AT_ENROLLMENT, AT_RENEWAL
    
    auto_evaluation = Column(Boolean, default=True)
    requires_manual_review = Column(Boolean, default=False)
    
    # Caching and performance
    cache_result = Column(Boolean, default=True)
    cache_duration_hours = Column(Integer, default=24)
    
    # Error handling
    error_handling = Column(String(20), default='FAIL_SAFE')
    # Options: FAIL_SAFE, FAIL_SECURE, MANUAL_REVIEW, USE_DEFAULT
    
    default_result = Column(Boolean, nullable=True)  # Default when evaluation fails
    
    # =====================================================
    # NOTIFICATION & COMMUNICATION
    # =====================================================
    
    # Notification settings
    notify_on_failure = Column(Boolean, default=False)
    notify_on_success = Column(Boolean, default=False)
    
    # Communication templates
    failure_message_template = Column(String(100), nullable=True)
    success_message_template = Column(String(100), nullable=True)
    
    # Member communication
    member_visible = Column(Boolean, default=True)
    member_explanation = Column(Text, nullable=True)
    member_explanation_ar = Column(Text, nullable=True)
    
    # =====================================================
    # STATUS & CONTROL
    # =====================================================
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_system_generated = Column(Boolean, default=False)
    
    # Effective periods
    effective_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    effective_to = Column(DateTime, nullable=True)
    
    # Testing and validation
    is_test_condition = Column(Boolean, default=False)
    validation_status = Column(String(20), default='PENDING')
    # Options: PENDING, VALIDATED, FAILED, APPROVED
    
    # =====================================================
    # METADATA & DOCUMENTATION
    # =====================================================
    
    description = Column(Text, nullable=True)
    business_purpose = Column(Text, nullable=True)
    
    # Implementation details
    implementation_notes = Column(Text, nullable=True)
    example_scenarios = Column(JSONB, nullable=True)
    
    # Regulatory documentation
    regulatory_reference = Column(String(200), nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
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
    child_conditions = relationship("BenefitCondition", backref="parent_condition", remote_side=[id])
    
    # Related entities (will be defined when other models exist)
    # coverage = relationship("Coverage", back_populates="conditions")
    # benefit_type = relationship("BenefitType", back_populates="conditions")
    # limit = relationship("BenefitLimit", back_populates="conditions")
    
    # =====================================================
    # INDEXES
    # =====================================================
    
    __table_args__ = (
        Index('idx_conditions_type_category', 'condition_type', 'condition_category'),
        Index('idx_conditions_scope_operator', 'application_scope', 'logical_operator'),
        Index('idx_conditions_active_effective', 'is_active', 'effective_from', 'effective_to'),
        Index('idx_conditions_relationships', 'coverage_id', 'benefit_type_id', 'limit_id'),
        Index('idx_conditions_evaluation', 'evaluation_order', 'is_mandatory'),
        Index('idx_conditions_parent', 'parent_condition_id'),
    )
    
    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def evaluate_condition(
        self, 
        evaluation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate this condition against provided context.
        Returns detailed evaluation result with metadata.
        """
        try:
            # Check if condition is active and effective
            if not self.is_active or not self.is_effective_for_date():
                return {
                    'result': self.default_result,
                    'satisfied': self.default_result,
                    'reason': 'Condition not active or effective',
                    'condition_code': self.condition_code
                }
            
            # Evaluate prerequisite conditions first
            prereq_result = self._evaluate_prerequisites(evaluation_context)
            if not prereq_result['all_satisfied']:
                return {
                    'result': False,
                    'satisfied': False,
                    'reason': f"Prerequisites not satisfied: {prereq_result['unsatisfied']}",
                    'condition_code': self.condition_code
                }
            
            # Perform main condition evaluation
            evaluation_result = self._perform_evaluation(evaluation_context)
            
            # Apply logical operator if there are child conditions
            if self.child_conditions:
                child_results = [child.evaluate_condition(evaluation_context) for child in self.child_conditions]
                evaluation_result = self._apply_logical_operator(evaluation_result, child_results)
            
            return {
                'result': evaluation_result['satisfied'],
                'satisfied': evaluation_result['satisfied'],
                'reason': evaluation_result['reason'],
                'condition_code': self.condition_code,
                'evaluation_details': evaluation_result.get('details', {}),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Handle evaluation errors based on error handling setting
            if self.error_handling == 'FAIL_SAFE':
                result = True
            elif self.error_handling == 'FAIL_SECURE':
                result = False
            else:
                result = self.default_result
            
            return {
                'result': result,
                'satisfied': result,
                'reason': f"Evaluation error: {str(e)}",
                'condition_code': self.condition_code,
                'error': True
            }
    
    def _evaluate_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate prerequisite conditions"""
        if not self.prerequisite_conditions:
            return {'all_satisfied': True, 'unsatisfied': []}
        
        unsatisfied = []
        for prereq_id in self.prerequisite_conditions:
            # This would load and evaluate the prerequisite condition
            # For now, return placeholder
            pass
        
        return {
            'all_satisfied': len(unsatisfied) == 0,
            'unsatisfied': unsatisfied
        }
    
    def _perform_evaluation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the main condition evaluation logic"""
        
        # Age conditions
        if self.age_conditions:
            age_result = self._evaluate_age_conditions(context)
            if not age_result['satisfied']:
                return age_result
        
        # Gender conditions
        if self.gender_conditions:
            gender_result = self._evaluate_gender_conditions(context)
            if not gender_result['satisfied']:
                return gender_result
        
        # Employment conditions
        if self.employment_conditions:
            employment_result = self._evaluate_employment_conditions(context)
            if not employment_result['satisfied']:
                return employment_result
        
        # Service conditions
        if self.service_conditions:
            service_result = self._evaluate_service_conditions(context)
            if not service_result['satisfied']:
                return service_result
        
        # Provider conditions
        if self.provider_conditions:
            provider_result = self._evaluate_provider_conditions(context)
            if not provider_result['satisfied']:
                return provider_result
        
        # Geographic conditions
        if self.geographic_conditions:
            geo_result = self._evaluate_geographic_conditions(context)
            if not geo_result['satisfied']:
                return geo_result
        
        # If all specific conditions pass, condition is satisfied
        return {
            'satisfied': True,
            'reason': 'All condition criteria satisfied',
            'details': {}
        }
    
    def _evaluate_age_conditions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate age-based conditions"""
        member_age = context.get('member_age')
        if member_age is None:
            return {'satisfied': False, 'reason': 'Member age not provided'}
        
        age_criteria = self.age_conditions
        
        # Check minimum age
        if 'min_age' in age_criteria and member_age < age_criteria['min_age']:
            return {
                'satisfied': False,
                'reason': f"Age {member_age} below minimum {age_criteria['min_age']}"
            }
        
        # Check maximum age
        if 'max_age' in age_criteria and member_age > age_criteria['max_age']:
            return {
                'satisfied': False,
                'reason': f"Age {member_age} above maximum {age_criteria['max_age']}"
            }
        
        # Check specific ages
        if 'specific_ages' in age_criteria and member_age not in age_criteria['specific_ages']:
            return {
                'satisfied': False,
                'reason': f"Age {member_age} not in allowed ages {age_criteria['specific_ages']}"
            }
        
        return {'satisfied': True, 'reason': 'Age criteria satisfied'}
    
    def _evaluate_gender_conditions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate gender-based conditions"""
        member_gender = context.get('member_gender')
        if not member_gender:
            return {'satisfied': False, 'reason': 'Member gender not provided'}
        
        if member_gender not in self.gender_conditions:
            return {
                'satisfied': False,
                'reason': f"Gender {member_gender} not in allowed genders {self.gender_conditions}"
            }
        
        return {'satisfied': True, 'reason': 'Gender criteria satisfied'}
    
    def _evaluate_employment_conditions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate employment-based conditions"""
        employment_status = context.get('employment_status')
        
        if 'employment_status' in self.employment_conditions:
            if employment_status not in self.employment_conditions['employment_status']:
                return {
                    'satisfied': False,
                    'reason': f"Employment status {employment_status} not allowed"
                }
        
        # Check minimum hours if required
        if 'minimum_hours' in self.employment_conditions:
            hours_worked = context.get('hours_worked_per_week', 0)
            min_hours = self.employment_conditions['minimum_hours']
            if hours_worked < min_hours:
                return {
                    'satisfied': False,
                    'reason': f"Hours worked {hours_worked} below minimum {min_hours}"
                }
        
        return {'satisfied': True, 'reason': 'Employment criteria satisfied'}
    
    def _evaluate_service_conditions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate service-related conditions"""
        service_type = context.get('service_type')
        
        # Check covered services
        if 'covered_services' in self.service_conditions:
            if service_type not in self.service_conditions['covered_services']:
                return {
                    'satisfied': False,
                    'reason': f"Service type {service_type} not covered"
                }
        
        # Check excluded services
        if 'excluded_services' in self.service_conditions:
            if service_type in self.service_conditions['excluded_services']:
                return {
                    'satisfied': False,
                    'reason': f"Service type {service_type} explicitly excluded"
                }
        
        return {'satisfied': True, 'reason': 'Service criteria satisfied'}
    
    def _evaluate_provider_conditions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate provider-related conditions"""
        provider_network = context.get('provider_network_status')
        
        if 'network_participation' in self.provider_conditions:
            if self.provider_conditions['network_participation'] == 'required' and provider_network != 'IN_NETWORK':
                return {
                    'satisfied': False,
                    'reason': 'In-network provider required'
                }
        
        return {'satisfied': True, 'reason': 'Provider criteria satisfied'}
    
    def _evaluate_geographic_conditions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate geographic conditions"""
        member_state = context.get('member_state')
        service_location = context.get('service_location_state')
        
        if 'covered_states' in self.geographic_conditions:
            covered_states = self.geographic_conditions['covered_states']
            
            # Check member residence
            if member_state and member_state not in covered_states:
                return {
                    'satisfied': False,
                    'reason': f"Member state {member_state} not in covered states {covered_states}"
                }
            
            # Check service location
            if service_location and service_location not in covered_states:
                return {
                    'satisfied': False,
                    'reason': f"Service location {service_location} not in covered states {covered_states}"
                }
        
        return {'satisfied': True, 'reason': 'Geographic criteria satisfied'}
    
    def _apply_logical_operator(self, main_result: Dict[str, Any], child_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply logical operator to combine results"""
        if self.logical_operator == 'AND':
            all_satisfied = main_result['satisfied'] and all(r['satisfied'] for r in child_results)
            return {
                'satisfied': all_satisfied,
                'reason': 'All conditions must be satisfied (AND)' if all_satisfied else 'Not all AND conditions satisfied'
            }
        
        elif self.logical_operator == 'OR':
            any_satisfied = main_result['satisfied'] or any(r['satisfied'] for r in child_results)
            return {
                'satisfied': any_satisfied,
                'reason': 'At least one condition satisfied (OR)' if any_satisfied else 'No OR conditions satisfied'
            }
        
        elif self.logical_operator == 'NOT':
            return {
                'satisfied': not main_result['satisfied'],
                'reason': 'Condition negated (NOT)'
            }
        
        # Default to main result
        return main_result
    
    def is_effective_for_date(self, check_date: datetime = None) -> bool:
        """Check if condition is effective for a specific date"""
        if not check_date:
            check_date = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if check_date < self.effective_from:
            return False
        
        if self.effective_to and check_date > self.effective_to:
            return False
        
        return True
    
    def get_member_friendly_explanation(self) -> str:
        """Get member-friendly explanation of the condition"""
        if self.member_explanation:
            return self.member_explanation
        
        # Generate basic explanation based on condition type
        if self.condition_type == 'ELIGIBILITY':
            return f"You must meet eligibility requirements for {self.condition_name}"
        elif self.condition_type == 'EXCLUSION':
            return f"This benefit excludes {self.condition_name}"
        elif self.condition_type == 'WAITING_PERIOD':
            return f"There is a waiting period for {self.condition_name}"
        else:
            return f"Condition applies: {self.condition_name}"
    
    def __repr__(self):
        return f"<BenefitCondition(id={self.id}, code='{self.condition_code}', type='{self.condition_type}')>"