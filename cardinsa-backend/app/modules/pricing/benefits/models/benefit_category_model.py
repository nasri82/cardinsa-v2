# app/modules/benefits/models/benefit_category_model.py

"""
Benefit Category Model - File #1

Foundation model that categorizes all benefits and coverages.
Think of this as the "folders" that organize different types of benefits.

Examples:
- Medical Services (doctor visits, hospital care)
- Dental Care (cleanings, fillings, orthodontics)  
- Vision Care (eye exams, glasses, contacts)
- Pharmacy (prescription medications)
- Wellness (preventive care, health screenings)
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class CategoryType(str, Enum):
    """Types of benefit categories"""
    MEDICAL = "medical"           # Medical services and treatments
    DENTAL = "dental"             # Dental care and treatments
    VISION = "vision"             # Vision care and eye treatments
    PHARMACY = "pharmacy"         # Prescription medications
    WELLNESS = "wellness"         # Preventive and wellness care
    MENTAL_HEALTH = "mental_health"  # Mental health services
    MATERNITY = "maternity"       # Pregnancy and childbirth
    EMERGENCY = "emergency"       # Emergency services
    SPECIALTY = "specialty"       # Specialist care
    DIAGNOSTIC = "diagnostic"     # Tests and diagnostics


class BenefitCategory(Base):
    """
    Benefit Category Model
    
    Organizes benefits into logical groups like Medical, Dental, Vision, etc.
    This is the top-level classification that helps structure the benefit hierarchy.
    
    Real-world example:
    - Category: "Medical Services"  
    - Contains: Doctor visits, Hospital care, Surgery, etc.
    """
    
    __tablename__ = "benefit_categories"
    
    __table_args__ = (
        # Indexes for performance
        Index('idx_benefit_categories_code', 'category_code'),
        Index('idx_benefit_categories_type', 'category_type'),
        Index('idx_benefit_categories_parent', 'parent_category_id'),
        Index('idx_benefit_categories_active', 'is_active'),
        Index('idx_benefit_categories_order', 'display_order'),
        
        # Composite indexes
        Index('idx_benefit_categories_type_active', 'category_type', 'is_active'),
        Index('idx_benefit_categories_parent_order', 'parent_category_id', 'display_order'),
    )
    
    # ================================================================
    # PRIMARY IDENTIFICATION
    # ================================================================
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the category"
    )
    
    category_code = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="Unique code for the category (e.g., 'MED', 'DENT', 'VIS')"
    )
    
    # ================================================================
    # BASIC INFORMATION
    # ================================================================
    
    category_name = Column(
        String(200),
        nullable=False,
        comment="Category name in English (e.g., 'Medical Services')"
    )
    
    category_name_ar = Column(
        String(200),
        nullable=True,
        comment="Category name in Arabic"
    )
    
    category_name_fr = Column(
        String(200),
        nullable=True,
        comment="Category name in French"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed description of what this category includes"
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
    # CATEGORIZATION
    # ================================================================
    
    category_type = Column(
        String(50),
        nullable=False,
        default=CategoryType.MEDICAL.value,
        comment="Type of category (medical, dental, vision, etc.)"
    )
    
    # Hierarchical structure - categories can have parent categories
    parent_category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("benefit_categories.id", ondelete="CASCADE"),
        nullable=True,
        comment="Parent category for hierarchical organization"
    )
    
    # ================================================================
    # DISPLAY AND ORGANIZATION
    # ================================================================
    
    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Order for displaying categories (lower numbers first)"
    )
    
    icon_name = Column(
        String(100),
        nullable=True,
        comment="Icon identifier for UI display"
    )
    
    color_code = Column(
        String(7),
        nullable=True,
        comment="Hex color code for UI theming (e.g., '#FF5733')"
    )
    
    # ================================================================
    # STATUS AND LIFECYCLE
    # ================================================================
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this category is currently active"
    )
    
    is_visible = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this category should be shown to users"
    )
    
    is_mandatory = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this category must be included in plans"
    )
    
    # ================================================================
    # BUSINESS RULES
    # ================================================================
    
    requires_authorization = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether benefits in this category require authorization"
    )
    
    default_waiting_period_days = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Default waiting period for benefits in this category"
    )
    
    age_restrictions = Column(
        JSONB,
        nullable=True,
        comment="Age-based restrictions for this category"
    )
    
    # ================================================================
    # METADATA AND CONFIGURATION
    # ================================================================
    
    tags = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Tags for categorization and searching"
    )
    
    category_metadata = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional metadata and configuration"
    )
    
    # Business rules specific to this category
    business_rules = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Category-specific business rules"
    )
    
    # ================================================================
    # AUDIT FIELDS
    # ================================================================
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When this category was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="When this category was last updated"
    )
    
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created this category"
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who last updated this category"
    )
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    # Self-referential relationship for category hierarchy
    parent_category = relationship(
        "BenefitCategory",
        remote_side=[id],
        backref="child_categories"
    )
    
    # Relationship to coverages in this category
    coverages = relationship(
        "Coverage",
        back_populates="category",
        cascade="all, delete-orphan"
    )
    
    # Relationship to benefit types in this category
    benefit_types = relationship(
        "BenefitType",
        back_populates="category",
        cascade="all, delete-orphan"
    )
    
    # ================================================================
    # VALIDATORS
    # ================================================================
    
    @validates('category_type')
    def validate_category_type(self, key, value):
        """Ensure category type is valid"""
        if value not in [e.value for e in CategoryType]:
            raise ValueError(f"Invalid category type: {value}. Must be one of: {[e.value for e in CategoryType]}")
        return value
    
    @validates('category_code')
    def validate_category_code(self, key, value):
        """Ensure category code is properly formatted"""
        if not value or not value.strip():
            raise ValueError("Category code cannot be empty")
        
        # Convert to uppercase and remove spaces
        value = value.strip().upper()
        
        # Check length
        if len(value) > 50:
            raise ValueError("Category code cannot exceed 50 characters")
        
        return value
    
    @validates('color_code')
    def validate_color_code(self, key, value):
        """Ensure color code is valid hex format"""
        if value and not value.startswith('#'):
            value = f"#{value}"
        
        if value and len(value) != 7:
            raise ValueError("Color code must be in hex format (#RRGGBB)")
        
        return value
    
    # ================================================================
    # BUSINESS METHODS
    # ================================================================
    
    def get_full_hierarchy_path(self) -> List[str]:
        """Get the full path from root to this category"""
        path = [self.category_name]
        current = self.parent_category
        
        while current:
            path.insert(0, current.category_name)
            current = current.parent_category
        
        return path
    
    def get_hierarchy_level(self) -> int:
        """Get the level of this category in the hierarchy (0 = root)"""
        level = 0
        current = self.parent_category
        
        while current:
            level += 1
            current = current.parent_category
        
        return level
    
    def is_child_of(self, potential_parent_id: UUID) -> bool:
        """Check if this category is a child of another category"""
        current = self.parent_category
        
        while current:
            if current.id == potential_parent_id:
                return True
            current = current.parent_category
        
        return False
    
    def get_all_child_categories(self) -> List['BenefitCategory']:
        """Get all child categories recursively"""
        children = []
        
        for child in self.child_categories:
            children.append(child)
            children.extend(child.get_all_child_categories())
        
        return children
    
    def to_dict(self, include_children: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        result = {
            'id': str(self.id),
            'category_code': self.category_code,
            'category_name': self.category_name,
            'category_name_ar': self.category_name_ar,
            'category_name_fr': self.category_name_fr,
            'description': self.description,
            'short_description': self.short_description,
            'category_type': self.category_type,
            'parent_category_id': str(self.parent_category_id) if self.parent_category_id else None,
            'display_order': self.display_order,
            'icon_name': self.icon_name,
            'color_code': self.color_code,
            'is_active': self.is_active,
            'is_visible': self.is_visible,
            'is_mandatory': self.is_mandatory,
            'requires_authorization': self.requires_authorization,
            'default_waiting_period_days': self.default_waiting_period_days,
            'hierarchy_level': self.get_hierarchy_level(),
            'hierarchy_path': self.get_full_hierarchy_path(),
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_children:
            result['child_categories'] = [
                child.to_dict(include_children=False) 
                for child in sorted(self.child_categories, key=lambda x: x.display_order)
            ]
        
        return result
    
    def __repr__(self) -> str:
        return f"<BenefitCategory(id={self.id}, code='{self.category_code}', name='{self.category_name}', type='{self.category_type}')>"
    
    def __str__(self) -> str:
        hierarchy_path = " > ".join(self.get_full_hierarchy_path())
        return f"{self.category_code}: {hierarchy_path}"


# ================================================================
# EXAMPLE USAGE AND COMMON PATTERNS
# ================================================================

"""
Common Benefit Category Examples:

1. ROOT CATEGORIES:
   - Medical Services (MED)
   - Dental Care (DENT) 
   - Vision Care (VIS)
   - Pharmacy (PHARM)
   - Wellness (WELL)

2. HIERARCHICAL STRUCTURE:
   Medical Services (MED)
   ├── Primary Care (MED_PRIMARY)
   ├── Specialist Care (MED_SPEC)
   │   ├── Cardiology (MED_CARDIO)
   │   └── Dermatology (MED_DERM)
   └── Emergency Care (MED_EMERG)

3. BUSINESS RULES EXAMPLES:
   {
       "requires_referral": true,
       "max_visits_per_year": 12,
       "geographic_restrictions": ["UAE", "KSA"]
   }

4. AGE RESTRICTIONS EXAMPLES:
   {
       "min_age": 18,
       "max_age": 65,
       "pediatric_only": false
   }
"""