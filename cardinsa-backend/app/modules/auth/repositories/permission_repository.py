from typing import Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.modules.auth.models.permission_model import Permission

def get_by_code(db: Session, code: str) -> Optional[Permission]:
    return db.scalar(select(Permission).where(Permission.code == code).limit(1))

def list_all(db: Session) -> Sequence[Permission]:
    return list(db.scalars(select(Permission).where(Permission.is_active.is_(True)).order_by(Permission.code)))

def save(db: Session, perm: Permission) -> Permission:
    db.add(perm); db.commit(); db.refresh(perm); return perm
