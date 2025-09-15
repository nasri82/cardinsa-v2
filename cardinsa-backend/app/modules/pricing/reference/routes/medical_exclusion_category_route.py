from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.pricing.reference.services.medical_exclusion_category_service import MedicalExclusionCategoryService
from app.modules.pricing.reference.schemas.medical_exclusion_category_schema import MedicalExclusionCategoryCreate, MedicalExclusionCategoryUpdate

router = APIRouter()


@router.get("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def list_medical_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return MedicalExclusionCategoryService(db).list(skip, limit)


@router.get("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def get_medical_category(id: str, db: Session = Depends(get_db)):
    return MedicalExclusionCategoryService(db).get(id)


@router.post("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="create"))])
def create_medical_category(obj_in: MedicalExclusionCategoryCreate, db: Session = Depends(get_db)):
    return MedicalExclusionCategoryService(db).create(obj_in)


@router.put("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="update"))])
def update_medical_category(id: str, obj_in: MedicalExclusionCategoryUpdate, db: Session = Depends(get_db)):
    return MedicalExclusionCategoryService(db).update(id, obj_in)


@router.delete("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="delete"))])
def delete_medical_category(id: str, db: Session = Depends(get_db)):
    return MedicalExclusionCategoryService(db).delete(id)
