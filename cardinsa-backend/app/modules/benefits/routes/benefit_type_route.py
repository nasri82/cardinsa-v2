from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.dependencies import get_db
from app.modules.benefits.schemas.benefit_type_schema import (
BenefitTypeCreate, BenefitTypeUpdate, BenefitTypeOut
)
from app.modules.benefits.services.benefit_type_service import BenefitTypeService


router = APIRouter(prefix="/benefit-types", tags=["Benefit Types"])


@router.get("/", response_model=list[BenefitTypeOut])
def list_benefit_types(db: Session = Depends(get_db)):
    return BenefitTypeService(db).get_all()


@router.get("/{id}", response_model=BenefitTypeOut)
def get_benefit_type(id: UUID, db: Session = Depends(get_db)):
    obj = BenefitTypeService(db).get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Benefit type not found")
    return obj


@router.post("/", response_model=BenefitTypeOut)
def create_benefit_type(data: BenefitTypeCreate, db: Session = Depends(get_db)):
    return BenefitTypeService(db).create(data)


@router.put("/{id}", response_model=BenefitTypeOut)
def update_benefit_type(id: UUID, data: BenefitTypeUpdate, db: Session = Depends(get_db)):
    return BenefitTypeService(db).update(id, data)


@router.delete("/{id}")
def delete_benefit_type(id: UUID, db: Session = Depends(get_db)):
    BenefitTypeService(db).delete(id)
    return {"message": "Deleted successfully"}