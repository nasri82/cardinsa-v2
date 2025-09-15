from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.pricing.reference.services.motor_exclusion_category_service import MotorExclusionCategoryService
from app.modules.pricing.reference.schemas.motor_exclusion_category_schema import MotorExclusionCategoryCreate, MotorExclusionCategoryUpdate

router = APIRouter()


@router.get("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def list_motor_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return MotorExclusionCategoryService(db).list(skip, limit)


@router.get("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def get_motor_category(id: str, db: Session = Depends(get_db)):
    return MotorExclusionCategoryService(db).get(id)


@router.post("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="create"))])
def create_motor_category(obj_in: MotorExclusionCategoryCreate, db: Session = Depends(get_db)):
    return MotorExclusionCategoryService(db).create(obj_in)


@router.put("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="update"))])
def update_motor_category(id: str, obj_in: MotorExclusionCategoryUpdate, db: Session = Depends(get_db)):
    return MotorExclusionCategoryService(db).update(id, obj_in)


@router.delete("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="delete"))])
def delete_motor_category(id: str, db: Session = Depends(get_db)):
    return MotorExclusionCategoryService(db).delete(id)
