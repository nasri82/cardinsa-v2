# app/modules/auth/routes/user_roles_effective_route.py
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped, resolve_scope, ScopeContext
from app.modules.auth.models.role_model import Role
from app.modules.auth.models.user_role_model import UserRole

router = APIRouter(prefix="/users", tags=["User Roles"])

@router.get("/{user_id}/roles/effective",
            dependencies=[Depends(require_permission_scoped("roles","manage"))])
def effective_roles(
    user_id: UUID,
    scope: ScopeContext = Depends(resolve_scope),
    db: Session = Depends(get_db),
):
    stmt = select(UserRole, Role).join(Role, Role.id == UserRole.role_id).where(
        UserRole.user_id == user_id, Role.is_active.is_(True)
    )
    preds = []
    if scope.unit_id:
        preds += [
            and_(UserRole.unit_id == scope.unit_id),
            and_(UserRole.department_id == scope.department_id, UserRole.unit_id.is_(None)),
            and_(UserRole.company_id == scope.company_id, UserRole.department_id.is_(None), UserRole.unit_id.is_(None)),
            and_(UserRole.company_id.is_(None), UserRole.department_id.is_(None), UserRole.unit_id.is_(None)),
        ]
    elif scope.department_id:
        preds += [
            and_(UserRole.department_id == scope.department_id, UserRole.unit_id.is_(None)),
            and_(UserRole.company_id == scope.company_id, UserRole.department_id.is_(None), UserRole.unit_id.is_(None)),
            and_(UserRole.company_id.is_(None), UserRole.department_id.is_(None), UserRole.unit_id.is_(None)),
        ]
    elif scope.company_id:
        preds += [
            and_(UserRole.company_id == scope.company_id, UserRole.department_id.is_(None), UserRole.unit_id.is_(None)),
            and_(UserRole.company_id.is_(None), UserRole.department_id.is_(None), UserRole.unit_id.is_(None)),
        ]
    else:
        preds += [and_(UserRole.company_id.is_(None), UserRole.department_id.is_(None), UserRole.unit_id.is_(None))]

    stmt = stmt.where(or_(*preds)).order_by(Role.name)
    rows = db.execute(stmt).all()
    return [
        {
            "user_role_id": ur.id,
            "role_id": r.id,
            "role_name": r.name,
            "company_id": ur.company_id,
            "department_id": ur.department_id,
            "unit_id": ur.unit_id,
        }
        for ur, r in rows
    ]
