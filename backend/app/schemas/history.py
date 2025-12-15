from pydantic import BaseModel

class HistoryItem(BaseModel):
    task_id: str
    prompt: str
    image_url: str
    timestamp: str
