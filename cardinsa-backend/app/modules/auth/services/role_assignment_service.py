from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.modules.auth.models.user_model import User
from app.modules.auth.models.role_model import Role
from app.modules.org.models.company_model import Company
from app.modules.org.models.department_model import Department
from app.modules.org.models.unit_model import Unit

from app.modules.auth.repositories import user_role_repository as repo

def _validate_user_and_role(db: Session, user_id: UUID, role_id: UUID | None, role_name: str | None) -> tuple[User, Role]:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = None
    if role_id:
        role = db.get(Role, role_id)
    elif role_name:
        role = db.query(Role).filter(Role.name.ilike(role_name)).limit(1).one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if not getattr(role, "is_active", True):
        raise HTTPException(status_code=400, detail="Role is inactive")
    return user, role

def _validate_scope(db: Session, company_id: UUID | None, department_id: UUID | None, unit_id: UUID | None):
    """
    Enforce parent consistency:
      - department must belong to company (if both provided)
      - unit must belong to department (and implicitly to company if given)
    """
    company = department = unit = None

    if company_id:
        company = db.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

    if department_id:
        department = db.get(Department, department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        if company_id and department.company_id != company_id:
            raise HTTPException(status_code=400, detail="Department does not belong to company")

    if unit_id:
        unit = db.get(Unit, unit_id)
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        if department_id and unit.department_id != department_id:
            raise HTTPException(status_code=400, detail="Unit does not belong to department")

    return company, department, unit

def assign_role_scoped(
    db: Session, *, user_id: UUID, role_id: UUID | None, role_name: str | None,
    company_id: UUID | None, department_id: UUID | None, unit_id: UUID | None
):
    _validate_scope(db, company_id, department_id, unit_id)
    _, role = _validate_user_and_role(db, user_id, role_id, role_name)
    return repo.assign(db, user_id, role.id, company_id=company_id, department_id=department_id, unit_id=unit_id)

def revoke_role_scoped(
    db: Session, *, user_id: UUID, role_id: UUID | None, role_name: str | None,
    company_id: UUID | None, department_id: UUID | None, unit_id: UUID | None
) -> bool:
    _validate_scope(db, company_id, department_id, unit_id)
    _, role = _validate_user_and_role(db, user_id, role_id, role_name)
    return repo.revoke(db, user_id, role.id, company_id=company_id, department_id=department_id, unit_id=unit_id)
