# app/modules/pricing/product/routes/actuarial_table_routes.py

"""
Actuarial Table Routes

API endpoints for actuarial table management and calculations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.pricing.product.services import actuarial_table_service as service
from app.modules.pricing.product.schemas.actuarial_table_schema import (
    ActuarialTableCreate,
    ActuarialTableUpdate,
    ActuarialTableResponse,
    ActuarialTableListResponse,
    ActuarialTableFilter,
    ActuarialCalculationRequest,
    ActuarialCalculationResponse,
    ActuarialTableImport,
    ActuarialTableExport,
    TableStatus,
    TableType,
    TableSource,
    Gender,
    SmokingStatus
)

router = APIRouter(
    prefix="/actuarial-tables",
    tags=["Actuarial Tables"]
)


# ================================================================
# CREATE ENDPOINTS
# ================================================================

@router.post(
    "/",
    response_model=ActuarialTableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create actuarial table"
)
async def create_table(
    table_data: ActuarialTableCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new actuarial table.
    
    - **table_code**: Unique table identifier
    - **table_name**: Display name of the table
    - **table_type**: Type (mortality, morbidity, lapse, etc.)
    - **table_source**: Source (industry, regulatory, company, etc.)
    - **base_year**: Base year for table data
    - **table_data**: Array of actuarial data rows
    """
    try:
        return service.create_actuarial_table(
            db, 
            table_data, 
            created_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/import",
    response_model=ActuarialTableResponse,
    summary="Import actuarial table"
)
async def import_table(
    file: UploadFile = File(..., description="CSV or JSON file"),
    table_code: str = Body(..., description="Unique table code"),
    table_name: str = Body(..., description="Table name"),
    table_type: TableType = Body(..., description="Table type"),
    table_source: TableSource = Body(..., description="Table source"),
    base_year: int = Body(..., description="Base year"),
    version: str = Body(..., description="Table version"),
    min_age: int = Body(0, description="Minimum age"),
    max_age: int = Body(120, description="Maximum age"),
    validate_only: bool = Body(False, description="Only validate without saving"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Import actuarial table from file.
    
    Supported formats:
    - CSV: Must have 'age' and 'rate' columns minimum
    - JSON: Array of objects with age and rate properties
    """
    try:
        # Read file content
        content = await file.read()
        
        # Determine format from file extension
        file_format = "csv" if file.filename.endswith(".csv") else "json"
        
        import_data = ActuarialTableImport(
            format=file_format,
            data=content,
            validate_only=validate_only
        )
        
        table_metadata = {
            "table_code": table_code,
            "table_name": table_name,
            "table_type": table_type,
            "table_source": table_source,
            "base_year": base_year,
            "version": version,
            "min_age": min_age,
            "max_age": max_age
        }
        
        return service.import_actuarial_table(
            db,
            import_data,
            table_metadata,
            created_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# READ ENDPOINTS
# ================================================================

@router.get(
    "/",
    response_model=ActuarialTableListResponse,
    summary="List actuarial tables"
)
async def list_tables(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    table_type: Optional[TableType] = Query(None, description="Filter by type"),
    table_source: Optional[TableSource] = Query(None, description="Filter by source"),
    status: Optional[TableStatus] = Query(None, description="Filter by status"),
    country: Optional[str] = Query(None, max_length=2, description="Country code (ISO)"),
    gender_specific: Optional[bool] = Query(None, description="Gender-specific tables"),
    smoking_specific: Optional[bool] = Query(None, description="Smoking-specific tables"),
    base_year_from: Optional[int] = Query(None, ge=1900, description="Base year from"),
    base_year_to: Optional[int] = Query(None, le=2100, description="Base year to"),
    search_term: Optional[str] = Query(None, description="Search in name/code/description"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of actuarial tables with optional filtering.
    """
    filters = ActuarialTableFilter(
        table_type=table_type,
        table_source=table_source,
        status=status,
        country=country,
        gender_specific=gender_specific,
        smoking_specific=smoking_specific,
        base_year_from=base_year_from,
        base_year_to=base_year_to,
        search_term=search_term,
        tags=tags
    )
    
    return service.search_actuarial_tables(db, filters, page, page_size)


@router.get(
    "/latest",
    response_model=ActuarialTableResponse,
    summary="Get latest table version"
)
async def get_latest_table(
    table_type: TableType = Query(..., description="Table type"),
    country: Optional[str] = Query(None, max_length=2, description="Country code"),
    db: Session = Depends(get_db)
):
    """
    Get the latest version of a specific table type.
    """
    try:
        return service.get_latest_table(db, table_type, country)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/{table_id}",
    response_model=dict,
    summary="Get table details"
)
async def get_table(
    table_id: UUID,
    include_analysis: bool = Query(True, description="Include statistical analysis"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive actuarial table details.
    
    Includes:
    - Table metadata
    - Complete data rows
    - Statistical analysis (if requested)
    """
    try:
        return service.get_actuarial_table(db, table_id, include_analysis)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# CALCULATION ENDPOINTS
# ================================================================

@router.post(
    "/calculate",
    response_model=ActuarialCalculationResponse,
    summary="Perform actuarial calculation"
)
async def calculate_actuarial_value(
    calculation_request: ActuarialCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Perform comprehensive actuarial calculations.
    
    Calculates:
    - Base and adjusted rates
    - Premiums (annual, monthly, net, gross)
    - Present values
    - Life expectancy (for mortality tables)
    - Reserve amounts
    """
    try:
        return service.perform_actuarial_calculation(db, calculation_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/calculate-premium",
    response_model=dict,
    summary="Calculate risk premium"
)
async def calculate_risk_premium(
    table_id: UUID = Body(..., description="Actuarial table UUID"),
    age: int = Body(..., ge=0, le=150, description="Age of insured"),
    sum_insured: float = Body(..., gt=0, description="Sum insured"),
    term_years: int = Body(1, ge=1, description="Term in years"),
    loading_factor: float = Body(1.2, ge=1.0, description="Loading for expenses/profit"),
    db: Session = Depends(get_db)
):
    """
    Calculate risk premium with loading.
    
    Returns:
    - Pure risk premium
    - Expense loading
    - Total premium
    - Monthly premium
    """
    try:
        return service.calculate_risk_premium(
            db,
            table_id,
            age,
            Decimal(str(sum_insured)),
            term_years,
            Decimal(str(loading_factor))
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# COMPARISON & ANALYSIS ENDPOINTS
# ================================================================

@router.post(
    "/compare",
    response_model=dict,
    summary="Compare actuarial tables"
)
async def compare_tables(
    table_ids: List[UUID] = Body(..., min_items=2, max_items=5, description="Tables to compare"),
    age_range: Optional[List[int]] = Body(None, min_items=2, max_items=2, description="Age range [min, max]"),
    db: Session = Depends(get_db)
):
    """
    Compare multiple actuarial tables.
    
    - Minimum 2 tables, maximum 5 tables
    - Compare rates across age range
    - Variance analysis
    - Consistency scoring
    """
    try:
        return service.compare_actuarial_tables(
            db,
            table_ids,
            tuple(age_range) if age_range else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/mortality-improvement",
    response_model=dict,
    summary="Analyze mortality improvement"
)
async def analyze_mortality_improvement(
    old_table_id: UUID = Body(..., description="Older table UUID"),
    new_table_id: UUID = Body(..., description="Newer table UUID"),
    db: Session = Depends(get_db)
):
    """
    Analyze mortality improvement between two tables.
    
    Returns:
    - Improvement by age
    - Average improvement percentage
    - Life expectancy changes
    - Annual improvement rates
    """
    try:
        return service.analyze_mortality_improvement(
            db, old_table_id, new_table_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# UPDATE ENDPOINTS
# ================================================================

@router.put(
    "/{table_id}",
    response_model=ActuarialTableResponse,
    summary="Update actuarial table"
)
async def update_table(
    table_id: UUID,
    update_data: ActuarialTableUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update actuarial table.
    
    Can update:
    - Table metadata
    - Table data (complete replacement)
    - Status
    - Regulatory approval
    """
    try:
        from app.modules.pricing.product.repositories import actuarial_table_repository as repo
        
        updated_table = repo.update_actuarial_table(
            db,
            table_id,
            update_data,
            updated_by=current_user.get("user_id")
        )
        
        # Convert table_data for response
        updated_table.table_data = [
            ActuarialDataRow(**row) if isinstance(row, dict) else row
            for row in updated_table.table_data
        ]
        
        return ActuarialTableResponse.model_validate(updated_table)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{table_id}/factors",
    response_model=ActuarialTableResponse,
    summary="Update table factors"
)
async def update_factors(
    table_id: UUID,
    improvement_factor: Optional[float] = Body(None, ge=0, description="Improvement factor"),
    selection_factor: Optional[float] = Body(None, ge=0, description="Selection factor"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update improvement and selection factors for a table.
    
    Applies the same factors to all rows in the table.
    """
    try:
        return service.update_table_factors(
            db,
            table_id,
            Decimal(str(improvement_factor)) if improvement_factor else None,
            Decimal(str(selection_factor)) if selection_factor else None,
            updated_by=current_user.get("user_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{table_id}/approve",
    response_model=ActuarialTableResponse,
    summary="Approve actuarial table"
)
async def approve_table(
    table_id: UUID,
    approval_reference: str = Body(..., description="Regulatory approval reference"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Approve an actuarial table for use.
    
    Sets status to APPROVED and records approval reference.
    """
    try:
        from app.modules.pricing.product.repositories import actuarial_table_repository as repo
        
        table = repo.approve_actuarial_table(
            db,
            table_id,
            approval_reference,
            approved_by=current_user.get("user_id")
        )
        
        # Convert table_data for response
        table.table_data = [
            ActuarialDataRow(**row) if isinstance(row, dict) else row
            for row in table.table_data
        ]
        
        return ActuarialTableResponse.model_validate(table)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/bulk-approve",
    response_model=dict,
    summary="Bulk approve tables"
)
async def bulk_approve_tables(
    table_ids: List[UUID] = Body(..., description="Tables to approve"),
    approval_reference: str = Body(..., description="Regulatory approval reference"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Approve multiple actuarial tables.
    """
    return service.bulk_approve_tables(
        db,
        table_ids,
        approval_reference,
        approved_by=current_user.get("user_id")
    )


# ================================================================
# EXPORT ENDPOINTS
# ================================================================

@router.post(
    "/export",
    response_model=dict,
    summary="Export actuarial tables"
)
async def export_tables(
    export_request: ActuarialTableExport,
    db: Session = Depends(get_db)
):
    """
    Export actuarial tables to various formats.
    
    Supported formats:
    - CSV
    - JSON
    - Excel (if configured)
    """
    try:
        return service.export_actuarial_tables(db, export_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{table_id}/export",
    summary="Export single table"
)
async def export_single_table(
    table_id: UUID,
    format: str = Query("json", pattern="^(csv|json)$", description="Export format"),
    db: Session = Depends(get_db)
):
    """
    Export a single actuarial table.
    """
    from app.modules.pricing.product.repositories import actuarial_table_repository as repo
    
    try:
        data = repo.export_actuarial_table(db, table_id, format)
        
        # Return appropriate response based on format
        if format == "csv":
            from fastapi.responses import Response
            return Response(
                content=data,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=table_{table_id}.csv"
                }
            )
        else:
            return {"format": format, "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# VALIDATION & COMPLIANCE ENDPOINTS
# ================================================================

@router.get(
    "/{table_id}/validate",
    response_model=dict,
    summary="Validate table compliance"
)
async def validate_compliance(
    table_id: UUID,
    regulatory_standard: Optional[str] = Query(None, description="Standard to validate against (SOA, NAIC, etc.)"),
    db: Session = Depends(get_db)
):
    """
    Validate table compliance with regulatory standards.
    
    Checks:
    - Approval status
    - Data completeness
    - Rate validity
    - Table age
    - Standard-specific requirements
    """
    try:
        return service.validate_table_compliance(
            db, table_id, regulatory_standard
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ================================================================
# ANALYTICS & REPORTING ENDPOINTS
# ================================================================

@router.get(
    "/{table_id}/usage",
    response_model=dict,
    summary="Get table usage analytics"
)
async def get_usage_analytics(
    table_id: UUID,
    period_days: int = Query(30, ge=1, description="Analysis period in days"),
    db: Session = Depends(get_db)
):
    """
    Get usage analytics for an actuarial table (mock data).
    
    Returns:
    - Usage statistics
    - Calculation breakdown
    - Performance metrics
    - Related products
    """
    return service.get_table_usage_analytics(db, table_id, period_days)


@router.post(
    "/report",
    response_model=dict,
    summary="Generate actuarial report"
)
async def generate_report(
    report_type: str = Body(..., pattern="^(mortality_analysis|table_comparison|portfolio_summary)$"),
    parameters: Dict[str, Any] = Body(..., description="Report parameters"),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive actuarial report.
    
    Report types:
    - mortality_analysis: Analyze mortality patterns
    - table_comparison: Compare multiple tables
    - portfolio_summary: Overview of all tables
    """
    try:
        return service.generate_actuarial_report(db, report_type, parameters)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/statistics",
    response_model=dict,
    summary="Get actuarial statistics"
)
async def get_statistics(
    db: Session = Depends(get_db)
):
    """
    Get overall actuarial table statistics.
    """
    from app.modules.pricing.product.repositories import actuarial_table_repository as repo
    
    return repo.get_actuarial_statistics(db)


# ================================================================
# DELETE ENDPOINTS
# ================================================================

@router.delete(
    "/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete actuarial table"
)
async def delete_table(
    table_id: UUID,
    soft_delete: bool = Query(True, description="Soft delete (can be recovered)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an actuarial table (soft or hard delete).
    """
    from app.modules.pricing.product.repositories import actuarial_table_repository as repo
    
    try:
        repo.delete_actuarial_table(
            db,
            table_id,
            soft_delete,
            deleted_by=current_user.get("user_id")
        )
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ================================================================
# END OF ROUTES
# ================================================================