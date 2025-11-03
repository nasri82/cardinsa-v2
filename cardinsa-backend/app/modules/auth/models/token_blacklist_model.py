# app/modules/auth/models/token_blacklist_model.py

"""
Token Blacklist Model

SECURITY: Implements token revocation for refresh token rotation and logout.
Essential for localStorage-based authentication security.
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class TokenBlacklist(Base):
    """
    Blacklisted tokens for logout and token rotation.

    SECURITY USE CASES:
    - When a refresh token is used, the old token is blacklisted (rotation)
    - When a user logs out, their tokens are blacklisted (immediate revocation)
    - Prevents token replay attacks
    - Enables detection of compromised tokens

    CLEANUP:
    - Expired tokens can be periodically cleaned up using expires_at field
    - Recommended: Daily cron job to delete records where expires_at < now()
    """
    __tablename__ = "token_blacklist"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    token_jti = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="JWT ID (jti claim) - unique identifier for this token"
    )

    token_type = Column(
        String(20),
        nullable=False,
        comment="Token type: 'access' or 'refresh'"
    )

    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User who owns this token"
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="When token expires (for cleanup queries)"
    )

    blacklisted_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When token was blacklisted"
    )

    reason = Column(
        String(100),
        nullable=True,
        comment="Why blacklisted: 'logout', 'rotation', 'security', 'suspicious'"
    )

    def __repr__(self):
        return f"<TokenBlacklist(jti={self.token_jti[:8]}..., type={self.token_type}, reason={self.reason})>"
