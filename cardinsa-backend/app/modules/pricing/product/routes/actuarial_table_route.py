from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.modules.pricing.product.schemas.actuarial_table_schema import (
    ActuarialTableCreate, ActuarialTableRead, ActuarialTableUpdate
)
from app.modules.pricing.product.services.actuarial_table_service import ActuarialTableService
from app.core.dependencies import get_db, require_permission_scoped

router = APIRouter(prefix="/actuarial-tables", tags=["Actuarial Tables"])
RESOURCE = "pricing.actuarial_table"

@router.get("/", response_model=List[ActuarialTableRead])
def list_tables(
    region: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="read"))
):
    return ActuarialTableService(db).list(region=region, year=year)

@router.post("/", response_model=ActuarialTableRead)
def create_table(
    data: ActuarialTableCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="create"))
):
    return ActuarialTableService(db).create(data)

@router.put("/{id}", response_model=ActuarialTableRead)
def update_table(
    id: UUID,
    data: ActuarialTableUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="update"))
):
    service = ActuarialTableService(db)
    updated = service.update(id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Actuarial entry not found")
    return updated

@router.delete("/{id}")
def delete_table(
    id: UUID,
    db: Session = Depends(get_db),
    _: str = Depends(require_permission_scoped(RESOURCE, action="delete"))
):
    service = ActuarialTableService(db)
    success = service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Actuarial entry not found")
    return {"message": "Deleted"}
