# app/modules/pricing/product/models/product_catalog_model.py

"""
Product Catalog Model

Core entity for managing insurance products in the system.
This model serves as the foundation for all insurance products
and links to plans, features, and pricing profiles.
"""

from sqlalchemy import Column, String, Text, Boolean, Date, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


# ================================================================
# ENUMS
# ================================================================

class ProductCategory(str, Enum):
    """Product category enumeration"""
    MEDICAL = "medical"
    MOTOR = "motor"
    LIFE = "life"
    TRAVEL = "travel"
    PROPERTY = "property"
    LIABILITY = "liability"
    MARINE = "marine"
    AVIATION = "aviation"
    OTHER = "other"


class ProductType(str, Enum):
    """Product type enumeration"""
    INDIVIDUAL = "individual"
    GROUP = "group"
    FAMILY = "family"
    CORPORATE = "corporate"
    SME = "sme"
    GOVERNMENT = "government"


class ProductStatus(str, Enum):
    """Product lifecycle status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISCONTINUED = "discontinued"
    ARCHIVED = "archived"


class DistributionChannel(str, Enum):
    """Distribution channel enumeration"""
    DIRECT = "direct"
    BROKER = "broker"
    AGENT = "agent"
    BANCASSURANCE = "bancassurance"
    DIGITAL = "digital"
    PARTNERSHIP = "partnership"
    AGGREGATOR = "aggregator"


# ================================================================
# MODEL
# ================================================================

class ProductCatalog(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Product Catalog Model
    
    Core entity representing insurance products in the system.
    Manages product definitions, features, regulatory compliance,
    and relationships with plans and pricing.
    """
    
    __tablename__ = "product_catalog"
    __table_args__ = (
        # Indexes for performance optimization
        Index('idx_product_catalog_code', 'product_code', unique=True),
        Index('idx_product_catalog_category', 'product_category'),
        Index('idx_product_catalog_type', 'product_type'),
        Index('idx_product_catalog_status', 'product_status'),
        Index('idx_product_catalog_active', 'is_active'),
        Index('idx_product_catalog_launch_date', 'launch_date'),
        # Composite indexes
        Index('idx_product_catalog_category_status', 'product_category', 'product_status'),
        Index('idx_product_catalog_active_category', 'is_active', 'product_category'),
        {'extend_existing': True}
    )
    
    # ================================================================
    # CORE PRODUCT IDENTIFICATION
    # ================================================================
    
    # Basic Information
    product_code = Column(String(50), nullable=False, unique=True, comment="Unique product identifier code")
    product_name = Column(String(100), nullable=False, comment="Product display name")
    product_name_ar = Column(String(100), nullable=True, comment="Product name in Arabic")
    product_category = Column(String(50), nullable=False, default=ProductCategory.MEDICAL.value, comment="Product category")
    product_type = Column(String(50), nullable=False, default=ProductType.INDIVIDUAL.value, comment="Product type")
    
    # Description
    description = Column(Text, nullable=True, comment="Detailed product description")
    description_ar = Column(Text, nullable=True, comment="Product description in Arabic")
    short_description = Column(String(500), nullable=True, comment="Brief product summary")
    key_features = Column(JSONB, nullable=True, comment="Key product features as JSON")
    
    # ================================================================
    # PRODUCT CONFIGURATION
    # ================================================================
    
    # Market Configuration
    target_market = Column(JSONB, nullable=True, comment="Target market segments and demographics")
    distribution_channels = Column(ARRAY(String), nullable=True, comment="Allowed distribution channels")
    geographic_coverage = Column(JSONB, nullable=True, comment="Geographic areas where product is available")
    
    # Product Rules
    min_entry_age = Column(Integer, nullable=True, comment="Minimum age for product eligibility")
    max_entry_age = Column(Integer, nullable=True, comment="Maximum age for product eligibility")
    min_coverage_amount = Column(Integer, nullable=True, comment="Minimum coverage amount")
    max_coverage_amount = Column(Integer, nullable=True, comment="Maximum coverage amount")
    waiting_period_days = Column(Integer, default=0, comment="Waiting period in days")
    
    # ================================================================
    # REGULATORY & COMPLIANCE
    # ================================================================
    
    regulatory_approvals = Column(JSONB, nullable=True, comment="Regulatory approval details")
    regulatory_code = Column(String(100), nullable=True, comment="Regulatory filing code")
    compliance_requirements = Column(JSONB, nullable=True, comment="Compliance requirements checklist")
    license_number = Column(String(100), nullable=True, comment="Product license number")
    
    # ================================================================
    # PRICING & UNDERWRITING
    # ================================================================
    
    # Pricing References
    pricing_model_id = Column(UUID(as_uuid=True), nullable=True, comment="Reference to pricing model")
    base_premium_table_id = Column(UUID(as_uuid=True), nullable=True, comment="Reference to premium table")
    actuarial_table_id = Column(UUID(as_uuid=True), nullable=True, comment="Reference to actuarial table")
    
    # Underwriting
    underwriting_rules = Column(JSONB, nullable=True, comment="Underwriting rules configuration")
    underwriting_guidelines = Column(Text, nullable=True, comment="Underwriting guidelines document")
    risk_assessment_required = Column(Boolean, default=True, comment="Whether risk assessment is required")
    medical_underwriting_required = Column(Boolean, default=False, comment="Whether medical underwriting is required")
    
    # ================================================================
    # TERMS & CONDITIONS
    # ================================================================
    
    policy_terms = Column(JSONB, nullable=True, comment="Policy terms and conditions")
    coverage_options = Column(JSONB, nullable=True, comment="Available coverage options")
    exclusions = Column(JSONB, nullable=True, comment="Product exclusions list")
    riders_available = Column(JSONB, nullable=True, comment="Available riders/add-ons")
    
    # Documents
    terms_document_url = Column(String(500), nullable=True, comment="URL to terms document")
    product_brochure_url = Column(String(500), nullable=True, comment="URL to product brochure")
    policy_wording_url = Column(String(500), nullable=True, comment="URL to policy wording document")
    
    # ================================================================
    # COMMISSION & INCENTIVES
    # ================================================================
    
    commission_structure = Column(JSONB, nullable=True, comment="Commission structure for agents/brokers")
    incentive_programs = Column(JSONB, nullable=True, comment="Incentive programs configuration")
    referral_fee_structure = Column(JSONB, nullable=True, comment="Referral fee configuration")
    
    # ================================================================
    # PRODUCT LIFECYCLE
    # ================================================================
    
    product_status = Column(String(20), nullable=False, default=ProductStatus.DRAFT.value, comment="Current product status")
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether product is currently active")
    is_new_business_allowed = Column(Boolean, default=True, comment="Whether new policies can be issued")
    is_renewal_allowed = Column(Boolean, default=True, comment="Whether renewals are allowed")
    
    # Dates
    launch_date = Column(Date, nullable=True, comment="Product launch date")
    sunset_date = Column(Date, nullable=True, comment="Product sunset/end date")
    last_review_date = Column(Date, nullable=True, comment="Last product review date")
    next_review_date = Column(Date, nullable=True, comment="Next scheduled review date")
    
    # ================================================================
    # VERSIONING & AUDIT
    # ================================================================
    
    version = Column(String(20), default="1.0.0", comment="Product version")
    version_notes = Column(Text, nullable=True, comment="Version change notes")
    approval_status = Column(String(50), nullable=True, comment="Approval workflow status")
    approved_by = Column(UUID(as_uuid=True), nullable=True, comment="User who approved the product")
    approved_date = Column(Date, nullable=True, comment="Date of approval")
    
    # ================================================================
    # METADATA & CONFIGURATION
    # ================================================================
    
    product_metadata = Column(JSONB, nullable=True, comment="Additional metadata")
    configuration = Column(JSONB, nullable=True, comment="Product-specific configuration")
    feature_flags = Column(JSONB, nullable=True, comment="Feature toggles for this product")
    tags = Column(ARRAY(String), nullable=True, comment="Product tags for categorization")
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    # One-to-many relationships
    plans = relationship("Plan", back_populates="product", cascade="all, delete-orphan")
    features = relationship("ProductFeature", back_populates="product", cascade="all, delete-orphan")
    # Note: Add more relationships as we create related models
    
    # ================================================================
    # METHODS
    # ================================================================
    
    def __repr__(self) -> str:
        return f"<ProductCatalog(code={self.product_code}, name={self.product_name})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            'id': str(self.id),
            'product_code': self.product_code,
            'product_name': self.product_name,
            'product_name_ar': self.product_name_ar,
            'product_category': self.product_category,
            'product_type': self.product_type,
            'description': self.description,
            'status': self.product_status,
            'is_active': self.is_active,
            'launch_date': self.launch_date.isoformat() if self.launch_date else None,
            'sunset_date': self.sunset_date.isoformat() if self.sunset_date else None,
            'distribution_channels': self.distribution_channels,
            'target_market': self.target_market,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_available_for_sale(self) -> bool:
        """Check if product is available for new sales"""
        from datetime import date
        today = date.today()
        
        # Check basic availability
        if not self.is_active or not self.is_new_business_allowed:
            return False
        
        # Check product status
        if self.product_status != ProductStatus.ACTIVE.value:
            return False
        
        # Check launch date
        if self.launch_date and today < self.launch_date:
            return False
        
        # Check sunset date
        if self.sunset_date and today > self.sunset_date:
            return False
        
        return True
    
    def is_eligible_for_age(self, age: int) -> bool:
        """Check if age is eligible for this product"""
        if self.min_entry_age and age < self.min_entry_age:
            return False
        if self.max_entry_age and age > self.max_entry_age:
            return False
        return True
    
    def get_available_channels(self) -> List[str]:
        """Get list of available distribution channels"""
        return self.distribution_channels or []
    
    def requires_medical_underwriting(self) -> bool:
        """Check if product requires medical underwriting"""
        return self.medical_underwriting_required or False
    
    def get_waiting_period(self) -> int:
        """Get waiting period in days"""
        return self.waiting_period_days or 0
    
    def update_status(self, new_status: str, updated_by: Optional[uuid.UUID] = None) -> None:
        """Update product status with audit trail"""
        old_status = self.product_status
        self.product_status = new_status
        
        if updated_by:
            self.updated_by = updated_by
        
        # Add to product_metadata for audit
        if not self.product_metadata:
            self.product_metadata = {}
        
        if 'status_history' not in self.product_metadata:
            self.product_metadata['status_history'] = []
        
        self.product_metadata['status_history'].append({
            'from_status': old_status,
            'to_status': new_status,
            'changed_at': func.now(),
            'changed_by': str(updated_by) if updated_by else None
        })


# ================================================================
# END OF MODEL
# ================================================================