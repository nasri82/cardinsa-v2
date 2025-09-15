from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.employee.services.skill_category_service import SkillCategoryService
from app.modules.employee.schemas.skill_category_schema import SkillCategoryCreate, SkillCategoryUpdate, SkillCategoryOut

router = APIRouter()

@router.get("/", response_model=List[SkillCategoryOut], dependencies=[Depends(require_permission_scoped("skillcategory", "read"))])
def list_items(db: Session = Depends(get_db)):
    return SkillCategoryService.get_all(db)

@router.post("/", response_model=SkillCategoryOut, dependencies=[Depends(require_permission_scoped("skillcategory", "create"))])
def create_item(payload: SkillCategoryCreate, db: Session = Depends(get_db)):
    return SkillCategoryService.create(db, payload)

@router.put("/{category_id}", response_model=SkillCategoryOut, dependencies=[Depends(require_permission_scoped("skillcategory", "update"))])
def update_item(category_id: str, payload: SkillCategoryUpdate, db: Session = Depends(get_db)):
    return SkillCategoryService.update(db, category_id, payload)

@router.delete("/{category_id}", dependencies=[Depends(require_permission_scoped("skillcategory", "delete"))])
def delete_item(category_id: str, db: Session = Depends(get_db)):
    return SkillCategoryService.delete(db, category_id)