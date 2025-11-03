# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
import logging

from app.core.settings import settings
from app.core.logging import configure_logging
from app.core.middleware import (
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    install_rate_limiting
)
from app.core.exceptions import install_exception_handlers
from app.api.v1.router import api_router
from app.core.error_handlers import add_error_handlers

# Configure logging first
configure_logging()
logger = logging.getLogger(__name__)

# IMPORTANT: Import OpenAPI bypass BEFORE creating the app
import app.core.openapi_bypass  # noqa

# NOTE: OpenAPI temporarily disabled due to 299 endpoints needing response_model fixes
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Cardinsa Insurance Management System API",
    openapi_url="/openapi.json",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS Configuration - Allow your Next.js frontend
cors_origins = [
    "http://localhost:3000",      # Next.js development server (admin portal)
    "http://127.0.0.1:3000",      # Alternative localhost
    "http://localhost:3001",      # Backup port
    "http://localhost:3003",      # Broker portal
    "http://127.0.0.1:3003",      # Broker portal alternative
    "https://localhost:3000",     # HTTPS version (if using SSL in dev)
]

# Add production URLs if not in debug mode
if not settings.DEBUG and hasattr(settings, 'FRONTEND_URL'):
    cors_origins.append(settings.FRONTEND_URL)

# Add CORS middleware FIRST (order matters)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST", 
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "HEAD"
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "X-Portal-Context",    # Your custom portal header
        "X-Request-ID",        # Your custom request ID header
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Mx-ReqToken",
        "Keep-Alive",
        "If-Modified-Since",
    ],
)

# Add other middlewares
app.add_middleware(RequestIDMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1024)

# Add rate limiting middleware
# SECURITY: Protects against brute force, API abuse, DoS attacks
install_rate_limiting(
    app,
    enabled=settings.RATE_LIMIT_ENABLED,
    requests_per_window=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW,
    storage=settings.RATE_LIMIT_STORAGE,
    redis_url=settings.RATE_LIMIT_REDIS_URL
)

# Add security headers middleware (LAST in chain = FIRST to execute)
# SECURITY: Adds CSP, X-Frame-Options, HSTS, etc.
enforce_https = settings.ENV == "production" if hasattr(settings, "ENV") else False
app.add_middleware(SecurityHeadersMiddleware, enforce_https=enforce_https)

# Install error handlers
add_error_handlers(app)
install_exception_handlers(app)

# Add startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"API URL: {settings.API_V1_STR}")
    logger.info(f"CORS origins: {cors_origins}")

# Add shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint with health check
@app.get("/", tags=["Health"])
def root():
    """Root endpoint - provides basic API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
        "api_version": settings.API_V1_STR,
        "status": "healthy",
        "docs": "/docs" if settings.DEBUG else None,
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
    }

# NOTE: Catch-all OPTIONS route removed - CORS middleware handles preflight automatically
# The catch-all @app.options("/{path:path}") was causing 405 errors on all routes

# Development-only endpoints
if settings.DEBUG:
    @app.get("/debug/cors", tags=["Debug"])
    def debug_cors():
        """Debug CORS configuration"""
        return {
            "cors_origins": cors_origins,
            "allow_credentials": True,
            "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
            "frontend_should_use": "http://localhost:3000",
            "api_base": f"http://localhost:8001{settings.API_V1_STR}",
        }
    
    @app.get("/debug/headers", tags=["Debug"])  
    def debug_headers(request):
        """Debug incoming headers"""
        return {
            "headers": dict(request.headers),
            "origin": request.headers.get("origin"),
            "user_agent": request.headers.get("user-agent"),
        }

