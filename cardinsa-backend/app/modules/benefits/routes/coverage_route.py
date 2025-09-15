

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.dependencies import get_db
from app.modules.benefits.schemas.coverage_schema import (
CoverageCreate, CoverageUpdate, CoverageOut
)
from app.modules.benefits.services.coverage_service import CoverageService


router = APIRouter(prefix="/coverages", tags=["Coverages"])


@router.get("/", response_model=list[CoverageOut])
def list_coverages(db: Session = Depends(get_db)):
    return CoverageService(db).get_all()


@router.get("/{id}", response_model=CoverageOut)


def get_coverage(id: UUID, db: Session = Depends(get_db)):
    obj = CoverageService(db).get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Coverage not found")
    return obj


@router.post("/", response_model=CoverageOut)
def create_coverage(data: CoverageCreate, db: Session = Depends(get_db)):
    return CoverageService(db).create(data)


@router.put("/{id}", response_model=CoverageOut)
def update_coverage(id: UUID, data: CoverageUpdate, db: Session = Depends(get_db)):
    return CoverageService(db).update(id, data)


@router.delete("/{id}")
def delete_coverage(id: UUID, db: Session = Depends(get_db)):
    CoverageService(db).delete(id)
    return {"message": "Deleted successfully"}