from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from uuid import UUID, uuid4
from jose import JWTError, jwt
from passlib.context import CryptContext

ALG = "HS256"
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    if not plain or len(plain) < 8:
        raise ValueError("Password must be at least 8 chars.")
    return _pwd.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return bool(hashed) and _pwd.verify(plain, hashed)

def create_access_token(*, sub: Union[str, UUID], secret: str, minutes: int = 60, extra: Optional[Dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(sub), "iat": int(now.timestamp()), "nbf": int(now.timestamp()), "jti": str(uuid4()), **(extra or {})}
    if minutes:
        payload["exp"] = int((now + timedelta(minutes=minutes)).timestamp())
    return jwt.encode(payload, secret, algorithm=ALG)

def decode_token(token: str, *, secret: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, secret, algorithms=[ALG])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e
