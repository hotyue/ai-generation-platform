from datetime import datetime, timezone
from typing import Optional

from pydantic import field_serializer

from backend.app.schemas._utc_base import UTCModel


class HistoryItem(UTCModel):
    id: int
    task_id: Optional[str] = None
    prompt: str
    image_url: Optional[str]
    """
    历史记录的展示用图片URL。
    由后端裁决返回：
    - 若存在归档URL，则为归档访问路径
    - 否则为生成阶段的临时访问路径
    前端不得自行判断或拼接。
    """

    status: str
    created_at: datetime

    @field_serializer("created_at", when_used="json")
    def serialize_created_at(self, v: datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        else:
            v = v.astimezone(timezone.utc)

        return v.isoformat().replace("+00:00", "Z")
