# app/modules/pricing/product/models/plan_type_model.py

"""
Plan Type Model

Defines the different types of insurance plans available in the system.
Used for categorizing and managing plan variations like Individual, Family, Group, etc.
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from typing import Dict, Any, Optional
from enum import Enum


# ================================================================
# ENUMS
# ================================================================

class PlanTypeCode(str, Enum):
    """Standard plan type codes"""
    IND = "IND"          # Individual
    FAM = "FAM"          # Family
    GRP = "GRP"          # Group
    CRP = "CRP"          # Corporate
    SME = "SME"          # Small/Medium Enterprise
    STU = "STU"          # Student
    SEN = "SEN"          # Senior
    EMP = "EMP"          # Employee
    GOV = "GOV"          # Government
    VIP = "VIP"          # VIP/Premium
    BAS = "BAS"          # Basic
    STD = "STD"          # Standard
    PRE = "PRE"          # Premium
    CUS = "CUS"          # Custom


class PlanTypeCategory(str, Enum):
    """Plan type categories"""
    INDIVIDUAL = "individual"
    GROUP = "group"
    SPECIAL = "special"
    CUSTOM = "custom"


# ================================================================
# MODEL
# ================================================================

class PlanType(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Plan Type Model
    
    Manages different types of insurance plans and their configurations.
    Provides categorization and rules for plan variations.
    """
    
    __tablename__ = "plan_types"
    __table_args__ = (
        # Indexes
        Index('idx_plan_type_code', 'code', unique=True),
        Index('idx_plan_type_category', 'category'),
        Index('idx_plan_type_active', 'is_active'),
        Index('idx_plan_type_order', 'order_index'),
        # Composite indexes
        Index('idx_plan_type_category_active', 'category', 'is_active'),
        {'extend_existing': True}
    )
    
    # ================================================================
    # CORE IDENTIFICATION
    # ================================================================
    
    # Basic Information
    code = Column(String(10), unique=True, nullable=False, comment="Unique plan type code")
    label = Column(String(100), nullable=False, comment="Display label for plan type")
    label_ar = Column(String(100), nullable=True, comment="Arabic label for plan type")
    category = Column(String(20), nullable=False, default=PlanTypeCategory.INDIVIDUAL.value, comment="Plan type category")
    
    # Description
    description = Column(Text, nullable=True, comment="Detailed description of plan type")
    description_ar = Column(Text, nullable=True, comment="Arabic description")
    
    # ================================================================
    # CONFIGURATION
    # ================================================================
    
    # Display Configuration
    icon = Column(String(50), nullable=True, comment="Icon identifier for UI")
    color_code = Column(String(7), nullable=True, comment="Color hex code for UI")
    order_index = Column(Integer, default=100, nullable=False, comment="Display order index")
    display_group = Column(String(50), nullable=True, comment="Grouping for display purposes")
    
    # Multi-language Support
    language_labels = Column(JSONB, nullable=True, comment="Labels in multiple languages")
    
    # ================================================================
    # RULES & CONSTRAINTS
    # ================================================================
    
    # Member Limits
    min_members = Column(Integer, default=1, comment="Minimum number of members")
    max_members = Column(Integer, nullable=True, comment="Maximum number of members")
    min_adults = Column(Integer, default=1, comment="Minimum number of adults")
    max_adults = Column(Integer, nullable=True, comment="Maximum number of adults")
    min_children = Column(Integer, default=0, comment="Minimum number of children")
    max_children = Column(Integer, nullable=True, comment="Maximum number of children")
    
    # Age Rules
    min_primary_age = Column(Integer, nullable=True, comment="Minimum age for primary member")
    max_primary_age = Column(Integer, nullable=True, comment="Maximum age for primary member")
    min_dependent_age = Column(Integer, nullable=True, comment="Minimum age for dependents")
    max_dependent_age = Column(Integer, nullable=True, comment="Maximum age for dependents")
    child_age_limit = Column(Integer, default=18, comment="Age limit for children")
    
    # Eligibility Rules
    eligibility_rules = Column(JSONB, nullable=True, comment="Complex eligibility rules")
    requires_employment = Column(Boolean, default=False, comment="Whether employment is required")
    requires_sponsorship = Column(Boolean, default=False, comment="Whether sponsorship is required")
    requires_residency = Column(Boolean, default=False, comment="Whether residency is required")
    
    # ================================================================
    # PRICING RULES
    # ================================================================
    
    # Pricing Configuration
    pricing_method = Column(String(50), nullable=True, comment="Pricing method for this plan type")
    base_rate_multiplier = Column(NUMERIC(5, 3), default=1.0, comment="Base rate multiplier")
    family_discount_applicable = Column(Boolean, default=False, comment="Whether family discount applies")
    group_discount_applicable = Column(Boolean, default=False, comment="Whether group discount applies")
    volume_discount_applicable = Column(Boolean, default=False, comment="Whether volume discount applies")
    
    # Discount Rules
    discount_rules = Column(JSONB, nullable=True, comment="Discount rules configuration")
    max_discount_percentage = Column(NUMERIC(5, 2), nullable=True, comment="Maximum discount allowed")
    
    # ================================================================
    # COVERAGE RULES
    # ================================================================
    
    # Coverage Configuration
    coverage_rules = Column(JSONB, nullable=True, comment="Coverage rules for this plan type")
    benefit_sharing_allowed = Column(Boolean, default=True, comment="Whether benefits can be shared")
    individual_limits = Column(Boolean, default=False, comment="Whether limits are per individual")
    pooled_benefits = Column(Boolean, default=False, comment="Whether benefits are pooled")
    
    # Network Rules
    network_restrictions = Column(JSONB, nullable=True, comment="Network restrictions for plan type")
    allows_out_of_network = Column(Boolean, default=True, comment="Whether out-of-network is allowed")
    
    # ================================================================
    # UNDERWRITING
    # ================================================================
    
    underwriting_required = Column(Boolean, default=False, comment="Whether underwriting is required")
    medical_questions_required = Column(Boolean, default=False, comment="Whether medical questions required")
    health_declaration_required = Column(Boolean, default=False, comment="Whether health declaration required")
    underwriting_rules = Column(JSONB, nullable=True, comment="Specific underwriting rules")
    
    # ================================================================
    # OPERATIONAL SETTINGS
    # ================================================================
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether plan type is active")
    is_new_business = Column(Boolean, default=True, comment="Available for new business")
    is_renewable = Column(Boolean, default=True, comment="Available for renewals")
    
    # Validity Period
    min_coverage_period_months = Column(Integer, default=12, comment="Minimum coverage period")
    max_coverage_period_months = Column(Integer, default=12, comment="Maximum coverage period")
    
    # ================================================================
    # DOCUMENTATION
    # ================================================================
    
    required_documents = Column(JSONB, nullable=True, comment="Required documents for this plan type")
    terms_conditions_url = Column(String(500), nullable=True, comment="Terms and conditions URL")
    sample_policy_url = Column(String(500), nullable=True, comment="Sample policy document URL")
    
    # ================================================================
    # METADATA
    # ================================================================
    
    plan_type_metadata = Column(JSONB, nullable=True, comment="Additional metadata")
    configuration = Column(JSONB, nullable=True, comment="Plan type specific configuration")
    tags = Column(ARRAY(String), nullable=True, comment="Tags for categorization")
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    # One-to-many relationship with plans
    plans = relationship("Plan", back_populates="plan_type")
    
    # ================================================================
    # METHODS
    # ================================================================
    
    def __repr__(self) -> str:
        return f"<PlanType(code={self.code}, label={self.label})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            'id': str(self.id),
            'code': self.code,
            'label': self.label,
            'label_ar': self.label_ar,
            'category': self.category,
            'description': self.description,
            'min_members': self.min_members,
            'max_members': self.max_members,
            'is_active': self.is_active,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def validate_member_count(self, adult_count: int, child_count: int = 0) -> tuple[bool, str]:
        """
        Validate member counts for this plan type
        Returns: (is_valid, error_message)
        """
        total = adult_count + child_count
        
        # Check total members
        if self.min_members and total < self.min_members:
            return False, f"Minimum {self.min_members} members required"
        if self.max_members and total > self.max_members:
            return False, f"Maximum {self.max_members} members allowed"
        
        # Check adults
        if self.min_adults and adult_count < self.min_adults:
            return False, f"Minimum {self.min_adults} adults required"
        if self.max_adults and adult_count > self.max_adults:
            return False, f"Maximum {self.max_adults} adults allowed"
        
        # Check children
        if self.min_children and child_count < self.min_children:
            return False, f"Minimum {self.min_children} children required"
        if self.max_children and child_count > self.max_children:
            return False, f"Maximum {self.max_children} children allowed"
        
        return True, "Valid"
    
    def is_eligible_for_age(self, age: int, is_primary: bool = True) -> bool:
        """Check if age is eligible for this plan type"""
        if is_primary:
            if self.min_primary_age and age < self.min_primary_age:
                return False
            if self.max_primary_age and age > self.max_primary_age:
                return False
        else:
            if self.min_dependent_age and age < self.min_dependent_age:
                return False
            if self.max_dependent_age and age > self.max_dependent_age:
                return False
        return True
    
    def get_pricing_multiplier(self) -> float:
        """Get the base rate multiplier for this plan type"""
        return float(self.base_rate_multiplier) if self.base_rate_multiplier else 1.0
    
    def allows_discounts(self) -> Dict[str, bool]:
        """Get allowed discount types"""
        return {
            'family': self.family_discount_applicable or False,
            'group': self.group_discount_applicable or False,
            'volume': self.volume_discount_applicable or False
        }


# ================================================================
# END OF MODEL
# ================================================================