from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.mailer import get_mailer
from app.modules.auth.schemas.password_reset_schema import (
    ForgotPasswordIn, ResetPasswordIn, ResetPasswordOut
)
from app.modules.auth.services.password_reset_service import (
    request_reset, reset_password
)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/forgot-password", response_model=ResetPasswordOut)
def forgot_password(body: ForgotPasswordIn, request: Request, db: Session = Depends(get_db)):
    if not body.email and not body.username:
        # stay generic; don't leak details
        return {"status": "ok"}
    request_reset(
        db,
        email=(body.email.lower() if body.email else None),
        username=(body.username.lower() if body.username else None),
        client_ip=(request.client.host if request.client else None),
        user_agent=request.headers.get("user-agent"),
        mailer=get_mailer(),
    )
    # Always return ok (no user enumeration)
    return {"status": "ok"}

@router.post("/reset-password", response_model=ResetPasswordOut)
def reset_password_route(body: ResetPasswordIn, db: Session = Depends(get_db)):
    reset_password(db, token=body.token, new_password=body.new_password)
    return {"status": "ok"}
