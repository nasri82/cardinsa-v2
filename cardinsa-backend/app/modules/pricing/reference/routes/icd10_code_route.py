from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.pricing.reference.services.icd10_code_service import ICD10CodeService
from app.modules.pricing.reference.schemas.icd10_code_schema import ICD10CodeCreate, ICD10CodeUpdate

router = APIRouter()


@router.get("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def list_icd10_codes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ICD10CodeService(db).list(skip, limit)


@router.get("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def get_icd10_code(id: str, db: Session = Depends(get_db)):
    return ICD10CodeService(db).get(id)


@router.post("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="create"))])
def create_icd10_code(obj_in: ICD10CodeCreate, db: Session = Depends(get_db)):
    return ICD10CodeService(db).create(obj_in)


@router.put("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="update"))])
def update_icd10_code(id: str, obj_in: ICD10CodeUpdate, db: Session = Depends(get_db)):
    return ICD10CodeService(db).update(id, obj_in)


@router.delete("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="delete"))])
def delete_icd10_code(id: str, db: Session = Depends(get_db)):
    return ICD10CodeService(db).delete(id)
