import datetime as dt
import secrets
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.settings import settings
from app.core.mailer import Mailer, get_mailer

from app.modules.auth.repositories import user_repository as users
from app.modules.auth.repositories import password_reset_repository as repo
from app.modules.auth.services.password_service import hash as hash_password

# Load the template once
PASSWORD_EMAIL_TEMPLATE = """<!doctype html>
<html>
  <body style="font-family: Arial, sans-serif; color:#222;">
    <h2>{app_name} – Password Reset</h2>
    <p>Hello,</p>
    <p>We received a request to reset your password. Click the link below to set a new one:</p>
    <p>
      <a href="{reset_url}" style="background:#2563eb;color:#fff;padding:10px 16px;text-decoration:none;border-radius:6px;">
        Reset your password
      </a>
    </p>
    <p>This link will expire in {token_ttl_minutes} minutes. If you didn’t request this, you can ignore this email.</p>
    <hr/>
    <p style="font-size:12px;color:#666;">If the button doesn’t work, paste this URL into your browser:<br/>{reset_url}</p>
  </body>
</html>"""

def _now():
    return dt.datetime.now(dt.timezone.utc)

def _ttl_minutes() -> int:
    return getattr(settings, "PASSWORD_RESET_TOKEN_TTL_MINUTES", 30)

def _frontend_base() -> str:
    # e.g., https://portal.cardinsa.com
    return getattr(settings, "FRONTEND_BASE_URL", "http://localhost:3000")

def _app_name() -> str:
    return getattr(settings, "APP_NAME", "Cardinsa")

def request_reset(
    db: Session, *,
    email: Optional[str],
    username: Optional[str],
    client_ip: Optional[str],
    user_agent: Optional[str],
    mailer: Optional[Mailer] = None,
) -> None:
    """Non-enumerating: always returns None; silently succeeds if user not found."""
    user = users.get_by_email_or_username(db, email=email, username=username)
    if not user or not user.is_active:
        return

    token = secrets.token_urlsafe(48)
    expires_at = _now() + dt.timedelta(minutes=_ttl_minutes())
    rec = repo.create_token(
        db,
        user_id=user.id,
        token=token,
        expires_at=expires_at,
        ip_address=client_ip,
        user_agent=user_agent,
    )

    reset_url = f"{_frontend_base().rstrip('/')}/reset-password?token={rec.token}"
    html = PASSWORD_EMAIL_TEMPLATE.format(
        app_name=_app_name(),
        reset_url=reset_url,
        token_ttl_minutes=_ttl_minutes(),
    )
    (mailer or get_mailer()).send_email(
        to=user.email,
        subject=f"{_app_name()} – Password Reset",
        html=html,
        text=f"Open this link to reset your password (expires in {_ttl_minutes()} minutes): {reset_url}",
    )

def reset_password(db: Session, *, token: str, new_password: str) -> None:
    rec = repo.get_by_token(db, token)
    if not rec or rec.used or rec.expires_at <= _now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = users.get_by_id(db, rec.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user.hashed_password = hash_password(new_password)
    db.add(user); db.commit()
    repo.mark_used(db, rec)
