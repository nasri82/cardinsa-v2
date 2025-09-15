from fastapi import APIRouter
router = APIRouter(prefix="/accounting/journals", tags=["gl_journals"])

@router.get("/_ping")
def _ping():
    return {"ok": True, "module": "gl_journals"}
