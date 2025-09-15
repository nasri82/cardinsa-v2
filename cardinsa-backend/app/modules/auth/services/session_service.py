from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence
from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.auth.models.session_model import Session as UserSession

DEFAULT_DAYS = 30

def create(db: Session, *, user_id: UUID, user_agent: Optional[str], ip: Optional[str], ttl_days: int = DEFAULT_DAYS) -> UserSession:
    now = datetime.now(timezone.utc)
    sess = UserSession(
        id=uuid4(), user_id=user_id, user_agent=(user_agent or "")[:255], ip_address=(ip or "")[:64],
        created_at=now, last_seen=now, expires_at=now + timedelta(days=ttl_days), is_revoked=False
    )
    db.add(sess); db.commit(); db.refresh(sess); return sess

def touch(db: Session, session_id: UUID) -> None:
    s = db.get(UserSession, session_id); 
    if not s: return
    s.last_seen = datetime.now(timezone.utc); db.add(s); db.commit()

def list_active_for_user(db: Session, user_id: UUID) -> Sequence[UserSession]:
    now = datetime.now(timezone.utc)
    stmt = select(UserSession).where(UserSession.user_id==user_id, UserSession.is_revoked.is_(False), UserSession.expires_at>now).order_by(UserSession.last_seen.desc())
    return list(db.scalars(stmt))
