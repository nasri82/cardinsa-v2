from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.employee.services.skill_tag_service import SkillTagService
from app.modules.employee.schemas.skill_tag_schema import SkillTagCreate, SkillTagUpdate, SkillTagOut

router = APIRouter()

@router.get("/", response_model=List[SkillTagOut], dependencies=[Depends(require_permission_scoped("skilltag", "read"))])
def list_items(db: Session = Depends(get_db)):
    return SkillTagService.get_all(db)

@router.post("/", response_model=SkillTagOut, dependencies=[Depends(require_permission_scoped("skilltag", "create"))])
def create_item(payload: SkillTagCreate, db: Session = Depends(get_db)):
    return SkillTagService.create(db, payload)

@router.put("/{tag_id}", response_model=SkillTagOut, dependencies=[Depends(require_permission_scoped("skilltag", "update"))])
def update_item(tag_id: str, payload: SkillTagUpdate, db: Session = Depends(get_db)):
    return SkillTagService.update(db, tag_id, payload)

@router.delete("/{tag_id}", dependencies=[Depends(require_permission_scoped("skilltag", "delete"))])
def delete_item(tag_id: str, db: Session = Depends(get_db)):
    return SkillTagService.delete(db, tag_id)