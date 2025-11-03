# app/core/dependencies.py
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Header, Query, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, or_, and_, literal
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.core.database import get_db
from app.core.security import decode_token, is_token_blacklisted

from app.modules.auth.models.user_model import User
from app.modules.auth.models.role_model import Role
from app.modules.auth.models.user_role_model import UserRole
from app.modules.auth.models.permission_model import Permission
from app.modules.auth.models.role_permission_model import RolePermission

# OAuth2 password flow (token URL must match your auth route)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ---------------------
# Current user wrapper
# ---------------------
class CurrentUser:
    """Wrapper class for current authenticated user"""
    
    def __init__(self, user: User) -> None:
        self.user = user

    @property
    def id(self) -> UUID:
        """Get user ID"""
        return self.user.id

    @property
    def roles(self) -> List[Role]:
        """Get user roles"""
        return list(self.user.roles or [])

    def has_any(self, slugs: List[str]) -> bool:
        """
        Check if user has any of the specified roles.
        
        Args:
            slugs: List of role slugs to check
            
        Returns:
            True if user has any of the roles, False otherwise
        """
        want = {s.lower() for s in slugs}
        have = {getattr(r, "slug", getattr(r, "name", "")).lower() for r in (self.user.roles or [])}
        return bool(want & have)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
        
    Returns:
        CurrentUser wrapper with authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Decode JWT using your security module & settings
        payload = decode_token(token, secret=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = (payload or {}).get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid subject"
        )

    # SECURITY: Check if access token is blacklisted (logout/revocation)
    jti = (payload or {}).get("jti")
    if jti and is_token_blacklisted(jti, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive or missing user"
        )
    
    return CurrentUser(user)


async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[CurrentUser]:
    """
    Optional dependency to get current user if token provided.
    Returns None if no token or invalid token.

    Args:
        token: Optional JWT access token
        db: Database session

    Returns:
        CurrentUser if valid token, None otherwise

    SECURITY: Must use await when calling async get_current_user
    """
    if not token:
        return None

    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


# ---------------------
# Role guard (optional)
# ---------------------
def require_role(*role_slugs: str):
    """
    Dependency to require user to have specific role(s).
    
    Args:
        role_slugs: Role slugs that user must have (OR condition - any one)
        
    Returns:
        Dependency function that checks role
        
    Example:
        @router.get("/admin", dependencies=[Depends(require_role("admin", "superadmin"))])
    """
    slugs = [s.strip().lower() for s in role_slugs if s and s.strip()]

    async def _dep(current: CurrentUser = Depends(get_current_user)) -> None:
        if not slugs:
            return
        if not current.has_any(slugs):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role"
            )
    return _dep


# ---------------------------------------
# Global (non-scoped) permission guard
# - now supports wildcards: resource == "*" or action == "*"
# ---------------------------------------
async def user_has_permission(
    current: CurrentUser,
    resource: str,
    action: str,
    db: Session
) -> bool:
    """
    Check if user has permission without raising exception.
    
    Args:
        current: Current user
        resource: Resource name (e.g., "users", "policies")
        action: Action name (e.g., "read", "write", "delete")
        db: Database session
        
    Returns:
        True if user has permission, False otherwise
    """
    resource = resource.strip().lower()
    action = action.strip().lower()
    
    # Superrole bypass
    if current.has_any(["superadmin"]):
        return True

    role_ids = [r.id for r in current.roles]
    if not role_ids:
        return False

    stmt = (
        select(Permission.id)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .where(
            Role.id.in_(role_ids),
            Role.is_active.is_(True),
            Permission.is_active.is_(True),
            or_(Permission.resource == resource, Permission.resource == literal("*")),
            or_(Permission.action == action, Permission.action == literal("*")),
        )
        .limit(1)
    )
    return db.scalar(stmt) is not None


def require_permission(resource: str, action: str):
    """
    Dependency to require user to have specific permission.
    
    Args:
        resource: Resource name (e.g., "users", "policies")
        action: Action name (e.g., "read", "write", "delete")
        
    Returns:
        Dependency function that checks permission
        
    Example:
        @router.post("/users", dependencies=[Depends(require_permission("users", "create"))])
    """
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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permission"
            )

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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permission"
            )
    return _dep


# -------------------
# Scoped permission guard (Company/Dept/Unit)
# - reads scope from headers → query → path params
# - supports wildcards and superrole bypass
# ---------------------------------------
class ScopeContext:
    """Context for scoped permissions (company/department/unit level)"""
    
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
    """
    Resolve scope context from headers, query params, or path params.
    
    Priority: Headers > Query Params > Path Params
    """
    # Also allow RESTful paths like /companies/{company_id}/...
    p = (request.path_params or {})
    company_id = x_company_id or q_company_id or p.get("company_id")
    department_id = x_department_id or q_department_id or p.get("department_id")
    unit_id = x_unit_id or q_unit_id or p.get("unit_id")
    return ScopeContext(company_id, department_id, unit_id)


async def user_has_permission_scoped(
    current: CurrentUser,
    resource: str,
    action: str,
    scope: ScopeContext,
    db: Session
) -> bool:
    """
    Check if user has scoped permission without raising exception.
    
    Args:
        current: Current user
        resource: Resource name
        action: Action name
        scope: Scope context (company/department/unit)
        db: Database session
        
    Returns:
        True if user has permission, False otherwise
    """
    resource = resource.strip().lower()
    action = action.strip().lower()
    
    # Superrole bypass
    if current.has_any(["superadmin"]):
        return True
    
    # Build scope conditions
    scope_conditions = []
    
    if scope.unit_id:
        scope_conditions.append(
            and_(
                UserRole.company_id == scope.company_id,
                UserRole.department_id == scope.department_id,
                UserRole.unit_id == scope.unit_id
            )
        )
    
    if scope.department_id:
        scope_conditions.append(
            and_(
                UserRole.company_id == scope.company_id,
                UserRole.department_id == scope.department_id,
                UserRole.unit_id.is_(None)
            )
        )
    
    if scope.company_id:
        scope_conditions.append(
            and_(
                UserRole.company_id == scope.company_id,
                UserRole.department_id.is_(None),
                UserRole.unit_id.is_(None)
            )
        )
    
    # Global permission
    scope_conditions.append(
        and_(
            UserRole.company_id.is_(None),
            UserRole.department_id.is_(None),
            UserRole.unit_id.is_(None)
        )
    )
    
    # Query for permission
    stmt = (
        select(Permission.id)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(
            UserRole.user_id == current.id,
            Role.is_active.is_(True),
            Permission.is_active.is_(True),
            or_(Permission.resource == resource, Permission.resource == literal("*")),
            or_(Permission.action == action, Permission.action == literal("*")),
            or_(*scope_conditions) if scope_conditions else literal(False)
        )
        .limit(1)
    )
    
    return db.scalar(stmt) is not None


def require_permission_scoped(resource: str, action: str):
    """
    Dependency to require scoped permission (company/department/unit level).
    
    Args:
        resource: Resource name
        action: Action name
        
    Returns:
        Dependency function that checks scoped permission
        
    Example:
        @router.get(
            "/companies/{company_id}/users",
            dependencies=[Depends(require_permission_scoped("users", "read"))]
        )
    """
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
        # 1. Exact match at unit level
        # 2. Broader match at department level
        # 3. Broader match at company level
        # 4. Global permission (no scope restrictions)
        
        scope_conditions = []
        
        if scope.unit_id:
            # Unit level permission
            scope_conditions.append(
                and_(
                    UserRole.company_id == scope.company_id,
                    UserRole.department_id == scope.department_id,
                    UserRole.unit_id == scope.unit_id
                )
            )
        
        if scope.department_id:
            # Department level permission (covers all units in dept)
            scope_conditions.append(
                and_(
                    UserRole.company_id == scope.company_id,
                    UserRole.department_id == scope.department_id,
                    UserRole.unit_id.is_(None)
                )
            )
        
        if scope.company_id:
            # Company level permission (covers all depts/units in company)
            scope_conditions.append(
                and_(
                    UserRole.company_id == scope.company_id,
                    UserRole.department_id.is_(None),
                    UserRole.unit_id.is_(None)
                )
            )
        
        # Global permission (no scope, applies everywhere)
        scope_conditions.append(
            and_(
                UserRole.company_id.is_(None),
                UserRole.department_id.is_(None),
                UserRole.unit_id.is_(None)
            )
        )

        # Query for permission with scope
        stmt = (
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == current.id,
                Role.is_active.is_(True),
                Permission.is_active.is_(True),
                or_(Permission.resource == resource, Permission.resource == literal("*")),
                or_(Permission.action == action, Permission.action == literal("*")),
                or_(*scope_conditions) if scope_conditions else literal(False)
            )
            .limit(1)
        )
        
        if db.scalar(stmt) is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permission for this scope"
            )
    
    return _dep