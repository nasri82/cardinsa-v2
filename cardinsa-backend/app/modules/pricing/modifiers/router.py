# app/modules/pricing/modifiers/router.py

"""
Main router export for the Pricing Modifiers module.
This file exports the master router that includes all sub-routes.
"""

from app.modules.pricing.modifiers.routes.master_router import master_router

# Export the master router as the module's main router
router = master_router

# Alternative: If you want to keep individual routers accessible
from app.modules.pricing.modifiers.routes.pricing_deductible_route import router as deductible_router
from app.modules.pricing.modifiers.routes.pricing_copayment_route import router as copayment_router
from app.modules.pricing.modifiers.routes.pricing_discount_route import router as discount_router
from app.modules.pricing.modifiers.routes.pricing_commission_route import router as commission_router
from app.modules.pricing.modifiers.routes.pricing_industry_adjustment_route import router as industry_adjustment_router

__all__ = [
    "router",  # Main master router
    "deductible_router",
    "copayment_router", 
    "discount_router",
    "commission_router",
    "industry_adjustment_router"
]