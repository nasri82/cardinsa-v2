from typing import Iterable, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.modules.auth.models.user_role_model import UserRole

def _scope_clause(company_id: UUID | None, department_id: UUID | None, unit_id: UUID | None):
    clauses = []
    if company_id is None:
        clauses.append(UserRole.company_id.is_(None))
    else:
        clauses.append(UserRole.company_id == company_id)
    if department_id is None:
        clauses.append(UserRole.department_id.is_(None))
    else:
        clauses.append(UserRole.department_id == department_id)
    if unit_id is None:
        clauses.append(UserRole.unit_id.is_(None))
    else:
        clauses.append(UserRole.unit_id == unit_id)
    return and_(*clauses)

def list_for_user(
    db: Session, user_id: UUID, *, company_id: UUID | None = None,
    department_id: UUID | None = None, unit_id: UUID | None = None
) -> list[UserRole]:
    stmt = select(UserRole).where(UserRole.user_id == user_id)
    if any([company_id, department_id, unit_id]):
        stmt = stmt.where(_scope_clause(company_id, department_id, unit_id))
    return list(db.scalars(stmt.order_by(UserRole.created_at)))

def get_one(
    db: Session, user_id: UUID, role_id: UUID, *,
    company_id: UUID | None, department_id: UUID | None, unit_id: UUID | None
) -> Optional[UserRole]:
    stmt = (
        select(UserRole)
        .where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
            _scope_clause(company_id, department_id, unit_id),
        )
        .limit(1)
    )
    return db.scalar(stmt)

def assign(
    db: Session, user_id: UUID, role_id: UUID, *,
    company_id: UUID | None, department_id: UUID | None, unit_id: UUID | None
) -> UserRole:
    existing = get_one(db, user_id, role_id, company_id=company_id, department_id=department_id, unit_id=unit_id)
    if existing:
        return existing
    obj = UserRole(
        user_id=user_id, role_id=role_id,
        company_id=company_id, department_id=department_id, unit_id=unit_id
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def revoke(
    db: Session, user_id: UUID, role_id: UUID, *,
    company_id: UUID | None, department_id: UUID | None, unit_id: UUID | None
) -> bool:
    obj = get_one(db, user_id, role_id, company_id=company_id, department_id=department_id, unit_id=unit_id)
    if not obj:
        return False
    db.delete(obj); db.commit()
    return True
