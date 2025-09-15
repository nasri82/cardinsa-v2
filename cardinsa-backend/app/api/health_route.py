from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db

router = APIRouter(prefix="/health")

@router.get("/liveness")
def liveness():
    return {"status": "ok"}

@router.get("/readiness")
def readiness(db: Session = Depends(get_db)):
    # Touch the DB session to ensure pool connectivity (lightweight no-op)
    _ = db.connection().closed  # triggers lazy connection without query
    return {"status": "ready"}
