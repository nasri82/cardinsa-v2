# app/modules/benefits/models/plan_benefit_schedule_model.py
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, Optional, List
import uuid

from app.core.database import Base


class PlanBenefitSchedule(Base):
    """
    Model for plan benefit schedules - the master document defining all benefits, 
    coverage levels, and cost-sharing for a specific insurance plan.
    This is the comprehensive benefit grid/schedule that members see.
    """
    
    __tablename__ = "plan_benefit_schedules"
    
    # =====================================================
    # PRIMARY FIELDS
    # =====================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    schedule_code = Column(String(50), unique=True, nullable=False, index=True)
    schedule_name = Column(String(150), nullable=False)
    schedule_name_ar = Column(String(150), nullable=True)
    
    # =====================================================
    # PLAN ASSOCIATIONS
    # =====================================================
    
    # Link to insurance plan
    plan_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    plan_code = Column(String(50), nullable=False, index=True)
    plan_name = Column(String(150), nullable=False)
    
    # Product hierarchy
    product_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    product_line = Column(String(50), nullable=True)
    
    # Market segment
    market_segment = Column(String(30), nullable=True)
    # Options: INDIVIDUAL, GROUP, LARGE_GROUP, GOVERNMENT, MEDICARE, MEDICAID
    
    target_demographic = Column(String(50), nullable=True)
    # Options: YOUNG_ADULTS, FAMILIES, SENIORS, EMPLOYEES, STUDENTS
    
    # =====================================================
    # SCHEDULE CLASSIFICATION
    # =====================================================
    
    schedule_type = Column(String(30), nullable=False, default='COMPREHENSIVE')
    # Options: COMPREHENSIVE, SUMMARY, DETAILED, COMPARISON, REGULATORY
    
    coverage_level = Column(String(20), nullable=False, default='STANDARD')
    # Options: BASIC, STANDARD, PREMIUM, PLATINUM, CATASTROPHIC
    
    metal_tier = Column(String(10), nullable=True)
    # Options: BRONZE, SILVER, GOLD, PLATINUM (ACA tiers)
    
    plan_type = Column(String(20), nullable=False, default='PPO')
    # Options: HMO, PPO, EPO, POS, HDHP, INDEMNITY
    
    # =====================================================
    # FINANCIAL OVERVIEW
    # =====================================================
    
    # Annual limits and deductibles
    annual_deductible_individual = Column(Numeric(10, 2), nullable=True)
    annual_deductible_family = Column(Numeric(10, 2), nullable=True)
    
    out_of_pocket_max_individual = Column(Numeric(10, 2), nullable=True)
    out_of_pocket_max_family = Column(Numeric(10, 2), nullable=True)
    
    # Network differentials
    in_network_deductible = Column(Numeric(10, 2), nullable=True)
    out_of_network_deductible = Column(Numeric(10, 2), nullable=True)
    
    in_network_oop_max = Column(Numeric(10, 2), nullable=True)
    out_of_network_oop_max = Column(Numeric(10, 2), nullable=True)
    
    # Lifetime maximums
    lifetime_maximum = Column(Numeric(15, 2), nullable=True)
    
    # Currency
    currency_code = Column(String(3), default='USD')
    
    # =====================================================
    # BENEFIT CATEGORIES & STRUCTURE
    # =====================================================
    
    # Core benefit structure (JSON format for flexibility)
    medical_benefits = Column(JSONB, nullable=True)
    # Example: {
    #   "preventive_care": {"in_network": "100%", "out_network": "70%", "deductible_applies": false},
    #   "primary_care": {"in_network": "$25 copay", "out_network": "70% after deductible"},
    #   "specialist": {"in_network": "$50 copay", "out_network": "70% after deductible"}
    # }
    
    prescription_benefits = Column(JSONB, nullable=True)
    # Example: {
    #   "generic": {"copay": "$10", "mail_order": "$25"},
    #   "brand_preferred": {"copay": "$35", "mail_order": "$87.50"},
    #   "brand_non_preferred": {"copay": "$70", "mail_order": "$175"},
    #   "specialty": {"coinsurance": "25%", "max_copay": "$150"}
    # }
    
    dental_benefits = Column(JSONB, nullable=True)
    vision_benefits = Column(JSONB, nullable=True)
    mental_health_benefits = Column(JSONB, nullable=True)
    wellness_benefits = Column(JSONB, nullable=True)
    
    # Additional benefit categories
    supplemental_benefits = Column(JSONB, nullable=True)
    value_added_benefits = Column(JSONB, nullable=True)
    
    # =====================================================
    # DETAILED BENEFIT BREAKDOWN
    # =====================================================
    
    # Professional services
    physician_services = Column(JSONB, nullable=True)
    specialist_services = Column(JSONB, nullable=True)
    
    # Facility services  
    hospital_inpatient = Column(JSONB, nullable=True)
    hospital_outpatient = Column(JSONB, nullable=True)
    emergency_services = Column(JSONB, nullable=True)
    urgent_care = Column(JSONB, nullable=True)
    
    # Diagnostic services
    lab_services = Column(JSONB, nullable=True)
    radiology_services = Column(JSONB, nullable=True)
    imaging_services = Column(JSONB, nullable=True)
    
    # Therapeutic services
    physical_therapy = Column(JSONB, nullable=True)
    occupational_therapy = Column(JSONB, nullable=True)
    speech_therapy = Column(JSONB, nullable=True)
    
    # Specialized care
    maternity_services = Column(JSONB, nullable=True)
    pediatric_services = Column(JSONB, nullable=True)
    geriatric_services = Column(JSONB, nullable=True)
    
    # Advanced treatments
    transplant_services = Column(JSONB, nullable=True)
    oncology_services = Column(JSONB, nullable=True)
    dialysis_services = Column(JSONB, nullable=True)
    
    # Home and extended care
    home_health_care = Column(JSONB, nullable=True)
    skilled_nursing = Column(JSONB, nullable=True)
    hospice_care = Column(JSONB, nullable=True)
    
    # =====================================================
    # NETWORK & PROVIDER INFORMATION
    # =====================================================
    
    network_tiers = Column(JSONB, nullable=True)
    # Example: {
    #   "tier_1": {"description": "Preferred providers", "cost_share": "lowest"},
    #   "tier_2": {"description": "Standard network", "cost_share": "moderate"},
    #   "out_of_network": {"description": "Non-contracted", "cost_share": "highest"}
    # }
    
    provider_access = Column(JSONB, nullable=True)
    # Example: {
    #   "primary_care_required": false,
    #   "referrals_required": true,
    #   "prior_auth_services": ["MRI", "CT", "surgery"],
    #   "direct_specialist_access": true
    # }
    
    geographic_coverage = Column(JSONB, nullable=True)
    # Example: {
    #   "service_area": ["TX", "OK", "AR"],
    #   "international_coverage": "emergency_only",
    #   "travel_coverage": true
    # }
    
    # =====================================================
    # EXCLUSIONS & LIMITATIONS
    # =====================================================
    
    # Major exclusions
    general_exclusions = Column(JSONB, nullable=True)
    # Example: ["cosmetic surgery", "experimental treatments", "weight loss surgery"]
    
    coverage_limitations = Column(JSONB, nullable=True)
    # Example: {
    #   "chiropractic": {"visits_per_year": 20},
    #   "acupuncture": {"visits_per_year": 12, "requires_referral": true}
    # }
    
    pre_existing_conditions = Column(JSONB, nullable=True)
    waiting_periods = Column(JSONB, nullable=True)
    
    # Age-related limitations
    age_restrictions = Column(JSONB, nullable=True)
    # Example: {
    #   "pediatric_vision": {"max_age": 18},
    #   "fertility_treatment": {"min_age": 18, "max_age": 45}
    # }
    
    # =====================================================
    # SPECIAL FEATURES & PROGRAMS
    # =====================================================
    
    # Wellness programs
    wellness_programs = Column(JSONB, nullable=True)
    # Example: {
    #   "health_screening": {"covered": "100%", "frequency": "annual"},
    #   "gym_membership": {"discount": "20%"},
    #   "smoking_cessation": {"covered": "100%", "no_limit": true}
    # }
    
    # Disease management
    disease_management = Column(JSONB, nullable=True)
    chronic_care_programs = Column(JSONB, nullable=True)
    
    # Technology features
    telemedicine = Column(JSONB, nullable=True)
    digital_tools = Column(JSONB, nullable=True)
    
    # Member resources
    member_services = Column(JSONB, nullable=True)
    customer_support = Column(JSONB, nullable=True)
    
    # =====================================================
    # REGULATORY & COMPLIANCE
    # =====================================================
    
    # ACA compliance
    essential_health_benefits = Column(Boolean, default=True)
    aca_compliant = Column(Boolean, default=True)
    
    # State compliance
    state_requirements = Column(JSONB, nullable=True)
    mandated_benefits = Column(JSONB, nullable=True)
    
    # Quality ratings
    star_rating = Column(Numeric(2, 1), nullable=True)  # 1.0 to 5.0
    quality_metrics = Column(JSONB, nullable=True)
    
    # Regulatory approvals
    regulatory_approvals = Column(JSONB, nullable=True)
    filing_references = Column(JSONB, nullable=True)
    
    # =====================================================
    # EFFECTIVE PERIODS & VERSIONING
    # =====================================================
    
    # Plan year and effective periods
    plan_year = Column(Integer, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    termination_date = Column(DateTime, nullable=True)
    
    # Open enrollment periods
    open_enrollment_start = Column(DateTime, nullable=True)
    open_enrollment_end = Column(DateTime, nullable=True)
    
    # Mid-year changes
    allows_mid_year_changes = Column(Boolean, default=False)
    qualifying_events = Column(JSONB, nullable=True)
    
    # =====================================================
    # DOCUMENT MANAGEMENT
    # =====================================================
    
    # Version control
    version = Column(String(20), nullable=False, default='1.0')
    version_effective_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    supersedes_schedule_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Document status
    approval_status = Column(String(20), default='DRAFT')
    # Options: DRAFT, PENDING_REVIEW, APPROVED, PUBLISHED, ARCHIVED, WITHDRAWN
    
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    
    # Publication information
    published_date = Column(DateTime, nullable=True)
    distribution_channels = Column(JSONB, nullable=True)
    
    # =====================================================
    # MEMBER COMMUNICATION
    # =====================================================
    
    # Summary information
    plan_summary = Column(Text, nullable=True)
    plan_highlights = Column(JSONB, nullable=True)
    
    # Marketing descriptions
    marketing_description = Column(Text, nullable=True)
    key_features = Column(JSONB, nullable=True)
    
    # Member materials
    member_handbook_url = Column(String(500), nullable=True)
    provider_directory_url = Column(String(500), nullable=True)
    formulary_url = Column(String(500), nullable=True)
    
    # Multilingual support
    available_languages = Column(JSONB, nullable=True)
    primary_language = Column(String(5), default='en')
    
    # =====================================================
    # STATUS & CONTROL
    # =====================================================
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_published = Column(Boolean, default=False, index=True)
    is_enrollable = Column(Boolean, default=True)
    
    # Availability flags
    available_individual = Column(Boolean, default=True)
    available_group = Column(Boolean, default=True)
    available_online = Column(Boolean, default=True)
    
    # =====================================================
    # METADATA & AUDIT
    # =====================================================
    
    description = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Source information
    source_system = Column(String(50), nullable=True)
    external_id = Column(String(50), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # =====================================================
    # INDEXES
    # =====================================================
    
    __table_args__ = (
        Index('idx_plan_schedules_plan', 'plan_id', 'plan_code'),
        Index('idx_plan_schedules_active_published', 'is_active', 'is_published'),
        Index('idx_plan_schedules_effective', 'effective_date', 'termination_date'),
        Index('idx_plan_schedules_plan_year', 'plan_year', 'version'),
        Index('idx_plan_schedules_type_level', 'schedule_type', 'coverage_level'),
        Index('idx_plan_schedules_market', 'market_segment', 'plan_type'),
    )
    
    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def get_benefit_for_service(self, service_type: str, network_status: str = 'in_network') -> Dict[str, Any]:
        """
        Get benefit details for a specific service type and network status.
        """
        # Map service types to benefit categories
        service_mapping = {
            'primary_care': self.medical_benefits.get('primary_care', {}) if self.medical_benefits else {},
            'specialist': self.medical_benefits.get('specialist', {}) if self.medical_benefits else {},
            'hospital_inpatient': self.hospital_inpatient or {},
            'hospital_outpatient': self.hospital_outpatient or {},
            'emergency': self.emergency_services or {},
            'urgent_care': self.urgent_care or {},
            'lab': self.lab_services or {},
            'radiology': self.radiology_services or {},
            'prescription_generic': self.prescription_benefits.get('generic', {}) if self.prescription_benefits else {},
            'prescription_brand': self.prescription_benefits.get('brand_preferred', {}) if self.prescription_benefits else {},
        }
        
        benefit_details = service_mapping.get(service_type, {})
        
        if not benefit_details:
            return {'covered': False, 'reason': 'Service not found in benefit schedule'}
        
        # Get network-specific benefit
        network_key = f"{network_status}_network" if network_status != 'in_network' else 'in_network'
        
        benefit = benefit_details.get(network_key, benefit_details.get('in_network', {}))
        
        return {
            'covered': True,
            'benefit_details': benefit,
            'service_type': service_type,
            'network_status': network_status,
            'deductible_applies': benefit.get('deductible_applies', True),
            'prior_auth_required': benefit.get('prior_auth_required', False)
        }
    
    def calculate_member_cost(
        self, 
        service_cost: Decimal, 
        service_type: str,
        network_status: str = 'in_network',
        deductible_met: Decimal = Decimal('0'),
        oop_met: Decimal = Decimal('0')
    ) -> Dict[str, Any]:
        """
        Calculate member's cost for a service based on the benefit schedule.
        """
        service_cost = Decimal(str(service_cost))
        deductible_met = Decimal(str(deductible_met))
        oop_met = Decimal(str(oop_met))
        
        # Get benefit details
        benefit = self.get_benefit_for_service(service_type, network_status)
        if not benefit['covered']:
            return {
                'total_cost': service_cost,
                'member_pays': service_cost,
                'insurance_pays': Decimal('0'),
                'covered': False
            }
        
        benefit_details = benefit['benefit_details']
        
        # Determine applicable deductible
        if network_status == 'in_network':
            deductible = Decimal(str(self.in_network_deductible or self.annual_deductible_individual or 0))
            oop_max = Decimal(str(self.in_network_oop_max or self.out_of_pocket_max_individual or 0))
        else:
            deductible = Decimal(str(self.out_of_network_deductible or 0))
            oop_max = Decimal(str(self.out_of_network_oop_max or 0))
        
        member_cost = Decimal('0')
        insurance_pays = Decimal('0')
        
        # Apply deductible if required
        if benefit_details.get('deductible_applies', True) and deductible > deductible_met:
            remaining_deductible = deductible - deductible_met
            deductible_amount = min(service_cost, remaining_deductible)
            member_cost += deductible_amount
            service_cost -= deductible_amount
        
        # Apply copay or coinsurance to remaining amount
        if service_cost > 0:
            benefit_value = benefit_details.get('copay') or benefit_details.get('coinsurance')
            
            if isinstance(benefit_value, str):
                if '$' in benefit_value:
                    # Fixed copay
                    copay = Decimal(benefit_value.replace('$', '').replace(',', ''))
                    member_cost += min(copay, service_cost)
                    insurance_pays = service_cost - min(copay, service_cost)
                elif '%' in benefit_value:
                    # Coinsurance
                    if 'after deductible' in benefit_value:
                        rate_str = benefit_value.split('%')[0]
                        rate = Decimal(rate_str) / 100
                        member_coinsurance = service_cost * (1 - rate)
                        member_cost += member_coinsurance
                        insurance_pays = service_cost * rate
                    else:
                        # Member pays percentage
                        rate_str = benefit_value.split('%')[0] 
                        rate = Decimal(rate_str) / 100
                        member_coinsurance = service_cost * rate
                        member_cost += member_coinsurance
                        insurance_pays = service_cost - member_coinsurance
        
        # Apply out-of-pocket maximum
        if oop_max > 0:
            remaining_oop = max(Decimal('0'), oop_max - oop_met)
            if member_cost > remaining_oop:
                excess = member_cost - remaining_oop
                member_cost = remaining_oop
                insurance_pays += excess
        
        return {
            'total_cost': Decimal(str(service_cost)) + member_cost + insurance_pays,
            'member_pays': member_cost,
            'insurance_pays': insurance_pays,
            'covered': True,
            'benefit_applied': benefit_details
        }
    
    def is_service_covered(self, service_type: str, network_status: str = 'in_network') -> bool:
        """Check if a service type is covered under this plan"""
        benefit = self.get_benefit_for_service(service_type, network_status)
        return benefit['covered']
    
    def requires_prior_authorization(self, service_type: str) -> bool:
        """Check if a service requires prior authorization"""
        benefit = self.get_benefit_for_service(service_type)
        if benefit['covered']:
            return benefit['benefit_details'].get('prior_auth_required', False)
        return False
    
    def get_plan_summary(self) -> Dict[str, Any]:
        """Get a summary of key plan features"""
        return {
            'schedule_name': self.schedule_name,
            'plan_type': self.plan_type,
            'coverage_level': self.coverage_level,
            'metal_tier': self.metal_tier,
            'deductible_individual': self.annual_deductible_individual,
            'deductible_family': self.annual_deductible_family,
            'oop_max_individual': self.out_of_pocket_max_individual,
            'oop_max_family': self.out_of_pocket_max_family,
            'plan_year': self.plan_year,
            'is_enrollable': self.is_enrollable,
            'key_features': self.key_features
        }
    
    def is_effective_for_date(self, check_date: datetime = None) -> bool:
        """Check if schedule is effective for a specific date"""
        if not check_date:
            check_date = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if check_date < self.effective_date:
            return False
        
        if self.termination_date and check_date > self.termination_date:
            return False
        
        return True
    
    def __repr__(self):
        return f"<PlanBenefitSchedule(id={self.id}, code='{self.schedule_code}', plan='{self.plan_name}')>"