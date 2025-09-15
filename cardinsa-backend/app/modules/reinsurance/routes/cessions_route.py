from fastapi import APIRouter
router = APIRouter(prefix="/reinsurance/cessions", tags=["reinsurance_cessions"])

@router.get("/_ping")
def _ping():
    return {"ok": True, "module": "reinsurance_cessions"}
