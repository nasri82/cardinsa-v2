from fastapi import APIRouter

from app.modules.pricing.modifiers.routes.pricing_deductible_route import router as deductible_router
from app.modules.pricing.modifiers.routes.pricing_copayment_route import router as copayment_router
from app.modules.pricing.modifiers.routes.pricing_discount_route import router as discount_router
from app.modules.pricing.modifiers.routes.pricing_commission_route import router as commission_router
from app.modules.pricing.modifiers.routes.pricing_industry_adjustment_route import router as industry_adjustment_router

router = APIRouter()

router.include_router(deductible_router)
router.include_router(copayment_router)
router.include_router(discount_router)
router.include_router(commission_router)
router.include_router(industry_adjustment_router)
