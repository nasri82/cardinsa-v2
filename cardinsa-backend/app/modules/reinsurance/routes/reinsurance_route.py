from fastapi import APIRouter
router = APIRouter(prefix="/reinsurance", tags=["reinsurance"])

@router.get("/_ping")
def _ping():
    return {"ok": True, "module": "reinsurance"}
