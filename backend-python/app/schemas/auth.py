from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str
    device_type: str = "pc"


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1, description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码（至少6位）")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")


class ResetPasswordRequest(BaseModel):
    user_id: int = Field(..., description="要重置密码的用户ID")
    new_password: str = Field(..., min_length=6, description="新密码（至少6位）")
