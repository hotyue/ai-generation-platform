from datetime import datetime, timezone
from typing import Optional

from pydantic import field_serializer

from backend.app.schemas._utc_base import UTCModel


class HistoryItem(UTCModel):
    id: int
    task_id: str
    prompt: str
    image_url: Optional[str]
    status: str
    created_at: datetime

    @field_serializer("created_at", when_used="json")
    def serialize_created_at(self, v: datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        else:
            v = v.astimezone(timezone.utc)

        return v.isoformat().replace("+00:00", "Z")
