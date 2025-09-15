from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.pricing.reference.services.motor_exclusion_code_service import MotorExclusionCodeService
from app.modules.pricing.reference.schemas.motor_exclusion_code_schema import MotorExclusionCodeCreate, MotorExclusionCodeUpdate

router = APIRouter()


@router.get("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def list_motor_codes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return MotorExclusionCodeService(db).list(skip, limit)


@router.get("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def get_motor_code(id: str, db: Session = Depends(get_db)):
    return MotorExclusionCodeService(db).get(id)


@router.post("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="create"))])
def create_motor_code(obj_in: MotorExclusionCodeCreate, db: Session = Depends(get_db)):
    return MotorExclusionCodeService(db).create(obj_in)


@router.put("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="update"))])
def update_motor_code(id: str, obj_in: MotorExclusionCodeUpdate, db: Session = Depends(get_db)):
    return MotorExclusionCodeService(db).update(id, obj_in)


@router.delete("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="delete"))])
def delete_motor_code(id: str, db: Session = Depends(get_db)):
    return MotorExclusionCodeService(db).delete(id)
