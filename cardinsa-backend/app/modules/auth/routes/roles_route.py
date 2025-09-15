from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_role
from app.modules.auth.schemas.role_schema import RoleCreate, RoleOut
from app.modules.auth.models.role_model import Role
from app.modules.auth.repositories import role_repository as repo

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post("", response_model=RoleOut, dependencies=[Depends(require_role("superadmin","admin"))])
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    if repo.get_by_slug(db, payload.slug) or repo.get_by_name(db, payload.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role exists")
    role = Role(name=payload.name.strip(), slug=payload.slug.strip().lower(),
                description=payload.description, is_active=payload.is_active)
    return repo.save(db, role)

@router.get("", response_model=list[RoleOut], dependencies=[Depends(require_role("superadmin","admin"))])
def list_roles(db: Session = Depends(get_db)):
    return repo.list_roles(db)
