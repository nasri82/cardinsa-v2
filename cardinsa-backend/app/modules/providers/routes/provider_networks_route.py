from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.dependencies import get_db
from app.modules.providers.schemas.provider_network_schema import *
from app.modules.providers.services import provider_network_service
from app.core.dependencies import require_permission_scoped

router = APIRouter(prefix="/provider-networks", tags=["Provider Networks"])

@router.get("/{id}", response_model=ProviderNetworkOut)
async def get_network(id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "view"))):
    db_obj = await provider_network_service.get_provider_network(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Network not found")
    return db_obj

@router.post("", response_model=ProviderNetworkOut)
async def create_network(obj_in: ProviderNetworkCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "create"))):
    return await provider_network_service.create_provider_network(db, obj_in)

@router.put("/{id}", response_model=ProviderNetworkOut)
async def update_network(id: UUID, obj_in: ProviderNetworkUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "update"))):
    db_obj = await provider_network_service.get_provider_network(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Network not found")
    return await provider_network_service.update_provider_network(db, db_obj, obj_in)

@router.delete("/{id}")
async def delete_network(id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "delete"))):
    db_obj = await provider_network_service.get_provider_network(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Network not found")
    await provider_network_service.delete_provider_network(db, db_obj)
    return {"detail": "Deleted"}
