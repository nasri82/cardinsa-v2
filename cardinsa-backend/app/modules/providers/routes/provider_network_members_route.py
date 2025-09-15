from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.dependencies import get_db
from app.modules.providers.schemas.provider_network_member_schema import *
from app.modules.providers.services import provider_network_member_service
from app.core.dependencies import require_permission_scoped

router = APIRouter(prefix="/provider-network-members", tags=["Provider Network Members"])

@router.get("/{id}", response_model=ProviderNetworkMemberOut)
async def get_member(id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "view"))):
    db_obj = await provider_network_member_service.get_network_member(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_obj

@router.post("", response_model=ProviderNetworkMemberOut)
async def create_member(obj_in: ProviderNetworkMemberCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "create"))):
    return await provider_network_member_service.create_network_member(db, obj_in)

@router.delete("/{id}")
async def delete_member(id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "delete"))):
    db_obj = await provider_network_member_service.get_network_member(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Member not found")
    await provider_network_member_service.delete_network_member(db, db_obj)
    return {"detail": "Deleted"}
