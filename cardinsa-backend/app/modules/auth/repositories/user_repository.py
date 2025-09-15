from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.modules.auth.models.user_model import User
from app.modules.auth.models.role_model import Role

def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
    return db.get(User, user_id)

def get_by_email_or_username(db: Session, *, email: Optional[str]=None, username: Optional[str]=None) -> Optional[User]:
    if not email and not username: return None
    stmt = select(User)
    conds = []
    if email: conds.append(User.email == email.strip().lower())
    if username: conds.append(User.username == username.strip().lower())
    return db.scalar(stmt.where(or_(*conds)).limit(1))

def list_users(db: Session, *, q: Optional[str]=None, limit: int = 50, offset: int = 0) -> Sequence[User]:
    stmt = select(User)
    if q:
        qx = f"%{q.lower()}%"
        stmt = stmt.where(or_(User.email.ilike(qx), User.username.ilike(qx), User.full_name.ilike(qx)))
    stmt = stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt))

def save(db: Session, user: User) -> User:
    db.add(user); db.commit(); db.refresh(user); return user
