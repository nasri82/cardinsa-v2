from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.dependencies import get_db
from app.modules.benefits.schemas.benefit_category_schema import (
BenefitCategoryCreate, BenefitCategoryUpdate, BenefitCategoryOut
)
from app.modules.benefits.services.benefit_category_service import BenefitCategoryService


router = APIRouter(prefix="/benefit-categories", tags=["Benefit Categories"])


@router.get("/", response_model=list[BenefitCategoryOut])
def list_benefit_categories(db: Session = Depends(get_db)):
    return BenefitCategoryService(db).get_all()


@router.get("/{id}", response_model=BenefitCategoryOut)
def get_benefit_category(id: UUID, db: Session = Depends(get_db)):
    obj = BenefitCategoryService(db).get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Benefit category not found")
    return obj


@router.post("/", response_model=BenefitCategoryOut)
def create_benefit_category(data: BenefitCategoryCreate, db: Session = Depends(get_db)):
    return BenefitCategoryService(db).create(data)


@router.put("/{id}", response_model=BenefitCategoryOut)
def update_benefit_category(id: UUID, data: BenefitCategoryUpdate, db: Session = Depends(get_db)):
    return BenefitCategoryService(db).update(id, data)


@router.delete("/{id}")
def delete_benefit_category(id: UUID, db: Session = Depends(get_db)):
    BenefitCategoryService(db).delete(id)
    return {"message": "Deleted successfully"}