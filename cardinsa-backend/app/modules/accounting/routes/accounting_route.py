from fastapi import APIRouter
router = APIRouter(prefix="/accounting", tags=["accounting"])

@router.get("/_ping")
def _ping():
    return {"ok": True, "module": "accounting"}
