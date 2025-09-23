# app/modules/pricing/modifiers/models/pricing_industry_adjustment_model.py

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
import enum
from typing import Dict, Any, Optional

from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin

class AdjustmentType(enum.Enum):
    """Industry adjustment calculation types"""
    MULTIPLIER = "multiplier"
    PERCENTAGE_INCREASE = "percentage_increase"
    PERCENTAGE_DECREASE = "percentage_decrease"
    FIXED_AMOUNT_INCREASE = "fixed_amount_increase"
    FIXED_AMOUNT_DECREASE = "fixed_amount_decrease"
    TIERED = "tiered"
    EXPERIENCE_MODIFIED = "experience_modified"

class RiskLevel(enum.Enum):
    """Industry risk classification levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXCLUDED = "excluded"

class IndustryGroup(enum.Enum):
    """Major industry groupings"""
    PROFESSIONAL_SERVICES = "professional_services"
    MANUFACTURING = "manufacturing"
    CONSTRUCTION = "construction"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    HOSPITALITY = "hospitality"
    TRANSPORTATION = "transportation"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    EDUCATION = "education"
    GOVERNMENT = "government"
    AGRICULTURE = "agriculture"
    MINING = "mining"
    UTILITIES = "utilities"
    OTHER = "other"

class PricingIndustryAdjustment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Pricing Industry Adjustment Model for Step 5 - Advanced Pricing Components
    
    This model handles industry-specific risk adjustments and loading factors
    that modify base premiums based on the client's industry characteristics.
    
    Key Features:
    - Industry-specific risk loading factors
    - NAICS code mapping and classification
    - Tiered adjustments based on company size
    - Experience modification factors
    - Seasonal adjustment factors
    - Geographic industry risk variations
    - Regulatory compliance adjustments
    - Integration with pricing profiles
    - Comprehensive audit and approval workflow
    """
    __tablename__ = "premium_industries"

    # =====================================================
    # CORE FIELDS
    # =====================================================
    
    code = Column(String(50), unique=True, nullable=False, index=True,
                 comment="Unique identifier code for the adjustment (e.g., 'CONSTRUCTION_HIGH', 'TECH_LOW')")
    
    name = Column(String(200), nullable=False,
                 comment="Industry adjustment name")
    
    description = Column(Text,
                        comment="Detailed description of industry risks and adjustment rationale")

    # =====================================================
    # INDUSTRY CLASSIFICATION
    # =====================================================
    
    industry_group = Column(Enum(IndustryGroup), nullable=False,
                           comment="Major industry grouping")
    
    naics_codes = Column(JSONB,
                        comment="JSON array of applicable NAICS codes")
    
    # Example naics_codes:
    # ["23", "236", "2362", "236220"] - Construction industry codes at different levels
    
    sic_codes = Column(JSONB,
                      comment="JSON array of applicable SIC codes (legacy support)")
    
    industry_keywords = Column(JSONB,
                              comment="JSON array of keywords for industry matching")
    
    excluded_naics_codes = Column(JSONB,
                                 comment="JSON array of NAICS codes specifically excluded")

    # =====================================================
    # RISK ASSESSMENT
    # =====================================================
    
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.MODERATE,
                       comment="Overall risk level classification")
    
    adjustment_type = Column(Enum(AdjustmentType), nullable=False, default=AdjustmentType.MULTIPLIER,
                            comment="Type of adjustment calculation")
    
    # Primary adjustment values
    adjustment_factor = Column(Numeric(8, 4), nullable=False, default=1.0000,
                              comment="Primary adjustment factor (multiplier or percentage)")
    
    fixed_amount = Column(Numeric(15, 2),
                         comment="Fixed amount adjustment")
    
    currency = Column(String(3), default="USD", nullable=False,
                     comment="ISO 3-letter currency code")

    # =====================================================
    # TIERED ADJUSTMENT STRUCTURE
    # =====================================================
    
    # JSON structure for company size-based tiered adjustments
    size_tiers = Column(JSONB,
                       comment="JSON structure defining adjustments by company size")
    
    # Example size_tiers:
    # {
    #   "tiers": [
    #     {"max_employees": 50, "adjustment_factor": 1.15, "description": "Small company higher risk"},
    #     {"max_employees": 500, "adjustment_factor": 1.05, "description": "Medium company moderate risk"},
    #     {"max_employees": 99999, "adjustment_factor": 0.95, "description": "Large company lower risk"}
    #   ],
    #   "metric": "employee_count" // or "annual_revenue", "payroll"
    # }

    # =====================================================
    # EXPERIENCE MODIFICATION
    # =====================================================
    
    uses_experience_mod = Column(Boolean, default=False,
                                comment="Whether experience modification applies")
    
    base_experience_mod = Column(Numeric(6, 4), default=1.0000,
                                comment="Base experience modification factor")
    
    experience_period_years = Column(Integer, default=3,
                                    comment="Number of years for experience calculation")
    
    min_experience_mod = Column(Numeric(6, 4), default=0.5000,
                               comment="Minimum allowed experience mod")
    
    max_experience_mod = Column(Numeric(6, 4), default=2.0000,
                               comment="Maximum allowed experience mod")

    # =====================================================
    # SEASONAL AND GEOGRAPHIC ADJUSTMENTS
    # =====================================================
    
    seasonal_adjustments = Column(JSONB,
                                 comment="JSON structure for seasonal risk variations")
    
    # Example seasonal_adjustments:
    # {
    #   "Q1": 1.10, "Q2": 0.95, "Q3": 1.05, "Q4": 1.15,
    #   "applies_to": ["construction", "agriculture"],
    #   "description": "Construction seasonal risk pattern"
    # }
    
    geographic_variations = Column(JSONB,
                                  comment="JSON structure for geographic risk variations")
    
    # Example geographic_variations:
    # {
    #   "states": {
    #     "CA": 1.20, "TX": 1.05, "FL": 1.15, "NY": 1.25
    #   },
    #   "regions": {
    #     "hurricane_zone": 1.30, "earthquake_zone": 1.25, "tornado_alley": 1.15
    #   }
    # }

    # =====================================================
    # REGULATORY AND COMPLIANCE
    # =====================================================
    
    regulatory_requirements = Column(JSONB,
                                    comment="JSON structure defining regulatory requirements")
    
    compliance_adjustments = Column(JSONB,
                                   comment="JSON structure for compliance-based adjustments")
    
    # Example compliance_adjustments:
    # {
    #   "safety_program_discount": -0.05,
    #   "certification_discount": -0.03,
    #   "violation_penalty": 0.15,
    #   "required_coverages": ["workers_comp", "general_liability"]
    # }

    # =====================================================
    # BUSINESS RULES AND LIMITS
    # =====================================================
    
    min_premium_threshold = Column(Numeric(15, 2),
                                  comment="Minimum premium amount for this adjustment to apply")
    
    max_adjustment_cap = Column(Numeric(8, 4),
                               comment="Maximum total adjustment factor allowed")
    
    applies_to_new_business = Column(Boolean, default=True,
                                    comment="Whether adjustment applies to new business")
    
    applies_to_renewals = Column(Boolean, default=True,
                                comment="Whether adjustment applies to renewals")
    
    requires_underwriter_approval = Column(Boolean, default=False,
                                          comment="Whether this adjustment requires underwriter approval")

    # =====================================================
    # INTEGRATION WITH OTHER COMPONENTS
    # =====================================================
    
    profile_id = Column(UUID(as_uuid=True), ForeignKey('quotation_pricing_profiles.id'),
                       comment="Link to pricing profile from Step 4")
    
    priority = Column(Integer, default=100,
                     comment="Processing priority (lower = higher priority)")
    
    calculation_order = Column(String(50), default="after_base_premium",
                              comment="When to apply: before_base_premium, after_base_premium, final_adjustment")

    # =====================================================
    # VALIDITY AND STATUS
    # =====================================================
    
    effective_date = Column(DateTime, default=datetime.utcnow,
                           comment="Date when this adjustment becomes effective")
    
    expiration_date = Column(DateTime,
                            comment="Date when this adjustment expires")
    
    is_active = Column(Boolean, default=True, nullable=False, index=True,
                      comment="Whether this adjustment is currently active")
    
    auto_renewal = Column(Boolean, default=True,
                         comment="Whether this adjustment automatically renews")

    # =====================================================
    # AUDIT AND COMPLIANCE
    # =====================================================
    
    created_by = Column(UUID(as_uuid=True),
                       comment="User ID who created this adjustment")
    
    updated_by = Column(UUID(as_uuid=True),
                       comment="User ID who last updated this adjustment")
    
    version = Column(String(20), default="1.0",
                    comment="Version number for change tracking")
    
    approval_status = Column(String(50), default="draft",
                            comment="Approval status: draft, pending, approved, rejected")
    
    approved_by = Column(UUID(as_uuid=True),
                        comment="User ID who approved this adjustment")
    
    approved_at = Column(DateTime,
                        comment="Timestamp of approval")
    
    actuarial_notes = Column(Text,
                            comment="Notes from actuarial review")

    # =====================================================
    # RELATIONSHIPS
    # =====================================================
    
    # Relationship to pricing profile (Step 4 integration)
    profile = relationship("QuotationPricingProfile", back_populates="industry_adjustments")

    # =====================================================
    # TABLE CONFIGURATION
    # =====================================================
    
    __table_args__ = (
        # Indexes for performance
        {"comment": "Industry-specific pricing adjustments for Step 5 advanced pricing components"}
    )

    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def calculate_adjustment(self, base_premium: Decimal, company_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate industry adjustment based on company data and configuration.
        
        Args:
            base_premium: Base premium amount to adjust
            company_data: Company information including industry, size, location, etc.
            
        Returns:
            Dictionary with adjustment calculation details
        """
        if not self.is_active or not self._is_applicable(company_data):
            return {
                'adjusted_premium': base_premium,
                'adjustment_amount': Decimal('0.00'),
                'adjustment_factor': Decimal('1.0000'),
                'applicable': False,
                'reason': 'Not applicable'
            }
        
        # Get base adjustment factor
        base_factor = self._get_base_adjustment_factor(company_data)
        
        # Apply size-based adjustments
        size_factor = self._get_size_adjustment_factor(company_data)
        
        # Apply experience modification
        experience_factor = self._get_experience_modification(company_data)
        
        # Apply seasonal adjustments
        seasonal_factor = self._get_seasonal_adjustment()
        
        # Apply geographic adjustments
        geographic_factor = self._get_geographic_adjustment(company_data)
        
        # Calculate total adjustment factor
        total_factor = base_factor * size_factor * experience_factor * seasonal_factor * geographic_factor
        
        # Apply cap if specified
        if self.max_adjustment_cap:
            total_factor = min(total_factor, self.max_adjustment_cap)
        
        # Calculate adjusted premium
        if self.adjustment_type in [AdjustmentType.FIXED_AMOUNT_INCREASE, AdjustmentType.FIXED_AMOUNT_DECREASE]:
            adjustment_amount = self.fixed_amount or Decimal('0.00')
            if self.adjustment_type == AdjustmentType.FIXED_AMOUNT_DECREASE:
                adjustment_amount = -adjustment_amount
            adjusted_premium = base_premium + adjustment_amount
        else:
            adjustment_amount = base_premium * (total_factor - 1)
            adjusted_premium = base_premium * total_factor
        
        return {
            'adjusted_premium': adjusted_premium,
            'adjustment_amount': adjustment_amount,
            'adjustment_factor': total_factor,
            'base_factor': base_factor,
            'size_factor': size_factor,
            'experience_factor': experience_factor,
            'seasonal_factor': seasonal_factor,
            'geographic_factor': geographic_factor,
            'applicable': True,
            'industry_group': self.industry_group.value,
            'risk_level': self.risk_level.value
        }
    
    def _is_applicable(self, company_data: Dict[str, Any]) -> bool:
        """Check if this adjustment applies to the company."""
        if not company_data:
            return False
        
        # Check minimum premium threshold
        premium_amount = company_data.get('premium_amount')
        if premium_amount and self.min_premium_threshold:
            if premium_amount < self.min_premium_threshold:
                return False
        
        # Check business type applicability
        business_type = company_data.get('business_type', 'new')
        if business_type == 'new' and not self.applies_to_new_business:
            return False
        if business_type == 'renewal' and not self.applies_to_renewals:
            return False
        
        # Check NAICS code match
        company_naics = company_data.get('naics_code')
        if company_naics:
            if self.naics_codes:
                # Check if company NAICS matches any of our codes (with partial matching)
                matches = any(
                    company_naics.startswith(code) or code.startswith(company_naics)
                    for code in self.naics_codes
                )
                if not matches:
                    return False
            
            # Check exclusions
            if self.excluded_naics_codes:
                excluded = any(
                    company_naics.startswith(code) or code.startswith(company_naics)
                    for code in self.excluded_naics_codes
                )
                if excluded:
                    return False
        
        # Check industry keywords
        company_description = company_data.get('business_description', '').lower()
        if self.industry_keywords and company_description:
            keyword_match = any(
                keyword.lower() in company_description
                for keyword in self.industry_keywords
            )
            if not keyword_match:
                return False
        
        return True
    
    def _get_base_adjustment_factor(self, company_data: Dict[str, Any]) -> Decimal:
        """Get the base adjustment factor."""
        if self.adjustment_type == AdjustmentType.MULTIPLIER:
            return self.adjustment_factor
        
        elif self.adjustment_type == AdjustmentType.PERCENTAGE_INCREASE:
            return Decimal('1.0000') + (self.adjustment_factor / 100)
        
        elif self.adjustment_type == AdjustmentType.PERCENTAGE_DECREASE:
            return Decimal('1.0000') - (self.adjustment_factor / 100)
        
        else:
            return Decimal('1.0000')
    
    def _get_size_adjustment_factor(self, company_data: Dict[str, Any]) -> Decimal:
        """Get size-based adjustment factor."""
        if not self.size_tiers or not company_data:
            return Decimal('1.0000')
        
        metric = self.size_tiers.get('metric', 'employee_count')
        company_size = company_data.get(metric, 0)
        
        if not company_size:
            return Decimal('1.0000')
        
        # Find applicable tier
        for tier in sorted(self.size_tiers.get('tiers', []), key=lambda x: x.get('max_employees', 0)):
            max_size = tier.get(f'max_{metric.split("_")[0]}', tier.get('max_employees', 0))
            if company_size <= max_size:
                return Decimal(str(tier.get('adjustment_factor', 1.0000)))
        
        # If no tier matches, use the last (largest) tier
        if self.size_tiers.get('tiers'):
            last_tier = self.size_tiers['tiers'][-1]
            return Decimal(str(last_tier.get('adjustment_factor', 1.0000)))
        
        return Decimal('1.0000')
    
    def _get_experience_modification(self, company_data: Dict[str, Any]) -> Decimal:
        """Get experience modification factor."""
        if not self.uses_experience_mod or not company_data:
            return Decimal('1.0000')
        
        # Get claims experience data
        claims_data = company_data.get('claims_experience', {})
        
        if not claims_data:
            return self.base_experience_mod
        
        # Calculate experience mod based on claims history
        # This is a simplified calculation - real experience mod calculations are more complex
        expected_losses = claims_data.get('expected_losses', 0)
        actual_losses = claims_data.get('actual_losses', 0)
        
        if expected_losses == 0:
            return self.base_experience_mod
        
        experience_ratio = actual_losses / expected_losses
        experience_mod = Decimal(str(experience_ratio))
        
        # Apply limits
        if experience_mod < self.min_experience_mod:
            experience_mod = self.min_experience_mod
        elif experience_mod > self.max_experience_mod:
            experience_mod = self.max_experience_mod
        
        return experience_mod
    
    def _get_seasonal_adjustment(self) -> Decimal:
        """Get seasonal adjustment factor based on current date."""
        if not self.seasonal_adjustments:
            return Decimal('1.0000')
        
        current_month = datetime.utcnow().month
        
        # Determine quarter
        if current_month <= 3:
            quarter = 'Q1'
        elif current_month <= 6:
            quarter = 'Q2'
        elif current_month <= 9:
            quarter = 'Q3'
        else:
            quarter = 'Q4'
        
        seasonal_factor = self.seasonal_adjustments.get(quarter, 1.0)
        return Decimal(str(seasonal_factor))
    
    def _get_geographic_adjustment(self, company_data: Dict[str, Any]) -> Decimal:
        """Get geographic adjustment factor."""
        if not self.geographic_variations or not company_data:
            return Decimal('1.0000')
        
        state = company_data.get('state')
        region = company_data.get('region')
        
        # Check state-specific adjustments
        if state and 'states' in self.geographic_variations:
            state_factor = self.geographic_variations['states'].get(state)
            if state_factor:
                return Decimal(str(state_factor))
        
        # Check region-specific adjustments
        if region and 'regions' in self.geographic_variations:
            region_factor = self.geographic_variations['regions'].get(region)
            if region_factor:
                return Decimal(str(region_factor))
        
        return Decimal('1.0000')
    
    def get_applicable_naics_codes(self) -> list:
        """Get list of applicable NAICS codes."""
        return self.naics_codes or []
    
    def validate_configuration(self) -> tuple[bool, str]:
        """
        Validate the adjustment configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.adjustment_type in [AdjustmentType.MULTIPLIER, AdjustmentType.PERCENTAGE_INCREASE, AdjustmentType.PERCENTAGE_DECREASE]:
            if not self.adjustment_factor or self.adjustment_factor <= 0:
                return False, "Adjustment factor must be greater than 0"
        
        elif self.adjustment_type in [AdjustmentType.FIXED_AMOUNT_INCREASE, AdjustmentType.FIXED_AMOUNT_DECREASE]:
            if not self.fixed_amount or self.fixed_amount <= 0:
                return False, "Fixed amount must be greater than 0"
        
        # Validate experience mod limits
        if self.uses_experience_mod:
            if self.min_experience_mod and self.max_experience_mod:
                if self.min_experience_mod >= self.max_experience_mod:
                    return False, "Minimum experience mod must be less than maximum"
        
        return True, ""
    
    def to_dict(self) -> dict:
        """
        Convert model to dictionary for API responses.
        
        Returns:
            Dictionary representation of the model
        """
        return {
            'id': str(self.id),
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'industry_group': self.industry_group.value if self.industry_group else None,
            'risk_level': self.risk_level.value if self.risk_level else None,
            'adjustment_type': self.adjustment_type.value if self.adjustment_type else None,
            'adjustment_factor': float(self.adjustment_factor) if self.adjustment_factor else None,
            'fixed_amount': float(self.fixed_amount) if self.fixed_amount else None,
            'currency': self.currency,
            'naics_codes': self.naics_codes,
            'uses_experience_mod': self.uses_experience_mod,
            'is_active': self.is_active,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return f"<PricingIndustryAdjustment(code='{self.code}', factor={self.adjustment_factor}, industry='{self.industry_group.value}')>"

    def __str__(self) -> str:
        return f"{self.name}: {self.industry_group.value} - {self.risk_level.value}"