# app/modules/pricing/product/services/actuarial_table_service.py

"""
Actuarial Table Service

Business logic layer for Actuarial Table management.
Handles actuarial calculations, table management, and risk assessment.
"""

from typing import Optional, List, Dict, Any, Union, Tuple
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
import json
import math
from sqlalchemy.orm import Session

from app.modules.pricing.product.repositories import actuarial_table_repository as repo
from app.modules.pricing.product.schemas.actuarial_table_schema import (
    ActuarialTableCreate,
    ActuarialTableUpdate,
    ActuarialTableFilter,
    ActuarialTableResponse,
    ActuarialTableListResponse,
    ActuarialCalculationRequest,
    ActuarialCalculationResponse,
    ActuarialDataRow,
    ActuarialTableImport,
    ActuarialTableExport,
    TableStatus,
    TableType,
    TableSource,
    Gender,
    SmokingStatus
)
from app.core.database import get_db
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Define custom exceptions
class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class ConflictException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ================================================================
# TABLE CREATION & MANAGEMENT
# ================================================================

def create_actuarial_table(
    db: Session,
    table_data: ActuarialTableCreate,
    created_by: Optional[UUID] = None
) -> ActuarialTableResponse:
    """
    Create a new actuarial table with validation
    
    Args:
        db: Database session
        table_data: Table creation data
        created_by: User ID creating the table
        
    Returns:
        Created table response
        
    Raises:
        ValidationException: If validation fails
        ConflictException: If table code exists
    """
    try:
        # Validate table data
        _validate_table_structure(table_data)
        
        # Check for duplicate table code
        existing = repo.get_table_by_code(db, table_data.table_code)
        if existing:
            raise ConflictException(
                f"Table with code '{table_data.table_code}' already exists"
            )
        
        # Validate rates and factors
        _validate_table_rates(table_data.table_data)
        
        # Create the table
        table = repo.create_actuarial_table(db, table_data, created_by)
        
        logger.info(
            f"Actuarial table created: {table.id} - {table.table_name} "
            f"by user {created_by}"
        )
        
        # Convert table_data from JSON to ActuarialDataRow objects
        table.table_data = [
            ActuarialDataRow(**row) for row in table.table_data
        ]
        
        return ActuarialTableResponse.model_validate(table)
        
    except (ConflictException, ValidationException) as e:
        logger.warning(f"Table creation validation failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating table: {str(e)}")
        raise BadRequestException(f"Failed to create table: {str(e)}")


def _validate_table_structure(table_data: ActuarialTableCreate) -> None:
    """
    Validate actuarial table structure
    
    Args:
        table_data: Table data to validate
        
    Raises:
        ValidationException: If validation fails
    """
    # Validate base year
    current_year = date.today().year
    if table_data.base_year > current_year:
        raise ValidationException(
            f"Base year {table_data.base_year} cannot be in the future"
        )
    
    # Validate age range
    if table_data.min_age > table_data.max_age:
        raise ValidationException(
            "Minimum age cannot be greater than maximum age"
        )
    
    # Validate table data completeness
    if not table_data.table_data:
        raise ValidationException("Table data cannot be empty")
    
    # Check age continuity
    ages_in_table = sorted(set(row.age for row in table_data.table_data))
    expected_ages = list(range(table_data.min_age, table_data.max_age + 1))
    
    # For gender/smoking specific tables, multiple entries per age are allowed
    if not table_data.gender_specific and not table_data.smoking_specific:
        missing_ages = set(expected_ages) - set(ages_in_table)
        if missing_ages:
            raise ValidationException(
                f"Missing data for ages: {sorted(missing_ages)}"
            )
    
    # Validate dates if provided
    if table_data.effective_date and table_data.expiry_date:
        if table_data.expiry_date <= table_data.effective_date:
            raise ValidationException(
                "Expiry date must be after effective date"
            )


def _validate_table_rates(table_data: List[ActuarialDataRow]) -> None:
    """
    Validate actuarial rates
    
    Args:
        table_data: List of actuarial data rows
        
    Raises:
        ValidationException: If rates are invalid
    """
    for row in table_data:
        # Validate base rate
        if row.rate < 0 or row.rate > 1:
            raise ValidationException(
                f"Invalid rate {row.rate} for age {row.age}. "
                "Rates must be between 0 and 1"
            )
        
        # Validate gender-specific rates if present
        if row.rate_male is not None:
            if row.rate_male < 0 or row.rate_male > 1:
                raise ValidationException(
                    f"Invalid male rate {row.rate_male} for age {row.age}"
                )
        
        if row.rate_female is not None:
            if row.rate_female < 0 or row.rate_female > 1:
                raise ValidationException(
                    f"Invalid female rate {row.rate_female} for age {row.age}"
                )
        
        # Validate smoking-specific rates if present
        if row.rate_smoker is not None:
            if row.rate_smoker < 0 or row.rate_smoker > 1:
                raise ValidationException(
                    f"Invalid smoker rate {row.rate_smoker} for age {row.age}"
                )
            
            # Smoker rates should typically be higher than non-smoker
            if row.rate_non_smoker is not None:
                if row.rate_smoker < row.rate_non_smoker:
                    logger.warning(
                        f"Smoker rate lower than non-smoker rate "
                        f"for age {row.age}"
                    )
        
        # Validate improvement and selection factors
        if row.improvement_factor is not None:
            if row.improvement_factor < 0:
                raise ValidationException(
                    f"Invalid improvement factor for age {row.age}"
                )
        
        if row.selection_factor is not None:
            if row.selection_factor < 0:
                raise ValidationException(
                    f"Invalid selection factor for age {row.age}"
                )


# ================================================================
# TABLE RETRIEVAL & SEARCH
# ================================================================

def get_actuarial_table(
    db: Session,
    table_id: UUID,
    include_analysis: bool = True
) -> Dict[str, Any]:
    """
    Get actuarial table with analysis
    
    Args:
        db: Database session
        table_id: Table UUID
        include_analysis: Include statistical analysis
        
    Returns:
        Table details with analysis
    """
    table = repo.get_actuarial_table_by_id(db, table_id)
    
    if not table:
        raise NotFoundException(f"Table with ID {table_id} not found")
    
    # Convert table_data from JSON to ActuarialDataRow objects
    table.table_data = [
        ActuarialDataRow(**row) for row in table.table_data
    ]
    
    result = {
        "table": ActuarialTableResponse.model_validate(table),
        "metadata": {
            "source": table.table_source,
            "country": table.country,
            "region": table.region,
            "gender_specific": table.gender_specific,
            "smoking_specific": table.smoking_specific
        }
    }
    
    # Add analysis if requested
    if include_analysis:
        analysis = _analyze_table_data(table.table_data)
        result["analysis"] = analysis
    
    return result


def _analyze_table_data(
    table_data: List[ActuarialDataRow]
) -> Dict[str, Any]:
    """
    Analyze actuarial table data
    
    Args:
        table_data: List of actuarial data rows
        
    Returns:
        Statistical analysis
    """
    rates = [float(row.rate) for row in table_data]
    ages = [row.age for row in table_data]
    
    analysis = {
        "statistics": {
            "min_rate": min(rates),
            "max_rate": max(rates),
            "avg_rate": sum(rates) / len(rates),
            "median_rate": sorted(rates)[len(rates) // 2],
            "age_range": f"{min(ages)}-{max(ages)}",
            "data_points": len(table_data)
        },
        "rate_progression": [],
        "high_risk_ages": [],
        "mortality_curve": "unknown"
    }
    
    # Analyze rate progression
    for i in range(1, len(ages)):
        if ages[i] == ages[i-1] + 1:  # Consecutive ages
            rate_change = rates[i] - rates[i-1]
            change_pct = (rate_change / rates[i-1] * 100) if rates[i-1] > 0 else 0
            
            analysis["rate_progression"].append({
                "age": ages[i],
                "rate_change": rate_change,
                "change_percentage": change_pct
            })
    
    # Identify high-risk ages (rates above median)
    median_rate = analysis["statistics"]["median_rate"]
    high_risk = [
        {"age": row.age, "rate": float(row.rate)}
        for row in table_data
        if float(row.rate) > median_rate * 1.5
    ]
    analysis["high_risk_ages"] = sorted(high_risk, key=lambda x: x["rate"], reverse=True)[:10]
    
    # Determine mortality curve type
    if len(rates) > 10:
        # Simple classification based on rate progression
        early_avg = sum(rates[:len(rates)//3]) / (len(rates)//3)
        late_avg = sum(rates[-len(rates)//3:]) / (len(rates)//3)
        
        if late_avg > early_avg * 3:
            analysis["mortality_curve"] = "exponential"
        elif late_avg > early_avg * 1.5:
            analysis["mortality_curve"] = "geometric"
        else:
            analysis["mortality_curve"] = "linear"
    
    return analysis


def search_actuarial_tables(
    db: Session,
    filters: Optional[ActuarialTableFilter] = None,
    page: int = 1,
    page_size: int = 50
) -> ActuarialTableListResponse:
    """
    Search actuarial tables with filtering
    
    Args:
        db: Database session
        filters: Search filters
        page: Page number
        page_size: Items per page
        
    Returns:
        Paginated table list
    """
    skip = (page - 1) * page_size
    
    result = repo.get_tables_list(
        db, filters, skip, page_size
    )
    
    # Convert table_data for each table
    for table in result["tables"]:
        table.table_data = [
            ActuarialDataRow(**row) for row in table.table_data
        ]
    
    tables = [
        ActuarialTableResponse.model_validate(t)
        for t in result["tables"]
    ]
    
    return ActuarialTableListResponse(
        tables=tables,
        total_count=result["total_count"],
        page=page,
        page_size=page_size,
        total_pages=result["total_pages"]
    )


def get_latest_table(
    db: Session,
    table_type: TableType,
    country: Optional[str] = None
) -> ActuarialTableResponse:
    """
    Get the latest version of a table type
    
    Args:
        db: Database session
        table_type: Type of table
        country: Optional country filter
        
    Returns:
        Latest table
        
    Raises:
        NotFoundException: If no table found
    """
    table = repo.get_latest_table_version(db, table_type, country)
    
    if not table:
        raise NotFoundException(
            f"No {table_type} table found" +
            (f" for country {country}" if country else "")
        )
    
    # Convert table_data
    table.table_data = [
        ActuarialDataRow(**row) for row in table.table_data
    ]
    
    return ActuarialTableResponse.model_validate(table)


# ================================================================
# ACTUARIAL CALCULATIONS
# ================================================================

def perform_actuarial_calculation(
    db: Session,
    calculation_request: ActuarialCalculationRequest
) -> ActuarialCalculationResponse:
    """
    Perform comprehensive actuarial calculations
    
    Args:
        db: Database session
        calculation_request: Calculation parameters
        
    Returns:
        Detailed calculation results
    """
    # Get base calculation from repository
    base_calc = repo.calculate_actuarial_value(db, calculation_request)
    
    # Enhance with additional calculations
    table = repo.get_actuarial_table_by_id(db, calculation_request.table_id)
    
    if not table:
        raise NotFoundException(
            f"Table {calculation_request.table_id} not found"
        )
    
    # Calculate life expectancy if mortality table
    life_expectancy = None
    if table.table_type == TableType.MORTALITY:
        life_expectancy = _calculate_life_expectancy(
            table.table_data,
            calculation_request.age,
            calculation_request.gender,
            calculation_request.smoking_status
        )
    
    # Calculate present values if term and interest provided
    present_values = {}
    if calculation_request.term_years and calculation_request.interest_rate:
        present_values = _calculate_present_values(
            base_calc["adjusted_rate"],
            calculation_request.term_years,
            calculation_request.interest_rate,
            calculation_request.sum_insured
        )
    
    # Calculate reserves if applicable
    reserve_amount = None
    if base_calc.get("annual_premium") and calculation_request.term_years:
        reserve_amount = _calculate_reserve(
            Decimal(str(base_calc["annual_premium"])),
            calculation_request.term_years,
            calculation_request.interest_rate or Decimal('0.03')
        )
    
    # Create enhanced response
    enhanced_calc = ActuarialCalculationResponse(
        table_id=calculation_request.table_id,
        base_rate=Decimal(str(base_calc["base_rate"])),
        adjusted_rate=Decimal(str(base_calc["adjusted_rate"])),
        annual_premium=Decimal(str(base_calc["annual_premium"])) if base_calc.get("annual_premium") else None,
        monthly_premium=Decimal(str(base_calc["monthly_premium"])) if base_calc.get("monthly_premium") else None,
        net_premium=Decimal(str(base_calc["net_premium"])) if base_calc.get("net_premium") else None,
        gross_premium=Decimal(str(base_calc["gross_premium"])) if base_calc.get("gross_premium") else None,
        present_value=Decimal(str(base_calc["present_value"])) if base_calc.get("present_value") else None,
        reserve_amount=reserve_amount,
        calculation_details={
            **base_calc["calculation_details"],
            "life_expectancy": life_expectancy,
            "present_values": present_values,
            "table_type": table.table_type,
            "table_version": table.version
        },
        factors_applied=base_calc["factors_applied"]
    )
    
    return enhanced_calc


def _calculate_life_expectancy(
    table_data: List[Dict],
    current_age: int,
    gender: Optional[Gender],
    smoking_status: Optional[SmokingStatus]
) -> float:
    """
    Calculate life expectancy from mortality table
    
    Args:
        table_data: Mortality table data
        current_age: Current age
        gender: Gender
        smoking_status: Smoking status
        
    Returns:
        Life expectancy in years
    """
    survival_prob = 1.0
    expected_years = 0.0
    
    for age in range(current_age, min(current_age + 50, 120)):
        # Get mortality rate for this age
        rate = None
        for row in table_data:
            if row.get('age') == age:
                # Use specific rate based on gender/smoking
                if gender and gender == Gender.MALE and row.get('rate_male'):
                    rate = row['rate_male']
                elif gender and gender == Gender.FEMALE and row.get('rate_female'):
                    rate = row['rate_female']
                elif smoking_status and smoking_status == SmokingStatus.SMOKER and row.get('rate_smoker'):
                    rate = row['rate_smoker']
                elif smoking_status and smoking_status == SmokingStatus.NON_SMOKER and row.get('rate_non_smoker'):
                    rate = row['rate_non_smoker']
                else:
                    rate = row.get('rate')
                break
        
        if rate is None:
            break
        
        # Update survival probability
        survival_prob *= (1 - rate)
        expected_years += survival_prob
        
        if survival_prob < 0.01:  # Stop when survival probability is very low
            break
    
    return expected_years


def _calculate_present_values(
    rate: Decimal,
    term_years: int,
    interest_rate: Decimal,
    sum_insured: Optional[Decimal]
) -> Dict[str, float]:
    """
    Calculate various present values
    
    Args:
        rate: Mortality/morbidity rate
        term_years: Term in years
        interest_rate: Discount rate
        sum_insured: Sum insured amount
        
    Returns:
        Present value calculations
    """
    pv_calculations = {}
    
    # Present value of $1 annuity
    annuity_pv = Decimal('0')
    for year in range(1, term_years + 1):
        discount = (Decimal('1') + interest_rate) ** -year
        survival = (Decimal('1') - rate) ** year
        annuity_pv += discount * survival
    
    pv_calculations["annuity_present_value"] = float(annuity_pv)
    
    # Present value of insurance benefit
    if sum_insured:
        insurance_pv = Decimal('0')
        for year in range(1, term_years + 1):
            discount = (Decimal('1') + interest_rate) ** -year
            death_prob = rate * ((Decimal('1') - rate) ** (year - 1))
            insurance_pv += discount * death_prob * sum_insured
        
        pv_calculations["insurance_present_value"] = float(insurance_pv)
        pv_calculations["net_single_premium"] = float(insurance_pv)
    
    return pv_calculations


def _calculate_reserve(
    annual_premium: Decimal,
    term_years: int,
    interest_rate: Decimal
) -> Decimal:
    """
    Calculate policy reserve
    
    Args:
        annual_premium: Annual premium
        term_years: Policy term
        interest_rate: Interest rate
        
    Returns:
        Reserve amount
    """
    # Simplified reserve calculation
    # In practice, would use more sophisticated methods
    reserve = annual_premium * term_years * Decimal('0.3')  # 30% of total premiums
    
    # Adjust for interest
    discount_factor = (
        (Decimal('1') - (Decimal('1') + interest_rate) ** -term_years) /
        interest_rate
    )
    
    return reserve * discount_factor


def calculate_risk_premium(
    db: Session,
    table_id: UUID,
    age: int,
    sum_insured: Decimal,
    term_years: int = 1,
    loading_factor: Decimal = Decimal('1.2')
) -> Dict[str, Any]:
    """
    Calculate risk premium with loading
    
    Args:
        db: Database session
        table_id: Table UUID
        age: Age of insured
        sum_insured: Sum insured
        term_years: Term in years
        loading_factor: Loading for expenses/profit
        
    Returns:
        Risk premium calculation
    """
    calc_request = ActuarialCalculationRequest(
        table_id=table_id,
        age=age,
        sum_insured=sum_insured,
        term_years=term_years,
        interest_rate=Decimal('0.03'),  # Standard discount rate
        apply_improvement=True,
        apply_selection=False
    )
    
    calculation = perform_actuarial_calculation(db, calc_request)
    
    # Calculate pure risk premium
    pure_premium = calculation.net_premium or Decimal('0')
    
    # Apply loading
    loaded_premium = pure_premium * loading_factor
    
    # Calculate components
    expense_loading = loaded_premium - pure_premium
    
    return {
        "age": age,
        "sum_insured": float(sum_insured),
        "term_years": term_years,
        "pure_risk_premium": float(pure_premium),
        "expense_loading": float(expense_loading),
        "total_premium": float(loaded_premium),
        "loading_percentage": float((loading_factor - 1) * 100),
        "monthly_premium": float(loaded_premium / 12),
        "effective_rate": float(calculation.adjusted_rate)
    }


# ================================================================
# IMPORT/EXPORT OPERATIONS
# ================================================================

def import_actuarial_table(
    db: Session,
    import_data: ActuarialTableImport,
    table_metadata: Dict[str, Any],
    created_by: Optional[UUID] = None
) -> ActuarialTableResponse:
    """
    Import actuarial table from file
    
    Args:
        db: Database session
        import_data: Import data
        table_metadata: Table metadata
        created_by: User performing import
        
    Returns:
        Imported table
    """
    try:
        # Import through repository
        table = repo.import_actuarial_table(
            db,
            import_data.data,
            import_data.format,
            table_metadata,
            created_by
        )
        
        # Convert table_data
        table.table_data = [
            ActuarialDataRow(**row) for row in table.table_data
        ]
        
        # Validate if requested
        if import_data.validate_only:
            # Just validate, don't save
            db.rollback()
            return ActuarialTableResponse.model_validate(table)
        
        logger.info(f"Imported actuarial table: {table.id}")
        
        return ActuarialTableResponse.model_validate(table)
        
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        raise BadRequestException(f"Import failed: {str(e)}")


def export_actuarial_tables(
    db: Session,
    export_request: ActuarialTableExport
) -> Dict[str, Any]:
    """
    Export actuarial tables
    
    Args:
        db: Database session
        export_request: Export configuration
        
    Returns:
        Export data
    """
    exported_data = {}
    
    for table_id in export_request.table_ids:
        try:
            # Export through repository
            data = repo.export_actuarial_table(
                db, table_id, export_request.format
            )
            
            # Get table info
            table = repo.get_actuarial_table_by_id(db, table_id)
            
            exported_data[str(table_id)] = {
                "table_name": table.table_name,
                "table_code": table.table_code,
                "format": export_request.format,
                "data": data
            }
            
            if export_request.include_metadata:
                exported_data[str(table_id)]["metadata"] = {
                    "table_type": table.table_type,
                    "base_year": table.base_year,
                    "version": table.version,
                    "country": table.country,
                    "source": table.table_source,
                    "exported_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to export table {table_id}: {str(e)}")
            exported_data[str(table_id)] = {
                "error": str(e)
            }
    
    return {
        "export_count": len(export_request.table_ids),
        "successful": sum(1 for d in exported_data.values() if "error" not in d),
        "failed": sum(1 for d in exported_data.values() if "error" in d),
        "tables": exported_data
    }


# ================================================================
# TABLE COMPARISON & ANALYSIS
# ================================================================

def compare_actuarial_tables(
    db: Session,
    table_ids: List[UUID],
    age_range: Optional[Tuple[int, int]] = None
) -> Dict[str, Any]:
    """
    Compare multiple actuarial tables
    
    Args:
        db: Database session
        table_ids: List of table UUIDs to compare
        age_range: Optional age range for comparison
        
    Returns:
        Comparison results
    """
    if len(table_ids) < 2:
        raise ValidationException("At least 2 tables required for comparison")
    
    tables = []
    for table_id in table_ids:
        table = repo.get_actuarial_table_by_id(db, table_id)
        if not table:
            raise NotFoundException(f"Table {table_id} not found")
        tables.append(table)
    
    # Determine age range for comparison
    if not age_range:
        min_age = max(t.min_age for t in tables)
        max_age = min(t.max_age for t in tables)
        age_range = (min_age, max_age)
    
    comparison = {
        "tables": [],
        "age_range": f"{age_range[0]}-{age_range[1]}",
        "rate_comparison": [],
        "variance_analysis": {},
        "recommendations": []
    }
    
    # Add table info
    for table in tables:
        comparison["tables"].append({
            "id": str(table.id),
            "name": table.table_name,
            "type": table.table_type,
            "version": table.version,
            "base_year": table.base_year
        })
    
    # Compare rates across age range
    for age in range(age_range[0], age_range[1] + 1):
        age_comparison = {"age": age, "rates": {}}
        
        for table in tables:
            # Find rate for this age
            rate = None
            for row in table.table_data:
                if isinstance(row, dict) and row.get('age') == age:
                    rate = row.get('rate')
                    break
            
            if rate is not None:
                age_comparison["rates"][str(table.id)] = float(rate)
        
        if age_comparison["rates"]:
            # Calculate variance
            rates = list(age_comparison["rates"].values())
            if len(rates) > 1:
                avg_rate = sum(rates) / len(rates)
                variance = sum((r - avg_rate) ** 2 for r in rates) / len(rates)
                age_comparison["variance"] = variance
                age_comparison["cv"] = (variance ** 0.5) / avg_rate if avg_rate > 0 else 0
            
            comparison["rate_comparison"].append(age_comparison)
    
    # Overall variance analysis
    if comparison["rate_comparison"]:
        total_variance = sum(
            r.get("variance", 0) for r in comparison["rate_comparison"]
        ) / len(comparison["rate_comparison"])
        
        comparison["variance_analysis"] = {
            "average_variance": total_variance,
            "max_variance_age": max(
                comparison["rate_comparison"],
                key=lambda x: x.get("variance", 0)
            )["age"] if comparison["rate_comparison"] else None,
            "consistency_score": 1 / (1 + total_variance) * 100  # 0-100 score
        }
    
    # Generate recommendations
    if comparison["variance_analysis"].get("consistency_score", 0) < 70:
        comparison["recommendations"].append(
            "High variance between tables suggests different methodologies or data sources"
        )
    
    # Check for outdated tables
    current_year = date.today().year
    for table in tables:
        if current_year - table.base_year > 5:
            comparison["recommendations"].append(
                f"Table '{table.table_name}' may be outdated (base year: {table.base_year})"
            )
    
    return comparison


def analyze_mortality_improvement(
    db: Session,
    old_table_id: UUID,
    new_table_id: UUID
) -> Dict[str, Any]:
    """
    Analyze mortality improvement between two tables
    
    Args:
        db: Database session
        old_table_id: Older table UUID
        new_table_id: Newer table UUID
        
    Returns:
        Improvement analysis
    """
    old_table = repo.get_actuarial_table_by_id(db, old_table_id)
    new_table = repo.get_actuarial_table_by_id(db, new_table_id)
    
    if not old_table or not new_table:
        raise NotFoundException("One or both tables not found")
    
    if old_table.table_type != TableType.MORTALITY or new_table.table_type != TableType.MORTALITY:
        raise ValidationException("Both tables must be mortality tables")
    
    analysis = {
        "old_table": {
            "name": old_table.table_name,
            "base_year": old_table.base_year
        },
        "new_table": {
            "name": new_table.table_name,
            "base_year": new_table.base_year
        },
        "years_difference": new_table.base_year - old_table.base_year,
        "improvement_by_age": [],
        "average_improvement": 0,
        "life_expectancy_change": {}
    }
    
    if analysis["years_difference"] <= 0:
        raise ValidationException("New table must be more recent than old table")
    
    # Calculate improvement by age
    improvements = []
    min_age = max(old_table.min_age, new_table.min_age)
    max_age = min(old_table.max_age, new_table.max_age)
    
    for age in range(min_age, max_age + 1):
        old_rate = None
        new_rate = None
        
        # Get rates from both tables
        for row in old_table.table_data:
            if isinstance(row, dict) and row.get('age') == age:
                old_rate = row.get('rate')
                break
        
        for row in new_table.table_data:
            if isinstance(row, dict) and row.get('age') == age:
                new_rate = row.get('rate')
                break
        
        if old_rate and new_rate and old_rate > 0:
            improvement = ((old_rate - new_rate) / old_rate) * 100
            annual_improvement = improvement / analysis["years_difference"]
            
            improvements.append(improvement)
            
            analysis["improvement_by_age"].append({
                "age": age,
                "old_rate": float(old_rate),
                "new_rate": float(new_rate),
                "improvement_pct": improvement,
                "annual_improvement_pct": annual_improvement
            })
    
    # Calculate average improvement
    if improvements:
        analysis["average_improvement"] = sum(improvements) / len(improvements)
        analysis["average_annual_improvement"] = (
            analysis["average_improvement"] / analysis["years_difference"]
        )
    
    # Calculate life expectancy change at key ages
    for test_age in [0, 20, 40, 60, 80]:
        if test_age >= min_age and test_age <= max_age:
            old_le = _calculate_life_expectancy(
                old_table.table_data, test_age, None, None
            )
            new_le = _calculate_life_expectancy(
                new_table.table_data, test_age, None, None
            )
            
            analysis["life_expectancy_change"][f"age_{test_age}"] = {
                "old": old_le,
                "new": new_le,
                "change": new_le - old_le
            }
    
    return analysis


# ================================================================
# VALIDATION & COMPLIANCE
# ================================================================

def validate_table_compliance(
    db: Session,
    table_id: UUID,
    regulatory_standard: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate table compliance with regulatory standards
    
    Args:
        db: Database session
        table_id: Table UUID
        regulatory_standard: Standard to validate against
        
    Returns:
        Compliance validation results
    """
    table = repo.get_actuarial_table_by_id(db, table_id)
    
    if not table:
        raise NotFoundException(f"Table {table_id} not found")
    
    validation = {
        "table_id": str(table_id),
        "table_name": table.table_name,
        "is_compliant": True,
        "issues": [],
        "warnings": [],
        "checked_at": datetime.utcnow().isoformat()
    }
    
    # Check approval status
    if table.status != TableStatus.APPROVED:
        validation["warnings"].append(f"Table status is {table.status}, not approved")
    
    if not table.regulatory_approval:
        validation["issues"].append("No regulatory approval reference")
        validation["is_compliant"] = False
    
    # Check data completeness
    expected_ages = list(range(table.min_age, table.max_age + 1))
    actual_ages = set()
    
    for row in table.table_data:
        if isinstance(row, dict):
            actual_ages.add(row.get('age'))
    
    missing_ages = set(expected_ages) - actual_ages
    if missing_ages and not table.gender_specific and not table.smoking_specific:
        validation["issues"].append(f"Missing data for ages: {sorted(missing_ages)}")
        validation["is_compliant"] = False
    
    # Check table age
    current_year = date.today().year
    if current_year - table.base_year > 10:
        validation["warnings"].append(
            f"Table is {current_year - table.base_year} years old, consider updating"
        )
    
    # Check rates validity
    for row in table.table_data:
        if isinstance(row, dict):
            rate = row.get('rate')
            if rate is not None:
                if rate < 0 or rate > 1:
                    validation["issues"].append(
                        f"Invalid rate {rate} for age {row.get('age')}"
                    )
                    validation["is_compliant"] = False
    
    # Standard-specific checks
    if regulatory_standard:
        validation["standard"] = regulatory_standard
        
        if regulatory_standard == "SOA":  # Society of Actuaries
            if table.table_source != TableSource.INDUSTRY:
                validation["warnings"].append(
                    "Table source is not industry standard"
                )
        elif regulatory_standard == "NAIC":  # National Association of Insurance Commissioners
            if not table.country or table.country != "US":
                validation["issues"].append(
                    "NAIC compliance requires US-specific tables"
                )
                validation["is_compliant"] = False
    
    return validation


# ================================================================
# ANALYTICS & REPORTING
# ================================================================

def get_table_usage_analytics(
    db: Session,
    table_id: UUID,
    period_days: int = 30
) -> Dict[str, Any]:
    """
    Get usage analytics for an actuarial table (mock implementation)
    
    Args:
        db: Database session
        table_id: Table UUID
        period_days: Analysis period
        
    Returns:
        Usage analytics
    """
    table = repo.get_actuarial_table_by_id(db, table_id)
    
    if not table:
        raise NotFoundException(f"Table {table_id} not found")
    
    # Mock analytics - in production would come from usage logs
    analytics = {
        "table_id": str(table_id),
        "table_name": table.table_name,
        "period_days": period_days,
        "usage_statistics": {
            "total_calculations": 1250,
            "unique_users": 45,
            "average_daily_usage": 42,
            "peak_usage_day": "2024-01-15",
            "most_common_ages": [45, 50, 35, 40, 55]
        },
        "calculation_breakdown": {
            "premium_calculations": 850,
            "reserve_calculations": 250,
            "life_expectancy_calculations": 150
        },
        "performance_metrics": {
            "average_calculation_time_ms": 15,
            "success_rate": 99.5,
            "error_count": 6
        },
        "related_products": [
            {"product_id": "prod_123", "usage_count": 450},
            {"product_id": "prod_456", "usage_count": 320}
        ]
    }
    
    return analytics


def generate_actuarial_report(
    db: Session,
    report_type: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate comprehensive actuarial report
    
    Args:
        db: Database session
        report_type: Type of report
        parameters: Report parameters
        
    Returns:
        Generated report
    """
    report = {
        "report_type": report_type,
        "generated_at": datetime.utcnow().isoformat(),
        "parameters": parameters,
        "content": {}
    }
    
    if report_type == "mortality_analysis":
        # Mortality analysis report
        table_id = parameters.get("table_id")
        if not table_id:
            raise ValidationException("Table ID required for mortality analysis")
        
        table = repo.get_actuarial_table_by_id(db, UUID(table_id))
        if not table:
            raise NotFoundException(f"Table {table_id} not found")
        
        # Convert table data for analysis
        table.table_data = [
            ActuarialDataRow(**row) if isinstance(row, dict) else row
            for row in table.table_data
        ]
        
        analysis = _analyze_table_data(table.table_data)
        
        report["content"] = {
            "table_info": {
                "name": table.table_name,
                "type": table.table_type,
                "base_year": table.base_year
            },
            "statistical_summary": analysis["statistics"],
            "high_risk_ages": analysis["high_risk_ages"],
            "mortality_pattern": analysis["mortality_curve"],
            "recommendations": []
        }
        
        # Add recommendations
        if analysis["mortality_curve"] == "exponential":
            report["content"]["recommendations"].append(
                "Consider age-banded pricing for older age groups"
            )
        
        if analysis["statistics"]["max_rate"] > 0.5:
            report["content"]["recommendations"].append(
                "High mortality rates detected - ensure adequate reserves"
            )
            
    elif report_type == "table_comparison":
        # Table comparison report
        table_ids = parameters.get("table_ids", [])
        if len(table_ids) < 2:
            raise ValidationException("At least 2 tables required for comparison")
        
        comparison = compare_actuarial_tables(db, table_ids)
        report["content"] = comparison
        
    elif report_type == "portfolio_summary":
        # Portfolio summary report
        stats = repo.get_actuarial_statistics(db)
        
        report["content"] = {
            "statistics": stats,
            "table_distribution": {
                "by_type": stats["by_type"],
                "by_source": stats["by_source"]
            },
            "quality_metrics": {
                "approved_percentage": (
                    stats["approved_tables"] / stats["total_tables"] * 100
                    if stats["total_tables"] > 0 else 0
                ),
                "active_percentage": (
                    stats["active_tables"] / stats["total_tables"] * 100
                    if stats["total_tables"] > 0 else 0
                )
            }
        }
    else:
        raise ValidationException(f"Unknown report type: {report_type}")
    
    return report


# ================================================================
# BULK OPERATIONS
# ================================================================

def bulk_approve_tables(
    db: Session,
    table_ids: List[UUID],
    approval_reference: str,
    approved_by: Optional[UUID] = None
) -> Dict[str, Any]:
    """
    Bulk approve actuarial tables
    
    Args:
        db: Database session
        table_ids: List of table UUIDs
        approval_reference: Regulatory approval reference
        approved_by: User approving tables
        
    Returns:
        Approval results
    """
    results = {
        "approved": [],
        "failed": [],
        "total": len(table_ids)
    }
    
    for table_id in table_ids:
        try:
            table = repo.approve_actuarial_table(
                db, table_id, approval_reference, approved_by
            )
            results["approved"].append(str(table_id))
        except Exception as e:
            results["failed"].append({
                "table_id": str(table_id),
                "error": str(e)
            })
            logger.error(f"Failed to approve table {table_id}: {e}")
    
    results["approved_count"] = len(results["approved"])
    results["failed_count"] = len(results["failed"])
    
    logger.info(
        f"Bulk approved {results['approved_count']} tables, "
        f"{results['failed_count']} failed"
    )
    
    return results


def update_table_factors(
    db: Session,
    table_id: UUID,
    improvement_factor: Optional[Decimal] = None,
    selection_factor: Optional[Decimal] = None,
    updated_by: Optional[UUID] = None
) -> ActuarialTableResponse:
    """
    Update improvement and selection factors for a table
    
    Args:
        db: Database session
        table_id: Table UUID
        improvement_factor: Improvement factor to apply
        selection_factor: Selection factor to apply
        updated_by: User updating table
        
    Returns:
        Updated table
    """
    table = repo.get_actuarial_table_by_id(db, table_id)
    
    if not table:
        raise NotFoundException(f"Table {table_id} not found")
    
    # Update factors in table data
    updated_data = []
    for row in table.table_data:
        if isinstance(row, dict):
            row_copy = row.copy()
            if improvement_factor is not None:
                row_copy['improvement_factor'] = float(improvement_factor)
            if selection_factor is not None:
                row_copy['selection_factor'] = float(selection_factor)
            updated_data.append(ActuarialDataRow(**row_copy))
        else:
            updated_data.append(row)
    
    # Create update data
    update_data = ActuarialTableUpdate(
        table_data=updated_data,
        notes=f"Updated factors - Improvement: {improvement_factor}, Selection: {selection_factor}"
    )
    
    # Update the table
    updated_table = repo.update_actuarial_table(
        db, table_id, update_data, updated_by
    )
    
    # Convert table_data for response
    updated_table.table_data = [
        ActuarialDataRow(**row) if isinstance(row, dict) else row
        for row in updated_table.table_data
    ]
    
    logger.info(f"Updated factors for table {table_id}")
    
    return ActuarialTableResponse.model_validate(updated_table)


# ================================================================
# END OF SERVICE
# ================================================================