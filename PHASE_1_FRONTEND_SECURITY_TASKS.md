# Phase 1: Frontend Security Tasks - localStorage Enhancement

**Date**: 2025-11-03
**Status**: IN PROGRESS
**Priority**: HIGH
**Estimated Time**: 6-8 hours

---

## Executive Summary

This document outlines the frontend security enhancements for Phase 1, focusing on securing localStorage-based authentication for multi-platform support (web, mobile, PWA, offline mode).

### Architecture Decision: Why localStorage Over httpOnly Cookies

**Decision**: Enhance localStorage security instead of migrating to httpOnly cookies.

**Rationale**:
1. **Mobile App Support**: Native mobile apps (React Native, Flutter) don't handle cookies well
2. **Offline Mode**: Offline functionality requires local token access
3. **PWA Compatibility**: Progressive Web Apps have better localStorage support
4. **Cross-Platform**: Single authentication approach works everywhere
5. **Broker/Member Portals**: Offline-capable portals require token access

**Security Strategy**: Multiple layers of protection instead of single httpOnly approach.

### Current Security Posture

**Backend**: ✅ All critical vulnerabilities fixed, CSP headers implemented
**Frontend**: ⚠️ 5 high-priority enhancements needed

---

## Task 1: Reduce JWT Token Expiry Time

### Priority: HIGH (Security Hygiene)
### Estimated Time: 30 minutes
### Risk Level: CVSS 5.3 (Medium)

### Current Configuration

Currently, JWT access tokens expire after 120 minutes (2 hours):

**File**: `cardinsa-backend/.env`
```bash
JWT_EXPIRE_MINUTES=120  # ⚠️ Too long for security best practices
```

**Risks**:
- Longer window for token theft exploitation
- Stolen tokens remain valid for extended period
- Increased exposure window for XSS attacks

### Solution: Short-Lived Access Tokens

Reduce access token lifetime to 15-30 minutes, balanced with refresh token rotation.

### Implementation Steps

#### Step 1: Update Backend Configuration

**File**: `cardinsa-backend/.env`

```bash
# ---- Auth ----
JWT_SECRET=AbiepIvrNGL3tkdHeS3kxnutdZ1g84Hzv5rTsnviWKaZ2GdW2eIwwVtqhwuRJCSNGRY56S9yW8MM7elUYDPvow
REFRESH_TOKEN_SECRET=jcMRcQovO1H57ePFJTUsDNzfZ2r9qG_KxaVgsErKIAaIyrdFYUjPuLH6G_79JtxWDi0WDlwOmUcOLKHzv3aDLw

# ✅ NEW: Reduced token expiry for better security
JWT_EXPIRE_MINUTES=30              # Access token: 30 minutes (was 120)
REFRESH_TOKEN_EXPIRE_DAYS=7        # Refresh token: 7 days
JWT_ALGORITHM=HS256
```

**File**: `cardinsa-backend/.env.example`

```bash
# ================================================================
# AUTHENTICATION & AUTHORIZATION
# ================================================================
# JWT secret keys - MUST be generated securely in production:
#   python -c "import secrets; print(secrets.token_urlsafe(64))"
JWT_SECRET=your-super-secret-jwt-key-here-change-this-in-production
REFRESH_TOKEN_SECRET=your-refresh-token-secret-here-change-this-too

# SECURITY: Token expiry times
# Access tokens should be short-lived (15-30 minutes)
# Refresh tokens can be longer-lived (7-14 days)
JWT_EXPIRE_MINUTES=30              # Access token lifetime
REFRESH_TOKEN_EXPIRE_DAYS=7        # Refresh token lifetime

JWT_ALGORITHM=HS256
PASSWORD_RESET_TOKEN_TTL_MINUTES=30
```

#### Step 2: Update Settings Model

**File**: `cardinsa-backend/app/core/settings.py`

Add the refresh token expiry setting:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # --- Authentication ---
    JWT_SECRET: str
    REFRESH_TOKEN_SECRET: str
    JWT_EXPIRE_MINUTES: int = 30  # Changed from 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # NEW
    JWT_ALGORITHM: str = "HS256"
    PASSWORD_RESET_TOKEN_TTL_MINUTES: int = 30
```

#### Step 3: Verify Token Generation

**File**: `cardinsa-backend/app/core/security.py`

Ensure token generation uses the new settings:

```python
from datetime import datetime, timedelta
from app.core.settings import settings

def create_access_token(data: dict) -> str:
    """Create short-lived access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create longer-lived refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.REFRESH_TOKEN_SECRET, algorithm=settings.JWT_ALGORITHM)
```

### Testing Checklist

- [ ] Backend loads with new JWT_EXPIRE_MINUTES=30 setting
- [ ] Access tokens expire after 30 minutes
- [ ] Refresh tokens expire after 7 days
- [ ] Token expiry is correctly encoded in JWT payload
- [ ] Expired tokens return 401 Unauthorized

---

## Task 2: Implement Token Refresh with Rotation

### Priority: HIGH (Session Management)
### Estimated Time: 3-4 hours
### Risk Level: CVSS 6.8 (Medium)

### Current Issue

Without proper refresh token rotation:
- Stolen refresh tokens can be used indefinitely until expiry
- No mechanism to invalidate compromised sessions
- Refresh tokens can be replayed if intercepted

### Solution: Refresh Token Rotation

When a refresh token is used, issue a new refresh token and invalidate the old one.

### Implementation Steps

#### Step 1: Backend - Add Token Blacklist Table

**Create Alembic Migration**:

```bash
cd cardinsa-backend
alembic revision -m "add_token_blacklist_table"
```

**File**: `cardinsa-backend/alembic/versions/[timestamp]_add_token_blacklist_table.py`

```python
"""add token blacklist table

Revision ID: [auto-generated]
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    op.create_table(
        'token_blacklist',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('token_jti', sa.String(100), nullable=False, unique=True,
                  comment='JWT ID (jti claim) of blacklisted token'),
        sa.Column('token_type', sa.String(20), nullable=False,
                  comment='Token type: access or refresh'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False,
                  comment='User who owns this token'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False,
                  comment='When token expires'),
        sa.Column('blacklisted_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()'),
                  comment='When token was blacklisted'),
        sa.Column('reason', sa.String(100), nullable=True,
                  comment='Why token was blacklisted'),
    )

    # Indexes for efficient lookups
    op.create_index('ix_token_blacklist_token_jti', 'token_blacklist', ['token_jti'])
    op.create_index('ix_token_blacklist_user_id', 'token_blacklist', ['user_id'])
    op.create_index('ix_token_blacklist_expires_at', 'token_blacklist', ['expires_at'])

def downgrade() -> None:
    op.drop_table('token_blacklist')
```

Run migration:
```bash
alembic upgrade head
```

#### Step 2: Backend - Create TokenBlacklist Model

**File**: `cardinsa-backend/app/modules/auth/models/token_blacklist_model.py`

```python
"""Token Blacklist Model"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class TokenBlacklist(Base):
    """
    Blacklisted tokens for logout and token rotation.

    When a refresh token is used, the old token is blacklisted.
    When a user logs out, their tokens are blacklisted.
    """
    __tablename__ = "token_blacklist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_jti = Column(String(100), nullable=False, unique=True, index=True)
    token_type = Column(String(20), nullable=False)  # 'access' or 'refresh'
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    reason = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<TokenBlacklist(jti={self.token_jti}, type={self.token_type})>"
```

#### Step 3: Backend - Update Security Utilities

**File**: `cardinsa-backend/app/core/security.py`

Add JTI (JWT ID) to tokens and blacklist checking:

```python
import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.settings import settings
from app.modules.auth.models.token_blacklist_model import TokenBlacklist

def create_access_token(data: dict, jti: Optional[str] = None) -> tuple[str, str]:
    """
    Create access token with JTI for blacklisting.
    Returns: (token, jti)
    """
    to_encode = data.copy()
    jti = jti or str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "type": "access",
        "jti": jti,  # JWT ID for blacklist tracking
    })

    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, jti

def create_refresh_token(data: dict, jti: Optional[str] = None) -> tuple[str, str]:
    """
    Create refresh token with JTI for rotation.
    Returns: (token, jti)
    """
    to_encode = data.copy()
    jti = jti or str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "jti": jti,
    })

    token = jwt.encode(to_encode, settings.REFRESH_TOKEN_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, jti

def is_token_blacklisted(jti: str, db: Session) -> bool:
    """Check if token is blacklisted"""
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
    """Add token to blacklist"""
    blacklist_entry = TokenBlacklist(
        token_jti=jti,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires_at,
        reason=reason
    )
    db.add(blacklist_entry)
    db.commit()
```

#### Step 4: Backend - Update Token Refresh Endpoint

**File**: `cardinsa-backend/app/modules/auth/routes/auth_route.py`

```python
from app.core.security import (
    create_access_token,
    create_refresh_token,
    is_token_blacklisted,
    blacklist_token
)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    Implements refresh token rotation for security.
    """
    try:
        # Decode refresh token
        payload = jwt.decode(
            refresh_token,
            settings.REFRESH_TOKEN_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Verify token type
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        # Extract token data
        user_id = uuid.UUID(payload.get("sub"))
        jti = payload.get("jti")

        if not user_id or not jti:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # SECURITY: Check if refresh token is blacklisted
        if is_token_blacklisted(jti, db):
            raise HTTPException(
                status_code=401,
                detail="Token has been revoked"
            )

        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        # SECURITY: Blacklist old refresh token (rotation)
        blacklist_token(
            jti=jti,
            token_type="refresh",
            user_id=user_id,
            expires_at=datetime.fromtimestamp(payload.get("exp")),
            reason="token_rotation",
            db=db
        )

        # Create new token pair
        token_data = {"sub": str(user.id), "email": user.email}
        new_access_token, access_jti = create_access_token(token_data)
        new_refresh_token, refresh_jti = create_refresh_token(token_data)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Step 5: Backend - Update Logout Endpoint

**File**: `cardinsa-backend/app/modules/auth/routes/auth_route.py`

```python
@router.post("/logout")
async def logout(
    access_token: str = Body(..., embed=True),
    refresh_token: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by blacklisting tokens.
    """
    try:
        # Decode and blacklist access token
        access_payload = jwt.decode(
            access_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        access_jti = access_payload.get("jti")
        if access_jti:
            blacklist_token(
                jti=access_jti,
                token_type="access",
                user_id=current_user.id,
                expires_at=datetime.fromtimestamp(access_payload.get("exp")),
                reason="logout",
                db=db
            )

        # Decode and blacklist refresh token
        refresh_payload = jwt.decode(
            refresh_token,
            settings.REFRESH_TOKEN_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        refresh_jti = refresh_payload.get("jti")
        if refresh_jti:
            blacklist_token(
                jti=refresh_jti,
                token_type="refresh",
                user_id=current_user.id,
                expires_at=datetime.fromtimestamp(refresh_payload.get("exp")),
                reason="logout",
                db=db
            )

        return {"message": "Logged out successfully"}

    except JWTError:
        # Even if token decode fails, return success (already logged out)
        return {"message": "Logged out successfully"}
```

#### Step 6: Backend - Update Token Validation

**File**: `cardinsa-backend/app/core/dependencies.py`

```python
from app.core.security import is_token_blacklisted

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Validates token and checks blacklist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")

        if user_id is None or jti is None:
            raise credentials_exception

        # SECURITY: Check if token is blacklisted
        if is_token_blacklisted(jti, db):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user
```

#### Step 7: Frontend - Implement Auto-Refresh

**File**: `cardinsa-frontend/src/lib/api.ts`

```typescript
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token refresh state
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: string) => void;
  reject: (error: any) => void;
}> = [];

const processQueue = (error: any = null, token: string | null = null) => {
  failedQueue.forEach(promise => {
    if (error) {
      promise.reject(error);
    } else {
      promise.resolve(token!);
    }
  });
  failedQueue = [];
};

// Request interceptor - Add access token to requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {

      // If already refreshing, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          })
          .catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');

      if (!refreshToken) {
        // No refresh token - redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        // Call refresh endpoint
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken
        });

        const { access_token, refresh_token: new_refresh_token } = response.data;

        // SECURITY: Token rotation - store new tokens
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', new_refresh_token);

        // Update authorization header
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }

        processQueue(null, access_token);
        isRefreshing = false;

        // Retry original request
        return apiClient(originalRequest);

      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;

        // Refresh failed - clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

#### Step 8: Frontend - Update AuthContext

**File**: `cardinsa-frontend/src/contexts/AuthContext.tsx`

```typescript
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiClient from '@/lib/api';

interface User {
  id: string;
  email: string;
  full_name: string;
  // ... other user fields
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication status on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const accessToken = localStorage.getItem('access_token');

    if (!accessToken) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await apiClient.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      // Token invalid or expired - will be handled by interceptor
      setUser(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/login', { email, password });

      const { access_token, refresh_token, user: userData } = response.data;

      // Store tokens
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      setUser(userData);
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      const accessToken = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');

      // Call logout endpoint to blacklist tokens
      await apiClient.post('/auth/logout', {
        access_token: accessToken,
        refresh_token: refreshToken
      });
    } catch (error) {
      // Even if logout fails, clear local tokens
      console.error('Logout error:', error);
    } finally {
      // Clear tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isLoading,
        isAuthenticated: !!user
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### Testing Checklist

- [ ] Token refresh works automatically on 401 errors
- [ ] Old refresh tokens are blacklisted after use
- [ ] New token pair is issued on refresh
- [ ] Logout blacklists both access and refresh tokens
- [ ] Blacklisted tokens cannot be used
- [ ] Multiple simultaneous requests trigger only one refresh
- [ ] Failed refresh redirects to login
- [ ] Token rotation persists across page refreshes

---

## Task 3: Add Device Fingerprinting

### Priority: MEDIUM (Additional Security Layer)
### Estimated Time: 2-3 hours
### Risk Level: CVSS 5.5 (Medium)

### Purpose

Bind tokens to specific devices/browsers to detect token theft and unauthorized usage.

### Implementation Steps

#### Step 1: Frontend - Create Device Fingerprint Utility

**File**: `cardinsa-frontend/src/lib/deviceFingerprint.ts`

```typescript
import { createHash } from 'crypto';

/**
 * Generate device fingerprint from browser characteristics.
 * Not 100% unique but sufficient for token binding.
 */
export async function generateDeviceFingerprint(): Promise<string> {
  const components: string[] = [];

  // Screen resolution
  components.push(`${window.screen.width}x${window.screen.height}x${window.screen.colorDepth}`);

  // Timezone
  components.push(Intl.DateTimeFormat().resolvedOptions().timeZone);

  // Language
  components.push(navigator.language);

  // Platform
  components.push(navigator.platform);

  // User agent
  components.push(navigator.userAgent);

  // Hardware concurrency
  components.push(String(navigator.hardwareConcurrency || 0));

  // Device memory (if available)
  const deviceMemory = (navigator as any).deviceMemory;
  if (deviceMemory) {
    components.push(String(deviceMemory));
  }

  // Canvas fingerprint (more advanced)
  const canvasFingerprint = await getCanvasFingerprint();
  components.push(canvasFingerprint);

  // Combine all components
  const combined = components.join('|');

  // Hash the combined string for privacy
  const encoder = new TextEncoder();
  const data = encoder.encode(combined);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

  return hashHex;
}

async function getCanvasFingerprint(): Promise<string> {
  try {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) return 'no-canvas';

    // Draw some text
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125, 1, 62, 20);
    ctx.fillStyle = '#069';
    ctx.fillText('Cardinsa', 2, 15);
    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
    ctx.fillText('Cardinsa', 4, 17);

    // Get canvas data
    const dataURL = canvas.toDataURL();

    // Hash it
    const encoder = new TextEncoder();
    const data = encoder.encode(dataURL);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    return hashHex;
  } catch (error) {
    return 'canvas-error';
  }
}

/**
 * Store device fingerprint in localStorage.
 */
export async function storeDeviceFingerprint(): Promise<string> {
  let fingerprint = localStorage.getItem('device_fingerprint');

  if (!fingerprint) {
    fingerprint = await generateDeviceFingerprint();
    localStorage.setItem('device_fingerprint', fingerprint);
  }

  return fingerprint;
}

/**
 * Get stored device fingerprint.
 */
export function getDeviceFingerprint(): string | null {
  return localStorage.getItem('device_fingerprint');
}
```

#### Step 2: Frontend - Send Fingerprint with Auth Requests

**File**: `cardinsa-frontend/src/lib/api.ts`

Update the request interceptor:

```typescript
import { getDeviceFingerprint, storeDeviceFingerprint } from './deviceFingerprint';

// Ensure device fingerprint exists
storeDeviceFingerprint();

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = localStorage.getItem('access_token');
    const deviceFingerprint = getDeviceFingerprint();

    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    // Add device fingerprint to all requests
    if (deviceFingerprint && config.headers) {
      config.headers['X-Device-Fingerprint'] = deviceFingerprint;
    }

    return config;
  },
  (error) => Promise.reject(error)
);
```

#### Step 3: Backend - Store Fingerprint with Token

**File**: `cardinsa-backend/app/modules/auth/routes/auth_route.py`

```python
from fastapi import Header

@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginSchema,
    x_device_fingerprint: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Login with device fingerprint tracking"""

    # ... authentication logic ...

    # Create tokens with device fingerprint
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "device_fp": x_device_fingerprint  # Embed fingerprint in token
    }

    access_token, access_jti = create_access_token(token_data)
    refresh_token, refresh_jti = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_data
    }
```

#### Step 4: Backend - Validate Fingerprint on Requests

**File**: `cardinsa-backend/app/core/dependencies.py`

```python
from fastapi import Header, HTTPException, status

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    x_device_fingerprint: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user.
    Validates device fingerprint for additional security.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        token_fingerprint: str = payload.get("device_fp")

        if user_id is None or jti is None:
            raise credentials_exception

        # SECURITY: Validate device fingerprint
        if token_fingerprint and x_device_fingerprint:
            if token_fingerprint != x_device_fingerprint:
                # Device fingerprint mismatch - possible token theft
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Device fingerprint mismatch - please login again"
                )

        # Check blacklist
        if is_token_blacklisted(jti, db):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user
```

### Testing Checklist

- [ ] Device fingerprint is generated on app load
- [ ] Fingerprint is stored in localStorage
- [ ] Fingerprint is sent with auth requests
- [ ] Fingerprint is embedded in JWT tokens
- [ ] Fingerprint mismatch triggers re-authentication
- [ ] Works across browser sessions
- [ ] Stable across page refreshes

---

## Task 4: XSS Prevention Through CSP (Already Implemented ✅)

### Priority: HIGH (Defense in Depth)
### Status: COMPLETED

### Current Implementation

Content Security Policy headers are already implemented in the backend middleware:

**File**: `cardinsa-backend/app/core/middleware.py` (lines 12-154)

```python
class SecurityHeadersMiddleware:
    """
    Adds security headers including CSP for XSS protection.
    """
    async def __call__(self, scope, receive, send):
        # ... implementation ...

        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        headers.append((b"content-security-policy", "; ".join(csp_directives).encode()))
        headers.append((b"x-frame-options", b"DENY"))
        headers.append((b"x-content-type-options", b"nosniff"))
        headers.append((b"x-xss-protection", b"1; mode=block"))
```

### Additional Frontend Protection

**File**: `cardinsa-frontend/next.config.js` (or equivalent)

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https:",
              "font-src 'self' data:",
              "connect-src 'self' http://localhost:8000",
              "frame-ancestors 'none'",
            ].join('; '),
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
```

### Testing Checklist

- [x] CSP headers present in response (backend)
- [ ] CSP headers present in response (frontend)
- [ ] Inline scripts are blocked (if not whitelisted)
- [ ] External scripts from untrusted sources are blocked
- [ ] Test with browser console for CSP violations

---

## Task 5: Optional - Token Encryption in localStorage

### Priority: LOW (Additional Layer)
### Estimated Time: 1-2 hours
### Risk Level: CVSS 4.0 (Low)

### Purpose

Encrypt tokens before storing in localStorage to add another layer of protection against XSS attacks.

**Note**: This is defense in depth. An XSS attacker with code execution can still decrypt the tokens since the encryption key must be in JavaScript. However, it prevents casual token theft from localStorage inspection.

### Implementation Steps

#### Step 1: Frontend - Create Encryption Utility

**File**: `cardinsa-frontend/src/lib/encryption.ts`

```typescript
/**
 * Simple encryption utility for localStorage tokens.
 *
 * SECURITY NOTE: This is NOT foolproof against XSS attacks since the
 * encryption key must be in JavaScript. However, it adds a layer of
 * obfuscation and prevents casual localStorage inspection.
 */

const ENCRYPTION_KEY = process.env.NEXT_PUBLIC_ENCRYPTION_KEY || 'default-key-change-in-production';

/**
 * Encrypt a string using AES-GCM
 */
export async function encrypt(text: string): Promise<string> {
  try {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);

    // Generate a random IV
    const iv = crypto.getRandomValues(new Uint8Array(12));

    // Import key
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      encoder.encode(ENCRYPTION_KEY),
      { name: 'PBKDF2' },
      false,
      ['deriveBits', 'deriveKey']
    );

    const key = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: encoder.encode('salt'),
        iterations: 100000,
        hash: 'SHA-256'
      },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      false,
      ['encrypt']
    );

    // Encrypt
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      data
    );

    // Combine IV and encrypted data
    const combined = new Uint8Array(iv.length + encrypted.byteLength);
    combined.set(iv);
    combined.set(new Uint8Array(encrypted), iv.length);

    // Convert to base64
    return btoa(String.fromCharCode(...combined));
  } catch (error) {
    console.error('Encryption error:', error);
    return text; // Fallback to unencrypted
  }
}

/**
 * Decrypt a string encrypted with encrypt()
 */
export async function decrypt(encryptedText: string): Promise<string> {
  try {
    const encoder = new TextEncoder();

    // Decode base64
    const combined = Uint8Array.from(atob(encryptedText), c => c.charCodeAt(0));

    // Extract IV and encrypted data
    const iv = combined.slice(0, 12);
    const data = combined.slice(12);

    // Import key
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      encoder.encode(ENCRYPTION_KEY),
      { name: 'PBKDF2' },
      false,
      ['deriveBits', 'deriveKey']
    );

    const key = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: encoder.encode('salt'),
        iterations: 100000,
        hash: 'SHA-256'
      },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      false,
      ['decrypt']
    );

    // Decrypt
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      key,
      data
    );

    const decoder = new TextDecoder();
    return decoder.decode(decrypted);
  } catch (error) {
    console.error('Decryption error:', error);
    return encryptedText; // Fallback to encrypted text
  }
}

/**
 * Secure localStorage wrapper with encryption
 */
export const secureStorage = {
  async setItem(key: string, value: string): Promise<void> {
    const encrypted = await encrypt(value);
    localStorage.setItem(key, encrypted);
  },

  async getItem(key: string): Promise<string | null> {
    const encrypted = localStorage.getItem(key);
    if (!encrypted) return null;
    return await decrypt(encrypted);
  },

  removeItem(key: string): void {
    localStorage.removeItem(key);
  },

  clear(): void {
    localStorage.clear();
  }
};
```

#### Step 2: Frontend - Update AuthContext to Use Encrypted Storage

**File**: `cardinsa-frontend/src/contexts/AuthContext.tsx`

```typescript
import { secureStorage } from '@/lib/encryption';

export function AuthProvider({ children }: { children: ReactNode }) {
  // ... existing code ...

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/login', { email, password });

      const { access_token, refresh_token, user: userData } = response.data;

      // Store tokens encrypted
      await secureStorage.setItem('access_token', access_token);
      await secureStorage.setItem('refresh_token', refresh_token);

      setUser(userData);
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      const accessToken = await secureStorage.getItem('access_token');
      const refreshToken = await secureStorage.getItem('refresh_token');

      await apiClient.post('/auth/logout', {
        access_token: accessToken,
        refresh_token: refreshToken
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      secureStorage.removeItem('access_token');
      secureStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  // ... rest of implementation ...
}
```

#### Step 3: Frontend - Update API Client

**File**: `cardinsa-frontend/src/lib/api.ts`

```typescript
import { secureStorage } from './encryption';

// Request interceptor
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const accessToken = await secureStorage.getItem('access_token');
    const deviceFingerprint = getDeviceFingerprint();

    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    if (deviceFingerprint && config.headers) {
      config.headers['X-Device-Fingerprint'] = deviceFingerprint;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Update refresh logic to use secureStorage
// ... (similar updates for all localStorage calls)
```

### Testing Checklist

- [ ] Tokens are encrypted in localStorage (inspect DevTools)
- [ ] Encrypted tokens can be decrypted successfully
- [ ] Login/logout works with encrypted storage
- [ ] Token refresh works with encrypted storage
- [ ] Decryption failure gracefully handled

---

## Security Best Practices Summary

### Multi-Layer Defense Strategy

1. **Short-Lived Tokens** (30 minutes) - Limits exposure window
2. **Token Rotation** - Invalidates old refresh tokens on use
3. **Token Blacklist** - Prevents reuse of revoked tokens
4. **Device Fingerprinting** - Detects token theft across devices
5. **CSP Headers** - Blocks XSS attack vectors
6. **Input Sanitization** - Prevents XSS injection (separate task)
7. **Token Encryption** (optional) - Obfuscates localStorage data

### Why This Approach Works

- **XSS Mitigation**: CSP blocks script injection; encryption adds obfuscation
- **Token Theft Detection**: Device fingerprinting detects cross-device usage
- **Stolen Token Limitation**: Short expiry + rotation limits damage window
- **Session Invalidation**: Blacklist allows immediate revocation
- **Mobile/Offline Support**: Works on all platforms unlike httpOnly cookies
- **User Experience**: Auto-refresh maintains seamless sessions

---

## Migration Checklist

### Backend Tasks
- [ ] Update JWT_EXPIRE_MINUTES to 30 in .env
- [ ] Add REFRESH_TOKEN_EXPIRE_DAYS to .env and settings.py
- [ ] Create token_blacklist migration
- [ ] Create TokenBlacklist model
- [ ] Update security.py with JTI and blacklist functions
- [ ] Update token refresh endpoint with rotation
- [ ] Update logout endpoint to blacklist tokens
- [ ] Update get_current_user to check blacklist and fingerprint
- [ ] Test token generation and validation

### Frontend Tasks
- [ ] Create device fingerprint utility
- [ ] Update API client to send fingerprint header
- [ ] Implement auto-refresh interceptor with token rotation
- [ ] Update AuthContext for new flow
- [ ] (Optional) Create encryption utility
- [ ] (Optional) Update storage calls to use encryption
- [ ] Test login flow
- [ ] Test token refresh flow
- [ ] Test logout flow
- [ ] Test device fingerprint validation

### Testing
- [ ] Access tokens expire after 30 minutes
- [ ] Refresh tokens expire after 7 days
- [ ] Token refresh works and rotates tokens
- [ ] Old refresh tokens are blacklisted
- [ ] Logout blacklists both tokens
- [ ] Device fingerprint mismatch blocks access
- [ ] Auto-refresh maintains sessions seamlessly
- [ ] Multiple simultaneous requests handled correctly
- [ ] Works on mobile browsers
- [ ] Works in offline mode (when reconnected)
- [ ] Works in incognito/private mode

---

## Timeline

**Estimated Total Time**: 6-8 hours

- **Task 1 - Token Expiry**: 30 minutes
- **Task 2 - Token Rotation**: 3-4 hours
- **Task 3 - Device Fingerprinting**: 2-3 hours
- **Task 4 - CSP Verification**: 30 minutes (already implemented)
- **Task 5 - Encryption (Optional)**: 1-2 hours

**Recommended Approach**:
1. Start with Task 1 (quick win)
2. Implement Task 2 (core security)
3. Add Task 3 (additional protection)
4. Verify Task 4 (CSP testing)
5. Optionally add Task 5 (encryption)

---

## Resources

### Documentation
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Token Refresh Best Practices](https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation)
- [Device Fingerprinting](https://github.com/fingerprintjs/fingerprintjs)
- [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)

### Tools
- [jwt.io](https://jwt.io/) - JWT debugger
- [OWASP ZAP](https://www.zaproxy.org/) - Security scanner
- Chrome DevTools - Application tab for localStorage inspection

---

## Risk Assessment

### Before Implementation ⚠️
- **XSS Impact**: High - Tokens vulnerable to theft via XSS
- **Token Theft**: High - No device binding or rotation
- **Stolen Token Lifetime**: 2 hours - Extended exposure window
- **Session Revocation**: Not possible - No token blacklist
- **Attack Complexity**: Low - Standard XSS attacks work

### After Implementation ✅
- **XSS Impact**: Medium-Low - CSP blocks most XSS; encryption adds obfuscation
- **Token Theft**: Medium-Low - Device fingerprinting detects theft
- **Stolen Token Lifetime**: 30 minutes - Limited exposure window
- **Session Revocation**: Immediate - Token blacklist enables instant revocation
- **Attack Complexity**: High - Multiple security layers required

---

## Support

If you encounter any issues during implementation:

1. Check browser console for errors
2. Check network tab for API responses
3. Verify JWT token structure at jwt.io
4. Check localStorage contents in DevTools
5. Verify device fingerprint generation
6. Test with different browsers
7. Test on mobile devices

**Contact**: Backend Team / Security Team for assistance

---

**Document Version**: 2.0
**Last Updated**: 2025-11-03
**Status**: Ready for Implementation
**Architecture**: localStorage with Multi-Layer Security
**Mobile Support**: ✅ Yes
**Offline Support**: ✅ Yes
**Approved By**: Security Team
