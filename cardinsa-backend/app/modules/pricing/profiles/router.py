# app/modules/pricing/profiles/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models.user_model import User

# Import sub-routers
from app.modules.pricing.profiles.routes.pricing_profile_route import router as profile_router
from app.modules.pricing.profiles.routes.pricing_rules_route import router as rules_router
from app.modules.pricing.profiles.routes.pricing_analytics_route import router as analytics_router

# Create the main router
router = APIRouter(prefix="/pricing/profiles", tags=["Pricing Profiles"])

# Include the sub-routers
router.include_router(profile_router, prefix="", tags=["Pricing Profiles - Core"])
router.include_router(rules_router, prefix="", tags=["Pricing Rules"])
router.include_router(analytics_router, prefix="", tags=["Pricing Analytics"])


@router.get("/health", tags=["Health"])
def pricing_profiles_health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Health check endpoint for pricing profiles module.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "module": "pricing_profiles",
        "version": "1.0.0",
        "database_status": db_status,
        "services": [
            "pricing_profile_service",
            "pricing_rules_service",
            "rule_evaluation_service",
            "pricing_profile_validation_service"
        ],
        "endpoints": {
            "profiles": "/pricing/profiles/",
            "rules": "/pricing/profiles/rules/",
            "analytics": "/pricing/profiles/analytics/"
        },
        "features": [
            "profile_management",
            "rule_management",
            "rule_evaluation",
            "async_evaluation",
            "batch_processing",
            "performance_analytics",
            "system_monitoring"
        ]
    }


@router.get("/info", tags=["Module Info"])
def get_module_info() -> Dict[str, Any]:
    """
    Get module information.
    """
    return {
        "module": "Pricing Profiles",
        "description": "Comprehensive pricing profile and rule management system",
        "version": "1.0.0",
        "components": {
            "models": 5,
            "services": 4,
            "repositories": 3,
            "routes": 3
        },
        "total_endpoints": 43,
        "status": "Production Ready"
    }