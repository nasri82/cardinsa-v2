from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import require_permission_scoped
from app.modules.demographics.schemas.premium_age_bracket_schema import (
    PremiumAgeBracketCreate, PremiumAgeBracketUpdate, PremiumAgeBracketOut
)
from app.modules.demographics.services import premium_age_bracket_service

router = APIRouter()

@router.get("/", response_model=list[PremiumAgeBracketOut])
async def list_premium_age_brackets(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "view"))
):
    return await premium_age_bracket_service.get_all_premium_age_brackets(db)

@router.post("/", response_model=PremiumAgeBracketOut)
async def create_premium_age_bracket(
    data: PremiumAgeBracketCreate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "create"))
):
    return await premium_age_bracket_service.create_premium_age_bracket(db, data)

@router.put("/{id}", response_model=PremiumAgeBracketOut)
async def update_premium_age_bracket(
    id: UUID,
    data: PremiumAgeBracketUpdate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "update"))
):
    db_obj = await premium_age_bracket_service.get_premium_age_bracket(db, id)
    return await premium_age_bracket_service.update_premium_age_bracket(db, db_obj, data)

@router.delete("/{id}")
async def delete_premium_age_bracket(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("demographics", "delete"))
):
    db_obj = await premium_age_bracket_service.get_premium_age_bracket(db, id)
    return await premium_age_bracket_service.delete_premium_age_bracket(db, db_obj)
