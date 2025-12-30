# backend/app/models/honor_level_event.py

from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from datetime import datetime

from backend.app.database import Base


class HonorLevelEvent(Base):
    __tablename__ = "honor_level_events"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, nullable=False)

    trigger = Column(String(50), nullable=False)

    before_total_success_tasks = Column(Integer, nullable=False)
    after_total_success_tasks = Column(Integer, nullable=False)

    before_star = Column(Integer, nullable=False)
    after_star = Column(Integer, nullable=False)

    before_moon = Column(Integer, nullable=False)
    after_moon = Column(Integer, nullable=False)

    before_sun = Column(Integer, nullable=False)
    after_sun = Column(Integer, nullable=False)

    before_diamond = Column(Integer, nullable=False)
    after_diamond = Column(Integer, nullable=False)

    before_crown = Column(Integer, nullable=False)
    after_crown = Column(Integer, nullable=False)

    reward_quota_delta = Column(Integer, nullable=False, default=0)

    # ⚠️ UTC 死命令
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
