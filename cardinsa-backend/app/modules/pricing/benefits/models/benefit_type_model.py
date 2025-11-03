# app/modules/benefits/models/benefit_type_model.py

"""
Benefit Type Model - File #2

Defines specific types of benefits within categories.
While categories are broad (like "Medical Services"), benefit types are specific 
(like "Doctor Visit", "Hospital Stay", "Surgery").

Examples within Medical Services category:
- Outpatient Visit (doctor appointments)
- Inpatient Care (hospital stays)
- Emergency Room Visit
- Diagnostic Tests (X-rays, blood tests)
- Preventive Care (checkups, screenings)

This creates the relationship: Category > Benefit Type > Coverage
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, Index, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime
from enum import Enum
import uuid


class ServiceType(str, Enum):
    """Types of services for benefit classification"""
    PREVENTIVE = "preventive"         # Preventive care (checkups, screenings)
    DIAGNOSTIC = "diagnostic"         # Tests and diagnostics
    TREATMENT = "treatment"           # Active treatment and procedures
    EMERGENCY = "emergency"           # Emergency services
    CONSULTATION = "consultation"     # Consultations and evaluations
    THERAPY = "therapy"              # Physical, occupational therapy
    SURGERY = "surgery"              # Surgical procedures
    MEDICATION = "medication"        # Prescription drugs
    EQUIPMENT = "equipment"          # Medical equipment and devices
    TRANSPORT = "transport"          # Medical transportation


class AuthorizationType(str, Enum):
    """Types of authorization required"""
    NONE = "none"                    # No authorization needed
    NOTIFICATION = "notification"     # Notify insurer only
    PRIOR_AUTH = "prior_auth"        # Must get approval first
    CONCURRENT = "concurrent"        # Review during service
    RETROSPECTIVE = "retrospective"   # Review after service
    EMERGENCY_ONLY = "emergency_only" # Only in emergencies


class CostSharingType(str, Enum):
    """Types of cost sharing mechanisms"""
    COPAY = "copay"                      # Fixed amount paid by member
    COINSURANCE = "coinsurance"          # Percentage of cost paid by member
    DEDUCTIBLE = "deductible"            # Amount member pays before coverage kicks in
    OUT_OF_POCKET_MAX = "out_of_pocket_max"  # Maximum member pays in a period
    COPAY_AFTER_DEDUCTIBLE = "copay_after_deductible"  # Copay applies after deductible met
    COINSURANCE_AFTER_DEDUCTIBLE = "coinsurance_after_deductible"  # Coinsurance after deductible
    NO_COST_SHARING = "no_cost_sharing"  # No member cost sharing
    FLAT_BENEFIT = "flat_benefit"        # Insurance pays fixed amount
    PERCENTAGE_BENEFIT = "percentage_benefit"  # Insurance pays percentage


class NetworkTier(str, Enum):
    """Provider network tiers"""
    TIER_1 = "tier_1"                   # Preferred/lowest cost providers
    TIER_2 = "tier_2"                   # Standard network providers
    TIER_3 = "tier_3"                   # Non-preferred network providers
    TIER_4 = "tier_4"                   # Specialty/highest cost providers
    IN_NETWORK = "in_network"           # General in-network
    OUT_OF_NETWORK = "out_of_network"   # Out-of-network providers
    CENTER_OF_EXCELLENCE = "center_of_excellence"  # Designated specialty centers
    PREFERRED = "preferred"             # Preferred providers
    STANDARD = "standard"               # Standard network
    NON_PREFERRED = "non_preferred"     # Non-preferred but still in network


class CoverageLevel(str, Enum):
    """Coverage levels for benefit types"""
    BASIC = "basic"                     # Basic coverage level
    STANDARD = "standard"               # Standard coverage level  
    ENHANCED = "enhanced"               # Enhanced coverage level
    PREMIUM = "premium"                 # Premium coverage level
    COMPREHENSIVE = "comprehensive"     # Comprehensive coverage level
    MINIMAL = "minimal"                 # Minimal coverage level
    DELUXE = "deluxe"                  # Deluxe coverage level
    ULTIMATE = "ultimate"               # Ultimate coverage level


class BenefitType(Base):
    """
    Benefit Type Model
    
    Defines specific types of benefits that can be offered within categories.
    This is the middle layer: Category > Benefit Type > Coverage
    
    Real-world examples:
    - Category: "Medical Services" > Type: "Outpatient Visit" > Coverage: "General Practitioner Visit"
    - Category: "Dental Care" > Type: "Preventive" > Coverage: "Teeth Cleaning"
    - Category: "Vision Care" > Type: "Corrective" > Coverage: "Prescription Glasses"
    """
    
    __tablename__ = "benefit_types"
    
    __table_args__ = (
        # Indexes for performance
        Index('idx_benefit_types_code', 'type_code'),
        Index('idx_benefit_types_category', 'category_id'),
        Index('idx_benefit_types_service', 'service_type'),
        Index('idx_benefit_types_active', 'is_active'),
        Index('idx_benefit_types_order', 'display_order'),
        
        # Composite indexes
        Index('idx_benefit_types_category_active', 'category_id', 'is_active'),
        Index('idx_benefit_types_service_active', 'service_type', 'is_active'),
        Index('idx_benefit_types_category_order', 'category_id', 'display_order'),
    )
    
    # ================================================================
    # PRIMARY IDENTIFICATION
    # ================================================================
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the benefit type"
    )
    
    type_code = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="Unique code for the benefit type (e.g., 'OUT_VISIT', 'DENTAL_CLEAN')"
    )
    
    # ================================================================
    # BASIC INFORMATION
    # ================================================================
    
    type_name = Column(
        String(200),
        nullable=False,
        comment="Benefit type name in English (e.g., 'Outpatient Visit')"
    )
    
    type_name_ar = Column(
        String(200),
        nullable=True,
        comment="Benefit type name in Arabic"
    )
    
    type_name_fr = Column(
        String(200),
        nullable=True,
        comment="Benefit type name in French"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed description of this benefit type"
    )
    
    description_ar = Column(
        Text,
        nullable=True,
        comment="Description in Arabic"
    )
    
    short_description = Column(
        String(500),
        nullable=True,
        comment="Brief description for UI displays"
    )
    
    # ================================================================
    # CLASSIFICATION AND RELATIONSHIPS
    # ================================================================
    
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("benefit_categories.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to parent benefit category"
    )
    
    service_type = Column(
        String(50),
        nullable=False,
        default=ServiceType.TREATMENT.value,
        comment="Type of service this benefit provides"
    )
    
    coverage_level = Column(
        String(20),
        nullable=True,
        comment="Coverage level for this benefit type"
    )
    
    # ================================================================
    # COST SHARING CONFIGURATION
    # ================================================================
    
    default_cost_sharing_type = Column(
        String(30),
        nullable=True,
        comment="Default cost sharing mechanism for this benefit type"
    )
    
    network_tier_preference = Column(
        String(30),
        nullable=True,
        comment="Preferred network tier for this benefit type"
    )
    
    # ================================================================
    # DISPLAY AND ORGANIZATION
    # ================================================================
    
    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Order for displaying benefit types within category"
    )
    
    icon_name = Column(
        String(100),
        nullable=True,
        comment="Icon identifier for UI display"
    )
    
    color_code = Column(
        String(7),
        nullable=True,
        comment="Hex color code for UI theming"
    )
    
    # ================================================================
    # STATUS AND AVAILABILITY
    # ================================================================
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this benefit type is currently active"
    )
    
    is_visible = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this benefit type should be shown to users"
    )
    
    is_popular = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this is a commonly used benefit type"
    )
    
    # ================================================================
    # AUTHORIZATION AND REQUIREMENTS
    # ================================================================
    
    authorization_type = Column(
        String(30),
        nullable=False,
        default=AuthorizationType.NONE.value,
        comment="Type of authorization required for this benefit"
    )
    
    requires_referral = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this benefit requires a referral"
    )
    
    requires_pre_cert = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this benefit requires pre-certification"
    )
    
    network_requirement = Column(
        String(20),
        nullable=False,
        default="preferred",
        comment="Network requirement: required, preferred, none"
    )
    
    # ================================================================
    # DEFAULT FINANCIAL PARAMETERS
    # ================================================================
    # These serve as defaults for coverages of this type
    
    default_copay_amount = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Default copayment amount for this benefit type"
    )
    
    default_copay_percentage = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Default copayment percentage"
    )
    
    default_deductible = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Default deductible amount"
    )
    
    default_annual_limit = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Default annual limit"
    )
    
    # ================================================================
    # UTILIZATION PATTERNS
    # ================================================================
    
    typical_frequency = Column(
        String(20),
        nullable=True,
        comment="Typical usage frequency (daily, weekly, monthly, yearly)"
    )
    
    seasonal_pattern = Column(
        String(50),
        nullable=True,
        comment="Seasonal usage pattern if applicable"
    )
    
    average_cost_range = Column(
        JSONB,
        nullable=True,
        comment="Typical cost range for this benefit type"
    )
    
    # ================================================================
    # CLINICAL AND REGULATORY
    # ================================================================
    
    clinical_category = Column(
        String(100),
        nullable=True,
        comment="Clinical classification of this benefit"
    )
    
    regulatory_codes = Column(
        JSONB,
        nullable=True,
        comment="Associated regulatory and billing codes"
    )
    
    icd10_categories = Column(
        JSONB,
        nullable=True,
        comment="Relevant ICD-10 diagnosis categories"
    )
    
    cpt_code_ranges = Column(
        JSONB,
        nullable=True,
        comment="Relevant CPT code ranges"
    )
    
    # ================================================================
    # BUSINESS RULES AND CONSTRAINTS
    # ================================================================
    
    age_restrictions = Column(
        JSONB,
        nullable=True,
        comment="Age-based restrictions and requirements"
    )
    
    gender_restrictions = Column(
        String(10),
        nullable=True,
        comment="Gender restrictions (M, F, null=both)"
    )
    
    eligibility_criteria = Column(
        JSONB,
        nullable=True,
        comment="Specific eligibility criteria for this benefit type"
    )
    
    exclusion_conditions = Column(
        JSONB,
        nullable=True,
        comment="Conditions that exclude this benefit"
    )
    
    # ================================================================
    # PROVIDER REQUIREMENTS
    # ================================================================
    
    required_provider_types = Column(
        JSONB,
        nullable=True,
        comment="Types of providers who can deliver this benefit"
    )
    
    required_specialties = Column(
        JSONB,
        nullable=True,
        comment="Required medical specialties"
    )
    
    facility_requirements = Column(
        JSONB,
        nullable=True,
        comment="Facility or equipment requirements"
    )
    
    # ================================================================
    # QUALITY AND OUTCOMES
    # ================================================================
    
    quality_measures = Column(
        JSONB,
        nullable=True,
        comment="Quality metrics and benchmarks"
    )
    
    outcome_tracking = Column(
        JSONB,
        nullable=True,
        comment="Outcomes to track for this benefit type"
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
    
    benefit_metadata = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional metadata and configuration"
    )
    
    business_rules = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Benefit type-specific business rules"
    )
    
    # ================================================================
    # AUDIT FIELDS
    # ================================================================
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When this benefit type was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="When this benefit type was last updated"
    )
    
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created this benefit type"
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who last updated this benefit type"
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
    
    # Relationship to parent category
    category = relationship(
        "BenefitCategory",
        back_populates="benefit_types"
    )
    
    # Relationship to coverages of this type
    coverages = relationship(
        "Coverage",
        back_populates="benefit_type",
        cascade="all, delete-orphan"
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('service_type')
    def validate_service_type(self, key, value):
        """Ensure service type is valid"""
        if value not in [e.value for e in ServiceType]:
            raise ValueError(f"Invalid service type: {value}")
        return value
    
    @validates('authorization_type')
    def validate_authorization_type(self, key, value):
        """Ensure authorization type is valid"""
        if value not in [e.value for e in AuthorizationType]:
            raise ValueError(f"Invalid authorization type: {value}")
        return value
    
    @validates('default_cost_sharing_type')
    def validate_cost_sharing_type(self, key, value):
        """Ensure cost sharing type is valid"""
        if value and value not in [e.value for e in CostSharingType]:
            raise ValueError(f"Invalid cost sharing type: {value}")
        return value

    @validates('network_tier_preference') 
    def validate_network_tier(self, key, value):
        """Ensure network tier is valid"""
        if value and value not in [e.value for e in NetworkTier]:
            raise ValueError(f"Invalid network tier: {value}")
        return value
    
    @validates('network_requirement')
    def validate_network_requirement(self, key, value):
        """Ensure network requirement is valid"""
        valid_values = ['required', 'preferred', 'none']
        if value not in valid_values:
            raise ValueError(f"Invalid network requirement: {value}. Must be one of: {valid_values}")
        return value
    
    @validates('type_code')
    def validate_type_code(self, key, value):
        """Ensure benefit type code is properly formatted"""
        if not value or not value.strip():
            raise ValueError("Benefit type code cannot be empty")
        
        # Convert to uppercase and remove spaces
        value = value.strip().upper()
        
        # Check length
        if len(value) > 50:
            raise ValueError("Benefit type code cannot exceed 50 characters")
        
        return value
    
    @validates('coverage_level')
    def validate_coverage_level(self, key, value):
        """Ensure coverage level is valid"""
        if value and value not in [e.value for e in CoverageLevel]:
            raise ValueError(f"Invalid coverage level: {value}")
        return value
        
    # ================================================================
    # BUSINESS METHODS
    # ================================================================
    
    def get_full_classification(self) -> str:
        """Get full classification path: Category > Benefit Type"""
        if self.category:
            return f"{self.category.category_name} > {self.type_name}"
        return self.type_name
    
    def is_authorization_required(self) -> bool:
        """Check if any form of authorization is required"""
        return self.authorization_type != AuthorizationType.NONE.value
    
    def get_default_cost_sharing(self) -> Dict[str, Optional[Decimal]]:
        """Get default cost sharing parameters"""
        return {
            'copay_amount': self.default_copay_amount,
            'copay_percentage': self.default_copay_percentage,
            'deductible': self.default_deductible,
            'annual_limit': self.default_annual_limit
        }
    
    def check_age_eligibility(self, age: int) -> bool:
        """Check if age meets requirements for this benefit type"""
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
        """Check if gender meets requirements for this benefit type"""
        if not self.gender_restrictions:
            return True
        
        return gender.upper() == self.gender_restrictions.upper()
    
    def get_required_authorizations(self) -> List[str]:
        """Get list of authorization types required"""
        authorizations = []
        
        if self.authorization_type != AuthorizationType.NONE.value:
            authorizations.append(self.authorization_type)
        
        if self.requires_referral:
            authorizations.append('referral')
        
        if self.requires_pre_cert:
            authorizations.append('pre_certification')
        
        return authorizations
    
    def to_dict(self, include_defaults: bool = True) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        result = {
            'id': str(self.id),
            'type_code': self.type_code,
            'type_name': self.type_name,
            'type_name_ar': self.type_name_ar,
            'type_name_fr': self.type_name_fr,
            'description': self.description,
            'short_description': self.short_description,
            'category_id': str(self.category_id),
            'service_type': self.service_type,
            'coverage_level': self.coverage_level,
            'default_cost_sharing_type': self.default_cost_sharing_type,
            'network_tier_preference': self.network_tier_preference,
            'display_order': self.display_order,
            'icon_name': self.icon_name,
            'color_code': self.color_code,
            'is_active': self.is_active,
            'is_visible': self.is_visible,
            'is_popular': self.is_popular,
            'authorization_type': self.authorization_type,
            'requires_referral': self.requires_referral,
            'requires_pre_cert': self.requires_pre_cert,
            'network_requirement': self.network_requirement,
            'typical_frequency': self.typical_frequency,
            'clinical_category': self.clinical_category,
            'full_classification': self.get_full_classification(),
            'authorization_required': self.is_authorization_required(),
            'required_authorizations': self.get_required_authorizations(),
            'tags': self.tags,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_defaults:
            result['default_cost_sharing'] = self.get_default_cost_sharing()
        
        return result
    
    def __repr__(self) -> str:
        return f"<BenefitType(id={self.id}, code='{self.type_code}', name='{self.type_name}', service='{self.service_type}')>"
    
    def __str__(self) -> str:
        return f"{self.type_code}: {self.get_full_classification()}"


# ================================================================
# EXAMPLE USAGE AND COMMON PATTERNS
# ================================================================

"""
Common Benefit Type Examples:

1. MEDICAL SERVICES CATEGORY:
   - Outpatient Visit (OUT_VISIT) - Consultations
   - Inpatient Care (INP_CARE) - Hospital stays
   - Emergency Room (ER_VISIT) - Emergency services
   - Diagnostic Tests (DIAG_TEST) - Lab tests, imaging
   - Preventive Care (PREV_CARE) - Checkups, screenings
   - Surgery (SURGERY) - Surgical procedures

2. DENTAL CARE CATEGORY:
   - Preventive (DENT_PREV) - Cleanings, exams
   - Basic Restorative (DENT_BASIC) - Fillings, extractions
   - Major Restorative (DENT_MAJOR) - Crowns, bridges
   - Orthodontics (DENT_ORTHO) - Braces, aligners

3. BUSINESS RULES EXAMPLES:
   Age Restrictions:
   {
       "min_age": 0,
       "max_age": 18,
       "pediatric_only": true
   }
   
   Provider Requirements:
   {
       "specialties": ["cardiology", "internal_medicine"],
       "facility_types": ["hospital", "cardiac_center"]
   }
   
   Average Cost Range:
   {
       "min_cost": 100.00,
       "max_cost": 500.00,
       "currency": "USD",
       "region": "UAE"
   }
"""