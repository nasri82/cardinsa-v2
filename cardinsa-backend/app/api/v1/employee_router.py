# app/api/v1/employee_router.py

from fastapi import APIRouter
from app.modules.employee.routes import (
    employee_route,
    employee_skill_route,
    skills_taxonomy_route,
    skill_level_route,
    skill_category_route,
    skill_tag_route,
    skills_gap_analysis_route,
    skills_demand_forecast_route,
    skills_development_plan_route,
)

router = APIRouter(prefix="/employee", tags=["Employee Module"])

router.include_router(employee_route.router, prefix="/employees", tags=["Employees"])
router.include_router(employee_skill_route.router, prefix="/skills", tags=["Employee Skills"])
router.include_router(skills_taxonomy_route.router, prefix="/taxonomy", tags=["Skills Taxonomy"])
router.include_router(skill_level_route.router, prefix="/levels", tags=["Skill Levels"])
router.include_router(skill_category_route.router, prefix="/categories", tags=["Skill Categories"])
router.include_router(skill_tag_route.router, prefix="/tags", tags=["Skill Tags"])
router.include_router(skills_gap_analysis_route.router, prefix="/gap-analysis", tags=["Gap Analysis"])
router.include_router(skills_demand_forecast_route.router, prefix="/forecast", tags=["Demand Forecast"])
router.include_router(skills_development_plan_route.router, prefix="/development", tags=["Development Plans"])
