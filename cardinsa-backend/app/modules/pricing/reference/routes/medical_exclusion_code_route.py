from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.pricing.reference.services.medical_exclusion_code_service import MedicalExclusionCodeService
from app.modules.pricing.reference.schemas.medical_exclusion_code_schema import MedicalExclusionCodeCreate, MedicalExclusionCodeUpdate

router = APIRouter()


@router.get("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def list_medical_codes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return MedicalExclusionCodeService(db).list(skip, limit)


@router.get("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def get_medical_code(id: str, db: Session = Depends(get_db)):
    return MedicalExclusionCodeService(db).get(id)


@router.post("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="create"))])
def create_medical_code(obj_in: MedicalExclusionCodeCreate, db: Session = Depends(get_db)):
    return MedicalExclusionCodeService(db).create(obj_in)


@router.put("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="update"))])
def update_medical_code(id: str, obj_in: MedicalExclusionCodeUpdate, db: Session = Depends(get_db)):
    return MedicalExclusionCodeService(db).update(id, obj_in)


@router.delete("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="delete"))])
def delete_medical_code(id: str, db: Session = Depends(get_db)):
    return MedicalExclusionCodeService(db).delete(id)
