import datetime as dt
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.modules.auth.models.password_reset_token_model import PasswordResetToken

def create_token(
    db: Session, *, user_id: UUID, token: str, expires_at: dt.datetime,
    ip_address: str | None, user_agent: str | None
) -> PasswordResetToken:
    rec = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        ip_address=(ip_address or "")[:64],
        user_agent=(user_agent or "")[:255],
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def get_by_token(db: Session, token: str) -> Optional[PasswordResetToken]:
    return db.scalar(select(PasswordResetToken).where(PasswordResetToken.token == token).limit(1))

def mark_used(db: Session, rec: PasswordResetToken) -> None:
    rec.used = True
    rec.used_at = dt.datetime.now(dt.timezone.utc)
    db.add(rec)
    db.commit()
