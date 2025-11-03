# Phase 1: Frontend Security Tasks - TODO

**Date**: 2025-11-03
**Status**: PENDING
**Priority**: HIGH
**Estimated Time**: 4-6 hours

---

## Executive Summary

This document outlines the remaining frontend security tasks for Phase 1 of the security remediation plan. These tasks focus on protecting user sessions and preventing common web vulnerabilities like XSS and CSRF attacks.

### Current Security Posture

**Backend**: ✅ All critical vulnerabilities fixed
**Frontend**: ⚠️ 2 high-priority tasks remaining

---

## Task 1: Migrate Tokens from localStorage to httpOnly Cookies

### Priority: HIGH (XSS Protection)
### Estimated Time: 2-3 hours
### Risk Level: CVSS 7.5 (High)

### Current Vulnerability

Currently, JWT tokens are stored in `localStorage`, which makes them vulnerable to XSS (Cross-Site Scripting) attacks:

```javascript
// ❌ CURRENT: Vulnerable to XSS attacks
localStorage.setItem('access_token', token);
localStorage.setItem('refresh_token', refreshToken);
```

**Impact**:
- Any XSS vulnerability in the application allows token theft
- Malicious scripts can read localStorage and send tokens to attackers
- Users' accounts can be compromised without their knowledge

### Solution: httpOnly Cookies

**httpOnly cookies** cannot be accessed by JavaScript, providing strong XSS protection:

```javascript
// ✅ NEW: Protected from XSS attacks
// Tokens are set by backend as httpOnly cookies
// Frontend cannot read them, but they're automatically sent with requests
```

### Implementation Steps

#### Step 1: Backend Changes (Already Prepared)

The backend needs to set cookies in the authentication endpoints:

**File**: `cardinsa-backend/app/modules/auth/routes/auth_route.py`

```python
from fastapi import Response

@router.post("/login")
async def login(response: Response, credentials: LoginSchema, db: Session = Depends(get_db)):
    # ... authentication logic ...

    # Set httpOnly cookies instead of returning tokens in response
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,        # Cannot be accessed by JavaScript
        secure=True,          # Only sent over HTTPS (production)
        samesite="lax",       # CSRF protection
        max_age=3600,         # 1 hour
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,       # 7 days
        path="/api/v1/auth/refresh",  # Only sent to refresh endpoint
    )

    return {
        "message": "Login successful",
        "user": user_data,
        # No tokens in response body!
    }
```

#### Step 2: Frontend Changes (TODO)

**Affected Files**:
- `cardinsa-frontend/src/contexts/AuthContext.tsx` (or similar auth context)
- `cardinsa-frontend/src/lib/auth.ts` (authentication utilities)
- `cardinsa-frontend/src/lib/api.ts` (API client)

**Changes Required**:

1. **Remove localStorage usage**:
```typescript
// ❌ REMOVE THESE
localStorage.setItem('access_token', token);
localStorage.setItem('refresh_token', refreshToken);
localStorage.getItem('access_token');
localStorage.removeItem('access_token');
```

2. **Update API client to use credentials**:
```typescript
// ✅ ADD THIS
// File: src/lib/api.ts
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,  // Send cookies with every request
});
```

3. **Update authentication state management**:
```typescript
// ✅ NEW: Authentication without storing tokens
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication status on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // Call endpoint that requires authentication
      // Cookie is automatically sent with request
      const response = await apiClient.get('/auth/me');
      setUser(response.data.user);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    // No need to handle tokens - backend sets cookies
    const response = await apiClient.post('/auth/login', { email, password });
    setUser(response.data.user);
  };

  const logout = async () => {
    await apiClient.post('/auth/logout');
    // Backend will clear cookies
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}
```

4. **Update logout endpoint** (backend):
```python
@router.post("/logout")
async def logout(response: Response):
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
```

5. **Update CORS configuration** (already done in backend):
```python
# Backend main.py - already configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,  # Required for cookies
    # ...
)
```

### Testing Checklist

- [ ] Login sets httpOnly cookies (check DevTools → Application → Cookies)
- [ ] Cookies are automatically sent with API requests
- [ ] JavaScript cannot access cookies (`document.cookie` doesn't show them)
- [ ] Logout clears cookies
- [ ] Token refresh works with cookies
- [ ] Authentication persists across page refreshes
- [ ] Works in incognito/private mode

---

## Task 2: Add CSRF Protection

### Priority: HIGH
### Estimated Time: 2-3 hours
### Risk Level: CVSS 7.3 (High)

### Current Vulnerability

With cookie-based authentication, the application becomes vulnerable to CSRF (Cross-Site Request Forgery) attacks without proper protection.

**Attack Scenario**:
```html
<!-- Malicious website -->
<form action="https://cardinsa.com/api/v1/policies/123" method="POST">
  <input type="hidden" name="status" value="cancelled">
</form>
<script>document.forms[0].submit();</script>
```

If a logged-in user visits this malicious site, their browser automatically sends their cookies, and the request appears legitimate.

### Solution: CSRF Tokens

Implement CSRF protection using tokens that must be sent with state-changing requests.

### Implementation Steps

#### Step 1: Backend CSRF Middleware

**Install dependency**:
```bash
pip install fastapi-csrf-protect
```

**File**: `cardinsa-backend/requirements.txt`
```txt
fastapi-csrf-protect>=0.3.0
```

**File**: `cardinsa-backend/app/core/middleware.py`

Add CSRF protection:

```python
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    secret_key: str = settings.JWT_SECRET
    cookie_name: str = "csrf_token"
    cookie_samesite: str = "lax"
    cookie_secure: bool = settings.ENV == "production"
    cookie_httponly: bool = False  # Frontend needs to read this
    header_name: str = "X-CSRF-Token"

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
```

**File**: `cardinsa-backend/app/main.py`

Add CSRF exception handler:

```python
from fastapi_csrf_protect.exceptions import CsrfProtectError

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "CSRF token validation failed"}
    )
```

**Protect endpoints**:

```python
from fastapi_csrf_protect import CsrfProtect

# GET endpoint - sets CSRF token cookie
@router.get("/csrf-token")
async def get_csrf_token(csrf_protect: CsrfProtect = Depends()):
    # This will set the CSRF token cookie
    csrf_token = csrf_protect.generate_csrf()
    return {"csrf_token": csrf_token}

# POST/PUT/DELETE endpoints - require CSRF token
@router.post("/policies")
async def create_policy(
    policy: PolicyCreate,
    csrf_protect: CsrfProtect = Depends(),
    current_user: CurrentUser = Depends(get_current_user)
):
    await csrf_protect.validate_csrf()  # Validates CSRF token
    # ... endpoint logic ...
```

#### Step 2: Frontend CSRF Implementation

**File**: `cardinsa-frontend/src/lib/api.ts`

```typescript
let csrfToken: string | null = null;

// Fetch CSRF token on app initialization
export async function initCsrf() {
  try {
    const response = await apiClient.get('/auth/csrf-token');
    csrfToken = response.data.csrf_token;
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error);
  }
}

// Add CSRF token to all state-changing requests
apiClient.interceptors.request.use((config) => {
  if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
  }
  return config;
});

// Refresh CSRF token if it expires
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 403 && error.response?.data?.detail === 'CSRF token validation failed') {
      // Refresh CSRF token and retry
      await initCsrf();
      return apiClient.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

**File**: `cardinsa-frontend/src/app/layout.tsx` (or `_app.tsx` for Next.js pages router)

```typescript
import { useEffect } from 'react';
import { initCsrf } from '@/lib/api';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Initialize CSRF token on app load
    initCsrf();
  }, []);

  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

### Testing Checklist

- [ ] CSRF token is fetched on app initialization
- [ ] CSRF token cookie is set (check DevTools → Application → Cookies)
- [ ] POST/PUT/DELETE requests include X-CSRF-Token header
- [ ] Requests with invalid CSRF token are rejected (403 error)
- [ ] CSRF token is refreshed on expiration
- [ ] Works across different domains in development

---

## Security Best Practices

### Cookie Security Attributes

**httpOnly**: Prevents JavaScript access (XSS protection)
**secure**: Only send over HTTPS (production)
**samesite**: Prevents CSRF attacks
- `strict`: Never sent in cross-site requests (very secure, but breaks some flows)
- `lax`: Sent in top-level navigation (recommended)
- `none`: Always sent (requires `secure=true`)

### Token Expiration

**Access Token**: 1 hour (short-lived for security)
**Refresh Token**: 7 days (long-lived for convenience)
**CSRF Token**: Session-based

### CORS Configuration

```typescript
// Frontend - ensure credentials are sent
axios.create({
  baseURL: API_URL,
  withCredentials: true,  // Required for cookies
});
```

```python
# Backend - must allow credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Explicit origins
    allow_credentials=True,  # Required for cookies
    # ...
)
```

---

## Migration Checklist

### Backend Tasks
- [ ] Update login endpoint to set httpOnly cookies
- [ ] Update logout endpoint to clear cookies
- [ ] Add CSRF protection middleware
- [ ] Add CSRF token endpoint
- [ ] Protect state-changing endpoints with CSRF validation
- [ ] Update CORS configuration (already done)
- [ ] Test with Postman/curl

### Frontend Tasks
- [ ] Remove all localStorage token storage
- [ ] Update API client to use `withCredentials: true`
- [ ] Update AuthContext to work without token storage
- [ ] Add CSRF token initialization
- [ ] Add CSRF token to API requests
- [ ] Update logout flow
- [ ] Test authentication flows
- [ ] Test CSRF protection

### Testing
- [ ] Login/logout functionality
- [ ] Token refresh mechanism
- [ ] Protected route access
- [ ] CSRF protection (try requests without token)
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile browser testing
- [ ] Incognito/private mode testing

---

## Resources

### Documentation
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN: httpOnly Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

### Tools
- [OWASP ZAP](https://www.zaproxy.org/) - Web application security scanner
- [Burp Suite](https://portswigger.net/burp) - Security testing toolkit

---

## Risk Assessment

### Before Implementation ⚠️
- **XSS Impact**: High - Tokens can be stolen via XSS attacks
- **CSRF Impact**: High - State-changing requests can be forged
- **Attack Complexity**: Low - Well-known attack vectors
- **User Impact**: Critical - Account takeover possible

### After Implementation ✅
- **XSS Impact**: Low - Tokens not accessible to JavaScript
- **CSRF Impact**: Low - CSRF tokens prevent forged requests
- **Attack Complexity**: High - Multiple layers of protection
- **User Impact**: Minimal - Strong session protection

---

## Timeline

**Estimated Total Time**: 4-6 hours

- **Backend Implementation**: 1-2 hours
- **Frontend Implementation**: 2-3 hours
- **Testing**: 1-2 hours

**Recommended Approach**: Implement backend and frontend in parallel, test integration together.

---

## Support

If you encounter any issues during implementation:

1. Check browser console for errors
2. Check browser DevTools → Application → Cookies
3. Check network tab for cookie headers
4. Verify CORS configuration
5. Test with curl/Postman first

**Contact**: Security Team / Backend Team for assistance

---

**Document Version**: 1.0
**Last Updated**: 2025-11-03
**Status**: Ready for Implementation
**Approved By**: Security Team
