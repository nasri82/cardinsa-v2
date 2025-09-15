from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import  require_permission_scoped
from app.modules.demographics.schemas.occupation_category_schema import (
    OccupationCategoryCreate, OccupationCategoryUpdate, OccupationCategoryOut
)
from app.modules.demographics.services import occupation_category_service

router = APIRouter()

@router.get("/", response_model=list[OccupationCategoryOut])
async def list_occupation_categories(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "view"))
):
    return await occupation_category_service.get_all_occupation_categories(db)

@router.post("/", response_model=OccupationCategoryOut)
async def create_occupation_category(
    data: OccupationCategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "create"))
):
    return await occupation_category_service.create_occupation_category(db, data)

@router.put("/{id}", response_model=OccupationCategoryOut)
async def update_occupation_category(
    id: UUID,
    data: OccupationCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "update"))
):
    db_obj = await occupation_category_service.get_occupation_category(db, id)
    return await occupation_category_service.update_occupation_category(db, db_obj, data)

@router.delete("/{id}")
async def delete_occupation_category(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "delete"))
):
    db_obj = await occupation_category_service.get_occupation_category(db, id)
    return await occupation_category_service.delete_occupation_category(db, db_obj)
