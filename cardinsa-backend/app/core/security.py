# app/core/security.py
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.settings import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


# Alias for compatibility
def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt. (Alias for get_password_hash)
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return get_password_hash(password)


def create_token(
    data: Dict[str, Any], 
    secret: str, 
    expires_delta: Optional[timedelta] = None,
    algorithm: str = "HS256"
) -> str:
    """
    Create a JWT token.
    
    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        secret: Secret key for signing
        expires_delta: Token expiration time
        algorithm: JWT algorithm to use
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
    return encoded_jwt


def decode_token(token: str, secret: str, algorithm: str = "HS256") -> Dict[str, Any]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        secret: Secret key for verification
        algorithm: JWT algorithm used
        
    Returns:
        Decoded token payload
        
    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    extra_data: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    Create an access token with JTI for blacklist tracking.

    SECURITY: JTI enables token revocation and blacklisting

    Args:
        subject: User identifier (typically user ID as string)
        expires_delta: Optional custom expiration time
        extra_data: Optional extra claims to add to token (e.g., device_fp)

    Returns:
        Tuple of (token, jti) - Both needed for token rotation
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    # Generate unique JTI for this token
    jti = str(uuid.uuid4())

    # Prepare token data
    data = {"sub": subject, "jti": jti, "type": "access"}
    if extra_data:
        data.update(extra_data)

    token = create_token(
        data=data,
        secret=settings.JWT_SECRET,
        expires_delta=expires_delta,
        algorithm=settings.JWT_ALGORITHM
    )

    return token, jti


def create_refresh_token(
    subject: str,
    extra_data: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    Create a refresh token with JTI for rotation tracking.

    SECURITY: JTI enables refresh token rotation

    Args:
        subject: User identifier (typically user ID as string)
        extra_data: Optional extra claims to add to token (e.g., device_fp)

    Returns:
        Tuple of (token, jti) - Both needed for token rotation
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # Generate unique JTI for this token
    jti = str(uuid.uuid4())

    # Prepare token data
    data = {"sub": subject, "jti": jti, "type": "refresh"}
    if extra_data:
        data.update(extra_data)

    token = create_token(
        data=data,
        secret=settings.REFRESH_TOKEN_SECRET,  # Use separate secret for refresh tokens
        expires_delta=expires_delta,
        algorithm=settings.JWT_ALGORITHM
    )

    return token, jti


def verify_token(token: str) -> Optional[str]:
    """
    Verify a token and return the subject (user ID).
    
    Args:
        token: JWT token to verify
        
    Returns:
        User ID from token subject, or None if invalid
    """
    try:
        payload = decode_token(token, secret=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        user_id: str = payload.get("sub")
        return user_id
    except ValueError:
        return None


def create_password_reset_token(email: str) -> str:
    """
    Create a password reset token.
    
    Args:
        email: User email
        
    Returns:
        Password reset token (valid for 30 minutes)
    """
    delta = timedelta(minutes=settings.PASSWORD_RESET_TOKEN_TTL_MINUTES)
    return create_token(
        data={"sub": email, "type": "password_reset"},
        secret=settings.JWT_SECRET,
        expires_delta=delta,
        algorithm=settings.JWT_ALGORITHM
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the email.

    Args:
        token: Password reset token

    Returns:
        Email from token, or None if invalid
    """
    try:
        payload = decode_token(token, secret=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        if payload.get("type") != "password_reset":
            return None
        email: str = payload.get("sub")
        return email
    except ValueError:
        return None


# ================================================================
# TOKEN BLACKLIST FUNCTIONS (for rotation and revocation)
# ================================================================

def is_token_blacklisted(jti: str, db: Session) -> bool:
    """
    Check if a token is blacklisted.

    SECURITY: Prevents reuse of revoked tokens

    Args:
        jti: JWT ID (jti claim) from token
        db: Database session

    Returns:
        True if token is blacklisted, False otherwise
    """
    # Import here to avoid circular dependency
    from app.modules.auth.models.token_blacklist_model import TokenBlacklist

    blacklisted = db.query(TokenBlacklist).filter(
        TokenBlacklist.token_jti == jti
    ).first()

    return blacklisted is not None


def blacklist_token(
    jti: str,
    token_type: str,
    user_id: uuid.UUID,
    expires_at: datetime,
    reason: str,
    db: Session
) -> None:
    """
    Add a token to the blacklist.

    SECURITY USE CASES:
    - Token rotation: Blacklist old refresh token when issuing new one
    - Logout: Blacklist both access and refresh tokens
    - Security: Blacklist compromised tokens

    Args:
        jti: JWT ID (jti claim) from token
        token_type: 'access' or 'refresh'
        user_id: User who owns the token
        expires_at: When token expires (for cleanup)
        reason: Why blacklisting ('rotation', 'logout', 'security')
        db: Database session
    """
    # Import here to avoid circular dependency
    from app.modules.auth.models.token_blacklist_model import TokenBlacklist

    blacklist_entry = TokenBlacklist(
        token_jti=jti,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires_at,
        reason=reason
    )

    db.add(blacklist_entry)
    db.commit()


def cleanup_expired_blacklist_tokens(db: Session) -> int:
    """
    Clean up expired tokens from blacklist.

    MAINTENANCE: Should be run periodically (daily cron job recommended)

    Args:
        db: Database session

    Returns:
        Number of tokens deleted
    """
    # Import here to avoid circular dependency
    from app.modules.auth.models.token_blacklist_model import TokenBlacklist

    now = datetime.utcnow()

    deleted_count = db.query(TokenBlacklist).filter(
        TokenBlacklist.expires_at < now
    ).delete()

    db.commit()

    return deleted_count