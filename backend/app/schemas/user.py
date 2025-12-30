from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer

from backend.app.schemas._utc_base import UTCModel


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(UTCModel):
    """
    v1.0.30 User 输出 Schema（荣誉字段与数据库精确对齐）

    说明：
    - /auth/me 的初始化事实源
    - 字段名严格对齐 users 表
    - 不引入任何派生字段或映射逻辑
    """

    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]

    role: str

    # ===== 账户状态 =====
    account_status: str
    quota: int
    is_active: bool
    avatar_url: Optional[str]
    created_at: datetime

    # ===== 荣誉系统（与 users 表字段完全一致）=====
    total_success_tasks: int

    level_star: int
    level_moon: int
    level_sun: int
    level_diamond: int
    level_crown: int

    # ORM → Schema
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", when_used="json")
    def serialize_created_at(self, v: datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        else:
            v = v.astimezone(timezone.utc)
        return v.isoformat().replace("+00:00", "Z")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
