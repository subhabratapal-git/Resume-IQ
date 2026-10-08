from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserLogin(BaseModel):
    email: EmailStr

    password: str


class UserResponse(BaseModel):
    id: int

    full_name: str

    email: EmailStr

    is_active: bool

    pro_uses_remaining: int

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class AuthResponse(BaseModel):
    message: str

    access_token: str

    token_type: str

    user: UserResponse


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        min_length=1,
        max_length=128
    )

    # Minimum 8 characters — consistent with registration policy
    new_password: str = Field(
        min_length=8,
        max_length=128
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=128
    )