from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from backend.app.database import Base


class QuotaLog(Base):
    __tablename__ = "quota_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)
    change = Column(Integer, nullable=False)
    reason = Column(String(50), nullable=False)

    operator_id = Column(Integer)
    related_plan_id = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
