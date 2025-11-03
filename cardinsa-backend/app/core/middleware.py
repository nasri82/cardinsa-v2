import uuid
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.settings import settings

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
