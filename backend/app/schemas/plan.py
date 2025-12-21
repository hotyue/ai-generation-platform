from pydantic import BaseModel
from typing import Optional

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quota: Optional[int] = None
    duration_days: Optional[int] = None
    price: Optional[float] = None
