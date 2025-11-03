import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional
from fastapi import FastAPI, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp
from app.core.settings import settings


class SecurityHeadersMiddleware:
    """
    Adds security headers to all responses.

    SECURITY: Protects against:
    - XSS attacks (CSP, X-XSS-Protection)
    - Clickjacking (X-Frame-Options)
    - MIME sniffing (X-Content-Type-Options)
    - Man-in-the-middle (HSTS)
    - Information leakage (Referrer-Policy)
    """
    def __init__(self, app: ASGIApp, enforce_https: bool = False):
        self.app = app
        self.enforce_https = enforce_https

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)

        async def send_wrapper(message):
            if message.get("type") == "http.response.start":
                headers = message.setdefault("headers", [])

                # Content Security Policy - prevents XSS and injection attacks
                csp_directives = [
                    "default-src 'self'",
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Allow inline scripts for dev
                    "style-src 'self' 'unsafe-inline'",
                    "img-src 'self' data: https:",
                    "font-src 'self' data:",
                    "connect-src 'self'",
                    "frame-ancestors 'none'",  # Prevent embedding
                    "base-uri 'self'",
                    "form-action 'self'",
                ]
                headers.append((b"content-security-policy", "; ".join(csp_directives).encode()))

                # Prevent clickjacking attacks
                headers.append((b"x-frame-options", b"DENY"))

                # Prevent MIME sniffing
                headers.append((b"x-content-type-options", b"nosniff"))

                # Enable XSS filter (legacy but still useful)
                headers.append((b"x-xss-protection", b"1; mode=block"))

                # Control referrer information
                headers.append((b"referrer-policy", b"strict-origin-when-cross-origin"))

                # Permissions policy (formerly Feature-Policy)
                permissions = [
                    "camera=()",
                    "microphone=()",
                    "geolocation=()",
                    "payment=()",
                ]
                headers.append((b"permissions-policy", ", ".join(permissions).encode()))

                # HSTS - enforce HTTPS (only in production with HTTPS enabled)
                if self.enforce_https:
                    # max-age=31536000 (1 year), includeSubDomains, preload
                    headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains; preload"))

            await send(message)

        await self.app(scope, receive, send_wrapper)


class RequestIDMiddleware:
    """Adds a unique X-Request-ID header to each response."""
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)

        request_id = str(uuid.uuid4())

        async def send_wrapper(message):
            if message.get("type") == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((b"x-request-id", request_id.encode()))
            await send(message)

        await self.app(scope, receive, send_wrapper)

def install_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware with security validation.

    SECURITY: Never use wildcard origins with credentials enabled
    as this violates CORS spec and creates security vulnerabilities.
    """
    # Convert origins to string list
    origins = [str(o) for o in settings.CORS_ORIGINS] if settings.CORS_ORIGINS else []

    # Security validation: Cannot use wildcard with credentials
    if settings.CORS_ALLOW_CREDENTIALS and ("*" in origins or not origins):
        raise ValueError(
            "CORS Security Error: Cannot use wildcard origins or empty origins "
            "with allow_credentials=True. Please specify explicit origins in "
            "CORS_ORIGINS environment variable."
        )

    # In development, allow localhost variants if no origins specified
    if not origins and settings.DEBUG:
        origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
        ]
        print(f"⚠️  WARNING: Using default development origins: {origins}")
        print("   Set CORS_ORIGINS in .env for production!")

    if not origins:
        raise ValueError(
            "CORS_ORIGINS must be configured. Set CORS_ORIGINS in your .env file."
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        expose_headers=["X-Request-ID"],
    )


def install_security_headers(app: FastAPI, enforce_https: bool = False) -> None:
    """
    Install security headers middleware.

    Args:
        app: FastAPI application instance
        enforce_https: Enable HSTS header (only use in production with HTTPS)

    SECURITY: Adds comprehensive security headers to protect against:
    - Cross-Site Scripting (XSS)
    - Clickjacking
    - MIME type sniffing
    - Man-in-the-middle attacks (when HTTPS enforced)
    - Information leakage
    """
    app.add_middleware(SecurityHeadersMiddleware, enforce_https=enforce_https)


# ============================================================================
# RATE LIMITING MIDDLEWARE
# ============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse and DoS attacks.

    SECURITY: Protects against:
    - Brute force attacks on authentication endpoints
    - API abuse and excessive requests
    - Denial of Service (DoS) attacks

    Features:
    - In-memory storage for development (fast, no dependencies)
    - Redis storage for production (distributed, scalable)
    - Configurable rate limits per IP address
    - Automatic cleanup of expired entries
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_per_window: int = 100,
        window_seconds: int = 60,
        storage: str = "memory",
        redis_url: Optional[str] = None
    ):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.storage_type = storage
        self.redis_url = redis_url

        # In-memory storage: {ip: [timestamp1, timestamp2, ...]}
        self.request_counts: Dict[str, list] = defaultdict(list)

        # Redis storage (if enabled)
        self.redis = None
        if storage == "redis" and redis_url:
            try:
                import redis
                self.redis = redis.from_url(redis_url, decode_responses=True)
            except ImportError:
                print("Warning: Redis not installed, falling back to in-memory storage")
                self.storage_type = "memory"
            except Exception as e:
                print(f"Warning: Redis connection failed ({e}), falling back to in-memory storage")
                self.storage_type = "memory"

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request (handles proxies)"""
        # Check X-Forwarded-For header (proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check X-Real-IP header (nginx proxy)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    def _check_rate_limit_memory(self, ip: str) -> bool:
        """Check rate limit using in-memory storage"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)

        # Get requests for this IP
        requests = self.request_counts[ip]

        # Remove expired requests (older than window)
        requests = [ts for ts in requests if ts > window_start]
        self.request_counts[ip] = requests

        # Check if limit exceeded
        if len(requests) >= self.requests_per_window:
            return False

        # Add current request
        requests.append(now)
        return True

    def _check_rate_limit_redis(self, ip: str) -> bool:
        """Check rate limit using Redis storage"""
        if not self.redis:
            return self._check_rate_limit_memory(ip)

        try:
            key = f"ratelimit:{ip}"
            current = self.redis.get(key)

            if current is None:
                # First request in window
                self.redis.setex(key, self.window_seconds, 1)
                return True

            count = int(current)
            if count >= self.requests_per_window:
                return False

            # Increment counter
            self.redis.incr(key)
            return True

        except Exception as e:
            print(f"Redis error in rate limiting: {e}, falling back to memory")
            return self._check_rate_limit_memory(ip)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and check rate limits"""

        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check rate limit
        if self.storage_type == "redis":
            allowed = self._check_rate_limit_redis(client_ip)
        else:
            allowed = self._check_rate_limit_memory(client_ip)

        if not allowed:
            return Response(
                content='{"detail":"Rate limit exceeded. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Window": str(self.window_seconds),
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Window"] = str(self.window_seconds)

        return response


def install_rate_limiting(
    app: FastAPI,
    enabled: bool = True,
    requests_per_window: int = 100,
    window_seconds: int = 60,
    storage: str = "memory",
    redis_url: Optional[str] = None
) -> None:
    """
    Install rate limiting middleware.

    Args:
        app: FastAPI application instance
        enabled: Enable/disable rate limiting
        requests_per_window: Maximum requests allowed per window
        window_seconds: Time window in seconds
        storage: Storage backend ("memory" or "redis")
        redis_url: Redis connection URL (required if storage="redis")

    SECURITY: Protects against:
    - Brute force attacks
    - API abuse
    - Denial of Service (DoS) attacks

    Example:
        # Development (in-memory)
        install_rate_limiting(app, enabled=True, requests_per_window=100, window_seconds=60)

        # Production (Redis)
        install_rate_limiting(
            app,
            enabled=True,
            requests_per_window=100,
            window_seconds=60,
            storage="redis",
            redis_url="redis://localhost:6379/0"
        )
    """
    if not enabled:
        print("Rate limiting disabled")
        return

    app.add_middleware(
        RateLimitMiddleware,
        requests_per_window=requests_per_window,
        window_seconds=window_seconds,
        storage=storage,
        redis_url=redis_url
    )
    print(f"Rate limiting enabled: {requests_per_window} requests per {window_seconds}s ({storage} storage)")
