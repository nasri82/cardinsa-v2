# app/modules/org/routes/org_tree_route.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.org.permissions import COMPANIES_READ
from app.modules.org.models.company_model import Company
from app.modules.org.models.department_model import Department

router = APIRouter(prefix="/org", tags=["Org Tree"])

@router.get("/tree", dependencies=[Depends(require_permission_scoped(*COMPANIES_READ))])
def get_org_tree(db: Session = Depends(get_db)):
    stmt = (
        select(Company)
        .options(
            selectinload(Company.departments).selectinload(Department.units)
        )
        .order_by(Company.name)
    )
    companies = list(db.scalars(stmt))

    def to_dict(c: Company):
        return {
            "id": c.id, "name": c.name, "code": c.code, "is_active": c.is_active,
            "departments": [
                {
                    "id": d.id, "name": d.name, "code": d.code, "is_active": d.is_active,
                    "units": [
                        {"id": u.id, "name": u.name, "code": u.code, "is_active": u.is_active}
                        for u in (d.units or [])
                    ],
                }
                for d in (c.departments or [])
            ],
        }

    return [to_dict(c) for c in companies]
