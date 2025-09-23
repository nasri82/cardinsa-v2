# app/modules/pricing/product/models/actuarial_table_model.py

"""
Actuarial Table Model

Manages actuarial data including mortality tables, morbidity rates,
and other statistical data used for insurance pricing and risk assessment.
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, Date, Index, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import date


# ================================================================
# ENUMS
# ================================================================

class TableType(str, Enum):
    """Type of actuarial table"""
    MORTALITY = "mortality"
    MORBIDITY = "morbidity"
    LAPSE = "lapse"
    DISABILITY = "disability"
    ANNUITY = "annuity"
    LIFE_EXPECTANCY = "life_expectancy"
    CLAIM_FREQUENCY = "claim_frequency"
    CLAIM_SEVERITY = "claim_severity"
    EXPENSE = "expense"
    INVESTMENT_RETURN = "investment_return"
    RISK_ADJUSTMENT = "risk_adjustment"
    CUSTOM = "custom"


class TableStatus(str, Enum):
    """Status of actuarial table"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class GeographicScope(str, Enum):
    """Geographic scope of the table"""
    GLOBAL = "global"
    REGIONAL = "regional"
    NATIONAL = "national"
    STATE = "state"
    CITY = "city"
    CUSTOM = "custom"


class DemographicScope(str, Enum):
    """Demographic scope of the table"""
    GENERAL = "general"
    GENDER_SPECIFIC = "gender_specific"
    AGE_SPECIFIC = "age_specific"
    OCCUPATION_SPECIFIC = "occupation_specific"
    LIFESTYLE_SPECIFIC = "lifestyle_specific"
    MEDICAL_SPECIFIC = "medical_specific"


# ================================================================
# MODEL
# ================================================================

class ActuarialTable(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Actuarial Table Model
    
    Stores and manages actuarial data used for pricing, reserving,
    and risk assessment in insurance products.
    """
    
    __tablename__ = "actuarial_tables"
    __table_args__ = (
        # Indexes
        Index('idx_actuarial_table_name', 'table_name', unique=True),
        Index('idx_actuarial_table_type', 'table_type'),
        Index('idx_actuarial_table_status', 'status'),
        Index('idx_actuarial_table_active', 'is_active'),
        Index('idx_actuarial_table_effective', 'effective_date'),
        Index('idx_actuarial_table_version', 'version'),
        # Composite indexes
        Index('idx_actuarial_table_type_active', 'table_type', 'is_active'),
        Index('idx_actuarial_table_geo_demo', 'geographic_scope', 'demographic_scope'),
        # Constraints
        CheckConstraint('effective_date <= expiry_date', name='check_date_range'),
        {'extend_existing': True}
    )
    
    # ================================================================
    # CORE IDENTIFICATION
    # ================================================================
    
    # Basic Information
    table_name = Column(String(100), unique=True, nullable=False, comment="Unique table name")
    table_code = Column(String(50), nullable=True, unique=True, comment="Table code for reference")
    table_type = Column(String(30), nullable=False, default=TableType.MORTALITY.value, comment="Type of actuarial table")
    version = Column(String(20), nullable=False, default="1.0", comment="Table version")
    
    # Description
    description = Column(Text, nullable=True, comment="Detailed description of the table")
    purpose = Column(Text, nullable=True, comment="Purpose and use cases for this table")
    methodology = Column(Text, nullable=True, comment="Methodology used to create the table")
    
    # ================================================================
    # VALIDITY & SCOPE
    # ================================================================
    
    # Validity Period
    effective_date = Column(Date, nullable=False, default=date.today, comment="When table becomes effective")
    expiry_date = Column(Date, nullable=True, comment="When table expires")
    review_date = Column(Date, nullable=True, comment="Next review date")
    
    # Geographic Scope
    geographic_scope = Column(String(30), default=GeographicScope.NATIONAL.value, comment="Geographic applicability")
    countries = Column(JSONB, nullable=True, comment="List of applicable countries")
    regions = Column(JSONB, nullable=True, comment="List of applicable regions")
    
    # Demographic Scope
    demographic_scope = Column(String(30), default=DemographicScope.GENERAL.value, comment="Demographic applicability")
    gender_specific = Column(String(10), nullable=True, comment="Gender specificity (M/F/null)")
    age_range_min = Column(Integer, nullable=True, comment="Minimum age for applicability")
    age_range_max = Column(Integer, nullable=True, comment="Maximum age for applicability")
    
    # ================================================================
    # TABLE DATA
    # ================================================================
    
    # Main Data Storage
    table_data = Column(JSONB, nullable=False, comment="Main actuarial data in JSON format")
    
    # Data Structure Definition
    data_structure = Column(JSONB, nullable=True, comment="Schema/structure of table_data")
    data_columns = Column(JSONB, nullable=True, comment="Column definitions and types")
    
    # Statistical Information
    data_points_count = Column(Integer, nullable=True, comment="Number of data points in table")
    last_data_update = Column(Date, nullable=True, comment="Last data update date")
    
    # ================================================================
    # SOURCE & VALIDATION
    # ================================================================
    
    # Data Source
    data_source = Column(String(200), nullable=True, comment="Source of actuarial data")
    source_organization = Column(String(200), nullable=True, comment="Organization providing data")
    source_reference = Column(Text, nullable=True, comment="Reference documents or publications")
    source_year = Column(Integer, nullable=True, comment="Year of source data")
    
    # Validation
    validation_status = Column(String(50), nullable=True, comment="Validation status")
    validation_date = Column(Date, nullable=True, comment="Date of last validation")
    validation_notes = Column(Text, nullable=True, comment="Validation notes and findings")
    confidence_level = Column(NUMERIC(5, 2), nullable=True, comment="Statistical confidence level")
    
    # ================================================================
    # REGULATORY & COMPLIANCE
    # ================================================================
    
    # Regulatory Information
    regulatory_approval = Column(Boolean, default=False, comment="Whether regulatory approved")
    regulatory_body = Column(String(100), nullable=True, comment="Approving regulatory body")
    approval_reference = Column(String(100), nullable=True, comment="Approval reference number")
    approval_date = Column(Date, nullable=True, comment="Date of regulatory approval")
    approved_by = Column(UUID(as_uuid=True), nullable=True, comment="User who approved")
    
    # Compliance
    compliance_standards = Column(JSONB, nullable=True, comment="Compliance standards met")
    audit_trail = Column(JSONB, nullable=True, comment="Audit trail of changes")
    
    # ================================================================
    # ADJUSTMENTS & FACTORS
    # ================================================================
    
    # Adjustment Factors
    base_adjustment_factor = Column(NUMERIC(8, 6), default=1.0, comment="Base adjustment factor")
    trend_factors = Column(JSONB, nullable=True, comment="Trend adjustment factors")
    improvement_factors = Column(JSONB, nullable=True, comment="Mortality/morbidity improvement factors")
    loading_factors = Column(JSONB, nullable=True, comment="Loading factors for conservatism")
    
    # Selection Factors
    selection_factors = Column(JSONB, nullable=True, comment="Selection period adjustments")
    ultimate_rates = Column(JSONB, nullable=True, comment="Ultimate rates after selection")
    
    # ================================================================
    # USAGE & DEPENDENCIES
    # ================================================================
    
    # Usage Configuration
    applicable_products = Column(JSONB, nullable=True, comment="List of applicable product types")
    applicable_coverages = Column(JSONB, nullable=True, comment="List of applicable coverages")
    usage_restrictions = Column(JSONB, nullable=True, comment="Usage restrictions and conditions")
    
    # Dependencies
    parent_table_id = Column(UUID(as_uuid=True), nullable=True, comment="Parent table if derived")
    related_tables = Column(JSONB, nullable=True, comment="Related actuarial tables")
    
    # ================================================================
    # OPERATIONAL SETTINGS
    # ================================================================
    
    # Status
    status = Column(String(30), default=TableStatus.DRAFT.value, comment="Current table status")
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether table is active")
    is_default = Column(Boolean, default=False, comment="Whether this is default for its type")
    priority_order = Column(Integer, default=100, comment="Priority for table selection")
    
    # ================================================================
    # PERFORMANCE & CACHING
    # ================================================================
    
    # Cache Configuration
    cache_enabled = Column(Boolean, default=True, comment="Whether caching is enabled")
    cache_duration_minutes = Column(Integer, default=1440, comment="Cache duration in minutes")
    last_cached_at = Column(DateTime, nullable=True, comment="Last cache timestamp")
    
    # Performance Metrics
    average_lookup_time_ms = Column(Integer, nullable=True, comment="Average lookup time in ms")
    total_lookups = Column(Integer, default=0, comment="Total number of lookups")
    
    # ================================================================
    # METADATA
    # ================================================================
    
    table_metadata = Column(JSONB, nullable=True, comment="Additional metadata")
    tags = Column(ARRAY(String), nullable=True, comment="Tags for categorization")
    notes = Column(Text, nullable=True, comment="General notes")
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    # Relationships with other models
    # Note: Add relationships as needed when other models are created
    
    # ================================================================
    # METHODS
    # ================================================================
    
    def __repr__(self) -> str:
        return f"<ActuarialTable(name={self.table_name}, type={self.table_type}, version={self.version})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            'id': str(self.id),
            'table_name': self.table_name,
            'table_code': self.table_code,
            'table_type': self.table_type,
            'version': self.version,
            'description': self.description,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'geographic_scope': self.geographic_scope,
            'demographic_scope': self.demographic_scope,
            'status': self.status,
            'is_active': self.is_active,
            'data_source': self.data_source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_rate(self, age: int, gender: str = None, **kwargs) -> Optional[float]:
        """
        Get rate from table for given parameters
        
        Args:
            age: Age to lookup
            gender: Gender (M/F) if applicable
            **kwargs: Additional lookup parameters
            
        Returns:
            Rate value or None if not found
        """
        if not self.table_data:
            return None
        
        # Simple lookup implementation - enhance based on actual data structure
        if isinstance(self.table_data, list):
            for entry in self.table_data:
                if entry.get('age') == age:
                    if gender and self.gender_specific:
                        if entry.get('gender') == gender:
                            return entry.get('rate')
                    else:
                        return entry.get('rate')
        
        return None
    
    def apply_adjustments(self, base_rate: float) -> float:
        """Apply adjustment factors to base rate"""
        adjusted_rate = base_rate
        
        # Apply base adjustment
        if self.base_adjustment_factor:
            adjusted_rate *= float(self.base_adjustment_factor)
        
        # Additional adjustments can be added here
        
        return adjusted_rate
    
    def is_valid_for_date(self, check_date: date = None) -> bool:
        """Check if table is valid for given date"""
        if not check_date:
            check_date = date.today()
        
        if self.effective_date and check_date < self.effective_date:
            return False
        
        if self.expiry_date and check_date > self.expiry_date:
            return False
        
        return self.is_active
    
    def is_applicable_for_age(self, age: int) -> bool:
        """Check if table is applicable for given age"""
        if self.age_range_min and age < self.age_range_min:
            return False
        if self.age_range_max and age > self.age_range_max:
            return False
        return True
    
    def get_improvement_factor(self, year: int) -> Optional[float]:
        """Get improvement factor for given year"""
        if not self.improvement_factors:
            return None
        
        return self.improvement_factors.get(str(year))
    
    def validate_data_structure(self) -> bool:
        """Validate that table_data matches defined structure"""
        if not self.data_structure or not self.table_data:
            return True  # No structure defined, assume valid
        
        # Implement validation logic based on your needs
        return True


# ================================================================
# END OF MODEL
# ================================================================