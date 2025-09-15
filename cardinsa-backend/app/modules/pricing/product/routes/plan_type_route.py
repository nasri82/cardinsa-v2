from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.modules.pricing.product.schemas.plan_type_schema import (
    PlanTypeCreate, PlanTypeRead, PlanTypeUpdate
)
from app.modules.pricing.product.services.plan_type_service import PlanTypeService
from app.core.dependencies import get_db, require_permission_scoped

router = APIRouter(prefix="/plan-types", tags=["Plan Types"])
RESOURCE = "pricing.plan_type"

@router.get("/", response_model=List[PlanTypeRead])
def list_plan_types(
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="read"))
):
    return PlanTypeService(db).list()

@router.post("/", response_model=PlanTypeRead)
def create_plan_type(
    data: PlanTypeCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="create"))
):
    return PlanTypeService(db).create(data)

@router.put("/{id}", response_model=PlanTypeRead)
def update_plan_type(
    id: UUID,
    data: PlanTypeUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="update"))
):
    service = PlanTypeService(db)
    updated = service.update(id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Plan type not found")
    return updated

@router.delete("/{id}")
def delete_plan_type(
    id: UUID,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="delete"))
):
    service = PlanTypeService(db)
    success = service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan type not found")
    return {"message": "Deleted"}
