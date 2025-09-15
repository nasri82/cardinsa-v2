from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.settings import settings
from app.core.security import create_access_token
from app.modules.auth.repositories.user_repository import get_by_email_or_username
from app.modules.auth.services.password_service import verify as verify_password
from app.modules.auth.schemas.auth_schema import TokenOut

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenOut)
def login(request: Request, username: str, password: str, db: Session = Depends(get_db)):
    user = get_by_email_or_username(db, email=username, username=username)
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(sub=user.id, secret=settings.JWT_SECRET, minutes=settings.JWT_EXPIRE_MINUTES)
    return {"access_token": token}
