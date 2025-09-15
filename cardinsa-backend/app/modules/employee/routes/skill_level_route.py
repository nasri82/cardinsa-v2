from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.employee.services.skill_level_service import SkillLevelService
from app.modules.employee.schemas.skill_level_schema import SkillLevelCreate, SkillLevelUpdate, SkillLevelOut

router = APIRouter()

@router.get("/", response_model=List[SkillLevelOut], dependencies=[Depends(require_permission_scoped("skilllevel", "read"))])
def list_items(db: Session = Depends(get_db)):
    return SkillLevelService.get_all(db)

@router.post("/", response_model=SkillLevelOut, dependencies=[Depends(require_permission_scoped("skilllevel", "create"))])
def create_item(payload: SkillLevelCreate, db: Session = Depends(get_db)):
    return SkillLevelService.create(db, payload)

@router.put("/{level_id}", response_model=SkillLevelOut, dependencies=[Depends(require_permission_scoped("skilllevel", "update"))])
def update_item(level_id: str, payload: SkillLevelUpdate, db: Session = Depends(get_db)):
    return SkillLevelService.update(db, level_id, payload)

@router.delete("/{level_id}", dependencies=[Depends(require_permission_scoped("skilllevel", "delete"))])
def delete_item(level_id: str, db: Session = Depends(get_db)):
    return SkillLevelService.delete(db, level_id)