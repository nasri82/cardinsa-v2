from fastapi import APIRouter
router = APIRouter(prefix="/treaties", tags=["treaties"])

@router.get("/_ping")
def _ping():
    return {"ok": True, "module": "treaties"}
