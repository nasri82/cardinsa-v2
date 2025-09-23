# app/modules/pricing/product/repositories/actuarial_table_repository.py

"""
Actuarial Table Repository

Data access layer for Actuarial Table entities.
Handles all database operations for actuarial data management.
"""

from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
import json
import csv
import io
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.modules.pricing.product.models.actuarial_table_model import ActuarialTable
from app.modules.pricing.product.schemas.actuarial_table_schema import (
    ActuarialTableCreate,
    ActuarialTableUpdate,
    ActuarialTableFilter,
    ActuarialCalculationRequest,
    ActuarialDataRow,
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

class ConflictException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ================================================================
# CREATE OPERATIONS
# ================================================================

def create_actuarial_table(
    db: Session,
    table_data: ActuarialTableCreate,
    created_by: Optional[UUID] = None
) -> ActuarialTable:
    """
    Create a new actuarial table
    
    Args:
        db: Database session
        table_data: Actuarial table creation data
        created_by: ID of the user creating the table
        
    Returns:
        Created ActuarialTable instance
        
    Raises:
        ConflictException: If table code already exists
        BadRequestException: If data validation fails
    """
    try:
        # Check for duplicate table code
        existing = db.query(ActuarialTable).filter(
            and_(
                ActuarialTable.table_code == table_data.table_code,
                ActuarialTable.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ConflictException(
                f"Actuarial table with code '{table_data.table_code}' already exists"
            )
        
        # Validate table data consistency
        _validate_table_data(table_data.table_data)
        
        # Convert table data to JSON for storage
        table_data_json = [
            row.model_dump() for row in table_data.table_data
        ]
        
        # Create new table
        table = ActuarialTable(
            **table_data.model_dump(exclude={'tags', 'table_data'}),
            table_data=table_data_json,
            created_by=created_by,
            created_at=datetime.utcnow(),
            status=TableStatus.ACTIVE
        )
        
        # Handle tags if provided
        if table_data.tags:
            table.tags = table_data.tags
        
        db.add(table)
        db.commit()
        db.refresh(table)
        
        logger.info(f"Created actuarial table: {table.id}")
        return table
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        raise ConflictException("Table creation failed due to data conflict")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating actuarial table: {str(e)}")
        raise BadRequestException(f"Failed to create table: {str(e)}")


def _validate_table_data(data_rows: List[ActuarialDataRow]) -> None:
    """
    Validate actuarial table data for consistency
    
    Args:
        data_rows: List of actuarial data rows
        
    Raises:
        BadRequestException: If validation fails
    """
    if not data_rows:
        raise BadRequestException("Table data cannot be empty")
    
    # Check for duplicate age/gender/smoking combinations
    seen_combinations = set()
    
    for row in data_rows:
        combination = (
            row.age,
            row.gender.value if row.gender else None,
            row.smoking_status.value if row.smoking_status else None
        )
        
        if combination in seen_combinations:
            raise BadRequestException(
                f"Duplicate entry for age {row.age}, "
                f"gender {row.gender}, smoking {row.smoking_status}"
            )
        
        seen_combinations.add(combination)
    
    # Validate rates are within bounds
    for row in data_rows:
        if row.rate < 0 or row.rate > 1:
            raise BadRequestException(
                f"Rate {row.rate} for age {row.age} must be between 0 and 1"
            )


# ================================================================
# READ OPERATIONS
# ================================================================

def get_actuarial_table_by_id(
    db: Session,
    table_id: UUID,
    include_deleted: bool = False
) -> Optional[ActuarialTable]:
    """
    Get actuarial table by ID
    
    Args:
        db: Database session
        table_id: Table UUID
        include_deleted: Include soft-deleted records
        
    Returns:
        ActuarialTable instance or None
    """
    query = db.query(ActuarialTable).filter(ActuarialTable.id == table_id)
    
    if not include_deleted:
        query = query.filter(ActuarialTable.is_deleted == False)
    
    return query.first()


def get_table_by_code(
    db: Session,
    table_code: str
) -> Optional[ActuarialTable]:
    """
    Get actuarial table by code
    
    Args:
        db: Database session
        table_code: Table code
        
    Returns:
        ActuarialTable instance or None
    """
    return db.query(ActuarialTable).filter(
        and_(
            ActuarialTable.table_code == table_code.upper(),
            ActuarialTable.is_deleted == False
        )
    ).first()


def get_tables_by_type(
    db: Session,
    table_type: TableType,
    include_inactive: bool = False
) -> List[ActuarialTable]:
    """
    Get all tables of a specific type
    
    Args:
        db: Database session
        table_type: Type of actuarial table
        include_inactive: Include inactive tables
        
    Returns:
        List of ActuarialTable instances
    """
    query = db.query(ActuarialTable).filter(
        and_(
            ActuarialTable.table_type == table_type,
            ActuarialTable.is_deleted == False
        )
    )
    
    if not include_inactive:
        query = query.filter(ActuarialTable.status == TableStatus.ACTIVE)
    
    return query.order_by(ActuarialTable.base_year.desc()).all()


def get_tables_list(
    db: Session,
    filters: Optional[ActuarialTableFilter] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Get paginated list of tables with filters
    
    Args:
        db: Database session
        filters: Filter criteria
        skip: Number of records to skip
        limit: Maximum number of records to return
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        Dictionary containing tables list and pagination info
    """
    query = db.query(ActuarialTable).filter(ActuarialTable.is_deleted == False)
    
    # Apply filters
    if filters:
        if filters.table_type:
            query = query.filter(ActuarialTable.table_type == filters.table_type)
        
        if filters.table_source:
            query = query.filter(ActuarialTable.table_source == filters.table_source)
        
        if filters.status:
            query = query.filter(ActuarialTable.status == filters.status)
        
        if filters.country:
            query = query.filter(ActuarialTable.country == filters.country.upper())
        
        if filters.region:
            query = query.filter(ActuarialTable.region.ilike(f"%{filters.region}%"))
        
        if filters.gender_specific is not None:
            query = query.filter(ActuarialTable.gender_specific == filters.gender_specific)
        
        if filters.smoking_specific is not None:
            query = query.filter(
                ActuarialTable.smoking_specific == filters.smoking_specific
            )
        
        if filters.base_year_from:
            query = query.filter(ActuarialTable.base_year >= filters.base_year_from)
        
        if filters.base_year_to:
            query = query.filter(ActuarialTable.base_year <= filters.base_year_to)
        
        if filters.search_term:
            search_pattern = f"%{filters.search_term}%"
            query = query.filter(
                or_(
                    ActuarialTable.table_code.ilike(search_pattern),
                    ActuarialTable.table_name.ilike(search_pattern),
                    ActuarialTable.description.ilike(search_pattern)
                )
            )
        
        if filters.tags:
            query = query.filter(ActuarialTable.tags.contains(filters.tags))
        
        if filters.effective_date_from:
            query = query.filter(
                ActuarialTable.effective_date >= filters.effective_date_from
            )
        
        if filters.effective_date_to:
            query = query.filter(ActuarialTable.effective_date <= filters.effective_date_to)
    
    # Get total count
    total_count = query.count()
    
    # Apply sorting
    if hasattr(ActuarialTable, sort_by):
        order_column = getattr(ActuarialTable, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    
    # Apply pagination
    tables = query.offset(skip).limit(limit).all()
    
    return {
        "tables": tables,
        "total_count": total_count,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "total_pages": (total_count + limit - 1) // limit
    }


def get_latest_table_version(
    db: Session,
    table_type: TableType,
    country: Optional[str] = None
) -> Optional[ActuarialTable]:
    """
    Get the latest version of a table type
    
    Args:
        db: Database session
        table_type: Type of actuarial table
        country: Optional country filter
        
    Returns:
        Latest ActuarialTable instance or None
    """
    query = db.query(ActuarialTable).filter(
        and_(
            ActuarialTable.table_type == table_type,
            ActuarialTable.status == TableStatus.ACTIVE,
            ActuarialTable.is_deleted == False
        )
    )
    
    if country:
        query = query.filter(ActuarialTable.country == country.upper())
    
    # Get latest by base year and version
    return query.order_by(
        ActuarialTable.base_year.desc(),
        ActuarialTable.version.desc()
    ).first()


# ================================================================
# UPDATE OPERATIONS
# ================================================================

def update_actuarial_table(
    db: Session,
    table_id: UUID,
    update_data: ActuarialTableUpdate,
    updated_by: Optional[UUID] = None
) -> ActuarialTable:
    """
    Update actuarial table
    
    Args:
        db: Database session
        table_id: Table UUID
        update_data: Update data
        updated_by: ID of the user updating the table
        
    Returns:
        Updated ActuarialTable instance
        
    Raises:
        NotFoundException: If table not found
        BadRequestException: If update fails
    """
    table = get_actuarial_table_by_id(db, table_id)
    
    if not table:
        raise NotFoundException(f"Actuarial table with ID {table_id} not found")
    
    try:
        # Handle table data update separately
        if update_data.table_data is not None:
            _validate_table_data(update_data.table_data)
            table.table_data = [
                row.model_dump() for row in update_data.table_data
            ]
        
        # Update other fields
        update_dict = update_data.model_dump(exclude_unset=True, exclude={'table_data'})
        
        for field, value in update_dict.items():
            setattr(table, field, value)
        
        table.updated_at = datetime.utcnow()
        table.updated_by = updated_by
        
        db.commit()
        db.refresh(table)
        
        logger.info(f"Updated actuarial table: {table_id}")
        return table
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating table: {str(e)}")
        raise BadRequestException(f"Failed to update table: {str(e)}")


def approve_actuarial_table(
    db: Session,
    table_id: UUID,
    approval_reference: str,
    approved_by: Optional[UUID] = None
) -> ActuarialTable:
    """
    Approve an actuarial table for use
    
    Args:
        db: Database session
        table_id: Table UUID
        approval_reference: Regulatory approval reference
        approved_by: ID of the user approving
        
    Returns:
        Approved ActuarialTable instance
    """
    table = get_actuarial_table_by_id(db, table_id)
    
    if not table:
        raise NotFoundException(f"Actuarial table with ID {table_id} not found")
    
    try:
        table.status = TableStatus.APPROVED
        table.regulatory_approval = approval_reference
        table.approval_date = date.today()
        table.updated_at = datetime.utcnow()
        table.updated_by = approved_by
        
        db.commit()
        db.refresh(table)
        
        logger.info(f"Approved actuarial table: {table_id}")
        return table
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving table: {str(e)}")
        raise BadRequestException(f"Failed to approve table: {str(e)}")


# ================================================================
# DELETE OPERATIONS
# ================================================================

def delete_actuarial_table(
    db: Session,
    table_id: UUID,
    soft_delete: bool = True,
    deleted_by: Optional[UUID] = None
) -> bool:
    """
    Delete actuarial table (soft or hard delete)
    
    Args:
        db: Database session
        table_id: Table UUID
        soft_delete: If True, perform soft delete
        deleted_by: ID of the user deleting the table
        
    Returns:
        True if deleted successfully
        
    Raises:
        NotFoundException: If table not found
    """
    table = get_actuarial_table_by_id(db, table_id, include_deleted=False)
    
    if not table:
        raise NotFoundException(f"Actuarial table with ID {table_id} not found")
    
    try:
        if soft_delete:
            table.is_deleted = True
            table.deleted_at = datetime.utcnow()
            table.deleted_by = deleted_by
            table.status = TableStatus.ARCHIVED
        else:
            db.delete(table)
        
        db.commit()
        
        logger.info(f"{'Soft' if soft_delete else 'Hard'} deleted table: {table_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting table: {str(e)}")
        raise BadRequestException(f"Failed to delete table: {str(e)}")


# ================================================================
# CALCULATION OPERATIONS
# ================================================================

def calculate_actuarial_value(
    db: Session,
    calculation_request: ActuarialCalculationRequest
) -> Dict[str, Any]:
    """
    Perform actuarial calculations using table data
    
    Args:
        db: Database session
        calculation_request: Calculation parameters
        
    Returns:
        Dictionary containing calculation results
        
    Raises:
        NotFoundException: If table not found or age not in table
    """
    table = get_actuarial_table_by_id(db, calculation_request.table_id)
    
    if not table:
        raise NotFoundException(
            f"Actuarial table with ID {calculation_request.table_id} not found"
        )
    
    # Find the appropriate rate from table data
    base_rate = _get_rate_from_table(
        table.table_data,
        calculation_request.age,
        calculation_request.gender,
        calculation_request.smoking_status
    )
    
    if base_rate is None:
        raise NotFoundException(
            f"No rate found for age {calculation_request.age} in table"
        )
    
    # Apply adjustments
    adjusted_rate = Decimal(str(base_rate))
    factors_applied = {"base_rate": float(base_rate)}
    
    # Apply improvement factor if available
    if calculation_request.apply_improvement:
        improvement_factor = _get_improvement_factor(
            table.table_data,
            calculation_request.age
        )
        if improvement_factor:
            adjusted_rate *= improvement_factor
            factors_applied["improvement_factor"] = float(improvement_factor)
    
    # Apply selection factor if requested
    if calculation_request.apply_selection:
        selection_factor = _get_selection_factor(
            table.table_data,
            calculation_request.age
        )
        if selection_factor:
            adjusted_rate *= selection_factor
            factors_applied["selection_factor"] = float(selection_factor)
    
    # Apply additional loading if specified
    if calculation_request.additional_loading:
        adjusted_rate *= (Decimal('1') + calculation_request.additional_loading)
        factors_applied["additional_loading"] = float(calculation_request.additional_loading)
    
    # Calculate premiums if sum insured is provided
    annual_premium = None
    monthly_premium = None
    net_premium = None
    gross_premium = None
    
    if calculation_request.sum_insured:
        # Simple premium calculation
        annual_premium = calculation_request.sum_insured * adjusted_rate
        monthly_premium = annual_premium / Decimal('12')
        
        # Net premium (without expenses/commission)
        net_premium = annual_premium * Decimal('0.9')  # 90% of gross
        
        # Gross premium (with expenses/commission)
        gross_premium = annual_premium * Decimal('1.1')  # 110% with loading
    
    # Calculate present value if interest rate and term provided
    present_value = None
    if (calculation_request.interest_rate and 
        calculation_request.term_years and 
        annual_premium):
        
        discount_factor = (
            Decimal('1') - 
            (Decimal('1') + calculation_request.interest_rate) ** 
            -calculation_request.term_years
        ) / calculation_request.interest_rate
        
        present_value = annual_premium * discount_factor
    
    return {
        "table_id": calculation_request.table_id,
        "base_rate": float(base_rate),
        "adjusted_rate": float(adjusted_rate),
        "annual_premium": float(annual_premium) if annual_premium else None,
        "monthly_premium": float(monthly_premium) if monthly_premium else None,
        "net_premium": float(net_premium) if net_premium else None,
        "gross_premium": float(gross_premium) if gross_premium else None,
        "present_value": float(present_value) if present_value else None,
        "reserve_amount": None,  # Would require more complex calculation
        "calculation_details": {
            "age": calculation_request.age,
            "gender": calculation_request.gender.value if calculation_request.gender else None,
            "smoking_status": calculation_request.smoking_status.value if calculation_request.smoking_status else None,
            "sum_insured": float(calculation_request.sum_insured) if calculation_request.sum_insured else None,
            "term_years": calculation_request.term_years,
            "interest_rate": float(calculation_request.interest_rate) if calculation_request.interest_rate else None
        },
        "factors_applied": factors_applied
    }


def _get_rate_from_table(
    table_data: List[Dict],
    age: int,
    gender: Optional[Gender],
    smoking_status: Optional[SmokingStatus]
) -> Optional[float]:
    """
    Extract rate from table data based on parameters
    
    Args:
        table_data: Table data as list of dictionaries
        age: Age
        gender: Optional gender
        smoking_status: Optional smoking status
        
    Returns:
        Rate value or None if not found
    """
    for row in table_data:
        if row.get('age') != age:
            continue
        
        # Check gender match if specified
        if gender and row.get('gender'):
            if row['gender'] != gender.value:
                continue
        
        # Check smoking status match if specified
        if smoking_status and row.get('smoking_status'):
            if row['smoking_status'] != smoking_status.value:
                continue
        
        # Return the appropriate rate
        if gender and smoking_status:
            # Look for specific rate first
            if gender == Gender.MALE and row.get('rate_male'):
                return row['rate_male']
            elif gender == Gender.FEMALE and row.get('rate_female'):
                return row['rate_female']
            
            if smoking_status == SmokingStatus.SMOKER and row.get('rate_smoker'):
                return row['rate_smoker']
            elif smoking_status == SmokingStatus.NON_SMOKER and row.get('rate_non_smoker'):
                return row['rate_non_smoker']
        
        # Return general rate
        return row.get('rate')
    
    return None


def _get_improvement_factor(
    table_data: List[Dict],
    age: int
) -> Optional[Decimal]:
    """Get improvement factor from table data"""
    for row in table_data:
        if row.get('age') == age and row.get('improvement_factor'):
            return Decimal(str(row['improvement_factor']))
    return None


def _get_selection_factor(
    table_data: List[Dict],
    age: int
) -> Optional[Decimal]:
    """Get selection factor from table data"""
    for row in table_data:
        if row.get('age') == age and row.get('selection_factor'):
            return Decimal(str(row['selection_factor']))
    return None


# ================================================================
# IMPORT/EXPORT OPERATIONS
# ================================================================

def import_actuarial_table(
    db: Session,
    file_data: Union[str, bytes],
    file_format: str,
    table_info: Dict[str, Any],
    created_by: Optional[UUID] = None
) -> ActuarialTable:
    """
    Import actuarial table from file
    
    Args:
        db: Database session
        file_data: File content
        file_format: Format (csv, excel, json)
        table_info: Table metadata
        created_by: ID of the user importing
        
    Returns:
        Created ActuarialTable instance
        
    Raises:
        BadRequestException: If import fails
    """
    try:
        # Parse file based on format
        if file_format == 'csv':
            table_data = _parse_csv_data(file_data)
        elif file_format == 'json':
            table_data = _parse_json_data(file_data)
        else:
            raise BadRequestException(f"Unsupported format: {file_format}")
        
        # Create table creation data
        create_data = ActuarialTableCreate(
            **table_info,
            table_data=table_data
        )
        
        # Create the table
        return create_actuarial_table(db, create_data, created_by)
        
    except Exception as e:
        logger.error(f"Error importing table: {str(e)}")
        raise BadRequestException(f"Import failed: {str(e)}")


def _parse_csv_data(csv_data: Union[str, bytes]) -> List[ActuarialDataRow]:
    """Parse CSV data into actuarial data rows"""
    if isinstance(csv_data, bytes):
        csv_data = csv_data.decode('utf-8')
    
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = []
    
    for row in reader:
        data_row = ActuarialDataRow(
            age=int(row['age']),
            rate=Decimal(row['rate']),
            gender=Gender(row['gender']) if row.get('gender') else None,
            smoking_status=SmokingStatus(row['smoking_status']) if row.get('smoking_status') else None,
            rate_male=Decimal(row['rate_male']) if row.get('rate_male') else None,
            rate_female=Decimal(row['rate_female']) if row.get('rate_female') else None,
            rate_smoker=Decimal(row['rate_smoker']) if row.get('rate_smoker') else None,
            rate_non_smoker=Decimal(row['rate_non_smoker']) if row.get('rate_non_smoker') else None
        )
        rows.append(data_row)
    
    return rows


def _parse_json_data(json_data: Union[str, bytes]) -> List[ActuarialDataRow]:
    """Parse JSON data into actuarial data rows"""
    if isinstance(json_data, bytes):
        json_data = json_data.decode('utf-8')
    
    data = json.loads(json_data)
    rows = []
    
    for item in data:
        data_row = ActuarialDataRow(**item)
        rows.append(data_row)
    
    return rows


def export_actuarial_table(
    db: Session,
    table_id: UUID,
    export_format: str = 'json'
) -> Union[str, bytes]:
    """
    Export actuarial table to file format
    
    Args:
        db: Database session
        table_id: Table UUID
        export_format: Format (csv, json, excel)
        
    Returns:
        Exported data as string or bytes
        
    Raises:
        NotFoundException: If table not found
    """
    table = get_actuarial_table_by_id(db, table_id)
    
    if not table:
        raise NotFoundException(f"Actuarial table with ID {table_id} not found")
    
    try:
        if export_format == 'json':
            return json.dumps(table.table_data, indent=2)
        elif export_format == 'csv':
            return _export_to_csv(table.table_data)
        else:
            raise BadRequestException(f"Unsupported export format: {export_format}")
            
    except Exception as e:
        logger.error(f"Error exporting table: {str(e)}")
        raise BadRequestException(f"Export failed: {str(e)}")


def _export_to_csv(table_data: List[Dict]) -> str:
    """Export table data to CSV format"""
    if not table_data:
        return ""
    
    output = io.StringIO()
    fieldnames = table_data[0].keys()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(table_data)
    
    return output.getvalue()


# ================================================================
# STATISTICS OPERATIONS
# ================================================================

def get_actuarial_statistics(db: Session) -> Dict[str, Any]:
    """
    Get actuarial table statistics
    
    Args:
        db: Database session
        
    Returns:
        Dictionary containing statistics
    """
    try:
        total_tables = db.query(func.count(ActuarialTable.id)).filter(
            ActuarialTable.is_deleted == False
        ).scalar()
        
        active_tables = db.query(func.count(ActuarialTable.id)).filter(
            and_(
                ActuarialTable.is_deleted == False,
                ActuarialTable.status == TableStatus.ACTIVE
            )
        ).scalar()
        
        approved_tables = db.query(func.count(ActuarialTable.id)).filter(
            and_(
                ActuarialTable.is_deleted == False,
                ActuarialTable.status == TableStatus.APPROVED
            )
        ).scalar()
        
        tables_by_type = db.query(
            ActuarialTable.table_type,
            func.count(ActuarialTable.id)
        ).filter(
            ActuarialTable.is_deleted == False
        ).group_by(ActuarialTable.table_type).all()
        
        tables_by_source = db.query(
            ActuarialTable.table_source,
            func.count(ActuarialTable.id)
        ).filter(
            ActuarialTable.is_deleted == False
        ).group_by(ActuarialTable.table_source).all()
        
        return {
            "total_tables": total_tables,
            "active_tables": active_tables,
            "approved_tables": approved_tables,
            "pending_approval": total_tables - approved_tables,
            "by_type": dict(tables_by_type),
            "by_source": dict(tables_by_source)
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise BadRequestException(f"Failed to get statistics: {str(e)}")


# ================================================================
# END OF REPOSITORY
# ================================================================