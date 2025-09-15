from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.dependencies import get_db
from app.modules.providers.schemas.provider_schema import *
from app.modules.providers.services import provider_service
from app.core.dependencies import require_permission_scoped

router = APIRouter(prefix="/providers", tags=["Providers"])

@router.get("/{id}", response_model=ProviderOut)
async def get_provider(id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "view"))):
    db_obj = await provider_service.get_provider(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Provider not found")
    return db_obj

@router.post("", response_model=ProviderOut)
async def create_provider(obj_in: ProviderCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "create"))):
    return await provider_service.create_provider(db, obj_in)

@router.put("/{id}", response_model=ProviderOut)
async def update_provider(id: UUID, obj_in: ProviderUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "update"))):
    db_obj = await provider_service.get_provider(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Provider not found")
    return await provider_service.update_provider(db, db_obj, obj_in)

@router.delete("/{id}")
async def delete_provider(id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "delete"))):
    db_obj = await provider_service.get_provider(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Provider not found")
    await provider_service.delete_provider(db, db_obj)
    return {"detail": "Deleted"}
