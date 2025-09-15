from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.dependencies import get_db
from app.modules.benefits.schemas.coverage_option_schema import (
CoverageOptionCreate, CoverageOptionUpdate, CoverageOptionOut
)
from app.modules.benefits.services.coverage_option_service import CoverageOptionService


router = APIRouter(prefix="/coverage-options", tags=["Coverage Options"])


@router.get("/", response_model=list[CoverageOptionOut])
def list_coverage_options(db: Session = Depends(get_db)):
    return CoverageOptionService(db).get_all()


@router.get("/{id}", response_model=CoverageOptionOut)
def get_coverage_option(id: UUID, db: Session = Depends(get_db)):
    obj = CoverageOptionService(db).get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Coverage option not found")
        return obj


@router.post("/", response_model=CoverageOptionOut)
def create_coverage_option(data: CoverageOptionCreate, db: Session = Depends(get_db)):
    return CoverageOptionService(db).create(data)


@router.put("/{id}", response_model=CoverageOptionOut)
def update_coverage_option(id: UUID, data: CoverageOptionUpdate, db: Session = Depends(get_db)):
    return CoverageOptionService(db).update(id, data)


@router.delete("/{id}")
def delete_coverage_option(id: UUID, db: Session = Depends(get_db)):
    CoverageOptionService(db).delete(id)
    return {"message": "Deleted successfully"}