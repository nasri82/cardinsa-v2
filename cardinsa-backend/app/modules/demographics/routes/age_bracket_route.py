from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.demographics.schemas.age_bracket_schema import (
    AgeBracketCreate, AgeBracketUpdate, AgeBracketOut
)
from app.modules.demographics.services import age_bracket_service

router = APIRouter()

@router.get("/", response_model=list[AgeBracketOut])
async def list_age_brackets(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "view"))
):
    return await age_bracket_service.get_all_age_brackets(db)

@router.post("/", response_model=AgeBracketOut)
async def create_age_bracket(
    data: AgeBracketCreate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "create"))
):
    return await age_bracket_service.create_age_bracket(db, data)

@router.put("/{id}", response_model=AgeBracketOut)
async def update_age_bracket(
    id: UUID,
    data: AgeBracketUpdate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "update"))
):
    db_obj = await age_bracket_service.get_age_bracket(db, id)
    return await age_bracket_service.update_age_bracket(db, db_obj, data)

@router.delete("/{id}")
async def delete_age_bracket(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "delete"))
):
    db_obj = await age_bracket_service.get_age_bracket(db, id)
    return await age_bracket_service.delete_age_bracket(db, db_obj)
