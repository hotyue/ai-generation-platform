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
    v1.0.7 最终裁决版 User 输出 Schema

    设计原则：
    - 继承 UTCModel（仅用于 ORM 映射）
    - datetime 序列化逻辑放在本类（避免 Pydantic v2 启动期错误）
    """

    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    role: str
    quota: int
    is_active: bool
    avatar_url: Optional[str]
    created_at: datetime

    # ORM → Schema
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", when_used="json")
    def serialize_created_at(self, v: datetime):
        """
        将 created_at 输出为自描述 UTC 时间（ISO8601 + Z）

        - naive datetime：视为 UTC
        - aware datetime：转换为 UTC
        """
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
