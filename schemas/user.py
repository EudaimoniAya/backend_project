from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBaseSchema(BaseModel):
    """用户基础Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    """创建用户Schema"""
    password: str = Field(..., min_length=8)
    role: str = Field("buyer", pattern="^(buyer|seller)$")


class UserResponseSchema(UserBaseSchema):
    """用户响应Schema（不包含密码）"""
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True