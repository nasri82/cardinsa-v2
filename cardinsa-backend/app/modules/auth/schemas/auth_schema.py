# app/modules/auth/schemas/auth_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class TokenResponse(BaseModel):
    """
    Response model for login and refresh endpoints.

    SECURITY: Includes both access and refresh tokens for token rotation
    """
    access_token: str
    refresh_token: Optional[str] = None  # Included in login and refresh responses
    token_type: str = "bearer"
    

class TokenData(BaseModel):
    """Token payload data"""
    sub: Optional[str] = None


class LoginRequest(BaseModel):
    """Alternative login request model (if not using OAuth2PasswordRequestForm)"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class RoleInfo(BaseModel):
    """Role information for user"""
    id: str
    name: str
    
    class Config:
        from_attributes = True


class UserInfoResponse(BaseModel):
    """Current user information response"""
    id: UUID
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    user_type: Optional[str] = None
    company_id: Optional[UUID] = None
    department: Optional[str] = None
    unit: Optional[str] = None
    position: Optional[str] = None
    roles: List[RoleInfo] = []
    
    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class LogoutResponse(BaseModel):
    """Logout response"""
    message: str