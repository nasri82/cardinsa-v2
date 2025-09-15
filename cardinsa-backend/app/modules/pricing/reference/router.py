from fastapi import APIRouter

from app.modules.pricing.reference.routes.cpt_code_route import router as cpt_code_router
from app.modules.pricing.reference.routes.icd10_code_route import router as icd10_code_router
from app.modules.pricing.reference.routes.motor_exclusion_category_route import router as motor_exclusion_category_router
from app.modules.pricing.reference.routes.motor_exclusion_code_route import router as motor_exclusion_code_router
from app.modules.pricing.reference.routes.medical_exclusion_category_route import router as medical_exclusion_category_router
from app.modules.pricing.reference.routes.medical_exclusion_code_route import router as medical_exclusion_code_router

router = APIRouter(prefix="/reference", tags=["Pricing - Reference"])

router.include_router(cpt_code_router, prefix="/cpt-codes")
router.include_router(icd10_code_router, prefix="/icd10-codes")
router.include_router(motor_exclusion_category_router, prefix="/motor-exclusion-categories")
router.include_router(motor_exclusion_code_router, prefix="/motor-exclusion-codes")
router.include_router(medical_exclusion_category_router, prefix="/medical-exclusion-categories")
router.include_router(medical_exclusion_code_router, prefix="/medical-exclusion-codes")
