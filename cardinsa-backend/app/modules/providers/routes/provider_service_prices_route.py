from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.dependencies import get_db
from app.modules.providers.schemas.provider_service_price_schema import *
from app.modules.providers.services import provider_service_price_service
from app.core.dependencies import require_permission_scoped

router = APIRouter(prefix="/provider-service-prices", tags=["Provider Service Prices"])

@router.get("/{id}", response_model=ProviderServicePriceOut)
async def get_price(id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "view"))):
    db_obj = await provider_service_price_service.get_service_price(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Price not found")
    return db_obj

@router.post("", response_model=ProviderServicePriceOut)
async def create_price(obj_in: ProviderServicePriceCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "create"))):
    return await provider_service_price_service.create_service_price(db, obj_in)

@router.put("/{id}", response_model=ProviderServicePriceOut)
async def update_price(id: UUID, obj_in: ProviderServicePriceUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "update"))):
    db_obj = await provider_service_price_service.get_service_price(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Price not found")
    return await provider_service_price_service.update_service_price(db, db_obj, obj_in)

@router.delete("/{id}")
async def delete_price(id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission_scoped("provider", "delete"))):
    db_obj = await provider_service_price_service.get_service_price(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Price not found")
    await provider_service_price_service.delete_service_price(db, db_obj)
    return {"detail": "Deleted"}
