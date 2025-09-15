from fastapi import APIRouter
router = APIRouter(prefix="/accounting/entries", tags=["gl_entries"])

@router.get("/_ping")
def _ping():
    return {"ok": True, "module": "gl_entries"}
