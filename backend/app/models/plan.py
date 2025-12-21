from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from datetime import datetime

from backend.app.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(50), nullable=False)
    description = Column(String(255))

    quota = Column(Integer, nullable=False)
    duration_days = Column(Integer)

    # ✅ 金额字段：与数据库 numeric(10,2) 对齐
    price = Column(Numeric(10, 2), default=0)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
