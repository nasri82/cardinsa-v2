from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.employee.services.skills_development_plan_service import SkillsDevelopmentPlanService
from app.modules.employee.schemas.skills_development_plan_schema import SkillsDevelopmentPlanCreate, SkillsDevelopmentPlanUpdate, SkillsDevelopmentPlanOut

router = APIRouter()

@router.get("/", response_model=List[SkillsDevelopmentPlanOut], dependencies=[Depends(require_permission_scoped("skillsdevelopmentplan", "read"))])
def list_items(db: Session = Depends(get_db)):
    return SkillsDevelopmentPlanService.get_all(db)

@router.post("/", response_model=SkillsDevelopmentPlanOut, dependencies=[Depends(require_permission_scoped("skillsdevelopmentplan", "create"))])
def create_item(payload: SkillsDevelopmentPlanCreate, db: Session = Depends(get_db)):
    return SkillsDevelopmentPlanService.create(db, payload)

@router.put("/{plan_id}", response_model=SkillsDevelopmentPlanOut, dependencies=[Depends(require_permission_scoped("skillsdevelopmentplan", "update"))])
def update_item(plan_id: str, payload: SkillsDevelopmentPlanUpdate, db: Session = Depends(get_db)):
    return SkillsDevelopmentPlanService.update(db, plan_id, payload)

@router.delete("/{plan_id}", dependencies=[Depends(require_permission_scoped("skillsdevelopmentplan", "delete"))])
def delete_item(plan_id: str, db: Session = Depends(get_db)):
    return SkillsDevelopmentPlanService.delete(db, plan_id)