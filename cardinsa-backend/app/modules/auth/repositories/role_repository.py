# repository for Role (implement CRUD later)
from typing import Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.modules.auth.models.role_model import Role

def get_by_slug(db: Session, slug: str) -> Optional[Role]:
    return db.scalar(select(Role).where(Role.slug == slug.strip().lower()).limit(1))

def get_by_name(db: Session, name: str) -> Optional[Role]:
    return db.scalar(select(Role).where(Role.name == name.strip()).limit(1))

def list_roles(db: Session, *, limit: int = 100, offset: int = 0) -> Sequence[Role]:
    return list(db.scalars(select(Role).order_by(Role.name).limit(limit).offset(offset)))

def save(db: Session, role: Role) -> Role:
    db.add(role); db.commit(); db.refresh(role); return role
