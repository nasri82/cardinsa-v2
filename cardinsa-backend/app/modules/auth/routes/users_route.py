# app/modules/auth/routes/users_route.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, asc, desc

from app.core.database import get_db
from app.core.dependencies import require_permission_scoped, resolve_scope, ScopeContext, get_current_user, user_has_permission_scoped, CurrentUser
from app.common.pagination import Page, PageMeta, paginate
from app.modules.auth.models.user_model import User
from app.modules.auth.schemas.user_schema import UserCreate, UserUpdate, UserOut, ChangePasswordIn
from app.modules.auth.services.password_service import change_password_for_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=Page[UserOut],
            dependencies=[Depends(require_permission_scoped("users","read"))])
def list_users(
    db: Session = Depends(get_db),
    scope: ScopeContext = Depends(resolve_scope),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(default=None),
    sort: str = Query("username", pattern="^(username|email|created_at)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    stmt = select(User)
    if scope.company_id:
        stmt = stmt.where(User.company_id == scope.company_id)
    if search:
        s = f"%{search.lower()}%"
        stmt = stmt.where(or_(User.username.ilike(s), User.email.ilike(s)))
    sort_col = {"username": User.username, "email": User.email, "created_at": User.created_at}[sort]
    stmt = stmt.order_by(asc(sort_col) if order == "asc" else desc(sort_col))
    total, items = paginate(db, stmt, page, page_size)
    return Page[UserOut](items=[UserOut.model_validate(i) for i in items],
                         meta=PageMeta(page=page, page_size=page_size, total=total))

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission_scoped("users","manage"))])
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    scope: ScopeContext = Depends(resolve_scope),
    current: CurrentUser = Depends(get_current_user),
):
    is_global = user_has_permission_scoped(db, current.id, "users", "manage", ScopeContext(None, None, None))
    if scope.company_id and (not is_global):
        if not getattr(payload, "company_id", None) or payload.company_id != scope.company_id:
            raise HTTPException(status_code=403, detail="Cannot create user outside current company scope")

    exists = db.scalar(
        select(User).where(or_(User.username == payload.username.lower(), User.email == payload.email.lower())).limit(1)
    )
    if exists:
        raise HTTPException(status_code=409, detail="Username or email already exists")

    obj = User(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/{user_id}", response_model=UserOut,
            dependencies=[Depends(require_permission_scoped("users","read"))])
def get_user(user_id: UUID, db: Session = Depends(get_db), scope: ScopeContext = Depends(resolve_scope)):
    obj = db.get(User, user_id)
    if not obj: raise HTTPException(404, "User not found")
    if scope.company_id and obj.company_id != scope.company_id:
        raise HTTPException(403, "Cross-company access denied")
    return obj

@router.patch("/{user_id}", response_model=UserOut,
              dependencies=[Depends(require_permission_scoped("users","update"))])
def update_user(user_id: UUID, payload: UserUpdate, db: Session = Depends(get_db), scope: ScopeContext = Depends(resolve_scope)):
    obj = db.get(User, user_id)
    if not obj: raise HTTPException(404, "User not found")
    if scope.company_id and obj.company_id != scope.company_id:
        raise HTTPException(403, "Cross-company access denied")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.post("/{user_id}/password",
             dependencies=[Depends(require_permission_scoped("users","update"))])
def change_password(user_id: UUID, body: ChangePasswordIn, db: Session = Depends(get_db), scope: ScopeContext = Depends(resolve_scope)):
    obj = db.get(User, user_id)
    if not obj: raise HTTPException(404, "User not found")
    if scope.company_id and obj.company_id != scope.company_id:
        raise HTTPException(403, "Cross-company access denied")
    change_password_for_user(db, obj, body.new_password)
    return {"status": "ok"}

@router.post("/{user_id}/activate",
             dependencies=[Depends(require_permission_scoped("users","update"))])
def activate_user(user_id: UUID, db: Session = Depends(get_db), scope: ScopeContext = Depends(resolve_scope)):
    obj = db.get(User, user_id)
    if not obj: raise HTTPException(404, "User not found")
    if scope.company_id and obj.company_id != scope.company_id:
        raise HTTPException(403, "Cross-company access denied")
    obj.is_active = True; db.add(obj); db.commit()
    return {"status": "ok"}

@router.post("/{user_id}/deactivate",
             dependencies=[Depends(require_permission_scoped("users","update"))])
def deactivate_user(user_id: UUID, db: Session = Depends(get_db), scope: ScopeContext = Depends(resolve_scope)):
    obj = db.get(User, user_id)
    if not obj: raise HTTPException(404, "User not found")
    if scope.company_id and obj.company_id != scope.company_id:
        raise HTTPException(403, "Cross-company access denied")
    obj.is_active = False; db.add(obj); db.commit()
    return {"status": "ok"}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_permission_scoped("users","manage"))])
def delete_user(user_id: UUID, db: Session = Depends(get_db), scope: ScopeContext = Depends(resolve_scope)):
    obj = db.get(User, user_id)
    if not obj: raise HTTPException(404, "User not found")
    if scope.company_id and obj.company_id != scope.company_id:
        raise HTTPException(403, "Cross-company access denied")
    db.delete(obj); db.commit()
