# app/modules/benefits/models/benefit_limit_model.py
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional
import uuid

from app.core.database import Base


class BenefitLimit(Base):
    """
    Comprehensive model for benefit limits and restrictions.
    Handles all types of limits: monetary, frequency, quantity, time-based, etc.
    """
    
    __tablename__ = "benefit_limits"
    
    # =====================================================
    # PRIMARY FIELDS
    # =====================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    limit_code = Column(String(30), unique=True, nullable=False, index=True)
    limit_name = Column(String(100), nullable=False)
    limit_name_ar = Column(String(100), nullable=True)  # Arabic translation
    
    # =====================================================
    # LIMIT CLASSIFICATION
    # =====================================================
    
    limit_type = Column(String(30), nullable=False, index=True)
    # Options: MONETARY, FREQUENCY, QUANTITY, VISIT, TIME_BASED, AGGREGATE, LIFETIME
    
    limit_category = Column(String(30), nullable=False, default='COVERAGE')
    # Options: COVERAGE, DEDUCTIBLE, COPAY, COINSURANCE, OUT_OF_POCKET, BENEFIT_MAX
    
    limit_scope = Column(String(30), nullable=False, default='INDIVIDUAL')
    # Options: INDIVIDUAL, FAMILY, PER_INCIDENT, PER_CONDITION, AGGREGATE, LIFETIME
    
    # =====================================================
    # MONETARY LIMITS
    # =====================================================
    
    monetary_limit = Column(Numeric(15, 2), nullable=True)
    currency_code = Column(String(3), default='USD')
    
    # Deductible specific fields
    deductible_amount = Column(Numeric(15, 2), nullable=True)
    deductible_type = Column(String(20), nullable=True)
    # Options: INDIVIDUAL, FAMILY, EMBEDDED, NON_EMBEDDED, AGGREGATE
    
    # Out-of-pocket maximum
    out_of_pocket_max = Column(Numeric(15, 2), nullable=True)
    out_of_pocket_individual = Column(Numeric(15, 2), nullable=True)
    out_of_pocket_family = Column(Numeric(15, 2), nullable=True)
    
    # Copay limits
    copay_amount = Column(Numeric(10, 2), nullable=True)
    copay_percentage = Column(Numeric(5, 2), nullable=True)  # For percentage-based copays
    
    # Coinsurance limits
    coinsurance_percentage = Column(Numeric(5, 2), nullable=True)
    coinsurance_max = Column(Numeric(15, 2), nullable=True)
    
    # Coverage limits
    coverage_limit = Column(Numeric(15, 2), nullable=True)
    lifetime_limit = Column(Numeric(15, 2), nullable=True)
    annual_limit = Column(Numeric(15, 2), nullable=True)
    
    # =====================================================
    # FREQUENCY & QUANTITY LIMITS
    # =====================================================
    
    frequency_limit = Column(Integer, nullable=True)
    frequency_period = Column(String(20), nullable=True)
    # Options: DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUALLY, LIFETIME, PER_INCIDENT
    
    max_visits = Column(Integer, nullable=True)
    max_days = Column(Integer, nullable=True)
    max_units = Column(Integer, nullable=True)
    
    # Visit-specific limits
    visits_per_year = Column(Integer, nullable=True)
    visits_per_month = Column(Integer, nullable=True)
    visits_per_condition = Column(Integer, nullable=True)
    
    # =====================================================
    # TIME-BASED LIMITS
    # =====================================================
    
    waiting_period_days = Column(Integer, nullable=True)
    elimination_period_days = Column(Integer, nullable=True)
    benefit_period_days = Column(Integer, nullable=True)
    
    # Pre-existing condition limitations
    pre_existing_months = Column(Integer, nullable=True)
    pre_existing_lookback = Column(Integer, nullable=True)
    
    # Age-based limits
    age_limit_min = Column(Integer, nullable=True)
    age_limit_max = Column(Integer, nullable=True)
    
    # =====================================================
    # NETWORK & PROVIDER LIMITS
    # =====================================================
    
    network_type = Column(String(20), nullable=True)
    # Options: IN_NETWORK, OUT_OF_NETWORK, BOTH, PREFERRED, NON_PREFERRED
    
    in_network_limit = Column(Numeric(15, 2), nullable=True)
    out_of_network_limit = Column(Numeric(15, 2), nullable=True)
    
    in_network_percentage = Column(Numeric(5, 2), nullable=True)
    out_of_network_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Provider-specific limits
    specialist_limit = Column(Numeric(15, 2), nullable=True)
    referral_required = Column(Boolean, default=False)
    prior_auth_required = Column(Boolean, default=False)
    
    # =====================================================
    # GEOGRAPHIC & TEMPORAL RESTRICTIONS
    # =====================================================
    
    geographic_scope = Column(String(30), nullable=True)
    # Options: LOCAL, REGIONAL, NATIONAL, INTERNATIONAL, EMERGENCY_ONLY
    
    coverage_territory = Column(String(100), nullable=True)
    excluded_territories = Column(JSONB, nullable=True)
    
    # Time restrictions
    coverage_hours = Column(String(50), nullable=True)  # "24/7", "Business Hours", etc.
    seasonal_restrictions = Column(JSONB, nullable=True)
    
    # =====================================================
    # ACCUMULATOR SETTINGS
    # =====================================================
    
    accumulates_to_deductible = Column(Boolean, default=True)
    accumulates_to_oop = Column(Boolean, default=True)
    accumulates_to_benefit_max = Column(Boolean, default=True)
    
    # Cross-accumulation rules
    cross_accumulates = Column(Boolean, default=False)
    accumulation_family = Column(String(50), nullable=True)
    
    # Reset periods
    reset_period = Column(String(20), default='ANNUAL')
    # Options: ANNUAL, CALENDAR_YEAR, PLAN_YEAR, LIFETIME, NEVER
    
    reset_date = Column(DateTime, nullable=True)
    
    # =====================================================
    # RELATIONSHIPS & REFERENCES
    # =====================================================
    
    # Link to coverage or benefit type
    coverage_id = Column(UUID(as_uuid=True), ForeignKey('coverages.id'), nullable=True, index=True)
    benefit_type_id = Column(UUID(as_uuid=True), ForeignKey('benefit_types.id'), nullable=True, index=True)
    
    # Parent-child relationships for complex limits
    parent_limit_id = Column(UUID(as_uuid=True), ForeignKey('benefit_limits.id'), nullable=True)
    
    # =====================================================
    # BUSINESS RULES & CONDITIONS
    # =====================================================
    
    # Conditions for limit application
    conditions = Column(JSONB, nullable=True)
    # Example: {"age_range": {"min": 18, "max": 65}, "gender": "F", "state": "TX"}
    
    # Exception rules
    exceptions = Column(JSONB, nullable=True)
    # Example: {"emergency_override": true, "life_threatening": "no_limit"}
    
    # Calculation rules
    calculation_rules = Column(JSONB, nullable=True)
    # Example: {"rounding": "up", "minimum_charge": 50.00}
    
    # Override permissions
    can_override = Column(Boolean, default=False)
    override_level = Column(String(20), nullable=True)
    # Options: SUPERVISOR, MANAGER, UNDERWRITER, MEDICAL_DIRECTOR
    
    # =====================================================
    # STATUS & CONTROL
    # =====================================================
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_mandatory = Column(Boolean, default=False)
    is_system_generated = Column(Boolean, default=False)
    
    # Effective dates
    effective_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    effective_to = Column(DateTime, nullable=True)
    
    # =====================================================
    # DISPLAY & FORMATTING
    # =====================================================
    
    display_format = Column(String(50), nullable=True)
    # Options: CURRENCY, PERCENTAGE, VISITS, DAYS, UNITS
    
    display_order = Column(Integer, default=1)
    is_highlighted = Column(Boolean, default=False)
    
    # User-friendly descriptions
    member_description = Column(Text, nullable=True)
    member_description_ar = Column(Text, nullable=True)
    
    # =====================================================
    # METADATA & AUDIT
    # =====================================================
    
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Regulatory information
    regulatory_code = Column(String(50), nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
    # Source information
    source_system = Column(String(50), nullable=True)
    external_id = Column(String(50), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    
    # =====================================================
    # RELATIONSHIPS
    # =====================================================
    
    # Parent-child relationship for complex limits
    child_limits = relationship("BenefitLimit", backref="parent_limit", remote_side=[id])
    
    # Relationships will be defined when other models are created
    # coverage = relationship("Coverage", back_populates="limits")
    # benefit_type = relationship("BenefitType", back_populates="limits")
    
    # =====================================================
    # INDEXES
    # =====================================================
    
    __table_args__ = (
        Index('idx_benefit_limits_type_category', 'limit_type', 'limit_category'),
        Index('idx_benefit_limits_scope_network', 'limit_scope', 'network_type'),
        Index('idx_benefit_limits_active_effective', 'is_active', 'effective_from', 'effective_to'),
        Index('idx_benefit_limits_coverage_benefit', 'coverage_id', 'benefit_type_id'),
        Index('idx_benefit_limits_monetary', 'monetary_limit', 'currency_code'),
        Index('idx_benefit_limits_frequency', 'frequency_limit', 'frequency_period'),
    )
    
    # =====================================================
    # BUSINESS METHODS
    # =====================================================
    
    def calculate_member_responsibility(
        self, 
        service_cost: Decimal, 
        deductible_met: Decimal = Decimal('0'),
        out_of_pocket_met: Decimal = Decimal('0'),
        is_in_network: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate member's financial responsibility based on this limit.
        Returns breakdown of deductible, copay/coinsurance, and total member cost.
        """
        service_cost = Decimal(str(service_cost))
        deductible_met = Decimal(str(deductible_met))
        out_of_pocket_met = Decimal(str(out_of_pocket_met))
        
        result = {
            'service_cost': service_cost,
            'deductible_applied': Decimal('0'),
            'copay_coinsurance': Decimal('0'),
            'total_member_pays': Decimal('0'),
            'insurance_pays': Decimal('0'),
            'is_in_network': is_in_network,
            'coverage_applies': True
        }
        
        remaining_cost = service_cost
        member_share = Decimal('0')
        
        # Apply deductible first
        if self.deductible_amount:
            deductible_amount = Decimal(str(self.deductible_amount))
            remaining_deductible = max(Decimal('0'), deductible_amount - deductible_met)
            deductible_portion = min(remaining_cost, remaining_deductible)
            result['deductible_applied'] = deductible_portion
            remaining_cost -= deductible_portion
            member_share += deductible_portion
        
        # Apply copay or coinsurance
        if remaining_cost > 0:
            if self.copay_amount:
                # Fixed copay
                copay = min(remaining_cost, Decimal(str(self.copay_amount)))
                result['copay_coinsurance'] = copay
                member_share += copay
                remaining_cost -= copay
            elif self.coinsurance_percentage:
                # Percentage coinsurance
                coinsurance_rate = Decimal(str(self.coinsurance_percentage)) / 100
                coinsurance = remaining_cost * coinsurance_rate
                
                # Apply coinsurance maximum if set
                if self.coinsurance_max:
                    coinsurance = min(coinsurance, Decimal(str(self.coinsurance_max)))
                
                result['copay_coinsurance'] = coinsurance
                member_share += coinsurance
                remaining_cost -= coinsurance
        
        # Apply coverage limits
        insurance_pays = remaining_cost
        if self.coverage_limit:
            coverage_limit = Decimal(str(self.coverage_limit))
            if insurance_pays > coverage_limit:
                excess = insurance_pays - coverage_limit
                insurance_pays = coverage_limit
                member_share += excess
        
        # Apply out-of-pocket maximum
        total_member_cost = member_share
        if self.out_of_pocket_max:
            oop_max = Decimal(str(self.out_of_pocket_max))
            remaining_oop = max(Decimal('0'), oop_max - out_of_pocket_met)
            
            if total_member_cost > remaining_oop:
                # Member has hit out-of-pocket max
                excess_covered = total_member_cost - remaining_oop
                total_member_cost = remaining_oop
                insurance_pays += excess_covered
        
        result['total_member_pays'] = total_member_cost
        result['insurance_pays'] = insurance_pays
        result['coverage_applies'] = insurance_pays > 0 or total_member_cost < service_cost
        
        return result
    
    def check_frequency_limit(self, current_usage: int, period: str = None) -> Dict[str, Any]:
        """Check if current usage is within frequency limits"""
        period_to_check = period or self.frequency_period
        
        result = {
            'within_limit': True,
            'current_usage': current_usage,
            'limit': None,
            'period': period_to_check,
            'remaining': None
        }
        
        # Check frequency limit
        if self.frequency_limit:
            result['limit'] = self.frequency_limit
            result['within_limit'] = current_usage < self.frequency_limit
            result['remaining'] = max(0, self.frequency_limit - current_usage)
        
        # Check visit limits
        if self.max_visits:
            visit_limit = min(self.max_visits, result.get('limit', self.max_visits))
            result['limit'] = visit_limit
            result['within_limit'] = result['within_limit'] and current_usage < visit_limit
            result['remaining'] = max(0, visit_limit - current_usage)
        
        return result
    
    def is_effective_on_date(self, check_date: datetime = None) -> bool:
        """Check if limit is effective on a specific date"""
        if not check_date:
            check_date = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if self.effective_from and check_date < self.effective_from:
            return False
        
        if self.effective_to and check_date > self.effective_to:
            return False
        
        return True
    
    def applies_to_network(self, is_in_network: bool) -> bool:
        """Check if limit applies to the given network status"""
        if not self.network_type:
            return True  # No network restriction
        
        if self.network_type == 'BOTH':
            return True
        elif self.network_type == 'IN_NETWORK':
            return is_in_network
        elif self.network_type == 'OUT_OF_NETWORK':
            return not is_in_network
        
        return True
    
    def get_applicable_limit(self, is_in_network: bool = True) -> Optional[Decimal]:
        """Get the applicable monetary limit based on network status"""
        if not self.applies_to_network(is_in_network):
            return None
        
        if is_in_network and self.in_network_limit:
            return Decimal(str(self.in_network_limit))
        elif not is_in_network and self.out_of_network_limit:
            return Decimal(str(self.out_of_network_limit))
        elif self.monetary_limit:
            return Decimal(str(self.monetary_limit))
        elif self.coverage_limit:
            return Decimal(str(self.coverage_limit))
        
        return None
    
    def check_age_restrictions(self, age: int) -> bool:
        """Check if the limit applies to a specific age"""
        if self.age_limit_min and age < self.age_limit_min:
            return False
        if self.age_limit_max and age > self.age_limit_max:
            return False
        return True
    
    def format_for_display(self) -> str:
        """Format limit for member-friendly display"""
        if self.display_format == 'CURRENCY' and self.monetary_limit:
            return f"${self.monetary_limit:,.2f}"
        elif self.display_format == 'PERCENTAGE' and self.coinsurance_percentage:
            return f"{self.coinsurance_percentage}%"
        elif self.display_format == 'VISITS' and self.max_visits:
            return f"{self.max_visits} visits per {self.frequency_period.lower()}"
        elif self.display_format == 'DAYS' and self.max_days:
            return f"{self.max_days} days"
        else:
            return self.limit_name
    
    def __repr__(self):
        return f"<BenefitLimit(id={self.id}, code='{self.limit_code}', type='{self.limit_type}', limit={self.monetary_limit})>"