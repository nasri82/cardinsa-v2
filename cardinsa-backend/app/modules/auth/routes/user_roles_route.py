# app/modules/auth/routes/user_roles_route.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission_scoped, get_current_user, resolve_scope, ScopeContext, CurrentUser
from app.modules.auth.schemas.user_role_schema import AssignRoleIn, RevokeRoleIn, UserRoleOut
from app.modules.auth.repositories import user_role_repository as repo
from app.modules.auth.services.role_assignment_service import assign_role_scoped, revoke_role_scoped

router = APIRouter(prefix="/users", tags=["User Roles"])

@router.get("/{user_id}/roles", response_model=list[UserRoleOut],
            dependencies=[Depends(require_permission_scoped("roles","manage"))])
def list_user_roles(
    user_id: UUID,
    company_id: UUID | None = Query(default=None),
    department_id: UUID | None = Query(default=None),
    unit_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return repo.list_for_user(db, user_id, company_id=company_id, department_id=department_id, unit_id=unit_id)

@router.post("/{user_id}/roles/assign", response_model=UserRoleOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission_scoped("roles","manage"))])
def assign_role(
    user_id: UUID,
    body: AssignRoleIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
    scope: ScopeContext = Depends(resolve_scope),
):
    obj = assign_role_scoped(
        db,
        actor_id=current.id,
        user_id=user_id,
        role_id=body.role_id,
        role_name=body.role_name,
        company_id=body.company_id if body.company_id is not None else scope.company_id,
        department_id=body.department_id if body.department_id is not None else scope.department_id,
        unit_id=body.unit_id if body.unit_id is not None else scope.unit_id,
    )
    return obj

@router.post("/{user_id}/roles/revoke", status_code=status.HTTP_200_OK,
             dependencies=[Depends(require_permission_scoped("roles","manage"))])
def revoke_role(
    user_id: UUID,
    body: RevokeRoleIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
    scope: ScopeContext = Depends(resolve_scope),
):
    ok = revoke_role_scoped(
        db,
        actor_id=current.id,
        user_id=user_id,
        role_id=body.role_id,
        role_name=body.role_name,
        company_id=body.company_id if body.company_id is not None else scope.company_id,
        department_id=body.department_id if body.department_id is not None else scope.department_id,
        unit_id=body.unit_id if body.unit_id is not None else scope.unit_id,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"status": "ok"}
