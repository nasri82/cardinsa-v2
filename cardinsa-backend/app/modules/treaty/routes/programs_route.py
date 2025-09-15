from fastapi import APIRouter
router = APIRouter(prefix="/treaty-programs", tags=["treaty_programs"])

@router.get("/_ping")
def _ping():
    return {"ok": True, "module": "treaty_programs"}
