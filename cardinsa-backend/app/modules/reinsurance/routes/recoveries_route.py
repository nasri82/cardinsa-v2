from fastapi import APIRouter
router = APIRouter(prefix="/reinsurance/recoveries", tags=["reinsurance_recoveries"])

@router.get("/_ping")
def _ping():
    return {"ok": True, "module": "reinsurance_recoveries"}
