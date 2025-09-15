from pydantic import BaseModel, EmailStr, Field

class ForgotPasswordIn(BaseModel):
    # Accept either email or username; keep both optional but require at least one at route level
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=100)

class ResetPasswordIn(BaseModel):
    token: str = Field(min_length=10, max_length=200)
    new_password: str = Field(min_length=8, max_length=128)

class ResetPasswordOut(BaseModel):
    status: str = "ok"
