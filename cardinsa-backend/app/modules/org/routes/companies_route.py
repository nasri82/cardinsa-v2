# app/modules/org/routes/companies_route.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, asc, desc

from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.common.pagination import Page, PageMeta, paginate
from app.modules.org.permissions import COMPANIES_READ, COMPANIES_MANAGE
from app.modules.org.models.company_model import Company
from app.modules.org.schemas.company_schema import CompanyCreate, CompanyUpdate, CompanyOut

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("", response_model=Page[CompanyOut],
            dependencies=[Depends(require_permission_scoped(*COMPANIES_READ))])
def list_companies(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(default=None, description="Search in name/code"),
    sort: str = Query("name", pattern="^(name|code|created_at)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    stmt = select(Company)
    if search:
        s = f"%{search.lower()}%"
        stmt = stmt.where(or_(Company.name.ilike(s), Company.code.ilike(s)))
    sort_col = {"name": Company.name, "code": Company.code, "created_at": Company.created_at}[sort]
    stmt = stmt.order_by(asc(sort_col) if order == "asc" else desc(sort_col))

    total, items = paginate(db, stmt, page, page_size)
    return Page[CompanyOut](items=[CompanyOut.model_validate(i) for i in items],
                            meta=PageMeta(page=page, page_size=page_size, total=total))

@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission_scoped(*COMPANIES_MANAGE))])
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Company).where((Company.name == payload.name) | (Company.code == payload.code)).limit(1))
    if exists:
        raise HTTPException(status_code=409, detail="Company name or code already exists")
    obj = Company(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/{company_id}", response_model=CompanyOut,
            dependencies=[Depends(require_permission_scoped(*COMPANIES_READ))])
def get_company(company_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Company, company_id)
    if not obj: raise HTTPException(404, "Company not found")
    return obj

@router.patch("/{company_id}", response_model=CompanyOut,
              dependencies=[Depends(require_permission_scoped(*COMPANIES_MANAGE))])
def update_company(company_id: UUID, payload: CompanyUpdate, db: Session = Depends(get_db)):
    obj = db.get(Company, company_id)
    if not obj: raise HTTPException(404, "Company not found")
    if payload.name or payload.code:
        q = select(Company).where(Company.id != company_id)
        if payload.name: q = q.where(Company.name == payload.name)
        if payload.code: q = q.where(Company.code == payload.code)
        dupe = db.scalar(q.limit(1))
        if dupe: raise HTTPException(409, "Company name or code already exists")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.post("/{company_id}/activate",
             dependencies=[Depends(require_permission_scoped(*COMPANIES_MANAGE))])
def activate_company(company_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Company, company_id)
    if not obj: raise HTTPException(404, "Company not found")
    obj.is_active = True; db.add(obj); db.commit()
    return {"status": "ok"}

@router.post("/{company_id}/deactivate",
             dependencies=[Depends(require_permission_scoped(*COMPANIES_MANAGE))])
def deactivate_company(company_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Company, company_id)
    if not obj: raise HTTPException(404, "Company not found")
    obj.is_active = False; db.add(obj); db.commit()
    return {"status": "ok"}

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_permission_scoped(*COMPANIES_MANAGE))])
def delete_company(company_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Company, company_id)
    if not obj: raise HTTPException(404, "Company not found")
    db.delete(obj); db.commit()
