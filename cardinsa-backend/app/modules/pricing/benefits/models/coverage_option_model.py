# app/modules/benefits/models/coverage_option_model.py

"""
Coverage Option Model - File #4

Defines variants and alternatives within coverages.
While Coverage defines the main benefit, CoverageOption defines different ways 
to deliver that benefit with varying terms, costs, and conditions.

Examples:
- Coverage: "Prescription Eyeglasses"
  - Option 1: "Basic Frames" ($100 allowance)
  - Option 2: "Designer Frames" ($200 allowance, $50 extra copay)
  - Option 3: "Premium Frames" ($300 allowance, $100 extra copay)

- Coverage: "Physical Therapy"
  - Option 1: "Standard PT" (12 sessions per year)
  - Option 2: "Extended PT" (24 sessions per year, higher copay)
  - Option 3: "Specialized PT" (Specific conditions, prior auth required)
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


class OptionType(str, Enum):
    """Types of coverage options"""
    STANDARD = "standard"           # Standard/default option
    ENHANCED = "enhanced"           # Enhanced version with better benefits
    PREMIUM = "premium"             # Premium version with best benefits
    BASIC = "basic"                # Basic/minimal version
    ALTERNATIVE = "alternative"     # Alternative delivery method
    CONDITIONAL = "conditional"     # Available under specific conditions
    GEOGRAPHIC = "geographic"       # Geographic variant
    PROVIDER_SPECIFIC = "provider_specific"  # Specific to certain providers


class OptionStatus(str, Enum):
    """Status of coverage option"""
    ACTIVE = "active"               # Currently available
    INACTIVE = "inactive"           # Temporarily unavailable
    PENDING = "pending"             # Awaiting activation
    DEPRECATED = "deprecated"       # Being phased out
    SEASONAL = "seasonal"           # Available seasonally


class CostModifier(str, Enum):
    """How this option modifies the base coverage cost"""
    NONE = "none"                   # No cost change
    FIXED_INCREASE = "fixed_increase"    # Add fixed amount
    FIXED_DECREASE = "fixed_decrease"    # Subtract fixed amount
    PERCENTAGE_INCREASE = "percentage_increase"  # Increase by percentage
    PERCENTAGE_DECREASE = "percentage_decrease"  # Decrease by percentage
    REPLACE = "replace"             # Replace base cost entirely


class CoverageOption(Base):
    """
    Coverage Option Model
    
    Represents different ways to deliver a coverage with varying terms.
    This allows flexibility within coverages - same benefit, different delivery options.
    
    Real-world examples:
    1. Eyeglasses Coverage:
       - Basic Frames ($100 allowance)
       - Designer Frames ($200 allowance + $50 copay)
       - Premium Frames ($300 allowance + $100 copay)
    
    2. Physical Therapy:
       - Standard (12 sessions/year, $30 copay)
       - Extended (24 sessions/year, $40 copay)
       - Specialized (Unlimited for specific conditions, prior auth)
    """
    
    __tablename__ = "coverage_options"
    
    __table_args__ = (
        # Indexes for performance
        Index('idx_coverage_options_coverage', 'coverage_id'),
        Index('idx_coverage_options_code', 'option_code'),
        Index('idx_coverage_options_type', 'option_type'),
        Index('idx_coverage_options_status', 'status'),
        Index('idx_coverage_options_active', 'is_active'),
        
        # Composite indexes
        Index('idx_coverage_options_coverage_active', 'coverage_id', 'is_active'),
        Index('idx_coverage_options_coverage_type', 'coverage_id', 'option_type'),
        Index('idx_coverage_options_coverage_order', 'coverage_id', 'display_order'),
    )
    
    # ================================================================
    # PRIMARY IDENTIFICATION
    # ================================================================
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the coverage option"
    )
    
    option_code = Column(
        String(50),
        nullable=False,
        comment="Unique code for this option (e.g., 'BASIC_FRAMES', 'EXTENDED_PT')"
    )
    
    # ================================================================
    # PARENT RELATIONSHIP
    # ================================================================
    
    coverage_id = Column(
        UUID(as_uuid=True),
        ForeignKey("coverages.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to parent coverage"
    )
    
    # ================================================================
    # BASIC INFORMATION
    # ================================================================
    
    option_name = Column(
        String(200),
        nullable=False,
        comment="Option name in English"
    )
    
    option_name_ar = Column(
        String(200),
        nullable=True,
        comment="Option name in Arabic"
    )
    
    option_name_fr = Column(
        String(200),
        nullable=True,
        comment="Option name in French"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed description of this option"
    )
    
    description_ar = Column(
        Text,
        nullable=True,
        comment="Description in Arabic"
    )
    
    short_description = Column(
        String(500),
        nullable=True,
        comment="Brief description for displays"
    )
    
    member_benefit_summary = Column(
        Text,
        nullable=True,
        comment="Simple explanation of what member gets with this option"
    )
    
    # ================================================================
    # OPTION CLASSIFICATION
    # ================================================================
    
    option_type = Column(
        String(30),
        nullable=False,
        default=OptionType.STANDARD.value,
        comment="Type of option (standard, enhanced, premium, etc.)"
    )
    
    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this is the default option for the coverage"
    )
    
    is_recommended = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this option is recommended"
    )
    
    # ================================================================
    # DISPLAY AND ORGANIZATION
    # ================================================================
    
    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Order for displaying options within coverage"
    )
    
    display_priority = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Priority for highlighting (higher = more prominent)"
    )
    
    badge_text = Column(
        String(50),
        nullable=True,
        comment="Badge text to display (e.g., 'Most Popular', 'Best Value')"
    )
    
    icon_name = Column(
        String(100),
        nullable=True,
        comment="Icon identifier for UI display"
    )
    
    color_theme = Column(
        String(20),
        nullable=True,
        comment="Color theme for UI (primary, secondary, success, etc.)"
    )
    
    # ================================================================
    # STATUS AND AVAILABILITY
    # ================================================================
    
    status = Column(
        String(20),
        nullable=False,
        default=OptionStatus.ACTIVE.value,
        comment="Current status of the option"
    )
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether option is currently active"
    )
    
    is_available = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether option is available for selection"
    )
    
    availability_start_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When this option becomes available"
    )
    
    availability_end_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When this option is no longer available"
    )
    
    # ================================================================
    # COST MODIFICATIONS
    # ================================================================
    
    cost_modifier_type = Column(
        String(30),
        nullable=False,
        default=CostModifier.NONE.value,
        comment="How this option modifies the base coverage cost"
    )
    
    cost_modifier_amount = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Fixed amount to add/subtract from base cost"
    )
    
    cost_modifier_percentage = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentage to increase/decrease base cost"
    )
    
    # Override specific cost components
    override_copay = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Override copay amount for this option"
    )
    
    override_copay_percentage = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Override copay percentage for this option"
    )
    
    override_deductible = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Override deductible for this option"
    )
    
    override_coinsurance = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Override coinsurance percentage for this option"
    )
    
    # ================================================================
    # BENEFIT MODIFICATIONS
    # ================================================================
    
    # Override coverage limits
    override_limit_amount = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Override coverage limit for this option"
    )
    
    override_frequency_limit = Column(
        Integer,
        nullable=True,
        comment="Override frequency limit for this option"
    )
    
    override_max_visits = Column(
        Integer,
        nullable=True,
        comment="Override maximum visits for this option"
    )
    
    # Additional benefits
    additional_benefits = Column(
        JSONB,
        nullable=True,
        comment="Additional benefits included with this option"
    )
    
    benefit_enhancements = Column(
        JSONB,
        nullable=True,
        comment="Enhancements over base coverage"
    )
    
    # ================================================================
    # ACCESS AND AUTHORIZATION MODIFICATIONS
    # ================================================================
    
    override_authorization_required = Column(
        Boolean,
        nullable=True,
        comment="Override authorization requirement (null = inherit from base)"
    )
    
    override_referral_required = Column(
        Boolean,
        nullable=True,
        comment="Override referral requirement (null = inherit from base)"
    )
    
    override_network_required = Column(
        Boolean,
        nullable=True,
        comment="Override network requirement (null = inherit from base)"
    )
    
    additional_authorization_requirements = Column(
        JSONB,
        nullable=True,
        comment="Additional authorization requirements for this option"
    )
    
    # ================================================================
    # ELIGIBILITY AND RESTRICTIONS
    # ================================================================
    
    eligibility_requirements = Column(
        JSONB,
        nullable=True,
        comment="Specific requirements to access this option"
    )
    
    age_restrictions = Column(
        JSONB,
        nullable=True,
        comment="Age-based restrictions for this option"
    )
    
    medical_conditions_required = Column(
        JSONB,
        nullable=True,
        comment="Medical conditions required to access this option"
    )
    
    geographic_restrictions = Column(
        JSONB,
        nullable=True,
        comment="Geographic limitations for this option"
    )
    
    provider_restrictions = Column(
        JSONB,
        nullable=True,
        comment="Provider or facility restrictions"
    )
    
    # ================================================================
    # PROVIDER AND NETWORK
    # ================================================================
    
    preferred_providers = Column(
        JSONB,
        nullable=True,
        comment="List of preferred providers for this option"
    )
    
    exclusive_providers = Column(
        JSONB,
        nullable=True,
        comment="Providers exclusively available for this option"
    )
    
    network_tier_overrides = Column(
        JSONB,
        nullable=True,
        comment="Network tier configurations specific to this option"
    )
    
    # ================================================================
    # MEMBER EXPERIENCE
    # ================================================================
    
    member_instructions = Column(
        Text,
        nullable=True,
        comment="Special instructions for members choosing this option"
    )
    
    claim_process_notes = Column(
        Text,
        nullable=True,
        comment="Special claim process notes for this option"
    )
    
    member_guide_url = Column(
        String(500),
        nullable=True,
        comment="URL to specific guide for this option"
    )
    
    booking_instructions = Column(
        Text,
        nullable=True,
        comment="Instructions for booking/scheduling with this option"
    )
    
    # ================================================================
    # BUSINESS RULES
    # ================================================================
    
    business_rules = Column(
        JSONB,
        nullable=True,
        comment="Option-specific business rules"
    )
    
    combination_rules = Column(
        JSONB,
        nullable=True,
        comment="Rules for combining with other coverage options"
    )
    
    exclusion_rules = Column(
        JSONB,
        nullable=True,
        comment="What's excluded from this option specifically"
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
    
    option_metadata = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional metadata and configuration"
    )
    
    # ================================================================
    # AUDIT FIELDS
    # ================================================================
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When this option was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="When this option was last updated"
    )
    
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created this option"
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who last updated this option"
    )
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    # Parent coverage relationship
    coverage = relationship(
        "Coverage",
        back_populates="coverage_options"
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('option_type')
    def validate_option_type(self, key, value):
        """Ensure option type is valid"""
        if value not in [e.value for e in OptionType]:
            raise ValueError(f"Invalid option type: {value}")
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        """Ensure status is valid"""
        if value not in [e.value for e in OptionStatus]:
            raise ValueError(f"Invalid option status: {value}")
        return value
    
    @validates('cost_modifier_type')
    def validate_cost_modifier_type(self, key, value):
        """Ensure cost modifier type is valid"""
        if value not in [e.value for e in CostModifier]:
            raise ValueError(f"Invalid cost modifier type: {value}")
        return value
    
    @validates('option_code')
    def validate_option_code(self, key, value):
        """Ensure option code is properly formatted"""
        if not value or not value.strip():
            raise ValueError("Option code cannot be empty")
        
        # Convert to uppercase and replace spaces with underscores
        value = value.strip().upper().replace(' ', '_')
        
        # Check length
        if len(value) > 50:
            raise ValueError("Option code cannot exceed 50 characters")
        
        return value
    
    # ================================================================
    # BUSINESS METHODS
    # ================================================================
    
    def is_available_on_date(self, check_date: datetime) -> bool:
        """Check if option is available on a specific date"""
        if not self.is_active or not self.is_available:
            return False
        
        if self.availability_start_date and check_date < self.availability_start_date:
            return False
        
        if self.availability_end_date and check_date > self.availability_end_date:
            return False
        
        return True
    
    def calculate_modified_cost(self, base_cost: Decimal) -> Decimal:
        """Calculate cost after applying this option's modifiers"""
        if self.cost_modifier_type == CostModifier.NONE.value:
            return base_cost
        
        base_cost = Decimal(str(base_cost))
        
        if self.cost_modifier_type == CostModifier.FIXED_INCREASE.value:
            return base_cost + Decimal(str(self.cost_modifier_amount or 0))
        
        elif self.cost_modifier_type == CostModifier.FIXED_DECREASE.value:
            return max(Decimal('0'), base_cost - Decimal(str(self.cost_modifier_amount or 0)))
        
        elif self.cost_modifier_type == CostModifier.PERCENTAGE_INCREASE.value:
            modifier = Decimal(str(self.cost_modifier_percentage or 0)) / 100
            return base_cost * (1 + modifier)
        
        elif self.cost_modifier_type == CostModifier.PERCENTAGE_DECREASE.value:
            modifier = Decimal(str(self.cost_modifier_percentage or 0)) / 100
            return base_cost * (1 - modifier)
        
        elif self.cost_modifier_type == CostModifier.REPLACE.value:
            return Decimal(str(self.cost_modifier_amount or 0))
        
        return base_cost
    
    def get_effective_cost_sharing(self, base_coverage_cost_sharing: Dict[str, Any]) -> Dict[str, Any]:
        """Get effective cost sharing after applying option overrides"""
        result = base_coverage_cost_sharing.copy()
        
        # Apply overrides
        if self.override_copay is not None:
            result['copay'] = float(self.override_copay)
        
        if self.override_copay_percentage is not None:
            result['copay_percentage'] = float(self.override_copay_percentage)
        
        if self.override_deductible is not None:
            result['deductible'] = float(self.override_deductible)
        
        if self.override_coinsurance is not None:
            result['coinsurance'] = float(self.override_coinsurance)
        
        return result
    
    def get_effective_limits(self, base_coverage_limits: Dict[str, Any]) -> Dict[str, Any]:
        """Get effective limits after applying option overrides"""
        result = base_coverage_limits.copy()
        
        # Apply limit overrides
        if self.override_limit_amount is not None:
            result['limit_amount'] = float(self.override_limit_amount)
        
        if self.override_frequency_limit is not None:
            result['frequency_limit'] = self.override_frequency_limit
        
        if self.override_max_visits is not None:
            result['max_visits'] = self.override_max_visits
        
        return result
    
    def check_eligibility(self, member_context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if member is eligible for this option"""
        result = {
            'eligible': True,
            'reasons': [],
            'requirements_met': True
        }
        
        # Check age restrictions
        if self.age_restrictions:
            age = member_context.get('age')
            min_age = self.age_restrictions.get('min_age')
            max_age = self.age_restrictions.get('max_age')
            
            if age and min_age and age < min_age:
                result['eligible'] = False
                result['reasons'].append(f'Minimum age requirement: {min_age}')
            
            if age and max_age and age > max_age:
                result['eligible'] = False
                result['reasons'].append(f'Maximum age requirement: {max_age}')
        
        # Check medical conditions if required
        if self.medical_conditions_required:
            member_conditions = set(member_context.get('medical_conditions', []))
            required_conditions = set(self.medical_conditions_required)
            
            if not required_conditions.intersection(member_conditions):
                result['eligible'] = False
                result['reasons'].append('Required medical condition not met')
        
        # Check geographic restrictions
        if self.geographic_restrictions:
            member_location = member_context.get('location')
            allowed_locations = self.geographic_restrictions.get('allowed_regions', [])
            
            if allowed_locations and member_location not in allowed_locations:
                result['eligible'] = False
                result['reasons'].append('Geographic restriction applies')
        
        return result
    
    def get_comparison_with_base(self) -> Dict[str, Any]:
        """Get comparison highlighting differences from base coverage"""
        comparison = {
            'option_name': self.option_name,
            'option_type': self.option_type,
            'cost_differences': {},
            'benefit_differences': {},
            'access_differences': {}
        }
        
        # Cost differences
        if self.cost_modifier_type != CostModifier.NONE.value:
            comparison['cost_differences']['modifier'] = {
                'type': self.cost_modifier_type,
                'amount': float(self.cost_modifier_amount) if self.cost_modifier_amount else None,
                'percentage': float(self.cost_modifier_percentage) if self.cost_modifier_percentage else None
            }
        
        if self.override_copay is not None:
            comparison['cost_differences']['copay_override'] = float(self.override_copay)
        
        # Benefit differences
        if self.override_limit_amount is not None:
            comparison['benefit_differences']['limit_override'] = float(self.override_limit_amount)
        
        if self.additional_benefits:
            comparison['benefit_differences']['additional_benefits'] = self.additional_benefits
        
        # Access differences
        if self.override_authorization_required is not None:
            comparison['access_differences']['authorization_override'] = self.override_authorization_required
        
        if self.additional_authorization_requirements:
            comparison['access_differences']['additional_requirements'] = self.additional_authorization_requirements
        
        return comparison
    
    def to_dict(self, include_comparison: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        result = {
            'id': str(self.id),
            'option_code': self.option_code,
            'coverage_id': str(self.coverage_id),
            'option_name': self.option_name,
            'option_name_ar': self.option_name_ar,
            'option_name_fr': self.option_name_fr,
            'description': self.description,
            'short_description': self.short_description,
            'member_benefit_summary': self.member_benefit_summary,
            'option_type': self.option_type,
            'is_default': self.is_default,
            'is_recommended': self.is_recommended,
            'display_order': self.display_order,
            'display_priority': self.display_priority,
            'badge_text': self.badge_text,
            'icon_name': self.icon_name,
            'color_theme': self.color_theme,
            'status': self.status,
            'is_active': self.is_active,
            'is_available': self.is_available,
            'cost_modifier_type': self.cost_modifier_type,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_comparison:
            result['comparison_with_base'] = self.get_comparison_with_base()
        
        return result
    
    def __repr__(self) -> str:
        return f"<CoverageOption(id={self.id}, code='{self.option_code}', name='{self.option_name}', type='{self.option_type}')>"
    
    def __str__(self) -> str:
        return f"{self.option_code}: {self.option_name} ({self.option_type})"


# ================================================================
# EXAMPLE USAGE AND COMMON PATTERNS
# ================================================================

"""
Common Coverage Option Examples:

1. EYEGLASSES COVERAGE OPTIONS:
   Base Coverage: "Prescription Eyeglasses"
   - Option 1: "Basic Frames" (Standard, $100 allowance)
   - Option 2: "Designer Frames" (Enhanced, $200 allowance + $25 copay)
   - Option 3: "Premium Frames" (Premium, $300 allowance + $50 copay)

2. PHYSICAL THERAPY OPTIONS:
   Base Coverage: "Physical Therapy"
   - Option 1: "Standard PT" (Standard, 12 sessions/year, $30 copay)
   - Option 2: "Extended PT" (Enhanced, 24 sessions/year, $40 copay)
   - Option 3: "Specialized PT" (Premium, unlimited for specific conditions, prior auth)

3. DENTAL CLEANING OPTIONS:
   Base Coverage: "Teeth Cleaning"
   - Option 1: "Basic Cleaning" (Standard, 2 cleanings/year, 100% covered)
   - Option 2: "Deep Cleaning" (Enhanced, includes scaling, 80% covered)
   - Option 3: "Comprehensive Care" (Premium, includes fluoride treatment, exam)

Business Rules Examples:

Age Restrictions:
{
    "min_age": 18,
    "max_age": null,
    "pediatric_alternative": "CHILD_FRAMES_OPTION"
}

Medical Conditions Required:
["chronic_back_pain", "post_surgery_rehabilitation", "sports_injury"]

Additional Benefits:
{
    "includes": ["anti_glare_coating", "UV_protection", "scratch_resistance"],
    "value": 75.00,
    "description": "Premium lens treatments included at no extra cost"
}

Cost Modifier Examples:
- Fixed Increase: Add $25 copay for premium option
- Percentage Increase: 50% higher allowance than base
- Replace: Override base $100 allowance with $300 allowance
"""