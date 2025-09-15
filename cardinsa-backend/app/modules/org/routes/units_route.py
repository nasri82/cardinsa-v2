from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, asc, desc
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.common.pagination import Page, PageMeta, paginate

from app.modules.org.permissions import UNITS_READ, UNITS_MANAGE
from app.modules.org.models.unit_model import Unit
from app.modules.org.models.department_model import Department
from app.modules.org.schemas.unit_schema import UnitCreate, UnitUpdate, UnitOut

router = APIRouter(prefix="/units", tags=["Units"])

@router.get(
    "",
    response_model=Page[UnitOut],
    dependencies=[Depends(require_permission_scoped(*UNITS_READ))],
)
def list_units(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    department_id: UUID | None = Query(default=None),
    search: str | None = Query(default=None, description="Search in name/code"),
    sort: str = Query("name", regex="^(name|code|created_at)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
):
    stmt = select(Unit)

    if department_id:
        stmt = stmt.where(Unit.department_id == department_id)

    if search:
        s = f"%{search.lower()}%"
        stmt = stmt.where(or_(Unit.name.ilike(s), Unit.code.ilike(s)))

    sort_col = {"name": Unit.name, "code": Unit.code, "created_at": Unit.created_at}[sort]
    stmt = stmt.order_by(asc(sort_col) if order == "asc" else desc(sort_col))

    total, items = paginate(db, stmt, page, page_size)
    return Page[UnitOut](
        items=[UnitOut.model_validate(i) for i in items],
        meta=PageMeta(page=page, page_size=page_size, total=total),
    )

@router.post(
    "",
    response_model=UnitOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission_scoped(*UNITS_MANAGE))],
)
def create_unit(payload: UnitCreate, db: Session = Depends(get_db)):
    # Parent must exist
    dept = db.get(Department, payload.department_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    # Uniqueness within department scope
    dupe = db.scalar(
        select(Unit)
        .where(
            Unit.department_id == payload.department_id,
            or_(Unit.name == payload.name, Unit.code == payload.code),
        )
        .limit(1)
    )
    if dupe:
        raise HTTPException(status_code=409, detail="Unit name or code already exists in this department")

    obj = Unit(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get(
    "/{unit_id}",
    response_model=UnitOut,
    dependencies=[Depends(require_permission_scoped(*UNITS_READ))],
)
def get_unit(unit_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Unit, unit_id)
    if not obj:
        raise HTTPException(404, "Unit not found")
    return obj

@router.patch(
    "/{unit_id}",
    response_model=UnitOut,
    dependencies=[Depends(require_permission_scoped(*UNITS_MANAGE))],
)
def update_unit(unit_id: UUID, payload: UnitUpdate, db: Session = Depends(get_db)):
    obj = db.get(Unit, unit_id)
    if not obj:
        raise HTTPException(404, "Unit not found")

    # Enforce uniqueness within same department (department_id not editable by schema)
    if payload.name is not None or payload.code is not None:
        q = select(Unit).where(Unit.department_id == obj.department_id, Unit.id != unit_id)
        if payload.name is not None:
            q = q.where(Unit.name == payload.name)
        if payload.code is not None:
            q = q.where(Unit.code == payload.code)
        dupe = db.scalar(q.limit(1))
        if dupe:
            raise HTTPException(status_code=409, detail="Unit name or code already exists in this department")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.post(
    "/{unit_id}/activate",
    dependencies=[Depends(require_permission_scoped(*UNITS_MANAGE))],
)
def activate_unit(unit_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Unit, unit_id)
    if not obj:
        raise HTTPException(404, "Unit not found")
    obj.is_active = True; db.add(obj); db.commit()
    return {"status": "ok"}

@router.post(
    "/{unit_id}/deactivate",
    dependencies=[Depends(require_permission_scoped(*UNITS_MANAGE))],
)
def deactivate_unit(unit_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Unit, unit_id)
    if not obj:
        raise HTTPException(404, "Unit not found")
    obj.is_active = False; db.add(obj); db.commit()
    return {"status": "ok"}

@router.delete(
    "/{unit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission_scoped(*UNITS_MANAGE))],
)
def delete_unit(unit_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Unit, unit_id)
    if not obj:
        raise HTTPException(404, "Unit not found")
    db.delete(obj); db.commit()
