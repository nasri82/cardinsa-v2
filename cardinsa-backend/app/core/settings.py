# app/core/settings.py  (add/adjust these bits)

from typing import List, Optional
import json
from pydantic import AnyHttpUrl, Field, field_validator, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Cardinsa"
    APP_VERSION: str = "0.1.0"
    ENV: str = "dev"
    DEBUG: bool = True
    FRONTEND_BASE_URL: str = "http://localhost:3000"
    OPENAPI_URL: str = "/openapi.json"  # <-- add this so main.py works

    # --- API ---
    API_V1_STR: str = "/api/v1"

    # --- Security / JWT (compatible with your .env) ---
    JWT_SECRET: str = Field("change-me-in-.env", validation_alias=AliasChoices("JWT_SECRET", "SECRET_KEY"))
    REFRESH_TOKEN_SECRET: str = Field("change-me-in-.env-refresh", validation_alias=AliasChoices("REFRESH_TOKEN_SECRET"))
    JWT_EXPIRE_MINUTES: int = Field(30, validation_alias=AliasChoices("JWT_EXPIRE_MINUTES", "ACCESS_TOKEN_EXPIRE_MINUTES"))  # Changed from 60 to 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, validation_alias=AliasChoices("REFRESH_TOKEN_EXPIRE_DAYS"))  # NEW: 7 days
    JWT_ALGORITHM: str = Field("HS256", validation_alias=AliasChoices("JWT_ALGORITHM", "JWT_ALG"))

    # (keep your existing EdDSA fields if you still need them later)
    jwt_private_key_path: str = Field("./keys/ed25519-private.pem", validation_alias=AliasChoices("jwt_private_key_path", "JWT_PRIVATE_KEY_PATH"))
    jwt_public_key_path: str  = Field("./keys/ed25519-public.pem", validation_alias=AliasChoices("jwt_public_key_path", "JWT_PUBLIC_KEY_PATH"))

    PASSWORD_RESET_TOKEN_TTL_MINUTES: int = 30

    # --- Database ---
    # DATABASE_URL must be set in .env file - no default for security
    DATABASE_URL: str
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_PRE_PING: bool = True

    # --- CORS ---
    CORS_ORIGINS: List[AnyHttpUrl] = []
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # --- Rate Limiting ---
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # requests per window
    RATE_LIMIT_WINDOW: int = 60  # window in seconds
    RATE_LIMIT_STORAGE: str = "memory"  # "memory" or "redis"
    RATE_LIMIT_REDIS_URL: Optional[str] = None  # "redis://localhost:6379/0"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                try:
                    return json.loads(s)
                except json.JSONDecodeError:
                    return [s]
            return [item.strip() for item in s.split(",") if item.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
