# app/modules/pricing/product/models/product_feature_model.py

"""
Product Feature Model

Manages optional and mandatory features/add-ons for insurance products.
Features can modify coverage, add riders, or provide additional benefits.
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, Index, CheckConstraint, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from typing import Optional, Dict, Any, List
from decimal import Decimal
from enum import Enum
import uuid


# ================================================================
# ENUMS
# ================================================================

class FeatureType(str, Enum):
    """Feature type enumeration"""
    COVERAGE_EXTENSION = "coverage_extension"
    RIDER = "rider"
    ADDON = "addon"
    DISCOUNT = "discount"
    SERVICE = "service"
    BENEFIT_ENHANCEMENT = "benefit_enhancement"
    LIMIT_INCREASE = "limit_increase"
    DEDUCTIBLE_WAIVER = "deductible_waiver"
    NETWORK_UPGRADE = "network_upgrade"
    OTHER = "other"


class FeatureCategory(str, Enum):
    """Feature category for grouping"""
    MEDICAL = "medical"
    DENTAL = "dental"
    OPTICAL = "optical"
    WELLNESS = "wellness"
    TRAVEL = "travel"
    EMERGENCY = "emergency"
    MATERNITY = "maternity"
    SPORTS = "sports"
    LIFESTYLE = "lifestyle"
    FAMILY = "family"
    LEGAL = "legal"
    OTHER = "other"


class PremiumCalculationType(str, Enum):
    """How the feature premium is calculated"""
    FIXED_AMOUNT = "fixed_amount"
    PERCENTAGE = "percentage"
    TIERED = "tiered"
    AGE_BASED = "age_based"
    RISK_BASED = "risk_based"
    CUSTOM_FORMULA = "custom_formula"


class FeatureStatus(str, Enum):
    """Feature availability status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DISCONTINUED = "discontinued"
    SEASONAL = "seasonal"


# ================================================================
# MODEL
# ================================================================

class ProductFeature(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Product Feature Model
    
    Represents optional or mandatory features that can be added to products.
    Features modify the base product coverage or add additional benefits.
    """
    
    __tablename__ = "product_features"
    __table_args__ = (
        # Indexes
        Index('idx_product_feature_product_id', 'product_id'),
        Index('idx_product_feature_code', 'feature_code', unique=True),
        Index('idx_product_feature_type', 'feature_type'),
        Index('idx_product_feature_category', 'feature_category'),
        Index('idx_product_feature_active', 'is_active'),
        Index('idx_product_feature_optional', 'is_optional'),
        # Composite indexes
        Index('idx_product_feature_product_active', 'product_id', 'is_active'),
        Index('idx_product_feature_product_type', 'product_id', 'feature_type'),
        # Constraints
        CheckConstraint('min_age <= max_age', name='check_age_range'),
        CheckConstraint('additional_premium >= 0', name='check_premium_positive'),
        CheckConstraint('discount_percentage >= 0 AND discount_percentage <= 100', name='check_discount_range'),
        {'extend_existing': True}
    )
    
    # ================================================================
    # CORE IDENTIFICATION
    # ================================================================
    
    # Foreign Key
    product_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("product_catalog.id", ondelete="CASCADE"), 
        nullable=False,
        comment="Reference to parent product"
    )
    
    # Basic Information
    feature_code = Column(String(50), unique=True, nullable=False, comment="Unique feature code")
    feature_name = Column(String(100), nullable=False, comment="Feature display name")
    feature_name_ar = Column(String(100), nullable=True, comment="Feature name in Arabic")
    feature_type = Column(String(30), nullable=False, default=FeatureType.ADDON.value, comment="Type of feature")
    feature_category = Column(String(30), nullable=True, comment="Feature category for grouping")
    
    # Description
    description = Column(Text, nullable=True, comment="Detailed feature description")
    description_ar = Column(Text, nullable=True, comment="Feature description in Arabic")
    benefits_summary = Column(JSONB, nullable=True, comment="Summary of benefits provided")
    
    # ================================================================
    # CONFIGURATION
    # ================================================================
    
    # Availability
    is_optional = Column(Boolean, default=True, nullable=False, comment="Whether feature is optional or mandatory")
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether feature is currently active")
    is_visible = Column(Boolean, default=True, comment="Whether feature is visible to customers")
    is_default_selected = Column(Boolean, default=False, comment="Whether feature is selected by default")
    
    # Feature Configuration
    feature_config = Column(JSONB, nullable=True, comment="Feature-specific configuration")
    coverage_modifications = Column(JSONB, nullable=True, comment="How this feature modifies coverage")
    limit_adjustments = Column(JSONB, nullable=True, comment="Limit adjustments provided by feature")
    
    # ================================================================
    # PRICING
    # ================================================================
    
    # Premium Configuration
    additional_premium = Column(
        NUMERIC(15, 2), 
        default=0, 
        nullable=False,
        comment="Additional premium amount for this feature"
    )
    premium_calculation_type = Column(
        String(20), 
        default=PremiumCalculationType.FIXED_AMOUNT.value,
        comment="How premium is calculated"
    )
    premium_percentage = Column(
        NUMERIC(5, 2), 
        nullable=True,
        comment="Premium percentage if calculation type is percentage"
    )
    
    # Discount Configuration
    provides_discount = Column(Boolean, default=False, comment="Whether feature provides a discount")
    discount_percentage = Column(
        NUMERIC(5, 2), 
        nullable=True,
        comment="Discount percentage if feature provides discount"
    )
    discount_amount = Column(
        NUMERIC(15, 2), 
        nullable=True,
        comment="Fixed discount amount if applicable"
    )
    
    # Pricing Rules
    pricing_rules = Column(JSONB, nullable=True, comment="Complex pricing rules")
    pricing_tiers = Column(JSONB, nullable=True, comment="Tiered pricing configuration")
    
    # ================================================================
    # ELIGIBILITY & RULES
    # ================================================================
    
    # Eligibility Criteria
    eligibility_criteria = Column(JSONB, nullable=True, comment="Eligibility requirements")
    min_age = Column(Integer, nullable=True, comment="Minimum age for this feature")
    max_age = Column(Integer, nullable=True, comment="Maximum age for this feature")
    gender_restriction = Column(String(10), nullable=True, comment="Gender restriction if any")
    
    # Dependencies
    requires_features = Column(JSONB, nullable=True, comment="Other features required for this one")
    excludes_features = Column(JSONB, nullable=True, comment="Features that cannot be combined with this")
    requires_medical_underwriting = Column(Boolean, default=False, comment="Whether medical underwriting required")
    
    # Limits
    min_coverage_amount = Column(NUMERIC(15, 2), nullable=True, comment="Minimum coverage for eligibility")
    max_coverage_amount = Column(NUMERIC(15, 2), nullable=True, comment="Maximum coverage allowed")
    max_benefit_amount = Column(NUMERIC(15, 2), nullable=True, comment="Maximum benefit amount")
    
    # ================================================================
    # WAITING PERIODS & TERMS
    # ================================================================
    
    waiting_period_days = Column(Integer, default=0, comment="Waiting period in days")
    benefit_period_days = Column(Integer, nullable=True, comment="Benefit period in days")
    cooling_off_period_days = Column(Integer, default=14, comment="Cooling off period")
    
    # Terms
    terms_conditions = Column(JSONB, nullable=True, comment="Specific terms and conditions")
    exclusions = Column(JSONB, nullable=True, comment="Feature-specific exclusions")
    
    # ================================================================
    # DISPLAY & MARKETING
    # ================================================================
    
    display_order = Column(Integer, default=100, comment="Display order in UI")
    display_group = Column(String(50), nullable=True, comment="Grouping for display purposes")
    icon_url = Column(String(500), nullable=True, comment="Icon URL for UI")
    badge_text = Column(String(50), nullable=True, comment="Badge text (e.g., 'Popular', 'New')")
    
    # Marketing
    marketing_highlights = Column(JSONB, nullable=True, comment="Marketing bullet points")
    target_audience = Column(JSONB, nullable=True, comment="Target audience segments")
    promotional_period_start = Column(Date, nullable=True, comment="Promotion start date")
    promotional_period_end = Column(Date, nullable=True, comment="Promotion end date")
    
    # ================================================================
    # STATISTICS & ANALYTICS
    # ================================================================
    
    # Usage Statistics
    adoption_rate = Column(NUMERIC(5, 2), nullable=True, comment="Percentage of customers who select this")
    satisfaction_score = Column(NUMERIC(3, 2), nullable=True, comment="Customer satisfaction score")
    claim_frequency = Column(NUMERIC(5, 2), nullable=True, comment="Claim frequency for this feature")
    loss_ratio = Column(NUMERIC(5, 2), nullable=True, comment="Loss ratio for this feature")
    
    # ================================================================
    # METADATA
    # ================================================================
    
    status = Column(String(20), default=FeatureStatus.ACTIVE.value, comment="Feature status")
    effective_date = Column(Date, nullable=True, comment="When feature becomes effective")
    expiry_date = Column(Date, nullable=True, comment="When feature expires")
    feature_metadata = Column(JSONB, nullable=True, comment="Additional metadata")
    tags = Column(ARRAY(String), nullable=True, comment="Feature tags")
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    # Many-to-one relationship
    product = relationship("ProductCatalog", back_populates="features")
    
    # ================================================================
    # METHODS
    # ================================================================
    
    def __repr__(self) -> str:
        return f"<ProductFeature(code={self.feature_code}, name={self.feature_name})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'feature_code': self.feature_code,
            'feature_name': self.feature_name,
            'feature_name_ar': self.feature_name_ar,
            'feature_type': self.feature_type,
            'feature_category': self.feature_category,
            'description': self.description,
            'is_optional': self.is_optional,
            'is_active': self.is_active,
            'additional_premium': float(self.additional_premium) if self.additional_premium else 0,
            'premium_calculation_type': self.premium_calculation_type,
            'eligibility_criteria': self.eligibility_criteria,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def is_eligible_for_age(self, age: int) -> bool:
        """Check if age is eligible for this feature"""
        if self.min_age and age < self.min_age:
            return False
        if self.max_age and age > self.max_age:
            return False
        return True
    
    def is_eligible_for_gender(self, gender: str) -> bool:
        """Check if gender is eligible for this feature"""
        if not self.gender_restriction:
            return True
        return gender.lower() == self.gender_restriction.lower()
    
    def calculate_premium(self, base_amount: Decimal = None, age: int = None) -> Decimal:
        """Calculate feature premium based on configuration"""
        if self.premium_calculation_type == PremiumCalculationType.FIXED_AMOUNT.value:
            return Decimal(str(self.additional_premium or 0))
        
        elif self.premium_calculation_type == PremiumCalculationType.PERCENTAGE.value:
            if base_amount and self.premium_percentage:
                return base_amount * Decimal(str(self.premium_percentage)) / 100
        
        elif self.premium_calculation_type == PremiumCalculationType.AGE_BASED.value:
            # Implement age-based calculation from pricing_tiers
            if self.pricing_tiers and age:
                for tier in self.pricing_tiers:
                    if tier.get('min_age') <= age <= tier.get('max_age'):
                        return Decimal(str(tier.get('premium', 0)))
        
        return Decimal('0')
    
    def get_coverage_modifications(self) -> Dict[str, Any]:
        """Get coverage modifications provided by this feature"""
        return self.coverage_modifications or {}
    
    def is_compatible_with(self, other_feature_codes: List[str]) -> bool:
        """Check if this feature is compatible with other features"""
        if not self.excludes_features:
            return True
        
        excluded = self.excludes_features.get('codes', [])
        return not any(code in excluded for code in other_feature_codes)
    
    def get_required_features(self) -> List[str]:
        """Get list of required feature codes"""
        if not self.requires_features:
            return []
        return self.requires_features.get('codes', [])


# ================================================================
# END OF MODEL
# ================================================================