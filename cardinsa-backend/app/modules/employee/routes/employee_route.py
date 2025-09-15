from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.employee.services.employee_service import EmployeeService
from app.modules.employee.schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeOut

router = APIRouter()

@router.get("/", response_model=List[EmployeeOut], dependencies=[Depends(require_permission_scoped("employee", "read"))])
def list_items(db: Session = Depends(get_db)):
    return EmployeeService.get_all(db)

@router.post("/", response_model=EmployeeOut, dependencies=[Depends(require_permission_scoped("employee", "create"))])
def create_item(payload: EmployeeCreate, db: Session = Depends(get_db)):
    return EmployeeService.create(db, payload)

@router.put("/{employee_id}", response_model=EmployeeOut, dependencies=[Depends(require_permission_scoped("employee", "update"))])
def update_item(employee_id: str, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    return EmployeeService.update(db, employee_id, payload)

@router.delete("/{employee_id}", dependencies=[Depends(require_permission_scoped("employee", "delete"))])
def delete_item(employee_id: str, db: Session = Depends(get_db)):
    return EmployeeService.delete(db, employee_id)