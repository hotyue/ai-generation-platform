from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UTCModel(BaseModel):
    """
    v1.0.7 时间语义治理 · 基类最终裁决版

    只承担一件事：
    - 允许 ORM -> Schema（from_attributes）
    不做任何序列化拦截（避免 Pydantic v2 启动期错误）
    """

    model_config = ConfigDict(from_attributes=True)
