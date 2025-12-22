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
    v1.0.10 User 输出 Schema（修正版）

    核心修复：
    - 明确输出 account_status
    - 作为所有前端状态判断的唯一事实源
    """

    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]

    role: str

    # ✅ 关键字段（本次问题根因）
    account_status: str   # normal / restricted / banned

    quota: int
    is_active: bool
    avatar_url: Optional[str]
    created_at: datetime

    # ORM → Schema
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", when_used="json")
    def serialize_created_at(self, v: datetime):
        """
        将 created_at 输出为 UTC ISO8601（带 Z）
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
