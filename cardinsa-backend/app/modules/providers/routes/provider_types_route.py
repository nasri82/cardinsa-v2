from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.dependencies import get_db
from app.modules.providers.schemas.provider_type_schema import *
from app.modules.providers.services import provider_type_service
from app.core.dependencies import require_permission_scoped

router = APIRouter(prefix="/provider-types", tags=["Provider Types"])

@router.get("/{id}", response_model=ProviderTypeOut)
async def get_provider_type(id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "view"))):
    db_obj = await provider_type_service.get_provider_type(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Provider type not found")
    return db_obj

@router.post("", response_model=ProviderTypeOut)
async def create_provider_type(obj_in: ProviderTypeCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "create"))):
    return await provider_type_service.create_provider_type(db, obj_in)

@router.put("/{id}", response_model=ProviderTypeOut)
async def update_provider_type(id: UUID, obj_in: ProviderTypeUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "update"))):
    db_obj = await provider_type_service.get_provider_type(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Provider type not found")
    return await provider_type_service.update_provider_type(db, db_obj, obj_in)

@router.delete("/{id}")
async def delete_provider_type(id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "delete"))):
    db_obj = await provider_type_service.get_provider_type(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Provider type not found")
    await provider_type_service.delete_provider_type(db, db_obj)
    return {"detail": "Deleted"}
