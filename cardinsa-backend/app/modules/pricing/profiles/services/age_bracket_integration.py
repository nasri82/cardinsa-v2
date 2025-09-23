# app/modules/pricing/profiles/services/age_bracket_integration.py
"""
Advanced Age Bracket Integration System for Step 6 Completion
Handles demographic pricing with age, gender, territory, and actuarial tables
"""

from typing import List, Optional, Dict, Any, Tuple, Union
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ValidationError, BusinessLogicError
from app.core.logging import get_logger

logger = get_logger(__name__)


class Gender(str, Enum):
    """Gender categories for demographic pricing."""
    MALE = "M"
    FEMALE = "F"
    UNSPECIFIED = "U"


class RiskCategory(str, Enum):
    """Risk categories for actuarial calculations."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class DemographicProfile:
    """Complete demographic profile for pricing."""
    age: int
    gender: Gender
    territory: str
    occupation: Optional[str] = None
    risk_factors: List[str] = field(default_factory=list)
    medical_history: Optional[Dict[str, Any]] = None
    family_history: Optional[Dict[str, Any]] = None


@dataclass
class AgeBracket:
    """Represents an age bracket with pricing factors."""
    bracket_id: UUID
    name: str
    min_age: int
    max_age: int
    base_factor: Decimal
    gender_factors: Dict[Gender, Decimal] = field(default_factory=dict)
    territory_factors: Dict[str, Decimal] = field(default_factory=dict)
    risk_adjustments: Dict[RiskCategory, Decimal] = field(default_factory=dict)
    benefit_specific_factors: Dict[str, Decimal] = field(default_factory=dict)
    effective_date: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    is_active: bool = True


@dataclass
class ActuarialTable:
    """Actuarial table for mortality/morbidity rates."""
    table_id: UUID
    name: str
    table_type: str  # MORTALITY, MORBIDITY, DISABILITY
    rates: Dict[str, Dict[str, Decimal]]  # {age: {gender: rate}}
    effective_date: datetime
    version: str
    description: Optional[str] = None


@dataclass
class PricingAdjustment:
    """Represents a pricing adjustment with details."""
    adjustment_type: str
    base_value: Decimal
    adjusted_value: Decimal
    factor: Decimal
    description: str
    source: str  # What caused this adjustment


class AdvancedAgeBracketIntegration:
    """
    Advanced system for age bracket integration with demographics and actuarial data.
    Handles complex pricing scenarios with multiple demographic factors.
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.age_brackets: Dict[UUID, AgeBracket] = {}
        self.actuarial_tables: Dict[UUID, ActuarialTable] = {}
        self.territory_definitions: Dict[str, Dict[str, Any]] = {}
        self.occupation_risk_mapping: Dict[str, RiskCategory] = {}
    
    # ============================================================================
    # AGE BRACKET MANAGEMENT
    # ============================================================================
    
    def create_age_bracket(
        self,
        name: str,
        min_age: int,
        max_age: int,
        base_factor: Decimal,
        benefit_type: Optional[str] = None
    ) -> AgeBracket:
        """
        Create a new age bracket with validation.
        
        Args:
            name: Human-readable name for the bracket
            min_age: Minimum age (inclusive)
            max_age: Maximum age (inclusive)
            base_factor: Base pricing factor
            benefit_type: Optional benefit type for specific brackets
            
        Returns:
            Created age bracket
        """
        if min_age < 0 or max_age < 0:
            raise ValidationError("Age values cannot be negative")
        
        if min_age > max_age:
            raise ValidationError("Minimum age cannot be greater than maximum age")
        
        # Check for overlapping brackets
        overlapping = self._find_overlapping_brackets(min_age, max_age, benefit_type)
        if overlapping:
            logger.warning(f"Age bracket overlaps with existing brackets: {overlapping}")
        
        bracket = AgeBracket(
            bracket_id=UUID.hex,
            name=name,
            min_age=min_age,
            max_age=max_age,
            base_factor=base_factor
        )
        
        # Set default gender factors (can be customized later)
        bracket.gender_factors = {
            Gender.MALE: Decimal('1.0'),
            Gender.FEMALE: Decimal('1.0'),
            Gender.UNSPECIFIED: Decimal('1.0')
        }
        
        self.age_brackets[bracket.bracket_id] = bracket
        
        logger.info(f"Created age bracket: {name} ({min_age}-{max_age}) with factor {base_factor}")
        
        return bracket
    
    def update_gender_factors(
        self,
        bracket_id: UUID,
        gender_factors: Dict[Gender, Decimal]
    ):
        """Update gender-specific factors for an age bracket."""
        if bracket_id not in self.age_brackets:
            raise ValidationError(f"Age bracket {bracket_id} not found")
        
        self.age_brackets[bracket_id].gender_factors.update(gender_factors)
        logger.info(f"Updated gender factors for bracket {bracket_id}")
    
    def update_territory_factors(
        self,
        bracket_id: UUID,
        territory_factors: Dict[str, Decimal]
    ):
        """Update territory-specific factors for an age bracket."""
        if bracket_id not in self.age_brackets:
            raise ValidationError(f"Age bracket {bracket_id} not found")
        
        self.age_brackets[bracket_id].territory_factors.update(territory_factors)
        logger.info(f"Updated territory factors for bracket {bracket_id}")
    
    def update_benefit_factors(
        self,
        bracket_id: UUID,
        benefit_factors: Dict[str, Decimal]
    ):
        """Update benefit-specific factors for an age bracket."""
        if bracket_id not in self.age_brackets:
            raise ValidationError(f"Age bracket {bracket_id} not found")
        
        self.age_brackets[bracket_id].benefit_specific_factors.update(benefit_factors)
        logger.info(f"Updated benefit-specific factors for bracket {bracket_id}")
    
    # ============================================================================
    # DEMOGRAPHIC PRICING CALCULATIONS
    # ============================================================================
    
    def calculate_demographic_pricing(
        self,
        base_premium: Decimal,
        demographic_profile: DemographicProfile,
        benefit_type: Optional[str] = None,
        include_actuarial: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate complete demographic pricing with all factors.
        
        Args:
            base_premium: Base premium amount
            demographic_profile: Complete demographic information
            benefit_type: Specific benefit type for targeted pricing
            include_actuarial: Whether to include actuarial adjustments
            
        Returns:
            Detailed pricing calculation with breakdown
        """
        # Find applicable age bracket
        age_bracket = self._find_age_bracket(demographic_profile.age, benefit_type)
        if not age_bracket:
            raise BusinessLogicError(f"No age bracket found for age {demographic_profile.age}")
        
        adjustments = []
        final_premium = base_premium
        
        # 1. Apply base age factor
        age_adjustment = PricingAdjustment(
            adjustment_type="AGE_BRACKET",
            base_value=final_premium,
            adjusted_value=final_premium * age_bracket.base_factor,
            factor=age_bracket.base_factor,
            description=f"Age bracket {age_bracket.name} ({age_bracket.min_age}-{age_bracket.max_age})",
            source="age_bracket_base_factor"
        )
        adjustments.append(age_adjustment)
        final_premium = age_adjustment.adjusted_value
        
        # 2. Apply gender factor
        gender_factor = age_bracket.gender_factors.get(demographic_profile.gender, Decimal('1.0'))
        if gender_factor != Decimal('1.0'):
            gender_adjustment = PricingAdjustment(
                adjustment_type="GENDER",
                base_value=final_premium,
                adjusted_value=final_premium * gender_factor,
                factor=gender_factor,
                description=f"Gender factor for {demographic_profile.gender.value}",
                source="gender_demographic"
            )
            adjustments.append(gender_adjustment)
            final_premium = gender_adjustment.adjusted_value
        
        # 3. Apply territory factor
        territory_factor = age_bracket.territory_factors.get(demographic_profile.territory, Decimal('1.0'))
        if territory_factor != Decimal('1.0'):
            territory_adjustment = PricingAdjustment(
                adjustment_type="TERRITORY",
                base_value=final_premium,
                adjusted_value=final_premium * territory_factor,
                factor=territory_factor,
                description=f"Territory factor for {demographic_profile.territory}",
                source="territory_demographic"
            )
            adjustments.append(territory_adjustment)
            final_premium = territory_adjustment.adjusted_value
        
        # 4. Apply benefit-specific factors
        if benefit_type and benefit_type in age_bracket.benefit_specific_factors:
            benefit_factor = age_bracket.benefit_specific_factors[benefit_type]
            benefit_adjustment = PricingAdjustment(
                adjustment_type="BENEFIT_SPECIFIC",
                base_value=final_premium,
                adjusted_value=final_premium * benefit_factor,
                factor=benefit_factor,
                description=f"Benefit-specific factor for {benefit_type}",
                source="benefit_specific_pricing"
            )
            adjustments.append(benefit_adjustment)
            final_premium = benefit_adjustment.adjusted_value
        
        # 5. Apply risk factors
        risk_adjustments = self._calculate_risk_adjustments(
            final_premium, demographic_profile, age_bracket
        )
        adjustments.extend(risk_adjustments)
        for adj in risk_adjustments:
            final_premium = adj.adjusted_value
        
        # 6. Apply actuarial adjustments if requested
        if include_actuarial:
            actuarial_adjustments = self._calculate_actuarial_adjustments(
                final_premium, demographic_profile, benefit_type
            )
            adjustments.extend(actuarial_adjustments)
            for adj in actuarial_adjustments:
                final_premium = adj.adjusted_value
        
        return {
            "base_premium": base_premium,
            "final_premium": final_premium,
            "total_factor": final_premium / base_premium if base_premium > 0 else Decimal('1.0'),
            "age_bracket": {
                "id": str(age_bracket.bracket_id),
                "name": age_bracket.name,
                "min_age": age_bracket.min_age,
                "max_age": age_bracket.max_age
            },
            "demographic_profile": {
                "age": demographic_profile.age,
                "gender": demographic_profile.gender.value,
                "territory": demographic_profile.territory,
                "occupation": demographic_profile.occupation,
                "risk_factors": demographic_profile.risk_factors
            },
            "adjustments": [
                {
                    "type": adj.adjustment_type,
                    "base_value": float(adj.base_value),
                    "adjusted_value": float(adj.adjusted_value),
                    "factor": float(adj.factor),
                    "description": adj.description,
                    "source": adj.source
                }
                for adj in adjustments
            ],
            "calculation_timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_risk_adjustments(
        self,
        current_premium: Decimal,
        demographic_profile: DemographicProfile,
        age_bracket: AgeBracket
    ) -> List[PricingAdjustment]:
        """Calculate risk-based adjustments."""
        adjustments = []
        
        # Occupation risk adjustment
        if demographic_profile.occupation:
            risk_category = self.occupation_risk_mapping.get(
                demographic_profile.occupation, 
                RiskCategory.MEDIUM
            )
            
            risk_factor = age_bracket.risk_adjustments.get(risk_category, Decimal('1.0'))
            if risk_factor != Decimal('1.0'):
                risk_adjustment = PricingAdjustment(
                    adjustment_type="OCCUPATION_RISK",
                    base_value=current_premium,
                    adjusted_value=current_premium * risk_factor,
                    factor=risk_factor,
                    description=f"Occupation risk: {demographic_profile.occupation} ({risk_category.value})",
                    source="occupation_risk_mapping"
                )
                adjustments.append(risk_adjustment)
                current_premium = risk_adjustment.adjusted_value
        
        # Individual risk factors
        for risk_factor in demographic_profile.risk_factors:
            factor = self._get_risk_factor_adjustment(risk_factor, demographic_profile.age)
            if factor != Decimal('1.0'):
                risk_adjustment = PricingAdjustment(
                    adjustment_type="INDIVIDUAL_RISK",
                    base_value=current_premium,
                    adjusted_value=current_premium * factor,
                    factor=factor,
                    description=f"Risk factor: {risk_factor}",
                    source="individual_risk_assessment"
                )
                adjustments.append(risk_adjustment)
                current_premium = risk_adjustment.adjusted_value
        
        return adjustments
    
    def _calculate_actuarial_adjustments(
        self,
        current_premium: Decimal,
        demographic_profile: DemographicProfile,
        benefit_type: Optional[str]
    ) -> List[PricingAdjustment]:
        """Calculate actuarial table-based adjustments."""
        adjustments = []
        
        # Find relevant actuarial tables
        relevant_tables = self._find_relevant_actuarial_tables(benefit_type)
        
        for table in relevant_tables:
            rate = self._get_actuarial_rate(table, demographic_profile.age, demographic_profile.gender)
            if rate and rate != Decimal('1.0'):
                actuarial_adjustment = PricingAdjustment(
                    adjustment_type="ACTUARIAL",
                    base_value=current_premium,
                    adjusted_value=current_premium * rate,
                    factor=rate,
                    description=f"Actuarial adjustment from {table.name}",
                    source=f"actuarial_table_{table.table_id}"
                )
                adjustments.append(actuarial_adjustment)
                current_premium = actuarial_adjustment.adjusted_value
        
        return adjustments
    
    # ============================================================================
    # DYNAMIC BRACKET CREATION
    # ============================================================================
    
    def create_dynamic_age_brackets(
        self,
        min_age: int,
        max_age: int,
        bracket_size: int,
        base_factor_progression: str = "linear",
        factor_range: Tuple[Decimal, Decimal] = (Decimal('0.5'), Decimal('2.0'))
    ) -> List[AgeBracket]:
        """
        Dynamically create age brackets with specified parameters.
        
        Args:
            min_age: Starting age
            max_age: Ending age
            bracket_size: Size of each bracket in years
            base_factor_progression: How factors progress (linear, exponential, logarithmic)
            factor_range: Range of factors (min, max)
            
        Returns:
            List of created age brackets
        """
        brackets = []
        min_factor, max_factor = factor_range
        age_range = max_age - min_age
        
        current_age = min_age
        bracket_index = 0
        
        while current_age <= max_age:
            bracket_end = min(current_age + bracket_size - 1, max_age)
            
            # Calculate factor based on progression type
            if base_factor_progression == "linear":
                progress = (current_age - min_age) / age_range if age_range > 0 else 0
                factor = min_factor + (max_factor - min_factor) * Decimal(str(progress))
            
            elif base_factor_progression == "exponential":
                progress = (current_age - min_age) / age_range if age_range > 0 else 0
                factor = min_factor * ((max_factor / min_factor) ** Decimal(str(progress)))
            
            else:  # Default to linear
                progress = (current_age - min_age) / age_range if age_range > 0 else 0
                factor = min_factor + (max_factor - min_factor) * Decimal(str(progress))
            
            bracket = self.create_age_bracket(
                name=f"Age {current_age}-{bracket_end}",
                min_age=current_age,
                max_age=bracket_end,
                base_factor=factor
            )
            
            brackets.append(bracket)
            current_age = bracket_end + 1
            bracket_index += 1
        
        logger.info(f"Created {len(brackets)} dynamic age brackets from {min_age} to {max_age}")
        return brackets
    
    # ============================================================================
    # BENEFIT-SPECIFIC PRICING
    # ============================================================================
    
    def apply_benefit_specific_rules(
        self,
        base_calculation: Dict[str, Any],
        benefit_type: str,
        benefit_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply benefit-specific pricing rules and adjustments.
        
        Args:
            base_calculation: Base demographic calculation
            benefit_type: Type of benefit (medical, dental, vision, etc.)
            benefit_details: Specific benefit configuration
            
        Returns:
            Enhanced calculation with benefit-specific adjustments
        """
        enhanced_calculation = base_calculation.copy()
        additional_adjustments = []
        
        current_premium = base_calculation["final_premium"]
        
        # Benefit type specific adjustments
        if benefit_type == "DENTAL":
            # Dental benefits typically have lower age progression
            dental_factor = self._calculate_dental_age_factor(
                base_calculation["demographic_profile"]["age"]
            )
            dental_adjustment = PricingAdjustment(
                adjustment_type="DENTAL_SPECIFIC",
                base_value=current_premium,
                adjusted_value=current_premium * dental_factor,
                factor=dental_factor,
                description="Dental-specific age adjustment",
                source="dental_benefit_rules"
            )
            additional_adjustments.append(dental_adjustment)
            current_premium = dental_adjustment.adjusted_value
        
        elif benefit_type == "VISION":
            # Vision benefits have different age patterns
            vision_factor = self._calculate_vision_age_factor(
                base_calculation["demographic_profile"]["age"]
            )
            vision_adjustment = PricingAdjustment(
                adjustment_type="VISION_SPECIFIC",
                base_value=current_premium,
                adjusted_value=current_premium * vision_factor,
                factor=vision_factor,
                description="Vision-specific age adjustment",
                source="vision_benefit_rules"
            )
            additional_adjustments.append(vision_adjustment)
            current_premium = vision_adjustment.adjusted_value
        
        elif benefit_type == "MEDICAL":
            # Medical benefits may have utilization-based adjustments
            utilization_factor = self._calculate_medical_utilization_factor(
                base_calculation["demographic_profile"]["age"],
                base_calculation["demographic_profile"]["gender"]
            )
            medical_adjustment = PricingAdjustment(
                adjustment_type="MEDICAL_UTILIZATION",
                base_value=current_premium,
                adjusted_value=current_premium * utilization_factor,
                factor=utilization_factor,
                description="Medical utilization adjustment",
                source="medical_utilization_patterns"
            )
            additional_adjustments.append(medical_adjustment)
            current_premium = medical_adjustment.adjusted_value
        
        # Apply benefit configuration adjustments
        if "coverage_limits" in benefit_details:
            limit_factor = self._calculate_coverage_limit_factor(benefit_details["coverage_limits"])
            limit_adjustment = PricingAdjustment(
                adjustment_type="COVERAGE_LIMIT",
                base_value=current_premium,
                adjusted_value=current_premium * limit_factor,
                factor=limit_factor,
                description=f"Coverage limit adjustment: {benefit_details['coverage_limits']}",
                source="benefit_configuration"
            )
            additional_adjustments.append(limit_adjustment)
            current_premium = limit_adjustment.adjusted_value
        
        # Update enhanced calculation
        enhanced_calculation["final_premium"] = current_premium
        enhanced_calculation["benefit_type"] = benefit_type
        enhanced_calculation["benefit_details"] = benefit_details
        
        # Add new adjustments to existing ones
        all_adjustments = base_calculation["adjustments"] + [
            {
                "type": adj.adjustment_type,
                "base_value": float(adj.base_value),
                "adjusted_value": float(adj.adjusted_value),
                "factor": float(adj.factor),
                "description": adj.description,
                "source": adj.source
            }
            for adj in additional_adjustments
        ]
        enhanced_calculation["adjustments"] = all_adjustments
        
        return enhanced_calculation
    
    # ============================================================================
    # ACTUARIAL TABLE MANAGEMENT
    # ============================================================================
    
    def load_actuarial_table(
        self,
        name: str,
        table_type: str,
        rates_data: Dict[str, Dict[str, float]],
        version: str,
        description: Optional[str] = None
    ) -> ActuarialTable:
        """
        Load an actuarial table into the system.
        
        Args:
            name: Name of the actuarial table
            table_type: Type (MORTALITY, MORBIDITY, DISABILITY)
            rates_data: Rates by age and gender
            version: Version identifier
            description: Optional description
            
        Returns:
            Created actuarial table
        """
        # Convert rates to Decimal for precision
        decimal_rates = {}
        for age_str, gender_rates in rates_data.items():
            decimal_rates[age_str] = {
                gender: Decimal(str(rate))
                for gender, rate in gender_rates.items()
            }
        
        table = ActuarialTable(
            table_id=UUID.hex,
            name=name,
            table_type=table_type,
            rates=decimal_rates,
            effective_date=datetime.utcnow(),
            version=version,
            description=description
        )
        
        self.actuarial_tables[table.table_id] = table
        
        logger.info(f"Loaded actuarial table: {name} (type: {table_type}, version: {version})")
        
        return table
    
    def get_actuarial_rate(
        self,
        table_id: UUID,
        age: int,
        gender: Gender
    ) -> Optional[Decimal]:
        """Get actuarial rate for specific age and gender."""
        if table_id not in self.actuarial_tables:
            return None
        
        table = self.actuarial_tables[table_id]
        return self._get_actuarial_rate(table, age, gender)
    
    def _get_actuarial_rate(
        self,
        table: ActuarialTable,
        age: int,
        gender: Gender
    ) -> Optional[Decimal]:
        """Internal method to get actuarial rate."""
        age_str = str(age)
        
        if age_str in table.rates:
            gender_rates = table.rates[age_str]
            if gender.value in gender_rates:
                return gender_rates[gender.value]
            elif "UNISEX" in gender_rates:
                return gender_rates["UNISEX"]
        
        # Try to interpolate between nearby ages
        return self._interpolate_actuarial_rate(table, age, gender)
    
    def _interpolate_actuarial_rate(
        self,
        table: ActuarialTable,
        age: int,
        gender: Gender
    ) -> Optional[Decimal]:
        """Interpolate actuarial rate between available ages."""
        available_ages = [int(age_str) for age_str in table.rates.keys()]
        if not available_ages:
            return None
        
        available_ages.sort()
        
        # Find bounding ages
        lower_age = None
        upper_age = None
        
        for available_age in available_ages:
            if available_age <= age:
                lower_age = available_age
            if available_age >= age and upper_age is None:
                upper_age = available_age
                break
        
        # If exact match or no interpolation possible
        if lower_age == age:
            return self._get_rate_for_age(table, lower_age, gender)
        
        if lower_age is None or upper_age is None:
            # Use closest available age
            closest_age = min(available_ages, key=lambda x: abs(x - age))
            return self._get_rate_for_age(table, closest_age, gender)
        
        # Linear interpolation
        lower_rate = self._get_rate_for_age(table, lower_age, gender)
        upper_rate = self._get_rate_for_age(table, upper_age, gender)
        
        if lower_rate is None or upper_rate is None:
            return None
        
        # Interpolation formula
        weight = (age - lower_age) / (upper_age - lower_age)
        interpolated_rate = lower_rate + (upper_rate - lower_rate) * Decimal(str(weight))
        
        return interpolated_rate
    
    def _get_rate_for_age(
        self,
        table: ActuarialTable,
        age: int,
        gender: Gender
    ) -> Optional[Decimal]:
        """Get rate for specific age, handling gender fallbacks."""
        age_str = str(age)
        if age_str not in table.rates:
            return None
        
        gender_rates = table.rates[age_str]
        
        # Try exact gender match first
        if gender.value in gender_rates:
            return gender_rates[gender.value]
        
        # Fallback to unisex if available
        if "UNISEX" in gender_rates:
            return gender_rates["UNISEX"]
        
        # Fallback to average of available genders
        if gender_rates:
            rates = list(gender_rates.values())
            return sum(rates) / len(rates)
        
        return None
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _find_age_bracket(self, age: int, benefit_type: Optional[str] = None) -> Optional[AgeBracket]:
        """Find the appropriate age bracket for given age and benefit type."""
        candidates = []
        
        for bracket in self.age_brackets.values():
            if bracket.is_active and bracket.min_age <= age <= bracket.max_age:
                # If benefit type is specified, prefer brackets with specific factors
                if benefit_type and benefit_type in bracket.benefit_specific_factors:
                    candidates.insert(0, bracket)  # Prioritize benefit-specific brackets
                else:
                    candidates.append(bracket)
        
        return candidates[0] if candidates else None
    
    def _find_overlapping_brackets(
        self,
        min_age: int,
        max_age: int,
        benefit_type: Optional[str] = None
    ) -> List[AgeBracket]:
        """Find existing brackets that overlap with the given age range."""
        overlapping = []
        
        for bracket in self.age_brackets.values():
            if bracket.is_active:
                # Check for overlap
                if (min_age <= bracket.max_age and max_age >= bracket.min_age):
                    overlapping.append(bracket)
        
        return overlapping
    
    def _find_relevant_actuarial_tables(self, benefit_type: Optional[str]) -> List[ActuarialTable]:
        """Find actuarial tables relevant to the benefit type."""
        relevant_tables = []
        
        for table in self.actuarial_tables.values():
            # Map benefit types to actuarial table types
            if benefit_type == "MEDICAL" and table.table_type in ["MORBIDITY", "MORTALITY"]:
                relevant_tables.append(table)
            elif benefit_type == "DISABILITY" and table.table_type == "DISABILITY":
                relevant_tables.append(table)
            elif benefit_type == "LIFE" and table.table_type == "MORTALITY":
                relevant_tables.append(table)
            elif not benefit_type:  # Use all tables if no specific benefit type
                relevant_tables.append(table)
        
        return relevant_tables
    
    def _get_risk_factor_adjustment(self, risk_factor: str, age: int) -> Decimal:
        """Get risk factor adjustment based on factor type and age."""
        # Risk factor mapping with age-dependent adjustments
        risk_adjustments = {
            "SMOKING": {
                "base_factor": Decimal('1.5'),
                "age_multiplier": lambda age: Decimal('1.0') + Decimal('0.01') * (age - 18) if age > 18 else Decimal('1.0')
            },
            "DIABETES": {
                "base_factor": Decimal('1.3'),
                "age_multiplier": lambda age: Decimal('1.0') + Decimal('0.005') * (age - 30) if age > 30 else Decimal('1.0')
            },
            "HYPERTENSION": {
                "base_factor": Decimal('1.2'),
                "age_multiplier": lambda age: Decimal('1.0') + Decimal('0.003') * (age - 40) if age > 40 else Decimal('1.0')
            },
            "FAMILY_HISTORY_CARDIAC": {
                "base_factor": Decimal('1.15'),
                "age_multiplier": lambda age: Decimal('1.0') + Decimal('0.002') * (age - 35) if age > 35 else Decimal('1.0')
            }
        }
        
        if risk_factor in risk_adjustments:
            config = risk_adjustments[risk_factor]
            base_factor = config["base_factor"]
            age_multiplier = config["age_multiplier"](age)
            return base_factor * age_multiplier
        
        # Default adjustment for unknown risk factors
        return Decimal('1.1')
    
    def _calculate_dental_age_factor(self, age: int) -> Decimal:
        """Calculate dental-specific age factor."""
        if age < 18:
            return Decimal('0.6')  # Children have higher dental needs
        elif age < 35:
            return Decimal('0.8')  # Young adults, lower utilization
        elif age < 55:
            return Decimal('1.0')  # Standard rates
        elif age < 65:
            return Decimal('1.2')  # Increased maintenance needs
        else:
            return Decimal('1.4')  # Senior dental care needs
    
    def _calculate_vision_age_factor(self, age: int) -> Decimal:
        """Calculate vision-specific age factor."""
        if age < 25:
            return Decimal('0.7')  # Lower vision correction needs
        elif age < 40:
            return Decimal('0.9')  # Minimal age-related changes
        elif age < 50:
            return Decimal('1.1')  # Beginning presbyopia
        elif age < 60:
            return Decimal('1.3')  # Increased correction needs
        else:
            return Decimal('1.5')  # Complex vision issues
    
    def _calculate_medical_utilization_factor(self, age: int, gender: Gender) -> Decimal:
        """Calculate medical utilization factor based on age and gender."""
        base_factor = Decimal('1.0')
        
        # Age-based utilization
        if age < 5:
            base_factor = Decimal('1.4')  # High pediatric utilization
        elif age < 18:
            base_factor = Decimal('0.8')  # Lower utilization for children
        elif age < 30:
            base_factor = Decimal('0.9')  # Young adults
        elif age < 50:
            base_factor = Decimal('1.0')  # Standard utilization
        elif age < 65:
            base_factor = Decimal('1.3')  # Increased health issues
        else:
            base_factor = Decimal('1.8')  # High senior utilization
        
        # Gender-based adjustments
        if gender == Gender.FEMALE:
            if 18 <= age <= 45:
                base_factor *= Decimal('1.2')  # Reproductive health
        
        return base_factor
    
    def _calculate_coverage_limit_factor(self, coverage_limits: Dict[str, Any]) -> Decimal:
        """Calculate factor based on coverage limits."""
        # Example implementation - adjust based on actual limit structures
        if isinstance(coverage_limits, dict):
            annual_limit = coverage_limits.get("annual_limit", 0)
            if annual_limit:
                if annual_limit < 1000:
                    return Decimal('0.6')  # Low coverage
                elif annual_limit < 5000:
                    return Decimal('0.8')  # Medium coverage
                elif annual_limit < 10000:
                    return Decimal('1.0')  # Standard coverage
                else:
                    return Decimal('1.2')  # High coverage
        
        return Decimal('1.0')  # Default
    
    # ============================================================================
    # CONFIGURATION MANAGEMENT
    # ============================================================================
    
    def load_territory_definitions(self, territories: Dict[str, Dict[str, Any]]):
        """Load territory definitions with risk factors."""
        self.territory_definitions = territories
        logger.info(f"Loaded {len(territories)} territory definitions")
    
    def load_occupation_risk_mapping(self, mappings: Dict[str, str]):
        """Load occupation to risk category mappings."""
        self.occupation_risk_mapping = {
            occupation: RiskCategory(risk_level)
            for occupation, risk_level in mappings.items()
        }
        logger.info(f"Loaded {len(mappings)} occupation risk mappings")
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export all configuration for backup or transfer."""
        return {
            "age_brackets": {
                str(bracket_id): {
                    "name": bracket.name,
                    "min_age": bracket.min_age,
                    "max_age": bracket.max_age,
                    "base_factor": str(bracket.base_factor),
                    "gender_factors": {k.value: str(v) for k, v in bracket.gender_factors.items()},
                    "territory_factors": {k: str(v) for k, v in bracket.territory_factors.items()},
                    "benefit_specific_factors": {k: str(v) for k, v in bracket.benefit_specific_factors.items()},
                    "is_active": bracket.is_active
                }
                for bracket_id, bracket in self.age_brackets.items()
            },
            "actuarial_tables": {
                str(table_id): {
                    "name": table.name,
                    "table_type": table.table_type,
                    "version": table.version,
                    "description": table.description,
                    "rates": {
                        age: {gender: str(rate) for gender, rate in gender_rates.items()}
                        for age, gender_rates in table.rates.items()
                    }
                }
                for table_id, table in self.actuarial_tables.items()
            },
            "territory_definitions": self.territory_definitions,
            "occupation_risk_mapping": {
                occupation: risk.value
                for occupation, risk in self.occupation_risk_mapping.items()
            },
            "export_timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_advanced_age_bracket_usage():
    """Demonstrate the advanced age bracket integration system."""
    system = AdvancedAgeBracketIntegration()
    
    # Create age brackets
    brackets = system.create_dynamic_age_brackets(
        min_age=18,
        max_age=70,
        bracket_size=5,
        base_factor_progression="exponential",
        factor_range=(Decimal('0.7'), Decimal('2.0'))
    )
    
    # Configure gender factors for medical benefits
    for bracket in brackets:
        system.update_gender_factors(bracket.bracket_id, {
            Gender.MALE: Decimal('1.0'),
            Gender.FEMALE: Decimal('1.15'),  # Higher medical utilization
            Gender.UNSPECIFIED: Decimal('1.075')
        })
    
    # Configure territory factors
    territory_factors = {
        "URBAN": Decimal('1.1'),    # Higher costs in urban areas
        "SUBURBAN": Decimal('1.0'), # Standard
        "RURAL": Decimal('0.9')     # Lower costs in rural areas
    }
    
    for bracket in brackets:
        system.update_territory_factors(bracket.bracket_id, territory_factors)
    
    # Load occupation risk mappings
    system.load_occupation_risk_mapping({
        "CONSTRUCTION_WORKER": "HIGH",
        "OFFICE_WORKER": "LOW",
        "HEALTHCARE_PROVIDER": "MEDIUM",
        "TEACHER": "LOW",
        "PILOT": "HIGH"
    })
    
    # Create demographic profile
    profile = DemographicProfile(
        age=35,
        gender=Gender.FEMALE,
        territory="URBAN",
        occupation="HEALTHCARE_PROVIDER",
        risk_factors=["FAMILY_HISTORY_CARDIAC"]
    )
    
    # Calculate pricing
    base_premium = Decimal('1000.00')
    pricing_result = system.calculate_demographic_pricing(
        base_premium=base_premium,
        demographic_profile=profile,
        benefit_type="MEDICAL",
        include_actuarial=True
    )
    
    # Apply benefit-specific rules
    benefit_details = {
        "coverage_limits": {"annual_limit": 50000},
        "deductible": 1000,
        "copay_percentage": 20
    }
    
    final_result = system.apply_benefit_specific_rules(
        pricing_result,
        "MEDICAL",
        benefit_details
    )
    
    print(f"Base Premium: ${base_premium}")
    print(f"Final Premium: ${final_result['final_premium']}")
    print(f"Total Factor: {final_result['total_factor']}")
    print("\nAdjustments Applied:")
    for adjustment in final_result['adjustments']:
        print(f"  - {adjustment['type']}: {adjustment['factor']} ({adjustment['description']})")


if __name__ == "__main__":
    example_advanced_age_bracket_usage()