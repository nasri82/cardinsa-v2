# app/modules/pricing/modifiers/routes/master_router.py

"""
Master Router for Pricing Modifiers Module
Orchestrates all pricing component routes with organized grouping
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.core.responses import success_response, error_response

# Import individual route modules
from app.modules.pricing.modifiers.routes.pricing_deductible_route import router as deductible_router
from app.modules.pricing.modifiers.routes.pricing_copayment_route import router as copayment_router
from app.modules.pricing.modifiers.routes.pricing_discount_route import router as discount_router
from app.modules.pricing.modifiers.routes.pricing_commission_route import router as commission_router
from app.modules.pricing.modifiers.routes.pricing_industry_adjustment_route import router as industry_adjustment_router

# Import services for aggregated operations
from app.modules.pricing.modifiers.services import (
    pricing_deductible_service,
    pricing_copayment_service,
    pricing_discount_service,
    pricing_commission_service,
    pricing_industry_adjustment_service,
)

# Create the master router
master_router = APIRouter(
    prefix="/pricing/modifiers",
    tags=["Pricing Modifiers"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
    }
)

# ==================== SUB-ROUTERS ====================
# Include all individual component routers
master_router.include_router(deductible_router, prefix="/deductibles", tags=["Deductibles"])
master_router.include_router(copayment_router, prefix="/copayments", tags=["Copayments"])
master_router.include_router(discount_router, prefix="/discounts", tags=["Discounts"])
master_router.include_router(commission_router, prefix="/commissions", tags=["Commissions"])
master_router.include_router(industry_adjustment_router, prefix="/industry-adjustments", tags=["Industry Adjustments"])

# ==================== AGGREGATE ENDPOINTS ====================

@master_router.get("/", response_model=Dict[str, Any])
async def get_all_modifiers(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    active_only: bool = True
):
    """
    Get all pricing modifiers in a single call.
    Useful for loading all configuration data at once.
    """
    try:
        # Fetch all components
        deductibles = pricing_deductible_service.get_all(db)
        copayments = pricing_copayment_service.get_all(db)
        discounts = pricing_discount_service.get_all(db)
        commissions = pricing_commission_service.get_all(db)
        industry_adjustments = pricing_industry_adjustment_service.get_all(db)
        
        # Filter active only if requested
        if active_only:
            deductibles = [d for d in deductibles if d.is_active]
            copayments = [c for c in copayments if c.is_active]
            discounts = [d for d in discounts if d.is_active]
            commissions = [c for c in commissions if c.is_active]
            industry_adjustments = [i for i in industry_adjustments if i.is_active]
        
        return success_response(
            data={
                "deductibles": deductibles,
                "copayments": copayments,
                "discounts": discounts,
                "commissions": commissions,
                "industry_adjustments": industry_adjustments,
                "summary": {
                    "total_deductibles": len(deductibles),
                    "total_copayments": len(copayments),
                    "total_discounts": len(discounts),
                    "total_commissions": len(commissions),
                    "total_industry_adjustments": len(industry_adjustments),
                }
            },
            message="All pricing modifiers retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to retrieve pricing modifiers: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@master_router.get("/summary", response_model=Dict[str, Any])
async def get_modifiers_summary(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get a summary of all pricing modifiers.
    Returns counts and basic statistics.
    """
    try:
        # Get counts for each modifier type
        deductibles = pricing_deductible_service.get_all(db)
        copayments = pricing_copayment_service.get_all(db)
        discounts = pricing_discount_service.get_all(db)
        commissions = pricing_commission_service.get_all(db)
        industry_adjustments = pricing_industry_adjustment_service.get_all(db)
        
        # Calculate statistics
        active_deductibles = sum(1 for d in deductibles if d.is_active)
        active_copayments = sum(1 for c in copayments if c.is_active)
        active_discounts = sum(1 for d in discounts if d.is_active)
        active_commissions = sum(1 for c in commissions if c.is_active)
        active_industry_adjustments = sum(1 for i in industry_adjustments if i.is_active)
        
        summary = {
            "deductibles": {
                "total": len(deductibles),
                "active": active_deductibles,
                "inactive": len(deductibles) - active_deductibles
            },
            "copayments": {
                "total": len(copayments),
                "active": active_copayments,
                "inactive": len(copayments) - active_copayments
            },
            "discounts": {
                "total": len(discounts),
                "active": active_discounts,
                "inactive": len(discounts) - active_discounts
            },
            "commissions": {
                "total": len(commissions),
                "active": active_commissions,
                "inactive": len(commissions) - active_commissions
            },
            "industry_adjustments": {
                "total": len(industry_adjustments),
                "active": active_industry_adjustments,
                "inactive": len(industry_adjustments) - active_industry_adjustments
            },
            "totals": {
                "all_modifiers": sum([
                    len(deductibles),
                    len(copayments),
                    len(discounts),
                    len(commissions),
                    len(industry_adjustments)
                ]),
                "active_modifiers": sum([
                    active_deductibles,
                    active_copayments,
                    active_discounts,
                    active_commissions,
                    active_industry_adjustments
                ])
            }
        }
        
        return success_response(
            data=summary,
            message="Modifiers summary generated successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to generate summary: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@master_router.post("/bulk-update-status", response_model=Dict[str, Any])
async def bulk_update_modifier_status(
    modifier_type: str,
    ids: List[str],
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Bulk update the active status of modifiers.
    
    Args:
        modifier_type: Type of modifier (deductibles, copayments, discounts, commissions, industry_adjustments)
        ids: List of modifier IDs to update
        is_active: New active status
    """
    try:
        # Map modifier types to services
        service_map = {
            "deductibles": pricing_deductible_service,
            "copayments": pricing_copayment_service,
            "discounts": pricing_discount_service,
            "commissions": pricing_commission_service,
            "industry_adjustments": pricing_industry_adjustment_service,
        }
        
        if modifier_type not in service_map:
            return error_response(
                message=f"Invalid modifier type: {modifier_type}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        service = service_map[modifier_type]
        updated_count = 0
        failed_ids = []
        
        for id_str in ids:
            try:
                # Update each modifier
                result = service.update(
                    db, 
                    id_str, 
                    {"is_active": is_active}
                )
                if result:
                    updated_count += 1
                else:
                    failed_ids.append(id_str)
            except Exception:
                failed_ids.append(id_str)
        
        return success_response(
            data={
                "updated_count": updated_count,
                "failed_ids": failed_ids,
                "total_requested": len(ids)
            },
            message=f"Bulk status update completed for {modifier_type}"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to update modifier status: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@master_router.get("/search", response_model=Dict[str, Any])
async def search_modifiers(
    query: str,
    modifier_types: str = None,  # comma-separated list
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Search across all modifier types.
    
    Args:
        query: Search query string
        modifier_types: Comma-separated list of types to search (e.g., "deductibles,copayments")
        active_only: Whether to return only active modifiers
    """
    try:
        results = {}
        query_lower = query.lower()
        
        # Determine which types to search
        if modifier_types:
            types_to_search = [t.strip() for t in modifier_types.split(",")]
        else:
            types_to_search = ["deductibles", "copayments", "discounts", "commissions", "industry_adjustments"]
        
        # Search deductibles
        if "deductibles" in types_to_search:
            all_deductibles = pricing_deductible_service.get_all(db)
            deductibles = [
                d for d in all_deductibles
                if (query_lower in d.code.lower() or query_lower in d.label.lower())
                and (not active_only or d.is_active)
            ]
            if deductibles:
                results["deductibles"] = deductibles
        
        # Search copayments
        if "copayments" in types_to_search:
            all_copayments = pricing_copayment_service.get_all(db)
            copayments = [
                c for c in all_copayments
                if (query_lower in c.code.lower() or query_lower in c.label.lower())
                and (not active_only or c.is_active)
            ]
            if copayments:
                results["copayments"] = copayments
        
        # Search discounts
        if "discounts" in types_to_search:
            all_discounts = pricing_discount_service.get_all(db)
            discounts = [
                d for d in all_discounts
                if (query_lower in d.code.lower() or query_lower in d.label.lower())
                and (not active_only or d.is_active)
            ]
            if discounts:
                results["discounts"] = discounts
        
        # Search commissions
        if "commissions" in types_to_search:
            all_commissions = pricing_commission_service.get_all(db)
            commissions = [
                c for c in all_commissions
                if (query_lower in c.channel.lower() or query_lower in c.commission_type.lower())
                and (not active_only or c.is_active)
            ]
            if commissions:
                results["commissions"] = commissions
        
        # Search industry adjustments
        if "industry_adjustments" in types_to_search:
            all_adjustments = pricing_industry_adjustment_service.get_all(db)
            adjustments = [
                a for a in all_adjustments
                if query_lower in a.industry_code.lower()
                and (not active_only or a.is_active)
            ]
            if adjustments:
                results["industry_adjustments"] = adjustments
        
        # Count results
        total_results = sum(len(items) for items in results.values())
        
        return success_response(
            data={
                "results": results,
                "summary": {
                    "query": query,
                    "total_results": total_results,
                    "types_searched": types_to_search
                }
            },
            message=f"Found {total_results} results for '{query}'"
        )
    except Exception as e:
        return error_response(
            message=f"Search failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@master_router.get("/validate", response_model=Dict[str, Any])
async def validate_modifiers_configuration(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Validate the entire modifiers configuration.
    Checks for missing required configurations, conflicts, etc.
    """
    try:
        issues = []
        warnings = []
        
        # Check for at least one active configuration of each type
        deductibles = pricing_deductible_service.get_all(db)
        copayments = pricing_copayment_service.get_all(db)
        discounts = pricing_discount_service.get_all(db)
        commissions = pricing_commission_service.get_all(db)
        industry_adjustments = pricing_industry_adjustment_service.get_all(db)
        
        # Validation checks
        if not any(d.is_active for d in deductibles):
            warnings.append("No active deductibles configured")
        
        if not any(c.is_active for c in copayments):
            warnings.append("No active copayments configured")
        
        if not any(d.is_active for d in discounts):
            warnings.append("No active discounts configured")
        
        if not any(c.is_active for c in commissions):
            warnings.append("No active commissions configured")
        
        if not any(i.is_active for i in industry_adjustments):
            warnings.append("No active industry adjustments configured")
        
        # Check for duplicate codes
        deductible_codes = [d.code for d in deductibles if d.is_active]
        if len(deductible_codes) != len(set(deductible_codes)):
            issues.append("Duplicate deductible codes found")
        
        copayment_codes = [c.code for c in copayments if c.is_active]
        if len(copayment_codes) != len(set(copayment_codes)):
            issues.append("Duplicate copayment codes found")
        
        discount_codes = [d.code for d in discounts if d.is_active]
        if len(discount_codes) != len(set(discount_codes)):
            issues.append("Duplicate discount codes found")
        
        # Validation result
        is_valid = len(issues) == 0
        
        return success_response(
            data={
                "is_valid": is_valid,
                "issues": issues,
                "warnings": warnings,
                "statistics": {
                    "total_deductibles": len(deductibles),
                    "active_deductibles": sum(1 for d in deductibles if d.is_active),
                    "total_copayments": len(copayments),
                    "active_copayments": sum(1 for c in copayments if c.is_active),
                    "total_discounts": len(discounts),
                    "active_discounts": sum(1 for d in discounts if d.is_active),
                    "total_commissions": len(commissions),
                    "active_commissions": sum(1 for c in commissions if c.is_active),
                    "total_industry_adjustments": len(industry_adjustments),
                    "active_industry_adjustments": sum(1 for i in industry_adjustments if i.is_active),
                }
            },
            message="Configuration validation completed"
        )
    except Exception as e:
        return error_response(
            message=f"Validation failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Export the router
__all__ = ["master_router"]