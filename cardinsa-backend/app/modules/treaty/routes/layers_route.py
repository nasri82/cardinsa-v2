from fastapi import APIRouter
router = APIRouter(prefix="/treaty-layers", tags=["treaty_layers"])

@router.get("/_ping")
def _ping():
    return {"ok": True, "module": "treaty_layers"}
