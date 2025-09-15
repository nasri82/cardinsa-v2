from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.pricing.reference.services.cpt_code_service import CPTCodeService
from app.modules.pricing.reference.schemas.cpt_code_schema import CPTCodeCreate, CPTCodeUpdate

router = APIRouter()


@router.get("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def list_cpt_codes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CPTCodeService(db).list(skip, limit)


@router.get("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="read"))])
def get_cpt_code(id: str, db: Session = Depends(get_db)):
    return CPTCodeService(db).get(id)


@router.post("/", dependencies=[Depends(require_permission_scoped("pricing.reference", action="create"))])
def create_cpt_code(obj_in: CPTCodeCreate, db: Session = Depends(get_db)):
    return CPTCodeService(db).create(obj_in)


@router.put("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="update"))])
def update_cpt_code(id: str, obj_in: CPTCodeUpdate, db: Session = Depends(get_db)):
    return CPTCodeService(db).update(id, obj_in)


@router.delete("/{id}", dependencies=[Depends(require_permission_scoped("pricing.reference", action="delete"))])
def delete_cpt_code(id: str, db: Session = Depends(get_db)):
    return CPTCodeService(db).delete(id)
