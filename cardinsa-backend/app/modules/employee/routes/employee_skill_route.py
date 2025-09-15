from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.employee.services.employee_skill_service import EmployeeSkillService
from app.modules.employee.schemas.employee_skill_schema import EmployeeSkillCreate, EmployeeSkillUpdate, EmployeeSkillOut

router = APIRouter()

@router.get("/", response_model=List[EmployeeSkillOut], dependencies=[Depends(require_permission_scoped("employeeskill", "read"))])
def list_items(db: Session = Depends(get_db)):
    return EmployeeSkillService.get_all(db)

@router.post("/", response_model=EmployeeSkillOut, dependencies=[Depends(require_permission_scoped("employeeskill", "create"))])
def create_item(payload: EmployeeSkillCreate, db: Session = Depends(get_db)):
    return EmployeeSkillService.create(db, payload)

@router.put("/{skill_id}", response_model=EmployeeSkillOut, dependencies=[Depends(require_permission_scoped("employeeskill", "update"))])
def update_item(skill_id: str, payload: EmployeeSkillUpdate, db: Session = Depends(get_db)):
    return EmployeeSkillService.update(db, skill_id, payload)

@router.delete("/{skill_id}", dependencies=[Depends(require_permission_scoped("employeeskill", "delete"))])
def delete_item(skill_id: str, db: Session = Depends(get_db)):
    return EmployeeSkillService.delete(db, skill_id)