# app/modules/benefits/models/coverage_model.py

"""
Coverage Model - File #3

Defines individual coverage benefits - the specific services that members can access.
This is the most detailed level: Category > Benefit Type > Coverage

Examples:
- Category: "Medical Services" > Type: "Outpatient Visit" > Coverage: "General Practitioner Visit"
- Category: "Dental Care" > Type: "Preventive" > Coverage: "Teeth Cleaning & Exam"
- Category: "Vision Care" > Type: "Corrective" > Coverage: "Prescription Eyeglasses"

Each coverage has specific limits, copays, deductibles, and conditions.
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, Index, DateTime, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime, date
from enum import Enum
import uuid


class CoverageStatus(str, Enum):
    """Status of coverage availability"""
    ACTIVE = "active"               # Currently available
    INACTIVE = "inactive"           # Temporarily unavailable
    DRAFT = "draft"                # Being developed
    PENDING_APPROVAL = "pending_approval"  # Awaiting approval
    DEPRECATED = "deprecated"       # Being phased out
    ARCHIVED = "archived"          # No longer available


class LimitType(str, Enum):
    """Types of coverage limits"""
    PER_VISIT = "per_visit"         # Limit per visit/service
    PER_DAY = "per_day"            # Daily limit
    PER_MONTH = "per_month"        # Monthly limit
    PER_YEAR = "per_year"          # Annual limit
    PER_LIFETIME = "per_lifetime"   # Lifetime limit
    PER_CONDITION = "per_condition" # Per medical condition
    PER_EPISODE = "per_episode"    # Per treatment episode


class PaymentType(str, Enum):
    """How payments are handled"""
    DIRECT_BILLING = "direct_billing"     # Provider bills insurer directly
    REIMBURSEMENT = "reimbursement"       # Member pays and gets reimbursed
    CASHLESS = "cashless"                 # No payment by member
    COPAY_ONLY = "copay_only"            # Member pays only copay
    HYBRID = "hybrid"                     # Mix of methods


class Coverage(Base):
    """
    Coverage Model
    
    Represents individual coverage benefits that members can access.
    This is the detailed level where specific services, limits, and costs are defined.
    
    Real-world examples:
    - "General Practitioner Office Visit" with $20 copay, no limit
    - "MRI Scan" with 80% coverage after $500 deductible, max 4 per year
    - "Dental Cleaning" with 100% coverage, maximum 2 per year
    """
    
    __tablename__ = "coverages"
    
    __table_args__ = (
        # Indexes for performance
        Index('idx_coverages_code', 'coverage_code'),
        Index('idx_coverages_category', 'category_id'),
        Index('idx_coverages_type', 'benefit_type_id'),
        Index('idx_coverages_status', 'status'),
        Index('idx_coverages_active', 'is_active'),
        Index('idx_coverages_effective', 'effective_date', 'expiry_date'),
        
        # Composite indexes
        Index('idx_coverages_category_active', 'category_id', 'is_active'),
        Index('idx_coverages_type_active', 'benefit_type_id', 'is_active'),
        Index('idx_coverages_status_active', 'status', 'is_active'),
        
        # Search indexes
        Index('idx_coverages_name', 'name'),
        Index('idx_coverages_external', 'external_code'),
    )
    
    # ================================================================
    # PRIMARY IDENTIFICATION
    # ================================================================
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the coverage"
    )
    
    coverage_code = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="Unique internal code for the coverage"
    )
    
    external_code = Column(
        String(50),
        nullable=True,
        comment="External system reference code (e.g., insurance company code)"
    )
    
    # ================================================================
    # BASIC INFORMATION
    # ================================================================
    
    name = Column(
        String(200),
        nullable=False,
        comment="Coverage name in English"
    )
    
    name_ar = Column(
        String(200),
        nullable=True,
        comment="Coverage name in Arabic"
    )
    
    name_fr = Column(
        String(200),
        nullable=True,
        comment="Coverage name in French"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed description of what this coverage includes"
    )
    
    description_ar = Column(
        Text,
        nullable=True,
        comment="Description in Arabic"
    )
    
    short_description = Column(
        String(500),
        nullable=True,
        comment="Brief description for member-facing displays"
    )
    
    member_summary = Column(
        Text,
        nullable=True,
        comment="Simple explanation for members about what's covered"
    )
    
    # ================================================================
    # CLASSIFICATION AND RELATIONSHIPS
    # ================================================================
    
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("benefit_categories.id", ondelete="SET NULL"),
        nullable=True,
        comment="Reference to benefit category"
    )
    
    benefit_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("benefit_types.id", ondelete="SET NULL"),
        nullable=True,
        comment="Reference to benefit type"
    )
    
    parent_coverage_id = Column(
        UUID(as_uuid=True),
        ForeignKey("coverages.id", ondelete="CASCADE"),
        nullable=True,
        comment="Parent coverage for hierarchical relationships"
    )
    
    # ================================================================
    # FINANCIAL PARAMETERS - CORE
    # ================================================================
    
    # Coverage amount/limit
    limit_amount = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Maximum coverage amount"
    )
    
    limit_type = Column(
        String(20),
        nullable=False,
        default=LimitType.PER_YEAR.value,
        comment="Type of limit application"
    )
    
    # Copayments
    co_payment = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Fixed copayment amount"
    )
    
    co_payment_percentage = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Copayment as percentage of service cost"
    )
    
    # Deductibles
    deductible = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Deductible amount that must be met"
    )
    
    deductible_waived = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether deductible is waived for this coverage"
    )
    
    # Coinsurance
    coinsurance_percentage = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Member's share after deductible (e.g., 20% = member pays 20%)"
    )
    
    # ================================================================
    # FINANCIAL PARAMETERS - ADVANCED
    # ================================================================
    
    out_of_pocket_max = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Maximum out-of-pocket cost for member"
    )
    
    lifetime_maximum = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Lifetime maximum coverage"
    )
    
    per_incident_limit = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Maximum coverage per incident/claim"
    )
    
    # Network-based cost sharing
    in_network_copay = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Copay when using in-network providers"
    )
    
    out_network_copay = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Copay when using out-of-network providers"
    )
    
    in_network_coinsurance = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Coinsurance percentage for in-network"
    )
    
    out_network_coinsurance = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Coinsurance percentage for out-of-network"
    )
    
    # ================================================================
    # UTILIZATION LIMITS
    # ================================================================
    
    frequency_limit = Column(
        Integer,
        nullable=True,
        comment="Number of times coverage can be used in frequency period"
    )
    
    frequency_period = Column(
        String(20),
        nullable=True,
        comment="Period for frequency limit (daily, monthly, yearly)"
    )
    
    max_visits = Column(
        Integer,
        nullable=True,
        comment="Maximum visits/services allowed"
    )
    
    visit_limit_period = Column(
        String(20),
        nullable=True,
        comment="Period for visit limit"
    )
    
    unit_type = Column(
        String(50),
        nullable=True,
        comment="Unit of measurement (per visit, per day, per procedure)"
    )
    
    # ================================================================
    # ACCESS AND AUTHORIZATION
    # ================================================================
    
    authorization_required = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether prior authorization is required"
    )
    
    referral_required = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether referral is required"
    )
    
    pre_certification_required = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether pre-certification is required"
    )
    
    emergency_override = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether authorization can be bypassed in emergencies"
    )
    
    # ================================================================
    # WAITING PERIODS
    # ================================================================
    
    waiting_period_days = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Waiting period before coverage becomes effective"
    )
    
    waiting_period_waiver_conditions = Column(
        JSONB,
        nullable=True,
        comment="Conditions under which waiting period can be waived"
    )
    
    # ================================================================
    # PROVIDER AND NETWORK
    # ================================================================
    
    network_required = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether in-network providers are required"
    )
    
    network_tiers_supported = Column(
        JSONB,
        nullable=True,
        comment="Supported network tiers and their benefits"
    )
    
    provider_specialties = Column(
        JSONB,
        nullable=True,
        comment="Required or preferred provider specialties"
    )
    
    facility_types = Column(
        JSONB,
        nullable=True,
        comment="Types of facilities where service can be provided"
    )
    
    # ================================================================
    # PAYMENT PROCESSING
    # ================================================================
    
    payment_method = Column(
        String(20),
        nullable=False,
        default=PaymentType.CASHLESS.value,
        comment="Primary payment method"
    )
    
    supports_direct_billing = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether direct billing to insurer is supported"
    )
    
    supports_reimbursement = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether reimbursement claims are supported"
    )
    
    # ================================================================
    # DATES AND STATUS
    # ================================================================
    
    effective_date = Column(
        Date,
        nullable=True,
        comment="Date when coverage becomes effective"
    )
    
    expiry_date = Column(
        Date,
        nullable=True,
        comment="Date when coverage expires"
    )
    
    status = Column(
        String(20),
        nullable=False,
        default=CoverageStatus.ACTIVE.value,
        comment="Current status of the coverage"
    )
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether coverage is currently active"
    )
    
    is_available = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether coverage is available for selection"
    )
    
    is_mandatory = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this coverage is mandatory in plans"
    )
    
    # ================================================================
    # DISPLAY AND ORGANIZATION
    # ================================================================
    
    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Order for displaying coverage in lists"
    )
    
    is_popular = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this is a popular/commonly used coverage"
    )
    
    is_featured = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether to feature this coverage prominently"
    )
    
    # ================================================================
    # REGULATORY AND COMPLIANCE
    # ================================================================
    
    regulatory_code = Column(
        String(50),
        nullable=True,
        comment="Regulatory classification code"
    )
    
    icd10_codes = Column(
        JSONB,
        nullable=True,
        comment="Associated ICD-10 diagnosis codes"
    )
    
    cpt_codes = Column(
        JSONB,
        nullable=True,
        comment="Associated CPT procedure codes"
    )
    
    hcpcs_codes = Column(
        JSONB,
        nullable=True,
        comment="Associated HCPCS codes"
    )
    
    # ================================================================
    # BUSINESS RULES
    # ================================================================
    
    eligibility_criteria = Column(
        JSONB,
        nullable=True,
        comment="Specific eligibility requirements for this coverage"
    )
    
    exclusions = Column(
        JSONB,
        nullable=True,
        comment="Conditions or situations that are excluded"
    )
    
    age_restrictions = Column(
        JSONB,
        nullable=True,
        comment="Age-based restrictions"
    )
    
    gender_restrictions = Column(
        String(10),
        nullable=True,
        comment="Gender restrictions (M, F, null=both)"
    )
    
    pre_existing_condition_rules = Column(
        JSONB,
        nullable=True,
        comment="Rules for pre-existing conditions"
    )
    
    # ================================================================
    # QUALITY AND OUTCOMES
    # ================================================================
    
    quality_measures = Column(
        JSONB,
        nullable=True,
        comment="Quality metrics and standards"
    )
    
    clinical_guidelines = Column(
        JSONB,
        nullable=True,
        comment="Clinical practice guidelines"
    )
    
    outcome_measures = Column(
        JSONB,
        nullable=True,
        comment="Expected outcomes and success metrics"
    )
    
    # ================================================================
    # MEMBER EXPERIENCE
    # ================================================================
    
    member_guide_url = Column(
        String(500),
        nullable=True,
        comment="URL to member guide for this coverage"
    )
    
    provider_directory_url = Column(
        String(500),
        nullable=True,
        comment="URL to find providers for this coverage"
    )
    
    claim_process_url = Column(
        String(500),
        nullable=True,
        comment="URL explaining claim process"
    )
    
    # ================================================================
    # METADATA
    # ================================================================
    
    tags = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Tags for categorization and searching"
    )
    
    coverage_metadata = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional metadata and configuration"
    )
    
    configuration = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Coverage-specific configuration parameters"
    )
    
    # ================================================================
    # AUDIT FIELDS
    # ================================================================
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When this coverage was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="When this coverage was last updated"
    )
    
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created this coverage"
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who last updated this coverage"
    )
    
    version = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Version number for change tracking"
    )
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    # Parent relationships
    category = relationship(
        "BenefitCategory",
        back_populates="coverages"
    )
    
    benefit_type = relationship(
        "BenefitType",
        back_populates="coverages"
    )
    
    # Hierarchical relationship
    parent_coverage = relationship(
        "Coverage",
        remote_side=[id],
        backref="child_coverages"
    )
    
    # Coverage options/variants
    coverage_options = relationship(
        "CoverageOption",
        back_populates="coverage",
        cascade="all, delete-orphan"
    )
    
    # Plan coverage links (when coverage is added to plans)
    plan_links = relationship(
        "PlanCoverageLink",
        back_populates="coverage"
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('status')
    def validate_status(self, key, value):
        """Ensure status is valid"""
        if value not in [e.value for e in CoverageStatus]:
            raise ValueError(f"Invalid coverage status: {value}")
        return value
    
    @validates('limit_type')
    def validate_limit_type(self, key, value):
        """Ensure limit type is valid"""
        if value not in [e.value for e in LimitType]:
            raise ValueError(f"Invalid limit type: {value}")
        return value
    
    @validates('payment_method')
    def validate_payment_method(self, key, value):
        """Ensure payment method is valid"""
        if value not in [e.value for e in PaymentType]:
            raise ValueError(f"Invalid payment method: {value}")
        return value
    
    @validates('coverage_code')
    def validate_coverage_code(self, key, value):
        """Ensure coverage code is properly formatted"""
        if not value or not value.strip():
            raise ValueError("Coverage code cannot be empty")
        
        # Convert to uppercase and remove spaces
        value = value.strip().upper().replace(' ', '_')
        
        # Check length
        if len(value) > 50:
            raise ValueError("Coverage code cannot exceed 50 characters")
        
        return value
    
    # ================================================================
    # BUSINESS METHODS
    # ================================================================
    
    def calculate_member_cost(
        self,
        service_cost: Decimal,
        is_in_network: bool = True,
        deductible_met: Decimal = Decimal('0'),
        out_of_pocket_met: Decimal = Decimal('0')
    ) -> Dict[str, Decimal]:
        """
        Calculate what the member pays for a service
        
        Args:
            service_cost: Total cost of the service
            is_in_network: Whether provider is in-network
            deductible_met: Amount of deductible already met this year
            out_of_pocket_met: Amount of out-of-pocket already met this year
        
        Returns:
            Dictionary with cost breakdown
        """
        
        # Determine applicable copay and coinsurance based on network
        if is_in_network:
            copay = self.in_network_copay or self.co_payment or Decimal('0')
            coinsurance_rate = self.in_network_coinsurance or self.coinsurance_percentage or Decimal('0')
        else:
            copay = self.out_network_copay or self.co_payment or Decimal('0')
            coinsurance_rate = self.out_network_coinsurance or self.coinsurance_percentage or Decimal('0')
        
        # Convert to Decimal for calculations
        copay = Decimal(str(copay)) if copay else Decimal('0')
        coinsurance_rate = Decimal(str(coinsurance_rate)) if coinsurance_rate else Decimal('0')
        service_cost = Decimal(str(service_cost))
        
        # Calculate deductible portion
        deductible_amount = Decimal(str(self.deductible)) if self.deductible and not self.deductible_waived else Decimal('0')
        remaining_deductible = max(Decimal('0'), deductible_amount - deductible_met)
        deductible_portion = min(service_cost, remaining_deductible)
        
        # Amount after deductible
        after_deductible = service_cost - deductible_portion
        
        # Apply copay (fixed amount) or coinsurance (percentage)
        if copay > 0:
            # Fixed copay
            member_share = min(copay, after_deductible)
            insurance_pays = after_deductible - member_share
        else:
            # Coinsurance
            member_share = after_deductible * (coinsurance_rate / 100)
            insurance_pays = after_deductible - member_share
        
        # Apply coverage limits
        if self.limit_amount:
            coverage_limit = Decimal(str(self.limit_amount))
            if insurance_pays > coverage_limit:
                excess = insurance_pays - coverage_limit
                insurance_pays = coverage_limit
                member_share += excess
        
        # Apply per-incident limit
        if self.per_incident_limit:
            incident_limit = Decimal(str(self.per_incident_limit))
            if insurance_pays > incident_limit:
                excess = insurance_pays - incident_limit
                insurance_pays = incident_limit
                member_share += excess
        
        # Apply out-of-pocket maximum
        total_member_cost = deductible_portion + member_share
        if self.out_of_pocket_max:
            oop_max = Decimal(str(self.out_of_pocket_max))
            remaining_oop = max(Decimal('0'), oop_max - out_of_pocket_met)
            
            if total_member_cost > remaining_oop:
                # Member has hit out-of-pocket max
                excess_covered = total_member_cost - remaining_oop
                total_member_cost = remaining_oop
                insurance_pays += excess_covered
        
        return {
            'service_cost': service_cost,
            'deductible_applied': deductible_portion,
            'copay_coinsurance': member_share,
            'total_member_pays': total_member_cost,
            'insurance_pays': insurance_pays,
            'is_in_network': is_in_network,
            'coverage_applies': insurance_pays > 0 or total_member_cost < service_cost
        }
    
    def check_utilization_limit(self, current_usage: int, period: str = None) -> bool:
        """Check if current usage is within limits"""
        if not self.frequency_limit and not self.max_visits:
            return True
        
        # Check frequency limit
        if self.frequency_limit:
            period_to_check = period or self.frequency_period
            if current_usage >= self.frequency_limit:
                return False
        
        # Check visit limit
        if self.max_visits:
            if current_usage >= self.max_visits:
                return False
        
        return True
    
    def is_effective_on_date(self, check_date: date) -> bool:
        """Check if coverage is effective on a specific date"""
        if not self.is_active or not self.is_available:
            return False
        
        if self.effective_date and check_date < self.effective_date:
            return False
        
        if self.expiry_date and check_date > self.expiry_date:
            return False
        
        return True
    
    def requires_authorization(self) -> bool:
        """Check if any form of authorization is required"""
        return (self.authorization_required or 
                self.referral_required or 
                self.pre_certification_required)
    
    def get_authorization_requirements(self) -> List[str]:
        """Get list of all authorization requirements"""
        requirements = []
        
        if self.authorization_required:
            requirements.append("prior_authorization")
        
        if self.referral_required:
            requirements.append("referral")
        
        if self.pre_certification_required:
            requirements.append("pre_certification")
        
        return requirements
    
    def check_age_eligibility(self, age: int) -> bool:
        """Check if age meets requirements for this coverage"""
        if not self.age_restrictions:
            return True
        
        min_age = self.age_restrictions.get('min_age')
        max_age = self.age_restrictions.get('max_age')
        
        if min_age and age < min_age:
            return False
        
        if max_age and age > max_age:
            return False
        
        return True
    
    def check_gender_eligibility(self, gender: str) -> bool:
        """Check if gender meets requirements for this coverage"""
        if not self.gender_restrictions:
            return True
        
        return gender.upper() == self.gender_restrictions.upper()
    
    def get_network_benefits(self) -> Dict[str, Dict[str, Any]]:
        """Get benefits breakdown by network tier"""
        return {
            'in_network': {
                'copay': float(self.in_network_copay) if self.in_network_copay else None,
                'coinsurance': float(self.in_network_coinsurance) if self.in_network_coinsurance else None,
                'deductible_waived': self.deductible_waived
            },
            'out_of_network': {
                'copay': float(self.out_network_copay) if self.out_network_copay else None,
                'coinsurance': float(self.out_network_coinsurance) if self.out_network_coinsurance else None,
                'deductible_waived': False  # Usually not waived for out-of-network
            }
        }
    
    def get_full_classification_path(self) -> str:
        """Get full classification path"""
        path_parts = []
        
        if self.category:
            path_parts.append(self.category.category_name)
        
        if self.benefit_type:
            path_parts.append(self.benefit_type.type_name)
        
        path_parts.append(self.name)
        
        return " > ".join(path_parts)
    
    def to_dict(self, include_financial: bool = True, include_rules: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        result = {
            'id': str(self.id),
            'coverage_code': self.coverage_code,
            'external_code': self.external_code,
            'name': self.name,
            'name_ar': self.name_ar,
            'name_fr': self.name_fr,
            'description': self.description,
            'short_description': self.short_description,
            'member_summary': self.member_summary,
            'category_id': str(self.category_id) if self.category_id else None,
            'benefit_type_id': str(self.benefit_type_id) if self.benefit_type_id else None,
            'parent_coverage_id': str(self.parent_coverage_id) if self.parent_coverage_id else None,
            'status': self.status,
            'is_active': self.is_active,
            'is_available': self.is_available,
            'is_mandatory': self.is_mandatory,
            'is_popular': self.is_popular,
            'is_featured': self.is_featured,
            'display_order': self.display_order,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'waiting_period_days': self.waiting_period_days,
            'authorization_required': self.requires_authorization(),
            'authorization_requirements': self.get_authorization_requirements(),
            'network_required': self.network_required,
            'supports_direct_billing': self.supports_direct_billing,
            'supports_reimbursement': self.supports_reimbursement,
            'payment_method': self.payment_method,
            'full_classification': self.get_full_classification_path(),
            'tags': self.tags,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_financial:
            result['financial_details'] = {
                'limit_amount': float(self.limit_amount) if self.limit_amount else None,
                'limit_type': self.limit_type,
                'co_payment': float(self.co_payment) if self.co_payment else None,
                'co_payment_percentage': float(self.co_payment_percentage) if self.co_payment_percentage else None,
                'deductible': float(self.deductible) if self.deductible else None,
                'deductible_waived': self.deductible_waived,
                'coinsurance_percentage': float(self.coinsurance_percentage) if self.coinsurance_percentage else None,
                'out_of_pocket_max': float(self.out_of_pocket_max) if self.out_of_pocket_max else None,
                'lifetime_maximum': float(self.lifetime_maximum) if self.lifetime_maximum else None,
                'per_incident_limit': float(self.per_incident_limit) if self.per_incident_limit else None,
                'network_benefits': self.get_network_benefits(),
                'frequency_limit': self.frequency_limit,
                'frequency_period': self.frequency_period,
                'max_visits': self.max_visits,
                'visit_limit_period': self.visit_limit_period,
                'unit_type': self.unit_type
            }
        
        if include_rules:
            result['business_rules'] = {
                'eligibility_criteria': self.eligibility_criteria,
                'exclusions': self.exclusions,
                'age_restrictions': self.age_restrictions,
                'gender_restrictions': self.gender_restrictions,
                'pre_existing_condition_rules': self.pre_existing_condition_rules,
                'waiting_period_waiver_conditions': self.waiting_period_waiver_conditions
            }
            
            result['clinical_info'] = {
                'regulatory_code': self.regulatory_code,
                'icd10_codes': self.icd10_codes,
                'cpt_codes': self.cpt_codes,
                'hcpcs_codes': self.hcpcs_codes,
                'provider_specialties': self.provider_specialties,
                'facility_types': self.facility_types
            }
        
        return result
    
    def __repr__(self) -> str:
        return f"<Coverage(id={self.id}, code='{self.coverage_code}', name='{self.name}', status='{self.status}')>"
    
    def __str__(self) -> str:
        return f"{self.coverage_code}: {self.get_full_classification_path()}"


# ================================================================
# EXAMPLE USAGE AND COMMON PATTERNS
# ================================================================

"""
Common Coverage Examples:

1. OUTPATIENT MEDICAL VISIT:
   - Name: "General Practitioner Office Visit"
   - Category: Medical Services > Outpatient Visit
   - Copay: $25 in-network, $50 out-of-network
   - No deductible, no visit limit
   - Authorization: None required

2. DIAGNOSTIC IMAGING:
   - Name: "MRI Scan"
   - Category: Medical Services > Diagnostic Tests
   - Coinsurance: 20% after deductible
   - Deductible: $500
   - Limit: 4 scans per year
   - Authorization: Prior auth required

3. DENTAL CLEANING:
   - Name: "Routine Teeth Cleaning"
   - Category: Dental Care > Preventive
   - Coverage: 100% (no member cost)
   - Limit: 2 cleanings per year
   - Waiting period: 6 months for new members

4. PRESCRIPTION GLASSES:
   - Name: "Prescription Eyeglasses"
   - Category: Vision Care > Corrective
   - Benefit: $200 allowance per year
   - Member pays difference
   - Limit: 1 pair per year

Cost Calculation Example:
- MRI costs $1,500
- Member has met $300 of $500 deductible
- Remaining deductible: $200
- After deductible: $1,300
- Member coinsurance (20%): $260
- Total member pays: $200 + $260 = $460
- Insurance pays: $1,040

Business Rules Examples:
Age Restrictions:
{
    "min_age": 18,
    "max_age": 65,
    "pediatric_version_available": true
}

Eligibility Criteria:
{
    "requires_primary_care_relationship": true,
    "pre_existing_condition_waiting_period": 12,
    "geographic_restrictions": ["UAE", "KSA"]
}
"""