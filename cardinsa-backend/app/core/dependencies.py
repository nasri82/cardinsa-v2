# app/core/dependencies.py
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Header, Query, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, or_, and_, literal
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.core.database import get_db
from app.core.security import decode_token

from app.modules.auth.models.user_model import User
from app.modules.auth.models.role_model import Role
from app.modules.auth.models.user_role_model import UserRole
from app.modules.auth.models.permission_model import Permission
from app.modules.auth.models.role_permission_model import RolePermission

# OAuth2 password flow (token URL must match your auth route)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------------------
# Current user wrapper
# ---------------------
class CurrentUser:
    def __init__(self, user: User) -> None:
        self.user = user

    @property
    def id(self) -> UUID:
        return self.user.id

    @property
    def roles(self) -> List[Role]:
        return list(self.user.roles or [])

    def has_any(self, slugs: List[str]) -> bool:
        want = {s.lower() for s in slugs}
        have = {getattr(r, "slug", getattr(r, "name", "")).lower() for r in (self.user.roles or [])}
        return bool(want & have)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    # Decode JWT using your security module & settings
    try:
        payload = decode_token(token, secret=settings.JWT_SECRET)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    sub = (payload or {}).get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid subject")

    # Prefer by UUID; fallback to username/email
    user: Optional[User] = None
    try:
        user = db.get(User, UUID(str(sub)))
    except Exception:
        user = db.scalar(
            select(User).where(
                or_(User.username == str(sub).lower(), User.email == str(sub).lower())
            ).limit(1)
        )

    if not user or not getattr(user, "is_active", False):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return CurrentUser(user)

# ---------------------
# Role guard (optional)
# ---------------------
def require_role(*role_slugs: str):
    slugs = [s.strip().lower() for s in role_slugs if s and s.strip()]

    async def _dep(current: CurrentUser = Depends(get_current_user)) -> None:
        if not slugs:
            return
        if not current.has_any(slugs):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return _dep

# ---------------------------------------
# Global (non-scoped) permission guard
# - now supports wildcards: resource == "*" or action == "*"
# ---------------------------------------
def require_permission(resource: str, action: str):
    resource = resource.strip().lower()
    action = action.strip().lower()

    async def _dep(
        current: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> None:
        # Superrole bypass (e.g., superadmin)
        if current.has_any(["superadmin"]):
            return

        role_ids = [r.id for r in current.roles]
        if not role_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permission")

        stmt = (
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .where(
                Role.id.in_(role_ids),
                Role.is_active.is_(True),
                Permission.is_active.is_(True),
                # wildcard-friendly checks
                or_(Permission.resource == resource, Permission.resource == literal("*")),
                or_(Permission.action == action, Permission.action == literal("*")),
            )
            .limit(1)
        )
        if db.scalar(stmt) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permission")
    return _dep

# ---------------------------------------
# Scoped permission guard (Company/Dept/Unit)
# - reads scope from headers -> query -> path params
# - supports wildcards and superrole bypass
# ---------------------------------------
class ScopeContext:
    def __init__(
        self,
        company_id: Optional[UUID],
        department_id: Optional[UUID],
        unit_id: Optional[UUID],
    ) -> None:
        self.company_id = company_id
        self.department_id = department_id
        self.unit_id = unit_id

async def resolve_scope(
    request: Request,
    # Preferred: frontend headers
    x_company_id: Optional[UUID] = Header(default=None, alias="X-Company-Id"),
    x_department_id: Optional[UUID] = Header(default=None, alias="X-Department-Id"),
    x_unit_id: Optional[UUID] = Header(default=None, alias="X-Unit-Id"),
    # Fallback: query params (Swagger/dev)
    q_company_id: Optional[UUID] = Query(default=None, alias="company_id"),
    q_department_id: Optional[UUID] = Query(default=None, alias="department_id"),
    q_unit_id: Optional[UUID] = Query(default=None, alias="unit_id"),
) -> ScopeContext:
    # Also allow RESTful paths like /companies/{company_id}/...
    p = (request.path_params or {})
    company_id = x_company_id or q_company_id or p.get("company_id")
    department_id = x_department_id or q_department_id or p.get("department_id")
    unit_id = x_unit_id or q_unit_id or p.get("unit_id")
    return ScopeContext(company_id, department_id, unit_id)

def require_permission_scoped(resource: str, action: str):
    resource = resource.strip().lower()
    action = action.strip().lower()

    async def _dep(
        scope: ScopeContext = Depends(resolve_scope),
        current: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> None:
        # 🔹 superrole bypass (platform owners)
        if current.has_any(["superadmin"]):
            return

        # Roles for this user
        role_ids_subq = (
            select(Role.id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == current.id, Role.is_active.is_(True))
        )

        # Build scope predicates: exact → broader → global
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
            preds += [
                and_(UserRole.company_id.is_(None), UserRole.department_id.is_(None), UserRole.unit_id.is_(None))
            ]

        role_ids_subq = role_ids_subq.where(or_(*preds))

        # Permission check with wildcard support
        has_perm = db.scalar(
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(
                Permission.is_active.is_(True),
                # wildcard-friendly checks
                or_(Permission.resource == resource, Permission.resource == literal("*")),
                or_(Permission.action == action,   Permission.action == literal("*")),
                RolePermission.role_id.in_(role_ids_subq),
            )
            .limit(1)
        )
        if has_perm is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permission for scope")
    return _dep

# --- Programmatic check for services (used by role assignment & users CRUD) ---
def user_has_permission_scoped(
    db: Session,
    user_id: UUID,
    resource: str,
    action: str,
    scope: ScopeContext,
) -> bool:
    resource = resource.strip().lower()
    action = action.strip().lower()

    role_ids_subq = (
        select(Role.id)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id, Role.is_active.is_(True))
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
        preds += [
            and_(UserRole.company_id.is_(None), UserRole.department_id.is_(None), UserRole.unit_id.is_(None))
        ]

    role_ids_subq = role_ids_subq.where(or_(*preds))

    return db.scalar(
        select(Permission.id)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(
            Permission.is_active.is_(True),
            or_(Permission.resource == resource, Permission.resource == literal("*")),
            or_(Permission.action == action,   Permission.action == literal("*")),
            RolePermission.role_id.in_(role_ids_subq),
        )
        .limit(1)
    ) is not None
