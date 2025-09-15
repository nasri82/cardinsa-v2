from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, asc, desc
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.common.pagination import Page, PageMeta, paginate

from app.modules.org.permissions import DEPARTMENTS_READ, DEPARTMENTS_MANAGE
from app.modules.org.models.department_model import Department
from app.modules.org.models.company_model import Company
from app.modules.org.schemas.department_schema import (
    DepartmentCreate, DepartmentUpdate, DepartmentOut
)

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get(
    "",
    response_model=Page[DepartmentOut],
    dependencies=[Depends(require_permission_scoped(*DEPARTMENTS_READ))],
)
def list_departments(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    company_id: UUID | None = Query(default=None),
    search: str | None = Query(default=None, description="Search in name/code"),
    sort: str = Query("name", regex="^(name|code|created_at)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
):
    stmt = select(Department)

    if company_id:
        stmt = stmt.where(Department.company_id == company_id)

    if search:
        s = f"%{search.lower()}%"
        stmt = stmt.where(or_(Department.name.ilike(s), Department.code.ilike(s)))

    sort_col = {"name": Department.name, "code": Department.code, "created_at": Department.created_at}[sort]
    stmt = stmt.order_by(asc(sort_col) if order == "asc" else desc(sort_col))

    total, items = paginate(db, stmt, page, page_size)
    return Page[DepartmentOut](
        items=[DepartmentOut.model_validate(i) for i in items],
        meta=PageMeta(page=page, page_size=page_size, total=total),
    )

@router.post(
    "",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission_scoped(*DEPARTMENTS_MANAGE))],
)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    # Parent must exist
    company = db.get(Company, payload.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Uniqueness within company scope
    dupe = db.scalar(
        select(Department)
        .where(
            Department.company_id == payload.company_id,
            or_(Department.name == payload.name, Department.code == payload.code),
        )
        .limit(1)
    )
    if dupe:
        raise HTTPException(status_code=409, detail="Department name or code already exists in this company")

    obj = Department(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get(
    "/{department_id}",
    response_model=DepartmentOut,
    dependencies=[Depends(require_permission_scoped(*DEPARTMENTS_READ))],
)
def get_department(department_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Department, department_id)
    if not obj:
        raise HTTPException(404, "Department not found")
    return obj

@router.patch(
    "/{department_id}",
    response_model=DepartmentOut,
    dependencies=[Depends(require_permission_scoped(*DEPARTMENTS_MANAGE))],
)
def update_department(department_id: UUID, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    obj = db.get(Department, department_id)
    if not obj:
        raise HTTPException(404, "Department not found")

    # Enforce uniqueness within the same company scope (company_id not editable by schema)
    if payload.name is not None or payload.code is not None:
        q = select(Department).where(
            Department.company_id == obj.company_id,
            Department.id != department_id,
        )
        if payload.name is not None:
            q = q.where(Department.name == payload.name)
        if payload.code is not None:
            q = q.where(Department.code == payload.code)
        dupe = db.scalar(q.limit(1))
        if dupe:
            raise HTTPException(status_code=409, detail="Department name or code already exists in this company")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.post(
    "/{department_id}/activate",
    dependencies=[Depends(require_permission_scoped(*DEPARTMENTS_MANAGE))],
)
def activate_department(department_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Department, department_id)
    if not obj:
        raise HTTPException(404, "Department not found")
    obj.is_active = True; db.add(obj); db.commit()
    return {"status": "ok"}

@router.post(
    "/{department_id}/deactivate",
    dependencies=[Depends(require_permission_scoped(*DEPARTMENTS_MANAGE))],
)
def deactivate_department(department_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Department, department_id)
    if not obj:
        raise HTTPException(404, "Department not found")
    obj.is_active = False; db.add(obj); db.commit()
    return {"status": "ok"}

@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission_scoped(*DEPARTMENTS_MANAGE))],
)
def delete_department(department_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Department, department_id)
    if not obj:
        raise HTTPException(404, "Department not found")
    db.delete(obj); db.commit()
