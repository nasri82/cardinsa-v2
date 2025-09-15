# app/modules/auth/services/password_service.py
from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password as _verify
from app.modules.auth.models.user_model import User


# Keep existing helpers (other services import these)
def hash(plain: str) -> str:
    return hash_password(plain)


def verify(plain: str, hashed: str) -> bool:
    return _verify(plain, hashed)


# ---- Missing function used by users_route.py ----
def change_password_for_user(db: Session, user: User, new_password: str) -> None:
    """
    Sets a new password for the given user and commits.
    """
    user.hashed_password = hash_password(new_password)
    db.add(user)
    db.commit()


# ---- Optional: use if you later require old password verification ----
def change_password_with_check(
    db: Session, user: User, old_password: str, new_password: str
) -> None:
    """
    Verifies the old password before updating to the new one.
    Not used by default routes, but handy if you add self-service change.
    """
    if not _verify(old_password, user.hashed_password or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    change_password_for_user(db, user, new_password)
