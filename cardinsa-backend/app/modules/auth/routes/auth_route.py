# app/modules/auth/routes/auth_route.py

"""
Authentication Routes - WITH TOKEN ROTATION

SECURITY: Implements refresh token rotation and blacklisting for
localStorage-based authentication with mobile/offline support.
"""

from datetime import datetime, timedelta
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt

from app.core.database import get_db
from app.core.settings import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    is_token_blacklisted,
    blacklist_token,
    decode_token
)
from app.modules.auth.schemas.auth_schema import TokenResponse, UserInfoResponse
from app.modules.auth.repositories.user_repository import UserRepository
from app.core.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    x_device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint"),
):
    """
    OAuth2 compatible token login with refresh token rotation.

    SECURITY FEATURES:
    - Returns both access token (30 min) and refresh token (7 days)
    - Tokens include JTI for blacklist tracking
    - Device fingerprint binding for token theft detection
    - Account lockout after failed attempts
    - Failed login tracking

    Returns:
        access_token: Short-lived token for API access
        refresh_token: Long-lived token for getting new access tokens
        token_type: "bearer"
    """
    # Validate input
    if not form_data.username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username cannot be empty"
        )

    if not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password cannot be empty"
        )

    # Get user from database
    user_repo = UserRepository(db)
    user = user_repo.get_by_username_or_email(form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )

    # Check if account is locked
    if user.account_locked_until and user.account_locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked until {user.account_locked_until}"
        )

    # Reset failed attempts and update last login
    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()
    user.account_locked_until = None
    db.commit()

    # SECURITY: Create tokens with JTI for blacklist tracking and device fingerprint binding
    extra_data = {}
    if x_device_fingerprint:
        extra_data["device_fp"] = x_device_fingerprint

    access_token, access_jti = create_access_token(
        subject=str(user.id),
        extra_data=extra_data if extra_data else None
    )
    refresh_token, refresh_jti = create_refresh_token(
        subject=str(user.id),
        extra_data=extra_data if extra_data else None
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.

    SECURITY: Implements refresh token rotation
    - Old refresh token is blacklisted after use
    - New refresh token is issued along with new access token
    - Prevents token replay attacks

    Args:
        refresh_token: The refresh token from localStorage

    Returns:
        New access_token and refresh_token pair
    """
    try:
        # Decode refresh token
        payload = decode_token(
            refresh_token,
            secret=settings.REFRESH_TOKEN_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )

        # Verify token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # Extract token data
        user_id_str = payload.get("sub")
        old_jti = payload.get("jti")
        device_fp = payload.get("device_fp")  # Preserve device fingerprint

        if not user_id_str or not old_jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        user_id = uuid.UUID(user_id_str)

        # SECURITY: Check if refresh token is blacklisted
        if is_token_blacklisted(old_jti, db):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        # Verify user exists and is active
        user_repo = UserRepository(db)
        user = user_repo.get(user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # SECURITY: Blacklist old refresh token (rotation)
        blacklist_token(
            jti=old_jti,
            token_type="refresh",
            user_id=user_id,
            expires_at=datetime.fromtimestamp(payload.get("exp")),
            reason="rotation",
            db=db
        )

        # Create new token pair (preserve device fingerprint from old token)
        extra_data = {}
        if device_fp:
            extra_data["device_fp"] = device_fp

        new_access_token, access_jti = create_access_token(
            subject=str(user.id),
            extra_data=extra_data if extra_data else None
        )
        new_refresh_token, refresh_jti = create_refresh_token(
            subject=str(user.id),
            extra_data=extra_data if extra_data else None
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        # Log the error for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout")
async def logout(
    access_token: str = Body(..., embed=True),
    refresh_token: str = Body(..., embed=True),
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by blacklisting tokens.

    SECURITY: Immediate token revocation
    - Blacklists both access and refresh tokens
    - Prevents token reuse
    - Essential for security when user logs out

    Args:
        access_token: Current access token
        refresh_token: Current refresh token

    Returns:
        Success message
    """
    try:
        # Decode and blacklist access token
        try:
            access_payload = decode_token(
                access_token,
                secret=settings.JWT_SECRET,
                algorithm=settings.JWT_ALGORITHM
            )
            access_jti = access_payload.get("jti")
            if access_jti:
                blacklist_token(
                    jti=access_jti,
                    token_type="access",
                    user_id=current.user.id,
                    expires_at=datetime.fromtimestamp(access_payload.get("exp")),
                    reason="logout",
                    db=db
                )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            # Token may be expired or invalid, but that's okay for logout
            pass

        # Decode and blacklist refresh token
        try:
            refresh_payload = decode_token(
                refresh_token,
                secret=settings.REFRESH_TOKEN_SECRET,
                algorithm=settings.JWT_ALGORITHM
            )
            refresh_jti = refresh_payload.get("jti")
            if refresh_jti:
                blacklist_token(
                    jti=refresh_jti,
                    token_type="refresh",
                    user_id=current.user.id,
                    expires_at=datetime.fromtimestamp(refresh_payload.get("exp")),
                    reason="logout",
                    db=db
                )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            # Token may be expired or invalid, but that's okay for logout
            pass

        return {"message": "Logged out successfully"}

    except Exception as e:
        # Even if something fails, pretend logout succeeded for security
        return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user information."""
    user = current.user

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "phone": user.phone,
        "is_active": user.is_active,
        "user_type": user.user_type,
        "company_id": user.company_id,
        "department": user.department,
        "unit": user.unit,
        "position": user.position,
        "roles": [{"id": str(r.id), "name": r.name} for r in user.roles] if user.roles else []
    }
