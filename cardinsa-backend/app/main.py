# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.core.settings import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware  # keep your custom middleware
from app.core.exceptions import install_exception_handlers
from app.api.v1.router import api_router
from app.core.error_handlers import add_error_handlers

configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=settings.OPENAPI_URL,              # now exists in settings.py
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Middlewares (exactly once)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o) for o in settings.CORS_ORIGINS],
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Error handlers
add_error_handlers(app)
install_exception_handlers(app)

# Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["meta"])
def root():
    return {
        "name": settings.APP_NAME,
        "env": settings.ENV,
        "version": settings.APP_VERSION,
        "api": settings.API_V1_STR,
    }
